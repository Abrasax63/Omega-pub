"""P5-OBS-03: real single-provider source receipts, no invented independence."""
import copy
import unittest

import p5_obs03_empirical_provenance as m


class RealProvenanceAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report=m.run()

    def test_twelve_actual_public_prs_and_no_independent_provider(self):
        x=self.report
        self.assertEqual(x["real_prs"],12)
        self.assertEqual(x["fresh_github_endpoint_observations"],36)
        self.assertEqual(x["additional_full_filenames_rereads"],12)
        self.assertEqual(x["providers_seen"],["github.com"])
        self.assertEqual(x["independent_provider_count"],1)
        self.assertEqual(x["independent_external_corroborations"],0)
        self.assertEqual(set(x["certificates"]),{
            "SAME_PROVIDER_CONSISTENT_NOT_TRANSACTIONALLY_PINNED"})
        self.assertEqual(sum(r["cert"]["observed_decision_from_github_fields"]
                             for r in x["cases"]),1)
        self.assertTrue(all(not r["cert"]["correctness_certified_independently"]
                            for r in x["cases"]))

    def test_raw_filenames_reproduce_boolean_not_just_trust_them(self):
        self.assertTrue(m.test_filename("Lib/test/test_abc.py"))
        self.assertTrue(m.test_filename("pkg/tests/alpha.txt"))
        self.assertTrue(m.test_filename("unit_test.py"))
        self.assertTrue(m.test_filename("test_example.sh"))
        self.assertFalse(m.test_filename("src/testing/abc.py"))
        self.assertFalse(m.test_filename("README.md"))
        self.assertFalse(m.test_filename("tools/testtools.py"))
        for row in self.report["cases"]:
            assert row["cert"]["status"]=="SAME_PROVIDER_CONSISTENT_NOT_TRANSACTIONALLY_PINNED"
            expected=any(m.test_filename(name) for name in row["changed_files_now"])
            self.assertEqual(row["cert"]["test_changed_recomputed"],expected)
            self.assertEqual(len(row["cert"]["full_filenames_sha256"]),64)

    def test_controls_include_strong_alternative_short_circuit_order(self):
        x=self.report["replay_controls"]
        self.assertEqual(x["status"],"REPLAY_FROM_RECORDED_FIELDS_NOT_ACTUAL_SAVED_CALLS")
        p=x["policies"]
        for name in p:
            self.assertEqual(p[name]["correct"],12 if name!="reject_all" else 11)
        self.assertEqual(p["fixed_both"]["logical_calls"],24)
        self.assertEqual(p["merged_first"]["logical_calls"],17)
        self.assertEqual(p["files_first"]["logical_calls"],15)
        self.assertEqual(p["reject_all"]["logical_calls"],0)

    def test_correlated_github_endpoints_are_not_two_suppliers(self):
        row=m._unique_rows(m._load(m.PARTS),3)[("python/cpython",154650)]
        files=m._unique_rows(m._load(m.FULL),3)[("python/cpython",154650)]
        cert=m.provenance_certificate(row,files)
        self.assertEqual(cert["independent_providers"],1)
        self.assertEqual(cert["status"],
                         "SAME_PROVIDER_CONSISTENT_NOT_TRANSACTIONALLY_PINNED")
        self.assertFalse(cert["correctness_certified_independently"])
        self.assertIn("unpinned",cert["race_warning"])

    def test_conflicting_metadata_fails_closed(self):
        row=copy.deepcopy(m._unique_rows(m._load(m.PARTS),3)[
            ("python/cpython",154650)])
        files=copy.deepcopy(m._unique_rows(m._load(m.FULL),3)[
            ("python/cpython",154650)])
        row["alternate"]["merged"]=not row["metadata"]["merged"]
        self.assertEqual(m.provenance_certificate(row,files)["status"],
                         "CROSS_ENDPOINT_CONFLICT")
        row["alternate"]["merged"]=row["metadata"]["merged"]
        row["alternate"]["head_sha"]="0"*40
        self.assertEqual(m.provenance_certificate(row,files)["status"],
                         "CROSS_ENDPOINT_CONFLICT")
        row["metadata"]["head_sha"]=None
        self.assertEqual(m.provenance_certificate(row,files)["status"],
                         "INSUFFICIENT_EVIDENCE")

    def test_changed_filenames_or_unrecognized_provider_rejected(self):
        row=copy.deepcopy(m._unique_rows(m._load(m.PARTS),3)[
            ("python/cpython",154650)])
        files=copy.deepcopy(m._unique_rows(m._load(m.FULL),3)[
            ("python/cpython",154650)])
        files["filenames"].append("test_new.py")
        self.assertEqual(m.provenance_certificate(row,files)["status"],
                         "CROSS_READ_FILE_PATH_DRIFT")
        files["filenames"].pop()
        files["provider"]="github-mirror.invalid"
        with self.assertRaises(ValueError):
            m.provenance_certificate(row,files)

    def test_no_false_independence_from_archived_fake_receipts(self):
        # The earlier provenance_cases fixtures are constructed examples;
        # they are not used by the empirical OBS03 runner.
        from pathlib import Path
        src=Path(m.__file__).read_text(encoding="utf-8")
        self.assertNotIn("provenance_cases/observations.json",src)
        self.assertNotIn("simulate",str(self.report["status"]).lower())
        self.assertIn("no actual independent-provider failures",
                      " ".join(self.report["limitations"]).lower())

if __name__=="__main__":
    unittest.main()
