"""Paired two-update diagnostic: omitted versus low-memory model loading.
No reconstruction, evaluation generations, saved weights, or promotion.
"""
import argparse, importlib.metadata, json, os, platform, random, time
from pathlib import Path
import private_checkpoint27 as q

def load(path):
    return json.loads(Path(path).read_text())

def write(path,value):
    Path(path).write_text(json.dumps(value,indent=2,allow_nan=False))

def environment(model):
    import torch
    packages={name:importlib.metadata.version(name) for name in
        ('torch','transformers','peft','accelerate','safetensors','huggingface_hub','numpy','tokenizers')}
    cpu={}
    for line in Path('/proc/cpuinfo').read_text().splitlines():
        if ':' in line:
            key,value=map(str.strip,line.split(':',1))
            if key in ('vendor_id','model name','flags') and key not in cpu:cpu[key]=value
    return dict(python=platform.python_version(),machine=platform.machine(),packages=packages,
        cpu=cpu,torch_build=torch.__config__.show(),threads=torch.get_num_threads(),
        interop_threads=torch.get_num_interop_threads(),
        cpu_capability=torch.backends.cpu.get_cpu_capability(),
        mkldnn_enabled=torch.backends.mkldnn.enabled,
        deterministic_algorithms=torch.are_deterministic_algorithms_enabled(),
        matmul_precision=torch.get_float32_matmul_precision(),
        attention_implementation=model.config._attn_implementation,
        model_attention_dropout=model.config.attention_dropout)

def arm(name):
    import numpy as np
    import torch
    from transformers import AutoTokenizer,AutoModelForCausalLM
    from peft import get_peft_model
    root=Path(os.environ['OMEGA_CHECKPOINT_ROOT'])
    started=time.monotonic();torch.set_num_threads(2);torch.manual_seed(q.t.SEED)
    random.seed(q.t.SEED);np.random.seed(q.t.SEED)
    tok=AutoTokenizer.from_pretrained(q.c.MODEL,revision=q.c.REV,trust_remote_code=False)
    rows,enc,plans,_=q.p.plan_audit(tok,root/'budget/realbudget10.json')
    batches=plans['adaptive']['batches'][:2]
    kwargs=dict(revision=q.c.REV,trust_remote_code=False,torch_dtype=torch.float32)
    if name=='low_memory':kwargs['low_cpu_mem_usage']=True
    model=AutoModelForCausalLM.from_pretrained(q.c.MODEL,**kwargs)
    q.need(model.config._commit_hash==q.c.REV,'REVISION')
    model.config.use_cache=False;model=get_peft_model(model,q.t.lora_config())
    named=[(n,v) for n,v in model.named_parameters() if v.requires_grad]
    params=[v for n,v in named]
    manifest=q.a.check_sources(root/'original',root/'results/pilot14-result.json')
    initial=q.r.tensor_hash(named)
    frozen=q.r.tensor_hash([(n,v) for n,v in model.named_parameters() if not v.requires_grad])
    q.need(initial==manifest['initial_adapter_sha'],'INITIAL_ADAPTER')
    q.need(frozen==manifest['frozen_base_sha'],'FROZEN_BASE')
    opt=torch.optim.AdamW(params,lr=.0002,weight_decay=0.)
    start=dict(initial_adapter_sha=initial,frozen_base_sha=frozen,batch_ids=batches,
        encoded_batch_sha=q.stable([q.t.collate(tok,enc,z) for z in batches]),
        torch_rng_sha=q.stable(torch.random.get_rng_state()),
        data_sha=q.r.digest(json.dumps(rows,sort_keys=True)),
        tokenizer_sha=q.r.digest(tok.backend_tokenizer.to_str()))
    model.train();trace=[]
    for i,ids in enumerate(batches):
        stats=q.t.optimizer_step(model,opt,params,q.t.collate(tok,enc,ids),'adaptive')
        trace.append(dict(update=i+1,stats=stats,adapter_sha=q.r.tensor_hash(named),
            optimizer_sha=q.stable(opt.state_dict()),torch_rng_sha=q.stable(torch.random.get_rng_state())))
    report=dict(arm=name,loading_argument='omitted' if name=='historical_loader' else True,
        start=start,trace=trace,environment=environment(model),seconds=time.monotonic()-started,
        source_sha={f:q.r.sha(Path(__file__).parent/f) for f in
            ('numerics29.py','private_checkpoint27.py','trainer07.py','pilot14.py','curriculum06.py')},
        model=q.c.MODEL,revision=q.c.REV,optimizer_updates=2,
        historical_stats=manifest['transaction']['stats'][:2],
        retained_scientific_updates=0,promotion_authorized=False)
    write(root/(name+'.json'),report)
    print('NUMERICS29_ARM_COMPLETE',name,report['seconds'],flush=True)

def compare():
    root=Path(os.environ['OMEGA_CHECKPOINT_ROOT'])
    a=load(root/'historical_loader.json');b=load(root/'low_memory.json')
    q.need(a['start']==b['start'],'START_STATE_OR_DATA_MISMATCH')
    q.need(a['environment']==b['environment'],'RUNTIME_MISMATCH')
    q.need(a['source_sha']==b['source_sha'],'SOURCE_MISMATCH')
    q.need(a['historical_stats']==b['historical_stats'],'REFERENCE_MISMATCH')
    matched={x['arm']:all(t['stats']==old for t,old in zip(x['trace'],x['historical_stats'])) for x in (a,b)}
    same=a['trace']==b['trace']
    if same:
        verdict='LOADER_CHANGE_NOT_SUFFICIENT_TO_EXPLAIN_EARLIER_DIVERGENCE'
    elif matched['historical_loader'] and not matched['low_memory']:
        verdict='LOADER_CHANGE_EXPLAINS_METRIC_DIVERGENCE_ON_THIS_TWO_STEP_PREFIX'
    else:
        verdict='LOADER_EFFECT_OBSERVED_BUT_HISTORICAL_CAUSE_UNRESOLVED'
    report=dict(status='NUMERICS29_PAIRED_TWO_STEP_DIAGNOSTIC_COMPLETE',verdict=verdict,
        same_initial_weights_optimizer_rng_data=True,same_runtime_and_sources=True,
        same_two_step_parameters_optimizer_rng_and_metrics=same,
        exact_historical_two_step_metrics=matched,
        historical_runtime_record_available=False,
        historical_loader_means_loading_argument_only=True,
        total_optimizer_updates=4,evaluation_generations=0,
        historical_checkpoint_128_reproduced=False,promotion_authorized=False,
        semantic_competence_tested=False,
        historical_delta={x['arm']:[{k:t['stats'][k]-old[k] for k in t['stats']} for t,old in zip(x['trace'],x['historical_stats'])] for x in (a,b)},
        arm_seconds={x['arm']:x['seconds'] for x in (a,b)},
        performance_comparison_valid=False,
        limit='One paired prefix on one runner; historical dependency and CPU fingerprints were not recorded. No conclusion about all 128 steps or semantic competence.')
    write(root/'numerics29.json',report)
    print(json.dumps(report,indent=2),flush=True)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('mode',choices=['historical_loader','low_memory','compare'])
    args=p.parse_args();compare() if args.mode=='compare' else arm(args.mode)
