import json
import subprocess
import sys
import tempfile
import unittest
from collections import Counter
from pathlib import Path
from unittest.mock import patch

import evaluate_external as e


class ExternalFolioHoldoutTests(unittest.TestCase):

    def test_sample_pinned_and_exact_30_external_rows(self):
        rows = e.load_frozen()
        self.assertEqual(len(rows), 30)
        self.assertEqual(Counter(row["label"] for row in rows),
                         Counter({"Uncertain":13,"True":11,"False":6}))
        self.assertEqual(len({e.stable_hash(row["premises"]) for row in rows}), 10)

    def test_sample_source_and_parent_translator_immutable(self):
        self.assertEqual(e.blob_sha(e.INPUT.read_bytes()), e.FOLIO_SAMPLE_BLOB)
        self.assertEqual(e.blob_sha(e.ORIGINAL_TRANSLATOR.read_bytes()),
                         e.ORIGINAL_TRANSLATOR_BLOB)
        self.assertEqual(e.FOLIO_SOURCE_BLOB,
                         "06244bd10b37eac73cba7aca6c336e96011ace58")

    def test_modified_corpus_is_rejected_before_scoring(self):
        with tempfile.TemporaryDirectory() as tmp:
            changed = Path(tmp) / "altered.jsonl"
            changed.write_bytes(e.INPUT.read_bytes() + b"\n")
            with patch.object(e, "INPUT", changed):
                with self.assertRaisesRegex(e.AuditError, "sample modified"):
                    e.load_frozen()

    def test_transport_is_exact_and_only_premise_text(self):
        rows=e.load_frozen()
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            info=e.prepare_document(root,1,rows[0])
            docs=e.translator.logic.discover((root,))
            self.assertEqual(list(docs), [info["id"]])
            self.assertEqual(docs[info["id"]]["lines"][1:],rows[0]["premises"])
            self.assertTrue(info["source_blob"])
            self.assertNotIn(rows[0]["label"], docs[info["id"]]["lines"][0])
            self.assertNotIn(rows[0]["conclusion-FOL"], docs[info["id"]]["lines"][0])

    def test_gold_is_never_supplied_to_frozen_translator(self):
        received=[]
        def fake_translator(text, documents, case_id):
            self.assertTrue(text)
            self.assertIsInstance(documents,dict)
            self.assertEqual(len(documents),1)
            self.assertTrue(case_id.startswith("FOLIO-"))
            record={"text":text,"id":case_id,
                    "lines":next(iter(documents.values()))["lines"][1:]}
            received.append(record)
            return {"id":case_id,"verdict":"ABSTAIN",
                    "translation_status":"MOCK_ABSTAIN",
                    "reason":"MOCK",
                    "typed_query":None,
                    "source_id":None,"certificate_valid":True}
        with patch.object(e.translator,"answer_text",side_effect=fake_translator):
            report=e.run_external()
        self.assertEqual(len(received),30)
        source=e.load_frozen()
        for pos,call in enumerate(received):
            self.assertEqual(call["text"],source[pos]["conclusion"])
            self.assertEqual(call["lines"],source[pos]["premises"])
        self.assertEqual(report["answered"],0)
        self.assertEqual(report["correct"],13)
        self.assertEqual(report["baseline_always_abstain_correct"],13)
        self.assertEqual(report["false_confident"],0)
        self.assertEqual(report["status"],"TRANSFER_NOT_DEMONSTRATED")

    def test_real_pipeline_reports_first_boundary_without_inference_claim(self):
        source=e.load_frozen()[0]
        with tempfile.TemporaryDirectory() as tmp:
            info=e.prepare_document(Path(tmp),1,source)
            docs=e.translator.logic.discover((Path(tmp),))
            out=e.translator.answer_text(source["conclusion"], docs, "FOLIO-001")
        self.assertEqual(out["verdict"],"ABSTAIN")
        self.assertIsNone(out["typed_query"])
        self.assertEqual(out["source_documents_scanned"],1)
        self.assertEqual(out["reason"],"AMBIGUOUS_OR_UNSUPPORTED_NATURAL_LANGUAGE")
        self.assertEqual(info["id"],"BR-EXT-FOLIO-001")

    def test_report_does_not_misrepresent_correct_abstention_as_reasoning(self):
        report=e.run_external()
        self.assertEqual(report["cases"],30)
        self.assertEqual(report["source_documents_loaded"],30)
        self.assertEqual(report["distinct_theory_groups"],10)
        self.assertEqual(report["baseline_always_abstain_correct"],13)
        self.assertEqual(report["answered"]+report["abstained"],30)
        self.assertEqual(report["false_confident"],0)
        self.assertEqual(report["invalid_certificates"],0)
        self.assertEqual(report["correct_non_abstain"],0)
        self.assertEqual(report["status"],"TRANSFER_NOT_DEMONSTRATED")
        self.assertTrue(report["predictions_sha256_before_gold"])
        self.assertTrue(report["input_gold_hidden_until_prediction_hash"])
        self.assertFalse(report["auto_promotion"])

    def test_full_cli_produces_inspectable_json(self):
        with tempfile.TemporaryDirectory() as tmp:
            out=Path(tmp)/"folio09-report.json"
            proc=subprocess.run([sys.executable,str(e.HERE/"evaluate_external.py"),
                                 "--output",str(out)],
                                text=True,capture_output=True,timeout=45)
            self.assertEqual(proc.returncode,0,proc.stderr)
            report=json.loads(out.read_text(encoding="utf-8"))
            self.assertEqual(report["cases"],30)
            self.assertTrue(proc.stdout.startswith("PREDICTIONS_BEFORE_GOLD_SHA256="))
            self.assertEqual(report["source"]["sample_blob"],e.FOLIO_SAMPLE_BLOB)

    def test_no_in_repo_output(self):
        command=[sys.executable,str(e.HERE/"evaluate_external.py"),
                 "--output",str(e.HERE/"forbidden-report.json")]
        proc=subprocess.run(command,text=True,capture_output=True,timeout=45)
        self.assertNotEqual(proc.returncode,0)
        self.assertIn("outside repository",proc.stderr)
        self.assertFalse((e.HERE/"forbidden-report.json").exists())


if __name__=="__main__":
    unittest.main()
