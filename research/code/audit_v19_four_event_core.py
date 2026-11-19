"""Search for inclusion-minimal four-event contradictions over a fixed C4."""
import json
from itertools import product, combinations
from time import perf_counter

from test_v19_locality_l_plus_1 import forced_edges, event_edges, coherent
from audit_v19_shadow_guard import exhaustive_shadow, guarded_shadow

CYCLE = (0, 1, 2, 3)


def audit():
    control = (1, 2, 3, 0)
    edges = forced_edges(control) + event_edges(control, (0, 1), 4)
    assert exhaustive_shadow(4, edges, CYCLE)
    assert guarded_shadow(4, edges, CYCLE) == exhaustive_shadow(4, edges, CYCLE)
    stats = dict(systems=0, skipped_forced_incoherent=0, queries=0, four_edges=0,
                 comparisons=0, errors=0, cores=0, first=None,
                 reference_seconds=0., guard_seconds=0.)

    def compare(edges):
        t = perf_counter()
        expected = exhaustive_shadow(7, edges, CYCLE)
        stats['reference_seconds'] += perf_counter()-t
        t = perf_counter()
        actual = guarded_shadow(7, edges, CYCLE)
        stats['guard_seconds'] += perf_counter()-t
        stats['comparisons'] += 1
        stats['errors'] += actual != expected
        return expected

    for suffix in product(range(7), repeat=3):
        transformation = control + suffix
        stats['systems'] += 1
        forced = forced_edges(transformation)
        if not coherent(7, forced):
            stats['skipped_forced_incoherent'] += 1
            continue
        for pair in combinations(range(7), 2):
            events = event_edges(transformation, pair, 4)
            stats['queries'] += 1
            full = compare(forced+events)
            if len(events) != 4:
                continue
            stats['four_edges'] += 1
            deleted = [compare(forced+events[:i]+events[i+1:]) for i in range(4)]
            if not full and all(deleted):
                stats['cores'] += 1
                if stats['first'] is None:
                    stats['first'] = dict(T=transformation,pair=pair,forced=forced,events=events,
                                          full_size=len(full),deletion_sizes=list(map(len,deleted)))
    assert stats['errors']==0
    return stats


if __name__=='__main__':
    print(json.dumps(audit(),sort_keys=True))
