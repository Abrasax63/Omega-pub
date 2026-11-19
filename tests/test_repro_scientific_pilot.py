import copy
import tempfile
import unittest
from pathlib import Path
from tools.repro_scientific_pilot import run_pinned_script
from tools.repro_history_pilot import find_reusable


class ScientificPilotTests(unittest.TestCase):
    def test_real_omega_script_twice_and_invalidation(self):
        root = Path(__file__).resolve().parents[1]
        script = "02_MATHEMATIQUES/observabilite_temporelle/sources/verification_specialisation_unaire.py"
        with tempfile.TemporaryDirectory() as d:
            first, manifest, result = run_pinned_script(root, script, d)
            self.assertEqual(result["returncode"], 0, result["stderr"])
            self.assertTrue(result["stdout"].strip())
            second, same, again = run_pinned_script(root, script, d)
            self.assertEqual(again["returncode"], 0, again["stderr"])
            self.assertEqual(manifest, same)
            self.assertNotEqual(first, second)
            self.assertEqual(len(list(Path(d).glob("*.json"))), 2)
            self.assertIsNone(find_reusable(d, manifest))
            changed = copy.deepcopy(manifest)
            changed["dependencies"]["sympy"] = "simulated-new-version"
            self.assertIsNone(find_reusable(d, changed))
            self.assertTrue(first.exists() and second.exists())


if __name__ == "__main__":
    unittest.main()
