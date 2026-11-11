"""Post-hoc exploration: prioritize a known normative primary over commentary.

This is NOT a preregistered score, not a hidden task, and not a new source
observation. The fixed comparator has the same primary source and budget as
the v0.2 adaptive policy, but declines to consult secondary documentation.
"""
import copy
import unittest
from provenance_benchmark import _read
from trusted_receipt_adapter import decide_guarded


class NormativeFirstComparatorTests(unittest.TestCase):
    def test_known_normative_origin_can_solve_t3_in_one_call(self):
        packet = _read("supplement_t3")
        original = packet["task"]
        # Same available primary provider; comparator is precommitted to
        # choosing it first. It never grants a new fact or hidden answer.
        task = copy.deepcopy(original)
        task["checks"] = [c for c in original["checks"]
                          if c["origin"] == "ietf" and c["primary"]]
        self.assertEqual(len(task["checks"]), 1)
        receipts = packet["observations"]
        prioritized = decide_guarded(task, receipts.__getitem__, budget=2,
                                     fixed=True, authority_by_field={"rule": "ietf"})
        adaptive = decide_guarded(original, receipts.__getitem__, budget=2,
                                  authority_by_field={"rule": "ietf"})
        self.assertEqual(prioritized["decision"], "yes")
        self.assertEqual(adaptive["decision"], "yes")
        self.assertEqual(len(prioritized["trace"]), 1)
        self.assertEqual(len(adaptive["trace"]), 2)
        self.assertEqual(prioritized["adapter_rejections"], [])

    def test_scope_absent_cannot_justify_arbitration(self):
        packet = _read("supplement_t3")
        task = packet["task"]
        receipts = copy.deepcopy(packet["observations"])
        receipts["00-copy"]["independence"] = "mdn"
        # No normative authority declared: a genuine contradictory secondary
        # cannot be silently ignored by default.
        out = decide_guarded(task, receipts.__getitem__, budget=2)
        self.assertIsNone(out["decision"])


if __name__ == "__main__":
    unittest.main()
