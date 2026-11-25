"""Count repeated SDL write destinations across two GitHub build steps."""
from hashlib import sha256
import json
from pathlib import Path
import re
from time import perf_counter

from provenance_xtrace import extract, fixed_verdict

STAMP = re.compile(r"^\ufeff?\d{4}-\d\d-\d\dT\S+Z ")
ENTRY = re.compile(r"'(/usr/local/lib/libSDL[^']*)' -> '(/lib/[^']+)'")
STARTS = ('##[group]Run if [ ! -d "deps/SDL2-',
          '##[group]Run sudo cp -av /usr/local/lib/libSDL* ')
ARCH = ("x86_64", "aarch64", "x86_64")
UNKNOWN = "indéterminé"


def blocks(log):
    lines = [STAMP.sub("", line) for line in log.splitlines()]
    result = []
    for marker in STARTS:
        starts = [i for i, line in enumerate(lines) if line.startswith(marker)]
        if len(starts) != 1:
            raise ValueError("step marker is missing or ambiguous")
        start = starts[0]
        body = next(i for i in range(start + 1, len(lines)) if lines[i] == "##[endgroup]") + 1
        end = next((i for i in range(body, len(lines)) if lines[i].startswith("##[group]Run ")), len(lines))
        result.append(lines[body:end])
    return result


def destinations(lines):
    return {m[2] for line in lines if (m := ENTRY.fullmatch(line))}


def candidate(first, second):
    return destinations(first) & destinations(second)


def fixed(first, second, arch):
    prefix = f"'/lib/{arch}-linux-gnu/libSDL"
    def matched(lines):
        entries = (line.split(" -> ", 1) for line in lines if line.startswith("'/usr/local/lib/libSDL"))
        return {right[1:-1] for fields in entries if len(fields) == 2
                for right in fields[1:] if right.startswith(prefix) and right.endswith("'")}
    return matched(first) & matched(second)


def main():
    start = perf_counter()
    evidence = []
    for i, arch in enumerate(ARCH):
        data = Path(f"job{i}.log").read_bytes()
        log = data.decode("utf-8")
        left, right = blocks(log)
        actual = candidate(left, right)
        reference = fixed(left, right, arch)
        target = f"/lib/{arch}-linux-gnu/libSDL2.a"
        assert actual == reference and target in actual
        assert fixed_verdict(extract(log, target)) == UNKNOWN
        assert candidate(left, [line.replace(target, target + ".other") for line in right]) == actual - {target}
        assert candidate(left + left, []) == set()
        evidence.append(dict(log_sha256=sha256(data).hexdigest(), first_count=len(destinations(left)),
                             second_count=len(destinations(right)), collisions=len(actual)))
    print(json.dumps(dict(logs=evidence, equal_to_fixed=3, adverse_passed=6,
                          provenance_verdict="indéterminé", seconds=perf_counter()-start), indent=2))


if __name__ == "__main__":
    main()
