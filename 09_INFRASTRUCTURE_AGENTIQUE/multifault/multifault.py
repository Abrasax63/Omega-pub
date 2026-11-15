"""OMEGA-MULTIFAULT-01: locate candidate fault sites, patch, falsify, compare Qwen.

All Python source originates in a closed, repository-controlled template grammar.
Only Qwen-generated OUTPUT is an ID. A weak public filter retains ambiguity;
the exact strong public oracle is withheld from Qwen, and a new reserve from all.
"""
from __future__ import annotations

import argparse
import ast
import hashlib
import json
from pathlib import Path
import re
import secrets
import subprocess
import sys
import time

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
INFRA = ROOT / "09_INFRASTRUCTURE_AGENTIQUE"
for module in ("auto_research","integrated_cycle","memory_ablation",
               "memory_repair","targeted_patch","prism"):
    if str(INFRA/module) not in sys.path:
        sys.path.insert(0,str(INFRA/module))

from reference import walks_exact
from model_proposal import validate_source
from model_pilot import score
from runner import graph_case
from variant_factory import generate
from gate import digest
from integrated_cycle import prepare, known_prior_sources
from targeted_patch import notes_from_rce
from memory_ablation import _manifest, _all_correct, _gate_for
from execution import start_execution, record_perspective, close_execution
from event_store import lifecycle_events, verify_events

EXPERIMENT = "OMEGA-MULTIFAULT-01"
DEVELOPMENT_SEEDS = (1101,1102,1103)
HOLDOUT_COUNT = 5
MAX_PATCHES = 100
MAX_SELECTOR_TOKENS = 64
SELECTOR_CTX = 3072
MODEL_MARKER = "SELECTED_PATCH: "
MIN_SPEED_MARGIN = .15

# Fault injection fixtures are for the BENCHMARK only. None of their identifiers,
# locations or original correct lines are given to enumerate_patches().
CORRECT = "\n".join([
    "def q_power(rows, steps):",
    "    if steps == 0:",
    "        return [1 << i for i in range(len(rows))]",
    "    result = rows[:]",
    "    for _ in range(steps - 1):",
    "        new_result = []",
    "        for i in range(len(rows)):",
    "            new_row = 0",
    "            for j in range(len(rows)):",
    "                if result[i] & (1 << j):",
    "                    new_row |= rows[j]",
    "            new_result.append(new_row)",
    "        result = new_result",
    "    return result",
]) + "\n"

def sha(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()

def benchmark_sources() -> list[dict]:
    """Benchmark-only injection. Repair API receives source strings, no labels."""
    changes = [
        ("C1", [("if result[i] & (1 << j):", "if rows[j] & (1 << i):")]),
        ("C2", [("new_row |= rows[j]", "new_row ^= rows[j]")]),
        ("C3", [("return [1 << i for i in range(len(rows))]", "return rows[:]")]),
        ("C4", [("for _ in range(steps - 1):", "for _ in range(steps):")]),
        ("C5", [("new_row |= rows[j]", "new_row ^= rows[j]"),
                ("for _ in range(steps - 1):", "for _ in range(steps):")]),
    ]
    records=[]
    for name,mutations in changes:
        code=CORRECT
        changed_lines=[]
        for old,new in mutations:
            if code.count(old)!=1:
                raise RuntimeError("benchmark fault injection ambiguous")
            changed_lines.append(next(i for i,line in enumerate(code.splitlines(),1) if old in line))
            code=code.replace(old,new,1)
        validate_source(code)
        records.append({"id":name, "source":code,"sha256":sha(code),
                        "audit_fault_lines":changed_lines,
                        "audit_mutation_count":len(mutations)})
    return records

def source_from_line_patch(source: str,line: int,replacement: str) -> str:
    """Exactly one source line replaced; AST, function name and arity invariant."""
    lines=source.splitlines(keepends=True)
    if line<1 or line>len(lines):
        raise ValueError("invalid line")
    old=lines[line-1]
    if old.rstrip("\n")==replacement:
        raise ValueError("unchanged candidate")
    lines[line-1]=replacement+"\n"
    patched="".join(lines)
    parsed=ast.parse(patched)
    funcs=[n for n in parsed.body if isinstance(n,ast.FunctionDef)]
    if len(funcs)!=1 or funcs[0].name!="q_power":
        raise ValueError("wrong function")
    if [x.arg for x in funcs[0].args.args]!=["rows","steps"]:
        raise ValueError("wrong parameter schema")
    validate_source(patched)
    if len(patched.splitlines())!=len(source.splitlines()):
        raise ValueError("line count changed")
    diff=[i for i,(a,b) in enumerate(zip(source.splitlines(),patched.splitlines()),1) if a!=b]
    if diff!=[line]:
        raise ValueError("patch not restricted to one line")
    return patched

def enumerate_patches(source: str) -> list[dict]:
    """AST discovery of admissible site TYPES, with no fault line supplied."""
    validate_source(source)
    tree=ast.parse(source)
    lines=source.splitlines()
    proposals=[]
    def propose(line,replacement,rule):
        if line<1 or line>len(lines):
            return
        try:
            candidate=source_from_line_patch(source,line,replacement)
        except (SyntaxError,ValueError):
            return
        proposals.append({"line":line,"rule":rule,"before":lines[line-1],
                          "after":replacement,"source":candidate,"source_sha256":sha(candidate)})
    for node in ast.walk(tree):
        no=node.lineno if hasattr(node,"lineno") else 0
        if not no or no>len(lines):
            continue
        raw=lines[no-1]
        ind=raw[:len(raw)-len(raw.lstrip())]
        if isinstance(node,ast.If) and "&" in raw and "(1 <<" in raw:
            for mask in ("rows","result"):
                for ri in ("i","j"):
                    for bit in ("i","j"):
                        expr=mask+"["+ri+"] & (1 << "+bit+")"
                        for polarity in (False,True):
                            body="not ("+expr+")" if polarity else expr
                            propose(no,ind+"if "+body+":","condition")
        if isinstance(node,ast.AugAssign) and isinstance(node.target,ast.Name) and node.target.id=="new_row":
            if raw.strip() in ("new_row |= rows[j]","new_row ^= rows[j]"):
                propose(no,ind+("new_row |= rows[j]" if "^=" in raw else "new_row ^= rows[j]"),"combine")
        if isinstance(node,ast.Return) and node.value is not None:
            if raw.strip() in ("return rows[:]","return [1 << i for i in range(len(rows))]"):
                other=("[1 << i for i in range(len(rows))]" if "rows[:]" in raw else "rows[:]")
                propose(no,ind+"return "+other,"zero_return")
        if isinstance(node,ast.For) and node.target and isinstance(node.target,ast.Name) and node.target.id=="_":
            if raw.strip() in ("for _ in range(steps):","for _ in range(steps - 1):"):
                other=("for _ in range(steps - 1):" if raw.strip()=="for _ in range(steps):"
                       else "for _ in range(steps):")
                propose(no,ind+other,"loop_bound")
        if isinstance(node,ast.Assign) and any(isinstance(t,ast.Name) and t.id=="result" for t in node.targets):
            if raw.strip() in ("result = rows[:]","result = [1 << i for i in range(len(rows))]"):
                other=("[1 << i for i in range(len(rows))]" if "rows[:]" in raw else "rows[:]")
                propose(no,ind+"result = "+other,"initial_relation")
    unique={}
    for row in proposals:
        unique.setdefault(row["source_sha256"],row)
    result=[]
    for row in unique.values():
        if len(result)>=MAX_PATCHES:
            raise RuntimeError("closed repair grammar exceeded budget")
        result.append({"id":"P"+str(len(result)).zfill(2),**row})
    return result

def public_suite():
    # Deliberately weak, same for every arm, so more than one patch survives.
    return [
        {"id":"smoke-h0","rows":[2,1],"steps":0},
        {"id":"smoke-h1-id","rows":[1,2],"steps":1},
        {"id":"smoke-h1-sink","rows":[0,2],"steps":1},
    ]

def discriminant_suite():
    # Stronger public exact test, NOT available to Qwen or weak selectors.
    cases=[
        {"id":"branch","rows":[6,4,4],"steps":2},
        {"id":"cycle-h3","rows":[2,4,1],"steps":3},
        {"id":"cycle-h9","rows":[2,4,1],"steps":9},
        {"id":"two-cycle-h4","rows":[2,1],"steps":4},
        {"id":"dense","rows":[7,5,2],"steps":5},
        {"id":"zero","rows":[2,1],"steps":0},
    ]
    for a in range(4):
        for b in range(4):
            for steps in (2,3,4):
                cases.append({"id":"two-"+str(a)+"-"+str(b)+"-"+str(steps),
                              "rows":[a,b],"steps":steps})
    return cases

def closed_function(source: str):
    """Only trusted internal grammar built from static fixture is evaluated here.
    This is NOT an isolation boundary. Docker is compulsory for final checks.
    """
    validate_source(source)
    safe={"__builtins__":{"range":range,"len":len}}
    local={}
    exec(compile(source,"<trusted-closed-dsl>","exec"),safe,local)
    return local["q_power"]

def check_public(source: str,cases:list[dict]):
    fn=closed_function(source)
    for pos,c in enumerate(cases,1):
        expected=walks_exact(c["rows"],c["steps"])
        try:
            result=fn(list(c["rows"]),c["steps"])
        except Exception as err:
            return {"passed":False,"checked":pos,
                    "counterexample":{"id":c["id"],"error":type(err).__name__,
                                      "rows":c["rows"],"steps":c["steps"]}}
        if result!=expected:
            return {"passed":False,"checked":pos,
                    "counterexample":{"id":c["id"],"rows":c["rows"],"steps":c["steps"],
                                      "expected":expected,"actual":result}}
    return {"passed":True,"checked":len(cases),"counterexample":None}

def heuristic_rank(row: dict):
    # Explicitly engineered rules grounded in existing finite observability
    # notation, not a learned prioritizer. All are available without an LLM.
    after=row["after"]
    return (
        0 if row["rule"] in ("combine","zero_return","loop_bound","condition") else 1,
        0 if "result[i] & (1 << j)" in after or "new_row |= rows[j]" in after
             or "return [1 << i" in after or "range(steps - 1)" in after else 1,
        row["id"],
    )

def selector_prompt(task_source: str, shortlist: list[dict], note:str) -> str:
    if not shortlist:
        raise ValueError("Qwen cannot choose from empty list")
    lines="\n".join(row["id"]+": L"+str(row["line"])+": "+row["after"].strip()
                    for row in shortlist)
    return (
        "<|im_start|>system\n"
        "You select one candidate edit ID for a finite-relation path function. "
        "Return one ID only. Never output code or additional text.\n"
        "<|im_end|>\n<|im_start|>user\n"
        "A one-line repair must make q_power compute exact-length paths, "
        "using bitwise OR to combine reachable neighbor sets. "
        "The following patches passed only THREE WEAK PUBLIC TESTS; some remain wrong. "
        "Do not infer any hidden case from this list.\n"
        "Defective source:\n"+task_source+
        "\nCandidates:\n"+lines+
        "\nUntrusted research context (equal-length across arms):\n"+note+
        "\nChoose exactly one candidate ID. Example: P04.\n"
        "<|im_end|>\n<|im_start|>assistant\n"+MODEL_MARKER
    )

def parse_choice(raw: str,prompt: str,allowed:set[str]) -> str:
    if prompt in raw:
        tail=raw.rsplit(prompt,1)[1]
    elif "... (truncated)\n" in raw:
        tail=raw.rsplit("... (truncated)\n",1)[1]
    else:
        raise ValueError("no unambiguous CLI generated span")
    tail=tail.split("\n[ Prompt:",1)[0].split("<|im_end|>",1)[0].strip()
    if tail.startswith(MODEL_MARKER):
        tail=tail[len(MODEL_MARKER):].strip()
    tail=tail.replace(chr(96),"").strip()
    lines=[s.strip() for s in tail.splitlines() if s.strip()]
    if len(lines)!=1 or not re.fullmatch(r"P[0-9]{2}",lines[0]):
        raise ValueError("not one exact patch ID")
    if lines[0] not in allowed:
        raise ValueError("ID not in public-passing list")
    return lines[0]

def qwen_choose(cli:Path,model:Path,task_source:str,
                shortlist:list[dict],note:str,arm:str):
    prompt=selector_prompt(task_source,shortlist,note)
    cmd=[str(cli),"-m",str(model),"-p",prompt,"-n",str(MAX_SELECTOR_TOKENS),
         "-c","3072","-t","4","--temp","0"]
    begin=time.perf_counter()
    try:
        process=subprocess.run(cmd,text=True,capture_output=True,timeout=240)
    except (OSError,subprocess.TimeoutExpired) as e:
        return {"called":True,"status":"CALL_FAILED","arm":arm,
                "failure":type(e).__name__,"prompt_sha256":sha(prompt)}
    rec={"called":True,"arm":arm,"returncode":process.returncode,
         "prompt_sha256":sha(prompt),"prompt_chars":len(prompt),
         "raw_sha256":sha(process.stdout),"raw_tail":process.stdout[-1800:],
         "inference_seconds":round(time.perf_counter()-begin,3)}
    if process.returncode:
        return {**rec,"status":"CALL_FAILED","error":process.stderr[-300:]}
    try:
        ident=parse_choice(process.stdout,prompt,{x["id"] for x in shortlist})
        return {**rec,"status":"VALID_ID","selected_id":ident}
    except ValueError as e:
        return {**rec,"status":"INVALID_ID","error":str(e)}

def prepare_tasks():
    weak=public_suite()
    strong=discriminant_suite()
    result=[]
    for entry in benchmark_sources():
        src=entry["source"]
        hyps=enumerate_patches(src)  # No fault line, class or target label supplied.
        checked=[]
        for candidate in hyps:
            tested=check_public(candidate["source"],weak)
            checked.append({**candidate,"weak":tested})
        shortlist=[x for x in checked if x["weak"]["passed"]]
        stronger={x["id"]:check_public(x["source"],strong) for x in shortlist}
        robust=[x for x in shortlist if stronger[x["id"]]["passed"]]
        result.append({
            "name":entry["id"],"source":src,"source_sha256":entry["sha256"],
            "audit_fault_lines":entry["audit_fault_lines"],
            "audit_mutation_count":entry["audit_mutation_count"],
            "all_candidates":checked,"weak_shortlist_ids":[x["id"] for x in shortlist],
            "strong_public_results":stronger,
            "fully_public_survivors":[x["id"] for x in robust],
            "first_weak":shortlist[0]["id"] if shortlist else None,
            "rce_weak":sorted(shortlist,key=heuristic_rank)[0]["id"] if shortlist else None,
            "symbolic_full":robust[0]["id"] if robust else None,
        })
    return result

def run(cli:Path,model:Path,root:Path=ROOT):
    if not cli.is_file() or not model.is_file():
        raise RuntimeError("pinned model / llama-cli unavailable")
    plan,bundle=prepare(root)
    notes=notes_from_rce(root)
    if len(notes["memory"])!=len(notes["placebo"]):
        raise RuntimeError("RCE context parity failed")
    seeds=[]
    while len(seeds)<HOLDOUT_COUNT:
        seed=secrets.randbits(48)
        if seed not in seeds and seed not in DEVELOPMENT_SEEDS:
            seeds.append(seed)
    reserved=[graph_case(seed) for seed in seeds]
    manifest=_manifest(reserved)
    manifest["experiment_id"]=EXPERIMENT
    frozen=digest(manifest)
    print("HOLDOUT_FROZEN_BEFORE_MODEL_AND_SEARCH="+frozen,flush=True)
    print("MODEL_NEVER_SEES_RESERVED_ANSWERS",flush=True)
    print("RCE_SOURCE_SHA256="+notes["scientific_source"]["source_blob_sha256"],flush=True)
    tasks=prepare_tasks()
    if len(tasks)!=5 or any(len(t["all_candidates"])>MAX_PATCHES for t in tasks):
        raise RuntimeError("unexpected task or hypothesis budget")
    # All candidate choices are fixed before evaluating *any* reserved case.
    for task in tasks:
        shortlist=[x for x in task["all_candidates"] if x["weak"]["passed"]]
        task["qwen_control"]=qwen_choose(cli,model,task["source"],shortlist,
                                         notes["placebo"],"qwen_control")
        task["qwen_rce"]=qwen_choose(cli,model,task["source"],shortlist,
                                     notes["memory"],"qwen_rce")
        task["choices"]={
            "symbolic_first":task["first_weak"],
            "symbolic_rce_prior":task["rce_weak"],
            "symbolic_full_public":task["symbolic_full"],
            "qwen_control":task["qwen_control"].get("selected_id"),
            "qwen_rce":task["qwen_rce"].get("selected_id"),
        }
        task["choices_sha256"]=digest(task["choices"])
    frozen_choices=digest([t["choices"] for t in tasks])
    print("CHOICES_FROZEN_BEFORE_HOLDOUT="+frozen_choices,flush=True)

    classical=generate()
    classical_results={
        n:score(classical[n]["source"],reserved)
        for n in ("square-scan","square-lowbit")}
    if not all(_all_correct(rows) for rows in classical_results.values()):
        raise RuntimeError("reference classic failed")
    best_classic=min(sum(x["cost"] for x in rows) for rows in classical_results.values())
    old_sha={x["source_sha256"] for x in known_prior_sources()}
    # Strong candidate check is public; code executes in Docker ONLY after
    # symbolic public discriminator passes. Score cache never counts as replication.
    development_cases=[graph_case(s) for s in DEVELOPMENT_SEEDS]
    for task in tasks:
        all_by_id={x["id"]:x for x in task["all_candidates"]}
        selected_ids={v for v in task["choices"].values() if v is not None}
        public_status={}
        for ident in sorted(selected_ids):
            if not task["strong_public_results"].get(ident,{}).get("passed",False):
                public_status[ident]={"public_valid":False,"development_valid":False}
                continue
            try:
                checks=score(all_by_id[ident]["source"],development_cases)
                public_status[ident]={
                    "public_valid":True,"development_valid":_all_correct(checks),
                    "development_checks":checks}
            except (ValueError,RuntimeError,TimeoutError) as e:
                public_status[ident]={
                    "public_valid":True,"development_valid":False,
                    "error":str(e)[:280]}
        heldout_cache={}
        arms={}
        for label,ident in task["choices"].items():
            info={"selected_id":ident,"reserve_opened":False,
                  "decision":"REJECTED","independent_replication":False}
            if ident is not None:
                info["public_discriminator_passed"]=bool(
                    task["strong_public_results"].get(ident,{}).get("passed"))
                info["development_passed"]=public_status[ident]["development_valid"]
                if info["development_passed"]:
                    row=all_by_id[ident]
                    if ident not in heldout_cache:
                        heldout_cache[ident]=score(row["source"],reserved)
                    outcome=heldout_cache[ident]
                    info.update({
                        "reserve_opened":True,"source_sha256":row["source_sha256"],
                        "heldout_rows":outcome,"correct":_all_correct(outcome),
                        "cost_us":sum(x["cost"] for x in outcome),
                        "historical_source_duplicate":row["source_sha256"] in old_sha,
                        "cached_same_candidate":sum(x==ident for x in task["choices"].values())>1})
                    gates={n:_gate_for(manifest,ref,outcome,classical[n]["sha256"],
                                       row["source_sha256"])
                           for n,ref in classical_results.items()}
                    info["gates"]={
                        n:{"status":g["status"],
                           "review":g["candidate_for_independent_review"]}
                        for n,g in gates.items()}
                    if (info["correct"] and not info["historical_source_duplicate"]
                        and not info["cached_same_candidate"]
                        and all(g["candidate_for_independent_review"] for g in gates.values())
                        and info["cost_us"]<=(1-MIN_SPEED_MARGIN)*best_classic):
                        info["decision"]="REVIEW_REQUIRED"
            arms[label]=info
        task["evaluated_public"]=public_status
        task["arms"]=arms
        task["unique_holdout_sources_evaluated"]=len(heldout_cache)
        # Do not keep full candidate program copies five times in all outputs.
        task["source_location_given_to_generator"]=False

    execution=start_execution(plan,bundle)
    record_perspective(
        execution,"computational",status="completed",
        output=json.dumps({"experiment":EXPERIMENT,"tasks":len(tasks),
                           "actual_qwen_calls":sum(
                               bool(t[a].get("called")) for t in tasks
                               for a in ("qwen_control","qwen_rce")),
                           "choices_sha256":frozen_choices},
                           sort_keys=True),
        evidence_refs=[
            "reserved-manifest-sha256:"+frozen,
            "choices-before-holdout-sha256:"+frozen_choices,
            "rce-evidence-sha256:"+notes["scientific_source"]["source_blob_sha256"]],
        limitations=[
            "Faults are researcher-injected; they are not independent unknown real-world bugs.",
            "Qwen outputs IDs only; candidate code comes from a fixed grammar.",
            "Local public screening executes trusted generated templates, not model code.",
            "P3 roles are not independent scientist agents.",
        ])
    close_execution(execution)
    events=lifecycle_events(plan,bundle,execution)
    provenance=verify_events(events)
    if not provenance["valid"]:
        raise RuntimeError("provenance event chain failed")

    summaries=[]
    for task in tasks:
        summaries.append({
            "task":task["name"],
            "mutation_count_for_audit_only":task["audit_mutation_count"],
            "fault_lines_for_audit_only":task["audit_fault_lines"],
            "candidate_count":len(task["all_candidates"]),
            "weak_passing_count":len(task["weak_shortlist_ids"]),
            "strong_passing_count":len(task["fully_public_survivors"]),
            "symbolic_full_id":task["symbolic_full"],
            "qwen_control_status":task["qwen_control"]["status"],
            "qwen_rce_status":task["qwen_rce"]["status"],
            "choices":task["choices"],
            "results":{name:{
                "selected_id":v["selected_id"],"public_valid":v.get("development_passed"),
                "reserve_opened":v["reserve_opened"],"correct":v.get("correct"),
                "decision":v["decision"]} for name,v in task["arms"].items()}})
    report={
        "experiment_id":EXPERIMENT,
        "scientific_status":"EXPERIMENTAL_BOUNDED_NOT_CERTIFIED",
        "model_sha256":hashlib.sha256(model.read_bytes()).hexdigest(),
        "rce":{k:v for k,v in notes.items() if k not in ("memory","placebo")},
        "rce_hint_sha256":sha(notes["memory"]),
        "public_weak_suite":public_suite(),
        "public_strong_suite":discriminant_suite(),
        "public_test_scope":"three weak and fifty-four strong synthetics; all labels from walks_exact",
        "task_summaries":summaries,
        "tasks_with_full_provenance":tasks,
        "reserved_manifest_sha256":frozen,
        "reserved_manifest":manifest,
        "reserved_seeds_revealed_after_evaluation":seeds,
        "frozen_pre_holdout_choices_sha256":frozen_choices,
        "strong_classics":{
            n:{"correct":sum(x["correct"] and x["delta_correct"] for x in rows),
               "cost_us":sum(x["cost"] for x in rows),
               "rows":rows} for n,rows in classical_results.items()},
        "comparison":{
            "total_tasks":len(tasks),
            "positive_single_fault_tasks":4,
            "negative_double_fault_control":1,
            "actual_model_calls":sum(
                bool(t[k].get("called")) for t in tasks
                for k in ("qwen_control","qwen_rce")),
            "symbolic_full_public_correct":sum(
                t["symbolic_full"] is not None for t in tasks),
            "unknown_fault_location_input":True,
            "source_location_given_to_generator":False,
            "general_intelligence_gain_demonstrated":False,
            "independent_certification":False,
        },
        "p3_coverage":execution["coverage"],
        "provenance":provenance,"events":events,
        "promotion_to_core":False,"main_modified":False,
        "limitations":[
            "These faults and candidate templates are human-engineered synthetic fixtures.",
            "Qwen is choosing among prewritten single-line edits, not creating new code.",
            "An unknown line to a generator is not a blind external real-world benchmark.",
            "The weak public test intentionally creates ambiguity and is not a correctness proof.",
            "The strong symbolic comparator has a strictly larger testing budget.",
            "RCE ordering/hint comes from human-coded priors grounded in a file.",
            "The reserved synthetic oracle is created in the same workflow, not externally.",
            "Code sourced from fixed trusted templates is interpreted locally for public screening.",
            "Docker wall time contains startup and shared-runner performance variation.",
            "A duplicate selected code is evaluated once, never counted as replication.",
        ],
    }
    report["report_sha256_without_self"]=digest(report)
    return report

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--llama-cli",type=Path,required=True)
    parser.add_argument("--model-file",type=Path,required=True)
    parser.add_argument("--output",type=Path,default=Path("multifault-result.json"))
    args=parser.parse_args()
    data=run(args.llama_cli,args.model_file)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(data,indent=2,sort_keys=True,ensure_ascii=False)+"\n",
                           encoding="utf-8")
    print(json.dumps({
        "id":data["experiment_id"],
        "reserved_manifest_sha256":data["reserved_manifest_sha256"],
        "choices_before_holdout_sha256":data["frozen_pre_holdout_choices_sha256"],
        "model_calls":data["comparison"]["actual_model_calls"],
        "tasks":data["task_summaries"],
        "classics_correct":{k:v["correct"] for k,v in data["strong_classics"].items()},
        "provenance_valid":data["provenance"]["valid"],
        "promoted":data["promotion_to_core"],
    },ensure_ascii=False,sort_keys=True,indent=2))

if __name__=="__main__":
    main()
