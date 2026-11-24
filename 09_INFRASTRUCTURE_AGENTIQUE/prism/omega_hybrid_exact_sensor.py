"""Omega exact sensory bridge for finite binary relations (read-only).

Reuses the established exact verifier in concept_abstraction_lab and
the atomic reader / witness / partition from omega_hybrid_tutor07.
This is TOOL competence only, not evidence of model learning or an LLM call.
Do not expose exact answers to blinded model holdouts.
"""
from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path

from concept_abstraction_lab import check_axioms
from omega_hybrid_tutor07 import (
    atomic_membership, exact_counterexample, exact_partition,
)

AXIOMS=("reflexive","symmetric","transitive")


def canonical(x):
    return json.dumps(x,sort_keys=True,separators=(",",":"),ensure_ascii=False)


def validate_relation(nodes,edge_arrays):
    if not isinstance(nodes,list) or not 1<=len(nodes)<=8 or any(
        type(n) is not str or not n or len(n)>64 for n in nodes
    ) or len(set(nodes))!=len(nodes):
        raise ValueError("INVALID_NODE_UNIVERSE")
    if not isinstance(edge_arrays,list) or len(edge_arrays)>len(nodes)**2:
        raise ValueError("INVALID_EDGE_LIST")
    edges=[]
    for row in edge_arrays:
        if not isinstance(row,list) or len(row)!=2 or any(
            type(x) is not str or x not in nodes for x in row
        ):
            raise ValueError("EDGE_ENDPOINT_OUTSIDE_UNIVERSE")
        edges.append(tuple(row))
    if len(set(edges))!=len(edges):
        raise ValueError("DUPLICATE_DIRECTED_EDGE")
    return tuple(nodes),frozenset(edges)


def inspect_atom(packet):
    """Exact lookup of a model-proposed triple; never auto-completes the edges."""
    if not isinstance(packet,dict) or set(packet)!={"nodes","edges","triple"}:
        raise ValueError("REQUIRES_EXACT_ATOM_PACKET")
    ns,edges=validate_relation(packet["nodes"],packet["edges"])
    triple=packet["triple"]
    bits=atomic_membership(ns,edges,triple)
    if bits is None:
        raise ValueError("INVALID_TRIPLE")
    violates=bits["xy"] and bits["yz"] and not bits["xz"]
    return {
       "status":"EXACT_TOOL_ATOM_CHECK",
       "triple":list(triple),
       "bits":bits,
       "violates_transitivity_for_this_triple":violates,
       "input_sha256":sha256(canonical(packet).encode()).hexdigest(),
       "source_authenticity":"CALLER_SUPPLIED_NOT_EXTERNALLY_AUTHENTICATED",
       "model_weight_update":False,
       "model_skill_certified":False
    }


def inspect_relation(packet):
    """Return a machine-checked witness OR an exact partition when available."""
    if not isinstance(packet,dict) or set(packet)!={"nodes","edges"}:
        raise ValueError("REQUIRES_EXACT_RELATION_PACKET")
    ns,edges=validate_relation(packet["nodes"],packet["edges"])
    facts=check_axioms(ns,edges)
    failed=[ax for ax in AXIOMS if not facts[ax]["holds"]]
    result={"status":"EXACT_FINITE_RELATION_EVALUATION",
       "equivalence":not failed,
       "failed_axioms":failed,
       "input_sha256":sha256(canonical(packet).encode()).hexdigest(),
       "source_authenticity":"CALLER_SUPPLIED_NOT_EXTERNALLY_AUTHENTICATED",
       "scope":"FINITE_BINARY_RELATIONS_ONLY",
       "model_skill_certified":False,
       "model_weight_update":False}
    if not failed:
        blocks=exact_partition(ns,edges)
        if blocks is None:
            raise AssertionError("EXACT_ORACLE_AND_PARTITION_DISAGREE")
        result["certificate"]={"kind":"partition","blocks":blocks}
    elif "transitive" in failed:
        triple=exact_counterexample(ns,edges)
        if triple is None:
            raise AssertionError("EXACT_ORACLE_AND_WITNESS_DISAGREE")
        bits=atomic_membership(ns,edges,triple)
        if bits!={"xy":True,"yz":True,"xz":False}:
            raise AssertionError("INVALID_MACHINE_WITNESS")
        result["certificate"]={"kind":"missing_transitive_edge",
             "triple":triple,"premises":bits}
    else:
        result["certificate"]={"kind":"exact_axiom_failures",
           "witnesses":{ax:facts[ax]["counterexample"] for ax in failed}}
    return result


def main():
    import argparse
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--input",required=True,type=Path)
    p.add_argument("--output",required=True,type=Path)
    p.add_argument("--mode",choices=("atom","relation"),required=True)
    args=p.parse_args()
    data=json.loads(args.input.read_text(encoding="utf-8"))
    result=inspect_atom(data) if args.mode=="atom" else inspect_relation(data)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(canonical({"status":result["status"],"model_skill_certified":False}))

if __name__=="__main__": main()
