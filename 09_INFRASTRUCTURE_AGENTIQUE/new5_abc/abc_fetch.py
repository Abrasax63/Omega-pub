"""Fetch strictly pinned upstream BUGGY snapshots and public test blobs.

Fixed PRODUCTION source may only be retrieved with --phase fixed-oracle.
During --phase buggy-only this script contacts the fixed commit ONLY through
one named raw regression-test file URL, not via git or source/diff API.
"""
import argparse
from hashlib import sha256
import json
from pathlib import Path
import re
import subprocess
from urllib.request import urlopen

ALLOW_REPOS = {"tqdm/tqdm", "cookiecutter/cookiecutter", "jakubroztocil/httpie"}
ALLOW_TEST_PREFIXES = ("tests/", "tqdm/tests/")


def fetch(cohort_file, checkouts_dir, tests_dir, phase):
    cohort=json.loads(cohort_file.read_text(encoding="utf8"))
    if cohort.get("experiment")!="OMEGA-NEW5-ABC-02" or len(cohort["cases"])!=5:
        raise ValueError("wrong experiment/case count")
    if phase not in ("buggy-only","fixed-oracle"):
        raise ValueError("invalid phase")
    checkouts_dir.mkdir(parents=True, exist_ok=True)
    tests_dir.mkdir(parents=True, exist_ok=True)
    evidence=[]
    for case in cohort["cases"]:
        ident=case["id"]
        repo=case["repository"]
        if repo not in ALLOW_REPOS or not re.fullmatch(r"N[1-5]",ident):
            raise ValueError("unregistered upstream repo or ID")
        test_file=case["test_file"]
        if not test_file.startswith(ALLOW_TEST_PREFIXES) or ".." in Path(test_file).parts:
            raise ValueError("unapproved regression test path")
        sha=case["buggy_sha"] if phase=="buggy-only" else case["fixed_sha"]
        if not re.fullmatch(r"[a-f0-9]{40}",sha):
            raise ValueError("bad Git SHA")
        root=checkouts_dir/ident
        subprocess.run(["git","init","-q",str(root)],check=True)
        subprocess.run(["git","-C",str(root),"remote","add","origin",
                        "https://github.com/"+repo+".git"],check=True)
        subprocess.run(["git","-C",str(root),"fetch","--depth=1","origin",sha],
                       check=True,stdout=subprocess.DEVNULL)
        subprocess.run(["git","-C",str(root),"checkout","-q","--detach","FETCH_HEAD"],
                       check=True)
        actual=subprocess.check_output(["git","-C",str(root),"rev-parse","HEAD"],
                                       text=True).strip()
        if actual!=sha:
            raise RuntimeError("wrong fetched commit")
        # A public regression TEST file is explicitly permitted as an input to
        # trace-guided repair. No fixed production file/diff is downloaded here.
        raw_url=("https://raw.githubusercontent.com/"+repo+"/"+case["fixed_sha"]
                 +"/"+test_file)
        with urlopen(raw_url,timeout=45) as conn:
            test_bytes=conn.read(1_000_001)
        if len(test_bytes)>1_000_000 or not test_bytes:
            raise ValueError("oversized/empty test file")
        (tests_dir/(ident+".py")).write_bytes(test_bytes)
        evidence.append({
            "id":ident,"project":case["project"],
            "source_commit":actual,"test_file":test_file,
            "regression_test_only_sha256":sha256(test_bytes).hexdigest(),
            "retrieved_full_fixed_production_repo":phase=="fixed-oracle",
        })
        print(ident,phase,"commit verified",actual,
              "test-only-sha256",sha256(test_bytes).hexdigest(),flush=True)
    return evidence


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--cohort",type=Path,required=True)
    parser.add_argument("--checkouts",type=Path,required=True)
    parser.add_argument("--tests",type=Path,required=True)
    parser.add_argument("--phase",choices=("buggy-only","fixed-oracle"),required=True)
    parser.add_argument("--manifest-output",type=Path,required=True)
    args=parser.parse_args()
    evidence=fetch(args.cohort,args.checkouts,args.tests,args.phase)
    args.manifest_output.parent.mkdir(parents=True,exist_ok=True)
    args.manifest_output.write_text(
        json.dumps(evidence,indent=2,sort_keys=True)+"\n",encoding="utf8")


if __name__=="__main__":
    main()
