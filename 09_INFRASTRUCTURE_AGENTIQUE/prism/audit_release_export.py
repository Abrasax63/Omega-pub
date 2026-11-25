"""Bind BuildKit vertices to one invocation in console logs."""
from hashlib import sha256
import json
from pathlib import Path
import re
from time import perf_counter_ns

from audit_multi_export import LOCAL, PROGRESS, classify

BOUNDARY = re.compile(r"^(?:\d{4}-\d\d-\d\dT\S+Z )?(?:##\[group\]Run |\[command\]\S*docker buildx bake(?: |$))")
FILES = {
    114737904164: "linux-amd64-ld-linux-amd64.tar.gz",
    114737904101: "linux-arm64-ld-linux-arm64.tar.gz",
}


def local_scoped(log):
    pending = set()
    completed = False
    for line in log.splitlines():
        if BOUNDARY.match(line):
            pending.clear()
        match = PROGRESS.fullmatch(line)
        if match:
            vertex, status = match.groups()
            if status == LOCAL:
                pending.add(vertex)
            elif status.startswith("DONE ") and vertex in pending:
                completed = True
                pending.remove(vertex)
    return completed


def main():
    start = perf_counter_ns()
    local = "#1 exporting to client directory\n"
    done = "#1 DONE 0.1s\n"
    command = "[command]/usr/bin/docker buildx bake other\n"
    assert classify(local + command + done)["candidate"] and not local_scoped(local + command + done)
    assert local_scoped(command + local + done)
    assert local_scoped(command + local + done + command + local + done)
    release = Path("114738190638.log").read_text()
    rows = {}
    for job in (*FILES, 114737852386):
        log = Path(f"{job}.log").read_text()
        name = FILES.get(job)
        receipt = bool(name and name in log and f"Uploaded {name}" in release)
        rows[job] = dict(baseline=classify(log)["candidate"], scoped=local_scoped(log),
                         separate_receipt=receipt,
                         cp_av=len(re.findall(r"\+ cp -av\b", log)),
                         sha256=sha256(log.encode()).hexdigest())
    print(json.dumps(dict(rows=rows, elapsed_ns=perf_counter_ns()-start), indent=2))


if __name__ == "__main__":
    main()
