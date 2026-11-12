"""Question-only translations frozen before opening the evaluator artifact.

Usage: python3 recompute_gsm8k.py
The benchmark gate publishes the 8B answer only if it matches a determinate
recomputation. The peer gate publishes the same answer only if 1B agrees.
Each gate receives one check per question. Human translation time is not
equated to a model call.
"""
import json
from fractions import Fraction as F
from math import ceil

# Keyed by the fixed, question-only artifact from run 43309000277.
results = {
    1: (12 - 2 * 2) * 20 * F(3, 4),
    2: 300 * 20 * 10,
    3: 9 + (9 + 5) + (9 + 5 - 3),
    4: 1000 * F(80, 100),
    5: (1200 + 250 + 2 * 75) * F(1, 100),
    6: 15 - 7 + 5,
    7: 5 / (F(1, 4) * F(1, 2)),
    8: F(80 * 15, 5 * 8 * 60) * 100,
    9: (50 + 20 + F(2, 5) * 20) * 2,
    10: F(40, 2) + 5 - 2,
    11: 3 * F(341 - 12, 1 + 3 + 3) + 12,
    12: 400 * F(80, 100),
    13: F(2 * 30, 4) * 5,
    14: F(70 - 2 * 20, 4 - 2),
    15: None,  # "Twice as many" could refer to one day or the two days combined.
    16: 30 * F(9, 10) / 3 + 40 * F(1, 2) + 40 * F(1, 2) * 3,
    17: 16 - 12 + 4,
    18: 120000 * F(3, 4),
    19: ceil(F(80, 2000 // 75)),  # Each flagstone must fit on a single truck.
    20: F(27000, 3) * F(100, 500),
    21: F(900, 1000) * 5 * 30,  # The energy unit is kWh.
    22: F(320 + 32, 8),
    23: (400 + 2 * 400) * (1 + F(3, 4)),
    24: 8 * F(1, 2) + 2,  # Read "$0.50 cents" as fifty cents.
}
notes = {
    15: "Ambiguous antecedent; 500 if Friday is twice either day, 750 if it is twice both days combined.",
    19: "A truck holds at most floor(2000/75)=26 intact stones. Three trucks hold 78, so four are needed.",
    21: "Energy in kWh, although the question says kilowatts.",
    24: "Treat the redundant wording '$0.50 cents' as 50 cents.",
}
assert set(results) == set(range(1, 25))
assert all(x is None or isinstance(x, (int, F)) for x in results.values())
if __name__ == "__main__":
    print(json.dumps({i: {"answer": str(x) if x is not None else None, "note": notes.get(i)} for i,x in results.items()}, indent=2))
