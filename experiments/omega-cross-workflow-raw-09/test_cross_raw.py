"""14 pre-source tests using SYNTHETIC ZIPs and logs, not the five real runs."""
from __future__ import annotations
from hashlib import sha256
from io import BytesIO
import copy
import json
from pathlib import Path
import shutil
import tempfile
import unittest
import zipfile

import collect
import infer
import score

RUN_IDS=(44168561827,44163800137,44162518044,44149347157,44149424240)
ART_IDS=(14367000971,14366048721,14365590280,14362909206,
         14363373146,14359120046,14358575909)
ROOT_INDEX=(0,0,1,2,2,3,4)
SAME_SHA="49d9cb31901549088b7baf699f0dd40d84fce8e6"


def zip_bytes(text):
    b=BytesIO()
    with zipfile.ZipFile(b,"w",compression=zipfile.ZIP_DEFLATED) as f:
        f.writestr("report.txt",text)
    return b.getvalue()


def write_json(p,doc):
    p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(doc,sort_keys=True,indent=2)+"\n")


def fixture(where, link_all=True):
    raw=where/"raw"
    index={"schema":"omega-cross-workflow-raw09",
           "source_type":"real_GitHub_REST_job_logs_and_artifact_ZIP_bytes",
           "archive_packets":[f"packet-{i:03d}" for i in range(9)],
           "log_files":[f"trace-{i:03d}.log" for i in range(5)],
           "gold_not_in_raw":True}
    gold={"experiment":"OMEGA-CROSS-WORKFLOW-RAW-09",
          "source_runs":[{"run_id":run,"run_attempt":1,
                          "head_sha":SAME_SHA if i>=3 else "%040d"%(i+1),
                          "event":"push"} for i,run in enumerate(RUN_IDS)],
          "logs":{}, "artifacts":{}, "transport_injections":{
              "mirror":"packet-007","orphan":"packet-008"}}
    write_json(raw/"inventory.json",index)
    zipped=[]
    for i in range(7):
        # Two distinct artifacts can have byte-identical content.
        b=zip_bytes("identical" if i>=5 else "trial_"+str(i))
        zipped.append(b)
        p=raw/"artifacts"/f"packet-{i:03d}"
        p.mkdir(parents=True)
        (p/"archive.zip").write_bytes(b)
        write_json(p/"transport.json",{
            "artifact_id":ART_IDS[i],
            "artifact_name":"same-name" if i in (5,6) else "a"+str(i),
            "zip_sha256":sha256(b).hexdigest()})
        gold["artifacts"][f"packet-{i:03d}"]={
            "origin_run_id":RUN_IDS[ROOT_INDEX[i]],
            "artifact_id":ART_IDS[i],"role":"ORIGINAL"}
    for i,j,name in ((7,0,"MIRROR"),(8,1,"ORPHAN")):
        dest=raw/"artifacts"/f"packet-{i:03d}"
        dest.mkdir()
        (dest/"archive.zip").write_bytes(zipped[j])
        envelope=json.loads((raw/"artifacts"/f"packet-{j:03d}"/"transport.json").read_bytes())
        if i==8:
            envelope["artifact_id"]=None
        write_json(dest/"transport.json",envelope)
        gold["artifacts"][f"packet-{i:03d}"]={
            "origin_run_id":None if i==8 else RUN_IDS[ROOT_INDEX[j]],
            "artifact_id":None if i==8 else ART_IDS[j],"role":name}
    for i,run_id in enumerate(RUN_IDS):
        links=[(aid,RUN_IDS[ROOT_INDEX[k]]) for k,aid in enumerate(ART_IDS)
               if ROOT_INDEX[k]==i]
        entries=[
            f"2026-11-17T00:00:00Z Artifact download URL: https://github.com/Abrasax63/Omega-pub/actions/runs/{rid}/artifacts/{aid}"
            for aid,rid in links] if link_all else []
        content=("\n".join(entries+["job test complete"])+"\n").encode()
        name=f"trace-{i:03d}.log"
        (raw/"logs").mkdir(exist_ok=True)
        (raw/"logs"/name).write_bytes(content)
        gold["logs"][name]={"run_id":run_id,"job_id":i+123,"size":len(content),
                             "sha256":sha256(content).hexdigest()}
    return raw,gold


class CrossWorkflowRawControls(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp=tempfile.TemporaryDirectory()
        cls.root=Path(cls.tmp.name)
        cls.raw,cls.gold=fixture(cls.root)
        cls.good=infer.resolve(cls.raw)

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def copy(self):
        tmp=tempfile.TemporaryDirectory()
        raw=Path(tmp.name)/"raw"
        shutil.copytree(self.raw,raw)
        return tmp,raw

    def test_01_preregistered_identifiers_and_sources(self):
        self.assertEqual(collect.PREREG_COMMIT,
                         "4a665830b38f133ab903882748029123c6b33389")
        self.assertEqual(tuple(x for x,_ in collect.SOURCE),RUN_IDS)
        self.assertEqual(sum(len(x) for _,x in collect.SOURCE),7)
        self.assertEqual(collect.SAMPLE_SEED,59221)

    def test_02_synthetic_urls_link_all_original_source_artifacts(self):
        self.assertEqual(self.good["status"],"LINKED_WITH_PROVIDER_LOGS")
        self.assertEqual(self.good["certified_artifact_links"],7)
        self.assertEqual(self.good["linked_packet_count"],8)
        self.assertEqual(self.good["linked_distinct_runs"],5)
        self.assertEqual(self.good["abstentions"],1)

    def test_03_content_identical_but_distinct_runs_are_not_merged(self):
        entries={r["artifact_id"]:r for r in self.good["results"]
                 if r["role"]=="ORIGINAL_TRANSPORT"}
        a,b=entries[ART_IDS[5]],entries[ART_IDS[6]]
        self.assertEqual(a["zip_sha256"],b["zip_sha256"])
        self.assertNotEqual(a["run_id"],b["run_id"])
        self.assertEqual([a["run_id"],b["run_id"]],list(RUN_IDS[-2:]))

    def test_04_two_different_artifacts_share_run_correctly(self):
        origins={x["artifact_id"]:x["run_id"] for x in self.good["results"]
                 if x["role"]=="ORIGINAL_TRANSPORT"}
        self.assertEqual(origins[ART_IDS[0]],origins[ART_IDS[1]])
        self.assertEqual(origins[ART_IDS[3]],origins[ART_IDS[4]])

    def test_05_duplicate_transport_mirror_and_orphan(self):
        results={r["packet"]:r for r in self.good["results"]}
        self.assertEqual(results["packet-007"]["role"],"MIRROR_TRANSPORT")
        self.assertEqual(results["packet-007"]["run_id"],
                         results["packet-000"]["run_id"])
        self.assertEqual(results["packet-008"]["status"],"ABSTAIN")
        self.assertIsNone(results["packet-008"]["run_id"])

    def test_06_no_urls_means_abstention_never_guess_by_name_or_bytes(self):
        t=tempfile.TemporaryDirectory()
        try:
            raw,g=fixture(Path(t.name),link_all=False)
            result=infer.resolve(raw)
            self.assertEqual(result["status"],"NO_PROVIDER_URL_SIGNAL")
            self.assertEqual(result["certified_artifact_links"],0)
            self.assertEqual(result["abstentions"],9)
            self.assertEqual(result["linked_distinct_runs"],0)
        finally:
            t.cleanup()

    def test_07_conflicting_run_in_log_fails_closed(self):
        t,raw=self.copy()
        try:
            p=raw/"logs"/"trace-000.log"
            with p.open("a") as f:
                f.write(f"Artifact download URL: https://github.com/Abrasax63/Omega-pub/actions/runs/99999999/artifacts/{ART_IDS[0]}\n")
            with self.assertRaisesRegex(infer.LinkConflict,"CONFLICTING_LOG_RUN_IDS"):
                infer.resolve(raw)
        finally:
            t.cleanup()

    def test_08_unrelated_url_not_provider_upload_link(self):
        t,raw=self.copy()
        try:
            p=raw/"logs"/"trace-000.log"
            p.write_text(
                "Docs reference https://github.com/Abrasax63/Omega-pub/actions/runs/90999999/artifacts/14367000971\n"
            )
            result=infer.resolve(raw)
            first=next(x for x in result["results"] if x["artifact_id"]==ART_IDS[0]
                       and x["role"]=="ORIGINAL_TRANSPORT")
            self.assertEqual(first["status"],"ABSTAIN")
        finally:
            t.cleanup()

    def test_09_corrupt_zip_rejected(self):
        t,raw=self.copy()
        try:
            (raw/"artifacts"/"packet-000"/"archive.zip").write_bytes(b"not-a-zip")
            with self.assertRaisesRegex(infer.LinkConflict,"INVALID_ARCHIVE_ZIP"):
                infer.resolve(raw)
        finally:
            t.cleanup()

    def test_10_wrong_zip_sha_rejected(self):
        t,raw=self.copy()
        try:
            p=raw/"artifacts"/"packet-000"/"transport.json"
            d=json.loads(p.read_bytes())
            d["zip_sha256"]="0"*64
            write_json(p,d)
            with self.assertRaisesRegex(infer.LinkConflict,
                                         "TRANSPORT_DIGEST_MISMATCH"):
                infer.resolve(raw)
        finally:
            t.cleanup()

    def test_11_unsupported_artifact_id_rejected(self):
        t,raw=self.copy()
        try:
            p=raw/"artifacts"/"packet-000"/"transport.json"
            d=json.loads(p.read_bytes())
            d["artifact_id"]="not-an-int"
            write_json(p,d)
            with self.assertRaisesRegex(infer.LinkConflict,
                                         "INVALID_TRANSPORT_ARTIFACT_ID"):
                infer.resolve(raw)
        finally:
            t.cleanup()

    def test_12_absent_log_fails_closed(self):
        t,raw=self.copy()
        try:
            (raw/"logs"/"trace-000.log").unlink()
            with self.assertRaisesRegex(infer.LinkConflict,
                                         "LOG_INVENTORY_MISMATCH"):
                infer.resolve(raw)
        finally:
            t.cleanup()

    def test_13_independent_gold_judge_checks_correct_links_and_name_baseline(self):
        result=score.evaluate(self.raw,self.good,self.gold)
        self.assertEqual(result["status"],"PROVIDER_LOG_LINKS_VERIFIED")
        self.assertEqual(result["linked_real_archives"],7)
        self.assertEqual(result["wrong_origin_links"],0)
        self.assertEqual(result["name_only_wrong_same_run_pairs"],1)
        self.assertEqual(result["transport_orphan_abstention_ok"],1)

    def test_14_judge_rejects_false_links_or_independence(self):
        wrong=copy.deepcopy(self.good)
        wrong["scientific_independence"]="PROVEN"
        with self.assertRaises(score.ScoreMismatch):
            score.evaluate(self.raw,wrong,self.gold)
        wrong=copy.deepcopy(self.good)
        rec=next(x for x in wrong["results"]
                 if x["role"]=="ORIGINAL_TRANSPORT")
        rec["run_id"]=99999999
        with self.assertRaises(score.ScoreMismatch):
            score.evaluate(self.raw,wrong,self.gold)


if __name__=="__main__":
    unittest.main()
