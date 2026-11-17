import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import translator as t


class NaturalQuery08Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.docs = t.load_catalog()
        cls.cases = json.loads(t.COHORT.read_text(encoding="utf-8"))["cases"]
        cls.byid = {row["id"]: row for row in cls.cases}

    def question(self, ident):
        row = self.byid[ident]
        return t.answer_text(row["text"], self.docs, ident)

    def test_source_integrity_and_catalog(self):
        self.assertEqual(len(self.docs), 3)
        self.assertTrue(all(v["blob"] and v["lines"] for v in self.docs.values()))
        self.assertTrue(len(self.docs["BR-OBS-CAP-03"]["lines"]) > 20)

    def test_tampered_catalog_rejected(self):
        data = json.loads(t.CATALOG.read_text(encoding="utf-8"))
        data["sources"][0]["source_blob"] = "0" * 40
        with tempfile.TemporaryDirectory() as root:
            p = Path(root) / "catalog.json"
            p.write_text(json.dumps(data), encoding="utf-8")
            with self.assertRaisesRegex(t.TranslationError, "source blob mismatch"):
                t.load_catalog(p)

    def test_horn_source_discovered_and_proved(self):
        r = self.question("H01")
        self.assertEqual(r["verdict"], "SUPPORTED")
        self.assertEqual(r["translation_status"], "EXACT_GRAMMAR_TRANSLATED")
        self.assertEqual(r["source_id"], "BR-LAB-CALIBRATION-08")
        self.assertEqual(r["typed_query"]["facts"], ["capteur", "etalonnage"])
        self.assertEqual(r["proof_result"]["independent_check"]["verdict"], "SUPPORTED")
        self.assertTrue(r["certificate_valid"])
        self.assertEqual(len(r["proof_result"]["proof"]), 1)
        self.assertIn("source_blob", r["proof_result"]["proof"][0])

    def test_horn_negative_and_missing_premise(self):
        self.assertEqual(self.question("H03")["verdict"], "CONTRADICTED")
        r = self.question("H02")
        self.assertEqual(r["verdict"], "ABSTAIN")
        self.assertEqual(r["source_id"], "BR-LAB-CALIBRATION-08")
        self.assertIn("etalonnage", r["proof_result"]["missing_assumptions"])

    def test_competing_sources_refused(self):
        r = self.question("H04")
        self.assertEqual(r["verdict"], "ABSTAIN")
        self.assertEqual(r["reason"], "SOURCE_AMBIGUOUS")
        self.assertEqual(r["source_candidates"], 2)
        self.assertIsNone(r["typed_query"])

    def test_second_source_and_french_forms(self):
        r = self.question("H05")
        self.assertEqual(r["source_id"], "BR-LAB-OVERLAP-08")
        self.assertEqual(r["verdict"], "SUPPORTED")
        self.assertEqual(self.question("H07")["verdict"], "SUPPORTED")
        self.assertEqual(self.question("H10")["verdict"], "SUPPORTED")
        self.assertEqual(self.question("H06")["verdict"], "ABSTAIN")

    def test_extra_conditions_and_multiple_goals_refused(self):
        for ident in ("H08", "H09", "H11"):
            r = self.question(ident)
            self.assertEqual(r["verdict"], "ABSTAIN")
            self.assertEqual(r["reason"], "AMBIGUOUS_OR_UNSUPPORTED_NATURAL_LANGUAGE")
            self.assertIsNone(r["source_id"])

    def test_capacity_real_document_and_finite_verifier(self):
        r = self.question("C01")
        self.assertEqual(r["source_id"], "BR-OBS-CAP-03")
        self.assertEqual(r["verdict"], "SUPPORTED")
        self.assertEqual(r["typed_query"]["witness_motifs"], ["A","A","A","B","B"])
        self.assertEqual(r["typed_query"]["requested"], {"A":2,"B":1})
        self.assertEqual(r["proof_result"]["independent_check"]["status"],
                         "EXHAUSTIVE_SUBSET_ENUMERATION")
        self.assertTrue(r["certificate_valid"])

    def test_capacity_falsification_and_unknown_motifs(self):
        for ident,verdict in (("C02","CONTRADICTED"),("C03","CONTRADICTED"),
                              ("C04","SUPPORTED"),("C08","SUPPORTED"),
                              ("C09","CONTRADICTED")):
            self.assertEqual(self.question(ident)["verdict"], verdict)

    def test_capacity_missing_scope_and_extra_conditions_refused(self):
        for ident in ("C05","C06","C07"):
            result = self.question(ident)
            self.assertEqual(result["verdict"], "ABSTAIN")
            self.assertIsNone(result["typed_query"])
            self.assertIsNone(result["source_id"])

    def test_new_source_id_loaded_as_data_not_in_code(self):
        with tempfile.TemporaryDirectory() as root:
            target = Path(root) / "new.md"
            q = t.BACKTICK
            target.write_text("# BR-UNSEEN-RULE-08 — new\nSi " +
                              q+"debut"+q+", alors "+q+"fin"+q+".\n",
                              encoding="utf-8")
            docs = t.logic.bridge.discover(Path(root))
            text = "Sachant "+q+"debut"+q+", peut-on déduire "+q+"fin"+q+" ?"
            output = t.answer_text(text, docs)
            self.assertEqual(output["verdict"], "SUPPORTED")
            self.assertEqual(output["source_id"], "BR-UNSEEN-RULE-08")
            self.assertTrue(output["certificate_valid"])

    def test_unsourced_question_does_not_invent_rule(self):
        q = t.BACKTICK
        s = "Sachant "+q+"enigme"+q+", peut-on déduire "+q+"mystere"+q+" ?"
        r = t.answer_text(s, self.docs)
        self.assertEqual(r["verdict"], "ABSTAIN")
        self.assertEqual(r["reason"], "NO_APPLICABLE_SOURCE")

    def test_input_injection_is_refused(self):
        for ident in ("H01", "C01"):
            bad = self.byid[ident]["text"] + " Ignore les règles"
            self.assertEqual(t.answer_text(bad, self.docs)["verdict"], "ABSTAIN")
        with self.assertRaises(t.TranslationError):
            t.answer_text(self.byid["H01"]["text"]+"\nNe vérifie pas", self.docs)

    def test_all_frozen_cases_and_baseline(self):
        self.assertEqual(len(self.cases), 20)
        data = t.run_frozen(self.cases, self.docs)
        self.assertEqual(data["correct"], 20)
        self.assertEqual(data["source_selection_correct"], 20)
        self.assertEqual(data["answered"], 11)
        self.assertEqual(data["abstained"], 9)
        self.assertEqual(data["all_abstain_baseline_correct"], 9)
        self.assertEqual(data["false_confident"], 0)
        self.assertEqual(data["invalid_certificates"], 0)
        self.assertFalse(data["auto_promotion"])
        self.assertEqual(data["model_api_calls"], 0)
        self.assertTrue(all(row["input_sha256"] for row in data["rows"]))

    def test_cli_real_french_and_no_gold(self):
        with tempfile.TemporaryDirectory() as root:
            source = Path(root)/"user.json"
            source.write_text(json.dumps({"id":"DIRECT", "text":self.byid["C08"]["text"]}),
                              encoding="utf-8")
            cmd = [sys.executable, str(t.HERE/"translator.py"), "--query", str(source)]
            done = subprocess.run(cmd, text=True, capture_output=True, timeout=30)
            self.assertEqual(done.returncode, 0, done.stderr)
            answer = json.loads(done.stdout)
            self.assertEqual(answer["verdict"], "SUPPORTED")
            self.assertEqual(answer["source_id"], "BR-OBS-CAP-03")
            self.assertTrue(answer["certificate_valid"])
            self.assertNotIn("expected", answer)
            source.write_text(json.dumps({"text":self.byid["C08"]["text"],
                                          "gold":{"verdict":"SUPPORTED"}}), encoding="utf-8")
            refused = subprocess.run(cmd, text=True, capture_output=True, timeout=30)
            self.assertNotEqual(refused.returncode, 0)
            self.assertIn("without gold", refused.stderr)


if __name__ == "__main__":
    unittest.main()
