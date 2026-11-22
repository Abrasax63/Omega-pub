"""OMEGA-PY-LEARN-02: syntax curriculum -> novel black-box reconstruction -> transfer.

PREREGISTERED one-shot real model pilot on entirely NEW tasks C and D.
The training exercises have visible source; hidden tasks have ORACLES never sent
to the model. Two D arms receive identical observation/dev/feedback budgets.
NO weight training. Never reuse V1 holdout in this pilot.
"""
from __future__ import annotations

import argparse
import ast
import json
from pathlib import Path
import random
import time

import prog_reconstruction_pilot as base

TRIAL = "OMEGA-PY-LEARN-02-2026-11-22"
RANDOM_SEED = 98537
ALPHABET = "abABcC01|:-?\\"
HOLDOUT_N = 40
CAPS = {"probe":120, "code":720, "repair":720, "lesson":220,
        "curriculum":450, "curriculum_repair":480}

# Hidden-program behavior lives ONLY in the trusted runner.
# Its source, metadata, and descriptions are never in model messages.
def _oracle_c(s):
    """Group maximal adjacent alphabetic runs, lowercase each, skip separators."""
    out = []
    current = []
    for ch in s:
        if ch.isalpha():
            current.append(ch.lower())
        else:
            if current:
                out.append("".join(current))
            current = []
    if current:
        out.append("".join(current))
    return out


def _oracle_d(s):
    """Return unique alphabetic characters in encounter order, lowercase."""
    result = []
    for ch in s:
        if ch.isalpha():
            lowered = ch.lower()
            if lowered not in result:
                result.append(lowered)
    return result


ORACLES = {"C": _oracle_c, "D": _oracle_d}
SEEDS = {
    "C": ["", "A", "a1B", "ab|CD", "aB cD", "|-:|", "AA11bb"],
    "D": ["", "a", "abBA", "1aB2a", "CCbbAa", "??", "A|b:A"],
}
DEV = {
    "C": ["aB:C", "1abc0D", "aA|bB", "---Ab", "a1a1a", "ABc\\De", "aB-c0a"],
    "D": ["bBaAc", "aa11BB", "A1a2A", "|C|b|c|", "aBAcC", "abcabc", "12:-"],
}

# Teaching exercises independent of C and D.
# No output of either hidden oracle is used in curriculum.
def broken_backslash():
    return ("def transform(s):\n"
            "    out = []\n"
            "    for ch in s:\n"
            "        if ch == '" + "\\" + "':\n"
            "            out.append(ch)\n"
            "    return out\n")


EXERCISES = [
    {"id":"escaped-string",
     "intent":"Return a list containing every literal backslash character from s.",
     "broken":broken_backslash(),
     "examples":[{"input":"a\\b","output":["\\"]},
                 {"input":"ab","output":[]}]},
    {"id":"for-colon",
     "intent":"Return a list containing each character of s in order.",
     "broken":"def transform(s):\n    out=[]\n    for char in s\n        out.append(char)\n    return out\n",
     "examples":[{"input":"abc","output":["a","b","c"]},
                 {"input":"","output":[]}]},
    {"id":"stray-brace",
     "intent":"Return the lowercase spelling of s in a one-element list.",
     "broken":"def transform(s):\n    out=[]\n    out.append(s.lower())\n    return out}\n",
     "examples":[{"input":"Ab","output":["ab"]},
                 {"input":"","output":[""]}]},
]


def oracle(task, s):
    return ORACLES[task](s)


def observations(task, texts):
    return [{"input":s,"output":oracle(task,s)} for s in texts]


def blind_inputs(task):
    rng=random.Random(RANDOM_SEED+(7 if task=="C" else 17))
    values=[]
    for _ in range(1000):
        length=rng.randint(0,base.MAX_INPUT)
        s="".join(rng.choice(ALPHABET) for _ in range(length))
        if (s not in values and s not in SEEDS[task] and s not in DEV[task]):
            values.append(s)
        if len(values)==HOLDOUT_N:
            break
    if len(values)!=HOLDOUT_N:
        raise ValueError("BLIND_INPUT_GENERATION_FAILED")
    return values


def diagnostic(code):
    """Exact compiler message, source line and position; no teacher oracle."""
    if not isinstance(code,str):
        return {"stage":"format","error":"NO_PARSEABLE_JSON_CODE"}
    try:
        ast.parse(code)
    except SyntaxError as ex:
        return {"stage":"syntax","error_type":type(ex).__name__,
                "message":str(ex.msg)[:200],"line":ex.lineno,
                "offset":ex.offset,
                "source_line":(ex.text or "").strip()[:160]}
    try:
        base.validate_program(code)
    except ValueError as e:
        return {"stage":"policy","error":str(e)}
    return {"stage":"valid","message":"Python parsed and restricted API accepted"}


def score(task, code, inputs, detail=False):
    results=base.execute_student(code,inputs) if code is not None else [
        {"error":"NO_CODE"} for _ in inputs]
    rows=[]
    for text,pred in zip(inputs,results):
        truth=oracle(task,text)
        record={"input":text,"correct":pred.get("value")==truth}
        if detail:
            record.update({"expected":truth,"actual":pred})
        rows.append(record)
    return {"n":len(rows),"correct":sum(r["correct"] for r in rows),
            "rows":rows}


def curriculum(client):
    """Two repair attempts per concept with compiler feedback from real Python."""
    experiences=[]
    for item in EXERCISES:
        intro=(
            "Python syntax workshop, not a hidden-program task. "
            "Given faulty source below, repair the function and ensure the "
            "stated expected behavior. Return JSON with key 'code' holding "
            "the COMPLETE Python source for def transform(s). "
            "Do not use imports or external tools; source must be safe. "
            "Explain briefly what syntax feature you corrected.\n"+
            "LEARNING OBJECTIVE: "+item["intent"]+
            "\nBROKEN PYTHON:\n"+item["broken"]+
            "\nPYTHON COMPILER FEEDBACK:\n"+json.dumps(diagnostic(item["broken"]))+
            "\nBEHAVIOR EXAMPLES:\n"+json.dumps(item["examples"]))
        raw1=client([
            {"role":"system","content":base.SYSTEM},
            {"role":"user","content":intro}],CAPS["curriculum"],
            "syntax:"+item["id"]+":first")
        code1=base.parse_code(raw1)
        diag1=diagnostic(code1)
        cases=[v["input"] for v in item["examples"]]
        got1=base.execute_student(code1,cases) if code1 else [
            {"error":"NO_VALID_CODE"} for _ in cases]
        check1=[{"input":v["input"],"expected":v["output"],
                 "actual":g} for v,g in zip(item["examples"],got1)]
        reply=(
            "Reflect on Python's compiler feedback from YOUR attempt and "
            "the public practice examples. Correct the syntax/behavior, then "
            "return JSON with key code. This is your final workshop attempt.\n"+
            "OBJECTIVE: "+item["intent"]+"\nYOUR CODE:\n"+
            json.dumps(code1)+"\nCOMPILER:\n"+json.dumps(diag1)+
            "\nPUBLIC PRACTICE FEEDBACK:\n"+json.dumps(check1))
        raw2=client([
            {"role":"system","content":base.SYSTEM},
            {"role":"user","content":reply}],CAPS["curriculum_repair"],
            "syntax:"+item["id"]+":repair")
        code2=base.parse_code(raw2)
        diag2=diagnostic(code2)
        got2=base.execute_student(code2,cases) if code2 else [
            {"error":"NO_VALID_CODE"} for _ in cases]
        passed=sum(g.get("value")==v["output"] for v,g in zip(item["examples"],got2))
        experiences.append({"exercise":item["id"],"goal":item["intent"],
            "broken_source":item["broken"],
            "first_raw":raw1,"first_code":code1,"first_diagnostic":diag1,
            "final_raw":raw2,"final_code":code2,"final_diagnostic":diag2,
            "public_practice_correct":passed,"public_practice_total":len(cases)})
    return experiences


def episode(client,task,tag,lesson=""):
    """Equal 3-call budget per D arm, with complete Python feedback to both."""
    lesson_block=("GENERAL PYTHON LESSONS FROM PRIOR PRACTICE "
                  "(not this hidden program's solution):\n"+lesson+"\n"
                  if lesson else "")
    initial=observations(task,SEEDS[task])
    prompt1=(
        "Investigate an UNKNOWN program taking string s and returning list[str]. "
        "The program's source is unavailable. Ask for up to three extra "
        "input/output probes, chosen by you (ASCII length <= 24). "
        "Return JSON {\"queries\":[...]}; no code yet.\n"+lesson_block+
        "KNOWN OBSERVATIONS:\n"+json.dumps(initial))
    raw_probe=client([{"role":"system","content":base.SYSTEM},
                      {"role":"user","content":prompt1}],
                     CAPS["probe"],tag+":probes")
    probes=base.parse_probes(raw_probe)
    obs_all=initial+observations(task,probes)
    prompt2=(
        "Infer the UNKNOWN program only from the input/output examples. "
        "Write safe Python code defining def transform(s) returning list[str]. "
        "Return exactly JSON {\"code\":\"...\"} with properly escaped newlines "
        "and quotes. No imports, file access, introspection or network.\n"+
        lesson_block+"OBSERVATIONS:\n"+json.dumps(obs_all))
    raw_code=client([{"role":"system","content":base.SYSTEM},
                     {"role":"user","content":prompt2}],
                    CAPS["code"],tag+":code")
    code1=base.parse_code(raw_code)
    compiler1=diagnostic(code1)
    development1=score(task,code1,DEV[task],detail=True)
    failures=[r for r in development1["rows"] if not r["correct"]][:4]
    prompt3=(
        "You are learning to debug your own Python. Fix the entire function. "
        "Review the REAL COMPILER result first; if parsing failed, resolve "
        "the exact SyntaxError before improving behavior. Then consider "
        "the public development cases. Return JSON with key 'code' with "
        "the COMPLETE corrected Python source. No unsafe operations.\n"+
        lesson_block+"EARLIER OBSERVATIONS:\n"+json.dumps(obs_all)+
        "\nYOUR CODE:\n"+json.dumps(code1)+
        "\nREAL PYTHON COMPILER:\n"+json.dumps(compiler1)+
        "\nPUBLIC DEVELOPMENT FAILURES:\n"+json.dumps(failures)+
        "\nPublic development successes: "+
        str(development1["correct"])+"/"+str(development1["n"]))
    raw_fix=client([{"role":"system","content":base.SYSTEM},
                    {"role":"user","content":prompt3}],
                   CAPS["repair"],tag+":repair")
    code2=base.parse_code(raw_fix)
    compiler2=diagnostic(code2)
    dev2=score(task,code2,DEV[task],detail=False)
    hidden=blind_inputs(task)
    blind1=score(task,code1,hidden,detail=True)
    blind2=score(task,code2,hidden,detail=True)
    return {
        "task":task,"arm":tag,"autonomous_probes":probes,
        "seen_observations":obs_all,
        "raw_model_messages":{"probes":raw_probe,"first":raw_code,"repaired":raw_fix},
        "first_code":code1,"final_code":code2,
        "first_compiler":compiler1,"final_compiler":compiler2,
        "first_dev_correct":development1["correct"],
        "final_dev_correct":dev2["correct"],
        "blind_first":{"n":blind1["n"],"correct":blind1["correct"]},
        "blind_final":blind2,
        "blind_score_given_to_model":False,
        "teacher_oracle_given_to_model":False,
    }


def summarize_lesson(client,curriculum_experience,learn_episode):
    # Only stage summaries are fed to the LLM, not oracle source or hidden cases.
    excerpt={
        "syntax_practice":[{"exercise":r["exercise"],
            "first_compiler":r["first_diagnostic"],
            "final_compiler":r["final_diagnostic"],
            "practice_correct":r["public_practice_correct"]}
            for r in curriculum_experience],
        "prior_hidden_program_training":{
            "observations":learn_episode["seen_observations"],
            "first_compiler":learn_episode["first_compiler"],
            "final_compiler":learn_episode["final_compiler"],
            "dev_score":learn_episode["final_dev_correct"],
            "initial_program":learn_episode["first_code"],
            "repaired_program":learn_episode["final_code"],
        }}
    prompt=(
        "Summarize reusable Python coding principles YOU learned from this "
        "practice. Do not speculate about or write a solution for a new "
        "unseen program. Maximum 600 characters. Return JSON {\"lesson\":\"...\"}.\n"+
        json.dumps(excerpt))
    raw=client([{"role":"system","content":base.SYSTEM},
                {"role":"user","content":prompt}],CAPS["lesson"],
               "learn:lesson")
    parsed=base.parse_json(raw)
    val=parsed.get("lesson") if parsed else None
    return {"raw":raw,"lesson":val[:600] if isinstance(val,str) else "",
            "contains_unverified_information":True}


def execute(endpoint, directory):
    directory=Path(directory)
    directory.mkdir(parents=True,exist_ok=True)
    client=base.Client(endpoint)
    report={"protocol":TRIAL,"status":"STARTED",
            "model":base.MODEL,
            "model_weights_updated":False,
            "real_finetuning_performed":False,
            "main_modified":False,"private_repo_created":False,
            "holdout_was_shown_to_model":False,
            "teacher_oracles_given_to_model":False}
    def checkpoint():
        report["calls"]=client.call_log
        (directory/"report.json").write_text(
            json.dumps(report,ensure_ascii=False,indent=2)+"\n",
            encoding="utf-8")
    checkpoint()
    try:
        report["D_baseline"]=episode(client,"D","D_baseline")
        checkpoint()
        report["syntax_training"]=curriculum(client)
        checkpoint()
        report["C_training"]=episode(client,"C","C_training")
        checkpoint()
        report["learned_lesson"]=summarize_lesson(
            client,report["syntax_training"],report["C_training"])
        checkpoint()
        report["D_transfer"]=episode(
            client,"D","D_transfer",report["learned_lesson"]["lesson"])
        checkpoint()
        a=report["D_baseline"]["blind_final"]
        b=report["D_transfer"]["blind_final"]
        report["comparison"]={
            "baseline_D_correct":a["correct"],
            "post_training_D_correct":b["correct"],
            "n":HOLDOUT_N,
            "delta":b["correct"]-a["correct"],
            "same_D_hidden_inputs":True,
            "same_D_seed_dev_examples":True,
            "same_D_stage_call_caps":True,
            "same_compiler_feedback_both_D_arms":True,
            "extra_training_calls_in_trained_arm":10,
            "total_equal_budget":False,
            "proven_causal_learning":False,
            "weight_training":False,
            "note":"Single-seed in-context transfer with more training calls and extra context; not a fair causal estimate.",
        }
        report["status"]="EVALUATED_NO_LEARNING_CLAIM"
    finally:
        checkpoint()
    return report


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--server",default="http://127.0.0.1:8080")
    p.add_argument("--output",type=Path,required=True)
    args=p.parse_args()
    r=execute(args.server,args.output)
    print(json.dumps({
        "status":r["status"],"protocol":r["protocol"],
        "baseline_D":r["comparison"]["baseline_D_correct"],
        "post_training_D":r["comparison"]["post_training_D_correct"],
        "C_training":r["C_training"]["blind_final"]["correct"],
        "n_hidden":HOLDOUT_N,
        "syntax_practice_valid":sum(
            v["final_diagnostic"]["stage"]=="valid" for v in r["syntax_training"]),
        "real_model_calls":len(r["calls"]),
        "weight_training":False,
    }))


if __name__=="__main__":
    main()
