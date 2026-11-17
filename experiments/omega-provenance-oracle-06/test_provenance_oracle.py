"""14 pre-holdout tests, including a separately written exhaustive oracle."""
from functools import lru_cache
from itertools import combinations
from unittest.mock import patch
import random
import unittest

import provenance_oracle as p


def independent_exhaustive(worlds, pairs, costs):
    """Brute force all available first tests without using ProvenanceOracle."""
    verdict = tuple(len(set(row)) >= 3 for row in worlds)
    bits = tuple(tuple(int(row[a] == row[b]) for a,b in pairs)
                 for row in worlds)

    @lru_cache(None)
    def go(remaining):
        current = list(remaining)
        if len({verdict[i] for i in current}) == 1:
            return 0
        candidates = []
        for k in range(len(pairs)):
            left = tuple(i for i in current if bits[i][k] == 0)
            right = tuple(i for i in current if bits[i][k] == 1)
            if left and right:
                candidates.append(len(current)*costs[k] + go(left) + go(right))
        if not candidates:
            raise p.Unresolved("UNRESOLVED_NOT_CERTIFIED")
        return min(candidates)
    return go(tuple(range(len(worlds))))


def recanon(values):
    mapping={}
    return tuple(mapping.setdefault(x,len(mapping)) for x in values)


class ProvenanceOracleControls(unittest.TestCase):
    def test_01_frozen_preregistered_protocol(self):
        self.assertEqual(p.PREREG_COMMIT,
                         "ce03dc1af00af9521a3ca7ddc80993d2718d5091")
        self.assertEqual(p.THRESHOLD,3)
        self.assertEqual(len(p.CALIBRATION_CASES),12)
        self.assertEqual(p.HOLDOUT_CASES,tuple(range(100,124)))
        self.assertEqual(set(p.CALIBRATION_CASES)&set(p.HOLDOUT_CASES),set())

    def test_02_exactly_fifteen_canonical_equivalence_partitions(self):
        self.assertEqual(len(p.PARTITIONS),15)
        self.assertEqual(len(set(p.PARTITIONS)),15)
        self.assertEqual(sum(p.certified_goal(x) for x in p.PARTITIONS),7)
        self.assertEqual(sum(not p.certified_goal(x) for x in p.PARTITIONS),8)
        self.assertEqual(len(p.QUESTION_PAIRS),6)
        self.assertEqual(len(set(p.QUESTION_PAIRS)),6)

    def test_03_independent_brute_force_vs_dp_on_2_to_5_worlds(self):
        indexes=[0,1,2,3,4,6,8,10,12,14]
        for seed in range(12):
            rng=random.Random(seed+92001)
            for n in (2,3,4,5):
                chosen=rng.sample(indexes,n)
                worlds=[p.PARTITIONS[i] for i in chosen]
                costs=[rng.randint(1,12) for _ in p.QUESTION_PAIRS]
                exact=p.ProvenanceOracle(worlds,p.QUESTION_PAIRS,costs)
                expected=independent_exhaustive(worlds,p.QUESTION_PAIRS,costs)
                self.assertEqual(exact.solve(),expected)
                paths=exact.all_paths("EXACT_VERDICT_ORACLE")
                self.assertEqual(sum(x["total_price"] for x in paths),expected)

    def test_04_all_fifteen_candidates_brute_force(self):
        for costs in ([1]*6,[1,3,5,7,9,11],[11,9,7,5,3,1]):
            exact=p.ProvenanceOracle(costs=costs)
            self.assertEqual(exact.solve(),
                             independent_exhaustive(p.PARTITIONS,p.QUESTION_PAIRS,costs))
            self.assertEqual(sum(x["total_price"] for x in
                    exact.all_paths("EXACT_VERDICT_ORACLE")),exact.solve())

    def test_05_all_four_policies_certify_each_of_fifteen_worlds(self):
        o=p.ProvenanceOracle(costs=(2,3,4,5,6,7))
        for arm in p.ACTIONS:
            paths=o.all_paths(arm)
            self.assertEqual(len(paths),15)
            self.assertTrue(all(x["status"]=="CERTIFIED" for x in paths))
            self.assertTrue(all(x["queries_paid"]<=6 for x in paths))
            self.assertTrue(all(x["verdict_at_least_three_origins"]==
                                (x["actual_distinct_origins"]>=3) for x in paths))
            self.assertGreater(sum(x["total_price"] for x in paths),0)

    def test_06_no_query_needed_when_all_worlds_agree(self):
        worlds=[x for x in p.PARTITIONS if not p.certified_goal(x)]
        oracle=p.ProvenanceOracle(worlds,costs=[3]*6)
        self.assertEqual(oracle.solve(),0)
        self.assertEqual(oracle.all_paths("EXACT_VERDICT_ORACLE")[0]["queries_paid"],0)

    def test_07_indistinguishability_reports_failure(self):
        worlds=((0,1,0,1),(0,1,2,3))
        oracle=p.ProvenanceOracle(worlds,((0,1),),(5,))
        with self.assertRaises(p.Unresolved):
            oracle.solve()

    def test_08_corrupted_paid_response_fails_closed(self):
        o=p.ProvenanceOracle()
        hidden=p.PARTITIONS[6]
        def counterfeit(world, question):
            return 1-p.paid_same_execution_origin(world,question)
        with self.assertRaises(AssertionError):
            o.episode(6,"CHEAP_FIRST",paid_probe=counterfeit)

    def test_09_bad_paid_response_types_fail(self):
        o=p.ProvenanceOracle()
        with self.assertRaises(AssertionError):
            o.episode(0,"CHEAP_FIRST",paid_probe=lambda world,q: 9)
        with self.assertRaises(AssertionError):
            o.episode(0,"CHEAP_FIRST",paid_probe=lambda world,q: True)

    def test_10_nonpositive_cost_or_invalid_pairs_fail(self):
        with self.assertRaises(ValueError):
            p.ProvenanceOracle(costs=[1,0,3,4,5,6])
        with self.assertRaises(ValueError):
            p.ProvenanceOracle(pairs=((0,1),(0,1)),costs=(1,2))
        with self.assertRaises(ValueError):
            p.ProvenanceOracle(pairs=((0,0),),costs=(1,))
        with self.assertRaises(ValueError):
            p.ProvenanceOracle(partitions=((0,1,1,1),(0,1,1,1)))

    def test_11_relabeling_evidence_items_preserves_optimum(self):
        costs=(2,5,1,8,4,11)
        original=p.ProvenanceOracle(costs=costs).solve()
        order=(2,0,3,1)
        worlds=[recanon(tuple(row[i] for i in order)) for row in p.PARTITIONS]
        new_cost=[]
        for i,j in p.QUESTION_PAIRS:
            oldpair=tuple(sorted((order[i],order[j])))
            new_cost.append(costs[p.QUESTION_PAIRS.index(oldpair)])
        reordered=p.ProvenanceOracle(worlds,p.QUESTION_PAIRS,new_cost)
        self.assertEqual(reordered.solve(),original)

    def test_12_paid_probes_not_repeated_and_belief_never_loses_truth(self):
        o=p.ProvenanceOracle(costs=[4,7,2,9,1,5])
        for arm in p.ACTIONS:
            for result in o.all_paths(arm):
                seen=set()
                active=set(range(15))
                for row in result["log"]:
                    question=tuple(row["question"])
                    self.assertNotIn(question,seen)
                    seen.add(question)
                    self.assertEqual(set(row["belief_before"]),active)
                    active={i for i in active if
                        p.paid_same_execution_origin(p.PARTITIONS[i],question)==
                        row["answer_same_origin"]}
                    self.assertEqual(set(row["belief_after"]),active)
                    self.assertIn(result["hidden_index"],active)
                self.assertEqual(set(result["remaining_hypotheses"]),active)

    def test_13_tariffs_are_reproducible_but_not_filtered(self):
        self.assertEqual(p.priced_questions(0),p.priced_questions(0))
        self.assertEqual(p.priced_questions(100),p.priced_questions(100))
        self.assertTrue(all(len(p.priced_questions(i))==6 for i in p.CALIBRATION_CASES))
        self.assertTrue(all(1<=x<=12 for i in p.CALIBRATION_CASES
                            for x in p.priced_questions(i)))
        self.assertNotEqual(p.priced_questions(1),p.priced_questions(2))
        with self.assertRaises(ValueError):
            p.priced_questions(-1)

    def test_14_calibration_only_and_frozen_status_formula(self):
        # Only 0..11 are evaluated by this test; never holdout 100..123.
        report=p.conduct("calibration")
        self.assertEqual(report["mode"],"calibration")
        self.assertEqual(report["case_ids"],list(range(12)))
        self.assertEqual(len(report["trials"]),12)
        self.assertEqual(report["summary"]["cases"],12)
        self.assertFalse(report["trained_policies"])
        for case in report["trials"]:
            vals=case["cost_sums_all_15_partitions"]
            self.assertLessEqual(vals["EXACT_VERDICT_ORACLE"],min(vals.values()))


if __name__=="__main__":
    unittest.main()
