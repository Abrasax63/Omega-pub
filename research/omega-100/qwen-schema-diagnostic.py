"""Locate errors in already generated fields without changing the pilot verdict."""
import json
import runpy
import sys
from collections import Counter
from pathlib import Path

from baseline import pack
from finite_oracle import check
from pilot import parsed_reply

def implies(left, right):
    return check({'domain':[-16,16], 'if':left, 'then':right})['status']

root = Path(sys.argv[1])
counts = Counter()
for i, case in enumerate(runpy.run_path(str(root/'private-cases.py'))['CASES'],1):
    _, contract, _, _ = pack(case)
    response = json.loads((root/f'private-candidate-{i}.json').read_text())['response']
    parsed = parsed_reply(response)
    fields = [(f"P{p['id']}", p['ast']) for p in contract['premises']]
    fields.append(('C', contract['conclusion']['ast']))
    for key, expected in fields:
        proposed = parsed.get(key)
        statuses = {implies(expected, proposed), implies(proposed, expected)}
        if 'ABSTAIN' in statuses:
            counts['unsupported'] += 1
        elif proposed == expected:
            counts['identical'] += 1
        elif 'COUNTEREXAMPLE' in statuses:
            counts['different_truth_set'] += 1
        else:
            counts['equivalent_in_finite_domain'] += 1
print(json.dumps(dict(counts), indent=2, sort_keys=True))
