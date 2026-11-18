"""Calibration and a second implementation of the finite mathematical oracle."""

from itertools import product
import unittest

from delta_bridge import (
    MAX_SYSTEMS, canonical_observations, counterexample, evaluate, propose,
)

SOURCE = (
    "# Énoncé\n"
    "On considère au plus 3 états et une dynamique déterministe totale.\n"
    "On fixe l’horizon à 2.\n"
    "L’observation est arbitraire sur son image.\n"
    "Alors Δ_h est toujours vide.\n"
).encode()


def independent_gap(transition, observation, horizon):
    alphabet = tuple(sorted(set(observation)))
    one_step = {(observation[i], observation[j]) for i, j in enumerate(transition)}
    possible = {
        (walk[0], walk[-1])
        for walk in product(alphabet, repeat=horizon + 1)
        if all(edge in one_step for edge in zip(walk, walk[1:]))
    }

    def jump(state, depth):
        return state if depth == 0 else jump(transition[state], depth - 1)

    reached = {
        (color, observation[jump(state, horizon)])
        for state, color in enumerate(observation)
    }
    return possible - reached


def valid_witness(result):
    witness = result["witness"]
    contract = result["contract"]
    transition, observation, endpoints, path = (
        witness[key] for key in ("T", "pi", "endpoints", "observed_path")
    )
    size = len(transition)
    horizon = contract["horizon"]
    edges = {(observation[i], observation[j]) for i, j in enumerate(transition)}
    return (
        1 <= size <= contract["max_states"] and len(observation) == size
        and all(0 <= target < size for target in transition)
        and (contract["observation"] != "injective" or len(set(observation)) == size)
        and len(path) == horizon + 1 and endpoints == [path[0], path[-1]]
        and all(edge in edges for edge in zip(path, path[1:]))
        and tuple(endpoints) in independent_gap(transition, observation, horizon)
    )


class DeltaBridgeTest(unittest.TestCase):
    def test_horizon_one_exhausts_full_budget(self):
        raw = SOURCE.replace(b"3 ", b"4 ").replace(b"2.", b"1.")
        report = evaluate(raw, "h1.md")
        self.assertEqual(report["status"], "CONFIRMED_WITHIN_BOUND")
        self.assertEqual(report["systems_checked"], MAX_SYSTEMS)

    def test_injective_observation(self):
        raw = SOURCE.replace(b"arbitraire", b"injective")
        report = evaluate(raw, "injective.md")
        self.assertEqual(report["status"], "CONFIRMED_WITHIN_BOUND")
        self.assertEqual(report["systems_checked"], 32)
        self.assertFalse(report["promotable"])

    def test_refutation_witness(self):
        result = evaluate(SOURCE, "arbitraire.md")
        self.assertEqual(result["status"], "REFUTED")
        self.assertTrue(valid_witness(result))

    def test_modified_contract_and_modified_evidence_are_rejected(self):
        for field in ("contract", "evidence"):
            proposal = propose(SOURCE, "sample.md")
            if field == "contract":
                proposal["contract"]["observation"] = "injective"
            else:
                proposal["claims"][0]["evidence"][0]["line"] += 1
            result = evaluate(SOURCE, "sample.md", proposal=proposal)
            self.assertEqual(result["status"], "ABSTAIN_CONTRACT_CITATION_MISMATCH")
            self.assertEqual(result["systems_checked"], 0)

    def test_changed_source_hash_rejects_earlier_proposal(self):
        proposal = propose(SOURCE, "sample.md")
        result = evaluate(SOURCE + b"\n", "sample.md", proposal=proposal)
        self.assertEqual(result["status"], "ABSTAIN_CONTRACT_CITATION_MISMATCH")

    def test_extra_or_conflicting_premise_abstains(self):
        for extra in ("La dynamique est bijective.", "Le nombre de pas est 3."):
            result = evaluate(SOURCE + extra.encode() + b"\n", "extra.md")
            self.assertEqual(result["status"], "ABSTAIN_UNSUPPORTED_OR_AMBIGUOUS_SOURCE")
            self.assertEqual(result["systems_checked"], 0)

    def test_budget_abstention(self):
        result = evaluate(SOURCE, "budget.md", budget=1)
        self.assertEqual(result, {
            "status": "ABSTAIN_BUDGET", "systems_checked": 1,
            "contract": propose(SOURCE, "budget.md")["contract"],
            "source_blob": propose(SOURCE, "budget.md")["source_blob"],
            "evidence": evaluate(SOURCE, "budget.md", arm="direct")["evidence"],
            "promotable": False,
        })

    def test_both_calculators_agree_up_to_three_states(self):
        for size in (1, 2, 3):
            for transition in product(range(size), repeat=size):
                for observation in canonical_observations(size):
                    for horizon in range(1, 6):
                        witness = counterexample(transition, observation, horizon)
                        gap = independent_gap(transition, observation, horizon)
                        self.assertEqual(bool(witness), bool(gap))
                        if witness:
                            self.assertIn(tuple(witness["endpoints"]), gap)


if __name__ == "__main__":
    unittest.main()
