"""Two independent representations audit the archival finite-observer claim."""
import itertools
import unittest

from legacy_observer_transfer import (
    canonicalize, partitions, common_refinement, refines, block_count,
    terminal_probe_guard, reconfiguration_gate, run_closed_world_audit, demo_task_switch,
)


def independent_equivalence_relation_audit():
    """No shared canonicalize/refines/common_refinement with the S-RGS implementation."""
    x = range(3)
    relations = sorted({frozenset((i, j) for i in x for j in x if labels[i] == labels[j])
                        for labels in itertools.product(range(3), repeat=3)}, key=lambda y: (len(y), tuple(sorted(y))))
    assert len(relations) == 5
    index = {r: i for i, r in enumerate(relations)}
    count = 0
    cases = 0
    for p, q in itertools.product(relations, repeat=2):
        together = p & q
        for policy in itertools.product((0, 1), repeat=5):
            for start in relations:
                cases += 1
                cur = start
                for _ in range(3):
                    nxt = cur & (p, q)[policy[index[cur]]]
                    if nxt == cur:
                        break
                    cur = nxt
                else:
                    raise AssertionError("cycle in refinement")
                count += any((i, j) in cur and (i, j) not in together for i in x for j in x)
    return cases, count


class LegacyObserverTransferTests(unittest.TestCase):
    def test_w04_two_independent_full_enumerations(self):
        r = run_closed_world_audit()
        self.assertEqual(len(partitions(3)), 5)
        self.assertEqual(r["results"]["cases"], 4000)
        self.assertEqual(r["results"]["nontrivial_cycles"], 0)
        self.assertEqual(r["results"]["terminal_underinformative"], 848)
        self.assertEqual(independent_equivalence_relation_audit(), (4000, 848))
        self.assertEqual(r["results"]["repaired_with_one_extra_probe"], 848)
        self.assertEqual(r["results"]["fixed_two_probes_full"], 4000)

    def test_w06_switch_and_negative_controls(self):
        report = demo_task_switch()
        self.assertEqual(report["example"]["decision"], "replace")
        self.assertEqual(report["example"]["joint_blocks"], 4)
        self.assertEqual(report["decisions"], {"keep": 7, "replace": 42})
        p = (0, 0, 1, 1)
        self.assertEqual(reconfiguration_gate(p, p, 2).decision, "keep")
        self.assertEqual(reconfiguration_gate(p, (0, 1, 2, 3), 2).decision, "infeasible")

    def test_probe_guard_relative_scope_only(self):
        p = (0, 0, 0)
        q = (0, 0, 1)
        self.assertEqual(terminal_probe_guard(p, p, (p, q))["status"], "underinformative")
        self.assertEqual(terminal_probe_guard(p, p, (p, p))["status"], "closed_relative_to_listed_probes")
        self.assertEqual(terminal_probe_guard(p, q, (p, q))["status"], "not_terminal")
        with self.assertRaises(ValueError):
            terminal_probe_guard(p, p, ())

    def test_permutation_invariance(self):
        p, q = (0, 0, 1, 1), (0, 1, 0, 1)
        perm = (2, 0, 3, 1)
        self.assertEqual(block_count(common_refinement(p, q)),
                         block_count(common_refinement(tuple(p[i] for i in perm), tuple(q[i] for i in perm))))
        self.assertEqual(reconfiguration_gate(p, q, 2).decision,
                         reconfiguration_gate(tuple(p[i] for i in perm), tuple(q[i] for i in perm), 2).decision)


if __name__ == "__main__":
    unittest.main()