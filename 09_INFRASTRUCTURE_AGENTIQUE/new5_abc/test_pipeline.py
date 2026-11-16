import json
import unittest

from abc_core import ARMS, MAX_PER_ARM, sha
from abc_oracle import verify_commitment
from abc_runner import MODEL_CALLS_PER_REPRODUCED_BUG, MODEL_NEW_TOKENS

def fixture():
    cases=[]
    co=[]
    for i in range(1,6):
        ident="N"+str(i)
        co.append({"id":ident,"buggy_sha":"b"+str(i)})
        cases.append({"id":ident,"buggy_sha":"b"+str(i),
                      "candidate_count":1,"candidates":[{"id":"P000"}],
                      "orders":{ARMS[0]:["P000"],ARMS[1]:["P000"],
                                ARMS[2]:["P000"]},
                      "fixed_source_seen":False,
                      "arms":{arm:{"actual_attempts":[],"logical_tests_consumed":0,
                                    "selected_patch_id":None}
                              for arm in ARMS}})
    cohort={"experiment":"OMEGA-NEW5-ABC-01","cases":co}
    freeze={"experiment":"OMEGA-NEW5-ABC-01","phase":"ABC_SELECTION_BUGGY_ONLY",
            "fixed_source_seen":False,"fixed_diff_seen":False,
            "external_oracle_opened":False,"new_model_calls":5,
            "cases":cases}
    freeze["selection_sha256"]=sha(json.dumps(freeze,sort_keys=True,ensure_ascii=False))
    return freeze,cohort


class PipelineContractTests(unittest.TestCase):
    def test_exact_model_budget(self):
        self.assertEqual(MODEL_CALLS_PER_REPRODUCED_BUG,1)
        self.assertEqual(MODEL_NEW_TOKENS,128)
        self.assertEqual(MAX_PER_ARM,4)

    def test_good_record_is_valid(self):
        a,b=fixture()
        self.assertEqual(verify_commitment(a,b),a["selection_sha256"])

    def test_modified_candidate_after_freeze_rejected(self):
        a,b=fixture()
        a["cases"][0]["candidate_count"]=5
        with self.assertRaisesRegex(ValueError,"commitment drift"):
            verify_commitment(a,b)

    def test_fixed_source_leak_rejected(self):
        a,b=fixture()
        a["fixed_source_seen"]=True
        a["selection_sha256"]=sha(json.dumps(
            {k:v for k,v in a.items() if k!="selection_sha256"},
            sort_keys=True,ensure_ascii=False))
        with self.assertRaisesRegex(ValueError,"fixed source"):
            verify_commitment(a,b)

    def test_more_than_five_model_calls_rejected(self):
        a,b=fixture()
        a["new_model_calls"]=6
        a["selection_sha256"]=sha(json.dumps(
            {k:v for k,v in a.items() if k!="selection_sha256"},
            sort_keys=True,ensure_ascii=False))
        with self.assertRaisesRegex(ValueError,"model budget"):
            verify_commitment(a,b)

    def test_oversized_patch_test_budget_rejected(self):
        a,b=fixture()
        a["cases"][0]["arms"][ARMS[1]]["logical_tests_consumed"]=5
        a["selection_sha256"]=sha(json.dumps(
            {k:v for k,v in a.items() if k!="selection_sha256"},
            sort_keys=True,ensure_ascii=False))
        with self.assertRaisesRegex(ValueError,"test budget"):
            verify_commitment(a,b)

    def test_unfrozen_patch_id_rejected(self):
        a,b=fixture()
        a["cases"][0]["arms"][ARMS[0]]["selected_patch_id"]="P999"
        a["selection_sha256"]=sha(json.dumps(
            {k:v for k,v in a.items() if k!="selection_sha256"},
            sort_keys=True,ensure_ascii=False))
        with self.assertRaisesRegex(ValueError,"patch outside"):
            verify_commitment(a,b)


if __name__=="__main__":
    unittest.main()
