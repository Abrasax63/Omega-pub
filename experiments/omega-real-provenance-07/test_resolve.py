"""Fourteen guards against false provenance and scientific-independence claims."""
import copy
import json
from pathlib import Path
import unittest

import resolve as p

HERE=Path(__file__).resolve().parent
FIXTURE=HERE/"fixtures"/"github_artifact_metadata.json"


def load():
    return json.loads(FIXTURE.read_text())


class GithubProvenanceControls(unittest.TestCase):
    def test_01_frozen_source_sample_and_artifacts(self):
        d=load()
        self.assertEqual(p.PREREG,"bc667631fca36fb992c4e26f2d700195f6462def")
        self.assertEqual(d["repository"],"Abrasax63/Omega-pub")
        self.assertEqual(len(d["source_documents"]),5)
        self.assertEqual(sum(x["artifact_count"] for x in d["source_documents"]),7)
        self.assertFalse(d["mirror_references_added"])

    def test_02_five_execution_attempt_groups_from_seven_artifacts(self):
        result=p.resolve(load())
        self.assertEqual(result["execution_grouping_status"],"VERIFIED_PROVIDER_METADATA")
        self.assertEqual(result["verified_distinct_artifact_ids"],7)
        self.assertEqual(len(result["verified_attempt_groups"]),5)
        groups={r["run_id"]:r["artifact_ids"] for r in result["verified_attempt_groups"]}
        self.assertEqual(groups[44162518044],[14362909206,14363373146])
        self.assertEqual(groups[44149424240],[14356939391,14358575909])
        self.assertEqual(groups[44149347157],[14359120046])
        self.assertEqual(groups[44159373482],[14363146153])
        self.assertEqual(groups[44151231771],[14358313578])

    def test_03_equal_sha_does_not_merge_distinct_runs(self):
        result=p.resolve(load())
        self.assertEqual(len(result["same_commit_but_distinct_run_pairs"]),1)
        pair=result["same_commit_but_distinct_run_pairs"][0]
        self.assertEqual(pair["distinct_run_ids"],[44149347157,44149424240])
        self.assertEqual(pair["head_sha"],
                         "49d9cb31901549088b7baf699f0dd40d84fce8e6")
        self.assertEqual(len(result["verified_attempt_groups"]),5)

    def test_04_never_claims_scientific_reproduction(self):
        r=p.resolve(load())
        self.assertEqual(r["scientific_independence"],"INDETERMINATE")
        self.assertFalse(r["scientific_replication_certified"])
        self.assertFalse(r["provenance_sources_are_live"])

    def test_05_manifest_mirror_does_not_create_new_group(self):
        d=load()
        art=copy.deepcopy(d["source_documents"][0]["artifacts"][0])
        d["source_documents"][0]["artifacts"].append(art)
        d["source_documents"][0]["artifact_count"]+=1
        r=p.resolve(d)
        self.assertEqual(r["duplicate_manifest_references"],1)
        self.assertEqual(r["verified_distinct_artifact_ids"],7)
        self.assertEqual(len(r["verified_attempt_groups"]),5)

    def test_06_duplicate_name_is_not_duplicated_identity(self):
        d=load()
        d["source_documents"][0]["artifacts"][0]["name"]="common-name"
        d["source_documents"][1]["artifacts"][0]["name"]="common-name"
        r=p.resolve(d)
        self.assertEqual(r["verified_distinct_artifact_ids"],7)
        self.assertEqual(len(r["verified_attempt_groups"]),5)

    def test_07_missing_run_attempt_cannot_be_inferred(self):
        d=load()
        del d["source_documents"][0]["run"]["run_attempt"]
        r=p.resolve(d)
        self.assertEqual(r["execution_grouping_status"],"PARTIAL_WITH_ABSTENTIONS")
        self.assertEqual(len(r["unverifiable_artifact_references"]),2)
        self.assertEqual(len(r["verified_attempt_groups"]),4)
        self.assertEqual(r["scientific_independence"],"INDETERMINATE")

    def test_08_missing_embedded_workflow_run_id_abstains(self):
        d=load()
        del d["source_documents"][2]["artifacts"][0]["workflow_run"]["id"]
        r=p.resolve(d)
        self.assertEqual(r["execution_grouping_status"],"PARTIAL_WITH_ABSTENTIONS")
        self.assertEqual(r["unverifiable_artifact_references"][0]["reason"],
                         "MISSING_ARTIFACT_PROVENANCE")

    def test_09_artifact_run_id_conflict_is_fatal(self):
        d=load()
        d["source_documents"][0]["artifacts"][0]["workflow_run"]["id"]=44149424240
        with self.assertRaisesRegex(p.ProvenanceConflict,"ARTIFACT_RUN_ID_CONFLICT"):
            p.resolve(d)

    def test_10_artifact_sha_conflict_is_fatal(self):
        d=load()
        d["source_documents"][0]["artifacts"][0]["workflow_run"]["head_sha"]="0"*40
        with self.assertRaisesRegex(p.ProvenanceConflict,"ARTIFACT_SHA_CONFLICT"):
            p.resolve(d)

    def test_11_artifact_conflict_reusing_same_artifact_id_is_fatal(self):
        d=load()
        d["source_documents"][1]["artifacts"][0]["id"]=d[
            "source_documents"][0]["artifacts"][0]["id"]
        with self.assertRaisesRegex(p.ProvenanceConflict,"DUPLICATE_ARTIFACT_CONFLICT"):
            p.resolve(d)

    def test_12_invalid_source_url_or_run_repository_is_fatal(self):
        d=load()
        d["source_documents"][0]["run_api_url"]="https://example.test/forged"
        with self.assertRaisesRegex(p.ProvenanceConflict,"RUN_SOURCE_URL_MISMATCH"):
            p.resolve(d)
        d=load()
        d["source_documents"][0]["run"]["repository"]="other/repo"
        with self.assertRaisesRegex(p.ProvenanceConflict,"RUN_REPOSITORY_MISMATCH"):
            p.resolve(d)

    def test_13_partial_artifact_list_fails_closed(self):
        d=load()
        d["source_documents"][0]["artifacts"].pop()
        with self.assertRaisesRegex(p.ProvenanceConflict,"ARTIFACT_LIST_INCOMPLETE"):
            p.resolve(d)

    def test_14_no_default_attempt_for_malformed_or_missing_fields(self):
        d=load()
        d["source_documents"][0]["run"]["run_attempt"]=0
        r=p.resolve(d)
        self.assertEqual(r["execution_grouping_status"],"PARTIAL_WITH_ABSTENTIONS")
        self.assertTrue(all(x["reason"]=="MISSING_RUN_ATTEMPT" for x in
                            r["unverifiable_artifact_references"]))
        d=load()
        d["source_documents"][1]["run"]["head_sha"]="F"*40
        with self.assertRaisesRegex(p.ProvenanceConflict,"BAD_RUN_SHA"):
            p.resolve(d)


if __name__=="__main__":
    unittest.main()
