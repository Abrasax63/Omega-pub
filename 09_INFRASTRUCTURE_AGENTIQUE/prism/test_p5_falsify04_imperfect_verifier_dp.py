"""Independent forward enumeration for FALSIFY-04."""
import unittest
from fractions import Fraction as F
from itertools import product
from p5_falsify04_imperfect_verifier_dp import (
    STATES,TOOLS,COST,MAX_CALLS,initial_belief,
    observation_probability,observe,optimal,terminal,heuristic_action,policy_tree
)

def exhaustive_world_value(policy,m,h):
    belief=initial_belief(m,h)
    total=F(0)
    for (y,r),prior in zip(STATES,belief):
        def walk(history,weight,spent,unused):
            b=belief
            for tool,signal in history:
                _,b=observe(b,tool,signal)
            last=history[-1] if history else None
            if policy=="bellman":
                action=optimal(b,unused,MAX_CALLS-len(history))[1]
            elif policy=="omega_like":
                action=heuristic_action(b,m,h,last[0] if last else None,
                                         last[1] if last else None)
            elif policy=="no_tool":
                action=terminal(b)[1]
            elif policy=="fixed_A_C":
                action="A" if not history else "C" if len(history)==1 else terminal(b)[1]
            else: raise ValueError(policy)
            if action in TOOLS:
                if action not in unused: raise AssertionError("duplicate tool")
                return sum(walk(history+[(action,z)],
                    weight*observation_probability(action,z,y,r),
                    spent+COST[action],tuple(t for t in unused if t!=action))
                    for z in (0,1))
            reward=F(1,20) if action=="abstain" else (
                F(1) if int(action[-1])==y else F(-2))
            return weight*(reward-spent)
        total+=walk([],prior,F(0),TOOLS)
    return total

class ExactFairnessTests(unittest.TestCase):
    def test_exhaustive_latent_world_reconstruction(self):
        for m,h in product((0,1),repeat=2):
            for policy in ("no_tool","fixed_A_C","omega_like","bellman"):
                with self.subTest(m=m,h=h,policy=policy):
                    self.assertEqual(exhaustive_world_value(policy,m,h),
                                     policy_tree(policy,m,h)["utility"])
    def test_optimality_constraint(self):
        for m,h in product((0,1),repeat=2):
            b=initial_belief(m,h)
            for policy in ("no_tool","fixed_A_C","omega_like"):
                self.assertGreaterEqual(optimal(b)[0],
                                        policy_tree(policy,m,h)["utility"])
    def test_posterior_normalization(self):
        for m,h in product((0,1),repeat=2):
            b=initial_belief(m,h)
            self.assertEqual(sum(b),1)
            for tool in TOOLS:
                outputs=[observe(b,tool,z) for z in (0,1)]
                self.assertEqual(sum(p for p,_ in outputs),1)
                for _,post in outputs:
                    self.assertEqual(sum(post),1)
    def test_same_results_do_not_prove_novelty(self):
        for m,h in product((0,1),repeat=2):
            self.assertEqual(policy_tree("omega_like",m,h)["utility"],
                             policy_tree("bellman",m,h)["utility"])
        self.assertEqual({optimal(initial_belief(m,h))[1]
                          for m,h in product((0,1),repeat=2)},{"A","B"})

if __name__=="__main__": unittest.main()
