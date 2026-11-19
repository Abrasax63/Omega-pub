#!/usr/bin/env python3
import argparse, hashlib, json, time, urllib.request

CASES = [
  ("s1", "Si n est pair.", "Alors n+2 est pair."),
  ("s2", "Si un graphe est un arbre.", "Alors il a exactement |V|-1 arêtes."),
  ("m1", "Hypothèse: T est une permutation finie.", "Conclusion: chaque orbite de T est périodique."),
  ("m2", "Hypothèse: A est une matrice triangulaire.", "Conclusion: les valeurs propres sont les éléments diagonaux."),
]

def invalid(case_id, premise, conclusion):
    claim={"claim_id":"c1","packet_id":case_id,"evidence":[
      {"role":"premise","packet_id":case_id,"line":1,"literal":premise},
      {"role":"conclusion","packet_id":case_id,"line":2,"literal":conclusion}]}
    body=json.dumps({"source_blob":case_id,"claims":[claim]},ensure_ascii=False)
    return body.replace('{"source_blob":', '{"source_blob":"wrong","source_blob":',1)

def unique_loads(text):
    def hook(pairs):
        out={}
        for k,v in pairs:
            if k in out: raise ValueError("duplicate key")
            out[k]=v
        return out
    return json.loads(text,object_pairs_hook=hook)

def oracle(obj, case_id, premise, conclusion):
    if set(obj) != {"source_blob","claims"} or obj["source_blob"] != case_id: return False
    if not isinstance(obj["claims"],list) or len(obj["claims"]) != 1: return False
    c=obj["claims"][0]
    if set(c) != {"claim_id","packet_id","evidence"} or c["packet_id"] != case_id: return False
    want=[("premise",premise,1),("conclusion",conclusion,2)]
    if not isinstance(c["evidence"],list) or len(c["evidence"]) != 2: return False
    for e,(role,literal,line) in zip(c["evidence"],want):
        if set(e) != {"role","packet_id","line","literal"}: return False
        if (e["role"],e["literal"],e["line"],e["packet_id"]) != (role,literal,line,case_id): return False
    return True

def request(endpoint, prompt):
    payload={"model":"qwen-local","messages":[{"role":"user","content":prompt}],
             "temperature":0,"seed":3801,"max_tokens":180,"response_format":{"type":"json_object"}}
    req=urllib.request.Request(endpoint+"/v1/chat/completions",data=json.dumps(payload).encode(),
                               headers={"Content-Type":"application/json"},method="POST")
    start=time.perf_counter()
    with urllib.request.urlopen(req,timeout=90) as r: data=json.load(r)
    return data["choices"][0]["message"]["content"],data.get("usage",{}),(time.perf_counter()-start)*1000

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--endpoint",default="http://127.0.0.1:18738")
    ap.add_argument("--arm",choices=("baseline","candidate"),required=True); ap.add_argument("--output",required=True)
    a=ap.parse_args(); rows=[]
    # Negative oracle control is fixed and must fail.
    bad={"source_blob":"s1","claims":[{"claim_id":"c1","packet_id":"s1","evidence":[
        {"role":"premise","packet_id":"s1","line":1,"literal":CASES[0][1]},
        {"role":"conclusion","packet_id":"s1","line":2,"literal":"fragment inventé"}]}]}
    assert not oracle(bad,"s1",CASES[0][1],CASES[0][2])
    for case_id,premise,conclusion in CASES:
        broken=invalid(case_id,premise,conclusion)
        diagnosis=("Diagnostic exact: duplicate key: source_blob. Garde une seule occurrence correcte. "
                   if a.arm=="candidate" else
                   "Relance neutre: la réponse précédente a été refusée. Réessaie sans autre indice. ")
        prompt=("Réécris uniquement l'objet JSON valide, sans markdown ni commentaire. "+diagnosis+
                "Ne change aucune autre valeur et n'invente aucune citation. Réponse refusée: "+broken)
        raw,usage,ms=request(a.endpoint,prompt)
        parsed=None; exact=False; error=None
        try: parsed=unique_loads(raw); exact=oracle(parsed,case_id,premise,conclusion)
        except Exception as e: error=type(e).__name__+":"+str(e)
        rows.append({"case":case_id,"arm":a.arm,"exact":exact,"parse_error":error,
                     "prompt_tokens":usage.get("prompt_tokens"),"completion_tokens":usage.get("completion_tokens"),
                     "elapsed_ms":round(ms,2),"raw_sha256":hashlib.sha256(raw.encode()).hexdigest()})
    with open(a.output,"x",encoding="utf-8") as f: json.dump(rows,f,ensure_ascii=False,indent=2); f.write("\n")

if __name__=="__main__": main()
