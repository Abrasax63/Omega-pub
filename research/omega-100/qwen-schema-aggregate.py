"""Summarize a paired trial without publishing per-case answers."""
import json
import sys
from collections import Counter
from pathlib import Path

def summarize(rows):
    ordered = {arm:sorted((r for r in rows if r['arm']==arm), key=lambda r:r['case'])
               for arm in ('reference','candidate')}
    reference, candidate = ordered.values()
    assert len(reference) == len(candidate) == 8
    assert [r['case'] for r in reference] == [r['case'] for r in candidate] == list(range(1,9))
    assert [r['expected'] for r in reference] == [r['expected'] for r in candidate]
    def transitions(pairs, left, right):
        return dict(
            gained=sum(a[left]!=a['expected'] and b[right]==b['expected'] for a,b in pairs),
            lost=sum(a[left]==a['expected'] and b[right]!=b['expected'] for a,b in pairs))
    result = {}
    for arm, batch in ordered.items():
        result[arm] = dict(
            format_valid=sum(r['form'] for r in batch),
            ast_faithful=sum(r['verified']!='abstain' for r in batch),
            stop_reasons=dict(Counter(r['finish'] for r in batch)),
            control_status=dict(Counter(r['status'] for r in batch)),
            prompt_tokens=sum(r['usage']['prompt_tokens'] for r in batch),
            output_tokens=sum(r['usage']['completion_tokens'] for r in batch),
            inference_seconds=sum(r['seconds'] for r in batch),
            evaluation_seconds=sum(r['evaluation_seconds'] for r in batch),
        )
        for mode in ('direct','verified'):
            result[arm][mode] = dict(
                correct=sum(r[mode]==r['expected'] for r in batch),
                errors=sum(r[mode] not in (r['expected'],'abstain') for r in batch),
                abstentions=sum(r[mode]=='abstain' for r in batch),
            )
    result['paired_verified'] = transitions(list(zip(reference,candidate)), 'verified','verified')
    result['candidate_direct_vs_verified'] = transitions([(r,r) for r in candidate], 'direct','verified')
    return result

if __name__ == '__main__':
    print(json.dumps(summarize([json.loads(line) for line in Path(sys.argv[1]).read_text().splitlines()]),
                     indent=2, ensure_ascii=False))
