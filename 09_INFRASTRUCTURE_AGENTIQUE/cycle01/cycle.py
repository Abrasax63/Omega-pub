#!/usr/bin/env python3
"""OMEGA CYCLE01: true source->route->exact/LLM->gate->memory->resource report.

No new scientific certification or capability claim. The finite problems have
independent exact oracles; the LLM line selector has only synthetic author gold.
The LLM KV cache remains OFF for the conservative branch, and ON is a
quarantined comparison, never a production decision.
"""
from __future__ import annotations
import argparse
from collections import OrderedDict
from hashlib import sha1,sha256
import json
from pathlib import Path
import sys
from time import perf_counter
import traceback
import urllib.request

HERE=Path(__file__).resolve().parent
AGENT=HERE.parent
ROOT=AGENT.parent
sys.path.insert(0,str(AGENT/"scale01"))
sys.path.insert(0,str(AGENT/"reader_bridge18"))
sys.path.insert(0,str(ROOT/"02_MATHEMATIQUES/defauts_recollement/sources"))

from adaptive_bitset import AdaptiveBitsetRouter
from witness_cache import trace
from delta_gluing_crosscheck import matrix_accepts
import paired
from single_resident import (
    ModelProfile,SingleResidentGovernor,LocalLlamaBackend,AdmissionRefused,
    EXPECTED_ENGINE
)

MANIFEST=HERE/"TASKS.json"
API_LABELS=("off","on")


def sha_bytes(data):
    return sha256(data).hexdigest()


def canonical(obj):
    return json.dumps(obj,sort_keys=True,ensure_ascii=False,separators=(",",":")).encode("utf-8")


def git_blob(raw):
    return sha1(b"blob "+str(len(raw)).encode("ascii")+b"\0"+raw).hexdigest()


def check_pinned_sources(manifest):
    source=manifest["source"]
    path=ROOT/source["path"]
    if git_blob(path.read_bytes())!=source["git_blob"]:
        raise ValueError("MATHEMATICAL_SOURCE_DRIFT")
    ref=manifest["reader_manifest"]
    if git_blob((ROOT/ref["path"]).read_bytes())!=ref["git_blob"]:
        raise ValueError("READER18_MANIFEST_DRIFT")
    if manifest["llama_cpp_sha"]!=EXPECTED_ENGINE:
        raise ValueError("LLAMA_CPP_REVISION_DRIFT")
    if manifest["model_label"]!="0p5b" or manifest["model_sha256"]!=paired.GGUF_SHA256["0p5b"]:
        raise ValueError("UNEXPECTED_MODEL_OR_SHA")
    prepared=paired.prepare()   # uses immutable source blobs and exact arithmetic oracle
    expected_ids=manifest["reader_cases"]
    if [p["ref"]["id"] for p in prepared]!=expected_ids:
        raise ValueError("READER18_SIX_SOURCE_ORDER_CHANGED")
    return prepared


class ScientificMemory:
    """Append-only local JSONL artifact. No cross-run persistence or promotions."""
    def __init__(self,path):
        self.path=Path(path)
        self.path.parent.mkdir(parents=True,exist_ok=True)
        self.records=OrderedDict()
        self.events=0
        self.path.write_text("",encoding="utf-8")

    def remember(self,record_key,record):
        if record_key in self.records:
            event={"type":"EXACT_REVISIT","key":record_key,
                   "original_event_id":self.records[record_key]}
            self._append(event)
            return event["original_event_id"],False
        event_id=sha_bytes(canonical({"key":record_key,"record":record}))
        event={"type":"RECORD","id":event_id,"key":record_key,"record":record}
        self._append(event)
        self.records[record_key]=event_id
        return event_id,True

    def _append(self,event):
        with self.path.open("a",encoding="utf-8") as f:
            f.write(canonical(event).decode("utf-8")+"\n")
        self.events+=1

    def index(self):
        return {"format":"OMEGA_APPEND_ONLY_JSONL_LOCAL_V1",
                "unique_records":len(self.records),
                "record_events":self.events,
                "revisits":self.events-len(self.records),
                "no_persistent_library_mutation":True,
                "content_keys":list(self.records)}

    def validate_replay(self):
        reconstructed={}
        events=0;revisits=0
        for line in self.path.read_text(encoding="utf-8").splitlines():
            event=json.loads(line);events+=1
            if event["type"]=="RECORD":
                expect=sha_bytes(canonical({"key":event["key"],"record":event["record"]}))
                if event["id"]!=expect or event["key"] in reconstructed:
                    raise ValueError("SCIENTIFIC_MEMORY_RECORD_HASH_OR_DUPLICATE")
                reconstructed[event["key"]]=event["id"]
            elif event["type"]=="EXACT_REVISIT":
                if reconstructed.get(event["key"])!=event["original_event_id"]:
                    raise ValueError("SCIENTIFIC_MEMORY_REVISIT_WITHOUT_PROVENANCE")
                revisits+=1
            else:raise ValueError("UNKNOWN_MEMORY_RECORD_TYPE")
        if reconstructed!=self.records or events!=self.events:
            raise ValueError("MEMORY_REPLAY_IS_NOT_IDENTICAL")
        return {"verified_events":events,"verified_unique":len(reconstructed),
                "revisits":revisits,"event_hashes_checked":True}


def verify_finite_question(T,pi,word):
    # Two historical independent implementations: direct micro-traces and
    # forward Boolean matrix on the full finite state space.
    starts=tuple(x for x in range(len(T)) if trace(T,pi,x,len(word))==word)
    direct=bool(starts)
    via_matrix=matrix_accepts(T,pi,word)
    first_empty=next((k for k in range(1,len(word)+1)
        if not any(trace(T,pi,x,k)==word[:k] for x in range(len(T)))),None)
    if direct!=via_matrix:
        raise ValueError("INDEPENDENT_GLUE_ORACLES_DISAGREE")
    return {"admissible":direct,
            "all_initial_witnesses":starts,
            "witness_multiplicity":len(starts),
            "first_empty_length":first_empty}


def run_exact(manifest,book):
    router=AdaptiveBitsetRouter("adaptive-bitset",
                                max_tracked_systems=32,max_prefixes=2048,
                                max_bitset_systems=8)
    t0=perf_counter();rows=[]
    for item in manifest["exact_questions"]:
        T=tuple(item["T"]);pi=tuple(item["pi"]);w=tuple(item["word"])
        computed=router.check(T,pi,w)
        independent=verify_finite_question(T,pi,w)
        if (computed.admissible!=independent["admissible"] or
            computed.witness_start!=(min(independent["all_initial_witnesses"])
                if independent["all_initial_witnesses"] else None) or
            computed.first_empty_length!=independent["first_empty_length"] or
            computed.observed_trace!=(w if independent["admissible"] else None)):
            raise ValueError("EXACT_GLUING_NOT_VERIFIED_BY_TWO_ORACLES")
        if (computed.admissible!=item["expected_admissible"] or
            computed.first_empty_length!=item["expected_first_empty_length"]):
            raise ValueError("FROZEN_EXACT_TASK_EXPECTATION_VIOLATED")
        key=sha_bytes(canonical({
            "source_blob":manifest["source"]["git_blob"],
            "T":T,"pi":pi,"word":w,
        }))
        memory_record={
            "status":"CALCUL_EXACT_VERIFIE",
            "scope":"finite deterministic observations only",
            "input":{"T":T,"pi":pi,"word":w},
            "source":{"path":manifest["source"]["path"],
                      "git_blob":manifest["source"]["git_blob"]},
            "admissible":computed.admissible,
            "witness_start":computed.witness_start,
            "witness_trace":computed.observed_trace,
            "all_initial_witnesses":independent["all_initial_witnesses"],
            "multiplicity":independent["witness_multiplicity"],
            "first_empty_length":computed.first_empty_length,
            "independent_oracles":["direct_micro_trace","boolean_matrix"],
            "new_theorem_claimed":False
        }
        event_id,is_new=book.remember("exact:"+key,memory_record)
        rows.append({
            "task_id":item["id"],"route":"EXACT_BITSET_ADAPTIVE",
            "status":"CALCUL_EXACT_VERIFIE",
            "admissible":computed.admissible,
            "first_empty_length":computed.first_empty_length,
            "witness_start":computed.witness_start,
            "multiplicity":independent["witness_multiplicity"],
            "memory_event_id":event_id,
            "memory_new":is_new,
        })
    return {"status":"EXACT_AND_INDEPENDENT_GATES_PASS",
            "rows":rows,"routing_counters":router.counters(),
            "wall_seconds":round(perf_counter()-t0,6)}


def query_server(port,path,payload):
    req=urllib.request.Request(
        f"http://127.0.0.1:{port}"+path,
        data=canonical(payload),method="POST",
        headers={"Content-Type":"application/json"})
    start=perf_counter()
    with urllib.request.urlopen(req,timeout=240) as response:
        obj=json.loads(response.read(500000))
    if not isinstance(obj,dict):raise ValueError("LLAMA_LOCAL_RESPONSE_NOT_OBJECT")
    return obj,round(perf_counter()-start,6)


def classify_readers(prepared,manifest,book,mode,call):
    """Consumer of *unchanged* Reader18 source selector and gate."""
    t0=perf_counter();rows=[]
    for p in prepared:
        extra={}
        def wrapped(messages):
            gen,metrics=call(messages,mode)
            extra.update(metrics)
            if not isinstance(gen,dict):raise ValueError("CALLBACK_NOT_PROVIDER_OUTPUT")
            return gen
        verified=paired.one_case(p,"0p5b",call=wrapped)
        if verified.get("certifications",0)!=0 or verified.get("horn_rules",0)!=0:
            raise ValueError("LLM_AUTOMATIC_CERTIFICATION_FORBIDDEN")
        if verified.get("status") not in ("VALID","REJECTED"):
            raise ValueError("INVALID_SOURCE_GATE_STATUS")
        if verified["status"]=="VALID" and verified["accepted_count"]!=len(verified["selected"]):
            raise ValueError("SOURCE_GATE_COUNT_MISMATCH")
        if verified.get("blob")!=p["ref"]["blob"]:
            raise ValueError("SCIENTIFIC_SOURCE_BLOB_CHANGED")
        prompt_digest=sha_bytes(canonical(paired.messages(p["candidates"])))
        input_key=sha_bytes(canonical({
            "source_blob":p["ref"]["blob"],"model_sha":manifest["model_sha256"],
            "mode":mode,"messages_sha256":prompt_digest,
        }))
        entry={
            "status":"PROPOSITION_LLM_NON_CERTIFIEE",
            "cache_policy":"EXPERIMENTAL_QUARANTINE" if mode=="on" else "CONSERVATIVE_OFF",
            "source":{"path":p["ref"]["path"],"git_blob":p["ref"]["blob"]},
            "model_sha256":manifest["model_sha256"],
            "messages_sha256":prompt_digest,
            "response_sha256":sha_bytes(verified["raw_reply"].encode("utf-8")),
            "raw_reply":verified["raw_reply"],
            "gate_status":verified["status"],"rejection":verified["rejection"],
            "selected_lines":verified["selected"],
            "accepted_line_count":verified["accepted_count"],
            "synthetic_gold_metrics":verified["metrics"],
            "human_independent_labels":False,
            "theorem_certified":False
        }
        event_id,_=book.remember("llm:"+input_key,entry)
        rows.append({
            "source_id":p["ref"]["id"],"source_blob":p["ref"]["blob"],
            "prompt_sha256":prompt_digest,"status":verified["status"],
            "raw_reply":verified["raw_reply"],"rejection":verified["rejection"],
            "selected":verified["selected"],
            "accepted_count":verified["accepted_count"],
            "metrics":verified["metrics"],
            "model_latency_seconds":verified["seconds"],
            "telemetry":extra,
            "memory_event_id":event_id,
            "policy":"EXPERIMENTAL_QUARANTINE" if mode=="on" else "CONSERVATIVE_OFF"
        })
    return {"mode":mode,"status":"READER18_SOURCE_GATES_APPLIED",
            "rows":rows,
            "quality":paired.summarize_metrics(rows),
            "wall_seconds":round(perf_counter()-t0,3),
            "all_certifications":0}


def compare_modes(off,on):
    if [r["source_id"] for r in off["rows"]]!=[r["source_id"] for r in on["rows"]]:
        raise ValueError("A_B_SOURCE_ORDER_NOT_PAIRED")
    divergences=[]
    for a,b in zip(off["rows"],on["rows"]):
        if a["source_blob"]!=b["source_blob"] or a["prompt_sha256"]!=b["prompt_sha256"]:
            raise ValueError("A_B_SCIENTIFIC_SOURCE_OR_MESSAGES_CHANGED")
        if any(a[k]!=b[k] for k in ("raw_reply","status","selected","rejection","accepted_count")):
            divergences.append({
                "source_id":a["source_id"],
                "off_reply":a["raw_reply"],"on_reply":b["raw_reply"],
                "off_selected":a["selected"],"on_selected":b["selected"],
                "off_status":a["status"],"on_status":b["status"],
            })
    return {
        "status":"LOCAL_TEXT_AND_SELECTION_PARITY" if not divergences else "DIVERGENCE_OBSERVED",
        "cases_compared":len(off["rows"]),
        "divergences":divergences,
        "off_quality":off["quality"],
        "on_quality":on["quality"],
        "real_external_document_quality":"NOT_MEASURED",
    }


def native_callback(port):
    def call(messages,mode):
        rendered,t_template=query_server(port,"/apply-template",{"messages":messages})
        prompt=rendered.get("prompt")
        if not isinstance(prompt,str) or not prompt:
            raise ValueError("NATIVE_CHAT_TEMPLATE_MISSING")
        options={
            "prompt":prompt,"cache_prompt":mode=="on","id_slot":0,
            "n_predict":64,"temperature":0,"seed":42,"stream":False,
            "stop":["<|im_end|>","<|im_start|>"],
        }
        response,t_completion=query_server(port,"/completion",options)
        text=response.get("content")
        if not isinstance(text,str):raise ValueError("LLM_REPLY_NONSTRING")
        tm=response.get("timings")
        if not isinstance(tm,dict):tm={}
        native={k:tm.get(k) if type(tm.get(k)) in (int,float) else None
                for k in ("cache_n","prompt_n","prompt_ms","predicted_n","predicted_ms")}
        return ({
            "raw_reply":text,"seconds":t_completion,
            "usage":None,"finish_reason":"native_completion",
            "server_model":"Qwen2.5-0.5B-Instruct-Q4"
        },{
            "rendered_prompt_sha256":sha_bytes(prompt.encode("utf8")),
            "native":native,"template_http_seconds":t_template,
            "completion_http_seconds":t_completion,
            "llama_truncated":response.get("truncated"),
        })
    return call


def measure_mode(mode,governor,profile,manifest,prepared,book,outfile):
    start=perf_counter()
    activation=governor.activate(profile)
    try:
        callback=native_callback(governor.backend.port)
        measured=classify_readers(prepared,manifest,book,mode,callback)
        measured["peak_rss_kib"]=governor.backend.peak_rss_kib()
        measured["activation"]=activation
    finally:
        governor.release() # force KV cache cold for next phase
    measured["total_wall_seconds_including_start_stop"]=round(perf_counter()-start,3)
    return measured


def run_real(manifest_path,report_path,model_path,binary,outdir):
    outdir.mkdir(parents=True,exist_ok=True)
    book=ScientificMemory(outdir/"memory.jsonl")
    report={"experiment":"OMEGA_CYCLE01_E2E","status":"STARTED",
            "main_changed":False,"paid_api_calls":0,
            "automatic_certifications":0,"stages":{}}
    try:
        manifest=json.loads(manifest_path.read_text(encoding="utf-8"))
        if manifest["version"]!="OMEGA_CYCLE01_FROZEN_2026_11_21":
            raise ValueError("UNREGISTERED_TASK_VERSION")
        prepared=check_pinned_sources(manifest)
        report["stages"]["source_validation"]={
            "status":"PINNED_SOURCES_VERIFIED",
            "exact_blob":manifest["source"]["git_blob"],
            "reader_manifest_blob":manifest["reader_manifest"]["git_blob"],
            "reader_cases":[p["ref"]["id"] for p in prepared]
        }
        report["stages"]["exact"]=run_exact(manifest,book)
        source=report_path.read_bytes()
        if sha_bytes(source)!=manifest["scale01_profile"]["report_sha256"]:
            raise ValueError("SCALE01_PROFILE_ARTIFACT_SHA_MISMATCH")
        profile=ModelProfile.from_scale_report(json.loads(source),model_path)
        governor=SingleResidentGovernor(
            LocalLlamaBackend(binary,port=8129),
            budget_kib=6*1024*1024,
            reserve_kib=512*1024)
        report["stages"]["admission"]={
            "status":"MEASURED_PROFILE_ACCEPTED",
            "scale01_run":manifest["scale01_profile"]["run_id"],
            "profile_report_sha256":sha_bytes(source),
            "model_label":profile.label,
            "model_file_bytes":profile.weight_bytes,
            "measured_peak_rss_kib":profile.observed_peak_rss_kib,
            "reserved_kib":512*1024,
            "budget_kib":6*1024*1024
        }
        report["stages"]["reader_off"]=measure_mode(
            "off",governor,profile,manifest,prepared,book,outdir)
        report["stages"]["reader_on"]=measure_mode(
            "on",governor,profile,manifest,prepared,book,outdir)
        report["stages"]["compare"]=compare_modes(
            report["stages"]["reader_off"],report["stages"]["reader_on"])
        report["status"]="FINISHED_WITH_EXPERIMENTAL_ON_QUARANTINED"
    except Exception as exc:
        report["status"]="FAILED_OR_INDETERMINATE"
        report["exception_type"]=type(exc).__name__
        report["exception"]=str(exc)
        report["traceback"]=traceback.format_exc()
        raise
    finally:
        report["memory_replay"]=book.validate_replay()
        report["memory_index"]=book.index()
        (outdir/"memory_index.json").write_text(
            json.dumps(report["memory_index"],indent=2,ensure_ascii=False)+"\n",
            encoding="utf-8")
        (outdir/"report.json").write_text(
            json.dumps(report,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
        print("CYCLE_STATUS",report["status"],flush=True)
        print("CYCLE_MEMORY",json.dumps(report["memory_replay"]),flush=True)
        if "compare" in report["stages"]:
            print("CYCLE_COMPARE",json.dumps(report["stages"]["compare"]),flush=True)


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--tasks",type=Path,default=MANIFEST)
    ap.add_argument("--profile",type=Path,required=True)
    ap.add_argument("--model",type=Path,required=True)
    ap.add_argument("--server",type=Path,required=True)
    ap.add_argument("--output-dir",type=Path,required=True)
    args=ap.parse_args()
    run_real(args.tasks,args.profile,args.model,args.server,args.output_dir)


if __name__=="__main__":
    main()
