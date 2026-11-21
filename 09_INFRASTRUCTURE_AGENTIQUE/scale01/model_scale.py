#!/usr/bin/env python3
"""SCALE01: pinned model RAM/throughput scaling on frozen Reader18 source gates.

Input volume 6→12→24 means independent source-reading requests, not a longer
model context or new documents: exactly six original scientific fixtures repeat.
The OFF and ON runs use byte-identical chat-templated prompts and same model.
"""
from __future__ import annotations
import argparse
from hashlib import sha256
import json
from pathlib import Path
import re
import subprocess
import sys
from time import perf_counter

HERE=Path(__file__).resolve().parent
AGENT=HERE.parent
sys.path.insert(0,str(AGENT/"kv_reader18"))
import bench as kv
import paired

STAGES=(6,12,24)
ORDER=("off","on","on","off")
MODEL_VERSIONS=paired.GGUF_SHA256
EXPECTED_ENGINE=paired.LLAMA_CPP_SHA
RSS_LIMIT_KIB=6*1024*1024


def proc_peak_rss_kib(pid):
    """Linux kernel process high water resident size, not total system RAM."""
    status=Path(f"/proc/{pid}/status")
    data=status.read_text(encoding="utf8")
    found=re.search(r"(?m)^VmHWM:\s*(\d+)\s+kB$",data)
    if found is None:
        raise RuntimeError("LINUX_VMHWM_UNAVAILABLE")
    return int(found.group(1))


def summary_metrics(rows):
    agg=paired.summarize_metrics(rows)
    return {
        "f1":agg["f1"],"precision":agg["precision"],
        "recall":agg["recall"],"tp":agg["tp"],
        "fp":agg["fp"],"fn":agg["fn"],
        "rejects":sum(r["status"]=="REJECTED" for r in rows),
        "abstentions":sum(r["abstained"] for r in rows),
        "admitted_source_lines":sum(r["accepted_count"] for r in rows),
    }


def run_one_block(args,rows,mode,index,report):
    block=report["blocks"][-1]
    name=f"block-{index}-{mode}"
    logfile=args.output.parent/(name+".server.log")
    cmd=[str(args.server),"-m",str(args.model),"-c","4096","-t","4",
         "--parallel","1","--host","127.0.0.1","--port","8118"]
    t0=perf_counter()
    with logfile.open("wb") as log:
        process=subprocess.Popen(cmd,stdout=log,stderr=subprocess.STDOUT)
        try:
            kv.wait_for_ready(process)
            block["server_startup_seconds"]=round(perf_counter()-t0,3)
            if proc_peak_rss_kib(process.pid)>RSS_LIMIT_KIB:
                raise RuntimeError("RESOURCE_LIMIT_AT_LOAD")
            for count in STAGES:
                stage_start=perf_counter()
                stage={"documents_processed":count,"rows":[]}
                block["stages"].append(stage)
                for pos in range(count):
                    item=rows[pos%len(rows)]
                    telemetry={}
                    def generate(messages):
                        rendered,_=kv.native_request(messages,"/apply-template")
                        prompt=rendered.get("prompt")
                        if not isinstance(prompt,str) or not prompt:
                            raise ValueError("EMPTY_RENDERED_PROMPT")
                        native,elapsed=kv.completion_request(prompt,mode=="on")
                        raw=native.get("content")
                        if not isinstance(raw,str):
                            raise ValueError("NONSTRING_MODEL_REPLY")
                        telemetry.update({
                            "prompt_sha256":sha256(prompt.encode("utf8")).hexdigest(),
                            "prompt_chars":len(prompt),
                            "native":kv.telemetry(native),
                            "completion_seconds":elapsed,
                            "truncated":native.get("truncated")
                        })
                        return {
                            "raw_reply":raw,"seconds":elapsed,
                            "usage":None,
                            "finish_reason":"native_completion",
                            "server_model":args.model_label,
                        }
                    verdict=paired.one_case(item,args.model_label,call=generate)
                    stage["rows"].append({
                        "request_index":pos,"source_id":item["ref"]["id"],
                        "source_blob":item["ref"]["blob"],
                        **verdict,**telemetry,
                    })
                    if proc_peak_rss_kib(process.pid)>RSS_LIMIT_KIB:
                        raise RuntimeError("RESOURCE_LIMIT_DURING_INFERENCE")
                stage["wall_seconds"]=round(perf_counter()-stage_start,3)
                stage["server_peak_rss_kib"]=proc_peak_rss_kib(process.pid)
                stage["quality"]=summary_metrics(stage["rows"])
                args.output.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
            block["server_peak_rss_kib"]=proc_peak_rss_kib(process.pid)
        finally:
            block["total_block_wall_seconds"]=round(perf_counter()-t0,3)
            process.terminate()
            try:process.wait(timeout=15)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait(timeout=15)
            args.output.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf8")


def sum_field(rows,name):
    values=[r["native"][name] for r in rows]
    if not values or any(x is None for x in values):
        return None
    return round(sum(values),3)


def aggregate(report):
    blocks=report["blocks"]
    if len(blocks)!=4 or any([s["documents_processed"] for s in b["stages"]]!=list(STAGES) for b in blocks):
        return {"status":"INCOMPLETE_BLOCKS"}
    paired_differences=[]
    for pair,(off,on) in enumerate(((blocks[0],blocks[1]),(blocks[3],blocks[2])),1):
        for os,ns in zip(off["stages"],on["stages"]):
            for a,b in zip(os["rows"],ns["rows"]):
                if (a["source_id"],a["source_blob"],a["prompt_sha256"])!=(
                    b["source_id"],b["source_blob"],b["prompt_sha256"]):
                    raise ValueError("SCIENTIFIC_INPUT_OR_PROMPT_CHANGED")
                if any(a[k]!=b[k] for k in (
                    "raw_reply","status","rejection","selected","accepted_count"
                )):
                    paired_differences.append({
                        "pair":pair,"documents_processed":os["documents_processed"],
                        "id":a["source_id"],"index":a["request_index"],
                        "off_text":a["raw_reply"],"on_text":b["raw_reply"],
                        "off_selection":a["selected"],"on_selection":b["selected"],
                    })
    by_mode={}
    for mode in ("off","on"):
        these=[b for b in blocks if b["mode"]==mode]
        by_size={}
        for count in STAGES:
            stages=[next(s for s in b["stages"] if s["documents_processed"]==count) for b in these]
            source_rows=[r for s in stages for r in s["rows"]]
            by_size[str(count)]={
                "documents_processed":count*len(stages),
                "unique_source_documents":6,
                "prompt_tokens_computed":sum_field(source_rows,"prompt_n"),
                "cached_prefix_tokens":sum_field(source_rows,"cache_n"),
                "prompt_ms":sum_field(source_rows,"prompt_ms"),
                "generation_tokens":sum_field(source_rows,"predicted_n"),
                "http_completion_seconds":round(sum(r["completion_seconds"] for r in source_rows),3),
                "stage_wall_seconds":round(sum(s["wall_seconds"] for s in stages),3),
                "quality":summary_metrics(source_rows),
            }
        by_mode[mode]={
            "size_levels":by_size,
            "server_peak_rss_kib_max":max(b["server_peak_rss_kib"] for b in these),
            "total_block_wall_seconds":round(sum(b["total_block_wall_seconds"] for b in these),3),
            "server_startup_seconds":round(sum(b["server_startup_seconds"] for b in these),3),
        }
    all_off=sum(by_mode["off"]["size_levels"][str(s)]["prompt_tokens_computed"] or 0 for s in STAGES)
    all_on=sum(by_mode["on"]["size_levels"][str(s)]["prompt_tokens_computed"] or 0 for s in STAGES)
    on_cached=[by_mode["on"]["size_levels"][str(s)]["cached_prefix_tokens"] for s in STAGES]
    measurable=all(x is not None for mode in ("off","on") for s in STAGES
        for x in (by_mode[mode]["size_levels"][str(s)]["prompt_tokens_computed"],
                  by_mode[mode]["size_levels"][str(s)]["cached_prefix_tokens"]))
    cache_status=(
        "MEASUREMENT_UNAVAILABLE" if not measurable else
        "PREFIX_REUSE_INSTRUMENTED" if sum(on_cached)>0 and all_on<all_off else
        "NO_REUSE_DEMONSTRATED"
    )
    return {
        "status":cache_status,
        "quality_status":"DIVERGENCE_OBSERVED" if paired_differences else "LOCAL_TEXT_AND_SOURCE_GATE_PARITY",
        "matched_comparisons":sum(STAGES)*2,
        "divergences":paired_differences,
        "by_mode":by_mode,
        "training_parameters_increased":False,
        "unique_documents_increased":False,
        "window_context_increased":False,
        "human_quality_verified":False,
    }


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--server",required=True,type=Path)
    ap.add_argument("--model",required=True,type=Path)
    ap.add_argument("--model-label",required=True,choices=("0p5b","3b"))
    ap.add_argument("--output",required=True,type=Path)
    args=ap.parse_args()
    args.output.parent.mkdir(parents=True,exist_ok=True)
    report={
        "experiment":"OMEGA_SCALE01_READER18_PINNED_MODEL_RAM_DATA",
        "status":"STARTED",
        "model_label":args.model_label,
        "model_expected_sha256":MODEL_VERSIONS[args.model_label],
        "engine_sha":EXPECTED_ENGINE,
        "model_weight_file_bytes":args.model.stat().st_size,
        "source_type":"six synthetic Reader18 documents repeated, no new external source gold",
        "order":ORDER,"stages":STAGES,"blocks":[],
        "server_rss_limit_kib":RSS_LIMIT_KIB,
        "paid_api_calls":0,"main_changed":False,
    }
    try:
        sources=paired.prepare()
        assert len(sources)==6
        for idx,mode in enumerate(ORDER,1):
            report["blocks"].append({"index":idx,"mode":mode,"stages":[]})
            run_one_block(args,sources,mode,idx,report)
        report["summary"]=aggregate(report)
        report["status"]="FINISHED"
    except Exception as exc:
        report["status"]="FAILED_RESOURCE_OR_INFRA_OR_HARNESS"
        report["error"]=repr(exc)
        raise
    finally:
        args.output.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n")
        print("STATUS",report["status"],flush=True)
        if "summary" in report:
            print("SUMMARY",json.dumps(report["summary"],ensure_ascii=False),flush=True)

if __name__=="__main__":
    main()
