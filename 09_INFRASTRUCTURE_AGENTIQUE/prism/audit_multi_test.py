from io import TextIOWrapper
from pathlib import Path
import json
from time import perf_counter_ns
from zipfile import ZipFile

from audit_failed_export import local_scoped, successful_local


def test_verdict(events, worker):
    name = "TestIntegration/TestMultipleExporters/worker=" + worker
    terminal = [r["Action"] for r in events if r.get("Test") == name
                and r.get("Package") == "github.com/moby/buildkit/client"
                and r["Action"] in ("pass", "fail", "skip")]
    return terminal == ["pass"]


def main():
    tick = perf_counter_ns()
    frame = dict(Test="TestIntegration/TestMultipleExporters/worker=oci",
                 Package="github.com/moby/buildkit/client")
    assert not test_verdict([dict(frame, Action="skip")], "oci")
    assert not test_verdict([dict(frame, Action="pass"), dict(frame, Action="fail")], "oci")
    result = {}
    for worker, ident in (("oci",138609906418),("containerd",138609906366)):
        with ZipFile(worker+".zip") as artifact:
            name, = [n for n in artifact.namelist() if n.startswith("go-test-") and n.endswith(".json")]
            with TextIOWrapper(artifact.open(name), encoding="utf-8") as stream:
                verified = test_verdict(map(json.loads, stream), worker)
        journal = Path(str(ident)+".log").read_text()
        result[worker] = dict(verified_test=verified, baseline=local_scoped(journal),
                              candidate=successful_local(journal),
                              expected_test_occurrences=journal.count("TestMultipleExporters/worker="+worker),
                              cp_av=journal.count("cp -av"))
    print(json.dumps(dict(result=result, elapsed_ns=perf_counter_ns()-tick), indent=2))


if __name__ == "__main__":
    main()
