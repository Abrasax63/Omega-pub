"""Compare explicit-path evidence to the BuildKit parser on a scoped excerpt."""
import json
import re
from pathlib import Path
from time import perf_counter

from provenance_xtrace import extract_buildkit_copy, fixed_verdict

TARGET = "rootfs/etc/nsswitch.conf"
SOURCE = "/etc/nsswitch.conf"


def exact_path(log, output):
    lines = [re.sub(r"^\ufeff?\d{4}-\d\d-\d\dT\S+Z ", "", l) for l in log.splitlines()]
    commands = [(i,m[1],m[2]) for i,l in enumerate(lines)
                if (m:=re.fullmatch(r"(#\d+) [0-9.]+ \+ cp -av ([\w./-]+) "+re.escape(output), l))]
    if len(commands) != 1:
        return False
    i,step,source = commands[0]
    if any(l.startswith(step+" ERROR:") for l in lines):
        return False
    reported = [j for j,l in enumerate(lines) if re.fullmatch(
        re.escape(step)+r" [0-9.]+ '"+re.escape(source)+"' -> '"+re.escape(output)+"'",l)]
    done = [j for j,l in enumerate(lines) if re.fullmatch(re.escape(step)+r" DONE [0-9.]+s",l)]
    return len(reported)==len(done)==1 and i<reported[0]<done[0]


def main():
    tick = perf_counter()
    s = Path("dev-excerpt.log").read_text()
    assert fixed_verdict(extract_buildkit_copy(s,TARGET)) == "indéterminé"
    assert exact_path(s,TARGET)
    wrong = s.replace(f"'{SOURCE}' -> '{TARGET}'",f"'{SOURCE}' -> '{TARGET}.other'")
    cached = re.sub(r"DONE [0-9.]+s", "CACHED", s)
    assert not exact_path(wrong,TARGET) and not exact_path(cached,TARGET)
    print(json.dumps(dict(old_confirmations=0,candidate_trace_matches=1,
                          adverse_abstentions=2,truth_ground_verified=False,
                          seconds=perf_counter()-tick),indent=2))

if __name__=="__main__":
    main()
