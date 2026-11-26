"""First atomic equality diagnostic. Frozen Qwen; no weight updates."""
import hashlib, json, random
from pathlib import Path

MODEL = 'Qwen/Qwen2.5-0.5B-Instruct'
REV = 'c89bee90d9f811437d9735454613c35b4a3c4dc8'
DEMO = 'Examples:\nA A -> Yes\nA B -> No\n'
PAIRS = [('C','C'),('D','D'),('E','E'),('F','F'),('C','D'),('D','C'),('E','F'),('F','E')]

def rows():
    out = [dict(a=a,b=b,gold='Yes' if a==b else 'No') for a,b in PAIRS]
    random.Random(33).shuffle(out)
    return out

def prompt(row, arm):
    return 'Are these two characters identical? Answer Yes or No only.\n'+(DEMO if arm=='examples' else '')+row['a']+' '+row['b']+' ->'

def score(rows, answers):
    assert len(rows)==len(answers)==8
    correct = [a.strip()==r['gold'] for r,a in zip(rows,answers)]
    by = {k:sum(ok for r,ok in zip(rows,correct) if r['gold']==k) for k in ('Yes','No')}
    paired = sum(all(ok for r,ok in zip(rows,correct) if r['a']==c) for c in 'CDEF')
    return dict(correct=sum(correct),total=8,by_class=by,paired_both=paired,all_correct=all(correct))

def selftest():
    z=rows()
    assert len({(r['a'],r['b']) for r in z})==8
    assert set('AB').isdisjoint({r[k] for r in z for k in ('a','b')})
    assert score(z,[r['gold'] for r in z])['paired_both']==4
    for answer in ('Yes','No'):
        s=score(z,[answer]*8)
        assert s['correct']==4 and s['paired_both']==0
    assert score(z,['No' if r['gold']=='Yes' else 'Yes' for r in z])['correct']==0

def run():
    selftest()
    import torch
    from transformers import AutoTokenizer, AutoModelForCausalLM
    torch.set_num_threads(2)
    tok=AutoTokenizer.from_pretrained(MODEL,revision=REV,trust_remote_code=False)
    model=AutoModelForCausalLM.from_pretrained(MODEL,revision=REV,trust_remote_code=False,torch_dtype=torch.float32,low_cpu_mem_usage=True)
    assert model.config._commit_hash==REV
    model.requires_grad_(False).eval()
    z=rows()
    report=dict(model=MODEL,revision=REV,scope='development only, tiny public cohort, not independent',optimizer_updates=0,promotion_authorized=False,rows=z,arms={})
    for arm in ('direct','examples'):
        answers=[]
        traces=[]
        for row in z:
            p=prompt(row,arm)
            inp=tok(tok.apply_chat_template([dict(role='user',content=p)],tokenize=False,add_generation_prompt=True),return_tensors='pt',add_special_tokens=False)
            with torch.inference_mode():
                out=model.generate(**inp,do_sample=False,max_new_tokens=6,pad_token_id=tok.eos_token_id)
            raw=tok.decode(out[0,inp['input_ids'].shape[1]:],skip_special_tokens=True,clean_up_tokenization_spaces=False)
            answers.append(raw)
            traces.append(dict(prompt=p,prompt_sha=hashlib.sha256(p.encode()).hexdigest(),raw=raw))
        report['arms'][arm]=dict(score=score(z,answers),traces=traces)
        Path('/tmp/atomic-equality33').mkdir(exist_ok=True)
        Path('/tmp/atomic-equality33/result.json').write_text(json.dumps(report,indent=2))
    print(json.dumps(report,indent=2))

if __name__=='__main__':
    import sys
    if sys.argv[1:]==['selftest']:
        selftest()
        print('ATOMIC_EQUALITY33 offline controls passed')
    else:
        assert not sys.argv[1:]
        run()
