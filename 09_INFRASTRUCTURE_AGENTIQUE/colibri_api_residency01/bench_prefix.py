"""Synthetic prefix exposure, NOT measured saved FLOPs/tokens."""
import json
from prefix_observer import PrefixObserver
O=PrefixObserver()
S=dict(tenant="A",authorization_scope="mock",endpoint="mock",
       model_revision="rev1",template_revision="template1")
calls=0
for i in range(12):
    b=json.dumps(dict(model="m",max_tokens=32,temperature=0,messages=[
        dict(role="system",content="stable scientific extraction rules"),
        dict(role="user",content="document-"+str(i))])).encode()
    def send(original):
        global calls
        calls+=1
        return b"reply:"+original
    assert O.forward(b,send,**S)==b"reply:"+b
assert calls==12
print("SYNTHETIC; no model or API")
print("Original requests forwarded unmodified: 12/12")
print("Actual network/model calls avoided: 0")
print("Observed overlapping message prefixes:",O.stats())
print("Saved KV-prefill tokens/compute/energy: UNKNOWN")
