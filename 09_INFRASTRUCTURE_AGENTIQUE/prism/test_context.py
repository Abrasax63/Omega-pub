import sys
import tempfile
import unittest
from pathlib import Path

from planner import plan_mission
from context import ContextPreparationError, prepare_contexts


class PrismContextTests(unittest.TestCase):
    def make_repo(self, root):
        gov = root / "00_GOUVERNANCE"
        gov.mkdir()
        (gov / "INDEX_GLOBAL.md").write_text(
            "| ID | Domaine | Énoncé / titre | Version | Statut scientifique source | Statut de publication | Fiche |\n"
            "|---|---|---|---|---|---|---|\n"
            "| BR-01 | Mathématiques | Noyau et période | 0.1 | DÉMONTRÉ (fiche interne) | EXPÉRIMENTAL | [Fiche](../fiche.md) |\n",
            encoding="utf-8")
        (gov / "REGISTRE_TRANSVERSAL.md").write_text(
            "| Identifiants / dossier | Domaine | État documentaire | Condition avant inscription comme fiche |\n"
            "|---|---|---|---|\n"
            "| CL-DYN-01 | Mathématiques | Sources à retrouver | Auditer les preuves |\n",
            encoding="utf-8")
        (root / "fiche.md").write_text("# BR-01\nPreuve à auditer sur le noyau et la période.\n", encoding="utf-8")

    def test_one_context_package_per_planned_role(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.make_repo(root)
            plan = plan_mission({"question": "noyau période", "mission_type": "mathematical"})
            bundle = prepare_contexts(root, plan)
            self.assertEqual([p["role"] for p in bundle["packages"]], ["refuter", "formalist"])
            self.assertEqual(bundle["manifest"]["search_calls"], 2)
            self.assertEqual(bundle["execution_model"]["role_tasks_executed"], 0)

    def test_exact_retrieval_preserves_registered_and_pending_types(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.make_repo(root)
            plan = plan_mission({
                "question": "noyau période",
                "mission_type": "mathematical",
                "known_ids": ["BR-01", "CL-DYN-01"],
            })
            bundle = prepare_contexts(root, plan)
            self.assertEqual(bundle["mission"]["known_ids"], ["BR-01", "CL-DYN-01"])
            for package in bundle["packages"]:
                records = {x["requested_id"]: x["retrieval"] for x in package["exact_retrievals"]}
                self.assertEqual(records["BR-01"]["record_type"], "registered_index_entry")
                self.assertEqual(records["CL-DYN-01"]["record_type"], "pending_migration")
                self.assertEqual(records["BR-01"]["scientific_validation"], "not_performed")

    def test_missing_exact_id_is_reported_not_substituted(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.make_repo(root)
            plan = plan_mission({
                "question": "noyau période",
                "mission_type": "mathematical",
                "known_ids": ["MISSING-999"],
            })
            bundle = prepare_contexts(root, plan)
            retrieval = bundle["packages"][0]["exact_retrievals"][0]["retrieval"]
            self.assertFalse(retrieval["found"])
            self.assertEqual(retrieval["id"], "MISSING-999")

    def test_each_role_gets_its_own_role_specific_search(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.make_repo(root)
            plan = plan_mission({"question": "noyau période", "mission_type": "general"})
            bundle = prepare_contexts(root, plan)
            self.assertEqual(len({p["search_context"]["mission"]["role"] for p in bundle["packages"]}), 2)
            self.assertTrue(all(p["execution_status"] == "not_executed" for p in bundle["packages"]))

    def test_invalid_known_ids_are_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.make_repo(root)
            plan = plan_mission({"question": "noyau période", "mission_type": "mathematical"})
            plan["mission"]["known_ids"] = ["../secret"]
            with self.assertRaises(ContextPreparationError):
                prepare_contexts(root, plan)

    def test_duplicate_roles_are_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.make_repo(root)
            plan = plan_mission({"question": "noyau période", "mission_type": "mathematical"})
            plan["tasks"].append(dict(plan["tasks"][0]))
            with self.assertRaises(ContextPreparationError):
                prepare_contexts(root, plan)

    def test_context_hash_is_present_and_bundle_is_read_only(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.make_repo(root)
            before = sorted(str(p.relative_to(root)) for p in root.rglob("*"))
            plan = plan_mission({"question": "noyau période", "mission_type": "mathematical"})
            bundle = prepare_contexts(root, plan)
            after = sorted(str(p.relative_to(root)) for p in root.rglob("*"))
            self.assertEqual(before, after)
            self.assertEqual(len(bundle["manifest"]["content_hash"]), 64)
            self.assertEqual(bundle["mode"], "read_only_local_checkout")


if __name__ == "__main__":
    unittest.main()
