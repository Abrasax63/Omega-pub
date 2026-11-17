import json
import tempfile
import unittest
from pathlib import Path

from pilot import (
    GOLD_PATH, ROOT, SOURCES, evaluate, git_blob, lexical_candidates,
    load_cards, read_source, rce_score, rce_terms, typed_dependencies,
)


class SemanticDependencyPilotTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cards = load_cards(ROOT)
        cls.gold = json.loads(GOLD_PATH.read_text(encoding="utf-8"))

    def test_frozen_sources_and_fourteen_unique_cases(self):
        self.assertEqual(len(self.gold["cases"]), 14)
        self.assertEqual(len({case["id"] for case in self.gold["cases"]}), 14)
        self.assertTrue({case["id"] for case in self.gold["cases"]} <= self.cards.keys())
        self.assertTrue(all(item["source_blob"] for item in self.cards.values()))

    def test_declared_dependencies_have_source_lines_and_not_certified(self):
        card = self.cards["BR-AFFINE-TREE-CORE"]
        edges = typed_dependencies(card)
        self.assertEqual({e["target"] for e in edges},
                         {"BR-AFFINE-TREE-GLUE", "BR-AFFINE-GROUP-CORE"})
        for edge in edges:
            self.assertEqual(edge["relation"], "declared_dependency_unverified")
            self.assertGreater(edge["line"], card["heading_line"])
            self.assertIn(edge["source_file"], SOURCES)

    def test_conceptual_relations_do_not_become_dependencies(self):
        for identifier in ("BR-DESC-01", "BR-DESC-02"):
            self.assertEqual(typed_dependencies(self.cards[identifier]), [])

    def test_negative_without_declared_dependency(self):
        for identifier in ("BR-AFFINE-TREE-GLUE", "BR-R90-01",
                           "BR-ACC-01", "BR-AFFINE-GROUP-CORE"):
            self.assertEqual(typed_dependencies(self.cards[identifier]), [])

    def test_lexical_returns_candidates_not_edge_certificates(self):
        proposed = lexical_candidates(self.cards, "BR-AFFINE-TREE-CORE")
        self.assertLessEqual(len(proposed), 3)
        self.assertNotIn("BR-AFFINE-TREE-CORE", proposed)
        self.assertEqual(len(proposed), len(set(proposed)))
        self.assertGreater(rce_score(rce_terms("noyau"), "noyau", "x.md"), 0)

    def test_tampered_blob_rejected(self):
        rel, blob = next(iter(SOURCES.items()))
        with tempfile.TemporaryDirectory() as tmp:
            file = Path(tmp) / rel
            file.parent.mkdir(parents=True)
            file.write_text("tampered", encoding="utf-8")
            self.assertNotEqual(git_blob(b"tampered"), blob)
            with self.assertRaisesRegex(ValueError, "blob changed"):
                read_source(Path(tmp), rel, blob)

    def test_deterministic_and_no_repo_write(self):
        marker = ROOT / "09_INFRASTRUCTURE_AGENTIQUE/semantic_dependency/GOLD_2026-11-17.json"
        before = marker.read_bytes()
        first = evaluate(ROOT)
        second = evaluate(ROOT)
        self.assertEqual(first, second)
        self.assertEqual(marker.read_bytes(), before)
        self.assertIn("metrics", first)
        self.assertEqual(first["status"], "EXPLORATORY_NONBLIND_SECONDARY_ANNOTATIONS")


if __name__ == "__main__":
    unittest.main()
