#!/usr/bin/env python3
"""Real Reader18 frozen-source, same-model KV cache ON/OFF comparison.

This experiment uses Reader18 unchanged: documents, candidate extraction,
prompt messages, strict parser, source gate, source labels and scoring.
Only the native llama.cpp /completion cache_prompt option changes.
"""
from __future__ import annotations
import argparse
from hashlib import sha256
import json
from pathlib import Path
import subprocess
import sys
import time
import urllib.error
import urllib.request

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/"reader_bridge18"))
import paired

ORDER=("off","on","on","off")
HOST="http://127.0.0.1:8118"
LABELS=("S01","S01_DUP","S02","S03","S04","S05","S06")
MAX_TOKENS=64


def paired_cases():
    p=paired.prepare()
    assert len(p)==6
    assert [x["ref"]["id"] for x in p]==["S01","S02","S03","S04","S05","S06"]
    return [p[0],p[0],*p[1:]]


def native_request(messages, endpoint):
    body=json.dumps({"messages":messages} if endpoint=="/apply-template" else messages,
                    ensure_ascii=False).encode("utf8")
    req=urllib.request.Request(HOST+endpoint,data=body,method="POST",
                               headers={"Content-Type":"application/json"})
    start=time.perf_counter()
    with urllib.request.urlopen(req,timeout=240) as response:
        data=json.loads(response.read(500000))
    return data,round(time.perf_counter()-start,6)


def completion_request(rendered_prompt, enable_cache):
    payload={
        "prompt":rendered_prompt,
        "cache_prompt":enable_cache,
        "id_slot":0,"n_predict":MAX_TOKENS,"temperature":0,
        "seed":42,"stream":False,
        "stop":["<|im_end|>","<|im_start|>"],
    }
    return native_request(payload,"/completion")


def telemetry(response):
    timing=response.get("timings")
    if not isinstance(timing,dict):
        timing={}
    keys=("cache_n","prompt_n","prompt_ms","predicted_n","predicted_ms")
    out={}
    for k in keys:
        value=timing.get(k)
        out[k]=value if isinstance(value,(int,float)) and not isinstance(value,bool) and value>=0 else None
    return out


def wait_for_ready(p):
    for _ in range(120):
        if p.poll() is not None:
            raise RuntimeError("LLAMA_SERVER_EXITED")
        try:
            with urllib.request.urlopen(HOST+"/health",timeout=2) as r:
                d=json.loads(r.read())
                if d.get("status")=="ok":
                    return
        except (urllib.error.URLError, TimeoutError, ValueError):
            pass
        time.sleep(1)
    raise RuntimeError("LLAMA_SERVER_NOT_READY")


def run_block(args, index, mode, source_rows, report):
    name=f"block-{index}-{mode}"
    log_path=args.output.parent/(name+".server.log")
    cmd=[str(args.server),"-m",str(args.model),"-c","4096","-t","4",
         "--parallel","1","--host","127.0.0.1","--port","8118"]
    with log_path.open("wb") as logs:
        process=subprocess.Popen(cmd,stdout=logs,stderr=subprocess.STDOUT)
        try:
            wait_for_ready(process)
            for label,prepared in zip(LABELS,source_rows):
                stats={}
                def callback(messages):
                    renderer,_=native_request(messages,"/apply-template")
                    prompt=renderer.get("prompt")
                    if not isinstance(prompt,str) or not prompt:
                        raise ValueError("TEMPLATE_RENDERING_INVALID")
                    raw,secs=completion_request(prompt,mode=="on")
                    content=raw.get("content")
                    if not isinstance(content,str):
                        raise ValueError("LLAMA_COMPLETION_TEXT_MISSING")
                    stats.update({
                        "rendered_prompt_sha256":sha256(prompt.encode("utf8")).hexdigest(),
                        "rendered_prompt_chars":len(prompt),
                        "telemetry":telemetry(raw),
                        "http_completion_seconds":secs,
                        "native_tokens_cached":raw.get("tokens_cached"),
                        "native_tokens_evaluated":raw.get("tokens_evaluated"),
                        "native_truncated":raw.get("truncated"),
                    })
                    return {"raw_reply":content,"seconds":secs,
                            "usage":None,
                            "finish_reason":"native_completion",
                            "server_model":args.model_label}
                one=paired.one_case(prepared,args.model_label,call=callback)
                report["blocks"][-1]["rows"].append({**one,"trace_label":label,**stats})
                args.output.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
        finally:
            process.terminate()
            try:process.wait(timeout=15)
            except subprocess.TimeoutExpired:
                process.kill();process.wait(timeout=15)


def sum_native(blocks,mode,key):
    values=[row["telemetry"].get(key)
            for block in blocks if block["mode"]==mode
            for row in block["rows"][1:]]
    if len(values)!=12 or any(x is None for x in values):
        return None
    return round(sum(values),4)


def summarize(report):
    blocks=report["blocks"]
    if len(blocks)!=4 or any(len(x["rows"])!=7 for x in blocks):
        return {"status":"INCOMPLETE_BLOCKS"}
    by_mode={}
    for mode in ("off","on"):
        these=[b for b in blocks if b["mode"]==mode]
        unique=[row for b in these for i,row in enumerate(b["rows"]) if i!=1]
        ag=paired.summarize_metrics(unique)
        by_mode[mode]={
            "blocks":len(these),
            "prompt_n_excluding_first":sum_native(blocks,mode,"prompt_n"),
            "cache_n_excluding_first":sum_native(blocks,mode,"cache_n"),
            "prompt_ms_excluding_first":sum_native(blocks,mode,"prompt_ms"),
            "predicted_n_excluding_first":sum_native(blocks,mode,"predicted_n"),
            "http_seconds_excluding_first":round(sum(r["http_completion_seconds"]
                  for b in these for r in b["rows"][1:]),3),
            "scientific_unique_cases_count":len(unique),
            "scientific_f1_micro":ag["f1"],
            "scientific_precision_micro":ag["precision"],
            "scientific_recall_micro":ag["recall"],
            "false_positive_lines":ag["fp"],
            "gold_correct_lines":ag["tp"],
            "rejections":sum(r["status"]=="REJECTED" for r in unique),
            "abstentions":sum(r["abstained"] for r in unique),
            "accepted_source_lines":sum(r["accepted_count"] for r in unique),
        }
    pairs=[(blocks[0],blocks[1]),(blocks[3],blocks[2])]
    changes=[]
    for pidx,(off,on) in enumerate(pairs):
        for a,b in zip(off["rows"],on["rows"]):
            if a["trace_label"]!=b["trace_label"] or a["blob"]!=b["blob"]:
                raise ValueError("UNPAIRED_OR_CHANGED_SCIENTIFIC_SOURCE")
            if a["rendered_prompt_sha256"]!=b["rendered_prompt_sha256"]:
                raise ValueError("UNPAIRED_OR_CHANGED_RENDERED_PROMPT")
            if a["raw_reply"]!=b["raw_reply"] or a["status"]!=b["status"] or a["selected"]!=b["selected"]:
                changes.append({"pair":pidx+1,"case":a["trace_label"],
                                "off":a["raw_reply"],"on":b["raw_reply"],
                                "off_selected":a["selected"],"on_selected":b["selected"],
                                "off_status":a["status"],"on_status":b["status"]})
    o=by_mode["off"];n=by_mode["on"]
    if None in (o["prompt_n_excluding_first"],n["prompt_n_excluding_first"],n["cache_n_excluding_first"]):
        status="MEASUREMENT_UNAVAILABLE"
    elif n["cache_n_excluding_first"]>0 and n["prompt_n_excluding_first"]<o["prompt_n_excluding_first"]:
        status="PREFIX_REUSE_INSTRUMENTED"
    else:status="NO_PREFIX_REUSE_DEMONSTRATED"
    quality=(n["scientific_f1_micro"] is not None and o["scientific_f1_micro"] is not None
             and n["scientific_f1_micro"]>=o["scientific_f1_micro"]
             and n["false_positive_lines"]<=o["false_positive_lines"]
             and n["rejections"]<=o["rejections"]
             and not changes)
    if changes or n["scientific_f1_micro"]!=o["scientific_f1_micro"] or n["false_positive_lines"]>o["false_positive_lines"]:
        quality_status="QUALITY_OR_OUTPUT_DIVERGENCE_OBSERVED"
    elif o["scientific_f1_micro"]==0 and n["scientific_f1_micro"]==0:
        quality_status="PARITY_OF_WEAK_BASELINE"
    elif quality:quality_status="LOCAL_NO_REGRESSION_ON_FROZEN_READER18"
    else:quality_status="QUALITY_NOT_ESTABLISHED"
    return {"status":status,"quality_status":quality_status,
            "by_mode":by_mode,"differences":changes,
            "compared_pairs":14,"text_and_selection_identity":not changes,
            "no_auto_certification":True,
            "scientific_generalization":"NOT_DEMONSTRATED"}


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--server",type=Path,required=True)
    parser.add_argument("--model",type=Path,required=True)
    parser.add_argument("--model-label",choices=("0p5b","3b"),required=True)
    parser.add_argument("--output",type=Path,required=True)
    args=parser.parse_args()
    args.output.parent.mkdir(parents=True,exist_ok=True)
    report={"protocol":"OMEGA_READER18_SCIENTIFIC_KV_ABBA","status":"STARTED",
            "model_label":args.model_label,"model_sha256_expected":paired.GGUF_SHA256[args.model_label],
            "engine_commit":paired.LLAMA_CPP_SHA,
            "frozen_source_blobs":[x["blob"] for x in json.loads(paired.MANIFEST.read_text())["documents"]],
            "order":ORDER,"labels":LABELS,"blocks":[],"paid_api_calls":0}
    try:
        cases=paired_cases()
        for n,mode in enumerate(ORDER,start=1):
            report["blocks"].append({"index":n,"mode":mode,"rows":[]})
            run_block(args,n,mode,cases,report)
        report["summary"]=summarize(report)
        report["status"]="FINISHED_REAL_LOCAL_INFERENCE"
    except Exception as exc:
        report["status"]="FAILED_INFRA_OR_HARNESS"
        report["error"]=repr(exc)
        raise
    finally:
        args.output.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
        print("RUN_STATUS",report["status"],flush=True)
        if "summary" in report:print("SUMMARY",json.dumps(report["summary"],ensure_ascii=False),flush=True)

if __name__=="__main__":main()
