"""OMEGA-LEAN-001: actual Lean 4 kernel checks for modular theorem dependencies.

Theorem proofs are CONDITIONAL on their premises. On retraction, an old
theorem remains a valid implication but is NOT a globally applicable fact.
A separate finite-model guard blocks ex falso in contradictory environments.

Strong ATMS+index and the Omega-labeled experimental ledger use the same
model, information, cache and number of Lean rechecks. No unique Omega gain
is attributed to an isomorphic implementation.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from hashlib import sha256
from itertools import combinations
import json
from math import gcd
from pathlib import Path
import re
import subprocess
import tempfile
import time

CASEFILE=Path(__file__).resolve().parent/"cases_lean_001.json"
VALID_NAME=re.compile(r"^[A-Z][A-Z0-9_]*$")
U=60

def validate_fact(c):
    if type(c) is not dict or set(c)!={"r","m"}:
        raise ValueError("congruence must be r,m")
    r,m=c["r"],c["m"]
    if type(r) is not int or type(m) is not int or m<=0 or U%m or not 0<=r<m:
        raise ValueError("invalid modular residue")
    return c

def validate_cases(corpus):
    if corpus.get("common_modulus")!=60 or corpus.get("lean_toolchain")!="leanprover/lean4:v4.26.0":
        raise ValueError("frozen corpus/toolchain drift")
    scenarios=corpus.get("scenarios")
    if not isinstance(scenarios,list) or len(scenarios)!=4:
        raise ValueError("expected 4 fixed scenarios")
    for s in scenarios:
        if set(s)!={"id","split","sources","initial","goals","events"}:
            raise ValueError("scenario keys not frozen")
        if not VALID_NAME.fullmatch(s["id"]) or s["split"] not in ("calibration","test"):
            raise ValueError("invalid scenario identity")
        if any(not VALID_NAME.fullmatch(key) for key in (*s["sources"],*s["goals"])):
            raise ValueError("bad source/goal label")
        for c in (*s["sources"].values(),*s["goals"].values()):
            validate_fact(c)
        active=set(s["initial"])
        if active-set(s["sources"]):
            raise ValueError("unknown initial source")
        for e in s["events"]:
            if e.get("id") not in s["sources"] or e.get("op") not in ("activate","retract","replace"):
                raise ValueError("unknown source or action")
            if e["op"]=="replace":
                if set(e)!={"op","id","value"} or e["id"] not in active:
                    raise ValueError("replacement requires an active source")
                validate_fact(e["value"])
            else:
                if set(e)!={"op","id"}:
                    raise ValueError("malformed source update")
                if (e["op"]=="activate") == (e["id"] in active):
                    raise ValueError("invalid activation or retraction")
                if e["op"]=="activate":active.add(e["id"])
                else:active.remove(e["id"])
    return scenarios

def states(s):
    versions={k:dict(v) for k,v in s["sources"].items()}
    active=set(s["initial"])
    yield {"scenario":s["id"],"split":s["split"],"step":0,
           "event":None,"active":{k:dict(versions[k]) for k in sorted(active)}}
    for i,e in enumerate(s["events"],1):
        name=e["id"]
        if e["op"]=="replace":versions[name]=dict(e["value"])
        elif e["op"]=="activate":active.add(name)
        else:active.remove(name)
        yield {"scenario":s["id"],"split":s["split"],"step":i,
               "event":e,"active":{k:dict(versions[k]) for k in sorted(active)}}

def crt(items):
    a,L=0,1
    for c in items:
        validate_fact(c)
        b,m=c["r"],c["m"]
        g=gcd(L,m)
        if (b-a)%g:
            return None
        factor=m//g
        t=0 if factor==1 else ((b-a)//g * pow(L//g,-1,factor))%factor
        a=(a+L*t)%(L*factor)
        L*=factor
    return a,L

def symbolic_kind(items,q):
    sol=crt(items)
    if sol is None:return "inconsistent_environment"
    a,L=sol
    r,m=q["r"],q["m"]
    if (a-r)%gcd(L,m):return "refuted"
    if L%m==0 and a%m==r:return "entailed"
    return "undetermined"

def finite_kind(items,q):
    feasible=[n for n in range(U) if all(n%p["m"]==p["r"] for p in items)]
    if not feasible:return "inconsistent_environment"
    matches=sum(n%q["m"]==q["r"] for n in feasible)
    return ("entailed" if matches==len(feasible) else
            "refuted" if matches==0 else "undetermined")

def minimal_supports(active,q,kind,method):
    ids=sorted(active)
    result=[]
    for n in range(1,min(3,len(ids))+1):
        for support in combinations(ids,n):
            if any(set(prior).issubset(support) for prior in result):
                continue
            vals=[active[x] for x in support]
            decision=(symbolic_kind(vals,q) if method=="symbolic"
                      else finite_kind(vals,q))
            if decision==kind:
                result.append(support)
    return result

def conflict_pairs(active):
    return [list(pair) for pair in combinations(sorted(active),2)
            if crt([active[k] for k in pair]) is None]

def cert_key(scenario,goal,statement,kind,support,active):
    data={"scenario":scenario,"goal":goal,"statement":statement,
          "kind":kind,
          "support":[{"source":id,**active[id]} for id in support]}
    canonical=json.dumps(data,sort_keys=True,separators=(",",":"))
    return sha256(canonical.encode("utf-8")).hexdigest()

def build_lean(theorems):
    """Generate actual theorem chains with explicit Lean dependencies.

    Each certificate yields three Lean *theorem* declarations:
    support_i -> derived_i -> final_i. The terminal statement depends on
    actual source assumptions, not on a guessed globally true premise.
    """
    lines=["import Init","set_option autoImplicit false",
           "namespace OmegaFormalCongruences", ""]
    for idx,cert in enumerate(theorems):
        args=" ".join(
            f"(h_{j} : n % {p['m']} = {p['r']})"
            for j,p in enumerate(cert["premises"]))
        lhs=f"(n : Nat) {args}".strip()
        q=cert["query"]
        atom=f"(n % {q['m']} = {q['r']})"
        goal=f"¬ {atom}" if cert["kind"]=="refuted" else atom
        inputs=" ".join(f"h_{j}" for j in range(len(cert["premises"])))
        application=f"n {inputs}".strip()
        base=f"support_{idx}"
        mid=f"derived_{idx}"
        final=f"final_{idx}"
        lines.extend([
            f"theorem {base} {lhs} : {goal} := by",
            "  omega",
            f"theorem {mid} {lhs} : {goal} := by",
            f"  exact {base} {application}",
            f"theorem {final} {lhs} : {goal} := by",
            f"  exact {mid} {application}",
            "",
        ])
    lines.append("end OmegaFormalCongruences")
    source="\n".join(lines)+"\n"
    for bad in ("sorry","admit","axiom","unsafe","native_decide"):
        if re.search(rf"\b{bad}\b",source):
            raise ValueError("untrusted Lean primitive forbidden")
    return source

def run_lean(lean,source,outdir,label):
    path=outdir/(label+".lean")
    path.write_text(source,encoding="utf-8")
    begin=time.perf_counter()
    p=subprocess.run([str(lean),str(path)],capture_output=True,
                     text=True,timeout=140)
    elapsed=time.perf_counter()-begin
    return {"success":p.returncode==0,"stdout":p.stdout[-2500:],
            "stderr":p.stderr[-2500:],"elapsed_seconds":round(elapsed,6),
            "path":str(path)}

def negative_tests(lean,outdir):
    """Proof checker must reject false statements but accept conditional
    ex falso. Actual system must veto using ex falso globally.
    """
    prologue="import Init\nset_option autoImplicit false\n"
    examples={
        "forged":(False,prologue+
                  "theorem forged (n : Nat) (h : n % 2 = 0) : n % 3 = 2 := by\n  omega\n"),
        "missing_source":(False,prologue+
                          "theorem stale (n : Nat) : n % 3 = 2 := by\n  omega\n"),
        "ex_falso_is_derivable":(True,prologue+
                                "theorem explosion (n : Nat) (he : n % 2 = 0) (ho : n % 2 = 1) : n % 3 = 2 := by\n  omega\n"),
    }
    checks={}
    for name,(expect,source) in examples.items():
        run=run_lean(lean,source,outdir,"negative_"+name)
        if run["success"]!=expect:
            raise AssertionError(f"Lean negative/control {name} unexpected result: {run}")
        checks[name]={"lean_compiled":run["success"],
                      "expected":expect,"elapsed_seconds":run["elapsed_seconds"]}
    return checks

def evaluate(corpus,lean,outdir):
    scenarios=validate_cases(corpus)
    modes=("full_recompile","strong_atms_index","omega_proof_ledger")
    caches={m:set() for m in modes}
    count={m:Counter() for m in modes}
    durations=defaultdict(float)
    certificate_archive={}
    summaries=defaultdict(Counter)
    recorded=[]
    for scenario in scenarios:
        initial_unrevised_status={}
        for state in states(scenario):
            active=state["active"]
            scenario_id=state["scenario"]
            split=state["split"]
            consistent=crt(active.values()) is not None
            conflict=conflict_pairs(active)
            if not consistent and not conflict:
                raise AssertionError("missing pairwise conflict")
            result={}
            prepared={}
            for qid,q in sorted(scenario["goals"].items()):
                oracle=finite_kind(active.values(),q)
                status=symbolic_kind(active.values(),q)
                if oracle!=status:
                    raise AssertionError(f"CRT disagrees with finite oracle {scenario_id}:{state['step']}:{qid}")
                if state["step"]==0:
                    initial_unrevised_status[qid]=status
                previous_answer=initial_unrevised_status[qid]
                summaries[split]["no_revision_status_mismatches"]+=(previous_answer!=status)
                summaries[split]["no_revision_false_confident_claims"]+=(
                    previous_answer in ("entailed","refuted") and previous_answer!=status)
                if not consistent and status!="inconsistent_environment":
                    raise AssertionError("explosion risk")
                supports=[]
                if status in ("entailed","refuted"):
                    symbolic=minimal_supports(active,q,status,"symbolic")
                    brute=minimal_supports(active,q,status,"finite")
                    if symbolic!=brute:
                        raise AssertionError("ATMS justification disagreement")
                    if not symbolic:
                        raise AssertionError("entailed/refuted without proof")
                    for support in symbolic:
                        key=cert_key(scenario_id,qid,q,status,support,active)
                        cert={"key":key,"query_id":qid,"query":q,
                              "kind":status,
                              "source_ids":list(support),
                              "premises":[active[x] for x in support],
                              "version_id":f"{scenario_id}:{state['step']}"}
                        if key in prepared and prepared[key]["premises"]!=cert["premises"]:
                            raise AssertionError("certificate hash collision")
                        prepared[key]=cert
                        supports.append(key)
                        if key not in certificate_archive:
                            certificate_archive[key]={
                                "origin_version":cert["version_id"],
                                "source_ids":list(support),
                                "premises":[dict(active[x]) for x in support],
                                "query_id":qid,"query":dict(q),"kind":status,
                                "reused_after_verification":0}
                result[qid]={"status":status,"proof_keys":supports,
                             "conflicting_pairs":conflict if not consistent else []}
                summaries[split]["judgments"]+=1
                summaries[split][status]+=1
                summaries[split]["active_proof_paths"]+=len(supports)
                summaries[split]["multiple_support_cases"]+=len(supports)>=2
            if not consistent and any(r["proof_keys"] for r in result.values()):
                raise AssertionError("inconsistent environment certified a claim")
            # Only compile genuinely new terms for the strong index and the
            # Omega-labeled ledger; compile every active term for full control.
            for mode in modes:
                candidates=sorted(prepared) if mode=="full_recompile" else sorted(
                    k for k in prepared if k not in caches[mode])
                if candidates:
                    source=build_lean([prepared[k] for k in candidates])
                    label=f"{scenario_id}_{state['step']:02d}_{mode}"
                    res=run_lean(lean,source,outdir,label)
                    if not res["success"]:
                        raise AssertionError(f"Lean kernel did not check {label}: {res}")
                    count[mode]["compiled_files"]+=1
                    count[mode]["compiled_proof_chains"]+=len(candidates)
                    count[mode]["checked_theorem_declarations"]+=3*len(candidates)
                    durations[mode]+=res["elapsed_seconds"]
                    caches[mode].update(candidates)
                count[mode]["active_certificate_applications"]+=len(prepared)
                if mode!="full_recompile":
                    if not set(prepared).issubset(caches[mode]):
                        raise AssertionError("active but unverified proof")
            if caches["strong_atms_index"]!=caches["omega_proof_ledger"]:
                raise AssertionError("strong ATMS vs Omega cache diverged")
            for key in prepared:
                if key in certificate_archive:
                    certificate_archive[key]["reused_after_verification"]+=(
                        key in caches["omega_proof_ledger"])
            recorded.append({**state,"consistent":consistent,
                             "conflicting_pairs":conflict,
                             "queries":result,
                             "no_revision_verdicts":dict(initial_unrevised_status),
                             "active_certificate_keys":sorted(prepared)})
            summaries[split]["states"]+=1
    # Counters are accumulated globally; correct split calls additionally
    # derived from the events, but do not claim per-split runtime costs.
    if len(recorded)!=24:raise AssertionError("frozen revision count differs")
    if sum(summaries[k]["judgments"] for k in summaries)!=91:
        raise AssertionError("frozen query count differs")
    if count["strong_atms_index"]!=count["omega_proof_ledger"]:
        raise AssertionError("index/Omega unequal operations")
    for key,archive in certificate_archive.items():
        if not archive["reused_after_verification"]:
            raise AssertionError("no certificate compiled and reused")
    negatives=negative_tests(lean,outdir)
    return {
        "status":"ACTUAL_LEAN4_KERNEL_CHECKED_CONDITIONAL_CONGRUENCE_THEOREMS",
        "frozen_cases_commit":"de4a08399a0f99d420f13e360fbf1deed5785161",
        "prereg_commit":"5ec12b01b21f6e1216e81922aed9a01096b05ebc",
        "expected_toolchain":"leanprover/lean4:v4.26.0",
        "model":"synthetic_modular_conditional_proof_dependency",
        "summaries":{k:dict(v) for k,v in summaries.items()},
        "lean_check_counts":{m:dict(count[m]) for m in modes},
        "lean_wall_clock_seconds_non_comparable":{
            m:round(durations[m],6) for m in modes},
        "unique_historical_verified_implications":len(certificate_archive),
        "negative_kernel_tests":negatives,
        "strong_ATMS_vs_Omega_exact_agreement":True,
        "independent_finite_residue_oracle":True,
        "trusted_source_attestation":False,
        "scientific_generalization_verified":False,
        "records":recorded,
        "historical_certificates":certificate_archive,
    }

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--lean",default="lean")
    parser.add_argument("--output",required=True)
    parser.add_argument("--proof-directory",required=True)
    a=parser.parse_args()
    corpus=json.loads(CASEFILE.read_text(encoding="utf-8"))
    outdir=Path(a.proof_directory)
    outdir.mkdir(parents=True,exist_ok=True)
    result=evaluate(corpus,a.lean,outdir)
    Path(a.output).write_text(json.dumps(result,indent=2,sort_keys=True,
                                        ensure_ascii=False),encoding="utf-8")
    print("OMEGA_LEAN_PROOF_REVISION "+json.dumps({
        k:result[k] for k in (
            "status","summaries","lean_check_counts",
            "unique_historical_verified_implications",
            "negative_kernel_tests",
            "strong_ATMS_vs_Omega_exact_agreement",
            "independent_finite_residue_oracle")
    },sort_keys=True,ensure_ascii=False))

if __name__=="__main__":
    main()
