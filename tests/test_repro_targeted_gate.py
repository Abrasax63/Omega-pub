import copy
import tempfile
import unittest
from pathlib import Path
from tools.repro_targeted_gate import eligible_for_reuse, snapshot


class TargetedGateTests(unittest.TestCase):
    def test_unchanged_reviewed_only(self):
        script = Path(__file__).resolve().parents[1] / "02_MATHEMATIQUES/observabilite_temporelle/sources/verification_specialisation_unaire.py"
        state = snapshot(script)
        self.assertTrue(eligible_for_reuse(state, snapshot(script), True))
        self.assertFalse(eligible_for_reuse(state, state, False))
        changed = copy.deepcopy(state)
        changed["sympy"] = "changed-version"
        self.assertFalse(eligible_for_reuse(state, changed, True))
        changed = copy.deepcopy(state)
        changed["mpmath"] = "changed-version"
        self.assertFalse(eligible_for_reuse(state, changed, True))

    def test_source_change_invalidates(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "script.py"
            p.write_text("print(1)")
            before = snapshot(p)
            p.write_text("print(2)")
            self.assertFalse(eligible_for_reuse(before, snapshot(p), True))


if __name__ == "__main__":
    unittest.main()
