"""youtube-dl-1: frozen lexical rank vs observable Python traceback rank.

No target-code import or historical fixed source access. The lexical weights,
AST inventory, and tokenization are reused from OMEGA-MECHANISM-LOC-01 (#119);
only the preregistered source package and public test path are changed.
"""
from __future__ import annotations

import argparse
import ast
import hashlib
import json
from pathlib import Path
import re
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "mechanism_loc_01"))
import localize as previous

previous.ROOT_PACKAGE = "youtube_dl"
previous.TEST_PATH = "test/test_utils.py"

BUGGY_COMMIT = "99036a1298089068dcf80c0985bfcc3f8c24f281"
FIXED_COMMIT = "1cc47c667419e0eadc0a6989256ab7b276852adf"
TEST_PATH = "test/test_utils.py"
PKG = "youtube_dl"
FRAME_RE = re.compile(r'File "([^"]+)", line (\d+), in ([^\s]+)')
TESTS_RE = re.compile(r"Ran (\d+) tests? in ",re.I)


def parse_frames(log: str) -> list[dict]:
    frames = []
    for match in FRAME_RE.finditer(log):
        raw_path, number, function = match.groups()
        normalized = raw_path.replace("\\", "/")
        needle = "/" + PKG + "/"
        if needle not in normalized:
            continue
        rel = PKG + "/" + normalized.split(needle, 1)[1]
        if ".." in Path(rel).parts or not rel.endswith(".py"):
            continue
        frames.append({"file": rel, "line": int(number), "function": function})
    return frames


def map_frame(frame: dict, targets: list[dict]) -> str | None:
    matches = [t for t in targets if t["file"] == frame["file"]
               and t["line"] <= frame["line"] <= t["end_line"]]
    if not matches:
        return None
    # If nested intervals overlap, choose the narrowest AST interval.
    matches.sort(key=lambda t: (t["end_line"] - t["line"],t["line"],t["key"]))
    return matches[0]["key"]


def build_manifest(buggy_checkout: Path, run_log: str, exit_code: int) -> dict:
    test = buggy_checkout / TEST_PATH
    if not test.is_file() or test.is_symlink():
        return {"status":"NO_TEST_SOURCE","phase":"BUGGY_ONLY"}
    try:
        test_data = test.read_bytes()
        signals = previous.test_signals(test_data.decode("utf-8"))
    except (SyntaxError,UnicodeError,OSError):
        return {"status":"SOURCE_PARSE_ERROR","phase":"BUGGY_ONLY"}
    inventory, hashes, errors = previous.collect_targets(buggy_checkout)
    if errors:
        return {"status":"SOURCE_PARSE_ERROR","phase":"BUGGY_ONLY",
                "errors":errors,"source_hashes":hashes}
    if not inventory:
        return {"status":"NO_FUNCTIONS","phase":"BUGGY_ONLY"}
    frames = parse_frames(run_log)
    mapped = [map_frame(f,inventory) for f in frames]
    first_seen = []
    for name in mapped:
        if name is not None and name not in first_seen:
            first_seen.append(name)
    n=len(first_seen)
    boosts = {key:1000+10*(n-index) for index,key in enumerate(first_seen)}
    base=[]
    for item in inventory:
        s,factors = previous.score(item,signals)
        base.append(dict(item,score_a=s,score_b=s+boosts.get(item["key"],0),
                         factors=factors,trace_boost=boosts.get(item["key"],0)))
    a=sorted(base,key=lambda t:(-t["score_a"],t["file"],t["line"],t["qualname"]))
    b=sorted(base,key=lambda t:(-t["score_b"],t["file"],t["line"],t["qualname"]))
    aranks={t["key"]:i+1 for i,t in enumerate(a)}
    branks={t["key"]:i+1 for i,t in enumerate(b)}
    testcounts=[int(x) for x in TESTS_RE.findall(run_log)]
    has_target_frames=bool(first_seen)
    valid_buggy_attempt=(exit_code not in (0,124,125,126,127,137) and
                         bool(testcounts) and testcounts[-1] > 0 and
                         has_target_frames)
    if valid_buggy_attempt:
        status="BUGGY_TRACE_OBSERVED_NOT_YET_ORACLE_VERIFIED"
    elif exit_code==0:
        status="BUGGY_TEST_SUITE_PASSED"
    else:
        status="REPRODUCER_UNCONFIRMED"
    return {
       "status":status,
       "experiment":"OMEGA-TRACEBACK-LOC-01",
       "phase":"BUGGY_ONLY_RANKING_FROZEN_BEFORE_FIXED",
       "project":"ytdl-org/youtube-dl",
       "bugsinpy_case":"youtube-dl-1",
       "buggy_commit":BUGGY_COMMIT,
       "fixed_commit_metadata_only":FIXED_COMMIT,
       "public_test_file":TEST_PATH,
       "test_sha256":previous.sha(test_data),
       "source_hashes":hashes,
       "source_parse_errors":errors,
       "total_targets":len(base),
       "test_signals":signals,
       "budget_at_10":10,
       "secondary_budgets":[5,20],
       "test_exit_code":exit_code,
       "test_suite_reported_tests":testcounts,
       "test_log_sha256":previous.sha(run_log.encode("utf-8")),
       "raw_package_frames":frames,
       "unmapped_package_frames":[f for f,k in zip(frames,mapped) if k is None],
       "ordered_unique_mapped_frame_keys":first_seen,
       "target_frames_usable":has_target_frames,
       "test_runtime_verified_historical_bug":False,
       "target_inventory":[dict(item,rank_a=aranks[item["key"]],
                                rank_b=branks[item["key"]])
                           for item in sorted(base,key=lambda t:t["key"])],
       "top_a":[x["key"] for x in a[:20]],
       "top_b":[x["key"] for x in b[:20]],
       "fixed_source_accessed":False,
       "model_called":False,
       "patch_generated":False,
       "actual_repair_correctness":None,
       "same_ranking_slots":True,
       "same_information_budget":False,
       "extra_runtime_cost_of_B":"historical buggy test execution",
       "main_modified":False,
    }


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--buggy-checkout",type=Path,required=True)
    p.add_argument("--test-log",type=Path,required=True)
    p.add_argument("--exit-code",type=int,required=True)
    p.add_argument("--output",type=Path,required=True)
    args=p.parse_args()
    result=build_manifest(args.buggy_checkout,
                          args.test_log.read_text(encoding="utf-8",errors="replace"),
                          args.exit_code)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,sort_keys=True,ensure_ascii=False,
                                      indent=2)+"\n",encoding="utf-8")
    print(json.dumps({
      "status":result["status"],
      "targets":result.get("total_targets"),
      "usable_frames":len(result.get("ordered_unique_mapped_frame_keys",[])),
      "test_exit_code":args.exit_code,
      "top_a":result.get("top_a",[])[:10],
      "top_b":result.get("top_b",[])[:10],
      "sha256":hashlib.sha256(args.output.read_bytes()).hexdigest(),
    },ensure_ascii=False))
    # Data collection never turns a missing reproducer into a success.
    # Allow job to archive evidence and let oracle check whether comparable.


if __name__=="__main__":
    main()
