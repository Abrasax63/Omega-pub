"""OMEGA-PROG-LEARN-01: black-box Python reconstruction and transfer test.

Real local-model pilot, not a weight-training pipeline. Two different hidden
string programs; the model only sees input/output observations. In one arm it
first attempts program A and extracts a lesson; then both arms attempt B with
equal B-stage call/output budgets. Exact tests remain inaccessible in prompts.
"""
from __future__ import annotations

import argparse
import ast
from hashlib import sha256
import json
import os
from pathlib import Path
import random
import subprocess
import sys
import tempfile
import time
from urllib.request import Request, urlopen

EXPERIMENT = "OMEGA-PROG-LEARN-01-2026-11-22"
MODEL = "Qwen2.5-3B-Instruct-Q4_K_M"
SEED = 47621
MAX_PROBES = 3
MAX_INPUT = 24
MAX_CODE_CHARS = 4500
MODEL_CALL_CAPS = {"probe":140, "code":660, "repair":700, "lesson":200}
ALPHABET = "abAB|\\cC"
SYSTEM = (
    "You are learning Python by observing unknown programs. "
    "Do not assume the intended algorithm; infer it from examples. "
    "Respond with one valid JSON object only. "
    "No imports, files, network, subprocesses, or introspection in submitted code. "
    "The code must define def transform(s): returning a list of strings. "
    "You may report uncertainty; do not claim you learned model weights."
)

# ORACLE CODE IS NEVER INCLUDED IN ANY MODEL MESSAGE.
def _oracle_a(s):
    """A: adjacent case-insensitive run summary, including punctuation."""
    if not s:
        return []
    out = []
    current = s[0].lower()
    count = 1
    for ch in s[1:]:
        lowered = ch.lower()
        if lowered == current:
            count += 1
        else:
            out.append(current + ":" + str(count))
            current = lowered
            count = 1
    out.append(current + ":" + str(count))
    return out


def _oracle_b(s):
    """B: split on unescaped pipe, skip empty fields, backslash escapes next."""
    tokens, buf = [], []
    escaped = False
    for ch in s:
        if escaped:
            buf.append(ch)
            escaped = False
        elif ch == "\\":
            escaped = True
        elif ch == "|":
            if buf:
                tokens.append("".join(buf))
            buf = []
        else:
            buf.append(ch)
    if escaped:
        buf.append("\\")
    if buf:
        tokens.append("".join(buf))
    return tokens


SEEDS = {
    "A": ["", "a", "aAa", "aabb", "abBA", "||", "aaBBa"],
    "B": ["", "a", "a|b", "a||b", "a\\|b|c", "a\\", "|a|"],
}
DEV = {
    "A": ["ABba", "aA|Bb", "baAAAB", "a|a", "AaaBbb", "CccaaB", "aAaAa"],
    "B": ["a\\|b", "||a||", "ab\\", "\\|", "a\\\\b", "a|b\\|c", "a\\b|c"],
}


def hidden_inputs(task, n=36):
    rng = random.Random(SEED + (11 if task == "A" else 29))
    candidates = []
    for _ in range(n * 5):
        size = rng.randint(0, 18)
        s = "".join(rng.choice(ALPHABET) for _ in range(size))
        if s not in SEEDS[task] and s not in DEV[task] and s not in candidates:
            candidates.append(s)
        if len(candidates) >= n:
            break
    if len(candidates) != n:
        raise RuntimeError("INSUFFICIENT_BLIND_INPUTS")
    return candidates


def oracle(task, s):
    if task == "A":
        return _oracle_a(s)
    if task == "B":
        return _oracle_b(s)
    raise ValueError("UNKNOWN_TASK")


def obs(task, strings):
    return [{"input":s, "output":oracle(task,s)} for s in strings]


def parse_json(raw):
    if not isinstance(raw, str):
        return None
    try:
        value = json.loads(raw.strip())
        return value if isinstance(value,dict) else None
    except (json.JSONDecodeError, ValueError):
        return None


def parse_probes(raw):
    data = parse_json(raw)
    queries = data.get("queries") if data else None
    if not isinstance(queries,list) or len(queries) > MAX_PROBES:
        return []
    if any(not isinstance(s,str) or len(s)>MAX_INPUT or
           any(ord(c)>127 or ord(c)<32 for c in s) for s in queries):
        return []
    # No retries when invalid/duplicates: retain the model's behavior.
    return list(dict.fromkeys(queries))


def parse_code(raw):
    data = parse_json(raw)
    code = data.get("code") if data else None
    if not isinstance(code,str) or not code.strip() or len(code)>MAX_CODE_CHARS:
        return None
    return code


# Stronger than checking for imports alone: a narrow AST language.
FORBIDDEN_AST = (ast.Import,ast.ImportFrom,ast.ClassDef,ast.AsyncFunctionDef,
                 ast.Lambda,ast.With,ast.AsyncWith,ast.Try,ast.Raise,
                 ast.Global,ast.Nonlocal,ast.Delete,ast.Yield,ast.YieldFrom,
                 ast.Await,ast.NamedExpr)
BUILTIN_CALLS = frozenset((
    "len","range","enumerate","str","int","list","dict","set",
    "tuple","min","max","sum","abs","bool","ord","chr","reversed",
))
METHODS = frozenset((
    "append","lower","upper","casefold","join","split","replace",
    "startswith","endswith","isdigit","isalpha","isalnum","isupper","islower","strip","pop","count","insert",
))


def validate_program(code):
    if not isinstance(code,str) or len(code)>MAX_CODE_CHARS:
        raise ValueError("CODE_TOO_LARGE")
    try:
        tree = ast.parse(code,mode="exec")
    except SyntaxError as e:
        raise ValueError("INVALID_PYTHON_SYNTAX") from e
    if (len(tree.body)!=1 or not isinstance(tree.body[0],ast.FunctionDef)
            or tree.body[0].name!="transform"):
        raise ValueError("MUST_DEFINE_ONLY_TRANSFORM")
    func=tree.body[0]
    args=func.args
    if (len(args.posonlyargs)!=0 or len(args.args)!=1 or
            args.args[0].arg!="s" or args.vararg or args.kwarg or
            args.kwonlyargs or args.defaults or args.kw_defaults or
            func.decorator_list or func.returns):
        raise ValueError("TRANSFORM_TAKES_ONLY_ONE_STRING")
    if len(list(ast.walk(tree)))>360:
        raise ValueError("PROGRAM_TOO_COMPLEX")
    for node in ast.walk(tree):
        if isinstance(node,FORBIDDEN_AST):
            raise ValueError("FORBIDDEN_SYNTAX_"+type(node).__name__)
        if isinstance(node,ast.FunctionDef) and node is not func:
            raise ValueError("NO_NESTED_FUNCTIONS")
        if isinstance(node,ast.Name):
            if "__" in node.id or node.id.startswith("_"):
                raise ValueError("FORBIDDEN_IDENTIFIER")
        if isinstance(node,ast.Attribute):
            if node.attr not in METHODS:
                raise ValueError("FORBIDDEN_ATTRIBUTE")
        if isinstance(node,ast.Call):
            if isinstance(node.func,ast.Name):
                if node.func.id not in BUILTIN_CALLS:
                    raise ValueError("FORBIDDEN_CALL")
            elif isinstance(node.func,ast.Attribute):
                if node.func.attr not in METHODS:
                    raise ValueError("FORBIDDEN_METHOD")
            else:
                raise ValueError("FORBIDDEN_DYNAMIC_CALL")
        if isinstance(node,ast.Constant):
            if isinstance(node.value,(bytes,complex)) or (
                    isinstance(node.value,(int,float)) and abs(node.value)>1000000):
                raise ValueError("FORBIDDEN_LITERAL")
    return True


# Trusted worker source, launched in a fresh process with resource quotas.
WORKER = r"""
import ast, builtins, json, resource, sys
resource.setrlimit(resource.RLIMIT_CPU,(2,2))
resource.setrlimit(resource.RLIMIT_AS,(192*1024*1024,192*1024*1024))
resource.setrlimit(resource.RLIMIT_FSIZE,(0,0))
payload=json.load(sys.stdin)
allowed=("len","range","enumerate","str","int","list","dict","set",
         "tuple","min","max","sum","abs","bool","ord","chr")
env={"__builtins__":{k:getattr(builtins,k) for k in allowed}}
code=compile(payload["code"],"student_program","exec")
exec(code,env,env)
out=[]
for text in payload["inputs"]:
    try:
        result=env["transform"](text)
        if not isinstance(result,list) or len(result)>60 or any(
                not isinstance(x,str) or len(x)>80 for x in result):
            out.append({"error":"INVALID_RETURN_TYPE_OR_SIZE"})
        else:
            out.append({"value":result})
    except Exception as exc:
        out.append({"error":type(exc).__name__})
json.dump(out,sys.stdout)
"""


def execute_student(code, inputs):
    try:
        validate_program(code)
    except ValueError as e:
        return [{"error":str(e)} for _ in inputs]
    if not inputs:
        return []
    if len(inputs)>48 or any(not isinstance(s,str) or len(s)>MAX_INPUT
                             for s in inputs):
        raise ValueError("INPUT_BATCH_REJECTED")
    with tempfile.TemporaryDirectory() as tmp:
        worker=Path(tmp)/"worker.py"
        worker.write_text(WORKER,encoding="utf-8")
        try:
            p=subprocess.run([sys.executable,"-I","-S",str(worker)],
                cwd=tmp, env={"PATH":"/usr/bin:/bin","PYTHONIOENCODING":"utf-8"},
                input=json.dumps({"code":code,"inputs":inputs}),
                text=True, stdout=subprocess.PIPE,stderr=subprocess.PIPE,
                timeout=4,check=False)
            if p.returncode!=0:
                return [{"error":"SANDBOX_EXIT_"+str(p.returncode)}
                        for _ in inputs]
            result=json.loads(p.stdout)
            if not isinstance(result,list) or len(result)!=len(inputs):
                raise ValueError("SANDBOX_RESULT_INVALID")
            return result
        except (subprocess.TimeoutExpired, ValueError, json.JSONDecodeError):
            return [{"error":"SANDBOX_TIMEOUT_OR_INVALID"} for _ in inputs]


def evaluate(task, code, inputs, show_expected=False):
    tested=execute_student(code,inputs) if code is not None else [
        {"error":"NO_VALID_CODE"} for _ in inputs]
    rows=[]
    for text,obtained in zip(inputs,tested):
        expected=oracle(task,text)
        correct=obtained.get("value")==expected
        row={"input":text,"correct":correct}
        if show_expected:
            row.update({"expected":expected,"received":obtained})
        rows.append(row)
    return {"total":len(rows),"correct":sum(x["correct"] for x in rows),
            "rows":rows}


class Client:
    def __init__(self,endpoint):
        self.url=endpoint.rstrip("/")+"/v1/chat/completions"
        self.call_log=[]
    def __call__(self,messages,tokens,tag):
        request={"model":MODEL,"messages":messages,"max_tokens":tokens,
                 "seed":SEED,"temperature":0,"stream":False,
                 "response_format":{"type":"json_object"}}
        req=Request(self.url,method="POST",
                    headers={"Content-Type":"application/json"},
                    data=json.dumps(request).encode())
        t=time.monotonic()
        with urlopen(req,timeout=220) as response:
            obj=json.load(response)
        raw=obj["choices"][0]["message"]["content"]
        if not isinstance(raw,str):
            raise ValueError("MODEL_OUTPUT_NOT_STRING")
        metric={"tag":tag,"elapsed_seconds":round(time.monotonic()-t,3),
                "usage":obj.get("usage",{}),
                "finish_reason":obj["choices"][0].get("finish_reason"),
                "raw_sha256":sha256(raw.encode()).hexdigest(),
                "cap":tokens}
        self.call_log.append(metric)
        return raw


def lesson_from_a(client,episode):
    prompt=(
        "Summarize reusable Python programming lessons from the experience "
        "below. Do NOT mention the specific A input/output function or propose "
        "a solution to the unknown next function. Focus on state handling, "
        "boundaries and testing. Return JSON with key lesson (string at most "
        "500 characters).\n[LEARNING SESSION A]\n"+
        json.dumps({"observations":episode["observations"],
                    "first_code":episode["code_first"],
                    "dev_feedback":episode["dev_feedback"],
                    "corrected_code":episode["code_revised"]},
                   ensure_ascii=False)+"\n[END]")
    raw=client([{"role":"system","content":SYSTEM},
                {"role":"user","content":prompt}],
               MODEL_CALL_CAPS["lesson"],"A:lesson")
    parsed=parse_json(raw)
    val=parsed.get("lesson") if parsed else None
    return {"raw":raw,"lesson":val[:500] if isinstance(val,str) else ""}


def run_episode(task,client,tag,lesson=None):
    """One three-call program reconstruction episode; gold only in observations."""
    initial=obs(task,SEEDS[task])
    lesson_text=("Previously learned general Python lessons (NOT a solution "
                 "to this new hidden program): "+lesson+"\n"
                 if lesson else "")
    probe_prompt=(
        "Black-box task "+task+": unknown transform(string) -> list of strings. "
        "You cannot see the source. You may request up to 3 additional string "
        "inputs. Return JSON {\"queries\":[\"...\",...]}. "
        "Avoid repeating the observations. ASCII only; length <= 24.\n"+
        lesson_text+"EXAMPLES:\n"+json.dumps(initial))
    probes_raw=client([{"role":"system","content":SYSTEM},
                       {"role":"user","content":probe_prompt}],
                      MODEL_CALL_CAPS["probe"],tag+":probe")
    probes=parse_probes(probes_raw)
    observations=initial+obs(task,probes)
    draft_prompt=(
        "Infer the unknown program's behavior ONLY from the observations "
        "below. Write Python code implementing def transform(s): returning "
        "list[str]. The code must have no imports, file access, introspection, "
        "or extra top-level statements. Return JSON with key code (Python "
        "source) and optionally reasoning.\n"+lesson_text+
        "OBSERVATIONS:\n"+json.dumps(observations))
    code_raw=client([{"role":"system","content":SYSTEM},
                     {"role":"user","content":draft_prompt}],
                    MODEL_CALL_CAPS["code"],tag+":code")
    code_first=parse_code(code_raw)
    dev=evaluate(task,code_first,DEV[task],show_expected=True)
    # Feedback is restricted to development examples fixed before the run.
    failing=[r for r in dev["rows"] if not r["correct"]][:4]
    repair_prompt=(
        "Your first program was tested on separate development cases. "
        "Fix the implementation if needed; otherwise return the same code. "
        "No imports or unsafe operations. Return one JSON object with key "
        "code containing the complete revised def transform(s).\n"+
        lesson_text+"EARLIER OBSERVATIONS:\n"+json.dumps(observations)+
        "\nFIRST CODE:\n"+json.dumps(code_first)+
        "\nDEVELOPMENT RESULTS (at most four failures):\n"+
        json.dumps(failing)+"\nPassed cases: "+str(dev["correct"])+
        " / "+str(dev["total"]))
    revised_raw=client([{"role":"system","content":SYSTEM},
                        {"role":"user","content":repair_prompt}],
                       MODEL_CALL_CAPS["repair"],tag+":repair")
    code_revised=parse_code(revised_raw)
    if code_revised is None:
        code_revised=code_first
    # HOLDOUT IS NEVER SENT TO THE MODEL OR USED IN REPAIR.
    final=evaluate(task,code_revised,hidden_inputs(task),show_expected=True)
    first=evaluate(task,code_first,hidden_inputs(task),show_expected=False)
    return {
        "task":task,"tag":tag,
        "initial_obs_count":len(initial),"probes_requested":probes,
        "observations":observations,
        "model_raw":{"probe":probes_raw,"code":code_raw,"repair":revised_raw},
        "code_first":code_first, "code_revised":code_revised,
        "dev_feedback":dev, "hidden_first":{"total":first["total"],"correct":first["correct"]},
        "hidden_final":final,"max_model_calls":3,
        "oracle_source_given_to_model":False,
    }


def conduct(endpoint,output):
    output=Path(output);output.mkdir(parents=True,exist_ok=True)
    client=Client(endpoint)
    report={"protocol":EXPERIMENT,"status":"STARTED","model":MODEL,
            "secret_tests_shown_to_model":False,"teacher_source_shown_to_model":False,
            "model_parameters_updated":False,"weight_training":False,
            "private_repository_created":False,
            "experimental_branch_only":True}
    def save():
        report["client_call_log"]=client.call_log
        (output/"report.json").write_text(
            json.dumps(report,indent=2,ensure_ascii=False)+"\n",
            encoding="utf-8")
    save()
    try:
        # BASELINE FIRST: cannot receive the first experiment's notes.
        report["B_baseline"]=run_episode("B",client,"B_baseline")
        save()
        report["A_learning"]=run_episode("A",client,"A_learning")
        save()
        memory=lesson_from_a(client,report["A_learning"])
        report["lesson"]=memory
        save()
        report["B_transfer"]=run_episode(
            "B",client,"B_transfer",lesson=memory["lesson"])
        save()
        a=report["B_baseline"]["hidden_final"]
        b=report["B_transfer"]["hidden_final"]
        report["comparison"]={
            "same_hidden_B_cases":True,
            "same_B_stage_call_caps":True,
            "B_baseline_correct":a["correct"],
            "B_transfer_correct":b["correct"],
            "B_cases":a["total"],
            "delta_correct":b["correct"]-a["correct"],
            "A_learning_additional_calls":4,
            "direct_cost_not_equal_to_learning_arm":True,
            "independent_transfer_experiment":False,
            "claim":"ONE_SHOT_IN_CONTEXT_SKILL_TRANSFER_ONLY_NOT_GRADIENT_TRAINING",
            "causal_gain_certified":False,
        }
        report["status"]="COMPLETED_UNVERIFIED_TRANSFER"
    finally:
        save()
    return report


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--server",default="http://127.0.0.1:8080")
    p.add_argument("--output",type=Path,required=True)
    a=p.parse_args()
    result=conduct(a.server,a.output)
    print(json.dumps({
        "status":result["status"],"protocol":EXPERIMENT,
        "B_baseline":result["comparison"]["B_baseline_correct"],
        "B_transfer":result["comparison"]["B_transfer_correct"],
        "B_total":result["comparison"]["B_cases"],
        "model_calls":len(result["client_call_log"]),
        "weights_updated":False},ensure_ascii=False))


if __name__=="__main__":
    main()
