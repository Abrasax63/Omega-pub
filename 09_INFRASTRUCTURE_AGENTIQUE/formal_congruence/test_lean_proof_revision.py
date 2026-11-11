"""Non-regressions and negative controls for actual Lean proof-checking study.

The kernel itself is run in the dedicated CI workflow, not mocked here.
These tests cover input locks, revisions, consistency, independent finite
truth and exact version identities before compiler invocation.
"""
from copy import deepcopy
from itertools import combinations
import json
from pathlib import Path
import re
import unittest

from lean_proof_revision import (
    CASEFILE, U, build_lean, cert_key, conflict_pairs, crt,
    finite_kind, minimal_supports, states, symbolic_kind, validate_cases,
    validate_fact,
)


class LeanProofRevisionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data=json.loads(CASEFILE.read_text(encoding="utf-8"))
        cls.scenarios=validate_cases(cls.data)

    def test_frozen_scenarios_and_exact_population(self):
        self.assertEqual(U,60)
        self.assertEqual(len(self.scenarios),4)
        self.assertEqual([s["id"] for s in self.scenarios],
                         ["ALT","CONTRA","SOURCE_REVISION","ALTERNATIVE_BRANCHES"])
        self.assertEqual(sum(1+len(s["events"]) for s in self.scenarios),24)
        self.assertEqual(sum((1+len(s["events"]))*len(s["goals"])
                             for s in self.scenarios),91)
        self.assertEqual(self.data["lean_toolchain"],"leanprover/lean4:v4.26.0")

    def test_no_explosion_and_recovery_after_retraction(self):
        contradiction={"E":{"r":0,"m":2},"O":{"r":1,"m":2}}
        q={"r":2,"m":3}
        self.assertIsNone(crt(contradiction.values()))
        self.assertEqual(symbolic_kind(contradiction.values(),q),
                         "inconsistent_environment")
        self.assertEqual(finite_kind(contradiction.values(),q),
                         "inconsistent_environment")
        self.assertEqual(conflict_pairs(contradiction),[["E","O"]])
        self.assertEqual(symbolic_kind([contradiction["E"]],q),
                         "undetermined")
        self.assertEqual(symbolic_kind([contradiction["O"]],{"r":0,"m":2}),
                         "refuted")

    def test_two_independent_supports_then_retract_one(self):
        scenario=self.scenarios[0]
        snapshots=list(states(scenario))
        q=scenario["goals"]["G3"]
        initial=minimal_supports(snapshots[0]["active"],q,"entailed","symbolic")
        self.assertEqual(initial,[("A",),("B",)])
        self.assertEqual(
            minimal_supports(snapshots[1]["active"],q,"entailed","symbolic"),
            [("B",)])
        self.assertEqual(symbolic_kind(snapshots[2]["active"].values(),q),
                         "undetermined")
        self.assertFalse(minimal_supports(snapshots[2]["active"],q,
                                          "entailed","symbolic"))

    def test_version_fingerprint_detects_replacement_and_restoration(self):
        s=self.scenarios[2]
        snapshots=list(states(s))
        q=s["goals"]["G3"]
        initial=cert_key(s["id"],"G3",q,"entailed",("A",),
                         snapshots[0]["active"])
        replacement=cert_key(s["id"],"G3",q,"entailed",("A",),
                             snapshots[1]["active"])
        restored=cert_key(s["id"],"G3",q,"entailed",("A",),
                          snapshots[3]["active"])
        self.assertNotEqual(initial,replacement)
        self.assertEqual(initial,restored)
        self.assertIsNone(crt(snapshots[1]["active"].values()))
        self.assertTrue(crt(snapshots[2]["active"].values()) is not None)

    def test_minimal_justifications_agree_with_independent_enumeration(self):
        for scenario in self.scenarios:
            for snap in states(scenario):
                active=snap["active"]
                expected_conflict=crt(active.values()) is None
                self.assertEqual(bool(conflict_pairs(active)),expected_conflict)
                for q in scenario["goals"].values():
                    self.assertEqual(symbolic_kind(active.values(),q),
                                     finite_kind(active.values(),q))
                    for kind in ("entailed","refuted"):
                        self.assertEqual(
                            minimal_supports(active,q,kind,"symbolic"),
                            minimal_supports(active,q,kind,"finite"))

    def test_generated_lean_contains_explicit_three_step_proof_dependencies(self):
        cert={"kind":"entailed","query":{"r":2,"m":3},
              "premises":[{"r":2,"m":6}]}
        code=build_lean([cert])
        self.assertIn("theorem support_0",code)
        self.assertIn("theorem derived_0",code)
        self.assertIn("theorem final_0",code)
        self.assertIn("exact support_0 n h_0",code)
        self.assertIn("exact derived_0 n h_0",code)
        self.assertIn("omega",code)
        self.assertNotRegex(code,r"\b(sorry|admit|axiom|native_decide|unsafe)\b")
        neg=build_lean([{"kind":"refuted","query":{"r":1,"m":2},
                        "premises":[{"r":0,"m":2}]}])
        self.assertIn("¬ (n % 2 = 1)",neg)
        self.assertEqual(neg.count("theorem "),3)

    def test_garbage_and_injected_names_rejected(self):
        invalid=[{"r":1,"m":0},{"r":0,"m":7},{"r":7,"m":6},
                 {"r":True,"m":6},{"r":0,"m":None}]
        for x in invalid:
            with self.subTest(fact=x),self.assertRaises(ValueError):
                validate_fact(x)
        c=deepcopy(self.data)
        c["scenarios"][0]["sources"]["A); sorry"]="x"
        with self.assertRaises(ValueError):validate_cases(c)
        c=deepcopy(self.data)
        c["scenarios"][0]["events"][0]={"op":"replace","id":"C","value":{"r":1,"m":6}}
        with self.assertRaises(ValueError):validate_cases(c)
        c=deepcopy(self.data)
        c["lean_toolchain"]="leanprover/lean4:master"
        with self.assertRaises(ValueError):validate_cases(c)

    def test_frozen_data_has_no_labels_or_oracle_answers(self):
        text=CASEFILE.read_text(encoding="utf-8")
        self.assertNotIn('"entailed"',text)
        self.assertNotIn('"refuted"',text)
        self.assertNotIn('"truth"',text)
        self.assertNotIn('"certificate"',text)


if __name__=="__main__":
    unittest.main()
