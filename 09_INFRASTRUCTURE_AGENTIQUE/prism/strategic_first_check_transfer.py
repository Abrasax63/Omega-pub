"""Prospective, equal-information first-check transfer on GitHub PRs.

This code is committed BEFORE fetching the target PR statuses and paths.
The original optimizer and the strong marginal-order baselines see the
same 12 historical observations and 2-check budget. The evaluation replays
recorded GitHub values; it does NOT charge actual per-arm network calls.
"""
from collections import Counter, defaultdict
from fractions import Fraction
import hashlib
import json
from pathlib import Path

from action_planning_two_step import optimize_policy

ROOT = Path(__file__).parent
TRAIN = ROOT / "live_github_pr_gate_observations_2026-11-11.json"
TARGET = ROOT / "strategic_first_check_holdout_2026-11-11.json"
ALPHA = 1

TARGET_IDS = [
    ("python/cpython", 161266), ("python/cpython", 161728),
    ("python/cpython", 161727), ("python/cpython", 155070),
    ("python/cpython", 161162), ("python/cpython", 160875),
    ("python/cpython", 161755), ("python/cpython", 152702),
    ("pallets/flask", 6155), ("pallets/flask", 6156),
    ("pallets/flask", 6147), ("pallets/flask", 6145),
    ("pallets/flask", 6144), ("pallets/flask", 6142),
    ("pallets/flask", 6124), ("pallets/flask", 6043),
    ("psf/requests", 7586), ("psf/requests", 7049),
    ("psf/requests", 7051), ("psf/requests", 7499),
    ("psf/requests", 5220), ("psf/requests", 6991),
    ("psf/requests", 7023), ("psf/requests", 6675),
]

WORLD_ORDER = [(False, False), (False, True), (True, False), (True, True)]
CHECK_FIELDS = {"00-merged": "merged", "01-tests": "touched_tests"}


def train_snapshot():
    train = json.loads(TRAIN.read_text(encoding="utf-8"))
    rows = train["cases"]
    assert len(rows) == 12
    assert len({(r["repo"], r["number"]) for r in rows}) == 12
    assert all(type(r["merged"]) is bool and type(r["touched_tests"]) is bool
               for r in rows)
    return rows


def empirical_counts(rows):
    return Counter((r["merged"], r["touched_tests"]) for r in rows)


def marginals(rows):
    return (sum(r["merged"] for r in rows),
            sum(r["touched_tests"] for r in rows))


def choose_marginal(rows):
    # Best short-circuit order for deterministic AND and equal check costs.
    merged, tested = marginals(rows)
    return "merged" if merged <= tested else "touched_tests"


def make_model(rows, case_id):
    counts = empirical_counts(rows)
    hypotheses = [
        {"id": "world%d" % i, "decision": ("accept" if m and t else "reject"),
         "weight": counts[(m, t)] + ALPHA}
        for i, (m, t) in enumerate(WORLD_ORDER)
    ]
    checks = []
    for key, field in CHECK_FIELDS.items():
        checks.append({
            "id": key, "step": "Observe " + field,
            "method": "github_provenance_read",
            "action": "verify",
            "available": True, "cost_milli": 1,
            "observations": [
                "yes" if ((m, t)[0] if field == "merged" else (m, t)[1])
                else "no"
                for m, t in WORLD_ORDER
            ],
        })
    return {
        "case_id": case_id, "question": "Is merged AND touched_tests?",
        "mission_type": "documentary",
        "uncertainty": "Unknown GitHub metadata and file paths",
        "hypotheses": hypotheses, "checks": checks,
    }


def training_policies(train):
    by_repo = defaultdict(list)
    for r in train:
        by_repo[r["repo"]].append(r)
    per_repo = {}
    for repo in sorted(by_repo):
        rows = by_repo[repo]
        per_repo[repo] = {
            "training_n": len(rows),
            "marginals": marginals(rows),
            "simple_first": choose_marginal(rows),
            "omega": optimize_policy(make_model(rows, "repository-"+repo),
                                      max_depth=2, max_cost_milli=2),
        }
    return {
        "global": {
            "training_n": len(train),
            "marginals": marginals(train),
            "simple_first": choose_marginal(train),
            "omega": optimize_policy(make_model(train, "global"),
                                      max_depth=2, max_cost_milli=2),
        },
        "by_repo": per_repo,
    }


def fixed_order(row, first):
    assert first in ("merged", "touched_tests")
    second = "touched_tests" if first == "merged" else "merged"
    if not row[first]:
        return "reject", 1
    return ("accept" if row[second] else "reject"), 2


def run_omega(policy, row):
    node = policy["policy"]
    visited = []
    while "check_id" in node:
        key = node["check_id"]
        if key not in CHECK_FIELDS or key in visited or len(visited) >= 2:
            raise AssertionError("budget or no-repeat violation")
        visited.append(key)
        val = row[CHECK_FIELDS[key]]
        assert type(val) is bool
        node = node["branches"]["yes" if val else "no"]
    if node["action"] == "insufficient_evidence":
        return None, len(visited), visited
    if node["action"] != "answer":
        raise AssertionError("unexpected action: " + str(node))
    # Decision must be logically forced by observations, not by hidden truth.
    consistent = [
        ("accept" if m and t else "reject")
        for m, t in WORLD_ORDER
        if all(((m if CHECK_FIELDS[k] == "merged" else t) == row[CHECK_FIELDS[k]])
               for k in visited)
    ]
    if len(set(consistent)) != 1:
        raise AssertionError("Omega claims a certain decision without enough evidence")
    return consistent[0], len(visited), visited


def evaluate():
    train = train_snapshot()
    policies = training_policies(train)
    snapshot = json.loads(TARGET.read_text(encoding="utf-8"))
    cases = snapshot["cases"]
    assert [(r["repo"], r["number"]) for r in cases] == TARGET_IDS
    summaries = defaultdict(lambda: {"cases":0, "correct":0, "wrong":0,
                                     "abstain":0, "calls":0, "first_field":Counter()})
    by_repo = defaultdict(lambda: defaultdict(lambda: {"cases":0, "calls":0,
                                                        "correct":0, "abstain":0}))
    records = []
    for row in cases:
        repo_info = policies["by_repo"].get(row["repo"], policies["global"])
        choices = {
            "always_merged": fixed_order(row, "merged"),
            "always_tests": fixed_order(row, "touched_tests"),
            "global_marginal": fixed_order(row, policies["global"]["simple_first"]),
            "repo_marginal": fixed_order(row, repo_info["simple_first"]),
            "both_always": ("accept" if row["merged"] and row["touched_tests"] else "reject", 2),
        }
        o_global = run_omega(policies["global"]["omega"], row)
        o_repo = run_omega(repo_info["omega"], row)
        choices["Omega_global"] = o_global[:2]
        choices["Omega_repo"] = o_repo[:2]
        truth = "accept" if row["merged"] and row["touched_tests"] else "reject"
        for arm, (prediction, cost) in choices.items():
            s = summaries[arm]
            s["cases"] += 1
            s["calls"] += cost
            s["correct"] += (prediction == truth)
            s["abstain"] += (prediction is None)
            s["wrong"] += (prediction is not None and prediction != truth)
            if arm in ("Omega_global", "Omega_repo"):
                first = (o_global if arm == "Omega_global" else o_repo)[2]
                s["first_field"][CHECK_FIELDS[first[0]] if first else "none"] += 1
            b = by_repo[row["repo"]][arm]
            b["cases"] += 1
            b["calls"] += cost
            b["correct"] += (prediction == truth)
            b["abstain"] += (prediction is None)
            records.append({
                "repo": row["repo"], "number": row["number"],
                "arm": arm, "prediction": prediction, "truth": truth,
                "calls": cost,
            })
    for arm, s in summaries.items():
        s["first_field"] = dict(s["first_field"])
    # Retrospective oracle restricted to one constant order per cohort,
    # never a usable precommitted policy or proof of Omega inferiority.
    retrospective = {"global_optimum_calls":
                     min(summaries["always_merged"]["calls"],
                         summaries["always_tests"]["calls"]),
                     "per_repo_optimum_calls": sum(
                         min(by_repo[repo]["always_merged"]["calls"],
                             by_repo[repo]["always_tests"]["calls"])
                         for repo in by_repo)}
    return {
        "status": "PROSPECTIVE_PUBLIC_EXTERNAL_FACTS_OFFLINE_REPLAY",
        "preregistered_commit": "8cc991b1d734b280825ce10a73458aacc3f06c7a",
        "model_calls": 0,
        "network_calls_in_replay": 0,
        "training_cases": len(train),
        "holdout_cases": len(cases),
        "arm_caps": 2,
        "prior_pseudocount": ALPHA,
        "training_policies": {
            "global": {
                "marginals": policies["global"]["marginals"],
                "simple_first": policies["global"]["simple_first"],
                "omega_first": policies["global"]["omega"]["policy"].get("check_id"),
            },
            "by_repo": {
                repo: {
                    "marginals": p["marginals"],
                    "simple_first": p["simple_first"],
                    "omega_first": p["omega"]["policy"].get("check_id"),
                } for repo, p in policies["by_repo"].items()
            },
        },
        "summary": dict(sorted(summaries.items())),
        "by_repo": {repo:dict(d) for repo,d in sorted(by_repo.items())},
        "retrospective_oracle_not_an_arm": retrospective,
        "paired_per_case": records,
        "source_snapshot_sha256": hashlib.sha256(TARGET.read_bytes()).hexdigest(),
    }


if __name__ == "__main__":
    print(json.dumps(evaluate(), indent=2, sort_keys=True, ensure_ascii=False))
