"""Synthetic comparison with shared evidence and an equal read budget."""
import unittest

from provenance_agent import learn, verdict
from provenance_selection import Piece, select_verdict


UNKNOWN = "indéterminé"


def record(operation, **changes):
    return {"job": "beta", "output": "a", "complete": True, "success": True,
            "operation": operation} | changes


class ProvenanceSelectionTests(unittest.TestCase):
    def test_comparison(self):
        # Same visible inventory for both policies. These are constructed
        # records, not raw GitHub journals or independently held-out cases.
        digest = Piece("digest", "digest", "beta", "a")
        first = Piece("step1", "execution", "beta", "a")
        second = Piece("step2", "execution", "beta", "a")
        cases = [
            ("calcul sans marqueur", [digest, first], {"step1": record("recalcul")}, UNKNOWN, "recalcul"),
            ("copie sans marqueur", [digest, first], {"step1": record("copie")}, UNKNOWN, "copie"),
            ("empreinte seule", [digest], {}, UNKNOWN, UNKNOWN),
            ("mauvais producteur", [first], {"step1": record("recalcul", job="alpha")}, UNKNOWN, UNKNOWN),
            ("journal partiel", [first], {"step1": record("recalcul", complete=False)}, UNKNOWN, UNKNOWN),
            ("traces contradictoires", [first, second], {"step1": record("recalcul"), "step2": record("copie")}, UNKNOWN, UNKNOWN),
            ("job en échec", [first], {"step1": record("recalcul", success=False)}, UNKNOWN, UNKNOWN),
            ("cas historique balisé", [digest, first], {"step1": record("copie", marker="COPIED a from originals")}, "copie", "copie"),
        ]
        program, _ = learn()
        for label, inventory, data, fixed_expected, expected in cases:
            with self.subTest(label=label):
                result = select_verdict(inventory, data.get, job="beta", output="a", budget=2)
                fixed_log = "\n".join(data.get(piece.name, {}).get("marker", "") for piece in inventory[:2])
                self.assertEqual(verdict(fixed_log, "a", program), fixed_expected)
                self.assertEqual(result["verdict"], expected)
                self.assertLessEqual(len(result["pieces_lues"]), 2)

    def test_abstains_when_budget_cannot_check_conflict(self):
        pieces = [Piece(str(i), "execution", "beta", "a") for i in range(3)]
        result = select_verdict(pieces, lambda _: record("recalcul"), job="beta", output="a", budget=2)
        self.assertEqual(result, {"verdict": UNKNOWN, "pieces_lues": ["0", "1"]})
