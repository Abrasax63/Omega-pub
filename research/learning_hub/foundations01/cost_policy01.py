"""Conservative cost policy selected by COST-SELECT01; validity remains independent."""
from invariant_select01 import choose, solve

POLICY_ID="COST-SELECT01-SIMPLE-v1"

def choose_efficient(task,params):
    admissible=choose(task,params)
    method=admissible
    if task=="rule90_histogram" and admissible=="causal_cone":
        if params["n"]-(2*params["h"]+3)<2:
            method="direct"
    return choose(task,params,method)

def solve_efficient(task,params):
    method=choose_efficient(task,params)
    result=solve(task,params,method)
    # The policy metadata is not part of the original outcome digest.
    return {"policy":POLICY_ID,"outcome":result}
