import hashlib
import importlib.util
import unittest
import sys
from pathlib import Path
from exact_verifier_cache import ExactVerifierCache

PINNED_REVISION="38b3f6250429901bb307cbea4d49dbcc9c8f6379"

def load_verifier():
    p=Path("/tmp/omega_sem22_checker.py")
    if not p.is_file():
        raise RuntimeError("missing pinned upstream SEM22 source")
    spec=importlib.util.spec_from_file_location("omega_sem22_checker",p)
    module=importlib.util.module_from_spec(spec)
    sys.modules[spec.name]=module
    spec.loader.exec_module(module)
    return module.verify_source

def blob(raw):
    return hashlib.sha1(b"blob "+str(len(raw)).encode()+b"\x00"+raw).hexdigest()

def fixture(i):
    modulus=5+i%16
    a=(i*3+1)%modulus
    b=(i*7)%modulus
    square="^2" if i%2 else ""
    claims=[
      "Proposition : f est injective.",
      "Proposition : f est surjective.",
      "Proposition : f possède au moins un point fixe.",
      "Proposition : pour tout x, f(f(x)) = x.",
      "Proposition : l'image de f contient exactement 2 éléments.",
      "Proposition : f possède exactement 0 point fixe.",
      "Proposition : f(f(0)) = 0.",
    ]
    s=(f"# Fiche T{i}\n\n## Données\n\nOn travaille dans Z/{modulus}Z. On définit f(x) = ({a}*x{square} + {b}) mod {modulus}.\n\n## Énoncé\n\n"
       +"\n".join(claims)+"\n")
    return s.encode("utf8")

class ExactVerifierReuseTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.fn=staticmethod(load_verifier())

    def run_one(self, cache, raw, source, revision=PINNED_REVISION, blob_override=None):
        return cache.verify(raw,expected_blob=blob_override or blob(raw),
                            source_path=source,verifier_revision=revision,
                            verification_fn=self.fn)

    def test_24_real_verifier_cases_byte_equal_results(self):
        cache=ExactVerifierCache()
        for i in range(24):
            raw=fixture(i)
            path=f"scientific/T{i}.md"
            direct=self.fn(raw,expected_blob=blob(raw),source_path=path)
            self.assertEqual(direct["status"],"EVALUATED_FINITE_SCOPE")
            self.assertEqual(len(direct["results"]),7)
            self.assertEqual(self.run_one(cache,raw,path),direct)
            self.assertEqual(self.run_one(cache,raw,path),direct)
        self.assertEqual(cache.actual_verifications,24)
        self.assertEqual(cache.hits,24)

    def test_changed_source_bytes_not_reused(self):
        c=ExactVerifierCache()
        self.run_one(c,fixture(1),"x")
        self.run_one(c,fixture(2),"x")
        self.assertEqual(c.actual_verifications,2)
    def test_changed_verifier_version_invalidates(self):
        c=ExactVerifierCache()
        self.run_one(c,fixture(1),"x")
        self.run_one(c,fixture(1),"x",revision="different-version")
        self.assertEqual(c.actual_verifications,2)
    def test_changed_source_path_invalidates(self):
        c=ExactVerifierCache()
        self.run_one(c,fixture(1),"x")
        self.run_one(c,fixture(1),"y")
        self.assertEqual(c.actual_verifications,2)
    def test_wrong_git_blob_rejected_each_time(self):
        c=ExactVerifierCache()
        for _ in range(2):
            with self.assertRaisesRegex(ValueError,"SOURCE_BLOB_MISMATCH"):
                self.run_one(c,fixture(1),"x",blob_override="0"*40)
        self.assertEqual(c.actual_verifications,2)
        self.assertEqual(c.hits,0)
    def test_unsupported_claims_keep_indeterminate(self):
        c=ExactVerifierCache()
        raw=fixture(2).replace(b"Proposition : f est injective.",b"Proposition : f is magical.")
        direct=self.fn(raw,expected_blob=blob(raw),source_path="bad")
        self.assertEqual(direct["results"][0]["verdict"],"INDETERMINATE")
        self.assertEqual(self.run_one(c,raw,"bad"),direct)
        self.assertEqual(self.run_one(c,raw,"bad"),direct)
    def test_cached_result_not_mutable(self):
        c=ExactVerifierCache()
        x=self.run_one(c,fixture(1),"x")
        x["status"]="CHANGED"
        self.assertNotEqual(self.run_one(c,fixture(1),"x")["status"],"CHANGED")
    def test_capacity_limited(self):
        c=ExactVerifierCache(capacity=2)
        for i in range(5): self.run_one(c,fixture(i),str(i))
        self.assertLessEqual(len(c._entries),2)
    def test_no_raw_content_in_cache(self):
        c=ExactVerifierCache()
        raw=fixture(3)
        self.run_one(c,raw,"s")
        self.assertNotIn(raw.decode(),repr(c._entries.keys()))

if __name__=="__main__": unittest.main()
