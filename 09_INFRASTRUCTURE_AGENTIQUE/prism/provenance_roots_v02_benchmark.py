"""Public, reproducible ablation: trusted source-root adapter vs strong fixed order.

No model, network access, hidden evaluation set, or independent human labels.
The original PR31 12-case corpus has been examined already; this is a repair
regression and a counterexample study, not generalization evidence.
"""
import copy
import json
from collections import defaultdict

from provenance_benchmark import _read
from provenance_policy import decide as decide_v1
from trusted_receipt_adapter import decide_guarded


def _score(lookup, tasks, observations, truth):
    out = defaultdict(lambda: dict(cases=0, correct=0, wrong=0, abstain=0,
                                   calls=0, confident_wrong=0))
    rows = []
    for task in tasks:
        for key, f in lookup.items():
            ans = f(task, observations[task["id"]].__getitem__)
            result = out[key]
            result["cases"] += 1
            result["calls"] += len(ans["trace"])
            match = ans["decision"] == truth[task["id"]]["decision"]
            if ans["decision"] is None:
                result["abstain"] += 1
            elif match:
                result["correct"] += 1
            else:
                result["wrong"] += 1
                result["confident_wrong"] += ans["risk"] == "0"
            rows.append({
                "case": task["id"], "arm": key, "decision": ans["decision"],
                "truth": truth[task["id"]]["decision"], "match": match,
                "calls": len(ans["trace"]), "rejections": ans.get("adapter_rejections", []),
            })
    return dict(out), rows


def run():
    tasks = _read("tasks")
    observations = _read("observations")
    answers = _read("answer_key")
    arms = {
        "B_v1_fixed": lambda t, c: decide_v1(t, c, budget=2, fixed=True),
        "D_v1_adaptive": lambda t, c: decide_v1(t, c, budget=2),
        "B_v2_fixed": lambda t, c: decide_guarded(t, c, budget=2, fixed=True),
        "D_v2_adaptive": lambda t, c: decide_guarded(t, c, budget=2),
    }
    summary, rows = _score(arms, tasks, observations, answers)
    t3 = _read("supplement_t3")
    task = t3["task"]
    # Replace the fixture's incorrect "IETF" root on the MDN receipt with
    # the catalogued MDN root. This is not retrieval or content authentication.
    obs = copy.deepcopy(t3["observations"])
    obs["00-copy"]["independence"] = "mdn"
    t3_arms = {
        name: decide_guarded(task, obs.__getitem__, budget=2, fixed=(name=="B_v2_fixed"),
                             authority_by_field={"rule":"ietf"})
        for name in ("B_v2_fixed", "D_v2_adaptive")
    }
    t3_summary = {name: dict(decision=out["decision"], calls=len(out["trace"]),
                             rejections=out["adapter_rejections"])
                  for name,out in t3_arms.items()}
    # Deliberate source-label forgery on D5: do not mistake for an actual
    # incident. Old system may falsely complete the two-source quorum.
    d5 = next(t for t in tasks if t["id"]=="D5")
    spoof = copy.deepcopy(observations["D5"])
    spoof["01-copy"]["independence"] = "invented-independent"
    d5_report = {
        name: dict(decision=output["decision"], calls=len(output["trace"]),
                   rejections=output.get("adapter_rejections", []))
        for name,output in {
            "B_v1_fixed": decide_v1(d5, spoof.__getitem__, budget=2, fixed=True),
            "D_v1_adaptive": decide_v1(d5, spoof.__getitem__, budget=2),
            "B_v2_fixed": decide_guarded(d5, spoof.__getitem__, budget=2, fixed=True),
            "D_v2_adaptive": decide_guarded(d5, spoof.__getitem__, budget=2),
        }.items()
    }
    return {
        "status":"PUBLIC_REPLAY_NOT_BLIND",
        "model_calls":0, "new_remote_consultations":0,
        "trusted_authenticity_of_payload":False,
        "maximum_consultations_per_case":2,
        "pre_registered_commit":"419df0d5a3e89a65e6e4288631c2b1b3ccba61d4",
        "summary_12_cases":summary,
        "t3_authentic_secondary_same_budget":t3_summary,
        "d5_forged_root_same_budget":d5_report,
        "rows":rows,
    }


if __name__=="__main__":
    print(json.dumps(run(), ensure_ascii=False, indent=2, sort_keys=True))
