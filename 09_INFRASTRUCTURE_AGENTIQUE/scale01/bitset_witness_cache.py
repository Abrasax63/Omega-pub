"""Exact finite-observation witness sets with bitset intersection.

This is standard set filtering / bitmap dynamic programming, not a new theorem.
Every bit is one *distinct initial microscopic state* s; it is never a macro
equivalence class. The bitset for w contains precisely all s such that
(pi(s), pi(T(s)), ..., pi(T^(len(w)-1)(s))) == w.
"""
from collections import OrderedDict
from dataclasses import dataclass
from witness_cache import validate,trace

@dataclass(frozen=True)
class BitsetVerdict:
    admissible: bool
    witness_start: int|None
    observed_trace: tuple[int,...]|None
    first_empty_length: int|None
    survivor_count: int

class ExactBitsetWitnessCache:
    def __init__(self,max_systems=8,max_prefixes=2048,max_states=8192,max_word_length=2048):
        if any(type(x) is not int or x<1 for x in
               (max_systems,max_prefixes,max_states,max_word_length)):
            raise ValueError("all capacities must be positive integers")
        self.max_systems=max_systems
        self.max_prefixes=max_prefixes
        self.max_states=max_states
        self.max_word_length=max_word_length
        self.systems=OrderedDict()
        self.prefixes=OrderedDict()
        self.cache_hits=0
        self.system_evictions=0
        self.prefix_evictions=0
        self.orbit_extensions=0
        self.bitset_intersections=0

    def _system(self,T,pi):
        key=(T,pi)
        cached=self.systems.get(key)
        if cached is not None:
            self.systems.move_to_end(key)
            return cached
        obj={"images":tuple(range(len(T))),"masks":[]}
        self.systems[key]=obj
        if len(self.systems)>self.max_systems:
            old,_=self.systems.popitem(last=False)
            self.system_evictions+=1
            # Invalidation is essential: a prefix state cannot outlive the
            # exact microscopic domain to which its orbit mask belongs.
            for p in list(self.prefixes):
                if p[:2]==old:
                    del self.prefixes[p]
        return obj

    def _mask_at(self,obj,T,pi,index,label):
        # Every system-level mask M_i(a) is generated from the exact T^i orbit.
        while len(obj["masks"])<=index:
            images=obj["images"]
            masks={}
            for start,current in enumerate(images):
                colour=pi[current]
                masks[colour]=masks.get(colour,0)|(1<<start)
            obj["masks"].append(masks)
            obj["images"]=tuple(T[x] for x in images)
            self.orbit_extensions+=1
        return obj["masks"][index].get(label,0)

    def _state(self,T,pi,word):
        validate(T,pi,word)
        n=len(T)
        if n>self.max_states or len(word)>self.max_word_length:
            raise ValueError("STATE_OR_WORD_EXCEEDS_EXPLICIT_EXPERIMENT_LIMIT")
        obj=self._system(T,pi)
        start_at=0
        survivors=(1<<n)-1
        first_empty=None
        for j in range(len(word),0,-1):
            key=(T,pi,word[:j])
            if key in self.prefixes:
                start_at=j
                survivors,first_empty=self.prefixes[key]
                self.prefixes.move_to_end(key)
                self.cache_hits+=1
                break
        for i in range(start_at,len(word)):
            survivors &= self._mask_at(obj,T,pi,i,word[i])
            self.bitset_intersections+=1
            if not survivors and first_empty is None:
                first_empty=i+1
            key=(T,pi,word[:i+1])
            self.prefixes[key]=(survivors,first_empty)
            self.prefixes.move_to_end(key)
            if len(self.prefixes)>self.max_prefixes:
                self.prefixes.popitem(last=False)
                self.prefix_evictions+=1
        return survivors,first_empty

    def check(self,T,pi,word):
        survivors,first=self._state(T,pi,word)
        if not survivors:
            return BitsetVerdict(False,None,None,first,0)
        start=(survivors & -survivors).bit_length()-1
        observations=trace(T,pi,start,len(word))
        if observations!=word:
            raise AssertionError("MICROSCOPIC_WITNESS_RECONSTRUCTION_FAILURE")
        return BitsetVerdict(True,start,observations,None,survivors.bit_count())

    def all_initial_witnesses(self,T,pi,word):
        """Exact distinct initial states; enumerate only when explicitly needed."""
        surviving,_=self._state(T,pi,word)
        starts=[]
        while surviving:
            bit=surviving & -surviving
            starts.append(bit.bit_length()-1)
            surviving ^= bit
        return tuple(starts)

    def counters(self):
        return {
            "cache_hits":self.cache_hits,
            "system_evictions":self.system_evictions,
            "prefix_evictions":self.prefix_evictions,
            "orbit_extensions":self.orbit_extensions,
            "bitset_intersections":self.bitset_intersections,
            "live_systems":len(self.systems),
            "live_prefix_states":len(self.prefixes),
        }
