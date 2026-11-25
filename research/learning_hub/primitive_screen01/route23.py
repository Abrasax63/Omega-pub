"""ROUTE23: prospective diagnostic-to-experiment gate, not an inference router.
Four correlated single-step probes never establish skill retention.
No model execution, no automatic training or promotion.
"""
import argparse,json,math,copy
from pathlib import Path

KINDS=("copy","select","membership","reverse")
EXPECTED="2f2a769b5aa7482baa96db11b208d66e2b15aae5f28b2d9a00735668561290b8"
EPS=1e-6

def need(ok,msg):
    if not ok:raise ValueError(msg)
def finite(x):
    return type(x) in (int,float) and math.isfinite(x)

def decide(report):
    need(report.get("status")=="REAL_QWEN_REVERSIBLE_DISPLACEMENT_DIAGNOSTIC","STATUS")
    need(report.get("first_block_adapter_sha")==EXPECTED and report.get("reproduction_updates")==128,"CHECKPOINT")
    need(report.get("proposed_probe_updates")==4 and report.get("retained_probe_updates")==0,"PROBE_COUNT")
    need(report.get("promotion_authorized") is False and report.get("weights_published") is False,"SCOPE")
    rows=report.get("probes",[])
    need(len(rows)==4 and {z["probe"] for z in rows}==set(range(4)),"COVERAGE")
    need(len({z["new_pair"] for z in rows})==4,"NEW_PAIR_DUPLICATE")
    inc={arm:{scope:0 for scope in ("anchor","disjoint_train_audit")} for arm in ("ordinary","protected")}
    new_gain={arm:[] for arm in inc}; ratios=[];fallbacks=0;conflicts=0
    seen=set()
    for z in rows:
        for field in ("anchor_pairs","disjoint_train_audit_pairs"):
            need(set(z[field])==set(KINDS),"SKILL_COVERAGE")
            for q in z[field].values():
                need(isinstance(q,str) and q not in seen,"REUSED_ANCHOR")
                seen.add(q)
        n=z["proposed_norm"];v=z["realized_norm"]
        need(finite(n) and finite(v) and n>0 and 0<=v<=n*(1+1e-5),"NORM")
        ratios.append(v/n)
        fallback=z["projection"]["fallback"] or z["rounding_fallback"]
        need(not fallback or v<=1e-10,"FALLBACK")
        fallbacks+=int(fallback)
        nconf=z["projection"]["violations_before"]
        need(type(nconf) is int and 0<=nconf<=4,"VIOLATIONS")
        conflicts+=nconf
        for stage in ("before","ordinary","protected"):
            d=z[stage];need(finite(d["new"]),"NEW_LOSS")
            for scope in ("anchor","disjoint_train_audit"):
                need(set(d[scope])==set(KINDS) and all(finite(v) for v in d[scope].values()),"OLD_LOSS")
        for arm in inc:
            new_gain[arm].append(z["before"]["new"]-z[arm]["new"])
            for scope in inc[arm]:
                inc[arm][scope]+=sum(z[arm][scope][s]>z["before"][scope][s]+EPS for s in KINDS)
    for scope,key in (("anchor","anchor_loss_increases"),("disjoint_train_audit","disjoint_train_loss_increases")):
        need(report[key]=={arm:inc[arm][scope] for arm in inc},"SUMMARY_MISMATCH")
    for arm in inc:
        declared=report["new_loss_deltas"][arm]
        need(len(declared)==4 and all(finite(a) and abs(a+b)<=1e-9 for a,b in zip(declared,new_gain[arm])),"NEW_GAIN_MISMATCH")
    ordinary=sum(new_gain["ordinary"]);protected=sum(new_gain["protected"])
    useful=sum(g>EPS for g in new_gain["protected"])
    retained=sum(v>=.1 for v in ratios)
    old_improved=inc["protected"]["anchor"]<inc["ordinary"]["anchor"] and inc["protected"]["disjoint_train_audit"]<=inc["ordinary"]["disjoint_train_audit"]
    # Prospective engineering screen, not statistical significance or proof.
    if ordinary<=EPS:
        route="DIAGNOSE_NEW_OBJECTIVE"
    elif conflicts==0 and inc["ordinary"]["disjoint_train_audit"]==0:
        route="SHARED_BLOCK_CONTROL"
    elif old_improved and protected>=.5*ordinary and useful>=3 and retained>=3 and fallbacks<=1:
        route="PROTECTED_VS_ORDINARY_BLOCK"
    else:
        route="COMPARE_ISOLATED_ADAPTER_AND_PROTECTION"
    return dict(status="PROSPECTIVE_ROUTE23",recommended_next_experiment=route,ordinary_loss_gain=ordinary,protected_loss_gain=protected,protected_new_loss_decrease_probes=useful,nontrivial_displacements=retained,fallbacks=fallbacks,linear_conflicts=conflicts,old_loss_increases=inc,thresholds=dict(min_new_loss_gain_fraction=.5,min_useful_probes=3,min_displacement_norm_fraction=.1,max_fallbacks=1),scope="four correlated train-only probes; route is hypothesis selection, not a competence or architecture verdict",training_authorized=False,promotion_authorized=False)

def fixture(mode):
    rows=[]
    for i in range(4):
        old={s:1.0 for s in KINDS}
        ordinary={s:1.1 for s in KINDS} if mode!="shared" else {s:.9 for s in KINDS}
        protected={s:.95 for s in KINDS}
        fallback=mode=="isolated"
        if fallback:protected=old.copy()
        rows.append(dict(probe=i,new_pair=f"new-{i}",anchor_pairs={s:f"a-{s}-{i}" for s in KINDS},disjoint_train_audit_pairs={s:f"h-{s}-{i}" for s in KINDS},proposed_norm=1.,realized_norm=0. if fallback else .8,projection=dict(fallback=fallback,violations_before=0 if mode=="shared" else 4),rounding_fallback=False,before=dict(new=1.,anchor=old,disjoint_train_audit=old),ordinary=dict(new=1.1 if mode=="diagnose" else .8,anchor=ordinary,disjoint_train_audit=ordinary),protected=dict(new=1. if fallback else .85,anchor=protected,disjoint_train_audit=protected)))
    return dict(status="REAL_QWEN_REVERSIBLE_DISPLACEMENT_DIAGNOSTIC",first_block_adapter_sha=EXPECTED,reproduction_updates=128,proposed_probe_updates=4,retained_probe_updates=0,promotion_authorized=False,weights_published=False,probes=rows,anchor_loss_increases={a:sum(z[a]["anchor"][s]>z["before"]["anchor"][s]+EPS for z in rows for s in KINDS) for a in ("ordinary","protected")},disjoint_train_loss_increases={a:sum(z[a]["disjoint_train_audit"][s]>z["before"]["disjoint_train_audit"][s]+EPS for z in rows for s in KINDS) for a in ("ordinary","protected")},new_loss_deltas={a:[z[a]["new"]-z["before"]["new"] for z in rows] for a in ("ordinary","protected")})
def selftest():
    expected={"shared":"SHARED_BLOCK_CONTROL","protected":"PROTECTED_VS_ORDINARY_BLOCK","isolated":"COMPARE_ISOLATED_ADAPTER_AND_PROTECTION","diagnose":"DIAGNOSE_NEW_OBJECTIVE"}
    for k,v in expected.items():
        q=decide(fixture(k));need(q["recommended_next_experiment"]==v and not q["training_authorized"],"ROUTE")
    for mutate in (lambda q:q["probes"].pop(),lambda q:q["anchor_loss_increases"].update(ordinary=99),lambda q:q["probes"][0].update(realized_norm=float("nan")),lambda q:q["probes"][1].update(anchor_pairs=q["probes"][0]["anchor_pairs"])):
        q=copy.deepcopy(fixture("protected"));mutate(q)
        try:decide(q)
        except ValueError:pass
        else:raise AssertionError("CORRUPT_EVIDENCE_ACCEPTED")
    print("ROUTE23_FIXTURE_OK: four routing cases and four invalid evidence controls; zero model updates")
if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("cmd",choices=["selftest","decide"]);p.add_argument("--report");a=p.parse_args()
    if a.cmd=="selftest":selftest()
    else:print(json.dumps(decide(json.loads(Path(a.report).read_text())),indent=2,allow_nan=False))
