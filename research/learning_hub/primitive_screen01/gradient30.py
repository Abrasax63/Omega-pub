"""Detailed first-backward diagnostics; no optimizer update or raw-gradient export."""
import json,math,os,time
from pathlib import Path
import private_checkpoint27 as q
import numerics29 as previous

def norm64(gradients):
    return math.sqrt(math.fsum(float(v)*float(v) for g in gradients for v in g.reshape(-1).tolist()))

def measure(gradients,foreach,threads):
    import torch
    torch.set_num_threads(threads)
    shadow=[]
    for g in gradients:
        p=torch.nn.Parameter(torch.zeros_like(g));p.grad=g.clone();shadow.append(p)
    measured=torch.nn.utils.clip_grad_norm_(shadow,1.0,error_if_nonfinite=True,foreach=foreach)
    return dict(foreach=foreach,threads=threads,norm=float(measured),
        applied_coefficient=float(torch.clamp(1.0/(measured+1e-6),max=1.0)),
        clipped_norm64=norm64([p.grad for p in shadow]),
        clipped_gradient_sha=q.r.tensor_hash([(str(i),p.grad) for i,p in enumerate(shadow)]))

def run():
    import torch
    from transformers import AutoTokenizer,AutoModelForCausalLM
    from peft import get_peft_model
    root=Path(os.environ['OMEGA_CHECKPOINT_ROOT']);started=time.monotonic()
    torch.set_num_threads(2);torch.manual_seed(q.t.SEED)
    tok=AutoTokenizer.from_pretrained(q.c.MODEL,revision=q.c.REV,trust_remote_code=False)
    rows,enc,plans,_=q.p.plan_audit(tok,root/'budget/realbudget10.json')
    model=AutoModelForCausalLM.from_pretrained(q.c.MODEL,revision=q.c.REV,
        trust_remote_code=False,torch_dtype=torch.float32,low_cpu_mem_usage=True)
    q.need(model.config._commit_hash==q.c.REV,'REVISION')
    model.config.use_cache=False;model=get_peft_model(model,q.t.lora_config())
    named=[(n,v) for n,v in model.named_parameters() if v.requires_grad]
    manifest=q.a.check_sources(root/'original',root/'results/pilot14-result.json')
    initial=q.r.tensor_hash(named)
    frozen=q.r.tensor_hash([(n,v) for n,v in model.named_parameters() if not v.requires_grad])
    q.need(initial==manifest['initial_adapter_sha'],'INITIAL_ADAPTER')
    q.need(frozen==manifest['frozen_base_sha'],'FROZEN_BASE')
    ids=plans['adaptive']['batches'][0];batch=q.t.collate(tok,enc,ids)
    model.train();out=model(input_ids=batch['input_ids'],attention_mask=batch['attention_mask'],use_cache=False)
    logits_sha=q.r.tensor_hash([('logits',out.logits)])
    loss,ce,hinge=q.t.loss_parts(out.logits,batch['labels'],'adaptive')
    loss.backward()
    q.need(all(v.grad is not None for n,v in named),'MISSING_GRADIENT')
    q.need(all(bool(torch.isfinite(v.grad).all()) for n,v in named),'NONFINITE_GRADIENT')
    gradients=[v.grad.detach().clone() for n,v in named]
    gradient_sha=q.r.tensor_hash([(n,g) for (n,v),g in zip(named,gradients)])
    tensors=[]
    for (name,v),g in zip(named,gradients):
        tensors.append(dict(parameter=name,shape=list(g.shape),dtype=str(g.dtype),
            finite=True,nonzero=int(torch.count_nonzero(g)),elements=g.numel(),
            norm32=float(torch.linalg.vector_norm(g)),norm64=norm64([g]),
            min=float(g.min()),max=float(g.max()),max_abs=float(g.abs().max()),
            gradient_sha=q.r.tensor_hash([(name,g)])))
    measurements=[measure(gradients,foreach,threads) for threads in (2,1) for foreach in (None,True,False)]
    torch.set_num_threads(2)
    q.need(q.r.tensor_hash([(n,v.grad) for n,v in named])==gradient_sha,'DIAGNOSTIC_MUTATED_GRADIENTS')
    q.need(q.r.tensor_hash(named)==initial,'DIAGNOSTIC_CHANGED_PARAMETERS')
    historical=manifest['transaction']['stats'][0]
    current=dict(loss=float(loss.detach()),ce=float(ce.detach()),hinge=float(hinge.detach()))
    distinct=sorted({z['norm'] for z in measurements})
    matches=[dict(foreach=z['foreach'],threads=z['threads']) for z in measurements if z['norm']==historical['grad_norm']]
    report=dict(status='GRADIENT30_FIRST_BACKWARD_DIAGNOSTIC_COMPLETE',
        model=q.c.MODEL,revision=q.c.REV,environment=previous.environment(model),
        initial_adapter_sha=initial,frozen_base_sha=frozen,batch_ids=ids,
        encoded_batch_sha=q.stable(batch),logits_sha=logits_sha,
        forward_metrics=current,historical_first_step=historical,
        forward_metrics_match_historical=all(current[k]==historical[k] for k in current),
        gradient_sha=gradient_sha,gradient_tensors=len(tensors),
        gradient_elements=sum(z['elements'] for z in tensors),
        all_gradients_finite=True,gradient_tensors_detail=tensors,
        norm_variants=measurements,distinct_norms=distinct,
        python_fsum_norm64=norm64(gradients),historical_norm_matching_variants=matches,
        norm_variant_effect_observed=len(distinct)>1,
        first_gradient_passes=1,optimizer_updates=0,evaluation_generations=0,
        raw_gradients_exported=False,weights_exported=False,parameters_unchanged=True,
        historical_raw_gradients_available=False,
        precise_historical_cause_confirmed=False,semantic_competence_tested=False,
        promotion_authorized=False,seconds=time.monotonic()-started,
        source_sha={name:q.r.sha(Path(__file__).parent/name) for name in
            ('gradient30.py','numerics29.py','private_checkpoint27.py','trainer07.py')},
        limit='Norm variants reuse exactly the same current raw gradients. Historical raw gradients are unavailable; a matching scalar alone would not establish the historical cause.')
    previous.write(root/'gradient30.json',report)
    print(json.dumps({k:v for k,v in report.items() if k in
        ('status','gradient_tensors','gradient_elements','distinct_norms','python_fsum_norm64',
         'historical_norm_matching_variants','norm_variant_effect_observed','seconds','optimizer_updates')},indent=2),flush=True)

if __name__=='__main__':run()
