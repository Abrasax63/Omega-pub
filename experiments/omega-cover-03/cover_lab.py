"""OMEGA-COUNTEREXAMPLE-COVER-03: matched-length candidate tests on opaque Mealy systems.

The AALpy L* learner, SUL charging, query budget failures and independent
exact equivalence evaluator come from PR #137, unchanged. Four EQ scheduling
methods differ; all candidate words are exactly ten input symbols.
"""
from __future__ import annotations

import argparse
from collections import deque
from copy import deepcopy
from hashlib import sha256
from pathlib import Path
import json
import random
import sys

from aalpy.learning_algs import run_Lstar

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/"omega-blackbox-resilience-02"))
import resilience_lab as resilience  # noqa: E402
from mealy_lab import Mealy,digest  # noqa: E402

b=resilience.b
EXPERIMENT="OMEGA-COUNTEREXAMPLE-COVER-03"
PREREG="2306aca73c7839c11f340f0102bda1f87548db71"
ARMS=("RANDOM_LEN10","FIXED_LEN10","OLD_OMEGA_LEN10","COVER_DISTINGUISH_LEN10")
EQ_LENGTH=10
EQ_ROUND_WORDS=32
BUDGETS=(900,1800)
PRIMARY=1800
GENERATORS=((4,36104,4),(5,36105,4),(6,36106,4))
RESERVED_WORDS=128


def reachable(machine):
    return resilience.accessible_truth_states(machine)


def distinguishable(machine):
    """Pairs separable under some finite input word; independent of L*."""
    for i in range(machine.size):
        for j in range(i+1,machine.size):
            queue=deque([(i,j)])
            seen={(i,j)}
            success=False
            while queue:
                x,y=queue.popleft()
                for a in b.ALPHABET:
                    if machine.outputs[x][a]!=machine.outputs[y][a]:
                        success=True
                        break
                    next_pair=(machine.transitions[x][a],machine.transitions[y][a])
                    if next_pair not in seen:
                        seen.add(next_pair)
                        queue.append(next_pair)
                if success:
                    break
            if not success:
                return False
    return True


def old_signatures():
    used=b.true_old_signatures()
    used.update(x["signature"] for x in b.new_machines())
    used.update(resilience.cycle_marker_machine(n).signature()
                for n in resilience.STRESS_SIZES)
    if len(used)!=1124:
        raise AssertionError("HISTORICAL_COHORT_LEDGER_MISMATCH")
    return used


def new_worlds():
    """Structural filter only, never look at any learner/score."""
    used=old_signatures()
    worlds=[]
    for n,seed,count in GENERATORS:
        rng=random.Random(seed)
        accepted=attempts=nonreachable=nonminimal=duplicate=0
        while accepted<count:
            attempts+=1
            if attempts>100000:
                raise AssertionError("MINIMAL_REACHABLE_GENERATOR_EXHAUSTED")
            world=Mealy(
                tuple(tuple(rng.randrange(n) for _ in b.ALPHABET)
                      for _ in range(n)),
                tuple(tuple(rng.randrange(3) for _ in b.ALPHABET)
                      for _ in range(n)),
            )
            if len(reachable(world))!=n:
                nonreachable+=1
                continue
            if not distinguishable(world):
                nonminimal+=1
                continue
            signature=world.signature()
            if signature in used:
                duplicate+=1
                continue
            used.add(signature)
            worlds.append({
                "name":f"N{n}_{accepted}",
                "n":n,
                "seed":seed,
                "index":accepted,
                "sig":signature,
                "draws":attempts,
                "inaccessible_rejections":nonreachable,
                "nonminimal_rejections":nonminimal,
                "isomorphism_rejections":duplicate,
                "world":world,
            })
            accepted+=1
    if len(worlds)!=12 or len(used)!=1124+12:
        raise AssertionError("NEW_HOLDOUT_SIGNATURE_CROSSOVER")
    return worlds


class MatchedOracle(b.CandidateOracle):
    """Only hypothesis transitions/outputs guide candidate scheduling.

    b.CandidateOracle.find_cex from PR #137 charges all 10-symbol candidates,
    fail-closes if a candidate cannot be afforded, and returns a real
    counterexample only after comparing *paid* SUL observations.
    """

    def __init__(self,sul,arm,seed):
        if arm not in ARMS:
            raise ValueError("UNKNOWN_EQ_METHOD")
        super().__init__(b.ALPHABET,sul,
                         "OMEGA_GUIDED_LSTAR" if arm in
                         ("OLD_OMEGA_LEN10","COVER_DISTINGUISH_LEN10")
                         else "RANDOM_LSTAR" if arm=="RANDOM_LEN10"
                         else "FIXED_LSTAR",
                         seed)
        self.arm_name=arm
        self.proposal_original_lengths=[]
        self.truncations=0
        self.paddings=0
        self.generated_words=[]
        self.cover_schedule=[]
        self.cover_index=0
        self.cover_structure=None
        self.cover_transition_keys=set()
        self.cover_pair_keys=set()

    def normalize(self,word):
        word=tuple(word)
        if not word or any(x not in b.ALPHABET for x in word):
            raise AssertionError("INVALID_PREPAID_EQ_WORD")
        self.proposal_original_lengths.append(len(word))
        if len(word)>EQ_LENGTH:
            self.truncations+=1
            word=word[:EQ_LENGTH]
        elif len(word)<EQ_LENGTH:
            self.paddings+=1
            word=word+tuple(self.rng.choice(b.ALPHABET)
                            for _ in range(EQ_LENGTH-len(word)))
        if len(word)!=EQ_LENGTH:
            raise AssertionError("MATCHED_EQ_LENGTH_VIOLATION")
        self.generated_words.append(list(word))
        return word

    def fingerprint(self,hypothesis):
        access=b.candidate_access_paths(hypothesis)
        return tuple(
            (state.state_id,tuple(state.output_fun[s] for s in b.ALPHABET),
             tuple(state.transitions[s].state_id for s in b.ALPHABET))
            for state,prefix in access
        )

    def generate_cover_schedule(self,hypothesis):
        """Transition cover + suffixes distinguishing candidate destination.

        Every transition included at least once, and each transition-to-other
        hypothesis-state comparison is offered if a distinguishing suffix
        exists in the candidate (never in the hidden world).
        """
        access=b.candidate_access_paths(hypothesis)
        proposals=[]
        pair_keys=set()
        transitions=set()
        for state,prefix in access:
            for symbol in b.ALPHABET:
                dst=state.transitions[symbol]
                edge=(state.state_id,symbol)
                transitions.add(edge)
                any_pair=False
                for other,_ in access:
                    if other is dst:
                        continue
                    suffix=b.distinguishing_suffix(dst,other,max_length=8)
                    if not suffix:
                        continue
                    pair=(state.state_id,symbol,other.state_id)
                    pair_keys.add(pair)
                    any_pair=True
                    proposals.append((
                        len(prefix)+1+len(suffix),
                        len(prefix),
                        str(state.state_id),symbol,str(other.state_id),
                        prefix+(symbol,)+suffix,
                    ))
                if not any_pair:
                    # If hypothesis is unobservable/nonminimal or one-state,
                    # still cover the transition and randomize a suffix.
                    tail=tuple(self.rng.choice(b.ALPHABET) for _ in range(4))
                    proposals.append((
                        len(prefix)+1+len(tail),len(prefix),
                        str(state.state_id),symbol,"",
                        prefix+(symbol,)+tail,
                    ))
        proposals.sort(key=lambda x:(x[1],x[2],x[3],x[4],x[0]))
        self.cover_transition_keys=transitions
        self.cover_pair_keys=pair_keys
        return [x[-1] for x in proposals]

    def next_word(self,hypothesis):
        if self.arm_name=="RANDOM_LEN10":
            proposed=tuple(self.rng.choice(b.ALPHABET)
                           for _ in range(EQ_LENGTH))
        elif self.arm_name=="FIXED_LEN10":
            i=self.fixed_index % (2**EQ_LENGTH)
            self.fixed_index+=1
            proposed=tuple((i>>bit)&1 for bit in range(EQ_LENGTH-1,-1,-1))
        elif self.arm_name=="OLD_OMEGA_LEN10":
            proposed=b.CandidateOracle.next_word(self,hypothesis)
        else:
            new_structure=self.fingerprint(hypothesis)
            if new_structure!=self.cover_structure:
                self.cover_structure=new_structure
                self.cover_schedule=self.generate_cover_schedule(hypothesis)
                self.cover_index=0
            if not self.cover_schedule:
                raise AssertionError("EMPTY_COVER_SCHEDULE")
            proposed=self.cover_schedule[self.cover_index % len(self.cover_schedule)]
            self.cover_index+=1
            # After a full transition+suffix pass, use varying suffix
            # extensions at the exact same matched query length.
        return self.normalize(proposed)


def train(machine,arm,cap,seed):
    """Actual AALpy, no target transition table exposed to EQ scheduler."""
    sul=b.MeteredBlackBox(machine,cap)
    oracle=MatchedOracle(sul,arm,seed)
    hypothesis=None
    status="NO_HYPOTHESIS"
    try:
        hypothesis=run_Lstar(list(b.ALPHABET),sul,oracle,
                             automaton_type="mealy",
                             cache_and_non_det_check=False,
                             print_level=0)
        status="PROVISIONAL_LSTAR_COMPLETED"
    except b.BudgetExhausted:
        hypothesis=oracle.last_candidate
        status=("BUDGET_INTERRUPTED_WITH_CANDIDATE"
                if hypothesis is not None else
                "BUDGET_INTERRUPTED_NO_CANDIDATE")
    except Exception as exc:
        raise RuntimeError(f"LSTAR_FAILURE:{arm}:{type(exc).__name__}:{exc}") from exc
    if hypothesis is not None:
        for state in hypothesis.states:
            if any(a not in state.transitions or a not in state.output_fun
                   for a in b.ALPHABET):
                raise AssertionError("INCOMPLETE_HYPOTHESIS")
    ledger=sul.summary()
    for q in ledger["query_log"]:
        if q["phase"]=="EQ" and len(q["inputs"])!=EQ_LENGTH and not q.get("incomplete_due_to_budget"):
            raise AssertionError("UNMATCHED_COMPLETED_EQ_LENGTH")
    if oracle.words_tested != sum(
        q["phase"]=="EQ" and not q.get("incomplete_due_to_budget")
        for q in ledger["query_log"]
    ):
        raise AssertionError("EQ_WORDS_TESTED_LEDGER_MISMATCH")
    queried={tuple(q["inputs"]) for q in ledger["query_log"]
             if not q.get("incomplete_due_to_budget")}
    return hypothesis,queried,{
        "arm":arm,"status":status,
        "hypothesis_states":len(hypothesis.states) if hypothesis is not None else None,
        "ledger":ledger,
        "eq_rounds":oracle.eq_rounds,
        "eq_words_tested":oracle.words_tested,
        "eq_counterexamples":oracle.counterexamples,
        "eq_round_log":oracle.rounds_log,
        "proposal_original_lengths":oracle.proposal_original_lengths,
        "proposal_truncations":oracle.truncations,
        "proposal_paddings":oracle.paddings,
        "generated_words_count":len(oracle.generated_words),
        "hypothesis_cover_transitions":len(oracle.cover_transition_keys),
        "hypothesis_cover_distinguishing_pairs":len(oracle.cover_pair_keys),
        "candidate_word_hash":digest(oracle.generated_words),
    }


def audit_truth(machine,ledger):
    """Independent evaluator, never used to generate an EQ candidate."""
    return resilience.assert_ledger_matches_truth(machine,ledger)


def test_words(n,index):
    rng=random.Random(960000+100*n+index)
    words=set()
    while len(words)<RESERVED_WORDS:
        size=rng.randint(12,20)
        words.add(tuple(rng.choice(b.ALPHABET) for _ in range(size)))
    return sorted(words)


def evaluate_one(machine,arm,cap,seed,words):
    hypothesis,asked,training=train(machine,arm,cap,seed)
    audit_truth(machine,training["ledger"])
    eq=b.exact_equivalence(machine,hypothesis)
    reserved=b.heldout_score(machine,hypothesis,words,asked)
    if eq["status"]=="EXACT_EQUIVALENT" and reserved["whole_word_accuracy"]!=1.0:
        raise AssertionError("EXACT_EQUIVALENCE_AND_RESERVED_CONFLICT")
    return {"training":training,"exact_equivalence":eq,"reserved":reserved}


def run():
    if b.version("aalpy")!="1.6.2":
        raise AssertionError("EXTERNAL_REFERENCE_VERSION_CHANGED")
    worlds=new_worlds()
    observations=[]
    for meta in worlds:
        machine=meta["world"]
        n=meta["n"]
        idx=meta["index"]
        words=test_words(n,idx)
        trials={}
        for cap in BUDGETS:
            trials[str(cap)]={}
            for i,arm in enumerate(ARMS):
                seed=910000+1000*n+30*idx+i
                trials[str(cap)][arm]=evaluate_one(
                    machine,arm,cap,seed,words)
        observations.append({
            "name":meta["name"],"n":n,"index":idx,
            "canonical_signature":meta["sig"],
            "generator_seed":meta["seed"],
            "draws":meta["draws"],
            "inaccessible_rejections":meta["inaccessible_rejections"],
            "nonminimal_rejections":meta["nonminimal_rejections"],
            "isomorphism_rejections":meta["isomorphism_rejections"],
            "accessible_states":len(reachable(machine)),
            "all_states_distinguishable":distinguishable(machine),
            "evaluator_only_world":{
                "transitions":machine.transitions,"outputs":machine.outputs,
                "initial_state":0,
            },
            "reserved_words_sha256":digest(words),
            "budgets":trials,
        })
    comparison={}
    for cap in BUDGETS:
        entries={}
        for arm in ARMS:
            values=[v["budgets"][str(cap)][arm] for v in observations]
            entries[arm]={
                "exact_equivalent":sum(
                    v["exact_equivalence"]["status"]=="EXACT_EQUIVALENT"
                    for v in values),
                "mean_whole_word_accuracy":sum(
                    v["reserved"]["whole_word_accuracy"] for v in values)/len(values),
                "total_paid_symbols":sum(
                    v["training"]["ledger"]["spent_symbols"] for v in values),
                "eq_paid_symbols":sum(
                    v["training"]["ledger"]["by_phase_spent"]["EQ"]
                    for v in values),
                "eq_words_tested":sum(v["training"]["eq_words_tested"]
                                      for v in values),
                "eq_counterexamples":sum(v["training"]["eq_counterexamples"]
                                          for v in values),
                "budget_interrupted":sum(v["training"]["status"].startswith("BUDGET_INTERRUPTED")
                                         for v in values),
            }
        comparison[str(cap)]=entries
    primary=comparison[str(PRIMARY)]
    candidate=primary["COVER_DISTINGUISH_LEN10"]
    baselines=[primary[k] for k in ARMS if k!="COVER_DISTINGUISH_LEN10"]
    passed=(all(candidate["exact_equivalent"]>p["exact_equivalent"]
                for p in baselines)
            and all(candidate["mean_whole_word_accuracy"]+1e-12 >=
                    p["mean_whole_word_accuracy"] for p in baselines))
    outcome="DESCRIPTIVE_COVER_GAIN" if passed else "NO_DEMONSTRATED_COVER_GAIN"
    return {
        "experiment":EXPERIMENT,
        "prereg_commit":PREREG,
        "status":outcome,
        "algorithm":"aalpy.run_Lstar, automaton_type=mealy",
        "dependency":"aalpy==1.6.2",
        "all_arms_share_actual_Lstar_engine":True,
        "all_EQ_words_matched_length":EQ_LENGTH,
        "same_seed_per_arm_across_budgets":True,
        "exact_oracle_evaluation_only":True,
        "no_paid_api":True,"main_modified":False,
        "general_gain_proven":False,
        "arms":list(ARMS),"budgets":list(BUDGETS),
        "primary_cap":PRIMARY,"new_worlds":len(observations),
        "cases":observations,"comparison":comparison,
        "limitations":[
            "All Mealy machines fully accessible and distinguishable by structural prefilter.",
            "All four methods are the existing AALpy L* with different approximate EQ test scheduling.",
            "Same maximum query budgets and EQ word lengths, not equal realized membership-query cost.",
            "Normalization truncates/pads proposed cover and old-Omega words: report rates.",
            "Exact equivalence is available to the external evaluator only.",
            "Approximate EQ can miss counterexamples even when budget remains.",
            "12 synthetic worlds are a descriptive pilot, not proof of generalization or autonomy.",
        ],
    }


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--output",required=True,type=Path)
    args=parser.parse_args()
    result=run()
    args.output.parent.mkdir(parents=True,exist_ok=True)
    data=(json.dumps(result,sort_keys=True,indent=2,ensure_ascii=False)+"\n").encode()
    args.output.write_bytes(data)
    print(json.dumps({
        "experiment":EXPERIMENT,"status":result["status"],
        "primary":result["comparison"][str(PRIMARY)],
        "secondary":result["comparison"][str(BUDGETS[0])],
        "report_sha256":sha256(data).hexdigest(),
    },sort_keys=True))


if __name__=="__main__":
    main()
