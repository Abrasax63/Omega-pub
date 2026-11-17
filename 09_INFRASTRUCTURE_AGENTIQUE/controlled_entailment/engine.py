#!/usr/bin/env python3
"""Tiny, conservative Horn-logic parser for controlled French science cards.

NOT a general natural-language understanding system. No gold annotations,
training, networking, or external dependency used by this module.
"""
from __future__ import annotations

import re
import unicodedata


class UnsupportedStatement(ValueError):
    pass


ATOM = re.compile(r"^[a-z]+$")
FACT = re.compile(r"^[a-z]+$")


def normalize(text: str) -> str:
    lowered = unicodedata.normalize("NFKD", text.casefold())
    return "".join(c for c in lowered if not unicodedata.combining(c)).strip()


def atom(text: str) -> str:
    value = normalize(text.strip().strip(". "))
    if not ATOM.fullmatch(value) or value in ("non", "et", "ou"):
        raise UnsupportedStatement(f"non-atomic proposition: {text!r}")
    return value


def conjunction(text: str) -> tuple[str, ...]:
    if re.search(r"\bou\b|\bnon\b", normalize(text)):
        raise UnsupportedStatement("disjunction or negation requires a different logic")
    items = re.split(r"\s+et\s+", normalize(text))
    if not 1 <= len(items) <= 2:
        raise UnsupportedStatement("antecedent size outside supported grammar")
    parsed = tuple(atom(item) for item in items)
    if len(set(parsed)) != len(parsed):
        raise UnsupportedStatement("duplicate antecedent")
    return parsed


def parse_statement(text: str, ref: str) -> dict:
    raw = normalize(text)
    if not raw.endswith("."):
        raise UnsupportedStatement("missing sentence boundary")
    sentence = raw[:-1].strip()
    # All patterns must match the entire sentence; permissive substring matches
    # risk promoting a mere correlation or ambiguous qualification to a proof.
    patterns = (
        (r"si (.+), alors (.+)", "if"),
        (r"(.+) decoule de (.+)", "inverse"),
        (r"(.+) resulte de (.+)", "inverse"),
        (r"(.+) garantissent (.+)", "guarantees"),
        (r"(.+) suffit pour (.+)", "forward"),
        (r"(.+) est suffisant pour (.+)", "forward"),
        (r"(.+) est necessaire pour (.+)", "necessary"),
        (r"lorsque (.+) est vrai, (.+) est vrai", "forward"),
        (r"(.+) entraine (.+)", "forward"),
    )
    for pattern, kind in patterns:
        m = re.fullmatch(pattern, sentence)
        if not m:
            continue
        left, right = m.group(1), m.group(2)
        if kind == "inverse":
            consequence, assumptions = atom(left), conjunction(right)
        elif kind == "necessary":
            consequence, assumptions = atom(left), conjunction(right)
        elif kind == "guarantees":
            consequence, assumptions = atom(right), conjunction(left)
        else:
            consequence, assumptions = atom(right), conjunction(left)
        return {"ref": ref, "premises": list(assumptions), "conclusion": consequence}
    raise UnsupportedStatement(f"unrecognized sentence: {text!r}")


def parse_case(case: dict) -> tuple[list[str], list[dict], str]:
    facts = [atom(x) for x in case["facts"]]
    goal = atom(case["goal"])
    rules = [parse_statement(x["text"], x["ref"]) for x in case["sources"]]
    return facts, rules, goal


def proof_closure(facts: list[str], rules: list[dict]) -> tuple[set[str], list[dict]]:
    available = set(facts)
    trace = []
    round_number = 0
    while True:
        newly = []
        for rule in rules:
            if set(rule["premises"]) <= available and rule["conclusion"] not in available:
                newly.append(rule)
        if not newly:
            return available, trace
        round_number += 1
        # Add all conclusions only AFTER all rules have been tested, so the
        # certificate records true synchronous rounds, not source-list order.
        for rule in newly:
            if rule["conclusion"] not in available:
                trace.append({
                    "round": round_number,
                    "source_ref": rule["ref"],
                    "premises": list(rule["premises"]),
                    "conclusion": rule["conclusion"],
                })
        available.update(rule["conclusion"] for rule in newly)


def evaluate_case(case: dict, one_pass: bool = False) -> dict:
    try:
        facts, rules, goal = parse_case(case)
    except (UnsupportedStatement, KeyError, TypeError) as exc:
        return {"verdict": "ABSTAIN", "reason": str(exc), "certificate": None}

    if one_pass:
        # Intentionally naive baseline: fails on multi-hop entailments.
        closure = set(facts)
        closure.update(rule["conclusion"] for rule in rules
                       if set(rule["premises"]) <= set(facts))
        trace = None
    else:
        closure, trace = proof_closure(facts, rules)

    if goal in closure:
        return {
            "verdict": "ENTAILED",
            "reason": "proved_from_facts_or_rules",
            "certificate": {
                "kind": "derivation",
                "facts": facts,
                "steps": trace if trace is not None else [],
                "goal": goal,
            } if not one_pass else None,
        }

    # A least Horn model is a countermodel for non-entailment: it satisfies
    # all rules and facts and sets every atom outside the closure false.
    atoms = set(facts) | {goal}
    for rule in rules:
        atoms.update(rule["premises"])
        atoms.add(rule["conclusion"])
    return {
        "verdict": "NOT_ENTAILED",
        "reason": "countermodel_found" if not one_pass else "single_pass_no_proof",
        "certificate": {
            "kind": "horn_least_model_counterexample",
            "true_atoms": sorted(closure),
            "false_atoms": sorted(atoms - closure),
            "goal": goal,
        } if not one_pass else None,
    }


def verify_certificate(case: dict, decision: dict) -> bool:
    try:
        facts, rules, goal = parse_case(case)
    except UnsupportedStatement:
        return decision["verdict"] == "ABSTAIN"
    cert = decision.get("certificate")
    if decision["verdict"] == "ABSTAIN":
        return False
    if not isinstance(cert, dict) or cert.get("goal") != goal:
        return False
    if decision["verdict"] == "ENTAILED":
        if cert.get("kind") != "derivation" or cert.get("facts") != facts:
            return False
        known = set(facts)
        # Validate all steps independently of the engine's internal closure.
        for step in cert.get("steps", []):
            if not any(r["ref"] == step.get("source_ref")
                       and r["premises"] == step.get("premises")
                       and r["conclusion"] == step.get("conclusion")
                       for r in rules):
                return False
            if not set(step["premises"]) <= known:
                return False
            known.add(step["conclusion"])
        return goal in known
    if decision["verdict"] == "NOT_ENTAILED":
        if cert.get("kind") != "horn_least_model_counterexample":
            return False
        true = set(cert["true_atoms"])
        false = set(cert["false_atoms"])
        all_atoms = set(facts) | {goal}
        for rule in rules:
            all_atoms.update(rule["premises"])
            all_atoms.add(rule["conclusion"])
        if true & false or true | false != all_atoms or goal in true:
            return False
        return set(facts) <= true and all(
            not set(r["premises"]) <= true or r["conclusion"] in true
            for r in rules
        )
    return False
