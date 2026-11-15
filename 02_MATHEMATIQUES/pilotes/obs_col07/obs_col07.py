#!/usr/bin/env python3
"""OBS-COL-07: bounded L*-style observation-table learning, real Omega P1 gate.

The learner sees only membership(word) for words of length <=7, never
the target state count or transition table. A classical baseline uses
the exact SAME algorithm without Omega P1. No Omega gain is asserted.
"""
from __future__ import annotations
from hashlib import sha256
from itertools import product
from pathlib import Path
import json
import sys

ROOT = Path(__file__).resolve().parents[3]
PRISM = ROOT / "09_INFRASTRUCTURE_AGENTIQUE" / "prism"
if str(PRISM) not in sys.path:
    sys.path.insert(0, str(PRISM))
from planner import plan_mission  # real module inherited from PR #90

ABC = ("p", "r")
H = 7
EVAL_LENGTHS = (8, 9, 10)
WORLDS = ("TOGGLE2", "CYCLE3", "CYCLE4", "SET2", "MIX3", "DELAY9_OOD")


def generator(kind):
    """Experimenter-only source. Never provided to the learner or Omega P1."""
    if kind == "TOGGLE2":
        return ((1, 0), (0, 1), (0, 1))
    if kind == "CYCLE3":
        return ((1, 2, 0), (0, 1, 2), (0, 1, 1))
    if kind == "CYCLE4":
        return ((1, 2, 3, 0), (0, 1, 2, 3), (0, 1, 1, 0))
    if kind == "SET2":
        return ((1, 1), (0, 1), (0, 1))
    if kind == "MIX3":
        return ((1, 2, 0), (0, 0, 0), (0, 1, 1))
    if kind == "DELAY9_OOD":
        return ((1, 2, 3, 4, 5, 6, 7, 8, 8), tuple(range(9)), (0,)*8+(1,))
    raise ValueError("unregistered world")


def truth(source, word):
    if not isinstance(word, str) or any(c not in ABC for c in word):
        raise ValueError("bad action word")
    p, r, outputs = source
    state = 0
    for c in word:
        state = (p if c == "p" else r)[state]
    return outputs[state]


class BlackBox:
    """Only the generator knows the actual world; training/eval are disjoint."""
    def __init__(self, kind):
        self._source = generator(kind)
        self.train_log = []
        self.eval_log = []

    def membership(self, word):
        if not isinstance(word, str) or len(word) > H:
            raise ValueError("training cannot access reserved histories")
        result = truth(self._source, word)
        self.train_log.append(word)
        return result

    def evaluate(self, word):
        if not isinstance(word, str) or len(word) not in EVAL_LENGTHS:
            raise ValueError("reserved evaluator only")
        self.eval_log.append(word)
        return truth(self._source, word)


def all_words(lo, hi):
    for length in range(lo, hi+1):
        for letters in product(ABC, repeat=length):
            yield "".join(letters)


class Membership:
    def __init__(self, oracle, use_p1):
        self.oracle = oracle
        self.use_p1 = use_p1
        self.cache = {}
        self.order = []
        self.mission_ids = []
        self.p1_calls = 0

    def __call__(self, word):
        if not isinstance(word, str) or len(word)>H or any(c not in ABC for c in word):
            raise ValueError("invalid or reserved training probe")
        if word in self.cache:
            return self.cache[word]
        if len(self.cache) >= 256:
            raise RuntimeError("budget exhausted")
        if self.use_p1:
            step = "Reset then observe after: " + (word or "[empty]")
            mission_id = "OBS-COL-07-" + sha256(word.encode()).hexdigest()[:16]
            mission = {"mission_id": mission_id, "mission_type": "mathematical",
                       "question": "Falsify a finite observable-machine conjecture",
                       "requires_computation": True,
                       "decision_context": {"blocking_uncertainty": "Observed traces may not identify the states",
                                            "verification": step,
                                            "verification_effect": "A measured output can refute the candidate machine"}}
            plan = plan_mission(mission)
            if (plan["next_action"]["action"] != "verify" or
                    plan["next_action"]["next_step"] != step):
                raise AssertionError("actual Omega P1 did not plan this query")
            self.p1_calls += 1
            self.mission_ids.append(mission_id)
        value = self.oracle.membership(word)
        self.cache[word] = value
        self.order.append(word)
        return value


def predict(machine, word):
    q = machine["initial"]
    for a in word:
        q = machine["transitions"][q][a]
    return machine["outputs"][q]


class BoundedLStar:
    """Closed/consistent observation table with finite counterexample search."""
    def __init__(self, member):
        self.ask = member
        self.S, self.E = [""], [""]
        self.refinements = []
        self.counterexamples = []

    def row(self, prefix):
        return tuple(self.ask(prefix + suffix) for suffix in self.E)

    def close_consistent(self):
        for _ in range(80):
            existing = {self.row(s) for s in self.S}
            found = None
            for s in self.S:
                for a in ABC:
                    if self.row(s+a) not in existing:
                        found = s+a
                        break
                if found is not None:
                    break
            if found is not None:
                if found not in self.S:
                    self.S.append(found)
                self.refinements.append({"new_state_prefix": found})
                continue
            found = None
            for i, s in enumerate(self.S):
                for t in self.S[i+1:]:
                    if self.row(s) != self.row(t):
                        continue
                    for a in ABC:
                        for e in self.E:
                            if self.ask(s+a+e) != self.ask(t+a+e):
                                found = a+e
                                break
                        if found is not None:
                            break
                    if found is not None:
                        break
                if found is not None:
                    break
            if found is not None:
                if found in self.E:
                    raise AssertionError("inconsistent but non-progressing table")
                self.E.append(found)
                self.refinements.append({"new_distinguishing_suffix": found})
                continue
            return
        raise RuntimeError("learner table did not stabilize")

    def hypothesis(self):
        self.close_consistent()
        reps, index = [], {}
        for s in self.S:
            key = self.row(s)
            if key not in index:
                index[key] = len(reps)
                reps.append(s)
        return {"initial": index[self.row("")], "states": len(reps),
                "representatives": reps,
                "outputs": [self.ask(s) for s in reps],
                "transitions": [{a:index[self.row(s+a)] for a in ABC} for s in reps]}

    def learn(self):
        for _ in range(25):
            machine = self.hypothesis()
            counterexample = None
            for word in all_words(0, H):
                if self.ask(word) != predict(machine, word):
                    counterexample = word
                    break
            if counterexample is None:
                return machine
            self.counterexamples.append(counterexample)
            self.refinements.append({"bounded_counterexample": counterexample})
            for i in range(len(counterexample)+1):
                p = counterexample[:i]
                if p not in self.S:
                    self.S.append(p)
        raise RuntimeError("more than 25 refinements")


def independent_minimal_count(source):
    """Evaluator-only partition refinement on true hidden transition graph."""
    p, r, outs = source
    n = len(outs)
    partition = list(outs)
    for _ in range(n+1):
        signatures = [(partition[i], partition[p[i]], partition[r[i]])
                      for i in range(n)]
        labels = {}
        updated = [labels.setdefault(sig, len(labels)) for sig in signatures]
        old_equiv = {(i,j) for i in range(n) for j in range(n) if partition[i]==partition[j]}
        new_equiv = {(i,j) for i in range(n) for j in range(n) if updated[i]==updated[j]}
        if old_equiv == new_equiv:
            return len(set(updated))
        partition = updated
    raise AssertionError("partition refinement did not converge")


def episode(kind):
    box, basebox = BlackBox(kind), BlackBox(kind)
    gated = Membership(box, use_p1=True)
    classical = Membership(basebox, use_p1=False)
    learner = BoundedLStar(gated)
    control = BoundedLStar(classical)
    model = learner.learn()
    baseline = control.learn()
    if model != baseline or gated.order != classical.order:
        raise AssertionError("P1-gated and classical algorithms diverged")
    errors = []
    holdout_count = 0
    for word in all_words(min(EVAL_LENGTHS), max(EVAL_LENGTHS)):
        answer = box.evaluate(word)
        if basebox.evaluate(word) != answer:
            raise AssertionError("comparison truths diverged")
        holdout_count += 1
        if predict(model, word) != answer:
            errors.append(word)
    return {
        "world_posthoc_only": kind, "learned_states": model["states"],
        "true_minimal_states_posthoc": independent_minimal_count(generator(kind)),
        "candidate_machine": model, "query_count": len(gated.cache),
        "baseline_query_count": len(classical.cache),
        "p1_calls": gated.p1_calls, "first_p1_mission_ids": gated.mission_ids[:3],
        "same_probe_order_as_classical": gated.order == classical.order,
        "same_model_as_classical": model == baseline,
        "table_refinements": learner.refinements,
        "counterexamples_from_training": learner.counterexamples,
        "holdout_total": holdout_count,
        "holdout_errors": len(errors), "first_errors": errors[:8],
        "status": "OUT_OF_HORIZON_WARNING" if errors else "COMPATIBLE_ON_RESERVED_TESTS",
        "model_calls": 0, "scientifically_certified": False,
    }


def run():
    result = [episode(kind) for kind in WORLDS]
    return {
        "protocol": "OBS-COL-07",
        "prereg_commit": "be19e777f76b77ba3cb464b9a8ed12ce9fa81de4",
        "method": "bounded L-star style closed/consistent residual-state learning",
        "training_horizon": H, "reserved_lengths": list(EVAL_LENGTHS),
        "real_p1_used": True, "p1_selects_probes": False,
        "baseline": "same classical observation table learner without P1",
        "no_true_equivalence_oracle": True, "model_calls": 0,
        "no_claim_of_open_world_discovery": True,
        "worlds": result,
    }


if __name__ == "__main__":
    print(json.dumps(run(), ensure_ascii=False, indent=2))
