import json
import tempfile
from pathlib import Path
from unittest.mock import patch
import unittest

from abc_core import ARMS, MAX_PER_ARM, sha
from abc_oracle import verify_commitment
from abc_runner import MODEL_CALLS_PER_REPRODUCED_BUG, MODEL_NEW_TOKENS, MountedPatch, run_regression, build_project_image

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
    @patch("abc_runner.subprocess.run")
    def test_mounted_patch_is_converted_to_actual_file_path(self, mock_run):
        mock_run.return_value.returncode=0
        mock_run.return_value.stdout="1 passed"
        mock_run.return_value.stderr=""
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            source=root/"patch.py"
            test=root/"testfile.py"
            source.write_text("pass\n")
            test.write_text("def test_ok(): pass\n")
            row={"project":"tqdm","test_file":"tests/testfile.py",
                 "test_id":"tests/testfile.py::test_ok"}
            result=run_regression("dummy-image",row,root,test,
                                  patch_file=MountedPatch(source,"mypackage/impl.py"))
            self.assertEqual(result["status"],"PASS")
            command=mock_run.call_args.args[0]
            self.assertIn("type=bind,src="+str(source.resolve())+
                          ",dst=/omega-patch.py,readonly",command)

    @patch("abc_runner.subprocess.run")
    def test_httpie_installs_separate_pinned_requirements(self, mock_run):
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = ""
        mock_run.return_value.stderr = ""
        text_seen = []
        def capture(command, **kwargs):
            idx = command.index("-f")
            dockerfile=Path(command[idx+1])
            text_seen.append(dockerfile.read_text())
            return mock_run.return_value
        mock_run.side_effect=capture
        with tempfile.TemporaryDirectory() as td:
            tag,build=build_project_image(
                {"id":"N5","python":"3.7.3","project":"httpie"},Path(td))
        self.assertEqual(build["exit"],0)
        self.assertIn("'requests' 'pytest-httpbin==1.0.2'",text_seen[0])
        self.assertNotIn("'requests pytest-httpbin",text_seen[0])

    @patch("abc_runner.subprocess.run")
    def test_profiler_json_not_sent_as_qwen_failure_message(self, mock_run):
        mock_run.return_value.returncode = 1
        mock_run.return_value.stdout = ("FAILED tests/testcase.py::test_a - AssertionError\n"
                                         'OMEGA_CALL_TRACE_V1={"schema":"omega-calltrace-v1","files":[]}')
        mock_run.return_value.stderr=""
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            test=root/"test.py"
            test.write_text("def test_a(): assert False\n")
            probe=root/"sitecustomize.py"
            probe.write_text("# mocked\n")
            c={"project":"tqdm","test_file":"tests/test.py",
               "test_id":"tests/test.py::test_a"}
            result=run_regression("dummy-image",c,root,test,profile_file=probe)
        self.assertEqual(result["status"],"FAIL")
        self.assertIn("AssertionError",result["log_tail"])
        self.assertNotIn("OMEGA_CALL_TRACE_V1=",result["log_tail"])
        self.assertIn("OMEGA_CALL_TRACE_V1=",result["trace_log"])

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
