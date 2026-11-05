import tempfile
import unittest
from pathlib import Path

from rce import build_context, load_pending_items, load_registered_results, markdown_tables


class MarkdownParsingTests(unittest.TestCase):
    def test_pipe_table(self):
        source = "| ID | Domaine |\n|---|---|\n| BR-01 | Mathématiques |\n"
        tables = list(markdown_tables(source))
        self.assertEqual(tables[0][1][0]["ID"], "BR-01")

    def test_registered_results_preserve_publication_status(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "00_GOUVERNANCE").mkdir()
            (root / "00_GOUVERNANCE/INDEX_GLOBAL.md").write_text(
                "| ID | Domaine | Énoncé / titre | Version | Statut scientifique source | Statut de publication | Fiche |\n"
                "|---|---|---|---|---|---|---|\n"
                "| BR-01 | Mathématiques | Noyau et période | 0.1 | DÉMONTRÉ (fiche interne) | EXPÉRIMENTAL | [Fiche](../02_MATHEMATIQUES/BR-01.md) |\n",
                encoding="utf-8")
            records = load_registered_results(root)
            self.assertEqual(len(records), 1)
            self.assertEqual(records[0]["scientific_status_source"], "DÉMONTRÉ (fiche interne)")
            self.assertEqual(records[0]["publication_status"], "EXPÉRIMENTAL")
            self.assertEqual(records[0]["epistemic_space"], "experimental_internal")

    def test_pending_items_are_separate(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "00_GOUVERNANCE").mkdir()
            (root / "00_GOUVERNANCE/REGISTRE_TRANSVERSAL.md").write_text(
                "## Éléments en attente de migration — non comptés comme fiches publiques\n\n"
                "| Identifiants / dossier | Domaine | État documentaire | Condition avant inscription comme fiche |\n"
                "|---|---|---|---|\n"
                "| CL-DYN-01 à CL-DYN-04 | Mathématiques | Sources à retrouver | Auditer les preuves |\n\n"
                "## Règle de mise à jour\n",
                encoding="utf-8")
            pending = load_pending_items(root)
            self.assertEqual(len(pending), 1)
            self.assertIn("CL-DYN", pending[0]["id"])
            self.assertIn("NON ÉTABLI", pending[0]["scientific_status_source"])

    def test_context_is_read_only_and_has_role_guidance(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            gov = root / "00_GOUVERNANCE"
            gov.mkdir()
            (gov / "INDEX_GLOBAL.md").write_text(
                "| ID | Domaine | Énoncé / titre | Version | Statut scientifique source | Statut de publication | Fiche |\n"
                "|---|---|---|---|---|---|---|\n"
                "| BR-01 | Mathématiques | Noyau période | 0.1 | DÉMONTRÉ | EXPÉRIMENTAL | [Fiche](../fiche.md) |\n",
                encoding="utf-8")
            (gov / "REGISTRE_TRANSVERSAL.md").write_text("", encoding="utf-8")
            (root / "fiche.md").write_text("# Noyau et période\nContre-exemple absent.\n", encoding="utf-8")
            before = (gov / "INDEX_GLOBAL.md").read_bytes()
            context = build_context(root, "noyau période", "refuter")
            after = (gov / "INDEX_GLOBAL.md").read_bytes()
            self.assertEqual(before, after)
            self.assertEqual(context["mission"]["role"], "refuter")
            self.assertIn("contre-exemples", context["mission"]["role_guidance"])
            self.assertEqual(context["manifest"]["mode"], "read_only_local_checkout")
            self.assertTrue(context["manifest"]["content_hash"])


if __name__ == "__main__":
    unittest.main()
