"""Sweep all first reads on one C3 observation with an unseen state."""
from collections import Counter

from audit_v19_bounded_completions import enumerate_shadows


def main():
    n = 10
    cycle = (0, 1, 2)
    paths = ((7, 5, 3), (8, 6, 4))
    counts = Counter()
    for side, path in enumerate(paths):
        for image in range(n):
            attempts, admitted, shadows = enumerate_shadows(n, cycle, paths, side, image)
            if image == path[-1]:
                assert len(shadows) > 1, "loop control must remain ambiguous"
                continue
            if not shadows:
                verdict = "infeasible"
            elif len(shadows) == 1:
                verdict = "unique"
            else:
                verdict = "ambiguous"
            counts[verdict] += 1
            counts["attempts"] += attempts
            counts["admitted"] += admitted
            print(side, image, admitted, verdict, sorted(map(len, shadows)))
    print(dict(counts))


if __name__ == "__main__":
    main()
