"""Development tests use ONLY prior eight public examples and synthetic controls.

No blind 12-source holdout file has been read or imported in these tests.
"""
import unittest
from structural_bridge import signature,score,match,guarded_proposal,MIN_SCORE,MIN_MARGIN


class BlindBridgeDevelopmentTests(unittest.TestCase):
    def test_math_polynomial_prior_experiment_11(self):
        nl="Prove that x^3 + 6x + 12 is irreducible in Q."
        a="theorem Artin_exercise_11_4_1b : Irreducible (12 + 6 * X + X ^ 3 : Polynomial ℚ) := by\n  sorry"
        b="theorem irrelevant: ¬ IsSimpleGroup G := by\n  sorry"
        out=match(nl,a,b)
        self.assertEqual(out["prediction"],"A")
        self.assertIn("irreducible",out["a"]["shared_features"])
        self.assertFalse(out["semantic_equivalence_certified"])

    def test_prior_group_simple_and_cardinality(self):
        nl="Prove that if |G|=1365 then G is not simple."
        correct="theorem someName {G : Type*} [Fintype G] [Group G] (hG : card G = 1365) : ¬ IsSimpleGroup G := by\n sorry"
        wrong="theorem other (p:ℝ) (h:p≤1) : ¬ Summable f := by\n sorry"
        self.assertEqual(match(nl,wrong,correct)["prediction"],"B")

    def test_prior_modular_divisibility(self):
        nl="Let p and q be distinct odd primes such that p-1 divides q-1. If (n,p q)=1, show that n^(q-1) ≡ 1 (mod p q)."
        correct="theorem num {p q n:ℕ} (hp:p.Prime) (h:p-1 ∣ q-1) (hn:n.gcd (p*q)=1) : n^(q-1) ≡ 1 [MOD p*q] := by\n sorry"
        wrong="theorem other : IsCompact K := by\n sorry"
        self.assertEqual(match(nl,correct,wrong)["prediction"],"A")

    def test_prior_integral_and_cosine(self):
        nl=r"Show that \int_{-\infty}^{\infty} \frac{\cos x}{x^2+a^2} dx = \pi e^{-a}/a for a > 0."
        correct="theorem x : Tendsto (fun y => ∫ x in -y..y, Real.cos x/(x^2+a^2)) atTop (𝓝 (Real.pi*(Real.exp (-a)/a))) := by\n sorry"
        wrong="theorem y : Irreducible (X + 1 : Polynomial ℚ) := by\n sorry"
        self.assertEqual(match(nl,wrong,correct)["prediction"],"B")

    def test_prior_linear_map_scalar(self):
        nl="Every linear map from one-dimensional vector space to itself is multiplication by some scalar."
        correct="theorem axler (T : V →ₗ[F] V) (hT:finrank F V=1): ∃ c:F,∀v:V,T v=c•v:= by\n sorry"
        wrong="theorem wrong : Continuous f := by\n sorry"
        self.assertEqual(match(nl,correct,wrong)["prediction"],"A")

    def test_none_and_no_overconfidence_from_shared_number(self):
        nl="An irreducible polynomial in Q of degree 1365"
        a="theorem irrelevant : card G = 1365 := by\n sorry"
        b="theorem other : Summable f := by\n sorry"
        self.assertEqual(match(nl,a,b)["prediction"],"NONE")
        self.assertEqual(match(nl,a,b)["status"],"UNSUPPORTED_ABSTAIN")

    def test_same_lean_text_is_ambiguous_not_fake_positive(self):
        nl="Prove that x^3 + 6x + 12 is irreducible."
        theorem="theorem nm : Irreducible (12 + 6 * X + X ^ 3 : Polynomial ℚ) := by\n sorry"
        r=match(nl,theorem,theorem)
        self.assertEqual(r["prediction"],"NONE")
        self.assertEqual(r["status"],"AMBIGUOUS_ABSTAIN")

    def test_theorem_identifier_not_a_source_id_shortcut(self):
        a="theorem Irreducible_Special_Source99 : ¬ IsSimpleGroup G := by\n sorry"
        b="theorem Name_11 : Irreducible (12 + 6*X + X^3 : Polynomial ℚ) := by\n sorry"
        nl="A polynomial is irreducible over Q."
        out=match(nl,a,b)
        self.assertEqual(out["prediction"],"B")

    def test_refusal_never_certifies(self):
        result=match("Some irreducible polynomial","theorem p : Irreducible P := by\n sorry","theorem q : ¬ Summable f := by\n sorry")
        for x in ("A","NONE","theorem p",""):
            guard=guarded_proposal(x,result)
            self.assertFalse(guard["semantic_equivalence_certified"])
            self.assertTrue(guard["cannot_promote_to_proof"])

    def test_preregistered_fixed_thresholds(self):
        self.assertEqual(MIN_SCORE,2.5)
        self.assertEqual(MIN_MARGIN,1.0)

    def test_invalid_input_refused(self):
        with self.assertRaises(ValueError):signature("","nl")
        with self.assertRaises(ValueError):signature("hi","ruby")
        with self.assertRaises(ValueError):signature("a"*50001,"nl")


if __name__=="__main__":unittest.main()
