"""Independent adversarial stress checks for recovered observer functions."""
import unittest

from legacy_representation_stress import (
    equivalence_class_count,exhaustive_reconfiguration_audit,
    independent_decision,partitions_as_equivalence_sets,
    scope_counterexample,witness_partition,
)


class LegacyObserverStressTests(unittest.TestCase):
    def test_four_state_900_cases_independently_match(self):
        report=exhaustive_reconfiguration_audit()
        self.assertEqual(report["partitions"],15)
        self.assertEqual(report["ordered_cases"],900)
        self.assertEqual(report["precommitted_W06_49_cases"],
                         {"keep":7,"replace":42})
        self.assertEqual(report["direct_target_baseline_feasible"],49)
        self.assertEqual(report["identity_check_baseline_changes"],42)
        self.assertEqual(report["gate_replacement_recommendations"],42)
        self.assertTrue(report["no_distinct_advantage_over_identity_check_baseline"])
        for cap,rows in report["counts_by_capacity"].items():
            self.assertEqual(sum(rows.values()),225,(cap,rows))
        expected={
            "1":{"keep":1,"replace":14,"infeasible":210},
            "2":{"keep":15,"refine":7,"replace":98,"infeasible":105},
            "3":{"keep":45,"refine":67,"replace":98,"infeasible":15},
            "4":{"keep":60,"refine":165},
        }
        self.assertEqual(report["counts_by_capacity"],expected)
        import json
        print("LEGACY_900_INDEPENDENT_CLASSIFICATION "+
              json.dumps(report["counts_by_capacity"],sort_keys=True))

    def test_equivalence_partition_generator_and_orthogonal_example(self):
        rels=partitions_as_equivalence_sets()
        self.assertEqual(len(rels),15)
        n2=[r for r in rels if equivalence_class_count(r)==2]
        self.assertEqual(len(n2),7)
        for r in rels:
            labels=witness_partition(r)
            relation=frozenset((i,j) for i in range(4) for j in range(4)
                               if labels[i]==labels[j])
            self.assertEqual(relation,r)
        def equiv(labels):
            return frozenset((i,j) for i in range(4) for j in range(4)
                             if labels[i]==labels[j])
        old=equiv([0,0,1,1])
        target=equiv([0,1,0,1])
        self.assertEqual(independent_decision(old,target,2),
                         ("replace",2,2,4))
        self.assertEqual(independent_decision(old,target,4),
                         ("refine",2,2,4))
        self.assertEqual(independent_decision(old,target,1),
                         ("infeasible",2,2,4))

    def test_partial_catalog_and_false_completeness(self):
        report=scope_counterexample()
        statuses=report["statuses"]
        self.assertEqual(statuses["honest_incomplete"],"closure_unknown")
        self.assertEqual(statuses["false_completeness_declaration"],
                         "closed_assuming_declared_probe_list")
        self.assertEqual(statuses["completed_catalog"],
                         "underinformative_relative_to_listed_probes")
        self.assertEqual(report["certificates_issued"],0)
        self.assertTrue(report["declared_exhaustive_is_unverified_assumption"])


if __name__=="__main__":
    unittest.main()
