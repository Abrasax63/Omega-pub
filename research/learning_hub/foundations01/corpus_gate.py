"""Offline corpus gate; no LLM, trainer, or access to hidden files.

The independent curator supplies split packets. Graph identity excludes the
queried triple; task identity includes the ordered triple. Bounded at 6 nodes.
"""
from collections import Counter
from itertools import permutations, product
import json

MOTIFS = tuple("".join(map(str, x)) for x in product((0, 1), repeat=3))
POSITIVE = "110"

def identities(packet):
    if type(packet) is not dict or set(packet) != {"nodes", "edges", "triple"}:
        raise ValueError("INVALID_PACKET")
    ns, es, tr = packet["nodes"], packet["edges"], packet["triple"]
    if (type(ns) is not list or not 3 <= len(ns) <= 6
        or any(type(n) is not str or not n or len(n)>64 for n in ns)
        or len(set(ns)) != len(ns)):
        raise ValueError("INVALID_NODES")
    if (type(es) is not list or len(es)>len(ns)**2
        or any(type(e) is not list or len(e)!=2 or
               any(type(n) is not str or n not in ns for n in e) for e in es)):
        raise ValueError("INVALID_EDGES")
    edges = {tuple(e) for e in es}
    if len(edges)!=len(es):
        raise ValueError("DUPLICATE_EDGE")
    if type(tr) is not list or len(tr)!=3 or any(type(n) is not str or n not in ns for n in tr):
        raise ValueError("INVALID_TRIPLE")
    candidates = []
    for order in permutations(ns):
        idx = {n:i for i,n in enumerate(order)}
        mask = sum(1 << (len(ns)*idx[a]+idx[b]) for a,b in edges)
        candidates.append((mask, tuple(idx[n] for n in tr)))
    mask, triple = min(candidates)
    return (len(ns), mask), (len(ns), mask, triple)

def motif(packet):
    identities(packet)
    edges = {tuple(e) for e in packet["edges"]}
    x,y,z = packet["triple"]
    return "".join("1" if pair in edges else "0" for pair in ((x,y),(y,z),(x,z)))

def quotas(size):
    if type(size) is not int or size<14 or size%2:
        raise ValueError("SIZE_MUST_BE_EVEN_AND_AT_LEAST_14")
    negatives = [m for m in MOTIFS if m != POSITIVE]
    q,r = divmod(size//2, len(negatives))
    return {m: size//2 if m==POSITIVE else q+int(negatives.index(m)<r)
            for m in MOTIFS}

def audit_splits(splits, sizes):
    """Fail closed; supplied packets are reviewed by curator, not proposer.

    Check exact quotas, duplicate tasks within splits, and graph disjointness
    across splits. Deliberately does not certify isolation from pretraining,
    actual model generation, or representation family disjointness.
    """
    if set(splits)!=set(sizes) or set(splits)!={"train","dev","holdout"}:
        raise ValueError("INVALID_SPLITS")
    owners, report = {}, {}
    for name in ("train","dev","holdout"):
        expected = quotas(sizes[name])
        rows = splits[name]
        if len(rows)!=sizes[name]:
            raise ValueError("WRONG_SIZE:"+name)
        seen, counts, graphs = set(), Counter(), set()
        for packet in rows:
            graph, task = identities(packet)
            if task in seen:
                raise ValueError("DUPLICATE_TASK:"+name)
            if graph in owners and owners[graph]!=name:
                raise ValueError("GRAPH_OVERLAP:"+owners[graph]+":"+name)
            owners[graph]=name
            seen.add(task)
            graphs.add(graph)
            counts[motif(packet)]+=1
        if dict(counts)!=expected:
            raise ValueError("MOTIF_QUOTA_MISMATCH:"+name)
        report[name]={"count":len(rows),"graphs":len(graphs),"motifs":dict(counts)}
    return report
