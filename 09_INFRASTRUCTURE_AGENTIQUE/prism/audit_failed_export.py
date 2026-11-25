from pathlib import Path
from time import perf_counter_ns
import json
import re

from audit_release_export import local_scoped, BOUNDARY, LOCAL, PROGRESS

BUILD_COMMAND = re.compile(r"^(?:\d{4}-\d\d-\d\dT\S+Z )?\[command\]\S*docker buildx (?:bake|build)(?: |$)")
ERROR = re.compile(r"^\S+Z (?:(?:##\[error\])|(?:ERROR: failed to solve))")


def successful_local(log):
    pending = set()
    successful = complete = failed = False
    for line in log.splitlines():
        if BOUNDARY.match(line) or BUILD_COMMAND.match(line):
            successful |= complete and not failed
            pending.clear()
            complete = failed = False
        if ERROR.match(line):
            failed = True
        event = PROGRESS.fullmatch(line)
        if not event:
            continue
        vertex, status = event.groups()
        if status.startswith("ERROR:"):
            failed = True
        elif status == LOCAL:
            pending.add(vertex)
        elif status.startswith("DONE ") and vertex in pending:
            complete = True
            pending.remove(vertex)
    return successful or complete and not failed


def main():
    started = perf_counter_ns()
    prefix = "##[group]Run a\n#1 exporting to client directory\n"
    done = "#1 DONE 0.1s\n"
    error = "#2 ERROR: export failed\n"
    assert local_scoped(prefix + done + error) and not successful_local(prefix + done + error)
    assert successful_local(prefix + done)
    assert successful_local(prefix + done + "##[group]Run b\n" + error)
    assert not successful_local(prefix + "##[group]Run b\n" + done)
    results = {}
    for job in (138366782749, 138366782684, 138366782449):
        log = Path(f"{job}.log").read_text()
        results[job] = dict(fixed=local_scoped(log), candidate=successful_local(log),
                            cp_av=len(re.findall(r"\+ cp -av\b", log)))
    print(json.dumps(dict(results=results, elapsed_ns=perf_counter_ns()-started), indent=2))


if __name__ == "__main__":
    main()
