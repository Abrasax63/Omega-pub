import unittest

from provenance_lab import UNKNOWN, classify, evaluate, synthesize


def case(command, expected, *, complete=True, exit_code=0):
    return {
        "complete": complete,
        "output": "result.json",
        "writers": [{"command": command, "exit_code": exit_code, "output": "result.json"}],
        "expected": expected,
    }


class ProvenanceLabTests(unittest.TestCase):
    def test_candidate_reuse_and_review(self):
        candidate = synthesize([
            case("cp input.json result.json", "copie"),
            case("python -m square 11", "recalcul"),
        ])
        reserved = [
            case("cp other.json result.json", "copie"),
            case("python -m square 23", "recalcul"),
            case("cp other.json result.json", UNKNOWN, complete=False),
            case("python -m square 17", UNKNOWN, exit_code=1),
        ]
        self.assertTrue(evaluate(candidate, {}, reserved)["recommend_for_review"])
        self.assertEqual(classify(reserved[0], candidate), "copie")

    def test_rejects_bad_generalization(self):
        candidate = synthesize([case("python -m square 11", "recalcul")])
        held_out = [case("python -m republish result.json", "copie")]
        result = evaluate(candidate, {}, held_out)
        self.assertEqual(result["candidate"]["false_confirmations"], 1)
        self.assertFalse(result["recommend_for_review"])
