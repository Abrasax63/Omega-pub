from pathlib import Path
import json
import re
from time import perf_counter_ns

PROGRESS = re.compile(r"^(?:\d{4}-\d\d-\d\dT\S+Z )?#(\d+) (?:\[[^]]+\] )?(.*)$")
LOCAL = "exporting to client directory"


def classify(log):
    current = {}
    completed = set()
    for line in log.splitlines():
        match = PROGRESS.fullmatch(line)
        if match:
            vertex, status = match.groups()
            if status.startswith("exporting to "):
                current[vertex] = status
            elif status.startswith("DONE ") and vertex in current:
                completed.add(current.pop(vertex))
    return dict(fixed=bool(completed), candidate=LOCAL in completed, exports=sorted(completed))


def main():
    start = perf_counter_ns()
    assert not classify("#1 exporting to image\n#1 DONE 1.0s")["candidate"]
    assert not classify("#2 exporting to client directory\n#3 DONE 1.0s")["candidate"]
    assert classify("#1 exporting to image\n#1 DONE 1.0s\n#2 exporting to client directory\n#2 DONE 1.0s")["candidate"]
    results = {}
    for job in (138363770471, 138363770689, 138905530526):
        log = Path(f"{job}.log").read_text()
        results[job] = dict(classify(log), cp_av=len(re.findall(r"\+ cp -av\b", log)))
    print(json.dumps(dict(results=results, ns=perf_counter_ns()-start), indent=2))


if __name__ == "__main__":
    main()
