"""P5-ABC-001 fairness and leakage regression suite (NO model calls)."""
from copy import deepcopy
import json
from pathlib import Path
import unittest
from unittest.mock import patch

from p5_abc_fair_preflight import (
    ARMS, CONDITIONS, DATA, DOMAINS, EXPECTED_GIT_BLOB,
    LEAKED_FIELDS, canonical, digest, get_rows, make_prompts, preflight,
    public_evidence, _assert_no_hidden_fields,
)
from planner import ROLE_ORDER, plan_mission


class P5AbcFairnessTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cases=get_rows()

    def test_frozen_public_data_and_composition(self):
        self.assertEqual(len(self.cases),24)
        self.assertEqual(sum(x["spoof_primary_in_adversarial"] for x in self.cases),8)
        self.assertEqual(sum(x["secondary_note_claim"]!=x["truth"]
                             for x in self.cases),8)
        self.assertEqual(set(DOMAINS),{"github","http","uri","python"})
        self.assertTrue(DATA.exists())
        self.assertEqual(len(EXPECTED_GIT_BLOB),40)

    def test_144_gold_free_inputs_have_exact_information_parity(self):
        packet=preflight(self.cases)
        self.assertEqual(packet["status"],"PREFLIGHT_ONLY_P5_LIVE_NOT_RUN")
        self.assertEqual(packet["case_count"],24)
        self.assertEqual(packet["prompt_count"],24*2*3)
        self.assertFalse(packet["external_holdout_evaluated"])
        self.assertEqual(packet["real_model_calls"],0)
        self.assertIsNone(packet["real_token_counts"])
        self.assertEqual(packet["human_independent_graders"],0)
        by_group={}
        for row in packet["requests"]:
            by_group.setdefault((row["case_id"],row["condition"]),[]).append(row)
            body=row["request"]["input"]
            self.assertEqual(set(body),{"shared","strategy"})
            _assert_no_hidden_fields(row["request"])
            self.assertEqual(digest(row["request"]),row["prompt_sha256"])
            self.assertEqual(digest(body["shared"]),row["shared_sha256"])
            self.assertNotIn('"truth":',canonical(row["request"]).decode())
            self.assertNotIn('"spoof_primary_in_adversarial"',canonical(row["request"]).decode())
            self.assertEqual(len(row["request"]["instructions"].splitlines()),1)
        self.assertEqual(len(by_group),48)
        for rows in by_group.values():
            self.assertEqual({r["arm"] for r in rows},set(ARMS))
            shared={canonical(r["request"]["input"]["shared"]) for r in rows}
            self.assertEqual(len(shared),1)
            instr={r["request"]["instructions"] for r in rows}
            self.assertEqual(len(instr),1)
            self.assertEqual(len({r["shared_sha256"] for r in rows}),1)
            self.assertEqual(len({r["prompt_sha256"] for r in rows}),3)

    def test_adaptive_roles_are_real_planner_outputs_with_shared_public_metadata(self):
        for source in self.cases:
            for condition in CONDITIONS:
                packet=make_prompts(source,condition)
                self.assertEqual(packet["B"]["fixed_roles"],list(ROLE_ORDER))
                plan=plan_mission({
                    "question":source["question"],
                    "mission_type":DOMAINS[source["domain"]],
                })
                self.assertEqual(packet["C"]["adaptive_roles"],
                                 [x["role"] for x in plan["tasks"]])
                self.assertEqual(
                    packet["C"]["request"]["input"]["shared"]["mission_type"],
                    DOMAINS[source["domain"]])
                self.assertEqual(
                    packet["A"]["request"]["input"]["shared"],
                    packet["C"]["request"]["input"]["shared"])
                self.assertNotIn("Contexte structure FOURNI",
                                 packet["C"]["request"]["input"]["strategy"])

    def test_source_inversion_is_hidden_and_the_same_for_all_three_arms(self):
        toggles=0
        for source in self.cases:
            safe=public_evidence(source,"intact")
            attacked=public_evidence(source,"perturbed")
            if source["spoof_primary_in_adversarial"]:
                self.assertNotEqual(safe["observations"][0]["claim_text"],
                                    attacked["observations"][0]["claim_text"])
                toggles+=1
            else:
                self.assertEqual(safe,attacked)
            self.assertEqual(
                safe["observations"][1],attacked["observations"][1])
            for condition in CONDITIONS:
                for arm in ARMS:
                    self.assertNotIn(
                        condition,make_prompts(source,condition)[arm]
                        ["request"]["input"])
        self.assertEqual(toggles,8)

    def test_reject_leaks_injected_into_any_shared_payload(self):
        for key in LEAKED_FIELDS:
            with self.subTest(key=key),self.assertRaises(ValueError):
                _assert_no_hidden_fields({"meta":{key:False}})
        with self.assertRaises(ValueError):
            _assert_no_hidden_fields({"source":[{"truth":True}]})

    def test_wrong_source_population_or_labels_fail_closed(self):
        broken=deepcopy(self.cases)
        broken[0]["id"]=broken[1]["id"]
        with self.assertRaises(ValueError):
            preflight(broken)
        broken=deepcopy(self.cases)
        broken.pop()
        with self.assertRaises(ValueError):
            preflight(broken)
        broken=deepcopy(self.cases)
        broken[0]["domain"]="unknown"
        with self.assertRaises(ValueError):
            preflight(broken)

    def test_deterministic_schedule_and_no_actual_randomized_experiment(self):
        p1=preflight(self.cases)
        p2=preflight(self.cases)
        self.assertEqual(p1["synthetic_preflight_schedule"],
                         p2["synthetic_preflight_schedule"])
        self.assertEqual(len(p1["synthetic_preflight_schedule"]),48)
        for group in p1["synthetic_preflight_schedule"]:
            self.assertEqual(set(group["arms"]),set(ARMS))
            self.assertEqual(len(group["arms"]),3)
        self.assertFalse(p1["independent_sessions_executed"])

    def test_existing_privileged_C_builder_must_not_be_used_here(self):
        # Regression: the historical constructor supplies C with extra
        # structured information. Our builder never calls that constructor.
        source=self.cases[0]
        with patch("p5_abc_fair_preflight.plan_mission",
                   wraps=plan_mission) as spy:
            p=make_prompts(source,"intact")
            self.assertTrue(spy.called)
            self.assertEqual(spy.call_args.kwargs,{})
            self.assertEqual(set(spy.call_args.args[0]),
                             {"question","mission_type"})
        self.assertEqual(set(p["C"]["request"]["input"]),
                         {"shared","strategy"})

if __name__=="__main__":
    unittest.main()
