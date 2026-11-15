"""One-shot offline algorithm search with fixed-template candidates and an independent gate.

Only audited generated programs are executed. Subprocess limits mitigate runaway
CPU/memory use; they are NOT a security sandbox for arbitrary untrusted code.
"""
import argparse
import json
from pathlib import Path
import random
import resource
import subprocess
import sys
import tempfile

from gate import digest, evaluate
from reference import observed_relation, walks_exact, delta
from variant_factory import generate, choose

# Fixed before the first run. Distinct seed families for candidate selection and holdout.
TRAIN_SEEDS = (1101, 1102, 1103)
RESERVED_SEEDS = (9301, 9302, 9303)
REPEATS = 15
MAX_COST_PER_CASE_US = 10_000_000
BASELINE = 'linear-scan'

# This code runs in the child process, after a known fixed-template source.
# It has no access to gold answers or to the scoring function.
CHILD = '''
import json
import sys
job = json.load(sys.stdin)
rows = job["rows"]
steps = job["steps"]
repeat = job["repeat"]
value = None
for _ in range(repeat):
    value = q_power(rows, steps)
print(json.dumps(value, separators=(",", ":")))
'''


def graph_case(seed):
    rng = random.Random(seed)
    count, colors_count = 72, 14
    colors = [i % colors_count for i in range(count)]
    rng.shuffle(colors)
    transitions = [rng.randrange(count) for _ in range(count)]
    steps = 160 + seed % 37
    return {'seed': seed, 'group_id': 'source-seed-' + str(seed),
            'transition': transitions, 'colors': colors, 'color_count': colors_count,
            'steps': steps}


def _limit_child():
    resource.setrlimit(resource.RLIMIT_CPU, (5, 6))
    resource.setrlimit(resource.RLIMIT_AS, (256 * 1024 * 1024,) * 2)
    resource.setrlimit(resource.RLIMIT_FSIZE, (1024 * 1024,) * 2)
    resource.setrlimit(resource.RLIMIT_CORE, (0, 0))


def execute(source, rows, steps, repeat=REPEATS):
    job = json.dumps({'rows': rows, 'steps': steps, 'repeat': repeat})
    with tempfile.TemporaryDirectory(prefix='omega84-') as cwd:
        start = resource.getrusage(resource.RUSAGE_CHILDREN)
        completed = subprocess.run(
            [sys.executable, '-I', '-S', '-B', '-c', source + '\n' + CHILD],
            cwd=cwd, input=job, text=True, capture_output=True, timeout=7,
            env={'LC_ALL': 'C', 'PYTHONHASHSEED': '0'},
            preexec_fn=_limit_child, check=False,
        )
        end = resource.getrusage(resource.RUSAGE_CHILDREN)
    if completed.returncode != 0:
        raise RuntimeError('candidate crashed or exceeded runtime limit: ' + completed.stderr[-400:])
    # Measured independently by parent, not as an untrusted child-reported value.
    cpu_us = round(((end.ru_utime + end.ru_stime) - (start.ru_utime + start.ru_stime)) * 1_000_000)
    result = json.loads(completed.stdout)
    if not isinstance(result, list) or any(type(x) is not int for x in result):
        raise ValueError('invalid output shape')
    return result, max(cpu_us, 0)


def evaluate_variant(source, cases):
    rows = []
    for case in cases:
        obs = observed_relation(case['transition'], case['colors'], case['color_count'])
        expected = walks_exact(obs, case['steps'])
        got, cost = execute(source, obs, case['steps'])
        correct = got == expected
        rows.append({'case_id': str(case['seed']), 'prediction': digest(got),
                     'expected': digest(expected), 'correct': correct, 'cost': cost,
                     'delta_correct': delta(case['transition'], case['colors'], case['color_count'],
                                            case['steps'], got) ==
                                      delta(case['transition'], case['colors'], case['color_count'],
                                            case['steps'], expected),
                     'group_id': case['group_id']})
    return rows


def run():
    programs = generate()
    training = [graph_case(seed) for seed in TRAIN_SEEDS]
    scores = {}
    for name, program in programs.items():
        rows = evaluate_variant(program['source'], training)
        scores[name] = {'correct': all(row['correct'] for row in rows),
                        'errors': sum(not row['correct'] for row in rows),
                        'cpu_us_total': sum(row['cost'] for row in rows),
                        'source_sha256': program['sha256']}
    winner = choose(scores)
    if winner is None:
        return {'status': 'NO_VALID_CANDIDATE', 'training': scores}

    # First and only evaluation of the selected winner on reserved seed families.
    reserved = [graph_case(seed) for seed in RESERVED_SEEDS]
    baseline_rows = evaluate_variant(programs[BASELINE]['source'], reserved)
    candidate_rows = evaluate_variant(programs[winner]['source'], reserved)
    manifest = {
        'experiment_id': 'OMEGA-ALGORITHMIC-01',
        'cost_unit': 'measured_child_cpu_us',
        'cost_policy': 'no_increase',
        'max_cost_per_case': MAX_COST_PER_CASE_US,
        'max_total_cost': MAX_COST_PER_CASE_US * len(reserved),
        'training_case_ids': [str(c['seed']) for c in training],
        'training_group_ids': [c['group_id'] for c in training],
        'previous_holdout_group_ids': [],
        'required_domains': ['finite-observability'],
        'holdout': [{'case_id': r['case_id'], 'group_id': r['group_id'],
                     'domain': 'finite-observability', 'expected': r['expected']}
                    for r in baseline_rows],
    }
    # Existing v0.2 gate authenticates neither run URL nor source; be explicit.
    observation = {'experiment_id': manifest['experiment_id'], 'arms': {}}
    for name, rows, source_name in [('baseline', baseline_rows, BASELINE),
                                   ('candidate', candidate_rows, winner)]:
        observation['arms'][name] = {
            'source_commit': 'generated-source-sha256:' + programs[source_name]['sha256'],
            'run_url': 'UNATTESTED-LOCAL-SUBPROCESS',
            'results': [{'case_id': row['case_id'], 'prediction': row['prediction'],
                         'cost': row['cost']} for row in rows],
        }
    gate = evaluate(manifest, observation, digest(manifest))
    # Both Q^h and Δ_h correctness were checked independently on first evaluation.
    delta_checked = all(r['delta_correct'] for r in baseline_rows + candidate_rows)
    return {
        'status': 'EXECUTED_SYNTHETIC_PILOT',
        'strategy': 'finite-template search; no LLM used',
        'winner': winner, 'baseline': BASELINE,
        'strong_classical_comparator': 'square-scan',
        'winner_equals_strong_classical': winner == 'square-scan',
        'source_sha256': programs[winner]['sha256'],
        'training': scores,
        'reserved_cases': len(reserved),
        'delta_exact_match': delta_checked,
        'gate': gate,
        'disclaimer': 'In-repo synthetic seeds, weak isolation, measurements noisy; no proof of Omega-specific AI advantage.',
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    result = run()
    data = json.dumps(result, indent=2, ensure_ascii=False, sort_keys=True)
    if args.output:
        args.output.write_text(data + '\n', encoding='utf-8')
    print(data)


if __name__ == '__main__':
    main()
