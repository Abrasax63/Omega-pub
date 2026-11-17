import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import integration as m


class RegistryAndAblationTests(unittest.TestCase):
    def test_original_engine_remains_unchanged(self):
        self.assertEqual(m.git_blob(m.OLD_ENGINE.read_bytes()), m.OLD_ENGINE_BLOB)

    def test_four_historical_new_sources_load_without_id_rules(self):
        data = m.load_registry()
        self.assertEqual(len(data), 4)
        self.assertEqual(set(data), {
            "BR-ACC-01", "BR-DESC-01", "BR-OBS-CAP-03", "BR-AFFINE-TREE-CORE"})
        self.assertTrue(all(row["blob"] and row["lines"] for row in data.values()))

    def test_fifth_unrecognized_id_loads_with_no_engine_edit(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "new.md").write_text("Nouvelle source expérimentale.\n", encoding="utf-8")
            identifier = "UNSEEN-QUANTUM-TEST-IGNORE"
            manifest = root / "registry.json"
            manifest.write_text(json.dumps({
                "version": "omega-source-registry-v1",
                "sources": [{"source_id": identifier, "relative_path": "new.md",
                             "git_blob": m.git_blob((root / "new.md").read_bytes())}],
            }), encoding="utf-8")
            registry = m.load_registry(manifest, root, pinned_blob=None)
            self.assertEqual(list(registry), [identifier])
            self.assertIn("expérimentale", registry[identifier]["text"])

    def test_changed_source_fails_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            file = root / "source.md"
            file.write_text("version un", encoding="utf-8")
            manifest = root / "registry.json"
            manifest.write_text(json.dumps({
                "version": "omega-source-registry-v1",
                "sources": [{"source_id": "ANY", "relative_path": "source.md",
                             "git_blob": m.git_blob(file.read_bytes())}],
            }), encoding="utf-8")
            file.write_text("version deux", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "source content"):
                m.load_registry(manifest, root, pinned_blob=None)

    def test_path_traversal_and_symlinks_fail_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            outside = root.parent / "not_allowed.md"
            for bad in ("../not_allowed.md", "/tmp/not_allowed.md", r"..\not_allowed.md"):
                manifest = root / "manifest.json"
                manifest.write_text(json.dumps({
                    "version": "omega-source-registry-v1",
                    "sources": [{"source_id": "ANY", "relative_path": bad,
                                 "git_blob": "0" * 40}],
                }), encoding="utf-8")
                with self.assertRaises(ValueError):
                    m.load_registry(manifest, root, pinned_blob=None)
            (root / "real.md").write_text("real", encoding="utf-8")
            (root / "alias.md").symlink_to(root / "real.md")
            manifest = root / "manifest.json"
            manifest.write_text(json.dumps({
                "version": "omega-source-registry-v1",
                "sources": [{"source_id": "ANY", "relative_path": "alias.md",
                             "git_blob": m.git_blob((root / "real.md").read_bytes())}],
            }), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "symlink"):
                m.load_registry(manifest, root, pinned_blob=None)

    def test_oracles_are_finite_and_balanced_on_frozen_cohort(self):
        cases = m.load_questions()
        values = [m.oracle(c) for c in cases]
        self.assertEqual(len(cases), 12)
        self.assertEqual(values.count("OUI"), 6)
        self.assertEqual(values.count("NON"), 6)
        self.assertEqual(m.oracle({"oracle_kind": "access", "word": "111",
                                   "access_test": "factor"}), "OUI")
        self.assertEqual(m.oracle({"oracle_kind": "access", "word": "111",
                                   "access_test": "start"}), "NON")
        self.assertEqual(m.oracle({"oracle_kind": "capacity",
                                   "multiplicities": [2, 2]}), "OUI")
        self.assertEqual(m.oracle({"oracle_kind": "capacity",
                                   "multiplicities": [2, 3]}), "NON")

    def test_prompt_does_not_include_oracle_fields(self):
        c = m.load_questions()[0]
        p = m.prompts(c["question"], m.load_registry()[c["source_id"]])
        self.assertNotIn("oracle_kind", p)
        self.assertNotIn("access_test", p)
        self.assertNotIn("multiplicities", p)
        self.assertIn("Git blob:", p)
        self.assertEqual(m.decode("noise\nREPONSE: OUI\n"), "OUI")
        self.assertEqual(m.decode("noise\nREPONSE: \n"), "ABSTENTION")
        self.assertEqual(m.decode("noise\nREPONSE: OUI NON\n"), "ABSTENTION")

    def test_predictions_frozen_before_any_oracle_call(self):
        invoked = []
        original = m.oracle
        def chooser(prompt, arm, case_id):
            invoked.append((case_id, arm, prompt))
            return {"verdict": "OUI", "called": True, "status": "MOCK"}
        def guarded(case):
            self.assertEqual(len(invoked), 24)
            return original(case)
        with patch.object(m, "oracle", side_effect=guarded):
            report = m.run(chooser)
        self.assertEqual(report["calls_attempted"], 24)
        self.assertEqual(report["metrics"]["solo"]["correct"], 6)
        self.assertEqual(report["metrics"]["memory"]["false_confident"], 6)
        self.assertEqual(report["metrics"]["memory_checked"]["false_confident"], 0)
        self.assertEqual(report["metrics"]["memory_checked"]["answered"], 6)
        self.assertTrue(report["h3_finite_oracle_safety_local"])
        self.assertFalse(report["h2_memory_gain_local"])
        self.assertFalse(report["input_token_parity_confirmed"])
        self.assertEqual(set(x[1] for x in invoked), {"solo", "memory"})
        self.assertNotIn("oracle_kind", "".join(x[2] for x in invoked))


if __name__ == "__main__":
    unittest.main()
