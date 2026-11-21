"""Conservative adaptive activation of *exact* bitset witnesses.

All modes return the same original Verdict type. The compressed engine
retains exact multiplicity and all initial witnesses internally; this router
uses the sufficient projection needed by existing source-gluing callers.
When the microscopic system is new, no bitset or orbit mask is allocated.
"""
from collections import OrderedDict
from witness_cache import NaiveExact,Verdict,validate
from bitset_witness_cache import ExactBitsetWitnessCache


class AdaptiveBitsetRouter:
    def __init__(self,mode="off",max_tracked_systems=32,max_prefixes=2048,max_bitset_systems=8):
        if mode not in ("off","bitset","adaptive-bitset"):
            raise ValueError("unsupported routing mode")
        if type(max_tracked_systems) is not int or max_tracked_systems<1:
            raise ValueError("max_tracked_systems must be positive")
        self.mode=mode
        self.max_tracked_systems=max_tracked_systems
        self.seen=OrderedDict()
        self.direct=NaiveExact()
        self.compressed=ExactBitsetWitnessCache(
            max_systems=max_bitset_systems,max_prefixes=max_prefixes)
        self.direct_calls=0
        self.compressed_calls=0
        self.tracking_evictions=0

    def check(self,T,pi,word):
        validate(T,pi,word)
        if self.mode=="off":
            self.direct_calls+=1
            return self.direct.check(T,pi,word)
        if self.mode=="bitset":
            self.compressed_calls+=1
            out=self.compressed.check(T,pi,word)
        else:
            key=(T,pi)
            count=self.seen.get(key,0)
            self.seen[key]=min(count+1,2)
            self.seen.move_to_end(key)
            if len(self.seen)>self.max_tracked_systems:
                self.seen.popitem(last=False)
                self.tracking_evictions+=1
            if count==0:
                self.direct_calls+=1
                return self.direct.check(T,pi,word)
            self.compressed_calls+=1
            out=self.compressed.check(T,pi,word)
        return Verdict(out.admissible,out.witness_start,
                       out.observed_trace,out.first_empty_length)

    def counters(self):
        return {
            "mode":self.mode,
            "direct_calls":self.direct_calls,
            "bitset_calls":self.compressed_calls,
            "bitset_hits":self.compressed.cache_hits,
            "bitset_prefix_entries":len(self.compressed.prefixes),
            "bitset_live_systems":len(self.compressed.systems),
            "tracked_systems":len(self.seen),
            "tracking_evictions":self.tracking_evictions,
            "direct_propagation_steps":self.direct.update_steps,
            "bitset_intersections":self.compressed.bitset_intersections,
        }
