import concurrent.futures
import threading
import time
import unittest
from router import CallResidency

BASE = dict(tenant="tenant-A", credential_scope="key-scope-A", endpoint="local-chat",
            model_revision="model-v1", payload={"model": "M", "messages": [{"role": "user", "content": "explain 3+5"}], "temperature": 0, "max_tokens": 24}, replay_approved=True)

class ApiCallResidencyTests(unittest.TestCase):
    def setUp(self):
        self.router = CallResidency()
        self.calls = 0
    def backend(self, payload):
        self.calls += 1
        return {"answer": "8", "used": payload["max_tokens"]}
    def call(self, **kw):
        return self.router.invoke(**(BASE | {"backend": self.backend} | kw))

    def test_repeated_identical_call_reused(self):
        self.assertEqual(self.call(), self.call()); self.assertEqual(self.calls, 1)
        self.assertEqual(self.router.metrics()["cache_hits"],1)
    def test_opt_in_required(self):
        self.call(replay_approved=False); self.call(replay_approved=False)
        self.assertEqual(self.calls,2)
    def test_tenant_scoped(self):
        self.call(); self.call(tenant="tenant-B"); self.assertEqual(self.calls,2)
    def test_auth_scope_scoped(self):
        self.call(); self.call(credential_scope="other-key-scope"); self.assertEqual(self.calls,2)
    def test_model_revision_scoped(self):
        self.call(); self.call(model_revision="model-v2"); self.assertEqual(self.calls,2)
    def test_payload_all_fields_count(self):
        self.call(); self.call(payload=BASE["payload"] | {"max_tokens": 25}); self.assertEqual(self.calls,2)
    def test_nonzero_temperature_not_cached(self):
        p=BASE["payload"] | {"temperature":0.6}
        self.call(payload=p); self.call(payload=p); self.assertEqual(self.calls,2)
    def test_no_streaming(self):
        p=BASE["payload"] | {"stream":True}
        self.call(payload=p); self.call(payload=p); self.assertEqual(self.calls,2)
    def test_no_tools(self):
        p=BASE["payload"] | {"tools":[{"type":"function","function":{"name":"now"}}]}
        self.call(payload=p); self.call(payload=p); self.assertEqual(self.calls,2)
    def test_different_endpoints_not_cached_together(self):
        self.call(); self.call(endpoint="other"); self.assertEqual(self.calls,2)
    def test_failure_not_cached(self):
        def bad(_): raise RuntimeError("offline")
        for _ in range(2):
            with self.assertRaisesRegex(RuntimeError, "offline"):
                self.call(backend=bad)
        self.assertEqual(self.router.metrics()["backend_calls"],2)
        self.assertEqual(self.router.metrics()["failures"],2)
    def test_cache_return_defensive_copy(self):
        a=self.call(); a["answer"]="tampered"; self.assertEqual(self.call()["answer"],"8")
        self.assertEqual(self.calls,1)
    def test_parallel_singleflight(self):
        n=0
        lock=threading.Lock()
        start=threading.Barrier(5)
        def backend(_):
            nonlocal n
            with lock: n+=1
            time.sleep(0.08)
            return {"answer": "8"}
        def run(_):
            start.wait()
            return self.call(backend=backend)
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as pool:
            replies=list(pool.map(run,range(5)))
        self.assertEqual(n,1)
        self.assertTrue(all(x==replies[0] for x in replies))
        self.assertEqual(self.router.metrics()["backend_calls"],1)
        self.assertEqual(self.router.metrics()["inflight_shared"],4)
    def test_nonjson_payload_rejected_when_opted_in(self):
        with self.assertRaises(TypeError): self.call(payload=BASE["payload"] | {"custom":object()})
    def test_metrics_no_prompt(self):
        self.call()
        self.assertNotIn("explain",str(self.router.metrics()))

if __name__ == "__main__": unittest.main()
