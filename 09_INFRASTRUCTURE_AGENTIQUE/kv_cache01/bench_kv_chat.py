#!/usr/bin/env python3
"""KV02 new chat-template control. Original KV01 prompts and results untouched."""
import argparse
import json
from pathlib import Path
import sys
import bench_kv as base

SYSTEM = (
    "Tu es un assistant de calcul pour un test local.\n"
    "Lis la question et réponds uniquement par le résultat entier décimal.\n"
    "N'écris ni ponctuation, ni phrase supplémentaire, ni exemple après le résultat.\n"
    "Exemples exacts du format demandé :\n"
    "Question : Calcule exactement 1 + 1.\nRéponse : 2\n"
    "Question : Calcule exactement 2 + 2.\nRéponse : 4\n"
    "Question : Calcule exactement 1 + 3.\nRéponse : 4\n"
    "Quand tu vois une nouvelle question, fais l'addition de ses deux nombres.\n"
    "Ne répète pas la question, ne change pas le format, et ne produis rien après l'entier.\n"
    "Les exemples donnent seulement la règle de présentation.\n"
)
CASES = (
    ("KV02-C01", 101, 2, 3),
    ("KV02-C02", 101, 3, 4),
    ("KV02-C03", 101, 5, 2),
    ("KV02-C04", 101, 6, 3),
    ("KV02-C05", 101, 4, 5),
    ("KV02-C06", 101, 2, 6),
    ("KV02-C07_REPEAT", 101, 2, 3),
)

def render_qwen_chat(case):
    _, _, a, b = case
    user = f"Calcule exactement {a} + {b}. Réponds uniquement par le nombre."
    # Standard Qwen2.5-Instruct chat framing, fixed before inferencing.
    return ("<|im_start|>system\n"+SYSTEM+"<|im_end|>\n"
            "<|im_start|>user\n"+user+"<|im_end|>\n"
            "<|im_start|>assistant\n")

def main():
    # Reuse pinned A/B harness as-is. Change its inputs only for this program.
    base.CASES = CASES
    base.prompt_for = render_qwen_chat
    p=argparse.ArgumentParser()
    p.add_argument("--server",required=True,type=Path)
    p.add_argument("--model",required=True,type=Path)
    p.add_argument("--output",required=True,type=Path)
    args=p.parse_args()
    args.output.parent.mkdir(parents=True,exist_ok=True)
    report={"protocol":"OMEGA_KV02_CHAT_ABBA_POSTHOC", "status":"STARTED",
            "model_sha256_expected":"74a4da8c9fdbcd15bd1f6d01d621410d31c6fc00986f5eb687824e7b93d7a9db",
            "llama_sha":"5a4afd80779ba51166b59986e61a0bfbb9e1a4c6",
            "chat_template":"Qwen2.5-Instruct standard framing", "order":base.ORDER,
            "sessions":[], "api_paid_calls":0,
            "source_trace":"six new synthetic one-digit additions with model chat framing plus one repeat"}
    try:
        for i,mode in enumerate(base.ORDER):
            report["sessions"].append({"index":i+1,"mode":mode,"rows":[]})
            base.one_session(mode,i+1,args,report)
        report["summary"]=base.summarize(report)
        report["status"]="COMPLETE"
    except Exception as e:
        report["status"]="INFRA_OR_HARNESS_FAILURE"
        report["error"]=repr(e)
        raise
    finally:
        args.output.write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n")
        print("STATUS",report["status"],flush=True)
        if "summary" in report: print("SUMMARY",json.dumps(report["summary"],ensure_ascii=False),flush=True)
if __name__=="__main__":main()
