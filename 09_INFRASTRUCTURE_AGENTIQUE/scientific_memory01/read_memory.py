"""Read-only verified scientific memory for future Omega cycles.

All records are tied to an executed source run and a SHA256 append-only ledger.
This reader can answer which *scoped* checks were done, not whether the
external Lean reference was compiled or understood by a language model.
"""
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT.parent/"external_memory01"))
from publisher import load_jsonl,verify_ledger


class ScientificMemoryReader:
    def __init__(self,base_path=None):
        self.base=Path(base_path) if base_path is not None else ROOT
        self.ledger=load_jsonl(self.base/"verified_ledger.jsonl")
        state=verify_ledger(self.ledger)
        self.index=json.loads((self.base/"index.json").read_text(encoding="utf-8"))
        if self.index.get("head_sha256")!=state["head_sha256"] or self.index.get("validated_count")!=state["validated_count"]:
            raise ValueError("DURABLE_MEMORY_INDEX_DOES_NOT_MATCH_LEDGER")
        if self.index.get("llm_predictions_in_verified_memory")!=0:
            raise ValueError("LLM_RESULT_SILENTLY_PROMOTED")
        if self.index.get("scientific_semantic_fidelity")!="NOT_VERIFIED":
            raise ValueError("UNSUPPORTED_SEMANTIC_CERTIFICATION")
        self.state=state

    def verified_source(self,source_id):
        """Only byte-integrity and original source pairing, never semantic truth."""
        matches=[row["observation"] for row in self.ledger
                 if row["observation"].get("record_type")=="EXTERNAL_SOURCE_PAIR_PROVENANCE"
                 and row["observation"].get("source_id")==source_id]
        if len(matches)!=1:
            raise KeyError("PINNED_EXTERNAL_SOURCE_NOT_FOUND_OR_AMBIGUOUS")
        return dict(matches[0])

    def independent_checks(self):
        return tuple(row["observation"] for row in self.ledger
                     if row["observation"].get("status") in (
                         "FINITE_ENUMERATION_VERIFIED",
                         "EISENSTEIN_PREMISES_ARITHMETICALLY_VERIFIED"))

    def benchmark(self):
        return tuple(row["observation"] for row in self.ledger
                     if row["observation"].get("record_type")=="MODEL_BENCHMARK_MEASUREMENT")

    def metadata(self):
        return dict(self.state)


if __name__=="__main__":
    obj=ScientificMemoryReader()
    print(json.dumps({"memory":obj.metadata(),
                      "scoped_independent_checks":obj.independent_checks(),
                      "benchmark":obj.benchmark(),
                      "no_unverified_llm_promotion":True},indent=2))
