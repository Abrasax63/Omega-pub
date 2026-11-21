"""Real exact SEM22 verifier, synthetic 24-source fixture, no LLM inference."""
import hashlib
import importlib.util
import json
import sys
from pathlib import Path
from exact_verifier_cache import ExactVerifierCache

p=Path("/tmp/omega_sem22_checker.py")
s=importlib.util.spec_from_file_location("checker",p)
c=importlib.util.module_from_spec(s);sys.modules[s.name]=c;s.loader.exec_module(c)
def blob(x):return hashlib.sha1(b"blob "+str(len(x)).encode()+b"\x00"+x).hexdigest()

def fixture(i):
    n=5+i%16;a=(3*i+1)%n;b=(7*i)%n
    phrases=["Proposition : f est injective.","Proposition : f est surjective.",
             "Proposition : f possède au moins un point fixe.",
             "Proposition : pour tout x, f(f(x)) = x.",
             "Proposition : l'image de f contient exactement 2 éléments.",
             "Proposition : f possède exactement 0 point fixe.",
             "Proposition : f(f(0)) = 0."]
    raw=(f"# Fiche T{i}\n\n## Données\n\nOn travaille dans Z/{n}Z. On définit f(x) = ({a}*x + {b}) mod {n}.\n\n## Énoncé\n\n" + "\n".join(phrases) + "\n").encode("utf8")
    return raw

cache=ExactVerifierCache()
direct=[];candidate=[]
for raw,path in [(fixture(i),f"scientific/T{i}.md") for i in range(24)]*2:
    direct.append(c.verify_source(raw,expected_blob=blob(raw),source_path=path))
    candidate.append(cache.verify(raw,expected_blob=blob(raw),source_path=path,
                  verifier_revision="38b3f6250429901bb307cbea4d49dbcc9c8f6379",
                  verification_fn=c.verify_source))
assert direct==candidate
print("SEM22 pinned real deterministic verifier used on synthetic 24-case fixtures x2")
print("Uncached verifications:",len(direct))
print("With cache: actual verifications",cache.actual_verifications,"hits",cache.hits)
print("Output identity (Python object equality):",direct==candidate)
print("LLM calls, GPU FLOPs, monetary savings: NOT MEASURED")
