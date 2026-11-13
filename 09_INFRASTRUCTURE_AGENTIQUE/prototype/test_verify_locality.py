from pathlib import Path
import shutil
from tempfile import TemporaryDirectory
import unittest

from verify_locality import CASE, COMMIT, SOURCE, audit


class LocalityAuditTests(unittest.TestCase):
    question = "Quel calcul soutient les 325 468 comparaisons ?"

    def setUp(self):
        directory = TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.root = Path(directory.name)
        checkout = Path(__file__).resolve().parents[2]
        shutil.copytree(checkout / CASE, self.root / CASE)

    def change(self, name, old, new):
        path = self.root / CASE / name
        original = path.read_text(encoding="utf-8")
        self.assertIn(old, original)
        path.write_text(original.replace(old, new), encoding="utf-8")

    def test_retrieves_and_verifies_reference(self):
        result = audit(self.root, self.question)
        self.assertEqual(result["statut"], "raccordé")
        self.assertEqual(result["source_rce"], SOURCE)
        self.assertEqual(result["comparaisons"], 325468)
        self.assertEqual(result["portee"], {"etats_max": 6, "L": [2, 3]})
        self.assertFalse(result["rejeu_local"])

    def test_wrong_run(self):
        self.change("SOURCE.md", "42788979270", "42788979271")
        self.assertEqual(audit(self.root, self.question)["statut"], "indéterminé")

    def test_wrong_checkout(self):
        self.change("run.log", COMMIT, "1" * 40)
        self.assertEqual(audit(self.root, self.question)["statut"], "indéterminé")

    def test_changed_script(self):
        path = self.root / CASE / "check.py"
        path.write_bytes(path.read_bytes() + b"\n")
        self.assertEqual(audit(self.root, self.question, replay=True)["statut"], "indéterminé")

    def test_unrelated_query(self):
        self.assertEqual(audit(self.root, "Quelle est la capitale du Japon ?")["statut"], "indéterminé")


if __name__ == "__main__":
    unittest.main()
