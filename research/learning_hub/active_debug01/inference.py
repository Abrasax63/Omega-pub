"""ACTIVE-DEBUG01 model inference, same-model and same-output-budget experiment.

Three model requests per task: INITIAL shared by both arms,
DIRECT_REVIEW without execution, and FEEDBACK_REVIEW containing only two
public-example execution outcomes. This script NEVER calls evaluator_view(),
reads hidden tests, updates weights, uses paid APIs or writes Git.
"""
from __future__ import annotations
from hashlib import sha256
import argparse
import json
from pathlib import Path
import sys
import time
import traceback
from urllib.request import Request,urlopen

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/"semantic04"))
import core
import execution_guided
import contract

def parse_code(text):
    code,status=core.permissive(text)
    return code,status

def public_feedback(text,public):
    code,status=parse_code(text)
    if code is None:
        return {"status":"UNSAFE_OR_INVALID_CODE","reason":status,
                "examples":[{"input":x["input"],"expected":x["output"],
                             "received":{"error":status}} for x in public]}
    results=core.sandbox.execute_student(code,[x["input"] for x in public])
    return {
        "status":"COMPILED_EXECUTED_RESTRICTED_SANDBOX",
        "total":len(public),
        "correct":sum(g.get("value")==e["output"] for g,e in zip(results,public)),
        "examples":[{"input":e["input"],"expected":e["output"],"received":g}
                    for e,g in zip(public,results)]
    }

class Client:
    def __init__(self,endpoint):
        # Prevent arbitrary network/API endpoints from receiving code.
        if endpoint not in ("http://127.0.0.1:8080","http://localhost:8080"):
            raise ValueError("LOCAL_LOOPBACK_ENDPOINT_ONLY")
        self.url=endpoint+"/v1/chat/completions"
        self.calls=[]

    def ask(self,messages,tag):
        if len(self.calls)>=contract.MAX_MODEL_CALLS:
            raise ValueError("PREDECLARED_MODEL_CALL_BUDGET_EXCEEDED")
        payload={
            "model":contract.MODEL,
            "messages":messages,
            "max_tokens":contract.MAX_TOKENS_PER_CALL,
            "temperature":0,
            "seed":contract.SEED,
            "stream":False
        }
        started=time.monotonic()
        request=Request(self.url,method="POST",
            headers={"Content-Type":"application/json"},
            data=json.dumps(payload).encode())
        with urlopen(request,timeout=200) as resp:
            data=json.load(resp)
        raw=data["choices"][0]["message"]["content"]
        if not isinstance(raw,str):
            raise ValueError("MODEL_RESPONSE_NOT_STRING")
        usage=data.get("usage") or {}
        metrics={
            "phase":tag,"max_output_tokens":contract.MAX_TOKENS_PER_CALL,
            "elapsed_seconds":round(time.monotonic()-started,3),
            "prompt_tokens":usage.get("prompt_tokens"),
            "completion_tokens":usage.get("completion_tokens"),
            "finish_reason":data["choices"][0].get("finish_reason"),
            "output_sha256":sha256(raw.encode()).hexdigest()}
        self.calls.append(metrics)
        return raw


def messages(user):
    return [{"role":"system","content":contract.SYSTEM},
            {"role":"user","content":user}]


def direct_review_prompt(item,initial):
    return (
        item["prompt"]+
        "\nPREVIOUS DRAFT:\n"+initial+
        "\nWithout executing the program or receiving new runtime feedback, "
        "critically review your draft against the original goal and public "
        "examples. Return the best final complete def transform(s) function only."
    )

def feedback_review_prompt(item,initial,feedback):
    return (
        item["prompt"]+
        "\nPREVIOUS DRAFT:\n"+initial+
        "\nACTUAL RESULTS OF RUNNING THE DRAFT IN A RESTRICTED PYTHON "
        "SANDBOX ON THE TWO PUBLIC EXAMPLES ONLY:\n"+
        json.dumps(feedback,ensure_ascii=False)+
        "\nCorrect errors revealed by these observations. Preserve all required "
        "behavior. Return ONLY the corrected complete def transform(s) function."
    )

def select_public_only(item,initial,direct_text,feedback_text):
    visible=item["public"]
    sym=execution_guided.resolve(item["broken"],visible)
    guarded=execution_guided.resolve_guarded(
        item["broken"],visible,model_text=feedback_text)
    first_code,first_status=parse_code(initial)
    direct_code,direct_status=parse_code(direct_text)
    feedback_code,feedback_status=parse_code(feedback_text)
    return {
        "initial":{"raw":initial,"code":first_code,"code_status":first_status,
                   "public_feedback":public_feedback(initial,visible)},
        "direct2":{"raw":direct_text,"code":direct_code,"code_status":direct_status,
                   "public_feedback":public_feedback(direct_text,visible)},
        "feedback2":{"raw":feedback_text,"code":feedback_code,
                     "code_status":feedback_status,
                     "public_feedback":public_feedback(feedback_text,visible)},
        "symbolic":{"code":sym["selected_code"],"status":sym["status"],
                    "candidates_examined":sym["examined"],
                    "matching_public_count":sym["matching_public_count"],
                    "advice_only":True,
                    "new_model_calls":0},
        "guarded_hybrid":{"code":guarded["selected_code"],"status":guarded["status"],
                          "candidates_examined":guarded["examined"],
                          "model_seed_considered":guarded["model_seed_considered"],
                          "matching_public_count":guarded["matching_public_count"],
                          "new_model_calls":0}
    }


def run(endpoint,output):
    client=Client(endpoint)
    items=contract.public_view()
    output=Path(output)
    output.mkdir(parents=True,exist_ok=True)
    report={
        "protocol":"OMEGA_ACTIVE_DEBUG01_INFERENCE",
        "status":"STARTED",
        "model":contract.MODEL,
        "model_sha256":contract.MODEL_SHA256,
        "frozen_git_blob":contract.FROZEN_BLOB,
        "seed":contract.SEED,
        "max_generated_tokens_per_call":contract.MAX_TOKENS_PER_CALL,
        "max_model_calls":contract.MAX_MODEL_CALLS,
        "shared_initial_generation":True,
        "direct_and_feedback_use_two_model_calls_each":True,
        "model_weights_modified":False,
        "paid_api_calls":0,
        "evaluator_view_imported":False,
        "hidden_tests_sent_to_model":False,
        "model_outputs_consumed_without_hidden_feedback":True,
        "calls":[],
        "tasks":{},
    }
    path=output/"inference.json"
    def save():
        report["calls"]=client.calls
        path.write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n",
                        encoding="utf-8")
    save()
    try:
        for item in items:
            ident=item["id"]
            initial=client.ask(messages(item["prompt"]),ident+":INITIAL")
            report["tasks"][ident]={"initial_raw":initial}
            save()

            direct=client.ask(messages(direct_review_prompt(item,initial)),
                              ident+":DIRECT_REVIEW")
            report["tasks"][ident]["direct_raw"]=direct
            save()

            first_feedback=public_feedback(initial,item["public"])
            feedback=client.ask(messages(
                feedback_review_prompt(item,initial,first_feedback)),
                ident+":FEEDBACK_REVIEW")
            report["tasks"][ident]["feedback_raw"]=feedback
            report["tasks"][ident]["first_public_feedback"]=first_feedback
            report["tasks"][ident]["candidates"]=select_public_only(
                item,initial,direct,feedback)
            save()
            print("ACTIVE_DEBUG01_GENERATED_AND_PUBLIC_SELECTED",
                  ident,"calls",len(client.calls),flush=True)
        if len(client.calls)!=contract.MAX_MODEL_CALLS:
            raise ValueError("INCOMPLETE_MODEL_CALLS")
        report["status"]="GENERATION_AND_PUBLIC_SELECTION_COMPLETE_NO_HIDDEN_SCORING"
        save()
        print("ACTIVE_DEBUG01_GENERATION_COMPLETE",
              len(items),len(client.calls),flush=True)
    except Exception:
        report["status"]="TECHNICAL_FAILURE_INFERENCE_INCOMPLETE"
        report["traceback"]=traceback.format_exc()
        save()
        raise
    return report


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--server",default="http://127.0.0.1:8080")
    p.add_argument("--output",type=Path,required=True)
    a=p.parse_args()
    run(a.server,a.output)


if __name__=="__main__":
    main()
