"""Offline regression suite: no network, model, paid API or gradients."""
import copy
import json
from pathlib import Path
import sys
import unittest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import pilot
import score


GOOD_S1 = """def transform(s):
    out = []
    for piece in s.split(';'):
        if piece:
            out.append(piece + ':' + str(len(piece)))
    return out
"""
GOOD_S2 = """def transform(s):
    out = []
    for i in range(1, len(s)):
        if s[i].lower() == s[i-1].lower():
            out.append('same')
        else:
            out.append('different')
    return out
"""
GOOD_H1 = """def transform(s):
    out = []
    for i in range(len(s)-2):
        part = s[i:i+3]
        if part == part[::-1]:
            out.append(part)
    return out
"""
GOOD_H2 = """def transform(s):
    n = 0
    out = []
    for ch in s:
        if ch.isdigit():
            n += int(ch)
            out.append(str(n))
    return out
"""
GOOD_H3 = """def transform(s):
    balance = 0
    valid = True
    out = []
    for i in range(len(s)):
        if s[i] == '(':
            balance += 1
        else:
            balance -= 1
        if balance < 0:
            valid = False
        if valid and balance == 0:
            out.append(str(i+1))
    return out
"""
BAD = "def transform(s):\n    return []\n"


class FakeModel:
    def __init__(self, successful_repair=True):
        self.successful_repair = successful_repair
        self.call_log = []
        self.prompts = []

    def __call__(self, messages, tokens, tag):
        self.prompts.append((tag, messages[-1]["content"]))
        self.call_log.append({"tag": tag, "cap": tokens, "usage": {}})
        if tag == "train:S1:initial":
            code = BAD
        elif tag == "train:S2:initial":
            code = GOOD_S2
        elif tag == "train:S1:repair":
            code = GOOD_S1 if self.successful_repair else BAD
        elif tag == "train:S1:lesson":
            return json.dumps({"lesson": "Validate separators and boundary cases, then preserve the correct output format."})
        elif tag.startswith("B:") and self.successful_repair:
            code = {"B:H1": GOOD_H1, "B:H2": GOOD_H2,
                    "B:H3": GOOD_H3}[tag]
        else:
            code = BAD
        return json.dumps({"code": code})


class Contract(unittest.TestCase):
    def test_frozen_git_blobs_and_partition(self):
        train, eval_public = pilot.public_contract()
        for name, pinned in pilot.PINS.items():
            raw = (HERE / name).read_bytes()
            self.assertEqual(pilot.git_blob(raw), pinned)
            self.assertNotEqual(pilot.git_blob(raw+b"tamper"), pinned)
        hidden = pilot.load_frozen("EVAL_SEALED_FROZEN.json")["holdout"]
        self.assertEqual(len(hidden), 3)
        self.assertEqual(sum(len(x["hidden_cases"]) for x in hidden), 15)
        self.assertFalse({x["family"] for x in train} &
                         {x["family"] for x in eval_public})
        for item, secret in zip(eval_public, hidden):
            self.assertEqual(item["id"], secret["id"])
            self.assertFalse({x["input"] for x in item["public_examples"]} &
                             {x["input"] for x in secret["hidden_cases"]})

    def test_positive_control_all_sealed_golds(self):
        hidden = pilot.load_frozen("EVAL_SEALED_FROZEN.json")["holdout"]
        for item, code in zip(hidden, [GOOD_H1, GOOD_H2, GOOD_H3]):
            with self.subTest(item=item["id"]):
                self.assertTrue(pilot.safe.validate_program(code))
                self.assertEqual(
                    pilot.score_public(code, item["hidden_cases"])["correct"], 5)

    def test_winning_memory_and_blind_score(self):
        fake = FakeModel()
        r = pilot.run(fake)
        self.assertEqual(r["learning"]["self_selected_task"], "S1")
        self.assertTrue(r["learning"]["improvement_on_practice"])
        self.assertTrue(r["learning"]["admitted_memory"])
        self.assertEqual(r["C"]["status"], "TRAINING_NOT_AUTHORIZED")
        self.assertEqual(r["C"]["new_weight_updates"], 0)
        self.assertEqual(r["total_model_calls"], 10)
        self.assertEqual(len(r["A"]), len(r["B"]))
        self.assertTrue(all(x["memory_used"] for x in r["B"]))
        self.assertFalse(any(x["memory_used"] for x in r["A"]))
        # Sealed evaluation file was not loaded by pilot.run; model saw only
        # public prompts and separately verified training development feedback.
        for tag, prompt in fake.prompts:
            self.assertNotIn('"hidden_cases"', prompt)
            self.assertNotIn('"holdout"', prompt)
        scored = score.score_report(r)
        self.assertEqual(scored["A"]["tests_exact"], 2)  # Two sealed cases correctly return []
        self.assertEqual(scored["B"]["tests_exact"], 15)
        self.assertEqual(scored["B"]["fully_correct"], 3)
        self.assertEqual(scored["status"], "EXPLORATORY_MEMORY_GAIN_NOT_GENERALIZATION")
        self.assertFalse(scored["causal_autonomous_learning_proven"])

    def test_failed_repair_does_not_create_memory(self):
        r = pilot.run(FakeModel(successful_repair=False))
        self.assertFalse(r["learning"]["admitted_memory"])
        self.assertFalse(r["learning"]["improvement_on_practice"])
        self.assertFalse(any(row["memory_used"] for row in r["B"]))
        scored = score.score_report(r)
        self.assertEqual(scored["delta_exact_tests_B_minus_A"], 0)
        self.assertEqual(scored["status"], "NO_POSITIVE_TRANSFER_DEMONSTRATED")

    def test_illicit_code_is_blocked(self):
        for src in ["def transform(s):\n    return open('private')\n",
                    "import os\ndef transform(s):\n    return []",
                    "def transform(s):\n    return eval(s)"]:
            raw = json.dumps({"code": src})
            self.assertIsNone(pilot.inspect_code(raw)[0])

    def test_guard_cannot_be_promoted_by_fake_report(self):
        r = pilot.run(FakeModel())
        bad = copy.deepcopy(r)
        bad["C"]["status"] = "TRAINED"
        with self.assertRaisesRegex(ValueError, "ILLEGAL_AUTOMATIC_TRAINING"):
            score.score_report(bad)

    def test_hash_and_unverified_memory_rejected(self):
        r = pilot.run(FakeModel())
        tampered = copy.deepcopy(r)
        tampered["A"][0]["raw"] = "modified"
        with self.assertRaisesRegex(ValueError, "MODEL_OUTPUT_TAMPERED"):
            score.score_report(tampered)
        false_memory = copy.deepcopy(r)
        false_memory["learning"]["improvement_on_practice"] = False
        with self.assertRaisesRegex(ValueError, "MEMORY_ADMITTED_WITHOUT_VERIFICATION"):
            score.score_report(false_memory)

    def test_no_gold_in_generation_script(self):
        src = (HERE / "pilot.py").read_text(encoding="utf-8")
        self.assertNotIn('load_frozen("EVAL_SEALED_FROZEN.json")', src)
        self.assertNotIn("from score import", src)
        self.assertNotIn("import score", src)


if __name__ == "__main__":
    unittest.main()
