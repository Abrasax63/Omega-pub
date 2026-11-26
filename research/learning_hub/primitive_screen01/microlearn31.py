"""Bounded closed-loop selection pilot. Algorithmic feedback, actual LoRA updates.
Four rounds maximum, two matched four-update proposals per round. No promotion.
"""
import argparse,base64,collections,hashlib,json,os,random,time,traceback,zipfile
from pathlib import Path
import private_checkpoint27 as q

SEED=2026112631
CONFIG=dict(seed=SEED,skill='select',max_rounds=4,steps_per_arm=4,
    max_optimizer_updates=32,max_generations=240,max_seconds=420,
    stop_after_rejections=2,dev_target=8,dev_retention=12,
    final_target=16,final_retention=12,min_correct_gain=2,min_pair_gain=1,
    max_new_tokens=12,initial_lr=.0002,final_correct_min=14,
    final_pairs_min=7,final_per_position_min=3,promotion_authorized=False)

def write(path,obj):
    temp=Path(str(path)+'.pending');temp.write_text(json.dumps(obj,indent=2,allow_nan=False));os.replace(temp,path)

def oracle(row):
    k=row['kind'];words=row['items']
    return (' '.join(words) if k=='copy' else ' '.join(reversed(words)) if k=='reverse'
        else dict(enumerate(words,1))[row['pos']] if k=='select'
        else ('Yes' if any(w==row['target'] for w in words) else 'No'))

def subset(split,seed,target_pairs_per_position):
    full=q.c.build(split,seed);q.c.validate(full,split);groups=q.c.groups(full)
    rng=random.Random(seed+100);chosen=[]
    for pos in range(1,5):
        pool=sorted(p for p,z in groups.items() if z[0]['kind']=='select' and z[0]['pos']==pos)
        chosen.extend(rng.sample(pool,target_pairs_per_position))
    for kind in ('copy','membership','reverse'):
        chosen.extend(rng.sample(sorted(p for p,z in groups.items() if z[0]['kind']==kind),2))
    rows=[r for p in chosen for r in groups[p]];rng.shuffle(rows)
    q.need(all(oracle(r)==r['gold'] for r in rows),'ORACLE')
    return rows

def datasets():
    train=q.c.build('train',SEED);q.c.validate(train,'train')
    dev=subset('dev',SEED+1,1);final=subset('holdout',SEED+2,2)
    allsets=[{r['prompt'] for r in z} for z in (train,dev,final)]
    q.need(all(not a&b for i,a in enumerate(allsets) for b in allsets[i+1:]),'SPLIT_OVERLAP')
    q.need(all(oracle(r)==r['gold'] for r in train),'TRAIN_ORACLE')
    return train,dev,final

def score(rows,pred):
    idx={r['id']:r for r in rows};q.need(len(idx)==len(rows),'DUPLICATE_LABEL')
    got={}
    for z in pred:
        q.need(z['id'] in idx and z['id'] not in got,'TRACE_ID')
        q.need(z['prompt_sha']==q.r.digest(idx[z['id']]['prompt']),'PROMPT_HASH')
        got[z['id']]=z['raw'].strip()==oracle(idx[z['id']])
    q.need(set(got)==set(idx),'COVERAGE')
    target=[r for r in rows if r['kind']=='select'];old=[r for r in rows if r['kind']!='select']
    pairs=q.c.groups(target)
    return dict(correct=sum(got[r['id']] for r in target),target_total=len(target),
        pairs=sum(all(got[r['id']] for r in z) for z in pairs.values()),pairs_total=len(pairs),
        by_position={str(p):sum(got[r['id']] for r in target if r['pos']==p) for p in range(1,5)},
        old_correct=sum(got[r['id']] for r in old),old_total=len(old),
        correct_ids=sorted(i for i,v in got.items() if v),
        old_correct_ids=sorted(r['id'] for r in old if got[r['id']]))

def gate(before,after):
    lost=sorted(set(before['old_correct_ids'])-set(after['old_correct_ids']))
    return dict(accepted=after['correct']-before['correct']>=2 and
        after['pairs']-before['pairs']>=1 and not lost,
        correct_gain=after['correct']-before['correct'],pair_gain=after['pairs']-before['pairs'],
        previously_correct_retention_lost=lost)


def format_diagnostic(rows,pred):
    idx={r['id']:r for r in rows};out={k:dict(total=0,in_contract=0,strict_correct=0) for k in q.c.KINDS}
    for z in pred:
        row=idx[z['id']];raw=z['raw'].strip();words=raw.split();k=row['kind']
        valid=(raw in row['items'] if k=='select' else raw in ('Yes','No') if k=='membership'
            else len(words)==len(row['items']) and sorted(words)==sorted(row['items']))
        out[k]['total']+=1;out[k]['in_contract']+=int(valid);out[k]['strict_correct']+=int(raw==oracle(row))
    return out

def matched_pools(tok,train):
    enc=q.t.prepare(tok,train);groups=q.c.groups(train);pool={p:collections.defaultdict(list) for p in range(1,5)}
    for pair,rows in groups.items():
        if rows[0]['kind']!='select':continue
        ids=[r['id'] for r in rows]
        flat=[x for i in ids for x in enc[i]]
        signature=(sum(len(x['input_ids']) for x in flat),
            sum(enc[i][0]['target_tokens'] for i in ids),sum(enc[i][1]['target_tokens'] for i in ids))
        pool[rows[0]['pos']][signature].append(pair)
    keys=set.intersection(*(set(pool[p]) for p in pool))
    q.need(bool(keys),'NO_MATCHED_TOKEN_BUDGET')
    signature=max(sorted(keys),key=lambda key:(min(len(pool[p][key]) for p in pool),sum(len(pool[p][key]) for p in pool)))
    return enc,groups,{p:sorted(pool[p][signature]) for p in pool},signature

def seal(root,checkpoint,controller,data):
    from cryptography.hazmat.primitives import hashes,serialization
    from cryptography.hazmat.primitives.asymmetric import padding
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
    private=root/'private-checkpoint.zip'
    with zipfile.ZipFile(private,'w',zipfile.ZIP_DEFLATED) as z:
        for f in checkpoint.iterdir():z.write(f,'checkpoint/'+f.name)
        z.writestr('controller.json',json.dumps(controller,indent=2))
        z.writestr('datasets.json',json.dumps(data))
    private.chmod(0o600);raw=private.read_bytes()
    public=(Path(__file__).parent/'RESUME27_PUBLIC.pem').read_bytes()
    pub=serialization.load_pem_public_key(public);key=AESGCM.generate_key(bit_length=256)
    nonce=os.urandom(12);aad=b'OMEGA-MICROLEARN31-v1'
    encrypted=AESGCM(key).encrypt(nonce,raw,aad);out=root/'encrypted';out.mkdir(mode=0o700,exist_ok=True)
    (out/'checkpoint.aesgcm').write_bytes(encrypted)
    wrapped=pub.encrypt(key,padding.OAEP(mgf=padding.MGF1(hashes.SHA256()),algorithm=hashes.SHA256(),label=None))
    write(out/'envelope.json',dict(schema=1,algorithm='RSA-OAEP-SHA256+AES-256-GCM',
        wrapped_key=base64.b64encode(wrapped).decode(),nonce=base64.b64encode(nonce).decode(),
        aad=base64.b64encode(aad).decode(),plaintext_sha256=hashlib.sha256(raw).hexdigest(),
        ciphertext_sha256=hashlib.sha256(encrypted).hexdigest(),public_key_sha256=hashlib.sha256(public).hexdigest(),
        accepted_updates=controller['accepted_updates'],promotion_authorized=False))

class BudgetStop(Exception):pass
class ProtocolStop(Exception):pass

def run():
    import torch
    from transformers import AutoTokenizer,AutoModelForCausalLM
    from peft import get_peft_model
    root=Path(os.environ['OMEGA_CHECKPOINT_ROOT']);root.mkdir(mode=0o700,parents=True,exist_ok=False)
    public=root/'reports';public.mkdir();started=time.monotonic();torch.set_num_threads(2);torch.manual_seed(q.t.SEED)
    data=datasets();train,dev,final=data
    tok=AutoTokenizer.from_pretrained(q.c.MODEL,revision=q.c.REV,trust_remote_code=False)
    enc,groups,pools,token_signature=matched_pools(tok,train)
    context=dict(model=q.c.MODEL,revision=q.c.REV,tokenizer_sha=q.r.digest(tok.backend_tokenizer.to_str()),
        data_sha=q.c.digest(train),plan_sha=q.c.digest(CONFIG))
    model=AutoModelForCausalLM.from_pretrained(q.c.MODEL,revision=q.c.REV,
        trust_remote_code=False,torch_dtype=torch.float32,low_cpu_mem_usage=True)
    q.need(model.config._commit_hash==q.c.REV,'MODEL_PIN');model.config.use_cache=False
    model=get_peft_model(model,q.t.lora_config());model.train()
    named=[(n,v) for n,v in model.named_parameters() if v.requires_grad];params=[v for n,v in named]
    initial=q.r.tensor_hash(named);frozen=q.r.tensor_hash([(n,v) for n,v in model.named_parameters() if not v.requires_grad])
    q.need(initial=='ada15cb69b933f9ef394f77a94c635819e489ed17a31ddc78877b786dee89846','INITIAL_ADAPTER')
    q.need(frozen=='61583ad3b25e36f5bf13c7c044b7d5f7bff17a99c588a20593ab907c6b8f7252','FROZEN_BASE')
    opt=torch.optim.AdamW(params,lr=CONFIG['initial_lr'],weight_decay=0.)
    incumbent=root/'states/initial';q.state.save(model,opt,incumbent,context,0);initial_path=incumbent
    report=dict(status='RUNNING',config=CONFIG,context=context,runtime=q.state.runtime_fingerprint(model),
        initial_adapter_sha=initial,frozen_base_sha=frozen,rows_sha={s:q.c.digest(z) for s,z in zip(('train','dev','final'),data)},
        matched_pair_token_signature=token_signature,matched_pool_sizes={str(p):len(v) for p,v in pools.items()},
        rounds=[],optimizer_updates=0,generations=0,accepted_updates=0,
        independent_curator=False,promotion_authorized=False,scope='new elementary-selection pilot from initial adapter; not a reproduction of PILOT14',
        source_sha={n:q.r.sha(Path(__file__).parent/n) for n in ('microlearn31.py','resume25.py','trainer07.py','curriculum06.py')})
    def flush():
        report['seconds']=time.monotonic()-started;write(public/'result.json',report)
    def budget():
        if time.monotonic()-started>=CONFIG['max_seconds']:raise BudgetStop('WALL_TIME_CAP')
    def evaluate(rows,label):
        mode=model.training;model.eval();pred=[]
        try:
            for row in rows:
                budget()
                if report['generations']>=CONFIG['max_generations']:raise BudgetStop('GENERATION_CAP')
                text=tok.apply_chat_template([{'role':'user','content':row['prompt']}],tokenize=False,add_generation_prompt=True)
                inputs=tok(text,return_tensors='pt',add_special_tokens=False);n=inputs['input_ids'].shape[1]
                q.need(n+CONFIG['max_new_tokens']<=q.t.MAX_LENGTH,'CONTEXT')
                with torch.inference_mode():ids=model.generate(**inputs,do_sample=False,
                    max_new_tokens=CONFIG['max_new_tokens'],pad_token_id=tok.eos_token_id)[0,n:].tolist()
                pred.append(dict(id=row['id'],prompt_sha=q.r.digest(row['prompt']),
                    raw=tok.decode(ids,skip_special_tokens=True,clean_up_tokenization_spaces=False),
                    input_tokens=n,output_tokens=len(ids)))
                report['generations']+=1;write(public/(label+'-predictions.json'),pred)
            report.setdefault('format_diagnostics',{})[label]=format_diagnostic(rows,pred)
            return score(rows,pred)
        finally:model.train(mode);flush()
    lr=CONFIG['initial_lr'];strategy='adaptive';stalls=0;current=None
    try:
        current=evaluate(dev,'initial-dev');report['initial_dev']=current;report['current_dev']=current;flush()
        # Added after the first pilot exposed an uninformative baseline.
        # This is a prospective guard, not a changed verdict for that pilot.
        if current['old_correct']==0:
            raise ProtocolStop('EMPTY_RETENTION_BASELINE_DIAGNOSE_OUTPUT_CONTRACT_FIRST')
        if report['format_diagnostics']['initial-dev']['select']['in_contract']==0:
            raise ProtocolStop('NO_VALID_SELECTION_OUTPUT_DIAGNOSE_CONTRACT_FIRST')
        for round_index in range(CONFIG['max_rounds']):
            if current['correct']==8 and current['pairs']==4:
                report['stop_reason']='DEV_CEILING';break
            budget();round_info=dict(index=round_index+1,learning_rate=lr,loss=strategy,
                incumbent_before=current,arms={},sampling_feedback=dict(current['by_position']))
            report['rounds'].append(round_info);flush()
            # The two proposals differ only by feedback-directed sampling.
            worst=sorted(range(1,5),key=lambda p:(current['by_position'][str(p)],p))
            positions={'fixed':[1,2,3,4], 'targeted':[worst[0],worst[1],worst[0],worst[1]]}
            for arm in ('fixed','targeted'):
                q.state.load(model,opt,incumbent,context)
                for group in opt.param_groups:group['lr']=lr
                chosen=[];steps=[];rng=random.Random(SEED+1000*round_index+(1 if arm=='targeted' else 0))
                for pos in positions[arm]:
                    available=[p for p in pools[pos] if p not in chosen] or pools[pos]
                    chosen.append(rng.choice(available))
                round_info['arms'][arm]=dict(status='TRAINING',train_pairs=chosen,positions=positions[arm],steps=steps)
                flush()
                for pair in chosen:
                    budget();q.need(report['optimizer_updates']<CONFIG['max_optimizer_updates'],'UPDATE_CAP')
                    batch=q.t.collate(tok,enc,[r['id'] for r in groups[pair]])
                    model.train();stats=q.t.optimizer_step(model,opt,params,batch,strategy)
                    report['optimizer_updates']+=1;steps.append(stats);flush()
                observed=evaluate(dev,'round-%d-%s-dev'%(round_index+1,arm));decision=gate(current,observed)
                path=root/('states/round-%d-%s'%(round_index+1,arm))
                q.state.save(model,opt,path,context,report['accepted_updates']+4)
                round_info['arms'][arm]=dict(score=observed,decision=decision,train_pairs=chosen,
                    positions=positions[arm],steps=steps,adapter_sha=q.r.tensor_hash(named),
                    checkpoint=path.name,token_budget_signature=[4*v for v in token_signature])
                flush()
            eligible=[arm for arm,z in round_info['arms'].items() if z['decision']['accepted']]
            if eligible:
                selected=max(eligible,key=lambda arm:(round_info['arms'][arm]['score']['pairs'],
                    round_info['arms'][arm]['score']['correct'],arm=='fixed'))
                incumbent=root/('states/round-%d-%s'%(round_index+1,selected))
                current=round_info['arms'][selected]['score'];report['accepted_updates']+=4;stalls=0
                round_info['selected']=selected;round_info['decision']='ACCEPT_DEVELOPMENT_ONLY'
            else:
                stalls+=1;round_info['selected']=None;round_info['decision']='ROLLBACK'
                if any(z['decision']['previously_correct_retention_lost'] for z in round_info['arms'].values()):
                    lr/=2;round_info['next_adjustment']='HALVE_LEARNING_RATE'
                else:
                    strategy='contrastive' if strategy=='adaptive' else 'adaptive'
                    round_info['next_adjustment']='SWITCH_LOSS_ONLY'
            q.state.load(model,opt,incumbent,context);report['current_dev']=current;flush()
            print('MICROLEARN31_ROUND',round_index+1,round_info['decision'],current['correct'],current['pairs'],flush=True)
            if stalls>=CONFIG['stop_after_rejections']:
                report['stop_reason']='TWO_ROUNDS_WITHOUT_ACCEPTED_GAIN';break
        if report['accepted_updates']:
            # Freeze selection before any final-cohort inference.
            report['selected_adapter_sha']=q.r.tensor_hash(named);flush()
            q.state.load(model,opt,initial_path,context);ref=evaluate(final,'initial-final')
            q.state.load(model,opt,incumbent,context);candidate=evaluate(final,'selected-final')
            lost=sorted(set(ref['old_correct_ids'])-set(candidate['old_correct_ids']))
            report['final']=dict(reference=ref,candidate=candidate,retention_lost=lost,
                exploratory_pass=candidate['correct']>=14 and candidate['pairs']>=7 and
                    min(candidate['by_position'].values())>=3 and not lost and
                    candidate['correct']-ref['correct']>=2 and candidate['pairs']-ref['pairs']>=1,
                consulted_only_after_candidate_freeze=True,independent_curator=False)
        else:report['final']={'status':'NOT_CONSUMED_NO_ACCEPTED_CANDIDATE'}
        report['status']='BOUNDED_MICROLEARNING_COMPLETE'
    except BudgetStop as error:
        report['status']='BUDGET_STOP';report['stop_reason']=str(error)
    except ProtocolStop as error:
        report['status']='BLOCKED_BASELINE';report['stop_reason']=str(error)
    except Exception as error:
        report['status']='TECHNICAL_FAILURE';report['error']=str(error);report['traceback']=traceback.format_exc()
    finally:
        q.state.load(model,opt,incumbent,context)
        report['retained_adapter_sha']=q.r.tensor_hash(named)
        report['incumbent_checkpoint']=incumbent.name;flush()
        seal(root,incumbent,report,dict(zip(('train','dev','final'),data)))
    print(json.dumps({k:report.get(k) for k in ('status','stop_reason','optimizer_updates','generations','accepted_updates','initial_dev','current_dev','final','seconds')},indent=2),flush=True)
    q.need(report['status']!='TECHNICAL_FAILURE','MICROLEARN31_TECHNICAL_FAILURE')

def selftest():
    train,dev,final=datasets();q.need(len(dev)==20 and len(final)==28,'COHORT_SIZE')
    def predictions(rows,modify=None):
        return [dict(id=r['id'],prompt_sha=q.r.digest(r['prompt']),raw=(modify(r) if modify else r['gold'])) for r in rows]
    perfect=score(dev,predictions(dev));q.need(perfect['correct']==8 and perfect['pairs']==4 and perfect['old_correct']==12,'PERFECT')
    constant=score(dev,predictions(dev,lambda r:'Yes'))
    q.need(constant['correct']==0 and constant['pairs']==0,'CONSTANT_REJECTED')
    diagnostic=format_diagnostic(dev,predictions(dev,lambda r:'The answer is '+r['gold']))
    q.need(diagnostic['select']['in_contract']==0 and diagnostic['select']['strict_correct']==0,'VERBOSE_OUTPUT_FLAGGED')
    before=dict(perfect,correct=4,pairs=2)
    q.need(gate(before,perfect)['accepted'],'POSITIVE_GATE')
    regressed=dict(perfect,old_correct_ids=perfect['old_correct_ids'][1:])
    q.need(not gate(before,regressed)['accepted'],'FORGETTING_REJECTED')
    for pred in (predictions(dev)[:-1],predictions(dev)+[predictions(dev)[0]],
        [dict(predictions(dev)[0],prompt_sha='altered')]+predictions(dev)[1:]):
        try:score(dev,pred)
        except ValueError:pass
        else:raise AssertionError('INVALID_TRACE_ACCEPTED')
    print('MICROLEARN31_OFFLINE_CONTROLS_PASSED')

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('cmd',choices=['selftest','run']);args=parser.parse_args()
    selftest() if args.cmd=='selftest' else run()
