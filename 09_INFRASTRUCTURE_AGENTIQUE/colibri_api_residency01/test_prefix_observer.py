import json
import random
import unittest
from prefix_observer import PrefixObserver

S=dict(tenant="A",authorization_scope="auth",endpoint="local",
       model_revision="rev1",template_revision="template1")
def pack(sys="S",usr="U",**changes):
    return json.dumps(dict(model="m",max_tokens=32,temperature=0,
            messages=[dict(role="system",content=sys),dict(role="user",content=usr)],
            **changes),ensure_ascii=False).encode()
class PrefixTests(unittest.TestCase):
    def setUp(self):
        self.o=PrefixObserver()
        self.sent=[]
    def send(self,body,**kwargs):
        def transport(b):
            self.sent.append(b)
            return b"reply:"+b
        return self.o.forward(body,transport,**(S|kwargs))
    def test_passes_unaltered(self):
        b=pack();self.assertEqual(self.send(b),b"reply:"+b);self.assertEqual(self.sent,[b])
    def test_shared_prefix(self):
        self.send(pack(usr="1"));self.send(pack(usr="2"))
        self.assertEqual(self.o.stats()["shared_prefix_requests"],1)
    def test_different_system(self):
        self.send(pack(sys="A"));self.send(pack(sys="B"))
        self.assertEqual(self.o.stats()["shared_prefix_requests"],0)
    def test_whitespace_in_content_matters(self):
        self.send(pack(sys="S"));self.send(pack(sys="S "))
        self.assertEqual(self.o.stats()["shared_prefix_requests"],0)
    def test_tenant_separated(self):
        b=pack();self.send(b);self.send(b,tenant="B")
        self.assertEqual(self.o.stats()["shared_prefix_requests"],0)
    def test_auth_separated(self):
        b=pack();self.send(b);self.send(b,authorization_scope="other")
        self.assertEqual(self.o.stats()["shared_prefix_requests"],0)
    def test_endpoint_separated(self):
        b=pack();self.send(b);self.send(b,endpoint="other")
        self.assertEqual(self.o.stats()["shared_prefix_requests"],0)
    def test_revision_separated(self):
        b=pack();self.send(b);self.send(b,model_revision="rev2")
        self.assertEqual(self.o.stats()["shared_prefix_requests"],0)
    def test_template_separated(self):
        b=pack();self.send(b);self.send(b,template_revision="other")
        self.assertEqual(self.o.stats()["shared_prefix_requests"],0)
    def test_generation_settings_separated(self):
        self.send(pack());self.send(pack(max_tokens=64))
        self.assertEqual(self.o.stats()["shared_prefix_requests"],0)
    def test_tool_schema_separated(self):
        self.send(pack(tools=[]));self.send(pack(tools=[{"name":"do"}]))
        self.assertEqual(self.o.stats()["shared_prefix_requests"],0)
    def test_different_user_never_skips_calls(self):
        self.send(pack(usr="A"));self.send(pack(usr="B"))
        self.assertEqual(len(self.sent),2)
    def test_bad_json_fail_open(self):
        b=b"not-json";self.assertEqual(self.send(b),b"reply:"+b)
        self.assertEqual(self.o.stats()["skipped"],1)
    def test_no_messages_fail_open(self):
        b=b'{"unrelated":1}';self.assertEqual(self.send(b),b"reply:"+b)
        self.assertEqual(self.o.stats()["skipped"],1)
    def test_binary_fail_open(self):
        b=b"\x00\xff";self.assertEqual(self.send(b),b"reply:"+b)
    def test_size_cap(self):
        o=PrefixObserver(max_bytes=4)
        b=pack()
        self.assertEqual(o.forward(b,lambda x:x,**S),b)
        self.assertEqual(o.stats()["skipped"],1)
    def test_capacity_cap(self):
        o=PrefixObserver(max_entries=2)
        for i in range(20): o.forward(pack(sys=str(i)),lambda x:x,**S)
        self.assertLessEqual(len(o._seen),2)
    def test_no_plaintext_stored(self):
        canary="VERY_PRIVATE_CANARY"
        self.send(pack(sys=canary))
        self.assertNotIn(canary,repr(self.o._seen))
        self.assertNotIn(canary,repr(self.o.stats()))
    def test_transport_error_not_hidden(self):
        with self.assertRaisesRegex(ValueError,"transport down"):
            self.o.forward(pack(),lambda x: (_ for _ in ()).throw(ValueError("transport down")),**S)
    def test_original_whitespace_preserved(self):
        b=b'{ "messages" : [ {"role":"system","content":"S"} ], "model":"m" }'
        self.assertEqual(self.send(b),b"reply:"+b);self.assertEqual(self.sent,[b])
    def test_fuzz_wire_identical_250(self):
        rng=random.Random(2401)
        for i in range(250):
            b=pack(sys="S"+str(rng.randrange(4)),usr="U"+str(i))
            self.assertEqual(self.send(b),b"reply:"+b)
            self.assertEqual(self.sent[-1],b)
        self.assertEqual(self.o.stats()["requests"],250)

if __name__=="__main__": unittest.main()
