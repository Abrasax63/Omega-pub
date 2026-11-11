"""Exact finite-probe strategy safety, optimality and reporting tests."""
import json
from copy import deepcopy
import unittest
from probe_strategy_benchmark import (
    CASE_FILE, Scenario, WORLD_COUNT, FULL_MASK, ARMS, mask_for,
    check_case, evaluate
)


class StrategyBenchmarkTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cases=json.loads(CASE_FILE.read_text(encoding="utf-8"))

    def test_frozen_population_and_no_external_oracle(self):
        self.assertEqual(self.cases["worlds"],60)
        self.assertEqual(len(self.cases["scenario_list"]),4)
        self.assertEqual(
            [s["id"] for s in self.cases["scenario_list"]],
            ["CAL_12","CAL_30","TEST_12","TEST_60"])
        self.assertEqual({s["split"] for s in self.cases["scenario_list"]},
                         {"calibration","test"})

    def test_exact_binary_partition_and_probe_outcomes(self):
        s=Scenario(self.cases["scenario_list"][0])
        for i,mask in enumerate(s.pmasks):
            pos,neg=s.split(FULL_MASK,i)
            self.assertEqual(pos & neg,0)
            self.assertEqual(pos | neg,FULL_MASK)
            self.assertEqual(pos.bit_count(),60//s.probes[i]["m"])
            self.assertEqual((pos ^ FULL_MASK),neg)
        self.assertEqual(mask_for({"r":2,"m":3}).bit_count(),20)

    def test_stop_baseline_and_hidden_world_certificate_soundness(self):
        for raw in self.cases["scenario_list"]:
            s=Scenario(raw)
            for w in range(WORLD_COUNT):
                trace=s.trace(w,"ZERO",())
                self.assertEqual(trace["cost"],0)
                self.assertEqual(trace["probe_calls"],0)
                for q,status in zip(raw["queries"],trace["truth_statuses"]):
                    if status=="entailed":
                        self.assertEqual(w%q["m"],q["r"])
                    if status=="refuted":
                        self.assertNotEqual(w%q["m"],q["r"])
                self.assertEqual(trace["total_loss"],
                                 5*trace["undetermined_queries"])

    def test_dynamic_programming_monotonicity_on_all_frozen_cases(self):
        for raw in self.cases["scenario_list"]:
            s=Scenario(raw)
            initial=s.stop_loss(FULL_MASK)
            v1=s.optimal(FULL_MASK,s.full,1)[0]
            v2=s.optimal(FULL_MASK,s.full,2)[0]
            full=s.optimal(FULL_MASK,s.full,-1)[0]
            self.assertLessEqual(full,v2)
            self.assertLessEqual(v2,v1)
            self.assertLessEqual(v1,initial)
            for w in (0,7,29,59):
                for policy in ("GREEDY1","OMEGA_LOOKAHEAD2",
                               "ADAPTIVE_DP_EXACT"):
                    trace=s.trace(w,policy,())
                    self.assertEqual(
                        len({x["index"] for x in trace["trace"]}),
                        len(trace["trace"]))
                    self.assertTrue(all(x["belief_size_after"]>0
                                        for x in trace["trace"]))

    def test_small_one_probe_logic_minimal_loss(self):
        raw={"id":"UNIT","split":"test",
             "queries":[{"r":0,"m":2}]*5,
             "probes":[{"id":"p0","r":0,"m":2,"cost":1},
                       {"id":"p1","r":1,"m":2,"cost":2},
                       {"id":"p2","r":0,"m":3,"cost":3}]}
        s=Scenario(raw)
        self.assertEqual(s.optimal(FULL_MASK,s.full,-1)[0],60)
        self.assertEqual(s.optimal(FULL_MASK,s.full,1)[0],60)
        for w in range(60):
            t=s.trace(w,"ADAPTIVE_DP_EXACT",())
            self.assertEqual(t["total_loss"],1)
            self.assertEqual(t["resolved_queries"],5)

    def test_all_arms_scored_and_optimal_reference_not_exceeded(self):
        result=evaluate(self.cases)
        self.assertEqual(result["scenario_count"],4)
        self.assertEqual(len(result["ledger"]),4*60*5)
        self.assertEqual(result["source_cases_commit"],
                         "883cbe181bac982b8f30d5128f8f16a0381f79f9")
        for s in result["scenarios"].values():
            stats=s["arm_metrics"]
            best=stats["ADAPTIVE_DP_EXACT"]["sum_total_loss_exact"]
            for p in ARMS:
                self.assertGreaterEqual(stats[p]["sum_total_loss_exact"],best)
                self.assertEqual(stats[p]["false_certificates"],0)
            self.assertEqual(best,s["full_adaptive_exact_loss_sum"])
            self.assertEqual(stats["FIXED_BEST"]["sum_total_loss_exact"],
                             s["fixed_schedule_optimum_loss_sum"])

    def test_cli_json_result_serialization_and_split_metadata(self):
        result=evaluate(self.cases)
        serialized=json.dumps(result,sort_keys=True)
        reread=json.loads(serialized)
        self.assertEqual(len(reread["ledger"]),4*60*5)
        for case in self.cases["scenario_list"]:
            self.assertEqual(reread["scenarios"][case["id"]]["split"],
                             case["split"])
        self.assertEqual(
            sum(1 for t in reread["ledger"] if t["split"]=="test"),
            2*60*5)

    def test_invalid_inputs_rejected(self):
        raw=deepcopy(self.cases["scenario_list"][0])
        for bad in [
            {"r":0,"m":0},
            {"r":2,"m":2},
            {"r":0,"m":7},
            {"r":False,"m":3},
        ]:
            x=deepcopy(raw)
            x["queries"][0]=bad
            with self.subTest(bad=bad),self.assertRaises(ValueError):
                Scenario(x)
        x=deepcopy(raw);x["probes"][0]["cost"]=0
        with self.assertRaises(ValueError):Scenario(x)
        x=deepcopy(raw);x["probes"][0]["id"]=x["probes"][1]["id"]
        with self.assertRaises(ValueError):Scenario(x)
        s=Scenario(raw)
        for world in (-1,60,"x",True):
            with self.assertRaises(ValueError):
                s.trace(world,"GREEDY1",())
        with self.assertRaises(ValueError):s.trace(1,"UNKNOWN",())


if __name__=="__main__":
    unittest.main()
