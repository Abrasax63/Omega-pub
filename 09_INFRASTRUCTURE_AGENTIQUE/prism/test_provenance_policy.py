import hashlib
import unittest
from collections import Counter

from audit_pr29_controls import replay
from provenance_benchmark import DATA, _read, run, run_supplement
from provenance_policy import decide


class ProvenanceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tasks = {task["id"]: task for task in _read("tasks")}
        cls.observations = _read("observations")

    def execute(self, case, budget=2, **settings):
        return decide(self.tasks[case], self.observations[case].__getitem__, budget=budget,
                      **settings)

    def test_frozen_inputs(self):
        for line in (DATA / "SHA256SUMS").read_text().splitlines():
            digest, name = line.split()
            self.assertEqual(hashlib.sha256((DATA / name).read_bytes()).hexdigest(), digest)

    def test_replan_after_mismatch_and_version(self):
        for case, issue, decision in [
            ("M1", "origin_or_scope_mismatch", "no"),
            ("T1", "version_or_date_out_of_scope", "yes"),
        ]:
            with self.subTest(case=case):
                result = self.execute(case)
                self.assertEqual(result["trace"][0]["issue"], issue)
                self.assertEqual(result["trace"][0]["risk_after"], "1/2")
                self.assertEqual(result["trace"][1]["risk_after"], "0")
                self.assertEqual(result["decision"], decision)
                self.assertIsNone(self.execute(case, budget=1)["decision"])

    def test_conflict_duplicate_and_missing(self):
        self.assertEqual(self.execute("D4")["trace"][-1]["conflicts_after"], ["claim"])
        self.assertEqual(self.execute("D5")["trace"][-1]["conflicts_after"], [])
        self.assertEqual(self.execute("F2")["trace"][0]["issue"], "missing_observation")
        for case in ("D4", "D5", "F2", "P1"):
            self.assertIsNone(self.execute(case)["decision"])

    def test_zero_budget_and_no_useful_check(self):
        self.assertEqual(self.execute("M2", budget=0)["decision"], "yes")
        self.assertEqual(self.execute("M2")["trace"], [])
        self.assertEqual(self.execute("D2", horizon=1)["reason"], "no_useful_check")

    def test_invariance_and_budget(self):
        for case, task in self.tasks.items():
            with self.subTest(case=case):
                changed = {**task, "checks": task["checks"][::-1], "worlds": task["worlds"][::-1]}
                result = decide(changed, self.observations[case].__getitem__, budget=2)
                self.assertEqual(result, self.execute(case))
                checks = [step["check"] for step in result["trace"]]
                self.assertEqual(len(checks), len(set(checks)))
                self.assertLessEqual(len(checks), 2)

    def test_exact_answers_without_receipt_policy(self):
        degree = Counter(v for edge in [(0, 1), (1, 2), (2, 3), (3, 0), (0, 2)]
                         for v in edge)
        self.assertEqual(tuple(degree[i] for i in range(4)), (3, 2, 3, 2))
        self.assertFalse(all(n % 2 == 0 for n in degree.values()))
        with self.assertRaises(ValueError):
            list(zip([1], [], strict=True))
        for case, numerators in {"D1": (3, 3), "D2": (3, 1), "D3": (1, 3)}.items():
            expected = "yes" if sum(n * 2 > 4 for n in numerators) == 1 else "no"
            self.assertEqual(self.execute(case)["decision"], expected)
        self.assertEqual(_read("answer_key")["M2"]["rationale"], "6k+3=2(3k+1)+1.")

    def test_authentic_documentary_disagreement(self):
        result = run_supplement()
        self.assertEqual(result["expected"], "yes")
        provenance = result["arms"]["D_provenance"]
        self.assertEqual(provenance["trace"][-1]["conflicts_after"], ["rule"])
        self.assertIsNone(provenance["decision"])

    def test_pr29_short_circuit_controls(self):
        result = replay()
        self.assertEqual(result["merged"], {"correct": 12, "calls": 17, "cases": 12})
        self.assertEqual(result["touched_tests"], {"correct": 12, "calls": 15, "cases": 12})

    def test_five_arm_calibration(self):
        result = run()
        self.assertEqual(len(result["cases"]), 60)
        scores = [(v["score"], v["consultations"]) for v in result["summary"].values()]
        self.assertEqual(scores, [(7, 0), (11, 21), (6, 15), (11, 21), (8, 15)])


if __name__ == "__main__":
    unittest.main()
