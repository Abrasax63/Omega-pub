import unittest
from finite_oracle11 import (
    validate_manual_claim_source, temporal_edges, components_unionfind,
    components_dfs, incidence_rank, constant_on_edges_count,
    direct_injective_histories, inclusion_exclusion, evaluate_exact
)


class V7ExactFiniteTests(unittest.TestCase):
    def test_manual_semantic_transcription_has_full_source_anchors(self):
        claims=validate_manual_claim_source()
        self.assertEqual(len(claims["claims"]),2)
        self.assertEqual(
            claims["status"],"HUMAN_TRANSCRIPTION_UNVERIFIED_NOT_AUTOMATIC_NLU"
        )
        self.assertTrue(all(c["source_line_anchors"] for c in claims["claims"]))

    def test_three_independent_codimension_oracles_on_triangle(self):
        t=(1,2,0)
        edges=temporal_edges(t,(0,1),3)
        self.assertEqual(len(edges),3)
        self.assertEqual(components_unionfind(3,edges),1)
        self.assertEqual(components_dfs(3,edges),1)
        self.assertEqual(incidence_rank(3,edges,2),2)
        self.assertEqual(incidence_rank(3,edges,3),2)
        self.assertEqual(constant_on_edges_count(3,edges,2),2)
        self.assertEqual(constant_on_edges_count(3,edges,3),3)

    def test_isolated_vertices_are_included_in_dimension(self):
        t=(0,1,2)
        edges=temporal_edges(t,(0,1),2)
        self.assertEqual(edges,frozenset({(0,1)}))
        self.assertEqual(components_unionfind(3,edges),2)
        self.assertEqual(components_dfs(3,edges),2)
        self.assertEqual(constant_on_edges_count(3,edges,3),9)

    def test_two_proofs_of_chromatic_count_disagree_with_naive_power(self):
        t=(0,1)
        self.assertEqual(direct_injective_histories(t,1,2),2)
        self.assertEqual(inclusion_exclusion(t,1,2),2)
        self.assertNotEqual(direct_injective_histories(t,1,2),2**2)
        self.assertEqual(direct_injective_histories(t,1,3),6)
        self.assertEqual(inclusion_exclusion(t,1,3),6)

    def test_singleton_boundary_including_q_one(self):
        self.assertEqual(direct_injective_histories((0,),1,1),1)
        self.assertEqual(inclusion_exclusion((0,),1,1),1)
        self.assertEqual(inclusion_exclusion((0,),3,3),3)

    def test_full_pre_registered_finite_audit(self):
        result=evaluate_exact()
        self.assertTrue(result["finite_test_success"])
        self.assertEqual(result["mathematical_mismatch_count"],0)
        self.assertEqual(result["number_of_total_maps_checked"],288)
        self.assertEqual(result["pair_horizon_graphs_checked"],4863)
        self.assertEqual(result["finite_field_coloring_count_checks"],9726)
        self.assertEqual(result["direct_vs_inclusion_exclusion_checks"],2592)
        self.assertEqual(len(result["deliberately_false_claims_refuted"]),3)
        self.assertFalse(result["manual_mapping_independently_semantically_adjudicated"])
        self.assertEqual(result["automatic_horn_rules_added"],0)


if __name__=="__main__":
    unittest.main()
