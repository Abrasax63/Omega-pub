"""Read-only durable memory checks; no simulated model output is scientific truth."""
import json
import sys
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/"external_memory01"))
from publisher import append_verified,verify_ledger,canonical
from read_memory import ScientificMemoryReader


class PersistentMemoryTests(unittest.TestCase):
    def setUp(self):
        self.dir=TemporaryDirectory()
        self.addCleanup(self.dir.cleanup)
        self.path=Path(self.dir.name)
        self.good={
            "record_type":"EXTERNAL_SOURCE_PAIR_PROVENANCE",
            "status":"SOURCE_BYTES_AND_PAIRING_VERIFIED",
            "source_id":11,"source_url":"https://github.com/example/at-pinned-commit",
            "source_blob":"a"*40,
            "lean_contains_sorry":True,
            "lean_proof_compiled_locally":False,
            "semantic_equivalence_certified":False
        }
        records=append_verified([],[
            self.good,
            {"id":"EXT01-ARITH-N99","status":"FINITE_ENUMERATION_VERIFIED",
             "checked_cases":5,"universal_theorem_certified":False},
        ],run_id=123)
        self.path.joinpath("verified_ledger.jsonl").write_text(
            "".join(canonical(x).decode("utf8")+"\n" for x in records),encoding="utf8")
        self.index={
            **verify_ledger(records),
            "llm_predictions_in_verified_memory":0,
            "scientific_semantic_fidelity":"NOT_VERIFIED"
        }
        self.path.joinpath("index.json").write_text(json.dumps(self.index),encoding="utf8")

    def test_replay_and_scoped_source_lookup(self):
        reader=ScientificMemoryReader(self.path)
        self.assertEqual(reader.verified_source(11)["source_blob"],"a"*40)
        self.assertFalse(reader.verified_source(11)["semantic_equivalence_certified"])
        self.assertEqual(reader.independent_checks()[0]["checked_cases"],5)
        self.assertEqual(reader.metadata()["validated_count"],2)

    def test_unknown_source_must_not_be_invented(self):
        reader=ScientificMemoryReader(self.path)
        with self.assertRaises(KeyError):reader.verified_source(99)

    def test_tampered_index_is_rejected(self):
        index=dict(self.index)
        index["head_sha256"]="0"*64
        self.path.joinpath("index.json").write_text(json.dumps(index),encoding="utf8")
        with self.assertRaisesRegex(ValueError,"INDEX_DOES_NOT_MATCH"):
            ScientificMemoryReader(self.path)

    def test_unverified_llm_claim_rejected_even_with_matching_hash(self):
        index=dict(self.index)
        index["scientific_semantic_fidelity"]="PROVED"
        self.path.joinpath("index.json").write_text(json.dumps(index),encoding="utf8")
        with self.assertRaisesRegex(ValueError,"SEMANTIC_CERTIFICATION"):
            ScientificMemoryReader(self.path)


if __name__=="__main__":unittest.main()
