"""Minimal counterexample: posterior-error optimality != certified-answer coverage."""
import unittest
from strategic_methods_executable import tasks, run_method, oracle
from strategic_method_selection import fit, execute_omega, execute_order, evaluate


class EvidenceObjectiveMismatchTests(unittest.TestCase):
    def test_modular_true_can_be_proved_in_one_check_but_omega_subtype_abstains(self):
        all_cases=tasks()
        train=[t for t in all_cases if t["partition"]=="train"]
        fitted=fit(train)
        target=next(t for t in all_cases if t["id"]=="M4")
        self.assertTrue(oracle(target))
        self.assertEqual(target["params"],{"a":8,"b":2,"m":2})
        self.assertEqual(run_method(target,"formal")["observation"],"yes")
        self.assertEqual(run_method(target,"compute")["observation"],"unknown")
        self.assertEqual(fitted["omega_kind"]["mod"]["policy"]["check_id"],
                         "method-compute")
        answer,trace=execute_omega(target,fitted["omega_kind"]["mod"])
        self.assertIsNone(answer)
        self.assertEqual(trace[0]["method"],"compute")
        # Same initial subtype known, same budget. Fixed trained procedure
        # directly applies universal modular proof instead.
        fixed,trace_fixed=execute_order(target,fitted["kind"]["mod"])
        self.assertEqual(fixed,"yes")
        self.assertEqual(len(trace_fixed),1)

    def test_no_tuning_original_comparison_after_exploratory_subtype_check(self):
        report=evaluate()
        summary=report["summary"]
        self.assertEqual((summary["C_omega"]["correct"],summary["C_omega"]["calls"]), (13,16))
        self.assertEqual((summary["C_omega_subtype_exploratory"]["correct"],
                          summary["C_omega_subtype_exploratory"]["calls"]), (12,16))
        self.assertEqual((summary["F_subtype_fixed"]["correct"],
                          summary["F_subtype_fixed"]["calls"]), (15,18))
        self.assertEqual((summary["B_domain_fixed"]["correct"],
                          summary["B_domain_fixed"]["calls"]), (15,20))


if __name__=="__main__":
    unittest.main()
