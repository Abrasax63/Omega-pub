"""One real model choice on E1, whose public screen leaves two external patches.

Model sees public candidates ONLY. Reserved evaluation runs separately in
no-network Docker, after a hash commitment of all choices.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import time

from external_real import CASES, digest, load_source, source_file, find_patches, execute_semantic

EXPECTED_MODEL_SHA="724fb256bec1ff062b2f65e4569e871ad2e95ab2a3989723d1769c54294730b7"
MARK="SELECTED_ID: "

def stable_hash(obj):
    return digest(json.dumps(obj,ensure_ascii=False,sort_keys=True))

def load(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))

def git_blob_sha(path):
    b=path.read_bytes()
    return hashlib.sha1(b"blob "+str(len(b)).encode()+b"\0"+b).hexdigest()

def validate_manifest(manifest):
    if manifest.get("phase")!="historical-reproduction-and-public-proposal":
        raise ValueError("unverified historical data")
    cases=manifest.get("cases",[])
    if len(cases)!=3 or {x["case"] for x in cases}!=set(CASES):
        raise ValueError("wrong case inventory")
    for row in cases:
        ident=row["case"]
        if row["status"]!="REPRODUCED_EXTERNAL_HISTORICAL_BUG":
            raise ValueError("original bug was not reproduced")
        if row["buggy_public"]["passed"] or not row["fixed_public"]["passed"]:
            raise ValueError("historical controls failed")
        if not row["fixed_reserved"]["passed"]:
            raise ValueError("historical fixed reserve failed")
        for mode in ("buggy","fixed"):
            got=git_blob_sha(source_file(ident,mode))
            if got!=CASES[ident][mode+"_blob"]:
                raise ValueError("historical source blob changed")
        candidates=find_patches(ident,load_source(ident,"buggy"))
        if [(p["id"],p["sha256"]) for p in candidates]!=[
                (p["id"],p["sha256"]) for p in row["candidates"]]:
            raise ValueError("candidate list drift")
    if {r["case"]:r["shortlist_ids"] for r in cases}!={"E1":["P00","P01"],"E2":["P00"],"E3":["P01"]}:
        raise ValueError("public result changed since preregistration")

def prompt_for_e1(row):
    eligible=[p for p in row["candidates"] if p["id"] in row["shortlist_ids"]]
    options="\n".join(p["id"]+": "+p["new"].strip() for p in eligible)
    return (
       "<|im_start|>system\n"
       "Choose one source-edit ID. Never output code or explanations.\n"
       "<|im_end|>\n<|im_start|>user\n"
       "An existing Python tracing function get_write_function(output) creates "
       "write(s), whose purpose is to write diagnostic text to a supplied file. "
       "A public smoke test with one write call accepts BOTH alternatives below. "
       "They differ only in file-open mode. Which is a safer conventional "
       "behavior for a reusable tracing logger?\n"
       "Pretested edit choices:\n"+options+"\n"
       "Output exactly one of those IDs.\n"
       "<|im_end|>\n<|im_start|>assistant\n"+MARK
    )

def extract_choice(raw,prompt,allowed):
    if prompt in raw:
        text=raw.rsplit(prompt,1)[1]
    elif "... (truncated)\n" in raw:
        text=raw.rsplit("... (truncated)\n",1)[1]
    else:
        raise ValueError("no trustworthy model response boundary")
    text=text.split("\n[ Prompt:",1)[0].split("<|im_end|>",1)[0]
    text=re.sub(r"(?m)^"+chr(96)*3+r"(?:python|text)?[ \t]*$", "",text).strip()
    if text.startswith(MARK):
        text=text[len(MARK):].strip()
    lines=[line.strip() for line in text.splitlines() if line.strip()]
    if len(lines)!=1 or not re.fullmatch(r"P\d\d",lines[0]):
        raise ValueError("model did not emit exactly one candidate ID")
    if lines[0] not in allowed:
        raise ValueError("model chose an unqualified ID")
    return lines[0]

def select(manifest,cli,model):
    validate_manifest(manifest)
    if not Path(cli).is_file() or not Path(model).is_file():
        raise RuntimeError("model/binary not found")
    sha=hashlib.sha256(Path(model).read_bytes()).hexdigest()
    if sha!=EXPECTED_MODEL_SHA:
        raise RuntimeError("Qwen GGUF identity changed")
    row=next(x for x in manifest["cases"] if x["case"]=="E1")
    prompt=prompt_for_e1(row)
    cmd=[str(cli),"-m",str(model),"-p",prompt,
         "-n","96","-c","2048","-t","4","--temp","0"]
    start=time.perf_counter()
    try:
        p=subprocess.run(cmd,text=True,capture_output=True,timeout=240)
    except (OSError,subprocess.TimeoutExpired) as error:
        inference={"called":True,"status":"CALL_FAILED",
                   "reason":type(error).__name__}
    else:
        inference={"called":True,"returncode":p.returncode,
                   "wall_seconds":round(time.perf_counter()-start,3),
                   "prompt_sha256":digest(prompt),
                   "output_sha256":digest(p.stdout),
                   "raw_tail":p.stdout[-2200:]}
        if p.returncode:
            inference.update(status="CALL_FAILED",reason=p.stderr[-250:])
        else:
            try:
                inference.update(status="VALID_ID",
                                 selected_id=extract_choice(p.stdout,prompt,set(row["shortlist_ids"])))
            except ValueError as error:
                inference.update(status="INVALID_ID",reason=str(error))
    choices={
        row["case"]:{
            "deterministic":row["deterministic_choice"],
            "qwen":inference.get("selected_id") if row["case"]=="E1" else None,
        } for row in manifest["cases"]
    }
    return {"experiment":"OMEGA-EXTERNAL-REAL-01",
            "phase":"CHOICES_COMMITTED_BEFORE_HOLDOUT",
            "source_manifest_sha256":stable_hash(manifest),
            "choices_sha256":stable_hash(choices),
            "choices":choices,
            "model_calls":1,"inference":inference,
            "qwen_eligible_tasks":1,"reserved_opened":False,
            "scientific_gain_demonstrated":False}

def evaluate(manifest,committed):
    validate_manifest(manifest)
    choices=committed["choices"]
    if committed["phase"]!="CHOICES_COMMITTED_BEFORE_HOLDOUT" or committed["reserved_opened"]:
        raise ValueError("not a pre-heldout choice freeze")
    if committed["source_manifest_sha256"]!=stable_hash(manifest) or committed["choices_sha256"]!=stable_hash(choices):
        raise ValueError("manifest tampering")
    out=[]
    for row in manifest["cases"]:
        ident=row["case"]
        all_patches={p["id"]:p for p in find_patches(ident,load_source(ident,"buggy"))}
        allowed=set(row["shortlist_ids"])
        audited={cid:execute_semantic(ident,all_patches[cid]["source"],"reserved")
                 for cid in sorted(allowed)}
        arms={}
        for arm in ("deterministic","qwen"):
            selected=choices[ident][arm]
            if selected is None:
                arms[arm]={"status":"NO_MODEL_CHOICE","correct":None,"id":None}
                continue
            if selected not in allowed:
                raise ValueError("unverified model ID")
            arms[arm]={"status":"RESERVED_EVALUATED","id":selected,
                       "correct":audited[selected]["passed"],
                       "source_sha256":all_patches[selected]["sha256"],
                       "same_source_not_independent_replication":(
                           selected==choices[ident].get("qwen") and arm=="deterministic")}
        out.append({"case":ident,"repo":CASES[ident]["repo"],"bug":CASES[ident]["bug"],
                    "public_survivors":sorted(allowed),
                    "all_survivor_reserve":audited,"arms":arms,
                    "upstream_fixed_reserved_correct":row["fixed_reserved"]["passed"]})
    return {"experiment":"OMEGA-EXTERNAL-REAL-01",
            "phase":"RESERVED_CHECKED_AFTER_CHOICE_FREEZE",
            "model_calls":committed["model_calls"],
            "model_selection_status":committed["inference"]["status"],
            "source_manifest_sha256":committed["source_manifest_sha256"],
            "choices_commitment_sha256":committed["choices_sha256"],
            "cases":out,
            "deterministic_successes":sum(c["arms"]["deterministic"]["correct"] is True for c in out),
            "qwen_successes_on_eligible_case":sum(c["arms"]["qwen"]["correct"] is True for c in out),
            "model_eligible_cases":1,
            "upstream_full_suite_run":False,
            "external_real_bugs":True,
            "independent_blind_evaluation":False,
            "model_intelligence_gain_demonstrated":False,
            "promoted":False,"main_modified":False,
            "limitations":[
                "These historical fixed diffs were inspected by the experimenter before the cohort was selected.",
                "We extracted original function ASTs with minimal standard-library dependency stubs.",
                "Cookiecutter locale cp1252 was simulated; no actual Windows runner test.",
                "Exactly one task has multiple candidates; Qwen cannot improve singleton choices.",
                "Held-out examples were predetermined by the same developers, not a sealed third-party oracle."
            ]}

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--mode",choices=("select","evaluate"),required=True)
    p.add_argument("--manifest",type=Path,required=True)
    p.add_argument("--choices",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    p.add_argument("--llama-cli",type=Path)
    p.add_argument("--model-file",type=Path)
    args=p.parse_args()
    manifest=load(args.manifest)
    if args.mode=="select":
        if not args.llama_cli or not args.model_file:
            raise ValueError("real inference requires both executable and GGUF")
        result=select(manifest,args.llama_cli,args.model_file)
    else:
        result=evaluate(manifest,load(args.choices))
    args.output.write_text(json.dumps(result,ensure_ascii=False,sort_keys=True,indent=2)+"\n",
                           encoding="utf-8")
    print(json.dumps({
        "phase":result["phase"],
        "model_status":result.get("inference",{}).get("status",result.get("model_selection_status")),
        "model_choice":result.get("inference",{}).get("selected_id"),
        "deterministic_correct":result.get("deterministic_successes"),
        "qwen_correct":result.get("qwen_successes_on_eligible_case"),
        "choice_sha256":result.get("choices_sha256",result.get("choices_commitment_sha256")),
    },ensure_ascii=False,indent=2))

if __name__=="__main__":
    main()
