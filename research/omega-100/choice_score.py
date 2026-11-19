"""Aggregate solver choices and outcomes without revealing reserved instances."""
from collections import Counter
import json
import random
import statistics
import sys
from pathlib import Path


def summarize(rows):
    assert [r['case'] for r in rows] == list(range(16))
    def stats(runs):
        counts = Counter(run['status'] for run in runs)
        return {**{x:counts[x] for x in ('correct','error','abstain')},
                'steps':sum(run['steps'] for run in runs),
                'solver_seconds':sum(run['seconds'] for run in runs)}
    picks=[]
    for seed in range(8):
        rng = random.Random(seed)
        picks.append([rng.choice('AB') for _ in rows])
    report={}
    for family in ('combined','parity','subset'):
        idx=[i for i,r in enumerate(rows) if family=='combined' or r['family']==family]
        batch=[rows[i] for i in idx]
        fixed = {m:stats([r['fixed'][m] for r in batch]) for m in 'AB'}
        chosen = stats([r['selected'] for r in batch])
        chosen['choices']=dict(Counter(r['selector_choice'] for r in batch))
        chosen['selector_seconds']=sum(r['selector_seconds'] for r in batch)
        chosen['prompt_tokens']=sum(r['tokens']['prompt_tokens'] for r in batch)
        chosen['completion_tokens']=sum(r['tokens']['completion_tokens'] for r in batch)
        random_counts=[sum(rows[i]['fixed'][order[i]]['status']=='correct' for i in idx) for order in picks]
        opportunity=sum(any(row['fixed'][m]['status']=='correct' for m in 'AB') for row in batch)
        report[family]=dict(n=len(batch),fixed=fixed,chosen=chosen,random_correct=random_counts,
                            random_median=statistics.median(random_counts),oracle_policy_ceiling=opportunity)
    def delta(group):
        s=report[group]
        return s['chosen']['correct'] - max(a['correct'] for a in s['fixed'].values())
    combined=report['combined']
    report['threshold_passed']=(delta('combined')>=2 and delta('parity')>=0 and delta('subset')>=1
        and combined['chosen']['correct']>combined['random_median'] and combined['chosen']['error']==0)
    return report


if __name__=='__main__':
    rows=[json.loads(line) for line in Path(sys.argv[1]).read_text().splitlines()]
    print(json.dumps(summarize(rows),indent=2))
