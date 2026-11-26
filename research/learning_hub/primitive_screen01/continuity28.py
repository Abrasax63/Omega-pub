"""Three actual CPU updates across two processes; no scientific qualification."""
import argparse, json, os, sys, time
from pathlib import Path
import private_checkpoint27 as q

def run(mode):
    import torch
    from transformers import AutoTokenizer, AutoModelForCausalLM
    from peft import get_peft_model
    root=Path(os.environ['OMEGA_CHECKPOINT_ROOT'])
    started=time.monotonic();torch.set_num_threads(2);torch.manual_seed(q.t.SEED)
    tok=AutoTokenizer.from_pretrained(q.c.MODEL,revision=q.c.REV,trust_remote_code=False)
    rows,enc,plans,_=q.p.plan_audit(tok,root/'budget/realbudget10.json')
    batches=plans['adaptive']['batches']
    context=dict(model=q.c.MODEL,revision=q.c.REV,
        tokenizer_sha=q.r.digest(tok.backend_tokenizer.to_str()),
        data_sha=q.r.digest(json.dumps(rows,sort_keys=True)),
        plan_sha=q.r.digest(json.dumps(batches,sort_keys=True)))
    model=AutoModelForCausalLM.from_pretrained(q.c.MODEL,revision=q.c.REV,
        trust_remote_code=False,torch_dtype=torch.float32,low_cpu_mem_usage=True)
    q.need(model.config._commit_hash==q.c.REV,'REVISION')
    model.config.use_cache=False;model=get_peft_model(model,q.t.lora_config())
    named=[(n,v) for n,v in model.named_parameters() if v.requires_grad]
    params=[v for n,v in named];opt=torch.optim.AdamW(params,lr=.0002,weight_decay=0.)
    manifest=q.a.check_sources(root/'original',root/'results/pilot14-result.json')
    q.need(q.r.tensor_hash([(n,v) for n,v in model.named_parameters() if not v.requires_grad])==manifest['frozen_base_sha'],'FROZEN_BASE')
    q.need(q.r.tensor_hash(named)==manifest['initial_adapter_sha'],'INITIAL_ADAPTER')
    checkpoint=root/'checkpoints/step-0001'
    if mode=='reference':
        model.train()
        q.t.optimizer_step(model,opt,params,q.t.collate(tok,enc,batches[0]),'adaptive')
        q.state.save(model,opt,checkpoint,context,1)
    else:
        q.need(q.state.load(model,opt,checkpoint,context)==1,'CURSOR')
    model.train()
    stats=q.t.optimizer_step(model,opt,params,q.t.collate(tok,enc,batches[1]),'adaptive')
    signature=dict(adapter=q.r.tensor_hash(named),optimizer=q.stable(opt.state_dict()),
                   rng=q.stable(q.state.rng()),loss=stats)
    if mode=='reference':
        (root/'reference.json').write_text(json.dumps(signature,indent=2))
    else:
        expected=json.loads((root/'reference.json').read_text())
        q.need(signature==expected,'NEW_PROCESS_CONTINUATION_MISMATCH')
    q.need(q.state.load(model,opt,checkpoint,context)==1,'RESTORE_CURSOR')
    saved=json.loads((checkpoint/'manifest.json').read_text())
    q.need(q.state.tensor_hash(named)==saved['trainable_sha'],'ROLLBACK')
    if mode=='verify':
        report=dict(status='REAL_QWEN_ONE_STEP_CHECKPOINT_NEW_PROCESS_EXACT',
            model=q.c.MODEL,revision=q.c.REV,torch=torch.__version__,
            snapshot_completed_updates=1,total_test_optimizer_updates=3,
            same_next_loss_parameters_optimizer_rng=True,rollback_exact=True,
            historical_128_checkpoint_reproduced=False,semantic_skill_tested=False,
            retained_scientific_updates=0,promotion_authorized=False,
            new_process_seconds=time.monotonic()-started,signature=signature)
        (root/'continuity28.json').write_text(json.dumps(report,indent=2))
        print(json.dumps(report,indent=2),flush=True)
    else:print('CONTINUITY28_REFERENCE_SAVED',flush=True)

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('mode',choices=['reference','verify'])
    run(parser.parse_args().mode)
