"""Conservative adaptive dispatcher for *exact* finite-observation questions.

'off' = direct precise witness evaluation, 'on' = pinned exact prefix cache.
'adaptive' = first request for a complete (T,pi) gets direct evaluation;
on its second occurrence begin populating a bounded cache. This is a
heuristic for avoiding zero-hit allocation, not a universal optimal policy.

All three paths return exactly the same witness and earliest empty-prefix
certificate. Not for LLM decisions, API answers or approximate similarity.
"""
from collections import OrderedDict
from witness_cache import NaiveExact, WitnessCache, validate

class ExactGluingRouter:
    def __init__(self, mode="off", max_prefixes=2048, max_systems=32):
        if mode not in ("off","on","adaptive"):
            raise ValueError("mode must be off, on or adaptive")
        if type(max_systems) is not int or max_systems<1:
            raise ValueError("max_systems must be positive")
        self.mode=mode
        self.direct=NaiveExact()
        self.cached=WitnessCache(max_entries=max_prefixes)
        self.seen=OrderedDict()
        self.max_systems=max_systems
        self.direct_calls=0
        self.cached_calls=0
        self.system_evictions=0

    def check(self,T,pi,word):
        validate(T,pi,word)
        if self.mode=="off":
            self.direct_calls+=1
            return self.direct.check(T,pi,word)
        if self.mode=="on":
            self.cached_calls+=1
            return self.cached.check(T,pi,word)
        key=(T,pi)
        previous=self.seen.get(key,0)
        self.seen[key]=min(previous+1,2)
        self.seen.move_to_end(key)
        if len(self.seen)>self.max_systems:
            self.seen.popitem(last=False)
            self.system_evictions+=1
        if previous==0:
            self.direct_calls+=1
            return self.direct.check(T,pi,word)
        self.cached_calls+=1
        return self.cached.check(T,pi,word)

    def counters(self):
        return {
            "mode":self.mode,
            "direct_calls":self.direct_calls,
            "cached_calls":self.cached_calls,
            "cache_hits":self.cached.cache_hits,
            "system_evictions":self.system_evictions,
            "prefix_evictions":self.cached.evictions,
            "prefix_cache_entries":len(self.cached.memo),
            "tracked_systems":len(self.seen),
            "steps":self.direct.update_steps+self.cached.update_steps,
            "pair_visits":self.direct.pair_visits+self.cached.pair_visits,
        }
