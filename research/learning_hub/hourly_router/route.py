"""Omega hourly capability selector: read-only, fail-closed, zero model calls.

Never runs a proposed capability, checks out any branch, executes git or a
network request, trains weights or changes an existing hourly schedule.
Selection is advisory: the automation must still verify exact PR ref and
evidence and obey the existing per-branch science workflow.
"""
from __future__ import annotations
import argparse
from hashlib import sha256
import json
from pathlib import Path
import re

HERE=Path(__file__).resolve().parent
REGISTRY=HERE/"CAPABILITY_REGISTRY.json"
SCHEMA="OMEGA_HOURLY_CAPABILITY_ROUTER_01"
VALID_LEVELS={
    "VERIFIED_SOFTWARE_ONLY","EXPERIMENTAL_ONLY",
    "VERIFIED_NARROW_COMPARISON","EXTERNAL_EXISTING_WORKFLOW"
}
SHA_RE=re.compile(r"^[0-9a-f]{40}$")

def require(condition,reason):
    if not condition:
        raise ValueError(reason)

def read_registry(path=REGISTRY):
    f=Path(path)
    require(f.is_file() and f.stat().st_size <= 150000,"REGISTRY_MISSING_OR_TOO_LARGE")
    d=json.loads(f.read_text(encoding="utf-8"))
    validate(d)
    return d

def validate(d):
    require(isinstance(d,dict) and d.get("schema")==SCHEMA,"INVALID_ROUTER_SCHEMA")
    require(d.get("main_modified") is False and
            d.get("auto_merge") is False and
            d.get("auto_train") is False and
            d.get("automatic_model_execution") is False and
            d.get("auto_promote_science") is False,"UNAUTHORIZED_SIDE_EFFECTS")
    require(d.get("repository")=="Abrasax63/Omega-pub","UNTRUSTED_REPOSITORY")
    items=d.get("capabilities")
    require(isinstance(items,list) and len(items)>=7,"INCOMPLETE_CAPABILITY_CATALOGUE")
    ids=[x.get("id") for x in items if isinstance(x,dict)]
    require(len(ids)==len(items) and len(set(ids))==len(ids) and all(ids),
            "DUPLICATE_OR_BAD_CAPABILITY")
    for x in items:
        require(x.get("level") in VALID_LEVELS,"UNKNOWN_VERIFICATION_LEVEL")
        require(x.get("code_path","").startswith(("research/","09_INFRASTRUCTURE_AGENTIQUE/")),
                "UNSAFE_OR_MISSING_CODE_PATH")
        require(".." not in x["code_path"] and not x["code_path"].startswith("/"),
                "UNSAFE_RELATIVE_PATH")
        require(x.get("ref") and x.get("measured") and x.get("scientific_limit"),
                "MISSING_PROVENANCE_AND_LIMITS")
        if x["level"]!="EXTERNAL_EXISTING_WORKFLOW":
            require(bool(SHA_RE.fullmatch(x["ref"])),"UNPINNED_EXPERIMENTAL_CODE")
            require(isinstance(x.get("evidence_run"),int) and x["evidence_run"]>0,
                    "NO_REAL_RUN_PROVENANCE")
    rules=d.get("route_rules")
    require(isinstance(rules,list) and rules,"NO_RULES")
    kinds=[r.get("task_kind") for r in rules]
    require(len(set(kinds))==len(kinds) and "other" in kinds,"DUPLICATE_OR_MISSING_FALLBACK")
    requires={"mathematical_proof_or_counterexample",
              "provenance_reconciliation","omega100_iteration",
              "local_python_semantic_bug","python_syntax_repair_pilot",
              "new_training_data_qa","learning_state_integrity"}
    require(requires.issubset(set(kinds)),"MISSING_SCIENTIFIC_ROUTING_CONTRACT")
    require([r["priority"] for r in rules]==sorted(r["priority"] for r in rules),
            "RULE_ORDER_CHANGED")
    for r in rules:
        require(all(i in ids for i in r.get("preferred",[])+r.get("reject",[])),
                "RULE_REFERENCES_UNKNOWN_TOOL")
        require(not set(r["preferred"]) & set(r["reject"]),
                "CONFLICTING_ROUTE_PREFERENCE")
    require(next(r for r in rules if r["task_kind"]=="local_python_semantic_bug")
            ["preferred"]==["symbolic_semantic_one_edit"],
            "SEMANTIC_COUNTEREXAMPLE_IGNORED")
    require("python_lora_syntax_pilot" in
            next(r for r in rules if r["task_kind"]=="local_python_semantic_bug")
            ["reject"],"LORA_SEMANTIC_0_OF_12_IGNORED")
    require(next(r for r in rules if r["task_kind"]=="other")["preferred"]==[],
            "FORCED_TOOL_FOR_UNKNOWN_KIND")
    safety=d.get("safe_default")
    require(safety.get("inspection_per_hour") is True and
            safety.get("mandatory_application_each_hour") is False and
            safety.get("enable_new_runs") is False and
            safety.get("allow_existing_hourly_schedule_change") is False and
            safety.get("require_fresh_reference_sha") is True and
            safety.get("require_relevant_test") is True and
            safety.get("require_independent_holdout_for_new_learning_claim") is True,
            "UNSAFE_HOURLY_DEFAULTS")
    return True

def select(d,kind):
    validate(d)
    rules={r["task_kind"]:r for r in d["route_rules"]}
    r=rules.get(kind,rules["other"])
    caps={x["id"]:x for x in d["capabilities"]}
    refs=[caps[k] for k in r["preferred"]]
    return {
        "schema":"OMEGA_HOURLY_SELECTION_01",
        "requested_kind":kind,
        "applied_rule":r["task_kind"],
        "selected_capabilities":[{
            "id":x["id"],"level":x["level"],"pr":x.get("pr"),
            "pinned_source":x["ref"],"code_path":x["code_path"],
            "evidence_run":x.get("evidence_run"),
            "scientific_limit":x["scientific_limit"]
        } for x in refs],
        "declined_capabilities":r["reject"],
        "reason":r["reason"],
        "advice_only":True,
        "actual_execution_performed":False,
        "source_availability_verified_this_run":False,
        "required_followup":"Check current GitHub sources and baseline; run only if relevant and within assigned branch",
        "registry_sha256":sha256(json.dumps(d,sort_keys=True,ensure_ascii=False).encode()).hexdigest()
    }

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--registry",type=Path,default=REGISTRY)
    parser.add_argument("--kind",default="other")
    args=parser.parse_args()
    result=select(read_registry(args.registry),args.kind)
    print(json.dumps(result,ensure_ascii=False,indent=2))

if __name__=="__main__":
    main()
