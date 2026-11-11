"""P5 multidomain adversarial evidence pilot, public and non-blind.

The actual Omega policy plans a single deterministic source check.
The task facts were verified from GitHub metadata, RFC references, and
Python runtime before this snapshot was created. The spoofing is artificial:
only the observation passed to the planner is inverted, not real sources.
No model generation, tool retrieval, or grading by an external human here.
"""
import json
from collections import defaultdict
from pathlib import Path

from action_planning_two_step import optimize_policy

DATA = Path(__file__).with_name("p5_multidomain_public_cases_2026-11-11.json")


def evidence_model(row):
    return {
        "case_id": row["id"],
        "question": row["question"],
        "mission_type": "documentary",
        "uncertainty": "Is the externally sourced claim true?",
        "hypotheses": [
            {"id": "false", "weight": 1, "decision": "no"},
            {"id": "true", "weight": 1, "decision": "yes"},
        ],
        "checks": [
            {"id": "00-primary-source", "action": "verify",
             "step": "Consult the claimed primary source",
             "method": "recorded_primary_observation",
             "available": True, "cost_milli": 5,
             "observations": ["no", "yes"]},
        ],
    }


def run_case(row, spoof=False):
    model = evidence_model(row)
    plan = optimize_policy(model, max_depth=1, max_cost_milli=5)
    root = plan["policy"]
    if root["action"] != "verify" or root["check_id"] != "00-primary-source":
        raise AssertionError("unexpected Omega first action")
    # Simulate source observation corruption; the reference truth is unchanged.
    observed = bool(row["truth"]) ^ bool(spoof and row["spoof_primary_in_adversarial"])
    outcome = "yes" if observed else "no"
    branch = root["branches"][outcome]
    if branch["action"] != "answer":
        raise AssertionError("Omega did not terminate after declared-perfect check")
    return {
        "omega": observed,
        "fixed": observed,
        "direct": bool(row["secondary_note_claim"]),
        # Diagnostic ONLY: uses the answer key as an independent oracle; cannot
        # be presented as a deployed equally budgeted fourth agent.
        "oracle_audit": None if observed != row["truth"] else observed,
        "omega_action": root["action"],
        "omega_reported_loss": plan["expected_total_loss"],
        "omega_calls": 1,
        "fixed_calls": 1,
        "direct_calls": 0,
    }


def summarize():
    rows = json.loads(DATA.read_text(encoding="utf-8"))["cases"]
    results = {}
    for condition in ("intact", "spoofed"):
        agg = defaultdict(lambda: {
            "cases": 0, "direct_correct": 0, "fixed_correct": 0,
            "omega_correct": 0, "omega_false_certainties": 0,
            "oracle_audit_correct": 0, "oracle_audit_abstentions": 0,
            "direct_calls": 0, "fixed_calls": 0, "omega_calls": 0,
        })
        for row in rows:
            r = run_case(row, spoof=(condition == "spoofed"))
            s = agg[row["domain"]]
            s["cases"] += 1
            for arm in ("direct", "fixed", "omega"):
                s[arm + "_correct"] += (r[arm] == row["truth"])
                s[arm + "_calls"] += r[arm + "_calls"]
            s["omega_false_certainties"] += (r["omega"] != row["truth"])
            s["oracle_audit_correct"] += (r["oracle_audit"] == row["truth"])
            s["oracle_audit_abstentions"] += (r["oracle_audit"] is None)
        total = {k: sum(v[k] for v in agg.values()) for k in next(iter(agg.values()))}
        results[condition] = {
            "total": total, "by_domain": dict(sorted(agg.items())),
        }
    return {
        "status": "PUBLIC_CALIBRATION_WITH_SYNTHETIC_SPOOFING",
        "models_called": 0,
        "new_live_calls_in_replay": 0,
        "human_blind_corrections": 0,
        "adversarial_control_is_fabricated": True,
        "comparator_has_same_one_check_budget": True,
        "oracle_audit_is_not_budget_matched": True,
        "results": results,
    }


if __name__ == "__main__":
    print(json.dumps(summarize(), indent=2, sort_keys=True, ensure_ascii=False))
