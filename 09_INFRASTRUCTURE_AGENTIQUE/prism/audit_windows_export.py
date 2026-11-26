"""Keep the test verdict separate from the exporter's expected failure."""
import json
from pathlib import Path
from time import perf_counter_ns
from zipfile import ZipFile

NAME = "TestIntegration/slice=2-4/TestExportLocalSourceNotFound/worker=containerd"
PACKAGE = "github.com/moby/buildkit/client"


def admitted(events):
    terminal = [row["Action"] for row in events
                if row.get("Test") == NAME and row.get("Package") == PACKAGE
                and row["Action"] in ("pass", "fail", "skip")]
    return terminal == ["pass"]


def main():
    started = perf_counter_ns()
    frame = dict(Test=NAME, Package=PACKAGE)
    assert not admitted([dict(frame, Action="skip")])
    assert not admitted([dict(frame, Action="pass"), dict(frame, Action="fail")])
    assert not admitted([dict(frame, Action="pass", Package="unrelated")])
    counts = []
    for i in range(1, 5):
        with ZipFile(f"shard{i}.zip") as z:
            report, = [name for name in z.namelist() if name.startswith("go-test-") and name.endswith(".json")]
            counts.append(admitted(map(json.loads, z.read(report).splitlines())))
    assert counts == [False, True, False, False]
    console = Path("client.log").read_text()
    # An expected error is verified by the pinned Go assertion plus the pass.
    # The assertion is not runtime error text and does not make the console admissible.
    print(json.dumps(dict(admitted=counts, naive_report="export_success",
                          source_anchored="expected_export_failure",
                          console_markers=console.count(NAME),
                          source_error_in_console=console.count("src=/nope:"),
                          local_export_in_console=console.count("exporting to client directory"),
                          cp_av=console.count("cp -av"),
                          elapsed_ns=perf_counter_ns()-started), indent=2))


if __name__ == "__main__":
    main()
