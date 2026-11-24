import unittest
import copy
import omega_hybrid_exact_sensor as sensor
from atomic_curriculum import create,validate
from teacher import admit
import json

class CurriculumTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.train=create(42,"train")
        cls.eval=create(43,"eval")
    def test_counts_and_sizes(self):
        self.assertEqual(validate(self.train,"train")["unique_graphs"],128)
        self.assertEqual(validate(self.eval,"eval")["unique_graphs"],64)
        self.assertEqual({len(r["packet"]["nodes"]) for r in self.train},{3,4})
        self.assertEqual({len(r["packet"]["nodes"]) for r in self.eval},{5,6})
    def test_labels_independent_sensor(self):
        for r in self.train+self.eval:
            self.assertEqual(r["label"],json.loads(admit(r["packet"],sensor)["target"]))
    def test_bad_label(self):
        rows=copy.deepcopy(self.train)
        rows[0]["label"]["xy"]=not rows[0]["label"]["xy"]
        with self.assertRaisesRegex(ValueError,"LABEL"):
            validate(rows,"train")
    def test_wrong_split(self):
        with self.assertRaises(ValueError):
            validate(self.train,"eval")
    def test_deterministic(self):
        self.assertEqual(self.train,create(42,"train"))
