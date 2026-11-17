#!/usr/bin/env python3
"""Omega 11: manual source-anchored hypotheses + independent exact finite oracles.

This is a POST-HOC feasibility study, NOT automatic reading, proof, or a fresh
holdout. On small total deterministic maps, compare independent mathematical
representations of V7 claims and falsify intentionally wrong variants.
"""
from __future__ import annotations

import argparse
import itertools
import json
from pathlib import Path

from fidelity import ROOT, git_blob

HERE = Path(__file__).resolve().parent
SOURCE = HERE / "holdout/NOTE_RECHERCHE_V7_POLYNOME_TEMPOREL.md"
SOURCE_SHA = "6c482f97345abbb7f3d5bcd5e20da96259b276ce"
CLAIMS = HERE / "CLAIMS_POSTHOC11.json"
CLAIMS_SHA = "4f9cc58dc2a5f1addca256112840e490e0240225"


def temporal_edges(t: tuple[int, ...], pair: tuple[int, int], horizon: int) -> frozenset:
    x, y = pair
    edges = set()
    for _ in range(horizon):
        if x != y:
            edges.add((min(x,y), max(x,y)))
        x, y = t[x], t[y]
    return frozenset(edges)


def components_unionfind(n: int, edges) -> int:
    parent = list(range(n))

    def find(x):
        while x != parent[x]:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    for x,y in edges:
        a,b = find(x),find(y)
        if a != b:
            parent[b] = a
    return len({find(i) for i in range(n)})


def components_dfs(n: int, edges) -> int:
    """Independent graph traversal, including isolated vertices."""
    neighbors = [set() for _ in range(n)]
    for x,y in edges:
        neighbors[x].add(y)
        neighbors[y].add(x)
    visited = set()
    parts = 0
    for root in range(n):
        if root in visited:
            continue
        parts += 1
        pending = [root]
        visited.add(root)
        while pending:
            v = pending.pop()
            for w in neighbors[v]:
                if w not in visited:
                    visited.add(w)
                    pending.append(w)
    return parts


def incidence_rank(n: int, edges, prime: int) -> int:
    """Independent linear algebra: signed incidence rows and modular RREF."""
    matrix = []
    for a,b in sorted(edges):
        row = [0]*n
        row[a] = 1
        row[b] = (-1) % prime
        matrix.append(row)
    rank = 0
    for col in range(n):
        pivot = next((r for r in range(rank,len(matrix))
                      if matrix[r][col] % prime != 0), None)
        if pivot is None:
            continue
        matrix[rank],matrix[pivot] = matrix[pivot],matrix[rank]
        factor = pow(matrix[rank][col] % prime,-1,prime)
        matrix[rank] = [(x*factor)%prime for x in matrix[rank]]
        for row_id in range(len(matrix)):
            if row_id == rank:
                continue
            multiple = matrix[row_id][col]
            if multiple:
                matrix[row_id] = [
                    (u - multiple*v) % prime
                    for u,v in zip(matrix[row_id],matrix[rank])
                ]
        rank += 1
    return rank


def constant_on_edges_count(n: int, edges, q: int) -> int:
    """Enumerate every vector in F_q^n for q=2 and 3."""
    return sum(
        all(color[x] == color[y] for x,y in edges)
        for color in itertools.product(range(q),repeat=n)
    )


def direct_injective_histories(t: tuple[int, ...], horizon: int, q: int) -> int:
    n=len(t)
    trajectory=[]
    for x in range(n):
        orbit=[]
        v=x
        for _ in range(horizon):
            orbit.append(v)
            v=t[v]
        trajectory.append(tuple(orbit))
    count=0
    for pi in itertools.product(range(q),repeat=n):
        signatures=[tuple(pi[v] for v in orbit) for orbit in trajectory]
        count += len(set(signatures)) == n
    return count


def inclusion_exclusion(t: tuple[int, ...], horizon: int, q: int) -> int:
    n=len(t)
    pairs=list(itertools.combinations(range(n),2))
    edge_sets=[temporal_edges(t,p,horizon) for p in pairs]
    answer=0
    for mask in range(1<<len(pairs)):
        all_edges=set()
        for index in range(len(pairs)):
            if mask & (1<<index):
                all_edges.update(edge_sets[index])
        exponent=components_dfs(n,all_edges)
        sign=-1 if mask.bit_count() % 2 else 1
        answer += sign * q**exponent
    return answer


def validate_manual_claim_source() -> dict:
    if git_blob(SOURCE.read_bytes()) != SOURCE_SHA:
        raise ValueError("source document altered")
    if git_blob(CLAIMS.read_bytes()) != CLAIMS_SHA:
        raise ValueError("manual claim transcription altered")
    data=json.loads(CLAIMS.read_text(encoding="utf-8"))
    if data["status"] != "HUMAN_TRANSCRIPTION_UNVERIFIED_NOT_AUTOMATIC_NLU":
        raise ValueError("claim status improperly promoted")
    lines=SOURCE.read_text(encoding="utf-8").splitlines()
    if len(data["claims"]) != 2:
        raise ValueError("missing manual theorem candidates")
    for claim in data["claims"]:
        if claim["epistemic_status"] != "HUMAN_TRANSCRIPTION_UNVERIFIED":
            raise ValueError("unreviewed source promoted")
        for anchor in claim["source_line_anchors"]:
            n=anchor["line"]
            if not 1<=n<=len(lines) or anchor["contains"] not in lines[n-1]:
                raise ValueError("misquoted source "+claim["id"]+" line "+str(n))
    return data


def evaluate_exact() -> dict:
    provenance=validate_manual_claim_source()
    pair_cases=0
    color_checks=0
    chromatic_checks=0
    mismatches=[]
    rejected_wrong={}
    oracle_agreement_cases=0
    transformations=0
    for n in (1,2,3,4):
        all_pairs=tuple(itertools.combinations(range(n),2))
        for t in itertools.product(range(n),repeat=n):
            transformations += 1
            for horizon in (1,2,3):
                for pair in all_pairs:
                    edges=temporal_edges(t,pair,horizon)
                    components=components_unionfind(n,edges)
                    alternate=components_dfs(n,edges)
                    codim=n-components
                    r2=incidence_rank(n,edges,2)
                    r3=incidence_rank(n,edges,3)
                    pair_cases += 1
                    if (components!=alternate or codim!=r2 or codim!=r3
                            or codim>min(horizon,n-1)):
                        mismatches.append({
                            "kind":"CODIM_RANK", "n":n,"t":t,"horizon":horizon,
                            "pair":pair,"edges":sorted(edges),
                            "components":components,"dfs":alternate,
                            "codim":codim,"rank2":r2,"rank3":r3
                        })
                    else:
                        oracle_agreement_cases+=1
                    for q in (2,3):
                        count=constant_on_edges_count(n,edges,q)
                        color_checks+=1
                        if count!=q**components:
                            mismatches.append({
                                "kind":"FIELD_COLORINGS","n":n,"t":t,"horizon":horizon,
                                "pair":pair,"q":q,"observed":count,
                                "predicted":q**components
                            })
                    if ("codim_equals_number_of_distinct_edges" not in rejected_wrong
                            and codim!=len(edges)):
                        rejected_wrong["codim_equals_number_of_distinct_edges"]={
                            "n":n,"t":t,"horizon":horizon,"pair":pair,
                            "codim":codim,"wrong_prediction":len(edges)
                        }
                    active=set(v for pair_edge in edges for v in pair_edge)
                    if ("ignore_isolated_vertices" not in rejected_wrong
                            and active and len(active)<n):
                        active_k=components_dfs(
                            len(active),
                            [(sorted(active).index(x),sorted(active).index(y))
                             for x,y in edges])
                        if active_k!=components:
                            rejected_wrong["ignore_isolated_vertices"]={
                                "n":n,"t":t,"horizon":horizon,"pair":pair,
                                "correct_components":components,
                                "wrong_components":active_k
                            }
                for q in (1,2,3):
                    direct=direct_injective_histories(t,horizon,q)
                    ie=inclusion_exclusion(t,horizon,q)
                    chromatic_checks+=1
                    if direct!=ie:
                        mismatches.append({
                            "kind":"CHROMATIC_INCLUSION_EXCLUSION",
                            "n":n,"t":t,"horizon":horizon,"q":q,
                            "direct":direct,"inclusion_exclusion":ie
                        })
                    if ("all_q_to_the_power_n_observations_are_injective" not in rejected_wrong
                            and direct!=q**n):
                        rejected_wrong["all_q_to_the_power_n_observations_are_injective"]={
                            "n":n,"t":t,"horizon":horizon,"q":q,
                            "correct":direct,"wrong":q**n
                        }
    required={
        "codim_equals_number_of_distinct_edges",
        "ignore_isolated_vertices",
        "all_q_to_the_power_n_observations_are_injective"
    }
    return {
        "status":"POSTHOC_MANUAL_SEMANTIC_MAPPING_EXACT_FINITE_CHECK",
        "scientific_scope":"N_LE_4_L_LE_3_Q_IN_1_2_3_NOT_UNIVERSAL_PROOF",
        "source_git_blob":SOURCE_SHA,
        "manual_claims_git_blob":CLAIMS_SHA,
        "source_to_claim_status":provenance["status"],
        "manual_claim_ids":[x["id"] for x in provenance["claims"]],
        "number_of_total_maps_checked":transformations,
        "pair_horizon_graphs_checked":pair_cases,
        "modular_rank_oracle_agreements":oracle_agreement_cases,
        "finite_field_coloring_count_checks":color_checks,
        "direct_vs_inclusion_exclusion_checks":chromatic_checks,
        "mathematical_mismatches":mismatches[:12],
        "mathematical_mismatch_count":len(mismatches),
        "deliberately_false_claims_refuted":rejected_wrong,
        "all_three_negative_controls_refuted":set(rejected_wrong)==required,
        "finite_test_success":not mismatches and set(rejected_wrong)==required,
        "manual_mapping_independently_semantically_adjudicated":False,
        "automatic_horn_rules_added":0,
        "interpretation":"Finite exact tests support two manually transcribed V7 claims on n<=4. They DO NOT prove theorems universally or prove natural-language semantic fidelity. The actual Omega 10 original unseen-holdout remained 0/16."
    }


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--output",type=Path)
    args=p.parse_args()
    report=evaluate_exact()
    s=json.dumps(report,indent=2,ensure_ascii=False)+"\n"
    if args.output:
        dest=args.output.resolve()
        if dest.is_relative_to(ROOT):
            p.error("write reports outside the repository")
        dest.write_text(s,encoding="utf-8")
    else:
        print(s,end="")


if __name__=="__main__":
    main()
