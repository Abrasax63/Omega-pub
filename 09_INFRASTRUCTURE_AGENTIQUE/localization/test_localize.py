"""Offline regression guards for OMEGA-LOC-01."""
import json
from pathlib import Path
import tempfile
import unittest
from localize import (BUGGY,INSPECT,sha,seal,verify_seal,unique_sites,rank_sites,
                      parse_trace,diff_old_sites,evaluate,TAG)

def candidate(i,path,line):
    return {"id":"P%02d"%i,"path":path,"line":line}

class TestLocalization(unittest.TestCase):
    def test_unique_site_budget_and_no_duplicate_reproductions(self):
        x=unique_sites([candidate(0,"tqdm/a.py",10),candidate(1,"tqdm/a.py",10),
                        candidate(2,"tqdm/b.py",3)])
        self.assertEqual(len(x),2)
        self.assertEqual(x[0]["first_candidate"],"P00")
        self.assertEqual(INSPECT,10)

    def test_trace_reorders_same_sites_without_adding_new_site(self):
        sites=unique_sites([candidate(0,"tqdm/a.py",10),candidate(1,"tqdm/b.py",3),
                            candidate(2,"tqdm/c.py",8)])
        evidence={("tqdm/b.py",3):{"last":100,"count":2},
                  ("tqdm/a.py",10):{"last":4,"count":50}}
        ranked=rank_sites(sites,evidence)
        self.assertEqual([(x["path"],x["line"]) for x in ranked],
                         [("tqdm/b.py",3),("tqdm/a.py",10),("tqdm/c.py",8)])
        self.assertEqual({(x["path"],x["line"]) for x in ranked},
                         {(x["path"],x["line"]) for x in sites})

    def test_invalid_trace_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/"trace.log"
            p.write_text(TAG+json.dumps({"event_count":4,"truncated":False,
                "lines":[{"path":"tqdm/../fixed.py","line":1,"count":2,"last":3}]})+"\n")
            with self.assertRaises(ValueError):
                parse_trace(p)
            p.write_text("pytest crashed\n")
            with self.assertRaises(ValueError):
                parse_trace(p)

    def test_valid_trace_single_record(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/"trace.log"
            p.write_text("1 failed\n"+TAG+json.dumps({"event_count":6,"truncated":False,
                "lines":[{"path":"tqdm/_tqdm.py","line":5,"count":3,"last":6}]})+"\n")
            evidence,lookup=parse_trace(p)
            self.assertEqual(lookup[("tqdm/_tqdm.py",5)]["last"],6)

    def test_diff_old_side_and_insertions_not_falsely_scored(self):
        diff=("diff --git a/tqdm/_tqdm.py b/tqdm/_tqdm.py\n"
              "@@ -11,2 +11,3 @@\n-old\n+new\n"
              "@@ -50,0 +53,2 @@\n+insert\n"
              "diff --git a/tqdm/tests/test.py b/tqdm/tests/test.py\n"
              "@@ -4 +4 @@\n-old\n+new\n")
        positions,insertions=diff_old_sites(diff)
        self.assertEqual(positions,{("tqdm/_tqdm.py",11),("tqdm/_tqdm.py",12)})
        self.assertEqual(insertions,[{"path":"tqdm/_tqdm.py","before_old_line":50}])

    def test_commitment_cannot_be_modified_without_detection(self):
        frozen=seal({"phase":"BUGGY_ONLY_FROZEN","fixed_source_seen":False,
                     "candidate_sites":[],"source_commit":BUGGY,"budget_unique_sites":10})
        verify_seal(frozen)
        frozen["candidate_sites"].append({"path":"tqdm/modified.py","line":1})
        with self.assertRaises(ValueError):
            verify_seal(frozen)

    def test_unmatched_grammar_abstention_and_no_false_gain(self):
        sites=[{"path":"tqdm/a.py","line":1,"first_candidate":"P00"}]
        freeze=seal({"phase":"BUGGY_ONLY_FROZEN","fixed_source_seen":False,
                     "source_commit":BUGGY,"budget_unique_sites":10,
                     "buggy_test_failed":True,"trace_status":"VALID",
                     "candidate_sites":sites,"static_top10":sites,"trace_top10":sites})
        diff="diff --git a/tqdm/other.py b/tqdm/other.py\n@@ -20 +20 @@\n"
        result=evaluate(freeze,diff,1,0)
        self.assertEqual(result["status"],"GRAMMAR_COVERAGE_MISSING")
        self.assertIsNone(result["arms"]["static"]["scientific_success"])
        self.assertIsNone(result["arms"]["trace"]["scientific_success"])

    def test_positive_exact_rank_only_after_reproduction(self):
        sites=[{"path":"tqdm/a.py","line":11,"first_candidate":"P00"}]
        frozen=seal({"phase":"BUGGY_ONLY_FROZEN","fixed_source_seen":False,
                     "source_commit":BUGGY,"budget_unique_sites":10,
                     "buggy_test_failed":True,"trace_status":"VALID",
                     "candidate_sites":sites,"static_top10":sites,"trace_top10":sites})
        diff="diff --git a/tqdm/a.py b/tqdm/a.py\n@@ -11 +11 @@\n-old\n+new\n"
        good=evaluate(frozen,diff,1,0)
        self.assertEqual(good["status"],"LOCALIZATION_EVALUATED")
        self.assertEqual(good["arms"]["trace"]["first_exact_rank"],1)
        blocked=evaluate(frozen,diff,0,0)
        self.assertEqual(blocked["status"],"BUG_NOT_REPRODUCED")
        self.assertIsNone(blocked["arms"]["trace"]["scientific_success"])

if __name__=="__main__":
    unittest.main()
