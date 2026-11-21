import hashlib
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase, main
from unittest.mock import patch
from single_resident import (
    AUTHORIZED, EXPECTED_ENGINE,AdmissionRefused,RuntimeUncertain,
    ModelProfile,check_model_file,SingleResidentGovernor,LocalLlamaBackend
)


class FakeBackend:
    def __init__(self):
        self.events=[]
        self.running=None
        self.fail_start=False
        self.fail_stop=False
        self.fail_health=False
        self.peak=1500
    def start(self,profile):
        self.events.append("start:"+profile.label)
        if self.fail_start: raise RuntimeError("start failed")
        if self.running is not None:raise RuntimeError("second model resident")
        self.running=profile.label
    def stop(self):
        self.events.append("stop")
        if self.fail_stop:raise RuntimeError("cannot stop")
        self.running=None
    def healthy(self):
        return self.running is not None and not self.fail_health
    def peak_rss_kib(self):
        return self.peak


class ResidencyTests(TestCase):
    def setUp(self):
        self.temp=TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path_a=Path(self.temp.name)/"a.gguf"
        self.path_b=Path(self.temp.name)/"b.gguf"
        self.path_a.write_bytes(b"mock-qwen-a-pinned-file")
        self.path_b.write_bytes(b"mock-qwen-b-pinned-file")
        self.sha_a=hashlib.sha256(self.path_a.read_bytes()).hexdigest()
        self.sha_b=hashlib.sha256(self.path_b.read_bytes()).hexdigest()
        self.digests=patch.dict(AUTHORIZED,{"0p5b":self.sha_a,"3b":self.sha_b})
        self.digests.start()
        self.addCleanup(self.digests.stop)
        self.a=ModelProfile("0p5b",self.path_a,self.sha_a,len(self.path_a.read_bytes()),1600,
                            EXPECTED_ENGINE,"TEST_ONLY")
        self.b=ModelProfile("3b",self.path_b,self.sha_b,len(self.path_b.read_bytes()),1700,
                            EXPECTED_ENGINE,"TEST_ONLY")
    def test_model_file_sha_verification_and_tampering(self):
        check_model_file(self.a)
        self.path_a.write_bytes(b"corrupted-sha-file------")
        with self.assertRaises(AdmissionRefused):check_model_file(self.a)
    def test_same_model_not_loaded_twice(self):
        backend=FakeBackend()
        g=SingleResidentGovernor(backend,budget_kib=3000,reserve_kib=512)
        self.assertEqual(g.activate(self.a),"NEW_LOCAL_MODEL_RESIDENT")
        self.assertEqual(g.activate(self.a),"REUSED_SAME_RESIDENT_MODEL")
        self.assertEqual(backend.events,["start:0p5b"])
        g.release()
        self.assertEqual(backend.events[-1],"stop")
    def test_switch_stops_then_starts_and_no_double_residency(self):
        backend=FakeBackend()
        g=SingleResidentGovernor(backend,budget_kib=3000,reserve_kib=512)
        g.activate(self.a)
        g.activate(self.b)
        self.assertEqual(backend.events,["start:0p5b","stop","start:3b"])
        self.assertEqual(backend.running,"3b")
        self.assertEqual(g.switches,2)
    def test_memory_budget_does_not_automatically_downgrade(self):
        backend=FakeBackend()
        g=SingleResidentGovernor(backend,budget_kib=2000,reserve_kib=512)
        with self.assertRaisesRegex(AdmissionRefused,"INSUFFICIENT_MEASURED_MEMORY_HEADROOM"):
            g.activate(self.b)
        self.assertEqual(backend.events,[])
        self.assertIsNone(g.current)
    def test_tampered_new_model_does_not_evict_current(self):
        backend=FakeBackend()
        g=SingleResidentGovernor(backend,budget_kib=3000,reserve_kib=512)
        g.activate(self.a)
        self.path_b.write_bytes(b"tampered")
        with self.assertRaises(AdmissionRefused):g.activate(self.b)
        self.assertEqual(backend.running,"0p5b")
        self.assertEqual(g.current,self.a)
    def test_stop_failure_blocks_all_future_swaps(self):
        backend=FakeBackend()
        g=SingleResidentGovernor(backend,budget_kib=3000,reserve_kib=512)
        g.activate(self.a)
        backend.fail_stop=True
        with self.assertRaises(RuntimeUncertain):g.activate(self.b)
        self.assertTrue(g.blocked)
        with self.assertRaises(RuntimeUncertain):g.activate(self.a)
        self.assertEqual(backend.events.count("start:3b"),0)
    def test_start_failure_fails_closed_and_recovers_after_stop(self):
        backend=FakeBackend()
        g=SingleResidentGovernor(backend,budget_kib=3000,reserve_kib=512)
        backend.fail_start=True
        with self.assertRaisesRegex(RuntimeError,"start failed"):g.activate(self.a)
        self.assertIsNone(g.current)
        self.assertIn("stop",backend.events)
        backend.fail_start=False
        self.assertEqual(g.activate(self.a),"NEW_LOCAL_MODEL_RESIDENT")
    def test_actual_rss_above_budget_aborts_load(self):
        backend=FakeBackend()
        backend.peak=2700
        g=SingleResidentGovernor(backend,budget_kib=3000,reserve_kib=512)
        with self.assertRaisesRegex(RuntimeError,"OBSERVED_PROCESS_EXCEEDS_MEMORY_BUDGET"):
            g.activate(self.a)
        self.assertIsNone(backend.running)
        self.assertIsNone(g.current)
    def test_unhealthy_model_blocks_existing_resident(self):
        backend=FakeBackend()
        g=SingleResidentGovernor(backend,budget_kib=3000,reserve_kib=512)
        g.activate(self.a)
        backend.fail_health=True
        with self.assertRaises(RuntimeUncertain):g.activate(self.a)
        self.assertTrue(g.blocked)
    def test_from_scale_report_requires_verified_output(self):
        profile={
            "status":"FINISHED","model_label":"0p5b",
            "engine_sha":EXPECTED_ENGINE,
            "model_expected_sha256":self.sha_a,
            "model_weight_file_bytes":self.a.weight_bytes,
            "summary":{"quality_status":"LOCAL_TEXT_AND_SOURCE_GATE_PARITY",
                       "by_mode":{"off":{"server_peak_rss_kib_max":1600},
                                  "on":{"server_peak_rss_kib_max":1800}}},
        }
        p=ModelProfile.from_scale_report(profile,self.path_a)
        self.assertEqual(p.observed_peak_rss_kib,1800)
        profile["summary"]["quality_status"]="DIVERGENCE_OBSERVED"
        with self.assertRaises(AdmissionRefused):ModelProfile.from_scale_report(profile,self.path_a)
        profile["summary"]["quality_status"]="LOCAL_TEXT_AND_SOURCE_GATE_PARITY"
        profile["summary"]["by_mode"]["on"].pop("server_peak_rss_kib_max")
        with self.assertRaises(AdmissionRefused):ModelProfile.from_scale_report(profile,self.path_a)
    def test_backend_port_requires_loopback_and_no_public_bind(self):
        with self.assertRaises(ValueError):LocalLlamaBackend("/tmp/nonexistent",port=80)
        backend=LocalLlamaBackend("/tmp/nonexistent",port=8129)
        self.assertEqual(backend.port,8129)
        with self.assertRaisesRegex(RuntimeError,"BINARY_MISSING"):
            backend.start(self.a)

if __name__=="__main__":main()
