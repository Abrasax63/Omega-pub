#!/usr/bin/env python3
"""APERCEPT01. Active symbolic observation and reversible finite representations.

No generative model, web, user input, imported oracle, or acquired training.
Policies can only query a sensor and update a public predeclared hypothesis library.
"""
from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import dataclass
import hashlib
import json
import math
from pathlib import Path
from typing import Callable

from make_worlds import library, generate, N

HERE = Path(__file__).resolve().parent
EXPECTED_SHA256 = 'a3c629350ac2afbf68d48ed4dd4a58ef5a25990cd2a695382df380a7897a2c1f'
POLICIES = ('A_fixed_lookup','B_fixed_versions','C_coverage_lookup',
            'D_balanced_disagreement','E_classical_disagreement')
FIXED_QUERIES = (0,3,6,9,12)
BUDGET = 5


def frozen_worlds():
    path=HERE/'FROZEN_WORLDS.json'
    if not path.exists():
        raise FileNotFoundError('Run python make_worlds.py to generate the frozen input.')
    raw=path.read_bytes()
    if hashlib.sha256(raw).hexdigest()!=EXPECTED_SHA256:
        raise ValueError('FROZEN_WORLD_SHA256_MISMATCH')
    worlds=json.loads(raw)
    assert len(worlds['problems'])==96 and worlds['seed']==20261119
    return worlds


def survivors_after(lib,observations):
    return {family:[row for row in rows if all(row[x]==y for x,y in observations.items())]
            for family,rows in lib.items()}


def flatten(survivors):
    return [row for candidates in survivors.values() for row in candidates]


def entropy(probabilities):
    return -sum(p*math.log2(p) for p in probabilities if p>0)


def disagreement_choice(survivors,observations,balanced):
    remaining=[x for x in range(N) if x not in observations]
    occupied={family:rows for family,rows in survivors.items() if rows}
    if not occupied:
        return coverage_choice(observations)
    best_x,best_score=None,-1.0
    for x in remaining:
        probs=[0.0]*4
        if balanced:
            for rows in occupied.values():
                weight=1/(len(occupied)*len(rows))
                for row in rows:
                    probs[row[x]]+=weight
        else:
            rows=flatten(occupied)
            for row in rows:
                probs[row[x]]+=1/len(rows)
        score=entropy(probs)
        if score>best_score+1e-12:
            best_x,best_score=x,score
    return best_x


def coverage_choice(observations):
    remaining=[x for x in range(N) if x not in observations]
    if not observations:
        return remaining[0]
    return max(remaining,key=lambda x:(min(abs(x-z) for z in observations),-x))


def nearest_guess(x,observations):
    if not observations:
        return 0
    closest=min(observations,key=lambda z:(abs(x-z),z))
    return observations[closest]


def infer(x,observations,survivors,policy):
    if x in observations:
        return observations[x],True,'OBSERVED'
    if policy in ('A_fixed_lookup','C_coverage_lookup'):
        return nearest_guess(x,observations),False,'NONPARAMETRIC_GUESS'
    rows=flatten(survivors)
    if not rows:
        return nearest_guess(x,observations),False,'OUT_OF_MODEL'
    frequencies=Counter(row[x] for row in rows)
    best=max(frequencies.values())
    choice=min(y for y,count in frequencies.items() if count==best)
    return choice,len(frequencies)==1,'VERSION_SPACE'


def choose_query(policy,step,observations,survivors):
    if policy in ('A_fixed_lookup','B_fixed_versions'):
        return FIXED_QUERIES[step]
    if policy=='C_coverage_lookup':
        return coverage_choice(observations)
    if policy=='D_balanced_disagreement':
        return disagreement_choice(survivors,observations,balanced=True)
    if policy=='E_classical_disagreement':
        return disagreement_choice(survivors,observations,balanced=False)
    raise ValueError('UNSUPPORTED_POLICY')


def run_episode(policy:str, probe:Callable[[int],int], lib, *, budget=BUDGET):
    """Policy has only a callable probe. The truth table is never passed to it."""
    if policy not in POLICIES or budget<1 or budget>N:
        raise ValueError('INVALID_POLICY_OR_BUDGET')
    seen={}
    trace=[]
    for step in range(budget):
        candidates=survivors_after(lib,seen)
        x=choose_query(policy,step,seen,candidates)
        if x in seen or not 0<=x<N:
            raise AssertionError('REPEATED_OR_INVALID_OBSERVATION')
        y=probe(x)
        if type(y)!=int or not 0<=y<4:
            raise ValueError('INVALID_SENSOR_READING')
        trace.append({'step':step+1,'x':x,'observed_y':y,
                      'remaining_hypotheses_before':sum(map(len,candidates.values()))})
        seen[x]=y
    candidates=survivors_after(lib,seen)
    predictions={x:infer(x,seen,candidates,policy) for x in range(N)}
    return {'queries':trace, 'observations':seen, 'predictions':predictions,
            'surviving_by_family':{f:len(rows) for f,rows in candidates.items()}}


def evaluate():
    worlds=frozen_worlds()
    lib=library()
    details=[]
    for world in worlds['problems']:
        truth=tuple(world['y'])
        for policy in POLICIES:
            accesses=[]
            def probe(x):
                accesses.append(x)
                return truth[x]
            outcome=run_episode(policy,probe,lib)
            assert len(accesses)==BUDGET and len(set(accesses))==BUDGET
            assert accesses==[x['x'] for x in outcome['queries']]
            observed=set(accesses)
            unseen=[x for x in range(N) if x not in observed]
            assert len(unseen)==N-BUDGET
            pred=outcome['predictions']
            unseen_correct=sum(pred[x][0]==truth[x] for x in unseen)
            safe_count=sum(pred[x][1] for x in unseen)
            safe_errors=sum(pred[x][1] and pred[x][0]!=truth[x] for x in unseen)
            out_count=sum(pred[x][2]=='OUT_OF_MODEL' for x in unseen)
            details.append({
                'case_id':world['id'],'category':world['kind'],'policy':policy,
                'unseen_correct':unseen_correct,'unseen_total':len(unseen),
                'safe_unseen':safe_count,'false_safe_unseen':safe_errors,
                'out_of_model_unseen':out_count,
                'full_correct':unseen_correct+BUDGET,
                'query_indices':accesses,'query_trace':outcome['queries'],
                'remaining_hypotheses':sum(outcome['surviving_by_family'].values()),
                'remaining_by_family':outcome['surviving_by_family'],
                'unseen_predictions':[{'x':x,'y_pred':pred[x][0], 'true_y':truth[x],
                                       'unanimous':pred[x][1],'status':pred[x][2]} for x in unseen],
            })
    summaries={}
    for cat in ['all','in_family','out_of_library']+sorted(k for k in lib):
        summaries[cat]={}
        for policy in POLICIES:
            group=[d for d in details if d['policy']==policy and
                   (cat=='all' or (cat=='in_family' and d['category']!='out_of_library') or d['category']==cat)]
            total=sum(d['unseen_total'] for d in group)
            correct=sum(d['unseen_correct'] for d in group)
            summaries[cat][policy]={
                'n_worlds':len(group),'unseen_correct':correct,'unseen_total':total,
                'unseen_accuracy':round(correct/total,6) if total else None,
                'safe_unseen':sum(d['safe_unseen'] for d in group),
                'false_safe_unseen':sum(d['false_safe_unseen'] for d in group),
                'out_of_model_unseen':sum(d['out_of_model_unseen'] for d in group),
            }
    paired={}
    for policy in POLICIES:
        if policy=='D_balanced_disagreement':continue
        delta=[d['unseen_correct']-next(e['unseen_correct'] for e in details
                if e['case_id']==d['case_id'] and e['policy']==policy)
                for d in details if d['policy']=='D_balanced_disagreement']
        paired['D_minus_'+policy]={'n':len(delta),'sum_extra_correct_unseen':sum(delta),
            'mean_extra_correct_unseen':round(sum(delta)/len(delta),6),
            'D_wins':sum(v>0 for v in delta), 'D_ties':sum(v==0 for v in delta),
            'D_losses':sum(v<0 for v in delta)}
    output={'experiment':'APERCEPT01','classification':'SYNTHETIC_SYMBOLIC_ACTIVE_OBSERVATION',
            'frozen_world_sha256':EXPECTED_SHA256,'budget':BUDGET,
            'family_candidate_counts':{f:len(rows) for f,rows in lib.items()},
            'summaries':summaries,'paired':paired,'episodes':details,
            'limitations':['No sensory vision/audio', 'No language comprehension',
              'No representation invention; finite predeclared family selection',
              'Heldout positions differ by policy', 'Synthetic worlds and deterministic seed',
              'No noisy readings or calibrated probability',
              'A correct version-space consensus is conditional on correct model specification']}
    return output


def main():
    report=evaluate()
    data=(json.dumps(report,ensure_ascii=False,sort_keys=True,indent=2)+'\n').encode()
    path=HERE/'RUN_RESULTS.json'
    path.write_bytes(data)
    print('Results:',path,'sha256='+hashlib.sha256(data).hexdigest())
    for scope in ('all','in_family','out_of_library'):
        print('\n',scope)
        for policy,v in report['summaries'][scope].items():
            print(policy,v['unseen_correct'],'/',v['unseen_total'],
                  f"acc={v['unseen_accuracy']}",'safe=',v['safe_unseen'],
                  'false-safe=',v['false_safe_unseen'],'out-of-model=',v['out_of_model_unseen'])
    print('\nPaired:',json.dumps(report['paired'],ensure_ascii=False))


if __name__=='__main__':
    main()
