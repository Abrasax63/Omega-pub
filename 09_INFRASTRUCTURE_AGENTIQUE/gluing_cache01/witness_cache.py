"""Exact witness-preserving prefix cache for finite observed deterministic systems.

The cache stores surviving microscopic state pairs (initial, current), indexed
by ALL transition / observation data and by the observed word prefix. It never
identifies two systems merely because their macro graph Q is the same.

Invariant: after reading w the stored pairs (s,x) are exactly the states s
whose first len(w) observations equal w, with x=T^len(w)(s).
Proof: induction on the length, filtering by pi[x]==next letter then moving T.
This is standard dynamic programming, not a newly claimed mathematical result.
"""
from collections import OrderedDict
from dataclasses import dataclass
from typing import NamedTuple

class State(NamedTuple):
    pairs: tuple[tuple[int,int],...]
    first_empty_length: int|None

@dataclass(frozen=True)
class Verdict:
    admissible: bool
    witness_start: int|None
    observed_trace: tuple[int,...]|None
    first_empty_length: int|None

def validate(T,pi,word):
    if not isinstance(T,tuple) or not isinstance(pi,tuple) or not isinstance(word,tuple):
        raise TypeError("immutable tuple inputs required")
    n=len(T)
    if n==0 or len(pi)!=n or any(type(x) is not int or not 0<=x<n for x in T):
        raise ValueError("invalid finite total function")
    if any(type(y) is not int or y<0 for y in pi+word):
        raise ValueError("invalid observation labels")

def trace(T,pi,start,length):
    result=[]
    for _ in range(length):
        result.append(pi[start]); start=T[start]
    return tuple(result)

def step(T,pi,state,letter,length):
    next_pairs=tuple((s,T[x]) for s,x in state.pairs if pi[x]==letter)
    first=state.first_empty_length
    if not next_pairs and first is None:
        first=length
    return State(next_pairs,first),len(state.pairs)

def verdict(T,pi,word,state):
    if not state.pairs:
        return Verdict(False,None,None,state.first_empty_length)
    start=min(s for s,_ in state.pairs)
    observed=trace(T,pi,start,len(word))
    assert observed==word, ("MICRO_WITNESS_CACHE_INVARIANT_BROKEN",T,pi,word)
    return Verdict(True,start,observed,None)

class NaiveExact:
    """Exact baseline: reprocess every query from every microscopic state."""
    def __init__(self):
        self.pair_visits=0
        self.update_steps=0
    def check(self,T,pi,word):
        validate(T,pi,word)
        state=State(tuple((s,s) for s in range(len(T))),None)
        for i,a in enumerate(word,1):
            state,visits=step(T,pi,state,a,i)
            self.pair_visits+=visits
            self.update_steps+=1
        return verdict(T,pi,word,state)

class WitnessCache:
    """Bounded LRU indexed by complete finite system and observation prefix."""
    def __init__(self,max_entries=4096):
        if type(max_entries) is not int or max_entries<1:
            raise ValueError("capacity must be a positive integer")
        self.max_entries=max_entries
        self.memo=OrderedDict()
        self.pair_visits=0
        self.update_steps=0
        self.cache_hits=0
        self.evictions=0

    def check(self,T,pi,word):
        validate(T,pi,word)
        j=0
        state=State(tuple((s,s) for s in range(len(T))),None)
        for k in range(len(word),0,-1):
            key=(T,pi,word[:k])
            if key in self.memo:
                j=k;state=self.memo[key]
                self.memo.move_to_end(key)
                self.cache_hits+=1
                break
        for i in range(j+1,len(word)+1):
            state,visits=step(T,pi,state,word[i-1],i)
            self.pair_visits+=visits
            self.update_steps+=1
            key=(T,pi,word[:i])
            self.memo[key]=state
            self.memo.move_to_end(key)
            if len(self.memo)>self.max_entries:
                self.memo.popitem(last=False)
                self.evictions+=1
        return verdict(T,pi,word,state)
