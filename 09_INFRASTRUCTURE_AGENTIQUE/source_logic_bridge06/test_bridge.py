import copy
import json
import tempfile
import unittest
from pathlib import Path

from bridge import (
    BridgeError, RULES_PATH, RULES_BLOB, SOURCES_DIR,
    assess, check_proof, discover, git_blob, load_bridge, run,
    safe_read, validate_rules,
)
from evaluate import evaluate, load_frozen, INPUT, GOLD, INPUT_BLOB, GOLD_BLOB


class SourceLogicBridgeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.docs, cls.by_source = load_bridge()
        cls.query_list = load_frozen(INPUT, INPUT_BLOB)["queries"]
        cls.queries = {q["id"]: q for q in cls.query_list}
        cls.rule_manifest = json.loads(RULES_PATH.read_text(encoding="utf-8"))

    def test_source_discovery_without_id_table(self):
        self.assertEqual(len(self.docs), 5)
        self.assertEqual(len(self.by_source), 4)
        self.assertIn("BR-OBS-CAP-01", self.docs)
        self.assertNotIn("BR-OBS-CAP-01", self.by_source)
        self.assertEqual(len(self.rule_manifest["rules"]), 12)
        self.assertEqual(git_blob(RULES_PATH.read_bytes()), RULES_BLOB)

    def test_inventory_auto_discovers_sixth_new_math_card(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            for source in SOURCES_DIR.glob("*.md"):
                (root / source.name).write_bytes(source.read_bytes())
            (root / "additional.md").write_text(
                "# BR-NOVEL-99 — card never in code\n\n## Hypothèses\nUnknown.\n",
                encoding="utf-8",
            )
            cards = discover(root)
            self.assertEqual(len(cards), 6)
            self.assertIn("BR-NOVEL-99", cards)

    def test_missing_or_unannotated_source_always_abstains(self):
        q = self.queries["Q14"]
        answer = assess(q, self.docs, self.by_source)
        self.assertEqual(answer["verdict"], "ABSTAIN")
        self.assertEqual(answer["reason"], "SOURCE_UNANNOTATED")
        other = {**q, "source_id": "BR-NOVEL-99"}
        self.assertEqual(assess(other, self.docs, self.by_source)["reason"],
                         "SOURCE_NOT_IN_CHECKOUT")

    def test_multihop_derived_negation_cites_each_source_step(self):
        q = self.queries["Q05"]
        answer = assess(q, self.docs, self.by_source)
        self.assertEqual(answer["verdict"], "CONTRADICTED")
        self.assertEqual([r["rule_id"] for r in answer["proof"]],
                         ["desc-update", "desc-derive"])
        self.assertTrue(check_proof(q, answer, self.docs, self.by_source))
        for step in answer["proof"]:
            self.assertEqual(step["source_id"], "BR-DESC-01")
            self.assertEqual(step["interpretation_status"],
                             "HUMAN_TRANSCRIPTION_UNVERIFIED")
            line = self.docs["BR-DESC-01"]["lines"][step["line"]-1].strip()
            self.assertEqual(step["excerpt"], line)

    def test_missing_hypotheses_and_no_inversion(self):
        q = self.queries["Q02"]
        ans = assess(q, self.docs, self.by_source)
        self.assertEqual(ans["verdict"], "ABSTAIN")
        self.assertIn("total_actions", ans["missing_assumptions"])
        cap = assess(self.queries["Q09"], self.docs, self.by_source)
        self.assertIn("independent_selection", cap["missing_assumptions"])
        # No claim of minimum cardinality from merely minimal by inclusion.
        tree = assess(self.queries["Q13"], self.docs, self.by_source)
        self.assertEqual(tree["verdict"], "ABSTAIN")
        self.assertEqual(tree["proof"], [])

    def test_negative_claim_needs_explicit_provenance(self):
        q = self.queries["Q10"]
        ans = assess(q, self.docs, self.by_source)
        self.assertEqual(ans["verdict"], "CONTRADICTED")
        self.assertEqual([r["rule_id"] for r in ans["proof"]],
                         ["cap-global-limit"])
        self.assertTrue(check_proof(q, ans, self.docs, self.by_source))

    def test_inconsistent_contract_yields_abstain_not_false_proof(self):
        new_map = copy.deepcopy(self.by_source)
        contradictory = copy.deepcopy(new_map["BR-ACC-01"][0])
        contradictory["rule_id"] = "access-opposite"
        contradictory["conclusion"] = "not:factor_language_equals_access_closure"
        new_map["BR-ACC-01"].append(contradictory)
        ans = assess(self.queries["Q01"], self.docs, new_map)
        self.assertEqual(ans["verdict"], "ABSTAIN")
        self.assertEqual(ans["reason"], "CONFLICTING_ANNOTATED_DERIVATIONS")
        self.assertEqual(ans["proof"], [])

    def test_changed_blob_rejected_before_logic(self):
        d = copy.deepcopy(self.docs)
        d["BR-ACC-01"]["blob"] = "0" * 40
        with self.assertRaisesRegex(BridgeError, "stale source blob"):
            validate_rules(self.rule_manifest, d)

    def test_quote_hallucination_rejected_before_logic(self):
        m = copy.deepcopy(self.rule_manifest)
        m["rules"][0]["anchor"] = "a fabricated theorem not present in source"
        with self.assertRaisesRegex(BridgeError, "anchor absent"):
            validate_rules(m, self.docs)

    def test_bare_axiom_promotion_rejected(self):
        m = copy.deepcopy(self.rule_manifest)
        m["rules"][0]["premises"] = []
        with self.assertRaisesRegex(BridgeError, "assumption-free"):
            validate_rules(m, self.docs)

    def test_invalid_or_duplicate_ids_rejected(self):
        m = copy.deepcopy(self.rule_manifest)
        m["rules"].append(copy.deepcopy(m["rules"][0]))
        with self.assertRaisesRegex(BridgeError, "duplicate or invalid rule"):
            validate_rules(m, self.docs)

    def test_no_user_self_assertion_as_certificate(self):
        q = copy.deepcopy(self.queries["Q01"])
        q["facts"].append(q["goal"])
        ans = assess(q, self.docs, self.by_source)
        self.assertEqual(ans["verdict"], "ABSTAIN")

    def test_cross_source_proofs_not_implicitly_shared(self):
        q = copy.deepcopy(self.queries["Q11"])
        q["source_id"] = "BR-ACC-01"
        self.assertEqual(assess(q, self.docs, self.by_source)["verdict"],
                         "ABSTAIN")

    def test_tampered_certificate_rejected(self):
        q = self.queries["Q01"]
        a = assess(q, self.docs, self.by_source)
        self.assertTrue(check_proof(q, a, self.docs, self.by_source))
        bad = copy.deepcopy(a)
        bad["proof"][0]["line"] += 1
        self.assertFalse(check_proof(q, bad, self.docs, self.by_source))

    def test_symlink_source_is_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            target = root / "source.md"
            target.write_text("# BR-SAFE-01\n", encoding="utf-8")
            (root / "bad.md").symlink_to(target)
            with self.assertRaises(BridgeError):
                discover(root)

    def test_structured_outputs_coherent_and_reproducible(self):
        a = evaluate()
        b = evaluate()
        self.assertEqual(a, b)
        self.assertEqual(a["cases"], 14)
        self.assertEqual(a["correct"], 14)
        self.assertEqual(a["confident_errors"], [])
        self.assertTrue(a["protocol_success"])
        self.assertTrue(a["all_certificates_valid"])
        self.assertTrue(a["fifth_unannotated_and_not_promoted"])
        self.assertTrue(a["multi_step_with_citations"])


if __name__ == "__main__":
    unittest.main()
