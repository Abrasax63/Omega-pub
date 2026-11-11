"""Independent geometry and adversarial-scope audit of recovered W06/I1 gate.

This is a post-integration STRESS TEST, not a new preregistered experiment.
The original W06 49-pair test was preregistered, here broadened to all 900
ordered (current,target,capacity) cases over the 15 partitions of 4 points.

The reference implementation uses set-valued equivalence relations and
disjoint-set counting. It never imports legacy refinement or block_count.
"""
from collections import Counter
from itertools import product
import json

from observer_guard_bridge import inspect_observer_evidence


def partitions_as_equivalence_sets(n=4):
    """Generate partitions via equivalence classes, without legacy functions."""
    if n != 4:
        raise ValueError("this audit intentionally fixes four states")
    found={}
    for mapping in product(range(n), repeat=n):
        rel=frozenset((a,b) for a in range(n) for b in range(n)
                      if mapping[a]==mapping[b])
        found.setdefault(rel,mapping)
    return sorted(found, key=lambda r:(len(r), tuple(sorted(r))))


def equivalence_class_count(rel, n=4):
    """Count connected components with a simple independent union/find."""
    parent=list(range(n))
    def root(x):
        while parent[x]!=x:x=parent[x]
        return x
    for a,b in rel:
        ra,rb=root(a),root(b)
        if ra!=rb:parent[ra]=rb
    return len({root(x) for x in range(n)})


def witness_partition(rel,n=4):
    labels=[]
    representatives={}
    for i in range(n):
        members=frozenset(j for j in range(n) if (i,j) in rel)
        if members not in representatives:
            representatives[members]=len(representatives)
        labels.append(representatives[members])
    return labels


def independent_decision(old_rel,target_rel,capacity):
    k=equivalence_class_count(old_rel)
    g=equivalence_class_count(target_rel)
    joint=equivalence_class_count(old_rel & target_rel)
    if g>capacity:
        return ("infeasible",k,g,joint)
    if old_rel.issubset(target_rel) and k<=capacity:
        return ("keep",k,g,joint)
    if joint<=capacity:
        return ("refine",k,g,joint)
    return ("replace",k,g,joint)


def exhaustive_reconfiguration_audit():
    rels=partitions_as_equivalence_sets()
    assert len(rels)==15
    decision_by_capacity={}
    tests=0
    for capacity in range(1,5):
        statuses=Counter()
        for current_rel,target_rel in product(rels,repeat=2):
            tests+=1
            current=witness_partition(current_rel)
            target=witness_partition(target_rel)
            got=inspect_observer_evidence({"reconfiguration":{
                "current_partition":current,
                "target_partition":target,"capacity":capacity}})
            item=got["reconfiguration"]
            expect,k,g,joint=independent_decision(current_rel,target_rel,capacity)
            if (item["decision"],item["current_blocks"],
                item["target_blocks"],item["joint_blocks"]) != (
                    expect,k,g,joint):
                raise AssertionError((current,target,capacity,expect,item))
            if item["durable_evidence_may_be_discarded"] or not item["working_representation_only"]:
                raise AssertionError("working-view-only contract broken")
            if got["scientific_certificate_issued"] or got["durable_memory_writes_performed"]:
                raise AssertionError("audit unexpectedly claimed certification or write")
            statuses[expect]+=1
        decision_by_capacity[str(capacity)]=dict(sorted(statuses.items()))
    assert tests==900
    # Equal-sized two-block partitions: on four states there are 7.
    two=[r for r in rels if equivalence_class_count(r)==2]
    assert len(two)==7
    regime=Counter()
    replacement_baseline=0
    identity_shortcut=0
    for a,b in product(two,repeat=2):
        status=independent_decision(a,b,2)[0]
        regime[status]+=1
        # Trivial policy: use target directly. It is feasible in all 49 cases.
        replacement_baseline+=1
        # Strong simple policy: keep if current equals target, else replace.
        identity_shortcut+=int(a!=b)
    assert regime=={"keep":7,"replace":42}
    assert identity_shortcut==42
    return {
        "status":"POST_INTEGRATION_EXACT_STRESS_NOT_A_NATURAL_TASK_BENCHMARK",
        "n_states":4,
        "partitions":len(rels),
        "capacities":[1,2,3,4],
        "ordered_cases":tests,
        "independent_method":"equivalence_relations_with_union_find",
        "counts_by_capacity":decision_by_capacity,
        "precommitted_W06_49_cases":dict(sorted(regime.items())),
        "direct_target_baseline_feasible":replacement_baseline,
        "identity_check_baseline_changes":identity_shortcut,
        "gate_replacement_recommendations":regime["replace"],
        "no_distinct_advantage_over_identity_check_baseline":True,
        "memory_untouched":True,
        "limitation":"Target representation is fully supplied and exact; no cost for diagnosis, learning, reconstruction or source verification is measured.",
    }


def scope_counterexample():
    """A partial probe list cannot establish closure against an omitted probe."""
    current=[0,0,0]
    chosen=[0,0,0]
    omitted=[0,0,1]
    incomplete={
        "current_partition":current,
        "selected_probe_partition":chosen,
        "listed_probe_partitions":[chosen],
        "declared_exhaustive":False,
    }
    unverified=inspect_observer_evidence({"termination":incomplete})
    asserted=inspect_observer_evidence({"termination":{
        **incomplete,"declared_exhaustive":True}})
    complete=inspect_observer_evidence({"termination":{
        **incomplete,
        "listed_probe_partitions":[chosen,omitted],
        "declared_exhaustive":True}})
    statuses=(unverified["termination"]["status"],
              asserted["termination"]["status"],
              complete["termination"]["status"])
    if statuses!=(
        "closure_unknown",
        "closed_assuming_declared_probe_list",
        "underinformative_relative_to_listed_probes",
    ):
        raise AssertionError(statuses)
    if any(x["scientific_certificate_issued"] or x["source_authenticity_verified"]
           for x in (unverified,asserted,complete)):
        raise AssertionError("falsely claimed authoritative closure")
    return {
        "status":"ADVERSARIAL_PARTIAL_CATALOG_CASE",
        "statuses":{"honest_incomplete":statuses[0],
                    "false_completeness_declaration":statuses[1],
                    "completed_catalog":statuses[2]},
        "actual_omitted_probe_distinguishes_states":True,
        "declared_exhaustive_is_unverified_assumption":True,
        "certificates_issued":0,
    }


def main():
    print("LEGACY_REPRESENTATION_STRESS "+json.dumps(
        {"stress":exhaustive_reconfiguration_audit(),
         "omitted_probe":scope_counterexample()},
        sort_keys=True,ensure_ascii=False))


if __name__=="__main__":
    main()
