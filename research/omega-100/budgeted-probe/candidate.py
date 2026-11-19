"""Test low masks before graph propagation, with one shared counter."""
from time import perf_counter

from rule import choose
from solver import Cap, OutOfBudget, graph_parity, solve

PROBE_LIMIT = 42
DENSE_THRESHOLD = 22


def solve_budgeted(case):
    method = choose(case)
    if case['kind'] != 'parity' or method != 'B' or len(case['edges']) < DENSE_THRESHOLD:
        return dict(solve(case,method),phase='ordinary',probe_steps=0)
    meter = Cap()
    start = perf_counter()

    def probe_tick():
        if meter.used >= PROBE_LIMIT:
            raise OutOfBudget
        meter.tick()

    try:
        for mask in (1,2):
            probe_tick()
            for a,b,p in case['edges']:
                probe_tick()
                if (((mask>>a)^(mask>>b))&1) != p:
                    break
            else:
                return dict(answer=True,witness=mask,steps=meter.used,probe_steps=meter.used,
                            phase='probe',seconds=perf_counter()-start)
    except OutOfBudget:
        pass
    probe_work = meter.used
    try:
        answer,witness=graph_parity(case,meter)
    except OutOfBudget:
        answer,witness=None,None
    return dict(answer=answer,witness=witness,steps=meter.used,probe_steps=probe_work,
                phase='fallback',seconds=perf_counter()-start)
