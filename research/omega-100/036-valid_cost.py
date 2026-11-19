"""Measure decoder overhead on the valid slice of the same reserve."""
import json
from statistics import median
from time import perf_counter_ns

from probe import HOLD, reference, reserve
from wire_guard import route


def main():
    data = [args for args, status in reserve() if status == HOLD]
    arms = [(0, reference), (1, route)]
    timings = [[], []]
    for i in range(200):
        for j, function in arms if i%2 == 0 else reversed(arms):
            start = perf_counter_ns()
            assert all(function(*args)['status'] == HOLD for args in data)
            timings[j].append(perf_counter_ns() - start)
    print(json.dumps(dict(valid_cases=len(data), repetitions=200,
                          reference_median_ns=median(timings[0]), candidate_median_ns=median(timings[1]))))


if __name__=='__main__':
    main()
