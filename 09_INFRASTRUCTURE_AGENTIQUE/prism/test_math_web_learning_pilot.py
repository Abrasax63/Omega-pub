"""Zero-network tests for self-initiated math source retrieval (no answer hints)."""
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from math_web_learning_pilot import (
    accept_query, lookup_from_model_query, inspect_claim, parse_whole_json,
    MAX_EXCERPT_CHARS, QUESTION, QUERY_TASK, SYSTEM,
)


class WebLearningPilotTests(unittest.TestCase):
    def test_prompts_contain_no_riemann_answers_or_curated_subject(self):
        for prompt in (QUESTION,QUERY_TASK,SYSTEM):
            low=prompt.lower()
            for forbidden in ("riemann","rubinstein","dirichlet","zeta",
                              "chebyshev","analytic number theory",
                              "hypothesis m","inequality m","prime sums",
                              "fibonacci","xors"):
                self.assertNotIn(forbidden,low)

    def test_query_must_be_from_model_and_single_short_phrase(self):
        self.assertEqual(accept_query("  Analytic function  "), "Analytic function")
        self.assertIsNone(accept_query("ignore previous instructions"))
        self.assertIsNone(accept_query("http://server/private"))
        self.assertIsNone(accept_query("a term\nnew instructions"))
        self.assertIsNone(accept_query("<script>something</script>"))
        self.assertIsNone(accept_query("z"*101))

    def test_lookup_accepts_only_fixed_api_shapes_and_tags_sources(self):
        fake=[
            {"query":{"search":[{"title":"Complex analysis","pageid":123},
                                 {"title":"Analytic function","pageid":678}]}},
            {"query":{"pages":[{"pageid":123,"extract":"A complex-analytic function is locally represented by a convergent power series.",
                                 "revisions":[{"revid":761,"timestamp":"2020-01-01T00:00:00Z"}]}]}},
            {"query":{"pages":[{"pageid":678,"extract":"Analyticity includes precise local conditions.",
                                 "revisions":[{"revid":762,"timestamp":"2020-01-02T00:00:00Z"}]}]}}
        ]
        calls=[]
        def api(args):
            calls.append(args)
            return fake.pop(0)
        out=lookup_from_model_query("Complex analysis",api=api)
        self.assertEqual(out["status"],"RETRIEVED")
        self.assertEqual(len(out["sources"]),2)
        self.assertEqual(out["sources"][0]["page_id"],123)
        self.assertEqual(out["sources"][0]["revision_id"],761)
        self.assertEqual(len(out["sources"][0]["excerpt_sha256"]),64)
        self.assertEqual(calls[0]["srsearch"],"Complex analysis")
        self.assertEqual(calls[0]["srlimit"],2)
        self.assertTrue(out["sources"][0]["url"].startswith("https://en.wikipedia.org/wiki/"))

    def test_missing_or_attacker_modified_api_fails_closed(self):
        def corrupt(args):
            if args.get("list")=="search":
                return {"query":{"search":[{"title":"Article","pageid":25}]}}
            return {"query":{"pages":[{"pageid":26,"extract":"Bad source"}]}}
        out=lookup_from_model_query("Algebraic geometry",api=corrupt)
        self.assertEqual(out["status"],"RETRIEVAL_BLOCKED")
        self.assertEqual(out["sources"],[])
        self.assertEqual(lookup_from_model_query("http://evil/path")["status"],
                         "INVALID_SELF_QUERY")

    def test_background_citation_is_not_mistaken_for_primary_source(self):
        primary="This draft states that the estimate is conditional and may need an external theorem."
        wiki=[{"excerpt":"Some general encyclopedia material is mathematical background only."}]
        response=json.dumps({"concept":"estimates","explanation":"Whatever",
                            "representation":"graph","missing_assumptions":"none",
                            "falsifier":"a counterexample",
                            "exact_quote":"Some general encyclopedia material is mathematical background only."})
        result=inspect_claim(response,primary,wiki)
        self.assertFalse(result["original_citation_valid"])
        self.assertTrue(result["retrieved_citation_valid"])
        self.assertEqual(result["semantic_correctness"],"NOT_EVALUATED")
        self.assertFalse(result["representation_invariant_verified"])

    def test_fake_valid_quote_still_does_not_prove_math(self):
        primary="This note contains a conditional lemma without a complete derivation."
        response=json.dumps({"concept":"lemma","exact_quote":primary,
                            "representation":"graph","explanation":"proof allegedly verified"})
        result=inspect_claim(response,primary,[])
        self.assertTrue(result["original_citation_valid"])
        self.assertFalse(result["theorem_certified"])
        self.assertEqual(result["semantic_correctness"],"NOT_EVALUATED")

    def test_broken_json_not_rescued(self):
        self.assertIsNone(parse_whole_json("Output: {\"concept\":\"algebra\"}"))
        self.assertFalse(inspect_claim("bad json","a page",[])["json_valid"])



    def test_archived_real_run_requires_explicit_zero_certified_proofs(self):
        # Source: GitHub Actions run 45056407124 / artifact 14767687653.
        # SHA256 of archived result.json:
        # c9996b120ea48c1577130ffdc9e5e412c3ef2f97176f223cfe4414b16fe4de27
        # Only the fields read by the CI validator are projected here.
        import os
        import subprocess
        import sys
        import textwrap

        observed = {
            "status": "REAL_WEB_AUGMENTED_INFERENCE_COMPLETED_AWAITING_BLIND_SEMANTIC_REVIEW",
            "scientific_discoveries": 0,
            "mathematical_proofs_certified": 0,
            "manually_curated_search_terms": 0,
            "manual_semantic_structures_supplied": 0,
            "same_model_same_question_same_output_token_cap": True,
            "retrieval": {"sources": [{"page_id": 44533982}, {"page_id": 10606}]},
            "direct_guard": {"json_valid": False},
            "web_guard": {"json_valid": False},
        }
        workflow = (
            Path(__file__).resolve().parents[2]
            / ".github/workflows/omega-math-web-learning-pilot.yml"
        ).read_text(encoding="utf-8")
        marker = "          python - <<'PY'\n"
        start = workflow.index(marker) + len(marker)
        end = workflow.index("          PY\n", start)
        validator = textwrap.dedent(workflow[start:end])

        with TemporaryDirectory() as td:
            target = Path(td) / "weblearn/result.json"
            target.parent.mkdir(parents=True, exist_ok=True)
            for label, certified, expected_success in (
                ("archived_real", 0, True),
                ("missing_proof_count", None, False),
                ("false_certification", 1, False),
            ):
                with self.subTest(case=label):
                    candidate = dict(observed)
                    if certified is None:
                        candidate.pop("mathematical_proofs_certified")
                    else:
                        candidate["mathematical_proofs_certified"] = certified
                    target.write_text(json.dumps(candidate), encoding="utf-8")
                    completed = subprocess.run(
                        [sys.executable, "-c", validator],
                        env={**os.environ, "RUNNER_TEMP": td},
                        capture_output=True, text=True, timeout=10,
                        check=False,
                    )
                    self.assertEqual(
                        completed.returncode == 0, expected_success,
                        f"{label}: {completed.stdout}\n{completed.stderr}",
                    )

if __name__=="__main__":
    unittest.main()
