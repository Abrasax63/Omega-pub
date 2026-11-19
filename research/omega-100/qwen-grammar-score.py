"""Summarize the paired syntax and fidelity trial."""
import json
import sys
from pathlib import Path

from aggregate import summarize


def score(rows):
    summary = summarize(rows)
    for arm in ('reference', 'candidate'):
        batch = [row for row in rows if row['arm'] == arm]
        summary[arm].update(
            executable_fields=sum(row['valid_fields'] for row in batch),
            total_fields=sum(row['total_fields'] for row in batch),
            all_fields_executable=sum(row['valid_fields']==row['total_fields'] for row in batch),
        )
    candidate = summary['candidate']
    paired = summary['paired_verified']
    summary['threshold_passed'] = (
        candidate['format_valid'] == candidate['all_fields_executable'] == 8
        and paired['gained'] >= 2 and paired['lost'] == 0
        and candidate['verified']['errors'] == 0
    )
    return summary


if __name__ == '__main__':
    rows = [json.loads(line) for line in Path(sys.argv[1]).read_text().splitlines()]
    print(json.dumps(score(rows), indent=2, ensure_ascii=False))
