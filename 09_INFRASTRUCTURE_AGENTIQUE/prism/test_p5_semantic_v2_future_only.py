"""Regression fixtures from two ALREADY SEEN public pilots; not blind validation."""
import unittest

from p5_semantic_v2_future_only import VERSION,extract

class V2PosthocFixtures(unittest.TestCase):
    def test_explicit_group_formats(self):
        self.assertEqual(extract("Groupe B avec un taux global de succès de 59%.","RATE")[0],"B")
        self.assertEqual(extract("Le groupe A présente le taux le plus élevé.","RATE")[0],"A")
        self.assertEqual(extract("Équipe A","RATE")[0],"A")
        self.assertEqual(extract("A","RATE")[0],"A")
        self.assertIsNone(extract("Groupe B puis groupe A a gagné.","RATE")[0])

    def test_numeric_claims_are_not_silently_corrected(self):
        self.assertEqual(extract("91 * 17 = 1517","MUL")[0],"1517")
        self.assertEqual(extract("64 * 3 = 192","MUL")[0],"192")
        self.assertEqual(extract("Elle vaut 280.","MUL")[0],"280")
        self.assertIsNone(extract("Il vaut 2 ou 5","MUL")[0])
        self.assertIsNone(extract("A","CRT")[0])

    def test_yes_no_and_ambiguity(self):
        self.assertEqual(extract("Oui, f est injective.","INJ")[0],"OUI")
        self.assertEqual(extract("Non, elle n'est pas injective.","INJ")[0],"NON")
        self.assertIsNone(extract("Oui, elle n'est pas injective.","INJ")[0])

    def test_marked_exploratory(self):
        self.assertEqual(VERSION,"P5-SEMANTIC-V2-POSTHOC-FUTURE-ONLY")

if __name__=="__main__":
    unittest.main()
