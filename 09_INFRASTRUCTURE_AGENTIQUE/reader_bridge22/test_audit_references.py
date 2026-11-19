#!/usr/bin/env python3
"""Reader22 tests: immutable citations, precise matching, decoys, remote fail closed."""
import json
from pathlib import Path
import sys
import unittest
from urllib.parse import parse_qs, urlsplit

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from audit_references import (EXPECTED, MATCH, MISSING, INDETERMINATE,
    compare_metadata, decoy_of, evaluate, norm, read_manifest, remote_query, source_locs)
from read import safe_read
from web_access import NetworkPolicyError
from test_web_access import FakeResponse

SAMPLES={
  "Observable Graphs":{
    "DOI":"10.1016/j.dam.2011.02.009",
    "title":["Observable graphs"],
    "issued":{"date-parts":[[2011,6,28]]}, "type":"journal-article",
  },
  "Observability of Boolean Networks: A Graph-Theoretic Approach":{
    "DOI":"10.1016/j.automatica.2013.04.038",
    "title":["Observability of boolean networks: A graph-theoretic approach"],
    "issued":{"date-parts":[[2013,8]]}, "type":"journal-article",
  },
  "Temporal correlations in the simplest measurement sequences":{
    "DOI":"10.22331/q-2022-01-18-623",
    "title":["Temporal correlations in the simplest measurement sequences"],
    "issued":{"date-parts":[[2022,1,18]]},"type":"journal-article",
  },
}

class MockCrossref:
    def __init__(self,failure=False):
        self.calls=[]
        self.failure=failure
    def open(self,request,timeout):
        self.calls.append(request.full_url)
        if self.failure:
            raise OSError("MOCK_CROSSREF_NETWORK_DOWN")
        qs=parse_qs(urlsplit(request.full_url).query)
        query=norm(qs["query.bibliographic"][0])
        target=next((v for title,v in SAMPLES.items() if norm(title)==query),None)
        # A deliberately unrelated (valid-looking) citation must not pass.
        distractor={"DOI":"10.0000/irrelevant","title":["A graph-theoretic survey of news"],
                    "issued":{"date-parts":[[2022]]},"type":"journal-article"}
        items=[distractor]+([target] if target else [])
        encoded=json.dumps({"status":"ok","message":{"items":items}}).encode("utf-8")
        return FakeResponse(request.full_url,encoded,"application/json")

class Reader22Tests(unittest.TestCase):
    def test_source_is_exact_and_bibliography_is_anchored(self):
        data=read_manifest()
        raw=safe_read(Path(__file__).resolve().parents[2].parent/data["source_path"],EXPECTED)
        spans=source_locs(raw,data["references"])
        self.assertEqual(len(spans),3)
        for ref in data["references"]:
            self.assertIn(ref["title"].casefold(),spans[ref["id"]]["literal"].casefold())
            self.assertIn(str(ref["year"]),spans[ref["id"]]["literal"])

    def test_exact_match_is_not_fuzzy_and_no_theorem_is_promoted(self):
        r=read_manifest()["references"][0]
        item={"doi":"10.1234/test","title":"Observable Graphs",
              "issued":{"date-parts":[[2011]]}}
        check=compare_metadata(r,[item])
        self.assertEqual(check["status"],MATCH)
        self.assertFalse(check["novelty_proved"])
        self.assertFalse(check["mathematical_theorem_proved"])
        bad=[dict(item,title="Observable Graphs Extended"),
             dict(item,issued={"date-parts":[[2012]]})]
        for wrong in bad:
            self.assertEqual(compare_metadata(r,[wrong])["status"],MISSING)

    def test_blind_to_doi_and_decoys_all_rejected(self):
        source=read_manifest()
        fake=MockCrossref()
        report=evaluate(transport=fake)
        self.assertEqual(report["live_completed"],3)
        self.assertEqual(len(fake.calls),3)
        self.assertEqual(report["metadata_title_year_matches"],3)
        self.assertEqual(report["negative_controls_refused"],3)
        self.assertEqual(report["result_status"],"PASS_METADATA_AND_NEGATIVE_CONTROLS")
        self.assertEqual(report["without_web_external_doi_verification"],0)
        self.assertFalse(report["novelty_or_priority_established"])
        self.assertEqual(report["automatic_scientific_promotions"],0)
        self.assertTrue(all(z["baseline_without_web"]=="NO_EXTERNAL_METADATA" for z in report["results"]))

    def test_remote_unavailable_does_not_turn_into_negative_evidence(self):
        transport=MockCrossref(failure=True)
        report=evaluate(transport=transport)
        self.assertEqual(report["live_completed"],0)
        self.assertEqual(report["metadata_title_year_matches"],0)
        self.assertEqual(report["negative_controls_refused"],0)
        self.assertEqual(report["result_status"],"INDETERMINATE_REMOTE")
        self.assertTrue(all(x["web_status"]=="REMOTE_FETCH_FAILED" for x in report["results"]))

    def test_duplicate_doi_does_not_randomly_resolve(self):
        r=read_manifest()["references"][0]
        w=[{"doi":"10.1016/a","title":r["title"],"issued":{"date-parts":[[r["year"]]]}},
           {"doi":"10.1016/b","title":r["title"],"issued":{"date-parts":[[r["year"]]]}}]
        self.assertEqual(compare_metadata(r,w)["status"],"AMBIGUOUS_METADATA")

    def test_query_is_not_source_url_and_rejects_junk(self):
        self.assertEqual(remote_query("Observable Graphs"),"Observable Graphs")
        self.assertEqual(remote_query("A graph-theoretic approach"),
                         "A graph theoretic approach")
        with self.assertRaises(ValueError):
            remote_query("I"*400)
        self.assertEqual(norm("Theorem: A; B"),"theorem a b")

if __name__=="__main__":
    unittest.main(verbosity=2)
