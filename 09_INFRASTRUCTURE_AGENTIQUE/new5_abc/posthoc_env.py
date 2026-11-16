"""Post-hoc recheck of ONLY the environment-blocked N3/N5 historical tests.

This is NOT a blinded model/patch evaluation. Both fixed revisions were already
opened by the initial historic-oracle run. No LLM, no search, no patch proposed.
"""
import argparse
from hashlib import sha256
import json
from pathlib import Path
import tempfile

from abc_fetch import fetch
from abc_runner import build_project_image, run_regression

SUBSET = ("N3", "N5")
ORIGINAL_RUN = "https://github.com/Abrasax63/Omega-pub/actions/runs/43811742090"


def diagnose(cohort_path, output):
    cohort = json.loads(cohort_path.read_text())
    if cohort.get("experiment") != "OMEGA-NEW5-ABC-01" or len(cohort["cases"]) != 5:
        raise ValueError("source cohort changed")
    data = {
        "experiment": cohort["experiment"],
        "phase": "POSTHOC_INFRA_ONLY_FIXED_ALREADY_EXPOSED",
        "origin": ORIGINAL_RUN,
        "cases": [], "new_model_calls": 0, "patch_candidates_tested": 0,
        "holdout_blindness": False, "reproducible_but_not_prospective": True,
    }
    with tempfile.TemporaryDirectory(prefix="omega-new5-env-") as td:
        root = Path(td)
        buggy = root / "buggy"
        fixed = root / "fixed"
        tests = root / "tests"
        fixed_tests = root / "fixed-tests"
        # Fetching all five pinned SHAs preserves the original checkout logic,
        # but ONLY N3/N5 have test execution in this diagnostic.
        manifest_b = fetch(cohort_path, buggy, tests, "buggy-only")
        manifest_f = fetch(cohort_path, fixed, fixed_tests, "fixed-oracle")
        for case in cohort["cases"]:
            if case["id"] not in SUBSET:
                continue
            ident = case["id"]
            t = fixed_tests / (ident + ".py")
            if t.read_bytes() != (tests / (ident + ".py")).read_bytes():
                raise RuntimeError("regression test changed during posthoc check")
            image, build = build_project_image(case, buggy / ident)
            entry = {
                "id": ident, "project": case["project"],
                "buggy_sha": case["buggy_sha"], "fixed_sha": case["fixed_sha"],
                "test_file_sha256": sha256(t.read_bytes()).hexdigest(),
                "build": build,
            }
            if build["exit"] == 0:
                original = run_regression(image, case, buggy / ident, t)
                corrected = run_regression(image, case, fixed / ident, t)
                entry["buggy_test"] = {k: v for k, v in original.items()
                                       if k != "trace_log"}
                entry["fixed_test"] = {k: v for k, v in corrected.items()
                                      if k != "trace_log"}
                if original["status"] == "FAIL" and corrected["status"] == "PASS":
                    entry["status"] = "HISTORICAL_REGRESSION_NOW_REPRODUCED_POSTHOC"
                else:
                    entry["status"] = "ENVIRONMENT_STILL_BLOCKED_OR_NO_CONTRAST"
            else:
                entry["status"] = "DEPENDENCY_BUILD_BLOCKED"
            data["cases"].append(entry)
    if len(data["cases"]) != 2:
        raise RuntimeError("posthoc subset drift")
    data["historical_regressions_recovered_posthoc"] = sum(
        c["status"] == "HISTORICAL_REGRESSION_NOW_REPRODUCED_POSTHOC"
        for c in data["cases"])
    output.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf8")
    print(json.dumps({"phase": data["phase"],
                      "cases": [{k: c[k] for k in ("id","status")} for c in data["cases"]],
                      "recovered": data["historical_regressions_recovered_posthoc"],
                      "new_model_calls": 0}, indent=2))
    return data


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--cohort", required=True, type=Path)
    p.add_argument("--output", required=True, type=Path)
    a = p.parse_args()
    diagnose(a.cohort, a.output)


if __name__ == "__main__":
    main()
