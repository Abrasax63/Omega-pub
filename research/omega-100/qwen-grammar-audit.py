"""Audit finite truth sets and replay saved outcomes without another model call."""
import json
import runpy
import sys
from collections import Counter
from pathlib import Path

import baseline
import pilot
from grammar_trial import DOMAIN, result


def audit(folder, cases):
    report = {}
    for arm in ('reference', 'candidate'):
        counts = Counter()
        for i, (source, contract, expected, _) in enumerate(cases, 1):
            saved = json.loads((folder/f'private-{arm}-{i}.json').read_text())
            response, row = saved['response'], saved['row']
            replay = result(source, contract, response)
            assert replay == {key:row[key] for key in replay}
            assert row['expected'] == expected
            parsed = pilot.parsed_reply(response)
            fields = [(f"P{p['id']}", p['ast']) for p in contract['premises']]
            fields.append(('C', contract['conclusion']['ast']))
            agrees = True
            for key, label in fields:
                proposed = parsed.get(key)
                statuses = {
                    baseline.check({'domain': DOMAIN, 'if': x, 'then': y})['status']
                    for x, y in [(proposed, label), (label, proposed)]
                }
                if 'ABSTAIN' in statuses:
                    counts['unsupported_fields'] += 1
                    agrees = False
                elif 'COUNTEREXAMPLE' in statuses:
                    counts['different_truth_set_fields'] += 1
                    agrees = False
                else:
                    counts['equivalent_fields'] += 1
            counts['entire_case_equivalent'] += agrees
        report[arm] = dict(counts)
    return report


if __name__=='__main__':
    folder = Path(sys.argv[1])
    cases = [baseline.pack(case) for case in runpy.run_path(str(folder/'private-cases.py'))['CASES']]
    print(json.dumps(audit(folder, cases), indent=2))
