"""OMEGA-BLACKBOX-01: genuinely hidden Mealy models, actual AALpy L* learners.

All arms use AALpy 1.6.2 run_Lstar; only approximate equivalence testing
differs: RANDOM words, FIXED words, or OMEGA transition-characterization
words. Every actual SUL step is charged against the same per-arm cap.
Exact behavioral equivalence is evaluated independently AFTER training.
"""
from __future__ import annotations

from collections import deque
from copy import deepcopy
from hashlib import sha256
from importlib.metadata import version
from itertools import product
from pathlib import Path
import argparse
import json
import random
import sys

from aalpy.base import SUL, Oracle
from aalpy.learning_algs import run_Lstar

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/"omega-onpolicy-continuation-08"))
import onpolicy_lab as previous  # noqa: E402
from mealy_lab import Mealy,digest  # noqa: E402

EXPERIMENT="OMEGA-BLACKBOX-01"
PREREG="2715f3255ed4527c0a411998a62d48e971e7cc97"
ALPHABET=(0,1)
ARMS=("RANDOM_LSTAR","FIXED_LSTAR","OMEGA_GUIDED_LSTAR")
MAX_EQ_WORDS_PER_ROUND=32
BUDGETS=(700,1400)
PRIMARY_BUDGET=1400
DATASETS=((4,32041,3),(5,32051,3),(6,32061,3))
TEST_WORDS=128
EXTERNAL_LIBRARY_VERSION="1.6.2"


class BudgetExhausted(RuntimeError):
    pass


def true_old_signatures():
    """All previous eight finite-diagnostic experiments (#127 through #135)."""
    old=previous.b.cohorts()
    used=set(previous.m.old_signatures(old))
    for row in previous.m.new_holdouts(old).values():
        used.update(sig for sig,_ in row["machines"])
    _,former=previous.ranking.new_cohorts()
    for row in former.values():
        used.update(sig for sig,_ in row["machines"])
    for row in previous.make_holdouts(old).values():
        used.update(sig for sig,_ in row["machines"])
    if len(used)!=1112:
        raise AssertionError(f"HISTORICAL_SIGNATURE_LEDGER_MISMATCH:{len(used)}")
    return used


def new_machines():
    """No filtering by outcome, reachability or learning difficulty."""
    used=true_old_signatures()
    out=[]
    for count,seed,needed in DATASETS:
        rng=random.Random(seed)
        added=attempts=duplicates=0
        while added<needed:
            attempts+=1
            if attempts>10000:
                raise RuntimeError("UNIQUE_SAMPLING_FAILED")
            machine=Mealy(
                tuple(tuple(rng.randrange(count) for _ in ALPHABET)
                      for _ in range(count)),
                tuple(tuple(rng.randrange(3) for _ in ALPHABET)
                      for _ in range(count)),
            )
            sig=machine.signature()
            if sig in used:
                duplicates+=1
                continue
            used.add(sig)
            out.append({
                "public_id":f"N{count}_{added}",
                "signature":sig,
                "size":count,
                "generation_seed":seed,
                "draws":attempts,
                "iso_collisions_before":duplicates,
                "machine":machine,
            })
            added+=1
    if len(out)!=9 or len(used)!=1112+9:
        raise AssertionError("NEW_WORLD_COHORT_COLLISION")
    return out


def evaluator_step(machine,state,symbol):
    """Only the SUL kernel and heldout evaluator are allowed to inspect truth."""
    if symbol not in ALPHABET:
        raise ValueError("INVALID_INPUT")
    return machine.outputs[state][symbol],machine.transitions[state][symbol]


class MeteredBlackBox(SUL):
    """Resettable query API; no transition/output table exposed to learner."""

    def __init__(self,machine,budget):
        super().__init__()
        self.__world_step=lambda s,a:evaluator_step(machine,s,a)
        self.limit=budget
        self.spent=0
        self.resets=0
        self.complete_queries=0
        self.queries=[]
        self.phase="MQ"
        self._state=0
        self._inflight_inputs=[]
        self._inflight_outputs=[]
        self._inflight_phase=None

    @property
    def remaining(self):
        return self.limit-self.spent

    def pre(self):
        # Reset means the SAME initial physical state 0 each time.
        self._state=0
        self.resets+=1
        self._inflight_inputs=[]
        self._inflight_outputs=[]
        self._inflight_phase=self.phase

    def step(self,letter):
        if letter not in ALPHABET:
            raise ValueError("UNSUPPORTED_INPUT")
        if self.remaining<=0:
            raise BudgetExhausted("SUL symbol budget exhausted")
        observation,self._state=self.__world_step(self._state,letter)
        self.spent+=1
        self._inflight_inputs.append(letter)
        self._inflight_outputs.append(observation)
        return observation

    def post(self):
        if self._inflight_inputs:
            self.queries.append({
                "inputs":list(self._inflight_inputs),
                "outputs":list(self._inflight_outputs),
                "charge":len(self._inflight_inputs),
                "phase":self._inflight_phase,
            })
            self.complete_queries+=1
        self._inflight_inputs=[]
        self._inflight_outputs=[]
        self._inflight_phase=None

    def finish_incomplete(self):
        """Charge interrupted steps and keep an explicit partial-query audit."""
        if self._inflight_inputs:
            self.queries.append({
                "inputs":list(self._inflight_inputs),
                "outputs":list(self._inflight_outputs),
                "charge":len(self._inflight_inputs),
                "phase":self._inflight_phase,
                "incomplete_due_to_budget":True,
            })
            self._inflight_inputs=[]
            self._inflight_outputs=[]
            self._inflight_phase=None

    def summary(self):
        self.finish_incomplete()
        ledger=sum(row["charge"] for row in self.queries)
        if ledger!=self.spent or self.spent>self.limit:
            raise AssertionError("METERED_STEPS_NOT_RECONCILED")
        return {
            "budget_cap":self.limit,"spent_symbols":self.spent,
            "unspent_symbols":self.remaining,
            "reset_calls":self.resets,
            "completed_queries":self.complete_queries,
            "logged_queries":len(self.queries),
            "by_phase_spent":{
                phase:sum(row["charge"] for row in self.queries
                          if row["phase"]==phase)
                for phase in ("MQ","EQ")
            },
            "incomplete_queries":sum(
                bool(row.get("incomplete_due_to_budget")) for row in self.queries
            ),
            "queries_sha256":digest(self.queries),
            "query_log":self.queries,
        }


def candidate_access_paths(hypothesis):
    """Read only the proposed hypothesis; never the hidden SUL state."""
    root=hypothesis.initial_state
    todo=deque([(root,())])
    seen={id(root)}
    answer=[]
    while todo and len(answer)<32:
        state,prefix=todo.popleft()
        answer.append((state,prefix))
        for sym in ALPHABET:
            successor=state.transitions[sym]
            if id(successor) not in seen:
                seen.add(id(successor))
                todo.append((successor,prefix+(sym,)))
    return answer


def distinguishing_suffix(left,right,max_length=8):
    """Find a shortest distinguishing word using ONLY hypothesis transitions."""
    todo=deque([(left,right,())])
    seen={(id(left),id(right))}
    while todo:
        a,b,prefix=todo.popleft()
        if len(prefix)>=max_length:
            continue
        for sym in ALPHABET:
            seq=prefix+(sym,)
            if a.output_fun[sym]!=b.output_fun[sym]:
                return seq
            aa,bb=a.transitions[sym],b.transitions[sym]
            key=(id(aa),id(bb))
            if key not in seen:
                seen.add(key)
                todo.append((aa,bb,seq))
    return ()


class CandidateOracle(Oracle):
    """Fair-budget approximate equivalence tester, NOT an exact equivalence oracle."""

    def __init__(self,alphabet,sul,mode,seed):
        super().__init__(list(alphabet),sul)
        if mode not in ARMS:
            raise ValueError("INVALID_MODE")
        self.mode=mode
        self.rng=random.Random(seed)
        self.eq_rounds=0
        self.words_tested=0
        self.counterexamples=0
        self.fixed_index=0
        self.edge_counts={}
        self.last_candidate=None
        self.last_candidate_state_count=None
        self.rounds_log=[]

    def fixed_word(self):
        # Stable length/lexicographic schedule, independent of the black box.
        index=self.fixed_index
        self.fixed_index+=1
        for length in range(3,12):
            num=2**length
            if index<num:
                return tuple((index>>bit)&1 for bit in range(length-1,-1,-1))
            index-=num
        self.fixed_index=0
        return self.fixed_word()

    def random_word(self):
        length=self.rng.randint(3,11)
        return tuple(self.rng.choice(ALPHABET) for _ in range(length))

    def guided_word(self,hypothesis):
        """State/edge cover + characterization suffix, all from current guess."""
        access=candidate_access_paths(hypothesis)
        edges=[]
        for state,prefix in access:
            for symbol in ALPHABET:
                key=(state.state_id,symbol)
                score=self.edge_counts.get(key,0)
                edges.append((score,len(prefix),prefix,symbol,state))
        if not edges:
            return self.random_word()
        # Probe a least-tested conjectured transition; ties vary deterministically.
        min_score=min(row[0] for row in edges)
        tied=[row for row in edges if row[0]==min_score]
        _,_,prefix,symbol,state=self.rng.choice(tied)
        key=(state.state_id,symbol)
        self.edge_counts[key]=self.edge_counts.get(key,0)+1
        destination=state.transitions[symbol]
        others=[s for s,_ in access if s is not destination]
        if others:
            other=self.rng.choice(others)
            suffix=distinguishing_suffix(destination,other,max_length=6)
        else:
            suffix=()
        if not suffix:
            suffix=tuple(self.rng.choice(ALPHABET)
                         for _ in range(self.rng.randint(1,6)))
        word=prefix+(symbol,)+suffix
        if len(word)<3:
            word+=tuple(self.rng.choice(ALPHABET)
                        for _ in range(3-len(word)))
        return word[:16]

    def next_word(self,hypothesis):
        if self.mode=="FIXED_LSTAR":
            return self.fixed_word()
        if self.mode=="RANDOM_LSTAR":
            return self.random_word()
        # Fixed small random exploratory component: no target consultation.
        if self.rng.random()<0.10:
            return self.random_word()
        return self.guided_word(hypothesis)

    def find_cex(self,hypothesis):
        self.eq_rounds+=1
        self.last_candidate=deepcopy(hypothesis)
        self.last_candidate_state_count=len(hypothesis.states)
        checks=0
        found=False
        self.sul.phase="EQ"
        try:
            for _ in range(MAX_EQ_WORDS_PER_ROUND):
                word=self.next_word(hypothesis)
                if not word:
                    raise AssertionError("EMPTY_EQ_CANDIDATE_WORD")
                if len(word)>self.sul.remaining:
                    # An unexecutable test is NOT evidence of equivalence.
                    # Propagate to train_one as an interrupted, unverified model.
                    raise BudgetExhausted(
                        "INSUFFICIENT_BUDGET_TO_TEST_EQ_CANDIDATE"
                    )
                predicted=tuple(hypothesis.compute_output_seq(
                    hypothesis.initial_state,word))
                observed=tuple(self.sul.query(word))
                self.words_tested+=1
                checks+=1
                if observed!=predicted:
                    found=True
                    self.counterexamples+=1
                    return word
            return None
        finally:
            self.rounds_log.append({
                "round":self.eq_rounds,
                "hypothesis_states":len(hypothesis.states),
                "checks":checks,
                "counterexample_found":found,
                "remaining_budget":self.sul.remaining,
            })
            self.sul.phase="MQ"


def predict_mealy(hypothesis,word):
    if hypothesis is None:
        return None
    state=hypothesis.initial_state
    result=[]
    for a in word:
        result.append(state.output_fun[a])
        state=state.transitions[a]
    return tuple(result)


def truth_trace(machine,word):
    state=0
    result=[]
    for a in word:
        y,state=evaluator_step(machine,state,a)
        result.append(y)
    return tuple(result)


def exact_equivalence(machine,hypothesis):
    """Finite product BFS, evaluator-only, returning a shortest counterexample."""
    if hypothesis is None:
        return {"status":"NO_HYPOTHESIS","counterexample":None,"pairs":0}
    queue=deque([(0,hypothesis.initial_state,())])
    seen={(0,id(hypothesis.initial_state))}
    while queue:
        actual,guess,prefix=queue.popleft()
        for a in ALPHABET:
            if machine.outputs[actual][a]!=guess.output_fun[a]:
                word=prefix+(a,)
                if truth_trace(machine,word)==predict_mealy(hypothesis,word):
                    raise AssertionError("WRONG_BFS_COUNTEREXAMPLE")
                return {
                    "status":"NOT_EQUIVALENT",
                    "counterexample":list(word),
                    "shortest_counterexample_length":len(word),
                    "pairs":len(seen),
                }
            actual_next=machine.transitions[actual][a]
            guess_next=guess.transitions[a]
            key=(actual_next,id(guess_next))
            if key not in seen:
                seen.add(key)
                queue.append((actual_next,guess_next,prefix+(a,)))
    return {
        "status":"EXACT_EQUIVALENT",
        "counterexample":None,
        "shortest_counterexample_length":None,
        "pairs":len(seen),
    }


def accessible_states(machine):
    todo=[0]
    seen={0}
    while todo:
        v=todo.pop()
        for a in ALPHABET:
            w=machine.transitions[v][a]
            if w not in seen:
                seen.add(w)
                todo.append(w)
    return len(seen)


def reserved_words(n,j):
    rng=random.Random(880000+100*n+j)
    words=set()
    while len(words)<TEST_WORDS:
        length=rng.randint(12,20)
        words.add(tuple(rng.choice(ALPHABET) for _ in range(length)))
    return sorted(words)


def heldout_score(machine,hypothesis,words,queried):
    """Never trains or updates the hypothesis; excludes exact overlap."""
    unique=[w for w in words if w not in queried]
    if not unique:
        raise AssertionError("HELDOUT_ALL_QUERIED")
    word_matches=symbol_matches=symbols=0
    incorrect=[]
    for word in unique:
        truth=truth_trace(machine,word)
        guess=predict_mealy(hypothesis,word)
        if guess is not None:
            word_matches+=int(guess==truth)
            symbol_matches+=sum(x==y for x,y in zip(truth,guess))
        symbols+=len(word)
        if guess!=truth and len(incorrect)<8:
            incorrect.append({
                "input":list(word),"expected":list(truth),
                "predicted":list(guess) if guess is not None else None,
            })
    return {
        "requested_test_words":len(words),
        "excluded_identical_train_queries":len(words)-len(unique),
        "evaluated_test_words":len(unique),
        "whole_word_accuracy":word_matches/len(unique),
        "symbol_accuracy":symbol_matches/symbols,
        "correct_whole_words":word_matches,
        "correct_symbols":symbol_matches,
        "total_symbols":symbols,
        "incorrect_examples":incorrect,
    }


def train_one(machine,arm,budget,seed):
    """Only queries through metered SUL; no true model queries by learner."""
    sul=MeteredBlackBox(machine,budget)
    oracle=CandidateOracle(ALPHABET,sul,arm,seed)
    model=None
    status="NO_HYPOTHESIS"
    exception=None
    try:
        model=run_Lstar(list(ALPHABET),sul,oracle,automaton_type="mealy",
                        cache_and_non_det_check=False,print_level=0)
        status="PROVISIONAL_LSTAR_COMPLETED"
    except BudgetExhausted:
        model=oracle.last_candidate
        status=("BUDGET_INTERRUPTED_WITH_CANDIDATE"
                if model is not None else "BUDGET_INTERRUPTED_NO_CANDIDATE")
    except Exception as ex:
        # Infrastructure / code failure is not a negative scientific result.
        raise RuntimeError(f"LEARNER_ERROR:{arm}:{type(ex).__name__}:{ex}") from ex
    if model is not None:
        # Fail closed: incomplete state transition/output tables are not models.
        for st in model.states:
            if any(a not in st.transitions or a not in st.output_fun
                   for a in ALPHABET):
                raise AssertionError("INCOMPLETE_LSTAR_MODEL")
    ledger=sul.summary()
    queried={
        tuple(x["inputs"]) for x in ledger["query_log"]
        if not x.get("incomplete_due_to_budget")
    }
    return model,queried,{
        "arm":arm,"status":status,
        "model_states":len(model.states) if model is not None else None,
        "exception":exception,
        "equivalence_search_rounds":oracle.eq_rounds,
        "equivalence_words_tested":oracle.words_tested,
        "counterexamples_seen":oracle.counterexamples,
        "equivalence_round_log":oracle.rounds_log,
        "ledger":ledger,
    }


def execute_one(world,n,j,arm,budget):
    seed=500000+1000*n+20*j+budget
    model,queried,train=train_one(world,arm,budget,seed)
    test=heldout_score(world,model,reserved_words(n,j),queried)
    exact=exact_equivalence(world,model)
    if exact["status"]=="EXACT_EQUIVALENT" and test["whole_word_accuracy"]!=1:
        raise AssertionError("EXACT_EQUIVALENCE_DISAGREES_WITH_TEST")
    return {
        "train":train,
        "independent_exact_equivalence":exact,
        "reserved_word_evaluation":test,
    }


def conduct():
    if version("aalpy")!=EXTERNAL_LIBRARY_VERSION:
        raise RuntimeError("AALPY_VERSION_NOT_PINNED")
    worlds=new_machines()
    rows=[]
    for size,seed,needed in DATASETS:
        group=[row for row in worlds if row["size"]==size]
        for j,meta in enumerate(group):
            world=meta["machine"]
            evaluations={}
            for budget in BUDGETS:
                evaluations[str(budget)]={
                    arm:execute_one(world,size,j,arm,budget)
                    for arm in ARMS
                }
            rows.append({
                "public_id":meta["public_id"],
                "canonical_signature":meta["signature"],
                "size":size,
                "reachable_physical_states":accessible_states(world),
                "machine_generation_seed":meta["generation_seed"],
                "attempts_at_generation":meta["draws"],
                "duplicate_signature_rejections":meta["iso_collisions_before"],
                "sealed_world_sha256":digest({
                    "transitions":world.transitions,
                    "outputs":world.outputs,"initial_state":0
                }),
                # Audit-only sealed truth: not provided to any learner.
                "evaluator_only_truth":{
                    "transitions":world.transitions,
                    "outputs":world.outputs,
                    "initial_state":0,
                },
                "budgets":evaluations,
            })
    comparisons={}
    for budget in BUDGETS:
        q=str(budget)
        numbers={}
        for arm in ARMS:
            arms=[x["budgets"][q][arm] for x in rows]
            numbers[arm]={
                "exact_equivalent_models":sum(
                    x["independent_exact_equivalence"]["status"]=="EXACT_EQUIVALENT"
                    for x in arms
                ),
                "models_produced":sum(x["train"]["model_states"] is not None
                                      for x in arms),
                "mean_whole_word_accuracy":sum(
                    x["reserved_word_evaluation"]["whole_word_accuracy"]
                    for x in arms)/len(arms),
                "mean_symbol_accuracy":sum(
                    x["reserved_word_evaluation"]["symbol_accuracy"]
                    for x in arms)/len(arms),
                "total_spent_symbols":sum(
                    x["train"]["ledger"]["spent_symbols"] for x in arms
                ),
                "total_approximate_eq_words":sum(
                    x["train"]["equivalence_words_tested"] for x in arms
                ),
            }
        comparisons[q]=numbers
    scores=comparisons[str(PRIMARY_BUDGET)]
    omega=scores["OMEGA_GUIDED_LSTAR"]
    refs=[scores["RANDOM_LSTAR"],scores["FIXED_LSTAR"]]
    success=(
        all(omega["exact_equivalent_models"]>x["exact_equivalent_models"]
            for x in refs)
        and all(omega["mean_whole_word_accuracy"]+1e-12>=x["mean_whole_word_accuracy"]
                for x in refs)
    )
    state=("DESCRIPTIVE_QUERY_GAIN" if success
           else "NO_DEMONSTRATED_QUERY_GAIN")
    report={
        "experiment":EXPERIMENT,
        "preregistered_commit":PREREG,
        "status":state,
        "external_algorithm":"AALpy run_Lstar, automaton_type=mealy",
        "external_dependency_version":version("aalpy"),
        "learning_modes":list(ARMS),
        "same_learning_backend_for_all_arms":True,
        "same_budget_caps_for_all_arms":True,
        "actual_costs_may_differ":True,
        "exact_oracle_evaluation_only":True,
        "target_machine_hidden_from_learners":True,
        "no_paid_api":True,
        "main_modified":False,
        "general_scientific_gain_proven":False,
        "world_manifest": [{
            k:row[k] for k in (
                "public_id","canonical_signature","size",
                "reachable_physical_states","machine_generation_seed",
                "attempts_at_generation","duplicate_signature_rejections",
                "sealed_world_sha256"
            )
        } for row in rows],
        "budget_caps":list(BUDGETS),
        "primary_budget":PRIMARY_BUDGET,
        "equivalence_test_approximate_word_limit":MAX_EQ_WORDS_PER_ROUND,
        "reserved_words_per_machine":TEST_WORDS,
        "comparisons":comparisons,
        "machines":rows,
        "limitations":[
            "The input/output transition system is unknown to the learners, but available to independent evaluator.",
            "All three methods are pre-existing AALpy L* with different approximate equivalence-test scheduling.",
            "OMEGA-guided here is a candidate scheduling heuristic, not a continuously autonomous Omega agent.",
            "AALpy approximate equivalence test exhaustion is not an exact equivalence certificate.",
            "All arms share budget caps, NOT necessarily actual query cost.",
            "9 synthetic random systems are an initial pilot, not independent scientific validation.",
            "Unreachable/unobservable physical states do not prevent behavioral equivalence of initial-state behavior.",
            "The exact BFS equivalence oracle never trains any of the three models.",
            "No language model, no paid API, no autonomous self-modification.",
        ],
    }
    for world in rows:
        for budget in BUDGETS:
            for arm in ARMS:
                item=world["budgets"][str(budget)][arm]
                ledger=item["train"]["ledger"]
                if ledger["spent_symbols"]>budget:
                    raise AssertionError("BUDGET_VIOLATION")
                if ledger["by_phase_spent"]["MQ"]+ledger["by_phase_spent"]["EQ"]!=ledger["spent_symbols"]:
                    raise AssertionError("ACCOUNTING_BY_PHASE_FAILED")
                if item["independent_exact_equivalence"]["status"]=="EXACT_EQUIVALENT":
                    if item["reserved_word_evaluation"]["whole_word_accuracy"]!=1:
                        raise AssertionError("CERTIFIED_EQ_MUST_HAVE_FULL_TEST_ACCURACY")
    return report


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--output",type=Path,required=True)
    args=parser.parse_args()
    result=conduct()
    args.output.parent.mkdir(parents=True,exist_ok=True)
    data=(json.dumps(result,ensure_ascii=False,sort_keys=True,indent=2)+"\n").encode()
    args.output.write_bytes(data)
    print(json.dumps({
        "experiment":EXPERIMENT,
        "status":result["status"],
        "dependency":result["external_dependency_version"],
        "primary_budget":PRIMARY_BUDGET,
        "primary_results":result["comparisons"][str(PRIMARY_BUDGET)],
        "secondary_results":result["comparisons"][str(BUDGETS[0])],
        "report_sha256":sha256(data).hexdigest(),
    },sort_keys=True))


if __name__=="__main__":
    main()
