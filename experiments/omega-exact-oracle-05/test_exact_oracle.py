"""Fourteen pre-holdout guards. Compare the oracle with independent brute force."""
from functools import lru_cache
from itertools import product
import random
import unittest

import exact_oracle as e


def independent_brute(predictions, prices):
    """Independent search over ALL ordered questions and BOTH children.

    Intentionally no elision of equal partitions, no greedy upper bound, no
    Huffman lower bound and no calls to ExactOracle's internal methods.
    """
    n = len(predictions)
    full = frozenset(range(n))

    @lru_cache(None)
    def recurse(labels):
        if len(labels) == 1:
            return 0
        scores = []
        for q in range(len(prices)):
            children = [
                frozenset(i for i in labels if predictions[i][q] == bit)
                for bit in (0, 1)
            ]
            if not all(children):
                continue
            scores.append(len(labels) * prices[q] +
                          recurse(children[0]) + recurse(children[1]))
        if not scores:
            raise e.IndistinguishableError("UNOBSERVABLE_BY_MENU")
        return min(scores)
    return recurse(full)


class ExactOracleControls(unittest.TestCase):
    def test_01_preregistered_constants(self):
        self.assertEqual(e.PREREG_COMMIT, "dc02ab735e314b106868faa49b284fb4e77e4b9b")
        self.assertEqual((e.POOL_N, e.TEST_N, e.N_CANDIDATES, e.MAX_QUERIES),
                         (32, 24, 16, 12))
        self.assertEqual(e.TARIFFS, ((1, 5), (5, 1)))
        self.assertEqual(e.POLICIES, ("OPTIMUM", "PRICE_AWARE", "BALANCED"))

    def test_02_binary_code_length_lower_bound(self):
        self.assertEqual([e.code_length_numerator(k) for k in range(1,9)],
                         [0,2,5,8,12,16,20,24])

    def test_03_three_models_exact_vs_brute(self):
        words = [(0, 0), (1, 1)]
        output = [(0, 0), (0, 1), (1, 0)]
        oracle = e.ExactOracle(words, output, [1, 3])
        self.assertEqual(oracle.solve(), independent_brute(output, (1, 3)))
        self.assertEqual(oracle.solve(), 9)
        self.assertEqual(oracle.words[oracle.decision[oracle.full]], words[0])
        self.assertEqual(sum(x["cost"] for x in oracle.oracle_paths()),9)

    def test_04_reverse_prices_reverse_optimal_first_probe(self):
        words = [(0, 0), (1, 1)]
        output = [(0, 0), (0, 1), (1, 0)]
        oracle = e.ExactOracle(words, output, [3, 1])
        self.assertEqual(oracle.solve(), 9)
        self.assertEqual(oracle.words[oracle.decision[oracle.full]],words[1])

    def test_05_all_four_binary_words_independent_search(self):
        outputs = list(product((0,1), repeat=2))
        words = [(0,), (1,)]
        for price in ((1,1),(1,6),(5,1),(7,3)):
            oracle = e.ExactOracle(words, outputs, price)
            self.assertEqual(oracle.solve(), independent_brute(outputs, price))
            self.assertEqual(sum(x["cost"] for x in oracle.oracle_paths()),
                             oracle.solve())
            self.assertTrue(all(x["certified"] for x in oracle.oracle_paths()))

    def test_06_independent_brute_five_hypotheses_and_random_prices(self):
        words = [(x,) for x in range(4)]
        rows = [(0,0,0,0),(1,0,0,0),(0,1,0,0),
                (0,0,1,0),(0,0,0,1)]
        for seed in (1,4,17,42,57):
            prices = [random.Random(seed*10+i).randint(1,9)
                      for i in range(len(words))]
            oracle=e.ExactOracle(words,rows,prices)
            self.assertEqual(oracle.solve(),independent_brute(rows,prices))

    def test_07_permutes_hypothesis_ids_without_changing_cost(self):
        words=[(0,),(1,),(0,1),(1,0)]
        rows=[(0,0,0,0),(1,0,0,1),(0,1,0,1),(1,1,1,0),(0,0,1,1)]
        p=[2,5,3,2]
        first=e.ExactOracle(words,rows,p)
        shuffled=[rows[i] for i in (4,0,3,1,2)]
        second=e.ExactOracle(words,shuffled,p)
        self.assertEqual(first.solve(),second.solve())
        self.assertEqual(first.solve(),independent_brute(rows,p))

    def test_08_duplicates_and_complements_keep_cheapest(self):
        words=[(0,),(1,),(2,),(3,)]
        rows=[(0,1,0,1),(0,1,0,1),(1,0,1,0),(1,0,1,0)]
        # Deliberately ambiguous signatures should be rejected.
        with self.assertRaises(e.IndistinguishableError):
            e.ExactOracle(words,rows,[5,1,2,3])
        # Unique four-machine signatures with redundant complement columns.
        rows=[(0,0,1,1),(0,1,1,0),(1,0,0,1),(1,1,0,0)]
        oracle=e.ExactOracle(words,rows,[8,4,2,3])
        self.assertEqual(oracle.solve(),independent_brute(rows,[8,4,2,3]))
        self.assertEqual(oracle.solve(),20)

    def test_09_invalid_inputs_fail_closed(self):
        with self.assertRaises(ValueError):
            e.ExactOracle([(0,)],[(0,),(1,)],[0])
        with self.assertRaises(ValueError):
            e.ExactOracle([(0,)],[(0,),(9,)],[1])
        with self.assertRaises(ValueError):
            e.ExactOracle([(0,),(0,)],[(0,1),(1,0)],[1,2])

    def test_10_indistinguishable_signature_detected(self):
        with self.assertRaises(e.IndistinguishableError):
            e.ExactOracle([(0,),(1,)],[(0,0),(0,0)],[1,1])

    def test_11_observed_path_independent_of_true_model_at_choice(self):
        # The root choice and exact numerator are functions only of public rows.
        words=[(0,),(1,)]
        rows=[(0,0),(0,1),(1,0),(1,1)]
        oracle=e.ExactOracle(words,rows,[7,4])
        oracle.solve()
        chosen=oracle.words[oracle.decision[oracle.full]]
        self.assertEqual(chosen, (1,))
        self.assertEqual(len(set(x["hidden_index"] for x in oracle.oracle_paths())),4)
        self.assertEqual(oracle.solve(),independent_brute(rows,(7,4)))

    def test_12_previous_references_match_fixed_exposed_training_instance(self):
        space,_=e.s.enumerate_consistent_models(
            e.s.validate_observations(e.s.six_zero_observations()))
        oldpools,_,_,_=e.previous.fresh_pools(space,e.contrast.menu_words())
        row=e.previous.build_instances(oldpools["train"],1,0)[0]
        models=row["candidates"]
        words=e.contrast.menu_words()
        out=[[e.s.trace(m,w)[-1] for w in words] for m in models]
        price=[e.contrast.query_price(w,row["tariff"]) for w in words]
        oracle=e.ExactOracle(words,out,price)
        # No new holdout is inspected by the test.
        optimal=oracle.solve()
        ref=e.baseline_paths(models,words,row["tariff"],"PRICE_AWARE")
        self.assertLessEqual(optimal,sum(x["cost"] for x in ref))
        self.assertTrue(all(x["certified"] for x in ref))
        self.assertEqual(sum(x["cost"] for x in oracle.oracle_paths()),optimal)

    def test_13_new_pool_excludes_every_prior_cohort(self):
        space,_=e.s.enumerate_consistent_models(
            e.s.validate_observations(e.s.six_zero_observations()))
        menu=e.contrast.menu_words()
        try:
            pool,count,_=e.fresh_evaluation_pool(space,menu)
        except RuntimeError as error:
            # This is a legitimate falsification of the preregistered new
            # holdout: never silently reuse old models as "unseen".
            self.assertIn("INSUFFICIENT_NEW_MODELS",str(error))
            self.assertIn("eligible=",str(error))
            return
        old,_,_,_=e.previous.fresh_pools(space,menu)
        older,_,_=e.contrast.partition_models(space,menu)
        historical=set(sum((older[k] for k in ("train","calib","test")),[]))
        historical|=set(old["train"]+old["test"])
        self.assertFalse(set(pool)&historical)
        self.assertEqual(len(pool),32)
        self.assertGreaterEqual(count,32)
        self.assertEqual(len(set(pool)),32)

    def test_14_budget_and_regret_are_not_conflated(self):
        # A single hidden world may cost LESS than its uniform-prior optimum.
        words=[(0,),(1,)]
        rows=[(0,0),(0,1),(1,0)]
        oracle=e.ExactOracle(words,rows,[1,2])
        paths=oracle.oracle_paths()
        self.assertEqual(sum(x["cost"] for x in paths),oracle.solve())
        self.assertTrue(min(x["cost"] for x in paths)<oracle.solve()/3)


if __name__=="__main__":
    unittest.main()
