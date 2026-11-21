"""Infrastructure source-format guard. No gold labels or bridge scoring read."""
import unittest
from source_ingestion import extract,git_blob


class SourceFormatTests(unittest.TestCase):
    def item(self,raw):
        return {"id":100,"path":"proofnet-verified-latest/proofnet-100.lean",
                "git_blob":git_blob(raw)}

    def test_original_sorry_theorem_header(self):
        raw=(b"import Mathlib\n\n/-Informal Statement\n\n"
             b"Prove that a group is simple.\n-/\n\n"
             b"theorem foo (G:Type) : IsSimpleGroup G := by\n  sorry\n")
        out=extract(raw,self.item(raw))
        self.assertTrue(out["lean_contains_sorry"])
        self.assertEqual(out["lean_reference_exact"],
                         "theorem foo (G:Type) : IsSimpleGroup G")
        self.assertTrue(out["informal_exact"].startswith("\n"))

    def test_original_completed_lean_proof_body_never_reaches_model(self):
        raw=(b"import Mathlib\n/-Informal Statement\n\n"
             b"The multiplicative groups are not isomorphic.\n-/\n\n"
             b"theorem some_example :\n  IsEmpty (R \\equiv C) := by\n"
             b"  constructor\n  intro f\n  exact False.elim (impossible f)\n")
        got=extract(raw,self.item(raw))
        self.assertFalse(got["lean_contains_sorry"])
        self.assertNotIn("intro",got["lean_reference_exact"])
        self.assertNotIn("constructor",got["lean_reference_exact"])
        self.assertEqual(got["lean_reference_exact"],
                         "theorem some_example :\n  IsEmpty (R \\equiv C)")
        self.assertTrue(got["proof_body_excluded_from_model_input"])
        self.assertFalse(got["lean_proof_compiled_by_omega"])

    def test_corrupted_source_rejected(self):
        raw=(b"import Mathlib\n/-Informal Statement\nOne\n-/\n"
             b"theorem nm : True := by\n  sorry\n")
        item=self.item(raw)
        with self.assertRaisesRegex(ValueError,"GIT_BLOB"):
            extract(raw+b"tamper",item)

    def test_missing_or_multiple_theorem_fails(self):
        raw=(b"import Mathlib\n/-Informal Statement\nOne\n-/\n"
             b"theorem nm : True := by\n sorry\n"
             b"theorem nm2 : True := by\n sorry\n")
        with self.assertRaisesRegex(ValueError,"UNIQUE_SOURCE_PAIR"):
            extract(raw,self.item(raw))


if __name__=="__main__":
    unittest.main()
