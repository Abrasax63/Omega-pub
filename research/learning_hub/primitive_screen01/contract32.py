"""Prompt intervention on 8 consumed MICRO31 dev questions; zero weight updates.
Unlike PILOT14's post-hoc parser diagnostic, strict scoring is unchanged.
Explicit contract versus token-matched neutral instruction is the primary comparison.
"""
import json,os,time,traceback
from pathlib import Path
import microlearn31 as m
q=m.q
ARMS={'original':'','neutral':'\nPlease answer the question as requested.',
      'explicit':'\nAnswer with the selected word only.'}
PROTOCOL=dict(seed=m.SEED,model=q.c.MODEL,revision=q.c.REV,questions=8,
    consumed_development=True,final_exam_accessed=False,optimizer_updates=0,
    max_generations=24,max_new_tokens=12,max_seconds=120,
    primary_comparison=['explicit','neutral'],format_gain_min=2,
    strict_correct_gain_min=2,pair_gain_min=1,independent_curator=False,
    learning_demonstrated=False,promotion_authorized=False)

def metrics(rows,predictions):
    score=m.score(rows,predictions);idx={r['id']:r for r in rows}
    valid=sum(z['raw'].strip() in idx[z['id']]['items'] for z in predictions)
    score.update(in_contract=valid,out_of_contract=len(rows)-valid,
        wrong_in_list_word=sum(z['raw'].strip() in idx[z['id']]['items'] and
            z['raw'].strip()!=m.oracle(idx[z['id']]) for z in predictions))
    return score

def run():
    import torch
    from transformers import AutoTokenizer,AutoModelForCausalLM
    from peft import get_peft_model
    root=Path(os.environ['OMEGA_CHECKPOINT_ROOT']);root.mkdir(mode=0o700,parents=True,exist_ok=False)
    started=time.monotonic();torch.set_num_threads(2);torch.manual_seed(q.t.SEED)
    rows=[r for r in m.subset('dev',m.SEED+1,1) if r['kind']=='select']
    q.need(len(rows)==8 and all(m.oracle(r)==r['gold'] for r in rows),'COHORT')
    # No call to datasets()/holdout generator: the final cohort is not constructed.
    conditions={arm:[dict(r,prompt=r['prompt']+suffix) for r in rows] for arm,suffix in ARMS.items()}
    tok=AutoTokenizer.from_pretrained(q.c.MODEL,revision=q.c.REV,trust_remote_code=False)
    def encode(row):
        text=tok.apply_chat_template([{'role':'user','content':row['prompt']}],tokenize=False,add_generation_prompt=True)
        return tok(text,return_tensors='pt',add_special_tokens=False)
    lengths={arm:[encode(r)['input_ids'].shape[1] for r in z] for arm,z in conditions.items()}
    q.need(lengths['explicit']==lengths['neutral'],'NEUTRAL_TOKEN_MISMATCH')
    q.need(max(n for z in lengths.values() for n in z)+PROTOCOL['max_new_tokens']<=q.t.MAX_LENGTH,'CONTEXT')
    m.write(root/'protocol.json',dict(PROTOCOL,arm_suffixes=ARMS,input_lengths=lengths,
        cohort_sha=q.c.digest(rows),statement='Consumed development diagnostic; not a new qualification exam.'))
    model=AutoModelForCausalLM.from_pretrained(q.c.MODEL,revision=q.c.REV,
        trust_remote_code=False,torch_dtype=torch.float32,low_cpu_mem_usage=True)
    q.need(model.config._commit_hash==q.c.REV,'MODEL_PIN');model.config.use_cache=False
    model=get_peft_model(model,q.t.lora_config());model.eval()
    named=[(n,v) for n,v in model.named_parameters() if v.requires_grad]
    frozen=[(n,v) for n,v in model.named_parameters() if not v.requires_grad]
    initial=q.r.tensor_hash(named);base=q.r.tensor_hash(frozen)
    q.need(initial=='ada15cb69b933f9ef394f77a94c635819e489ed17a31ddc78877b786dee89846','INITIAL_ADAPTER')
    q.need(base=='61583ad3b25e36f5bf13c7c044b7d5f7bff17a99c588a20593ab907c6b8f7252','FROZEN_BASE')
    pred={arm:[] for arm in ARMS}
    result=dict(status='RUNNING',protocol=PROTOCOL,initial_adapter_sha=initial,
        frozen_base_sha=base,runtime=q.state.runtime_fingerprint(model),generations=0,
        neutral_and_explicit_input_tokens_matched=True,
        source_sha={name:q.r.sha(Path(__file__).parent/name) for name in
            ('contract32.py','microlearn31.py','curriculum06.py','trainer07.py','resume25.py')})
    def flush():
        result['seconds']=time.monotonic()-started;m.write(root/'result.json',result)
    try:
        # Rotate arm order per question; do not compare these timings as a benchmark.
        names=list(ARMS)
        for i in range(len(rows)):
            for j in range(len(names)):
                if time.monotonic()-started>=PROTOCOL['max_seconds']:raise TimeoutError('DIAGNOSTIC_TIME_CAP')
                arm=names[(i+j)%len(names)];row=conditions[arm][i];inputs=encode(row)
                n=inputs['input_ids'].shape[1]
                with torch.inference_mode():ids=model.generate(**inputs,do_sample=False,
                    max_new_tokens=PROTOCOL['max_new_tokens'],pad_token_id=tok.eos_token_id)[0,n:].tolist()
                pred[arm].append(dict(id=row['id'],prompt_sha=q.r.digest(row['prompt']),
                    raw=tok.decode(ids,skip_special_tokens=True,clean_up_tokenization_spaces=False),
                    input_tokens=n,output_tokens=len(ids)))
                result['generations']+=1;m.write(root/(arm+'-predictions.json'),pred[arm]);flush()
        scores={arm:metrics(conditions[arm],pred[arm]) for arm in ARMS}
        explicit,neutral=scores['explicit'],scores['neutral']
        fd=explicit['in_contract']-neutral['in_contract'];cd=explicit['correct']-neutral['correct'];pd=explicit['pairs']-neutral['pairs']
        format_signal=fd>=2;response_signal=cd>=2 and pd>=1
        verdict=('FORMAT_AND_STRICT_SELECTION_SIGNAL' if format_signal and response_signal else
            'FORMAT_SIGNAL_WITHOUT_STRICT_SELECTION_SIGNAL' if format_signal else
            'STRICT_SELECTION_SIGNAL_WITHOUT_FORMAT_SIGNAL' if response_signal else 'NO_DISCRIMINATING_SIGNAL')
        result.update(status='CONTRACT32_DIAGNOSTIC_COMPLETE',scores=scores,
            explicit_minus_neutral=dict(in_contract=fd,correct=cd,pairs=pd),
            format_signal=format_signal,strict_selection_signal=response_signal,verdict=verdict,
            learning_demonstrated=False,retention_tested=False,final_exam_accessed=False,
            optimizer_updates=0,promotion_authorized=False,
            measured_token_counts={arm:{'input':sum(z['input_tokens'] for z in v),
                'output':sum(z['output_tokens'] for z in v)} for arm,v in pred.items()})
    except Exception as error:
        result.update(status='DIAGNOSTIC_FAILED',error=str(error),traceback=traceback.format_exc())
    finally:
        result['weights_unchanged']=q.r.tensor_hash(named)==initial and q.r.tensor_hash(frozen)==base
        flush()
    print(json.dumps({k:result.get(k) for k in ('status','generations','scores','verdict','explicit_minus_neutral','weights_unchanged','seconds')},indent=2),flush=True)
    q.need(result['status']=='CONTRACT32_DIAGNOSTIC_COMPLETE' and result['weights_unchanged'],'DIAGNOSTIC_INCOMPLETE_OR_MUTATED')

if __name__=='__main__':run()
