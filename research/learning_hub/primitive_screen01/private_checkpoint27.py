"""One-time reconstruction, resumable every 16 steps; no public weight upload."""
import argparse, copy, hashlib, json, os, platform, sys, time, zipfile
from pathlib import Path

ROOT = Path(os.environ.get("OMEGA_CHECKPOINT_ROOT",str(Path(__file__).resolve().parent)))
SOURCE = ROOT/'source' if (ROOT/'source').is_dir() else Path(__file__).resolve().parent
sys.path.insert(0,str(SOURCE))
import curriculum06 as c
import trainer07 as t
import runner11 as r
import pilot14 as p
import cumulative18 as a
import resume25 as state

def streaming_hash(named, tuple_shape=False):
    h=hashlib.sha256()
    for name,value in named:
        h.update(name.encode());h.update(str(tuple(value.shape) if tuple_shape else value.shape).encode())
        h.update(str(value.dtype).encode())
        array=value.detach().cpu().contiguous().numpy()
        h.update(memoryview(array).cast('B'))
    return h.hexdigest()

# Same byte stream and digests as the original helpers, without large copies.
r.tensor_hash=lambda values:streaming_hash(values)
state.tensor_hash=lambda values:streaming_hash(values,True)

def need(ok, reason):
    if not ok: raise ValueError(reason)

def stable(obj):
    h=hashlib.sha256()
    def visit(value):
        import torch
        if torch.is_tensor(value):
            h.update(str(value.dtype).encode());h.update(str(tuple(value.shape)).encode())
            h.update(value.detach().cpu().contiguous().numpy().tobytes())
        elif isinstance(value,dict):
            for key in sorted(value,key=str):h.update(repr(key).encode());visit(value[key])
        elif isinstance(value,(tuple,list)):
            h.update(type(value).__name__.encode())
            for v in value:visit(v)
        else:h.update(repr(value).encode())
    visit(obj);return h.hexdigest()

def package(checkpoint, step, context, metadata):
    status=dict(stage='experimental_reconstruction',completed_steps=step,total_steps=128,
                checkpoint_directory=checkpoint.name,context=context,
                independent_qualification=False,metadata=metadata)
    (ROOT/'status.json').write_text(json.dumps(status,indent=2))
    target=ROOT/'omega_qwen_resume26_private_checkpoint.zip'
    temporary=target.with_suffix('.pending')
    with zipfile.ZipFile(temporary,'w',zipfile.ZIP_DEFLATED) as z:
        for f in checkpoint.iterdir():z.write(f,'checkpoint/'+f.name)
        z.write(ROOT/'status.json','status.json')
        z.write(__file__,'bootstrap.py')
        z.write(SOURCE/'resume25.py','resume25.py')
        z.write(ROOT/'budget/realbudget10.json','budget/realbudget10.json')
    os.replace(temporary,target)
    print('PRIVATE_CHECKPOINT_READY',step,str(target),flush=True)

def run(mode, stop_after=128):
    import torch
    from transformers import AutoTokenizer, AutoModelForCausalLM
    from peft import get_peft_model
    started=time.monotonic();torch.set_num_threads(2);torch.manual_seed(t.SEED)
    print('LOAD_TOKENIZER',flush=True)
    tok=AutoTokenizer.from_pretrained(c.MODEL,revision=c.REV,trust_remote_code=False)
    rows,enc,plans,budgets=p.plan_audit(tok,ROOT/'budget/realbudget10.json')
    batches=plans['adaptive']['batches']
    context=dict(model=c.MODEL,revision=c.REV,
                 tokenizer_sha=r.digest(tok.backend_tokenizer.to_str()),
                 data_sha=r.digest(json.dumps(rows,sort_keys=True)),
                 plan_sha=r.digest(json.dumps(batches,sort_keys=True)))
    print('LOAD_MODEL_LOW_MEMORY',flush=True)
    model=AutoModelForCausalLM.from_pretrained(c.MODEL,revision=c.REV,
        trust_remote_code=False,torch_dtype=torch.float32,low_cpu_mem_usage=True)
    print('MODEL_LOADED',flush=True)
    need(model.config._commit_hash==c.REV,'REVISION')
    model.config.use_cache=False;model=get_peft_model(model,t.lora_config())
    named=[(n,v) for n,v in model.named_parameters() if v.requires_grad]
    params=[v for n,v in named]
    opt=torch.optim.AdamW(params,lr=.0002,weight_decay=0.)
    manifest=a.check_sources(ROOT/'original',ROOT/'results/pilot14-result.json')
    need(r.tensor_hash([(n,v) for n,v in model.named_parameters() if not v.requires_grad])==manifest['frozen_base_sha'],'FROZEN_BASE')
    print('FROZEN_BASE_EXACT',flush=True)
    metadata=dict(model=c.MODEL,revision=c.REV,python=platform.python_version(),torch=torch.__version__,
                  seed=t.SEED,threads=2,source_artifacts=[15043104833,15047856395,15048321608])
    checkpoints=ROOT/'checkpoints';checkpoints.mkdir(mode=0o700,exist_ok=True)
    if mode=='prepare':
        need(r.tensor_hash(named)==manifest['initial_adapter_sha'],'INITIAL_ADAPTER')
        checkpoint=checkpoints/'step-0000'
        state.save(model,opt,checkpoint,context,0)
        package(checkpoint,0,context,metadata)
        print('PRIVATE_INITIAL_STATE_PREPARED',flush=True);return
    completed=sorted(checkpoints.glob('step-*'))
    if mode=='verify':
        checkpoint=checkpoints/'step-0128'
        if not checkpoint.exists() and (ROOT/'checkpoint').is_dir(): checkpoint=ROOT/'checkpoint'
        cursor=state.load(model,opt,checkpoint,context)
        need(cursor==128,'CURSOR')
        model.train()
        stats=t.optimizer_step(model,opt,params,t.collate(tok,enc,batches[cursor%128]),'adaptive')
        observed=dict(adapter=r.tensor_hash(named),optimizer=stable(opt.state_dict()),rng=stable(state.rng()),loss=stats)
        expected=json.loads((ROOT/'next-step-reference.json').read_text())
        need(observed==expected,'NEW_PROCESS_CONTINUATION_MISMATCH')
        state.load(model,opt,checkpoint,context)
        need(r.tensor_hash(named)==manifest['final_transaction_adapter_sha'],'FINAL_RESTORE')
        report=dict(status='REAL_QWEN_NEW_PROCESS_RESUME_EXACT',model=c.MODEL,revision=c.REV,
            reconstructed_steps=128,independent_process_next_step_exact=True,
            adapter_optimizer_rng_loss_exact=True,retained_test_updates=0,
            checkpoint_sha=r.sha(checkpoint/'state.pt'),private_storage_connected='local private directory, Library upload verified separately',
            elapsed_seconds=time.monotonic()-started,promotion_authorized=False)
        (ROOT/'verification.json').write_text(json.dumps(report,indent=2))
        print(json.dumps(report,indent=2),flush=True);return
    supplied=completed[-1] if completed else (ROOT/'checkpoint' if (ROOT/'checkpoint').is_dir() else None)
    if supplied is not None:
        cursor=state.load(model,opt,supplied,context)
        print('RESUMED_RECONSTRUCTION',cursor,flush=True)
    else:
        need(r.tensor_hash(named)==manifest['initial_adapter_sha'],'INITIAL_ADAPTER')
        cursor=0
    model.train()
    need(type(stop_after) is int and stop_after in range(16,129,16),'STOP_AFTER')
    for i in range(cursor,stop_after):
        stats=t.optimizer_step(model,opt,params,t.collate(tok,enc,batches[i]),'adaptive')
        if i<2:print('EARLY_UPDATE',i+1,flush=True)
        if (i+1)%8==0:print('RECONSTRUCTION',i+1,'/128',round(time.monotonic()-started,2),flush=True)
        if (i+1)%16==0:
            checkpoint=checkpoints/('step-%04d'%(i+1))
            state.save(model,opt,checkpoint,context,i+1)
            package(checkpoint,i+1,context,metadata)
    if stop_after<128:
        print('PARTIAL_RECONSTRUCTION_SAVED',stop_after,flush=True);return
    checkpoint=checkpoints/'step-0128'
    if not checkpoint.exists() and supplied is not None and cursor==128: checkpoint=supplied
    observed=r.tensor_hash(named)
    need(observed==manifest['final_transaction_adapter_sha'],'FINAL_ADAPTER_NOT_IDENTICAL')
    print('EXACT_HISTORICAL_ADAPTER_REPRODUCED',observed,flush=True)
    # One temporary step establishes the continuation reference, then rollback.
    stats=t.optimizer_step(model,opt,params,t.collate(tok,enc,batches[0]),'adaptive')
    expected=dict(adapter=r.tensor_hash(named),optimizer=stable(opt.state_dict()),rng=stable(state.rng()),loss=stats)
    (ROOT/'next-step-reference.json').write_text(json.dumps(expected,indent=2))
    state.load(model,opt,checkpoint,context)
    need(r.tensor_hash(named)==manifest['final_transaction_adapter_sha'],'ROLLBACK')
    print('RECONSTRUCTION_COMPLETE_READY_FOR_NEW_PROCESS',round(time.monotonic()-started,2),flush=True)

def encrypt_bundle(public_key_file=None):
    import base64
    from cryptography.hazmat.primitives import hashes,serialization
    from cryptography.hazmat.primitives.asymmetric import padding
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
    package_file=ROOT/'omega_qwen_resume26_private_checkpoint.zip'
    need(package_file.is_file(),'NO_PRIVATE_CHECKPOINT')
    status=json.loads((ROOT/'status.json').read_text())
    report_file=ROOT/'verification.json'
    report=json.loads(report_file.read_text()) if report_file.exists() else {}
    verified=report.get('status')=='REAL_QWEN_NEW_PROCESS_RESUME_EXACT'
    # The public artifact contains ciphertext only, never the plaintext bundle.
    with zipfile.ZipFile(package_file,'a',zipfile.ZIP_DEFLATED) as z:
        for module in SOURCE.glob('*.py'):z.write(module,'source/'+module.name)
        z.write(SOURCE/'RESUME27_PUBLIC.pem','source/RESUME27_PUBLIC.pem')
        for folder in ('original','results'):
            for f in (ROOT/folder).iterdir():
                if f.is_file():z.write(f,folder+'/'+f.name)
        for name in ('next-step-reference.json','verification.json'):
            if (ROOT/name).is_file():z.write(ROOT/name,name)
    raw=package_file.read_bytes()
    pem=Path(public_key_file or SOURCE/'RESUME27_PUBLIC.pem').read_bytes()
    pub=serialization.load_pem_public_key(pem)
    key=AESGCM.generate_key(bit_length=256);nonce=os.urandom(12);aad=b'OMEGA-RESUME27-v1'
    encrypted=AESGCM(key).encrypt(nonce,raw,aad)
    wrapped=pub.encrypt(key,padding.OAEP(mgf=padding.MGF1(hashes.SHA256()),algorithm=hashes.SHA256(),label=None))
    dest=ROOT/'encrypted';dest.mkdir(mode=0o700,exist_ok=True)
    (dest/'checkpoint.aesgcm').write_bytes(encrypted)
    envelope=dict(schema=1,algorithm='RSA-OAEP-SHA256+AES-256-GCM',
        wrapped_key=base64.b64encode(wrapped).decode(),nonce=base64.b64encode(nonce).decode(),
        aad=base64.b64encode(aad).decode(),plaintext_sha256=hashlib.sha256(raw).hexdigest(),
        ciphertext_sha256=hashlib.sha256(encrypted).hexdigest(),
        public_key_sha256=hashlib.sha256(pem).hexdigest(),completed_steps=status['completed_steps'],
        independent_process_verified=verified,promotion_authorized=False)
    (dest/'envelope.json').write_text(json.dumps(envelope,indent=2))
    (dest/'verification-public.json').write_text(json.dumps(report or {'status':'PARTIAL_OR_UNVERIFIED_CHECKPOINT'},indent=2))
    print('ENCRYPTED_CHECKPOINT_READY',status['completed_steps'],'verified',verified,flush=True)

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('mode',choices=['prepare','bootstrap','verify','encrypt']);parser.add_argument('--stop-after',type=int,default=128);args=parser.parse_args()
    if args.mode=='encrypt':encrypt_bundle()
    else:run(args.mode,args.stop_after)
