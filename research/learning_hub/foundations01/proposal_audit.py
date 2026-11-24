"""Post-run independent audit of PROPOSAL-01; no model or original grader imports."""
import argparse
from collections import Counter
from hashlib import sha256
from itertools import permutations
import json
from pathlib import Path

PROMPT = ('Invent a binary relation on 3 to 4 named nodes and a triple to inspect. '
          'Return only JSON with nodes, edges, triple. Edges are pairs of node names. '
          'Do not include answers.')
MODEL="HuggingFaceTB/SmolLM2-135M-Instruct"
REV="ee72e5415c002e8fc0566a191a07c0b2b708875a"

def require(condition, message):
    if not condition:
        raise ValueError(message)

def digest(s):
    return sha256(s.encode("utf-8")).hexdigest()

def decode(raw):
    require(isinstance(raw,str) and len(raw)<=4096,"SIZE")
    p=json.loads(raw)
    require(type(p) is dict and set(p)=={"nodes","edges","triple"},"PACKET")
    n,e,t=p["nodes"],p["edges"],p["triple"]
    require(type(n) is list and len(n) in (3,4) and
            all(type(x) is str and 0<len(x)<=64 for x in n) and len(set(n))==len(n),"NODES")
    require(type(e) is list and len(e)<=len(n)**2 and
            all(type(a) is list and len(a)==2 and all(type(x) is str and x in n for x in a) for a in e),"EDGES")
    require(len({tuple(a) for a in e})==len(e),"DUPLICATE_EDGE")
    require(type(t) is list and len(t)==3 and all(type(x) is str and x in n for x in t),"TRIPLE")
    return p

def independent_key(p):
    # Lexicographic adjacency string, independent of original integer mask.
    n,e,t=p["nodes"],p["edges"],p["triple"]
    variants=[]
    for order in permutations(n):
        a="".join("1" if [x,y] in e else "0" for x in order for y in order)
        variants.append((a,tuple(order.index(x) for x in t)))
    graph, triple=min(variants)
    return (len(n),graph),(len(n),graph,triple)

def audit(raw_bytes, report):
    require(sha256(raw_bytes).hexdigest()==report["raw_file_sha256"],"RAW_FILE_DIGEST")
    rows=[json.loads(s) for s in raw_bytes.decode("utf-8").splitlines()]
    require(len(rows)==32 and report["attempts"]==32,"ATTEMPTS")
    require(report["model"]==MODEL and report["revision"]==REV,"MODEL_IDENTITY")
    seen,graphs,expected,reject=set(),set(),{},set()
    motifs=Counter({f"{i:03b}":0 for i in range(8)})
    for i,r in enumerate(rows):
        require(r["seed"]==20261124+i,"SEED")
        require(digest(r["raw"])==r["raw_sha256"] and digest(PROMPT)==r["prompt_sha256"],"ROW_HASH")
        require(type(r["output_tokens"]) is int and 0<=r["output_tokens"]<=192 and
                len(r["output_token_ids"])==r["output_tokens"] and
                all(type(t) is int and t>=0 for t in r["output_token_ids"]),"TOKENS")
        require(type(r["input_tokens"]) is int and r["input_tokens"]>0,"INPUT_TOKENS")
        try:
            p=decode(r["raw"])
        except (ValueError,TypeError,KeyError):
            reject.add(i)
            continue
        g,k=independent_key(p)
        if k in seen:
            reject.add(i)
            continue
        seen.add(k)
        graphs.add(g)
        x,y,z=p["triple"]
        bits=[edge in p["edges"] for edge in ([x,y],[y,z],[x,z])]
        motif="".join(str(int(b)) for b in bits)
        motifs[motif]+=1
        canonical=json.dumps(p,sort_keys=True,separators=(",",":"),ensure_ascii=False)
        expected[i]={"target":dict(zip(("xy","yz","xz","violates"),[*bits,motif=="110"])),
                     "prompt":"Read the relation and return JSON with xy,yz,xz and violates. "+canonical,
                     "input_sha256":digest(canonical)}
    accepted=report["accepted"]
    rejected=report["rejected"]
    require(len(accepted)==len(expected) and {r["proposal_index"] for r in accepted}==set(expected),"ACCEPTED_INDEX")
    require(len(rejected)==len(reject) and {r["index"] for r in rejected}==reject,"REJECTED_INDEX")
    require(dict(Counter(r["reason"] for r in rejected))==report["rejection_counts"],"REJECTION_COUNTS")
    for a in accepted:
        e=expected[a["proposal_index"]]
        target=json.loads(a["target"])
        require(type(target) is dict and all(type(v) is bool for v in target.values()) and target==e["target"],"TARGET")
        require(a["prompt"]==e["prompt"] and a["input_sha256"]==e["input_sha256"],"PROVENANCE")
        require(a["model_generated"] is True and a["provenance"]=="MODEL_PROPOSAL_EXACT_TEACHER_LABEL","PROVENANCE_LABEL")
    require(report["accepted_unique"]==len(expected) and report["unique_graphs"]==len(graphs)
            and report["motifs"]==dict(motifs),"SCORES")
    require(report["input_tokens"]==sum(r["input_tokens"] for r in rows)
            and report["output_tokens"]==sum(r["output_tokens"] for r in rows),"TOTAL_TOKENS")
    positive=len(expected)>=16 and sum(v>0 for v in motifs.values())>=4 and motifs["110"]>=4
    status="EXPLORATORY_PROPOSAL_FEASIBILITY_SIGNAL" if positive else "PROPOSAL_FEASIBILITY_NOT_DEMONSTRATED"
    require(report["status"]==status and report["training_authorized"] is False and report["weight_updates"]==0
            and report["holdout_accessed"] is False,"VERDICT")
    return {"audit":"INDEPENDENT_REPORT_CONSISTENCY_PASSED","verdict":status,
            "accepted":len(expected),"graphs":len(graphs),"motifs":dict(motifs),
            "limitation":"Archive consistency only; not independent authentication of model execution or token decoding.",
            "training_authorized":False}

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("directory",type=Path)
    a=p.parse_args()
    print(json.dumps(audit((a.directory/"raw.jsonl").read_bytes(),
                           json.loads((a.directory/"report.json").read_text())),indent=2))
