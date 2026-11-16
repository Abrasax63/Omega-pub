"""No unverified scientific conclusions from a provenance-claim graph."""
import unittest
from slsa_dependency_compare import compare_reports


def report(repo, deps, *, verified=True):
    return {
        "signature_verified": verified,
        "status": "VERIFIED_BUILD_PROVENANCE_ONLY" if verified else "INDETERMINATE",
        "evidence": [{
            "certificate_repository_id": str(repo),
            "subject_sha256": "a"*64,
            "claimed_builder_id": "https://builder.invalid/workflow",
            "claimed_build_type": "https://example.invalid/buildtype",
            "claimed_invocation_id": "caller-supplied",
            "listed_dependency_count": len(deps),
            "reported_dependencies": deps,
            "dependencies_truncated": False,
        }],
    }


class DependencyCompareTests(unittest.TestCase):
    def test_shared_dependency_is_only_reported_claim(self):
        common = {"uri":"git+https://example.invalid/common","sha256":"b"*64}
        left = report("1",[common])
        right = report("2",[common])
        result=compare_reports(left,right)
        self.assertEqual(result["status"],"SIGNED_PROVENANCE_CLAIMS_COMPARED")
        self.assertEqual(result["shared_claimed_dependency_count"],1)
        self.assertTrue(result["distinct_certified_repositories"])
        self.assertEqual(result["scientific_independence"],"NOT_ESTABLISHED")
        self.assertTrue(result["unresolved_dependency_provenance"])

    def test_distinct_repositories_do_not_prove_independence(self):
        result=compare_reports(report("1",[]),report("2",[]))
        self.assertTrue(result["distinct_certified_repositories"])
        self.assertEqual(result["scientific_correctness"],"NOT_ESTABLISHED")

    def test_reject_unsigned_or_missing_records(self):
        for value in (None,{},report("1",[],verified=False),
                      {"signature_verified":True,"status":"VERIFIED_BUILD_PROVENANCE_ONLY","evidence":[]}):
            with self.subTest(value=value):
                self.assertEqual(compare_reports(value,report("2",[]))["status"],"INDETERMINATE")

    def test_invalid_repo_id_abstains(self):
        self.assertEqual(compare_reports(report("?",[]),report("2",[]))["status"],"INDETERMINATE")

    def test_mismatched_digest_same_uri_detected(self):
        left=report("1",[{"uri":"git://common","sha256":"a"*64}])
        right=report("2",[{"uri":"git://common","sha256":"b"*64}])
        result=compare_reports(left,right)
        self.assertEqual(result["shared_claimed_dependency_count"],0)
        self.assertIn("git://common",result["same_uri_without_matching_digest"])

    def test_unlabeled_dependency_kept_as_unverified_claim(self):
        left=report("1",[{"uri":"pkg:dependency","sha256":None}])
        right=report("2",[{"uri":"pkg:dependency","sha256":None}])
        result=compare_reports(left,right)
        self.assertEqual(result["shared_claimed_dependency_count"],1)
        self.assertTrue(result["unresolved_dependency_provenance"])


    def test_source_git_commits_are_retained_and_disjoint(self):
        a=report("212613049", [{"uri":"git+https://github.com/cli/cli@refs/heads/trunk",
                                 "git_commit":"a"*40,"sha256":None}])
        b=report("341596960", [{"uri":"git+https://github.com/sigstore/fulcio@refs/tags/v1.10.0",
                                 "git_commit":"b"*40,"sha256":None}])
        result=compare_reports(a,b)
        self.assertEqual(result["shared_claimed_dependency_count"],0)
        self.assertEqual(result["subjects"][0]["reported_dependencies"][0]["git_commit"],"a"*40)
        self.assertEqual(result["subjects"][1]["reported_dependencies"][0]["git_commit"],"b"*40)
        self.assertEqual(result["scientific_independence"],"NOT_ESTABLISHED")


if __name__=="__main__":
    unittest.main()
