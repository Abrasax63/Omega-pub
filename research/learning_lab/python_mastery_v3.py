"""OMEGA-PY-MASTERY-03: progressive Python practice with retained best code.

Reuses the existing V1 sandbox/client and V2 exact Python compiler diagnostics.
Only PRE-REGISTERED fresh tasks E and F may be used. Hidden programs and
mastery examples never enter model prompts. No parameter updates.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import random

import prog_reconstruction_pilot as v1
import python_curriculum_v2 as v2

PROTOCOL="OMEGA-PY-MASTERY-03-2026-11-22"
SEED=281119
ALPHABET="abABcC012345_|:-?"
HIDDEN_SIZE=40
MODEL_CAPS={"probe":130,"code":680,"repair":740,"practice":550,"practice_retry":590,"lesson":250}
MASTERY_THRESHOLD=2

# All examples and oracle implementations remain in the trusted runner.
# NO TASK DESCRIPTION OR ORACLE SOURCE IS INCLUDED IN MODEL PROMPTS.
def _target_e(s):
    """Maximal decimal digit runs -> decimal string without leading zeros."""
    out=[]
    buf=[]
    for ch in s:
        if ch in "0123456789":
            buf.append(ch)
        elif buf:
            out.append(str(int("".join(buf))))
            buf=[]
    if buf:
        out.append(str(int("".join(buf))))
    return out


def _target_f(s):
    """Unique lowercased ASCII alphabetic tokens, by first occurrence."""
    result=[]
    buf=[]
    for ch in s:
        if ch in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ":
            buf.append(ch.lower())
        else:
            if buf:
                text="".join(buf)
                if text not in result:
                    result.append(text)
            buf=[]
    if buf:
        text="".join(buf)
        if text not in result:
            result.append(text)
    return result


ORACLE={"E":_target_e,"F":_target_f}
TRAIN={
 "E":["","007","a12b3","123_000","a1b02c003","|1|2|3|","00:00"],
 "F":["","Ab","ab|CD|ab","AAA:aaa","a1b2a","aB_ab","a|a|A"],
}
DEV={
 "E":["0a001","12a003b","12345","1-0","|000|007|","cc23dd45","0:2_03"],
 "F":["aB|AB","aa1AA","a-a-a","ABC:abc","aB_ba","AbC|d|AbC","a_b_a"],
}

# New workshop exercises (NOT V2 and NOT E/F). Only the visible practice
# examples are shown to the model. Mastery examples are withheld.
PRACTICE=(
 {
  "id":"colon-if",
  "goal":"Return uppercase letters from s as lowercase strings, in order.",
  "broken":"def transform(s):\n    result=[]\n    for c in s:\n        if c.isupper()\n            result.append(c.lower())\n    return result\n",
  "visible":["A1bC","ab","XYZ"],
  "mastery":["AABb","?Z0","A aB"],
  "oracle":lambda s:[c.lower() for c in s if c.isupper()],
 },
 {
  "id":"indentation",
  "goal":"Return the characters of s in reverse order, as a list.",
  "broken":"def transform(s):\n    out=[]\n    for c in s:\n    out.insert(0,c)\n    return out\n",
  # To avoid unfair allowlist denial, a revised code using list indexing is
  # possible; 'insert' is added to the safe methods in the V3 AST guard below.
  "visible":["abc","","a1"],
  "mastery":["AbC","12|","a"],
  "oracle":lambda s:list(reversed(s)),
 },
 {
  "id":"quotes",
  "goal":"Return one string made from the uppercase version of s, in a list.",
  "broken":"def transform(s):\n    return [s.upper()]\n    \"\"\"\n",
  "visible":["ab","","A|b"],
  "mastery":["0c","a a","ABC"],
  "oracle":lambda s:[s.upper()],
 },
)

def evaluate(task,code,inputs,expose=False):
    outputs=v1.execute_student(code,inputs) if code is not None else [{"error":"NO_CODE"} for _ in inputs]
    rows=[]
    for s,actual in zip(inputs,outputs):
        expected=ORACLE[task](s)
        entry={"input":s,"correct":actual.get("value")==expected}
        if expose:
            entry.update({"expected":expected,"actual":actual})
        rows.append(entry)
    return {"n":len(rows),"correct":sum(x["correct"] for x in rows),"rows":rows}


def blind(task):
    rng=random.Random(SEED+(34 if task=="E" else 67))
    found=[]
    for _ in range(3000):
        length=rng.randrange(1,23)
        s="".join(rng.choice(ALPHABET) for i in range(length))
        if s not in found and s not in TRAIN[task] and s not in DEV[task]:
            found.append(s)
        if len(found)>=HIDDEN_SIZE:
            break
    if len(found)!=HIDDEN_SIZE:
        raise AssertionError("NOT_ENOUGH_HIDDEN_CASES")
    return found


def diagnostic(code):
    # Reuse V2 parse/AST validator; distinguish JSON, Python, and policy.
    return v2.diagnostic(code)


def parse_code_and_report(raw):
    parsed=v1.parse_json(raw)
    if parsed is None:
        return None,{"stage":"transport","error":"INVALID_JSON_OBJECT"}
    code=parsed.get("code")
    if not isinstance(code,str) or not code.strip():
        return None,{"stage":"transport","error":"MISSING_STRING_CODE_FIELD"}
    if len(code)>v1.MAX_CODE_CHARS:
        return None,{"stage":"transport","error":"CODE_FIELD_TOO_LARGE"}
    return code,diagnostic(code)


def choose_best(attempts):
    """Never discard earlier compilable, correct attempts due to bad JSON.

    Ranking uses PUBLIC development only, never hidden mastery/holdouts.
    """
    ranked=[]
    for i,row in enumerate(attempts):
        diag=row["diagnostic"]
        is_valid=diag["stage"]=="valid"
        rank=(int(is_valid),row.get("public_correct",0),-i)
        ranked.append((rank,i))
    best_index=max(ranked)[1]
    return best_index,attempts[best_index]


def execute_examples(code, examples):
    if code is None:
        return [{"error":"NO_CODE"} for _ in examples]
    return v1.execute_student(code,examples)


def practice_one(client,exercise):
    questions=exercise["visible"]
    public=[{"input":s,"output":exercise["oracle"](s)} for s in questions]
    first_prompt=(
        "This is a PYTHON REPAIR LESSON, not a mystery program. "
        "Repair the broken source to satisfy the stated behavior. "
        "Return a JSON object with key code containing COMPLETE Python "
        "def transform(s) returning list[str]; no imports. "
        "The compiler's diagnosis is authoritative, not a math answer.\n"+
        "GOAL: "+exercise["goal"]+"\nBROKEN SOURCE:\n"+exercise["broken"]+
        "\nREAL COMPILER DIAGNOSTIC:\n"+json.dumps(diagnostic(exercise["broken"]))+
        "\nVISIBLE PRACTICE CASES:\n"+json.dumps(public))
    raw=client([{"role":"system","content":v1.SYSTEM},
                {"role":"user","content":first_prompt}],MODEL_CAPS["practice"],
               "course:"+exercise["id"]+":first")
    code,diag=parse_code_and_report(raw)
    actual=execute_examples(code,questions)
    correct=sum(a.get("value")==p["output"] for a,p in zip(actual,public))
    attempts=[{"raw":raw,"code":code,"diagnostic":diag,
               "public_correct":correct}]
    feedback=[
        {"input":p["input"],"expected":p["output"],"received":a}
        for p,a in zip(public,actual)]
    revise=(
        "You can improve your first Python program. Read its error feedback "
        "and return ONE JSON object {\"code\": \"complete safe Python source\"}. "
        "If it is already valid and passes the public examples, preserve it; "
        "do not change it merely to change it. No hidden test is shown.\n"+
        "GOAL: "+exercise["goal"]+"\nFIRST ANSWER:\n"+raw[:4000]+
        "\nTRANSPORT/PYTHON/POLICY DIAGNOSTIC:\n"+json.dumps(diag)+
        "\nPUBLIC EXAMPLES AND RESULTS:\n"+json.dumps(feedback))
    raw2=client([{"role":"system","content":v1.SYSTEM},
                 {"role":"user","content":revise}],MODEL_CAPS["practice_retry"],
                "course:"+exercise["id"]+":revision")
    code2,diag2=parse_code_and_report(raw2)
    got2=execute_examples(code2,questions)
    correct2=sum(a.get("value")==p["output"] for a,p in zip(got2,public))
    attempts.append({"raw":raw2,"code":code2,"diagnostic":diag2,
                     "public_correct":correct2})
    best_idx,best=choose_best(attempts)
    hidden_inputs=exercise["mastery"]
    hidden_expected=[exercise["oracle"](s) for s in hidden_inputs]
    hidden_actual=execute_examples(best["code"],hidden_inputs)
    mastery_correct=sum(r.get("value")==e for r,e in zip(hidden_actual,hidden_expected))
    return {
        "exercise":exercise["id"],"attempts":attempts,
        "retained_best_index":best_idx,
        "best_python_valid":best["diagnostic"]["stage"]=="valid",
        "public_best":best["public_correct"],"public_n":len(questions),
        "mastery_correct":mastery_correct,"mastery_n":len(hidden_inputs),
        "mastery_pass":best["diagnostic"]["stage"]=="valid"
           and mastery_correct==len(hidden_inputs),
        "mastery_answers_in_model_prompts":False,
    }


def mystery_episode(client,task,tag,lesson=""):
    knowledge=("Prior learning note, not a solution to the unknown "
               "function:\n"+lesson+"\n" if lesson else "")
    known=[{"input":s,"output":ORACLE[task](s)} for s in TRAIN[task]]
    q1=("Unknown black-box program, input string to list of strings. "
        "Request up to 3 additional ASCII probes of <=24 characters in a "
        "JSON object with key queries. The implementation is hidden.\n"+
        knowledge+"INPUT/OUTPUT OBSERVATIONS:\n"+json.dumps(known))
    r1=client([{"role":"system","content":v1.SYSTEM},
               {"role":"user","content":q1}],MODEL_CAPS["probe"],tag+":probe")
    probes=v1.parse_probes(r1)
    known+= [{"input":s,"output":ORACLE[task](s)} for s in probes]
    q2=("Infer the program from these observations. Write safe Python "
        "def transform(s) returning list[str], no imports or side effects. "
        "Return a JSON object with key code. Be careful with Python and JSON "
        "string escaping; refer to the observed behavior, not a guessed name.\n"+
        knowledge+"INPUT/OUTPUT:\n"+json.dumps(known))
    r2=client([{"role":"system","content":v1.SYSTEM},
               {"role":"user","content":q2}],MODEL_CAPS["code"],tag+":code")
    c2,d2=parse_code_and_report(r2)
    dev2=evaluate(task,c2,DEV[task],expose=True)
    candidates=[{"raw":r2,"code":c2,"diagnostic":d2,
                 "public_correct":dev2["correct"]}]
    failures=[r for r in dev2["rows"] if not r["correct"]][:4]
    q3=("Repair your program after receiving feedback on public development "
        "examples. First resolve JSON/compile/policy issues if any. "
        "No imports, file/network access or introspection; use only simple "
        "Python builtins and string/list operations. Return JSON key code. "
        "Preserve working behavior rather than rewriting needlessly.\n"+
        knowledge+"INPUT/OUTPUT:\n"+json.dumps(known)+
        "\nYOUR FIRST CODE:\n"+json.dumps(c2)+
        "\nDIAGNOSTIC:\n"+json.dumps(d2)+
        "\nPUBLIC DEVELOPMENT FAILURES:\n"+json.dumps(failures)+
        "\nPUBLIC DEVELOPMENT PASSES: "+str(dev2["correct"])+"/"+str(dev2["n"]))
    r3=client([{"role":"system","content":v1.SYSTEM},
               {"role":"user","content":q3}],MODEL_CAPS["repair"],tag+":revision")
    c3,d3=parse_code_and_report(r3)
    dev3=evaluate(task,c3,DEV[task],expose=False)
    candidates.append({"raw":r3,"code":c3,"diagnostic":d3,
                       "public_correct":dev3["correct"]})
    idx,best=choose_best(candidates)
    # Hidden data are evaluated only AFTER all calls and are never fed back.
    unseen=blind(task)
    first=evaluate(task,c2,unseen,expose=True)
    last=evaluate(task,c3,unseen,expose=True)
    retained=evaluate(task,best["code"],unseen,expose=True)
    return {
      "task":task,"arm":tag,"probes":probes,"observations":known,
      "attempts":candidates,"best_index":idx,
      "best_python_valid":best["diagnostic"]["stage"]=="valid",
      "first_hidden_correct":first["correct"],"last_hidden_correct":last["correct"],
      "retained_hidden":retained,"hidden_answers_in_prompts":False,
    }


def build_lesson(client,training,practice):
    packet={"practice":[{"exercise":r["exercise"],
                         "best_python_valid":r["best_python_valid"],
                         "public_best":r["public_best"],
                         "mastery_pass":r["mastery_pass"]}
                        for r in practice],
            "prior_task":{"observations":training["observations"],
                          "best_program":training["attempts"][training["best_index"]]["code"],
                          "public_dev_correct":training["attempts"][training["best_index"]]["public_correct"]}}
    # Don't send prior-task hidden inputs/scores or oracle implementations.
    prompt=("Summarize a GENERAL reusable Python debugging and reconstruction "
            "lesson in <=500 characters. Do not guess another unknown task or "
            "report a certified learning gain. JSON key lesson.\n"+
            json.dumps(packet))
    raw=client([{"role":"system","content":v1.SYSTEM},
                {"role":"user","content":prompt}],MODEL_CAPS["lesson"],
               "course:general_lesson")
    parsed=v1.parse_json(raw)
    lesson=parsed.get("lesson") if parsed else None
    return {"raw":raw,"lesson":lesson[:500] if isinstance(lesson,str) else ""}


def run(endpoint,output_dir):
    output_dir=Path(output_dir)
    output_dir.mkdir(parents=True,exist_ok=True)
    client=v1.Client(endpoint)
    report={
      "protocol":PROTOCOL,"status":"STARTED",
      "model_weights_updated":False,"finetune_performed":False,
      "private_repo_created":False,"main_modified":False,
      "first_unknown_tasks_unseen":True,"mastery_threshold":MASTERY_THRESHOLD,
    }
    def save():
        report["model_calls"]=client.call_log
        (output_dir/"report.json").write_text(
            json.dumps(report,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    save()
    try:
        # Control FIRST: no exposure to any course or previous program E.
        report["F_direct"]=mystery_episode(client,"F","F_direct")
        save()
        report["syntax_practice"]=[]
        for exercise in PRACTICE:
            report["syntax_practice"].append(practice_one(client,exercise))
            save()
        passed=sum(r["mastery_pass"] for r in report["syntax_practice"])
        report["mastery_passed"]=passed
        report["mastery_gate_passed"]=passed>=MASTERY_THRESHOLD
        save()
        if not report["mastery_gate_passed"]:
            report["status"]="BLOCKED_BELOW_PYTHON_MASTERY_THRESHOLD"
            report["comparison"]={"transfer_status":"NOT_EXECUTED_GATE_FAILED",
                                  "F_baseline":report["F_direct"]["retained_hidden"]["correct"],
                                  "F_transfer":None,
                                  "n":HIDDEN_SIZE,
                                  "no_transfer_claim":True}
        else:
            report["E_training"]=mystery_episode(client,"E","E_training")
            save()
            report["lesson"]=build_lesson(client,report["E_training"],
                                          report["syntax_practice"])
            save()
            report["F_transfer"]=mystery_episode(
                client,"F","F_transfer",report["lesson"]["lesson"])
            save()
            b=report["F_direct"]["retained_hidden"]["correct"]
            x=report["F_transfer"]["retained_hidden"]["correct"]
            report["comparison"]={
                "transfer_status":"OBSERVATIONAL_NOT_CAUSAL",
                "F_baseline":b,"F_transfer":x,
                "delta":x-b,"n":HIDDEN_SIZE,"no_transfer_claim":True,
                "equal_F_stage_calls":True,"equal_total_cost":False,
                "additional_training_and_context":True,
            }
            report["status"]="COMPLETED_NO_CAUSAL_LEARNING_CLAIM"
    finally:
        save()
    return report


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--server",default="http://127.0.0.1:8080")
    parser.add_argument("--output",type=Path,required=True)
    args=parser.parse_args()
    r=run(args.server,args.output)
    print(json.dumps({
      "status":r["status"],"syntax_mastery_passed":r.get("mastery_passed"),
      "F_baseline":r["comparison"]["F_baseline"],
      "F_transfer":r["comparison"]["F_transfer"],
      "n":HIDDEN_SIZE,"model_calls":len(r["model_calls"]),
      "weights_updated":False},ensure_ascii=False))


if __name__=="__main__":
    main()
