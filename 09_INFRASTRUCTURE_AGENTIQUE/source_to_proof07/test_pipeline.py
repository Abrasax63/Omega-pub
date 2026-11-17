import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import pipeline as p

REAL_ID="BR-OBS-CAP-03"
HORN_ID="BR-LAB-RULES-07"


class SourceToProof07Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.documents=p.discover()
        cls.cases=json.loads((p.HERE/"CASES_FROZEN.json").read_text(encoding="utf-8"))["cases"]

    def test_real_historical_formula_found_with_all_prerequisites(self):
        doc=self.documents[REAL_ID]
        anchors=p.extract_bound(doc)
        self.assertEqual(len(anchors),3)
        self.assertTrue(all(x["source_blob"]==doc["blob"] for x in anchors))
        self.assertTrue(any(p.BOUND in x["excerpt"] for x in anchors))

    def test_extraction_is_from_markdown_not_a_rule_manifest(self):
        doc=self.documents[HORN_ID]
        rules=p.extract_horn(doc)
        self.assertEqual(len(rules),4)
        self.assertTrue(all(r["line"]>0 and r["source_blob"]==doc["blob"] for r in rules))
        self.assertEqual({r["conclusion"] for r in rules},
                         {"candidate","claim","ready","not:safe"})
        self.assertTrue(all(r["interpretation_status"]==
                            "AUTO_PATTERN_CANDIDATE_UNVERIFIED" for r in rules))

    def test_chain_of_two_rules_has_checkable_cited_proof(self):
        q=self.cases[0]
        r=p.answer(q,self.documents)
        self.assertEqual(r["verdict"],"SUPPORTED")
        self.assertEqual(len(r["proof"]),2)
        self.assertTrue(r["certificate_valid"])
        self.assertEqual(r["independent_check"]["verdict"],"SUPPORTED")
        self.assertEqual([s["conclusion"] for s in r["proof"]],["candidate","claim"])
        for step in r["proof"]:
            self.assertEqual(self.documents[HORN_ID]["lines"][step["line"]-1].strip(),
                             step["excerpt"])

    def test_missing_premise_abstains_but_not_negates(self):
        r=p.answer(self.cases[1],self.documents)
        self.assertEqual(r["verdict"],"ABSTAIN")
        self.assertEqual(r["independent_check"]["verdict"],"ABSTAIN")
        self.assertIn("assumptions",r["missing_assumptions"])

    def test_explicit_negative_consequence_not_closed_world(self):
        r=p.answer(self.cases[3],self.documents)
        self.assertEqual(r["verdict"],"CONTRADICTED")
        self.assertEqual(r["proof"][-1]["conclusion"],"not:safe")
        self.assertEqual(r["independent_check"]["verdict"],"CONTRADICTED")

    def test_instance_capacity_matches_independent_subset_enumeration(self):
        yes=p.answer(self.cases[6],self.documents)
        no=p.answer(self.cases[7],self.documents)
        self.assertEqual(yes["verdict"],"SUPPORTED")
        self.assertEqual(no["verdict"],"CONTRADICTED")
        self.assertTrue(yes["certificate_valid"] and no["certificate_valid"])
        self.assertTrue(yes["independent_check"]["feasible"])
        self.assertFalse(no["independent_check"]["feasible"])
        self.assertEqual(yes["proof"]["counts"],{"A":3,"B":2})

    def test_undeclared_independence_or_extra_constraints_abstain(self):
        self.assertEqual(p.answer(self.cases[10],self.documents)["verdict"],"ABSTAIN")
        self.assertEqual(p.answer(self.cases[11],self.documents)["verdict"],"ABSTAIN")

    def test_tampered_source_blob_rejected(self):
        bad=dict(self.cases[0],expected_source_blob="f"*40)
        with self.assertRaisesRegex(p.ContractError,"unpinned"):
            p.answer(bad,self.documents)

    def test_forged_proof_fails_independent_replay(self):
        doc=self.documents[HORN_ID]
        q=self.cases[0]
        rules=p.extract_horn(doc)
        by={doc["id"]:rules}
        basic={"source_id":doc["id"],"facts":q["facts"],"goal":q["goal"]}
        a=p.bridge.assess(basic,self.documents,by)
        self.assertTrue(p.bridge.check_proof(basic,a,self.documents,by))
        forged=json.loads(json.dumps(a))
        forged["proof"][-1]["excerpt"]="invented source citation"
        self.assertFalse(p.bridge.check_proof(basic,forged,self.documents,by))

    def test_unseen_document_rule_chain_without_id_dispatch(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            doc=root/"new.md"
            doc.write_text("# BR-NEW-RULE-007 — Unseen\n"
                           "Si "+p.TICK+"alpha"+p.TICK+", alors "+p.TICK+"beta"+p.TICK+".\n"
                           "Si "+p.TICK+"beta"+p.TICK+", alors "+p.TICK+"gamma"+p.TICK+".\n",
                           encoding="utf-8")
            docs=p.discover((root,))
            self.assertEqual(len(docs),1)
            query={"id":"UNSEEN","source_id":"BR-NEW-RULE-007",
                   "expected_source_blob":docs["BR-NEW-RULE-007"]["blob"],
                   "kind":"horn","facts":["alpha"],"goal":"gamma"}
            verdict=p.answer(query,docs)
            self.assertEqual(verdict["verdict"],"SUPPORTED")
            self.assertEqual(len(verdict["proof"]),2)
            self.assertTrue(verdict["certificate_valid"])

    def test_free_prose_and_analogies_not_automatically_inferred(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            f=root/"not_a_rule.md"
            f.write_text("# BR-LAB-OTHER-07 — Negative control\n"
                         "Quand alpha est vrai, beta devrait être vrai.\n"
                         "Si alpha alors beta.\n"
                         "La relation entre alpha et beta est conceptuelle.\n",
                         encoding="utf-8")
            docs=p.discover((root,))
            d=docs["BR-LAB-OTHER-07"]
            self.assertEqual(p.extract_horn(d),[])
            q={"source_id":d["id"],"expected_source_blob":d["blob"],
               "kind":"horn","facts":["alpha"],"goal":"beta"}
            self.assertEqual(p.answer(q,docs)["verdict"],"ABSTAIN")

    def test_source_missing_abstains(self):
        q={"source_id":"BR-ABSENT-000","kind":"horn",
           "facts":["a"],"goal":"b"}
        self.assertEqual(p.answer(q,self.documents)["verdict"],"ABSTAIN")

    def test_direct_cli_answers_real_source_without_gold(self):
        import subprocess
        import sys
        source=dict(self.cases[6])
        source.pop("expected")
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/"query.json"
            path.write_text(json.dumps(source),encoding="utf-8")
            proc=subprocess.run([sys.executable,str(p.HERE/"pipeline.py"),
                                 "--query",str(path)],
                                capture_output=True,text=True,timeout=20)
            self.assertEqual(proc.returncode,0,proc.stderr)
            result=json.loads(proc.stdout)
            self.assertEqual(result["verdict"],"SUPPORTED")
            self.assertTrue(result["certificate_valid"])
            self.assertEqual(result["source_id"],REAL_ID)
            self.assertNotIn("expected",result)
            source["expected"]="SUPPORTED"
            path.write_text(json.dumps(source),encoding="utf-8")
            refused=subprocess.run([sys.executable,str(p.HERE/"pipeline.py"),
                                    "--query",str(path)],
                                   capture_output=True,text=True,timeout=20)
            self.assertNotEqual(refused.returncode,0)
            self.assertIn("without expected",refused.stderr)

    def test_frozen_cohort_and_no_gold_leak(self):
        self.assertEqual(len(self.cases),12)
        self.assertEqual([q["expected"] for q in self.cases].count("SUPPORTED"),4)
        self.assertEqual([q["expected"] for q in self.cases].count("ABSTAIN"),5)
        real_answer=p.answer({k:v for k,v in self.cases[0].items() if k!="expected"},
                             self.documents)
        self.assertNotIn("expected",real_answer)
        r=p.run(self.cases,self.documents)
        self.assertEqual(r["cases"],12)
        self.assertEqual(r["false_confident"],0)
        self.assertEqual(r["correct"],12)
        self.assertEqual(r["answered"],7)
        self.assertEqual(r["always_abstain_baseline_correct"],5)
        self.assertEqual(r["invalid_certificates"],0)
        self.assertFalse(r["auto_promotion"])


if __name__=="__main__":
    unittest.main()
