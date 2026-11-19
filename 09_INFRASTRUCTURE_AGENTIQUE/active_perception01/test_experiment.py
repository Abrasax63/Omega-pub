#!/usr/bin/env python3
"""Contract tests of active perception experiment, separate from scientific claims."""
import hashlib
import json
import unittest
from collections import Counter
from pathlib import Path

from make_worlds import generate, library
from run_experiment import (frozen_worlds,run_episode,choose_query,infer,
    survivors_after,coverage_choice,disagreement_choice,POLICIES,
    BUDGET,EXPECTED_SHA256,evaluate)


class ActivePerceptionTest(unittest.TestCase):
    def test_worlds_frozen_checksum(self):
        path=Path(__file__).with_name('FROZEN_WORLDS.json')
        self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(),EXPECTED_SHA256)
        self.assertEqual(frozen_worlds(),generate())

    def test_worlds_distribution_and_ood(self):
        worlds=generate()['problems']; lib=library()
        self.assertEqual(len(worlds),96)
        counts=Counter(w['kind'] for w in worlds)
        self.assertEqual(counts['out_of_library'],24)
        self.assertEqual(len(counts),7)
        self.assertTrue(all(v==12 for k,v in counts.items() if k!='out_of_library'))
        known={row for rows in lib.values() for row in rows}
        self.assertTrue(all(tuple(w['y']) not in known for w in worlds if w['kind']=='out_of_library'))

    def test_only_five_sense_calls_each_policy(self):
        lib=library()
        for p in POLICIES:
            calls=[]
            def sensor(x):
                calls.append(x);return (x+2)%4
            res=run_episode(p,sensor,lib)
            self.assertEqual(len(calls),BUDGET)
            self.assertEqual(len(set(calls)),BUDGET)
            self.assertEqual(calls,[t['x'] for t in res['queries']])
            self.assertEqual([res['predictions'][x][0] for x in calls],[(x+2)%4 for x in calls])

    def test_fixed_policies_same_probes(self):
        lib=library()
        a=run_episode('A_fixed_lookup',lambda x:x%4,lib)
        b=run_episode('B_fixed_versions',lambda x:x%4,lib)
        self.assertEqual([r['x'] for r in a['queries']],[0,3,6,9,12])
        self.assertEqual([r['x'] for r in a['queries']],[r['x'] for r in b['queries']])

    def test_coverage_does_not_peek_at_y(self):
        self.assertEqual(coverage_choice({}),0)
        self.assertEqual(coverage_choice({0:0,15:3}),7)
        self.assertEqual(coverage_choice({0:2,15:1}),7)

    def test_reversible_elimination_with_correct_world(self):
        lib=library()
        target=lib['threshold'][-1]
        obs={0:target[0],8:target[8]}
        survivors=survivors_after(lib,obs)
        self.assertIn(target,survivors['threshold'])
        for x,y in obs.items():
            pred=infer(x,obs,survivors,'D_balanced_disagreement')
            self.assertEqual(pred[0],y)

    def test_true_ood_full_observation_is_not_certified(self):
        lib=library()
        ood=next(w for w in generate()['problems'] if w['kind']=='out_of_library')
        obs=dict(enumerate(ood['y']))
        survivors=survivors_after(lib,obs)
        self.assertEqual(sum(map(len,survivors.values())),0)
        guess=infer(0,{},survivors,'D_balanced_disagreement')
        self.assertEqual(guess[2],'OUT_OF_MODEL')
        self.assertFalse(guess[1])

    def test_invalid_sensor_fails_closed(self):
        with self.assertRaises(ValueError):
            run_episode('D_balanced_disagreement',lambda x:99,library())
        with self.assertRaises(ValueError):
            run_episode('D_balanced_disagreement',lambda x:True,library())

    def test_disagreement_same_for_one_hypothesis(self):
        survivors={'only':[(0,)*16]}
        self.assertEqual(disagreement_choice(survivors,{0:0},True),1)
        self.assertEqual(disagreement_choice(survivors,{0:0},False),1)

    def test_complete_report_and_determinism(self):
        a=evaluate();b=evaluate()
        self.assertEqual(a,b)
        self.assertEqual(len(a['episodes']),96*len(POLICIES))
        self.assertTrue(all(v['unseen_total']==11 for v in a['episodes']))
        self.assertTrue(all(v['false_safe_unseen']<=v['safe_unseen'] for v in a['episodes']))


if __name__=='__main__':unittest.main()
