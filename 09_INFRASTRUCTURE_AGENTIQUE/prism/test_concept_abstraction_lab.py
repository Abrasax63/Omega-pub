"""Exact bounded abstraction tests. No network, LLM, or source truth claims."""
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from concept_abstraction_lab import (
    AUTO_TASK, analyze, as_relation, bounded_witness, check_axioms,
    from_library, invariance_check,
)
from incremental_math_library import append_candidate


def specimen(name, edges, kind="edges", nodes=None):
    if nodes is None:
        nodes=["a","b","c"]
    if kind == "matrix":
        pairs={tuple(p) for p in edges}
        representation={"kind":"matrix",
                        "matrix":[[(a,b) in pairs for b in nodes]
                                  for a in nodes]}
    else:
        representation={"kind":"edges","edges":edges}
    return {"concept_id":name,"universe":nodes,
            "representation":representation}


def equivalence(name="example-equivalence",kind="edges"):
    return specimen(name,
        [["a","a"],["b","b"],["c","c"],["a","b"],["b","a"]], kind)


def order(name="example-order",kind="edges"):
    return specimen(name, [
        ["a","a"],["b","b"],["c","c"],
        ["a","b"],["b","c"],["a","c"]],kind)


def source_row(cid, name):
    return {
        "schema_version": 1, "record_type":"EDUCATIONAL_RESEARCH_CANDIDATE",
        "candidate_id":cid,
        "topic_chosen_by_model":name,
        "sources":[{"page_id":int(cid[-1])+1,"revision_id":72}],
        "model_output_raw":"candidate only",
        "verification":{"verbatim_source_quote_valid":True,
                        "semantic_fidelity":"NOT_VERIFIED"},
        "interpretation_candidate":{"concept":name,
                                    "definition":"Tentative mathematical description."},
        "publication_level":"QUARANTINE_ONLY",
    }


class FiniteAbstractionTests(unittest.TestCase):
    def test_intersection_forms_more_general_finite_axioms(self):
        result=analyze([equivalence(),order()])
        self.assertIn("reflexive",result["common_axioms_on_inputs"])
        self.assertIn("transitive",result["common_axioms_on_inputs"])
        self.assertIn("serial",result["common_axioms_on_inputs"])
        self.assertNotIn("symmetric",result["common_axioms_on_inputs"])
        self.assertNotIn("antisymmetric",result["common_axioms_on_inputs"])
        self.assertIn("symmetric",result["distinguishing_axioms"]["example-equivalence"])
        self.assertIn("antisymmetric",result["distinguishing_axioms"]["example-order"])
        self.assertTrue(result["bounded_models_showing_weaker_definition"]["example-equivalence"])
        self.assertTrue(result["bounded_models_showing_weaker_definition"]["example-order"])
        self.assertFalse(result["semantic_mapping_from_sources_verified"])
        self.assertEqual(result["theorems_certified"],0)

    def test_conjecture_stronger_than_shared_falsified_with_witness(self):
        result=analyze([equivalence(),order()],
                       proposed_axioms=["reflexive","symmetric"])
        self.assertEqual(result["model_proposal_status"],
                         "REFUTED_BY_INPUT_WITNESS")
        bad=result["model_proposal_counterexamples"]
        self.assertEqual(len(bad),1)
        self.assertEqual(bad[0]["violated_axiom"],"symmetric")
        self.assertEqual(bad[0]["concept_id"],"example-order")
        self.assertEqual(len(bad[0]["witness"]),2)

    def test_common_axioms_survive_change_of_representation(self):
        a=analyze([equivalence(),order()])
        b=analyze([equivalence(kind="matrix"),order(kind="matrix")])
        self.assertEqual(a["common_axioms_on_inputs"],b["common_axioms_on_inputs"])
        for record in b["input_fingerprints"]:
            self.assertEqual(record["representation_invariance"]["property_disagreements"],0)
            self.assertEqual(record["representation_invariance"]["label_permutations_checked"],6)
            self.assertTrue(record["representation_invariance"]["edge_matrix_roundtrip"])

    def test_independent_holdout_refutes_when_axioms_not_holding(self):
        good=specimen("diagonal",
            [["a","a"],["b","b"]], nodes=["a","b"])
        bad=specimen("not-reflexive",
            [["a","b"]],nodes=["a","b"])
        r=analyze([equivalence(),order()],holdout=[good,bad])
        self.assertEqual(r["shared_axioms_holdout_status"],"REFUTED_BY_HOLDOUT")
        self.assertTrue(r["holdout"][0]["passes_shared_axioms"])
        self.assertFalse(r["holdout"][1]["passes_shared_axioms"])
        self.assertTrue(any(x["axiom"]=="reflexive"
                            for x in r["holdout"][1]["violations"]))

    def test_no_holdout_does_not_imply_proof(self):
        r=analyze([equivalence(),order()],proposed_axioms=["transitive"])
        self.assertEqual(r["model_proposal_status"],"COMPATIBLE_ON_INPUTS_NOT_PROVED")
        self.assertEqual(r["shared_axioms_holdout_status"],"NOT_TESTED")
        self.assertEqual(r["publication_level"],"QUARANTINE_ONLY")

    def test_bounded_countermodel_is_exact_and_falsifies_extra_axiom(self):
        w=bounded_witness(["reflexive","transitive"],["symmetric"])
        self.assertIsNotNone(w)
        _,nodes,edges=as_relation({**w,"concept_id":"witness"})
        facts=check_axioms(nodes,edges)
        self.assertTrue(facts["reflexive"]["holds"])
        self.assertTrue(facts["transitive"]["holds"])
        self.assertFalse(facts["symmetric"]["holds"])

    def test_reject_vacuous_or_illformed_samples(self):
        invalid=[
            specimen("single",[],nodes=["a"]),
            specimen("duplicate",[],nodes=["a","a"]),
            specimen("edge-outside",[["a","z"]],nodes=["a","b"]),
            specimen("repeat",[["a","a"],["a","a"]],nodes=["a","b"]),
            {"concept_id":"X","universe":["a","b"],
             "representation":{"kind":"matrix","matrix":[[1,0],[0,1]]}},
            {"concept_id":"X","universe":["a","b"],
             "representation":{"kind":"matrix","matrix":[[True],[False]]}},
        ]
        for x in invalid:
            with self.subTest(value=x):
                with self.assertRaises(ValueError):
                    analyze([x,order()])
        with self.assertRaises(ValueError):
            analyze([equivalence(),equivalence()])
        with self.assertRaises(ValueError):
            analyze([equivalence(),order()],proposed_axioms=["made_up"])
        with self.assertRaises(ValueError):
            analyze([equivalence(),order()],proposed_axioms=["reflexive","reflexive"])

    def test_relabel_invariance_exhaustively_for_four_nodes(self):
        s=specimen("four",
            [["a","a"],["b","b"],["c","c"],["d","d"],
             ["a","b"],["b","c"],["a","c"]],
            nodes=["a","b","c","d"])
        _,nodes,edges=as_relation(s)
        proof=invariance_check(nodes,edges)
        self.assertEqual(proof["label_permutations_checked"],24)


class LlmLibraryBridgeTests(unittest.TestCase):
    def setUp(self):
        self.temp=TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.ledger=Path(self.temp.name)/"candidates.jsonl"
        append_candidate(self.ledger,source_row("id1","Untested A"))
        append_candidate(self.ledger,source_row("id2","Untested B"))

    def test_agent_selects_two_library_concepts_without_given_abstraction(self):
        outputs=[]
        def model(messages,max_tokens):
            outputs.append(messages)
            return {"text":json.dumps({
                "specimens":[equivalence("id1"),order("id2")],
                "proposed_axioms":["symmetric"],
                "rationale":"Potential shared concept, to be falsified."})}
        result=from_library(self.ledger,model_call=model)
        self.assertEqual(result["status"],
                         "STRUCTURAL_CHECKS_PASSED_SEMANTICS_UNVERIFIED")
        self.assertEqual(result["selected_candidate_ids"],["id1","id2"])
        self.assertEqual(result["analysis"]["model_proposal_status"],
                         "REFUTED_BY_INPUT_WITNESS")
        self.assertFalse(result["semantic_mapping_from_sources_verified"])
        self.assertFalse(result["analysis"]["semantic_mapping_from_sources_verified"])
        self.assertEqual(result["publication_level"],"QUARANTINE_ONLY")
        self.assertNotIn("example-equivalence",AUTO_TASK.lower())
        self.assertNotIn("preorder",AUTO_TASK.lower())
        self.assertIn("id1",outputs[0][1]["content"])
        self.assertIn("id2",outputs[0][1]["content"])

    def test_made_up_concept_ids_not_accepted(self):
        result=from_library(self.ledger,model_call=lambda *_:{"text":json.dumps({
            "specimens":[equivalence("id1"),order("invented")],
            "proposed_axioms":["reflexive"]})})
        self.assertEqual(result["status"],"INVALID_MODEL_SPECIMENS")
        self.assertNotIn("analysis",result)

    def test_abstention_is_not_patched_with_invented_examples(self):
        r=from_library(self.ledger,model_call=lambda *_:{"text":'{"abstain":true}'})
        self.assertEqual(r["status"],"MODEL_ABSTAINED_OR_INVALID_JSON")
        self.assertNotIn("analysis",r)

    def test_invalid_json_is_preserved_not_certified(self):
        r=from_library(self.ledger,model_call=lambda *_:{"text":"broken"})
        self.assertEqual(r["raw_model_output"],"broken")
        self.assertEqual(r["status"],"MODEL_ABSTAINED_OR_INVALID_JSON")
        self.assertEqual(r["theorems_certified"],0)

    def test_tampered_ledger_blocks_all_analysis(self):
        self.ledger.write_text(self.ledger.read_text().replace(
            "Untested A","Claimed theorem"),encoding="utf-8")
        with self.assertRaises(ValueError):
            from_library(self.ledger,model_call=lambda *_:
                         self.fail("Should fail before model"))

    def test_not_enough_entries_short_circuit(self):
        blank=Path(self.temp.name)/"blank.jsonl"
        r=from_library(blank,model_call=lambda *_:
                       self.fail("Should not call the model"))
        self.assertEqual(r["status"],"INSUFFICIENT_GROUNDED_LIBRARY_CANDIDATES")


if __name__=="__main__":
    unittest.main()
