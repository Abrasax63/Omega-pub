"""Expose the distinction between literal anchors and omitted conditions."""
from collections import Counter
from time import perf_counter
import json
from gate import gate
from read import packetize, verify_packets

CASES=[
    ("Hypothese : n est pair.","Conclusion : n au carre est pair.",
     lambda n:n%2==0,lambda n:n*n%2==0),
    ("Hypothese : n est non nul.","Conclusion : n au carre est au moins un.",
     lambda n:n!=0,lambda n:n*n>=1),
]
def measure():
    counts=Counter()
    witnesses=[]
    for premise,conclusion,condition,predicate in CASES:
        assert all(not condition(n) or predicate(n) for n in range(-8,9))
        counterexample=next(n for n in range(-8,9) if not predicate(n))
        witnesses.append(counterexample)
        raw=(premise+"\n"+conclusion+"\n").encode()
        doc=packetize(raw,"fixture.md")
        packet=doc["packets"][0]["packet_id"]
        def evidence(role,line,literal):
            return dict(role=role,line=line,literal=literal,packet_id=packet)
        claims=[
            dict(claim_id="Cfaithful",packet_id=packet,evidence=[
                evidence("premise",1,premise),evidence("conclusion",2,conclusion)]),
            dict(claim_id="Comitted",packet_id=packet,evidence=[
                evidence("conclusion",2,conclusion)]),
        ]
        result=gate(raw,"fixture.md",dict(source_blob=doc["source_blob"],claims=claims))
        accepted={c["claim_id"]:c for c in result["accepted"]}
        counts["faithful_quarantined"]+="Cfaithful" in accepted
        counts["omitted_condition_quarantined"]+="Comitted" in accepted
        counts["semantic_scope_marked_unknown"]+=sum(c["hypothesis_scope"]=="NOT_ESTABLISHED"
                                                     for c in accepted.values())
        counts["exact_citations"]+=not verify_packets(raw,doc)
        assert not result["horn_rules"] and result["automatic_promotions"]==0
    return counts,witnesses
if __name__=="__main__":
    print(json.dumps(measure(),sort_keys=True))
    start=perf_counter()
    for _ in range(1000):
        measure()
    print(round(perf_counter()-start,6))
