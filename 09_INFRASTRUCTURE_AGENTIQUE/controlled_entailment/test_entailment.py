import copy
import json
import unittest

from engine import (
    UnsupportedStatement,
    evaluate_case,
    parse_statement,
    verify_certificate,
)
from evaluate import GOLD_BLOB, INPUT_BLOB, GOLD_PATH, INPUT_PATH, exact_truth_table, git_blob, run


def card(texts, facts, goal):
    return {
        "facts": facts,
        "goal": goal,
        "sources": [{"ref": "F" + str(i), "text": text}
                    for i, text in enumerate(texts)],
    }


class ControlledEntailmentTests(unittest.TestCase):
    def test_frozen_corpus_blobs(self):
        self.assertEqual(git_blob(INPUT_PATH), INPUT_BLOB)
        self.assertEqual(git_blob(GOLD_PATH), GOLD_BLOB)

    def test_two_hop_proof(self):
        example = card(["Si alpha, alors beta.", "Si beta, alors gamma."],
                       ["alpha"], "gamma")
        answer = evaluate_case(example)
        self.assertEqual(answer["verdict"], "ENTAILED")
        self.assertTrue(verify_certificate(example, answer))
        self.assertEqual(evaluate_case(example, one_pass=True)["verdict"], "NOT_ENTAILED")

    def test_missing_conjunct_has_valid_countermodel(self):
        example = card(["Si alpha et beta, alors gamma."], ["alpha"], "gamma")
        answer = evaluate_case(example)
        self.assertEqual(answer["verdict"], "NOT_ENTAILED")
        self.assertIn("gamma", answer["certificate"]["false_atoms"])
        self.assertTrue(verify_certificate(example, answer))

    def test_necessary_direction_does_not_reverse(self):
        example = card(["alpha est nécessaire pour beta."], ["alpha"], "beta")
        answer = evaluate_case(example)
        self.assertEqual(answer["verdict"], "NOT_ENTAILED")
        other = card(["alpha est nécessaire pour beta."], ["beta"], "alpha")
        self.assertEqual(evaluate_case(other)["verdict"], "ENTAILED")

    def test_unknown_and_disjunction_abstain(self):
        for text in ("alpha est corrélé à beta.",
                     "Si alpha, alors beta ou gamma.",
                     "Si alpha et non beta, alors gamma."):
            example = card([text], ["alpha"], "beta")
            self.assertEqual(evaluate_case(example)["verdict"], "ABSTAIN")

    def test_inconsistent_facts_abstain(self):
        example = card(["alpha entraîne beta."], ["alpha", "non alpha"], "beta")
        self.assertEqual(evaluate_case(example)["verdict"], "ABSTAIN")

    def test_tampered_proof_rejected(self):
        example = card(["alpha suffit pour beta."], ["alpha"], "beta")
        answer = evaluate_case(example)
        self.assertTrue(verify_certificate(example, answer))
        bad = copy.deepcopy(answer)
        bad["certificate"]["steps"][0]["source_ref"] = "nonexistent"
        self.assertFalse(verify_certificate(example, bad))

    def test_tampered_countermodel_rejected(self):
        example = card(["Si alpha et beta, alors gamma."], ["alpha"], "gamma")
        answer = evaluate_case(example)
        bad = copy.deepcopy(answer)
        bad["certificate"]["true_atoms"].append("beta")
        self.assertFalse(verify_certificate(example, bad))

    def test_heldout_exact_oracle(self):
        inputs = json.loads(INPUT_PATH.read_text(encoding="utf-8"))
        gold = {x["id"]: x for x in json.loads(GOLD_PATH.read_text(encoding="utf-8"))["cases"]}
        heldout = [x for x in inputs["cases"] if x["split"] == "holdout"]
        self.assertEqual(len(heldout), 16)
        counts = {"ENTAILED": 0, "NOT_ENTAILED": 0, "ABSTAIN": 0}
        for c in heldout:
            verdict, witness = exact_truth_table(c, gold[c["id"]])
            counts[verdict] += 1
            if verdict == "NOT_ENTAILED":
                self.assertFalse(witness[c["goal"]])
        self.assertEqual(counts, {"ENTAILED": 7, "NOT_ENTAILED": 5, "ABSTAIN": 4})

    def test_deterministic_and_local_criterion(self):
        a, b = run(), run()
        self.assertEqual(a, b)
        self.assertTrue(a["all_engine_certificates_valid"])
        self.assertEqual(a["total_cases"], 26)
        self.assertTrue(a["pre_registered_criterion_met"])

    def test_source_order_invariance(self):
        c = card(["beta entraîne delta.", "Si alpha, alors beta."], ["alpha"], "delta")
        a = evaluate_case(c)
        c["sources"].reverse()
        b = evaluate_case(c)
        self.assertEqual(a["verdict"], b["verdict"])
        self.assertTrue(verify_certificate(c, b))


if __name__ == "__main__":
    unittest.main()
