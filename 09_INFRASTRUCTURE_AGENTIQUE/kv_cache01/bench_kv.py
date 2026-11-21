#!/usr/bin/env python3
"""KV-01: real pinned llama.cpp CPU prefix-cache A/B. No training or paid API."""
import argparse
import json
import os
from pathlib import Path
import re
import subprocess
import time
import urllib.error
import urllib.request

PREFIX = (
    "Omega -- contrôle expérimental sur des textes mathématiques finis.\n"
    "Ne crée jamais une affirmation générale. N'infère jamais une source qui n'est pas fournie.\n"
    "La réponse doit être un entier canonique représentant l'élément de Z/mZ.\n"
    "La réduction modulo m s'effectue dans les entiers et donne un entier compris entre 0 et m-1.\n"
    "Ne produis ni citation, ni preuve automatique, ni explication, ni texte complémentaire.\n"
    "Une erreur de calcul sera enregistrée comme erreur, pas réparée automatiquement.\n"
    "Les exemples suivants définissent seulement le format attendu :\n"
    "Dans Z/5Z, (1 + 3) mod 5 = 4.\n"
    "Dans Z/7Z, (6 + 5) mod 7 = 4.\n"
    "Dans Z/11Z, (10 + 9) mod 11 = 8.\n"
    "Dans Z/13Z, (9 + 7) mod 13 = 3.\n"
    "Dans Z/17Z, (16 + 4) mod 17 = 3.\n"
    "Dans Z/19Z, (18 + 9) mod 19 = 8.\n"
    "Applique cette définition, sans autres commentaires.\n\n"
)
CASES = (
    ("C01", 7, 4, 6),
    ("C02", 11, 8, 9),
    ("C03", 13, 3, 7),
    ("C04", 17, 11, 13),
    ("C05", 19, 8, 14),
    ("C06", 23, 15, 18),
    ("C07_REPEAT", 7, 4, 6),
)
ORDER = ("off", "on", "on", "off")
SERVER_HOST = "http://127.0.0.1:8106"
TIMEOUT_SECONDS = 130


def prompt_for(case):
    _, mod, a, b = case
    return PREFIX + f"Problème : Dans Z/{mod}Z, calcule ({a} + {b}) mod {mod}.\nRéponse :"


def request_for(case, cache):
    return {
        "prompt": prompt_for(case),
        "cache_prompt": bool(cache),
        "id_slot": 0,
        "n_predict": 16,
        "temperature": 0,
        "seed": 42,
        "stream": False,
    }


def parse_content(reply):
    if not isinstance(reply, dict) or not isinstance(reply.get("content"), str):
        raise ValueError("INVALID_COMPLETION_CONTENT")
    return reply["content"]


def timing(reply):
    x = reply.get("timings")
    if not isinstance(x, dict):
        return {"cache_n": None, "prompt_n": None, "prompt_ms": None,
                "predicted_n": None, "predicted_ms": None}
    out = {}
    for key in ("cache_n", "prompt_n", "prompt_ms", "predicted_n", "predicted_ms"):
        val = x.get(key)
        if not isinstance(val, (int, float)) or isinstance(val, bool) or val < 0:
            val = None
        out[key] = val
    return out


def exact_number(text, mod):
    t = text.strip()
    if not re.fullmatch(r"[0-9]{1,2}", t):
        return None
    n = int(t)
    return n if n < mod and str(n) == t else None


def post(payload, *, url=SERVER_HOST + "/completion"):
    raw = json.dumps(payload, ensure_ascii=False).encode("utf8")
    req = urllib.request.Request(url, data=raw, headers={"Content-Type":"application/json"}, method="POST")
    t0 = time.monotonic()
    with urllib.request.urlopen(req, timeout=TIMEOUT_SECONDS) as resp:
        data = json.loads(resp.read(300000))
    return data, round(time.monotonic()-t0, 6)


def await_ready(p, host=SERVER_HOST):
    for _ in range(90):
        if p.poll() is not None:
            raise RuntimeError("LOCAL_SERVER_EXITED_BEFORE_READY")
        try:
            with urllib.request.urlopen(host+"/health", timeout=3) as r:
                dat = json.loads(r.read())
                if dat.get("status") == "ok":
                    return
        except (TimeoutError, urllib.error.URLError, ValueError):
            pass
        time.sleep(1)
    raise RuntimeError("LOCAL_SERVER_NOT_READY")


def one_session(mode, n, args, report):
    label = f"block-{n}-{mode}"
    log_path = args.output.parent / (label+".server.log")
    cmd=[str(args.server), "-m", str(args.model), "-c", "4096", "-t", "4",
         "--parallel", "1", "--host", "127.0.0.1", "--port", "8106"]
    with log_path.open("wb") as log:
        p=subprocess.Popen(cmd,stdout=log,stderr=subprocess.STDOUT)
        try:
            await_ready(p)
            rows=[]
            for case in CASES:
                raw, dt=post(request_for(case,mode=="on"))
                content=parse_content(raw)
                _,m,a,b=case
                rows.append({
                    "case":case[0], "reference":(a+b)%m,
                    "content":content, "parsed":exact_number(content,m),
                    "correct":exact_number(content,m)==(a+b)%m,
                    "http_seconds":dt, "timing":timing(raw),
                    "truncated":raw.get("truncated"),
                    "tokens_evaluated":raw.get("tokens_evaluated"),
                    "tokens_cached":raw.get("tokens_cached"),
                    "stopped_eos":raw.get("stopped_eos")
                })
                report["sessions"][-1]["rows"]=rows
                args.output.write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n")
            return rows
        finally:
            p.terminate()
            try: p.wait(timeout=10)
            except subprocess.TimeoutExpired:
                p.kill()
                p.wait(timeout=10)


def sum_key(rows, key):
    vals=[r["timing"][key] for r in rows[1:]]
    return round(sum(vals),4) if vals and all(x is not None for x in vals) else None


def summarize(report):
    summary={}
    for mode in ("off","on"):
        sessions=[x for x in report["sessions"] if x["mode"]==mode and len(x.get("rows",[]))==len(CASES)]
        rows=[r for x in sessions for r in x["rows"]]
        summary[mode]={
            "blocks":len(sessions),
            "non_first_requests":sum(max(0,len(x["rows"])-1) for x in sessions),
            "prompt_n_after_first":sum(sum_key(x["rows"],"prompt_n") or 0 for x in sessions)
             if all(sum_key(x["rows"],"prompt_n") is not None for x in sessions) and sessions else None,
            "cache_n_after_first":sum(sum_key(x["rows"],"cache_n") or 0 for x in sessions)
             if all(sum_key(x["rows"],"cache_n") is not None for x in sessions) and sessions else None,
            "prompt_ms_after_first":round(sum(sum_key(x["rows"],"prompt_ms") or 0 for x in sessions),3)
             if all(sum_key(x["rows"],"prompt_ms") is not None for x in sessions) and sessions else None,
            "http_seconds_after_first":round(sum(r["http_seconds"] for x in sessions for r in x["rows"][1:]),3),
            "exact_math_correct":sum(r["correct"] for r in rows),
            "total_responses":len(rows),
        }
    a=[s for s in report["sessions"] if s["mode"]=="off" and len(s.get("rows",[]))==len(CASES)]
    b=[s for s in report["sessions"] if s["mode"]=="on" and len(s.get("rows",[]))==len(CASES)]
    if len(a)!=2 or len(b)!=2:
        return {"status":"INCOMPLETE_BLOCKS","by_mode":summary}
    diffs=[]
    for i in range(2):
        for off,on in zip(a[i]["rows"],b[i]["rows"]):
            if off["content"]!=on["content"]:
                diffs.append({"pair":i+1,"case":off["case"],
                              "off":off["content"],"on":on["content"]})
    off_n=summary["off"]["prompt_n_after_first"]
    on_n=summary["on"]["prompt_n_after_first"]
    on_cached=summary["on"]["cache_n_after_first"]
    if None in (off_n,on_n,on_cached):
        status="MEASUREMENT_UNAVAILABLE"
    elif on_cached<=0 or on_n>=off_n:
        status="NO_PREFIX_REUSE_DEMONSTRATED"
    else:
        status="PREFIX_REUSE_INSTRUMENTED"
    return {"status":status,"by_mode":summary, "exact_text_differences":diffs,
            "text_byte_identity":len(diffs)==0,
            "correctness_rate_off":summary["off"]["exact_math_correct"],
            "correctness_rate_on":summary["on"]["exact_math_correct"],
            "note":"CPU and network costs not equivalent to token computation; not provider billing"}


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--server",required=True,type=Path)
    ap.add_argument("--model",required=True,type=Path)
    ap.add_argument("--output",required=True,type=Path)
    args=ap.parse_args()
    args.output.parent.mkdir(parents=True,exist_ok=True)
    report={"protocol":"OMEGA_KV01_PINNED_ABBA", "status":"STARTED",
            "model_sha256_expected":"74a4da8c9fdbcd15bd1f6d01d621410d31c6fc00986f5eb687824e7b93d7a9db",
            "llama_sha":"5a4afd80779ba51166b59986e61a0bfbb9e1a4c6",
            "order":ORDER, "sessions":[], "api_paid_calls":0,
            "source_trace":"six synthetic finite math cases plus one repeat"}
    try:
        for i,mode in enumerate(ORDER):
            report["sessions"].append({"index":i+1,"mode":mode,"rows":[]})
            one_session(mode,i+1,args,report)
        report["summary"]=summarize(report)
        report["status"]="COMPLETE"
    except Exception as e:
        report["status"]="INFRA_OR_HARNESS_FAILURE"
        report["error"]=repr(e)
        raise
    finally:
        args.output.write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n",encoding="utf8")
        print("STATUS",report["status"],flush=True)
        if "summary" in report: print("SUMMARY",json.dumps(report["summary"],ensure_ascii=False),flush=True)


if __name__=="__main__":
    main()
