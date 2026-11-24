import unittest
from membership_curriculum import create,validate

class MembershipCurriculumTests(unittest.TestCase):
    def test_train(self):
        self.assertEqual(validate(create(20261129,"train"),"train"),
                         dict(examples=128,pairs=64,unique_graphs=128))
    def test_eval_fixture(self):
        self.assertEqual(validate(create(55,"eval"),"eval"),
                         dict(examples=64,pairs=32,unique_graphs=64))
    def test_label_mutation(self):
        r=create(55,"eval");r[0]["label"]=not r[0]["label"]
        with self.assertRaisesRegex(ValueError,"LABEL"): validate(r,"eval")
    def test_missing(self):
        with self.assertRaises(ValueError): validate(create(55,"eval")[:-1],"eval")
