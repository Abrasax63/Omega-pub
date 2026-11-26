import json
import re
from hashlib import sha256
from pathlib import Path
from time import perf_counter_ns
from zipfile import ZipFile

SOURCE = "bb1eb9fb69408ac52395fb21f49c6b52d564529a"
COPY = "COPY --from=base /hello.txt /"
JOBS = {"amd64": 138324867120, "arm64": 138324866877}


def inventory(payload):
    return len(payload) == 53


def admit(log, arch, statement, payload, source):
    step = re.search(r"#(\d+) \[stage-1 1/1\] " + re.escape(COPY), log)
    if not step or not re.search(r"#" + step[1] + r" DONE\b", log[step.end():]):
        return False
    definition = statement["predicate"]["buildDefinition"]
    config = definition["externalParameters"]["configSource"]
    dependencies = definition["resolvedDependencies"]
    return (
        COPY in source.splitlines()
        and f"checksum={SOURCE}" in log
        and config["path"] == "hello.Dockerfile"
        and config["digest"]["sha1"] == SOURCE
        and any(item["uri"].endswith("platform=linux%2F" + arch)
                for item in dependencies)
        and {"name": "hello.txt", "digest": {"sha256": sha256(payload).hexdigest()}}
        in statement["subject"]
    )


def main():
    start = perf_counter_ns()
    source = Path("hello.Dockerfile").read_text()
    with ZipFile("bake-output.zip") as archive:
        data = {
            arch: (archive.read(f"linux_{arch}/hello.txt"),
                   json.loads(archive.read(f"linux_{arch}/provenance.json")))
            for arch in JOBS
        }
    results = {}
    for arch, job in JOBS.items():
        other, = JOBS.keys() - {arch}
        payload, statement = data[arch]
        log = Path(f"{job}.log").read_text()
        results[arch] = {
            "verdicts": [inventory(payload), admit(log, arch, statement, payload, source)],
            "swapped": [inventory(payload), admit(log, arch, data[other][1], payload, source)],
            "subject": sha256(payload).hexdigest(),
            "cp_xtrace": len(re.findall(r"\+ cp -av\b", log)),
        }
    assert all(x["verdicts"] == [True, True] and x["swapped"] == [True, False]
               for x in results.values())
    print(json.dumps(dict(results=results, elapsed_ns=perf_counter_ns()-start), indent=2))


if __name__ == "__main__":
    main()
