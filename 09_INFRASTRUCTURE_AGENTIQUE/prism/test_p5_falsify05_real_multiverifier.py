"""FALSIFY-05 negative controls. THESE fixtures are not the real ClaimDB run."""
from copy import deepcopy
from tempfile import TemporaryDirectory
from pathlib import Path
import unittest

import p5_falsify05_real_multiverifier as p


def sample(n=120):
    result=[]
    for i in range(n):
        label=p.LABELS[i%3]
        rows=[]
        for k,tool in enumerate(p.TOOLS):
            outcome=(label if (i+k)%5 else p.LABELS[(i+1)%3])
            rows.append({"verdict":outcome,"trace":{
                "trace_available":True,
                "outputs":1 if (i+k)%11 else 0,
                "calls":1 if (i+k)%11 else 0}})
        result.append({
            "id":i,"db_name":"db_"+str(i//5),
            "claim":"Exactly 10 items" if i%2 else "This is true",
            "extra_info":"","context":"numeric" if i%2 else "other",
            "base":p.LABELS[(i+2)%3],
            "truth_evaluator_only":label,
            "reports_evaluator_only":rows,
        })
    return result


class RealDataMethodContracts(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cal=sample(120)
        cls.test=sample(22)

    def test_bad_sources_and_lfs_pointers_are_rejected(self):
        with TemporaryDirectory() as tmp:
            path=Path(tmp)/"data.jsonl"
            path.write_text("version https://git-lfs.github.com/spec/v1\n")
            with self.assertRaisesRegex(ValueError,"LFS_POINTER"):
                p._read(path,"0"*64)
            path.write_text('{"claim_id":1}\n')
            with self.assertRaisesRegex(ValueError,"SHA256"):
                p._read(path,"0"*64)

    def test_paid_trace_is_real_metadata_not_truth_label(self):
        rec=self.cal[0]
        view=p.view_of(rec)
        self.assertNotIn("truth_evaluator_only",view)
        self.assertNotIn("reports_evaluator_only",view)
        self.assertNotIn("verdict",view)
        self.assertEqual(p.symbol(rec,0,True),p.NO_SQL)
        self.assertNotEqual(p.symbol(rec,0,False),p.NO_SQL)
        receipt=p.read_tool(rec,0,True)
        self.assertEqual(receipt["symbol"],p.NO_SQL)
        self.assertFalse(receipt["independent_sql_reexecution"])
        self.assertEqual(receipt["same_source_gold_provider"],"claimdb/claimdb")

    def test_joint_model_preserves_correlated_outcomes_without_independence_assumption(self):
        j=p.Joint(self.cal,True,True)
        self.assertEqual(len(j.universe),3*4**3)
        self.assertEqual(j.symbols,p.LABELS+(p.NO_SQL,))
        view=p.view_of(self.cal[1])
        pr,fut=j.posterior(view,(None,None,None))
        self.assertAlmostEqual(sum(pr.values()),1.,places=12)
        self.assertAlmostEqual(sum(fut[0].values()),1.,places=12)
        for label in p.LABELS:
            self.assertGreater(pr[label],0)
        self.assertIn("numeric",j.ctx_counts)

    def test_bellman_is_at_least_terminal_value_under_fitted_model(self):
        agent=p.Agent("bayes_context_exact",self.cal)
        for row in self.cal[:8]:
            view=p.view_of(row)
            empty=(None,None,None)
            score,action=agent._dp(view,empty,p.MAX_COST,p.MAX_CALLS)
            terminal,_=agent.joint.stop(view,empty)
            self.assertGreaterEqual(score+1e-9,terminal)
            self.assertIn(action,p.LABELS+("ABSTAIN",)+(0,1,2))
            self.assertGreaterEqual(score,-.5)

    def test_all_policies_obey_budget_and_do_not_claim_oracle(self):
        for name in p.DEPLOYABLE:
            agent=p.Agent(name,self.cal)
            results=p.execute_agent(agent,self.test)
            summary=p.summarize(results)
            self.assertEqual(summary["N"],len(self.test))
            self.assertEqual(summary["correct"]+summary["wrong"]+
                             summary["abstained"],len(self.test))
            self.assertTrue(all(e["total_acquisitions"]<=2 for e in results))
            self.assertTrue(all(e["cost_proxy"]<=.24 for e in results))
            self.assertTrue(all(len(e["bought"])==len(set(e["bought"]))
                                for e in results))
            self.assertEqual(agent.call_count>0,True)

    def test_gold_change_does_not_change_actions_or_model_observations(self):
        agent=p.Agent("omega_like_full",self.cal)
        row=deepcopy(self.test[2])
        changed=deepcopy(row)
        changed["truth_evaluator_only"]=next(x for x in p.LABELS
                                              if x!=row["truth_evaluator_only"])
        a=p.execute_agent(agent,[row])[0]
        b=p.execute_agent(agent,[changed])[0]
        self.assertEqual(a["bought"],b["bought"])
        self.assertEqual(a["decision"],b["decision"])
        self.assertEqual(a["observed_trace"],b["observed_trace"])
        self.assertNotEqual(a["gold_evaluator_only"],b["gold_evaluator_only"])

    def test_contextual_and_raw_channels_declared_differently(self):
        self.assertTrue(p.Agent("omega_like_full",self.cal).joint.gated)
        self.assertFalse(p.Agent("omega_like_no_observability",self.cal).joint.gated)
        self.assertFalse(p.Agent("bayes_raw_exact",self.cal).joint.gated)
        self.assertTrue(p.Agent("bayes_context_exact",self.cal).joint.gated)
        self.assertFalse(p.Agent("bayes_global_exact",self.cal).joint.contextual)

    def test_bootstrap_paired_by_real_database_groups_not_claim_only(self):
        a=p.execute_agent(p.Agent("fixed_cheapest_two",self.cal),self.test)
        b=p.execute_agent(p.Agent("no_tool",self.cal),self.test)
        boot=p.bootstrap_by_database(a,b,60,20261112)
        self.assertEqual(boot["bootstrap_rounds"],60)
        self.assertGreater(boot["groups"],1)
        self.assertLessEqual(boot["lower_95"],boot["upper_95"])
        with self.assertRaises(ValueError):
            p.bootstrap_by_database(a,b[:-1],60,20261112)

    def test_source_counts_and_costs_frozen_before_test(self):
        self.assertEqual(p.COMMIT,"e06c3a22cc14a8ef6858bb5d40bca7925241b98d")
        self.assertEqual(p.COST,(8,12,16))
        self.assertEqual((p.MAX_COST,p.MAX_CALLS),(24,2))
        self.assertEqual(p.ALPHA,.10)
        self.assertEqual(len(p.SOURCES),5)
        self.assertEqual(len(p.DEPLOYABLE),8)
        self.assertIn("hindsight_oracle",p.POLICIES)

if __name__=="__main__":
    unittest.main()
