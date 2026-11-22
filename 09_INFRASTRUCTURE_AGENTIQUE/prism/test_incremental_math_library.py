"""Network-free regression tests for the Omega incremental research library."""
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from incremental_math_library import (
    append_candidate, read_ledger, run, verify_records, validate_card,
)

SOURCE_A = ("A holomorphic function is complex differentiable at every "
            "point of an open subset of the complex plane.")
SOURCE_B = ("A convergent power series defines an analytic function "
            "throughout the interior of its circle of convergence.")


def source(page_id, revision, excerpt):
    from hashlib import sha256
    return {
        "title": "Sample entry " + str(page_id),
        "page_id": page_id, "revision_id": revision,
        "revision_timestamp": "2026-01-01T00:00:00Z",
        "url": "https://en.wikipedia.org/wiki/Sample_entry_" + str(page_id),
        "excerpt_sha256": sha256(excerpt.encode()).hexdigest(),
        "excerpt": excerpt,
    }


def card(topic, page_id, quote, gap=""):
    return json.dumps({
        "concept": topic, "definition": "Tentative definition.",
        "hypotheses": ["May require assumptions."],
        "relations": ["Other fields may be related."],
        "example": "Example remains to be independently verified.",
        "falsifier": "Search for a counterexample.",
        "exact_quote": quote, "source_page_id": page_id,
        "next_gap": gap, "uncertainty": "Unknown",
    })


class ScriptedModel:
    def __init__(self, responses):
        self.responses = list(responses)
        self.calls = []

    def __call__(self, messages, max_tokens):
        self.calls.append((messages, max_tokens))
        if not self.responses:
            raise AssertionError("Model called more often than expected")
        return {"text": self.responses.pop(0)}


class LibraryTests(unittest.TestCase):
    def setUp(self):
        self.temp = TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.ledger = Path(self.temp.name) / "library.jsonl"

    def test_two_autonomous_research_steps_and_append_only_provenance(self):
        model = ScriptedModel([
            "Analytic function",
            card("Analytic function", 42, SOURCE_A,
                 "Holomorphic function"),
            card("Holomorphic function", 43, SOURCE_B),
        ])
        queries = []
        def retrieve(query):
            queries.append(query)
            return {"status": "RETRIEVED", "sources": [
                source(42, 9, SOURCE_A) if len(queries) == 1
                else source(43, 10, SOURCE_B)
            ]}
        report = run("Unannotated mathematical research page",
                     self.ledger, max_hops=2, model_call=model,
                     retriever=retrieve)
        self.assertEqual(queries, ["Analytic function", "Holomorphic function"])
        self.assertEqual(report["stored"], 2)
        self.assertEqual(report["independent_math_verifications"], 0)
        self.assertEqual(report["stop_reason"], "RESEARCH_BUDGET_EXHAUSTED")
        records = read_ledger(self.ledger)
        self.assertEqual(len(records), 2)
        self.assertEqual(records[0]["verification"]["status"],
                         "CANDIDATE_CITED_UNVERIFIED")
        self.assertEqual(records[1]["previous_record_sha256"],
                         records[0]["record_sha256"])
        self.assertEqual(len(records[0]["sources"][0]["excerpt_sha256"]), 64)
        self.assertNotIn("excerpt", records[0]["sources"][0])
        self.assertIn("CC BY-SA", records[0]["sources"][0]["license"])
        self.assertFalse(records[1]["verification"]["mathematical_theorem_certified"])
        self.assertEqual(len(model.calls), 3)

    def test_exact_same_source_version_is_not_stored_twice(self):
        def retrieve(_):
            return {"status": "RETRIEVED", "sources": [source(42, 9, SOURCE_A)]}
        responses = ["Analytic function", card("Analytic function", 42, SOURCE_A)]
        first = run("New source text", self.ledger, max_hops=1,
                    model_call=ScriptedModel(responses), retriever=retrieve)
        second = run("New source text", self.ledger, max_hops=1,
                     model_call=ScriptedModel(responses), retriever=retrieve)
        self.assertEqual(first["stored"], 1)
        self.assertEqual(second["stored"], 0)
        self.assertEqual(second["stop_reason"], "EXACT_SOURCE_VERSION_ALREADY_STORED")
        self.assertEqual(len(read_ledger(self.ledger)), 1)

    def test_new_source_revision_is_a_new_version_not_overwrite(self):
        def retrieve(revision):
            return lambda _: {"status": "RETRIEVED",
                              "sources": [source(42, revision, SOURCE_A)]}
        outputs = ["Analytic function", card("Analytic function", 42, SOURCE_A)]
        run("Seed", self.ledger,  max_hops=1,
            model_call=ScriptedModel(outputs), retriever=retrieve(9))
        run("Seed", self.ledger, max_hops=1,
            model_call=ScriptedModel(outputs), retriever=retrieve(10))
        records = read_ledger(self.ledger)
        self.assertEqual(len(records), 2)
        self.assertNotEqual(records[0]["candidate_id"], records[1]["candidate_id"])

    def test_bad_json_preserved_but_never_promoted(self):
        model = ScriptedModel(["Analytic function", "not JSON at all"])
        out = run("Research question", self.ledger, model_call=model,
                  retriever=lambda _: {"status": "RETRIEVED",
                                       "sources": [source(42, 9, SOURCE_A)]})
        self.assertEqual(out["stored"], 1)
        self.assertEqual(out["stop_reason"], "UNSUPPORTED_CARD_QUARANTINED")
        record = read_ledger(self.ledger)[0]
        self.assertEqual(record["model_output_raw"], "not JSON at all")
        self.assertEqual(record["verification"]["semantic_fidelity"], "NOT_VERIFIED")
        self.assertEqual(record["publication_level"], "QUARANTINE_ONLY")
        self.assertFalse(record["verification"]["schema_valid"])

    def test_wrong_quote_or_wrong_page_id_quarantined(self):
        sources = [source(42, 9, SOURCE_A)]
        for output in (card("X", 41, SOURCE_A), card("X", 42, SOURCE_B)):
            _, guard = validate_card(output, sources)
            self.assertFalse(guard["verbatim_source_quote_valid"])
            self.assertEqual(guard["status"], "QUARANTINED_UNSUPPORTED_OR_INVALID")

    def test_ledger_mutation_fails_closed(self):
        run("Research question", self.ledger, max_hops=1,
            model_call=ScriptedModel(
                ["Analytic function", card("Analytic function", 42, SOURCE_A)]),
            retriever=lambda _: {"status": "RETRIEVED",
                                 "sources": [source(42, 9, SOURCE_A)]})
        old = self.ledger.read_text()
        self.ledger.write_text(old.replace("Analytic function",
                                          "False mathematics"), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "BROKEN_LIBRARY_HASH_CHAIN"):
            read_ledger(self.ledger)
        with self.assertRaisesRegex(ValueError, "BROKEN_LIBRARY_HASH_CHAIN"):
            append_candidate(self.ledger, {
                "candidate_id": "new", "publication_level": "QUARANTINE_ONLY"})
        self.assertIn("False mathematics", self.ledger.read_text())

    def test_research_budget_and_query_safety(self):
        with self.assertRaisesRegex(ValueError, "INVALID_RESEARCH_BUDGET"):
            run("Seed", self.ledger, max_hops=99)
        out = run("Seed", self.ledger,
                  model_call=ScriptedModel(["http://private/key"]),
                  retriever=lambda _: self.fail("Network must not be contacted"))
        self.assertEqual(out["stored"], 0)
        self.assertEqual(out["stop_reason"], "INVALID_SELF_QUERY")
        self.assertFalse(self.ledger.exists())

    def test_corrupt_trailing_line_cannot_be_ignored(self):
        self.ledger.write_text('{"a": 1}\n', encoding="utf-8")
        with self.assertRaises(ValueError):
            read_ledger(self.ledger)


if __name__ == "__main__":
    unittest.main()
