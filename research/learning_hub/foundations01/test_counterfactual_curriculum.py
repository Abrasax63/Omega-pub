import unittest
from counterfactual_curriculum import create,validate

class CounterfactualTests(unittest.TestCase):
    def test_train(self):
        r=create(20261127,"train")
        self.assertEqual(validate(r,"train"),dict(rows=128,families=16,unique_graphs=128))
    def test_eval_fixture(self):
        r=create(81,"eval")
        self.assertEqual(validate(r,"eval"),dict(rows=64,families=8,unique_graphs=64))
    def test_incomplete(self):
        with self.assertRaises(ValueError):
            validate(create(81,"eval")[:-1],"eval")
