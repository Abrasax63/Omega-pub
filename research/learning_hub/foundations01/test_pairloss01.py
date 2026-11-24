import unittest
from pairloss01 import frozen_train,fresh_eval,families

class PairlossTests(unittest.TestCase):
    def test_frozen(self):
        self.assertEqual(len(families(frozen_train())),64)
    def test_fresh(self):
        rows=fresh_eval()
        self.assertEqual(len(rows),64)
        self.assertEqual(len(families(rows)),32)
        self.assertEqual(len({r["id"] for r in rows}),64)
