"""Read-only pilot: distinguish mirrored artifacts from distinct execution roots.

All attested fields are INPUT CLAIMS, not authenticated attestations.
This module never certifies a mathematical result, and never executes a job.
"""
from __future__ import annotations

from collections import Counter

UNKNOWN = "indetermine"
SAME = "meme_origine"
DISTINCT = "executions_distinctes_resultat_identique"


def _valid_label(value):
    return isinstance(value, str) and bool(value.strip())


def assess(bundle):
    """Infer origin equivalence from a fully linked, claimed-attested DAG.

    A 'recompute' node without parents identifies one execution via run_id.
    A 'copy' node has exactly one parent and inherits its execution root.
    Unknown, broken, ambiguous or cyclic chains cause an abstention.
    Distinct execution IDs are not proof of independent scientific replication.
    """
    if not isinstance(bundle, dict):
        return UNKNOWN
    nodes, outputs = bundle.get("nodes"), bundle.get("outputs")
    if not isinstance(nodes, list) or not isinstance(outputs, list):
        return UNKNOWN
    if len(outputs) < 2 or len(outputs) != len(set(map(str, outputs))):
        return UNKNOWN
    by_id = {}
    for node in nodes:
        if not isinstance(node, dict) or not _valid_label(node.get("id")) or node["id"] in by_id:
            return UNKNOWN
        by_id[node["id"]] = node
    if not all(isinstance(o, str) and o in by_id for o in outputs):
        return UNKNOWN

    memo = {}
    active = set()

    def origin(node_id):
        if node_id in memo:
            return memo[node_id]
        if node_id in active:
            raise ValueError("cycle")
        node = by_id.get(node_id)
        if node is None or node.get("attested") is not True:
            raise ValueError("unverified lineage")
        parents = node.get("parents")
        if not isinstance(parents, list):
            raise ValueError("missing parents")
        active.add(node_id)
        try:
            if node.get("kind") == "recompute":
                if parents or not _valid_label(node.get("run_id")):
                    raise ValueError("recompute lineage not grounded")
                root = node["run_id"]
            elif node.get("kind") == "copy":
                if len(parents) != 1 or not isinstance(parents[0], str):
                    raise ValueError("ambiguous copy")
                root = origin(parents[0])
            else:
                raise ValueError("unsupported node kind")
            memo[node_id] = root
            return root
        finally:
            active.remove(node_id)

    try:
        roots = [origin(o) for o in outputs]
        if len(set(roots)) == 1:
            return SAME
        digests = [by_id[o].get("result_digest") for o in outputs]
        if not all(_valid_label(d) for d in digests) or len(set(digests)) != 1:
            return UNKNOWN
        return DISTINCT
    except (ValueError, RecursionError):
        return UNKNOWN


def fixed_digest(bundle):
    """Weak comparator: same digest is mistaken for same execution."""
    try:
        ds = [next(n for n in bundle["nodes"] if n["id"] == o)["result_digest"]
              for o in bundle["outputs"]]
        if len(ds) < 2 or any(not _valid_label(d) for d in ds):
            return UNKNOWN
        return DISTINCT if len(set(ds)) > 1 else SAME
    except (KeyError, StopIteration, TypeError):
        return UNKNOWN


def fixed_run_id(bundle):
    """Weak comparator: counts immediate producing jobs, ignoring ancestors."""
    try:
        jobs = [next(n for n in bundle["nodes"] if n["id"] == o)["run_id"]
                for o in bundle["outputs"]]
        if len(jobs) < 2 or any(not _valid_label(j) for j in jobs):
            return UNKNOWN
        return DISTINCT if len(set(jobs)) > 1 else SAME
    except (KeyError, StopIteration, TypeError):
        return UNKNOWN


def next_verification(bundle):
    """Advisory only: no job is scheduled or executed."""
    state = assess(bundle)
    if state == UNKNOWN:
        return "verifier_liens_et_integrite_des_sources"
    if state == SAME:
        return "chercher_une_execution_distincte"
    return "faire_revue_independante_du_contenu_scientifique"


def compare_synthetic(cases):
    """Counts constructed-case outcomes; NOT an external or blind benchmark."""
    arms = {"digest": fixed_digest, "run_id": fixed_run_id, "lineage": assess}
    result = {}
    for name, classifier in arms.items():
        predicted = [classifier(case["bundle"]) for case in cases]
        result[name] = dict(Counter(
            "correct" if got == case["expected"] else
            "abstentions" if got == UNKNOWN else "wrong_non_abstaining"
            for got, case in zip(predicted, cases)
        ))
    return result
