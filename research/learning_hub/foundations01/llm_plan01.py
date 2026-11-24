"""LLM-PLAN01: real Qwen logits, bounded plan choices, frozen gold."""
import argparse,json,hashlib,random
from pathlib import Path

MODEL="Qwen/Qwen2.5-0.5B-Instruct"
OPTIONS={
"projection":"Ajuster un vecteur de façon minimale en norme euclidienne pour satisfaire des contraintes linéaires homogènes.",
"closure":"Vérifier, sur des observations et successeurs fournis, si deux observations identiques conduisent à des successeurs différents.",
"inverse":"Reconstruire des valeurs de moyenne nulle à partir de différences discrètes sur un cycle, sans modifier ces différences; signaler leur incompatibilité.",
"compose":"Corriger d'abord les différences discrètes d'un cycle en les projetant sur la somme nulle, puis reconstruire les valeurs de moyenne nulle.",
"unsupported":"Aucun des plans disponibles ne respecte la demande, ou les données nécessaires manquent; s'abstenir."}
CASES={
"projection":[
"Quel est le point le plus proche de mes coordonnées initiales dans le sous-espace homogène imposé ?",
"Conserver autant que possible le vecteur tout en rendant chaque contrainte linéaire exactement nulle.",
"Éliminer uniquement la partie parallèle à l'espace des lignes de la matrice.",
"Je veux que les produits avec les lignes valent zéro, avec une distance minimale au point de départ.",
"Pas d'intégration des écarts : effectuer seulement l'ajustement euclidien sous les équations homogènes.",
"Donner le meilleur approximant du vecteur appartenant au noyau de la matrice.",
"Les équations linéaires priment, et le changement de coordonnées doit être le plus petit possible.",
"Obtenir la composante tangentielle du vecteur en supprimant celle normale aux contraintes."],
"closure":[
"Ces relevés d'états permettent-ils de trouver deux présents indistinguables mais deux suites incompatibles ?",
"Un résumé identique conduit-il toujours au même prochain état observé dans les traces données ?",
"Relever une paire de mesures égales qui produit des sorties futures distinctes, si elle existe.",
"Décider uniquement sur cet échantillon si l'évolution des observations est cohérente avec une fonction.",
"Sans ajuster les coordonnées, examiner les observations présentes et les successeurs enregistrés.",
"Pour chaque paire d'états ayant la même mesure, vérifier si leurs transitions observées coïncident.",
"Montrer si une perte d'information empêche le déterminisme des transitions dans les relevés disponibles.",
"Les observations actuelles identiques ont-elles des lendemains différents dans ces données ?"],
"inverse":[
"Les écarts entre voisins du cercle sont imposés : retrouver les valeurs centrées ou signaler l'impossibilité.",
"Construire une suite de moyenne zéro sur un anneau dont les différences consécutives sont données.",
"Ne changer aucun incrément; restituer le potentiel discret périodique si compatible.",
"Déterminer le signal sur la boucle à partir de ses variations orientées, sans réparer les mesures.",
"Vérifier qu'une primitive de moyenne nulle existe sur ce cycle, puis la produire sans altérer les écarts.",
"Retrouver les hauteurs aux sommets d'un circuit fermé d'après les différences fournies.",
"Résoudre l'équation de différence cyclique avec moyenne de la solution fixée à zéro.",
"Calculer l'antécédent discret périodique des écarts, et non une correction de ceux-ci."],
"compose":[
"Rendre les écarts du cycle de somme nulle avec le plus petit changement, puis reconstruire les niveaux centrés.",
"Commencer par enlever la moyenne des variations sur l'anneau; terminer par leur primitive discrète.",
"Fournir les incréments corrigés au sens euclidien ainsi que les valeurs cycliques centrées qu'ils induisent.",
"Intégrer sur la boucle après avoir projeté les différences sur l'hyperplan de somme nulle.",
"Les variations ne ferment pas le cercle : réparer le défaut de somme avant de reconstruire le signal.",
"Ne pas se contenter de rendre la somme nulle : calculer ensuite l'antécédent périodique de moyenne zéro.",
"Produire d'abord les différences compatibles les plus proches, puis leur potentiel sur le cycle.",
"Soustraire la composante moyenne des incréments et, seulement après, résoudre l'équation de différence cyclique."],
"unsupported":[
"Trouver une primitive continue de la fonction exponentielle sur la droite réelle.",
"Calculer les valeurs propres et les vecteurs propres complexes de la matrice fournie.",
"Déterminer les futurs d'observations sans disposer d'aucune trace de transition.",
"Prouver que tous les fluides tridimensionnels restent réguliers pour tout temps.",
"Reconstruire d'abord une primitive sur le cycle, puis modifier ses incréments pour corriger leur somme.",
"Calculer une projection cartographique de la Terre vers un plan.",
"Exécuter simultanément les trois opérations, sans préciser de résultat attendu ni de dépendances.",
"Vérifier la fermeture de toute dynamique possible à partir de deux observations seulement."]}
def write(path,obj):
    Path(path).write_text(json.dumps(obj,ensure_ascii=False,indent=2,default=str))
def freeze(out):
    from toolroute01 import TRAIN,HOLDOUT,payload
    from semantic_ir01_benchmark import CASES as OLD
    from huggingface_hub import HfApi
    old=set(sum(TRAIN.values(),[])+sum(HOLDOUT.values(),[])+sum(OLD.values(),[]))
    assert len(set(sum(CASES.values(),[])))==40 and not old.intersection(sum(CASES.values(),[]))
    rng=random.Random(20261126);rows=[];gold=[]
    for route,seq in CASES.items():
        for s in seq:
            i=len(rows);order=list(OPTIONS);rng.shuffle(order);order2=order[1:]+order[:1]
            rows.append(dict(id=i,text=s,orders=[order,order2]))
            gold.append(dict(id=i,route=route,payloads=[payload(rng,i*2+j) for j in range(2)]))
    # Mix order, IDs remain stable, no class labels in question artifact.
    rng.shuffle(rows)
    revision=HfApi().model_info(MODEL).sha
    assert isinstance(revision,str) and len(revision)==40
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    write(out/"questions.json",rows);write(out/"gold.json",gold)
    write(out/"pin.json",dict(model=MODEL,revision=revision,questions_sha256=hashlib.sha256((out/"questions.json").read_bytes()).hexdigest()))
    print("MODEL_PIN",revision,flush=True)
def infer(q,pin,out):
    import torch
    from transformers import AutoModelForCausalLM,AutoTokenizer
    torch.set_num_threads(2);torch.manual_seed(0)
    raw=Path(q).read_bytes();p=json.loads(Path(pin).read_text())
    assert hashlib.sha256(raw).hexdigest()==p["questions_sha256"] and p["model"]==MODEL
    questions=json.loads(raw)
    tok=AutoTokenizer.from_pretrained(MODEL,revision=p["revision"],trust_remote_code=False)
    tok.padding_side="left"
    model=AutoModelForCausalLM.from_pretrained(MODEL,revision=p["revision"],torch_dtype=torch.float32,trust_remote_code=False).eval()
    letters=list("ABCDE");ids=[tok.encode(x,add_special_tokens=False) for x in letters]
    assert all(len(x)==1 for x in ids) and len({x[0] for x in ids})==5
    ids=[x[0] for x in ids];requests=[]
    for row in questions:
        for idx,order in enumerate(row["orders"]):
            options="\n".join(a+". "+OPTIONS[b] for a,b in zip(letters,order))
            content="Choisis exactement le plan qui répond à toute la demande. Respecte les interdictions et l'ordre des opérations. Si aucun plan ne convient, choisis l'abstention. Réponds par une seule lettre A, B, C, D ou E.\n"+options+"\nDemande : "+row["text"]
            prompt=tok.apply_chat_template([{"role":"system","content":"Tu es un assistant de planification mathématique."},{"role":"user","content":content}],tokenize=False,add_generation_prompt=True)
            requests.append((row["id"],idx,order,prompt))
    predictions=[]
    for i in range(0,len(requests),4):
        batch=requests[i:i+4];inputs=tok([x[3] for x in batch],return_tensors="pt",padding=True,add_special_tokens=False)
        with torch.inference_mode():
            logits=model(**inputs,use_cache=False,logits_to_keep=1).logits[:,-1,:]
        for j,(qid,idx,order,_) in enumerate(batch):
            l=logits[j];scores=l[ids].tolist();winner=max(range(5),key=lambda k:scores[k])
            predictions.append(dict(id=qid,order_index=idx,route=order[winner],letters=letters,order=order,logits=scores,top_token=tok.decode([int(l.argmax())]),tokens=int(inputs["attention_mask"][j].sum())))
        print("LLM_PLAN_PROGRESS",len(predictions),flush=True)
    write(out,dict(pin=p,parameters=sum(x.numel() for x in model.parameters()),predictions=predictions))
def score(q,g,pred,out):
    from collections import Counter
    from toolroute01 import fit,learned,keyword,dispatch,verify
    from semantic_ir01 import solve,guard,PLANS,abstain
    questions={r["id"]:r for r in json.loads(Path(q).read_text())}
    gold=json.loads(Path(g).read_text());raw=json.loads(Path(pred).read_text())
    assert raw["pin"]["questions_sha256"]==hashlib.sha256(Path(q).read_bytes()).hexdigest()
    by={}
    for r in raw["predictions"]:
        assert (r["id"],r["order_index"]) not in by
        order=questions[r["id"]]["orders"][r["order_index"]]
        assert r["order"]==order and r["route"]==order[max(range(5),key=lambda i:r["logits"][i])]
        by[r["id"],r["order_index"]]=r["route"]
    assert len(by)==80
    model=fit();stats={a:Counter() for a in ["single","agreement","ir","nb","keyword","oracle"]};per={a:{c:Counter() for c in OPTIONS} for a in stats};records=[]
    plans={route:dict(domain=domain,goals=steps.copy(),steps=steps.copy(),forbidden=[],reason=None) for domain,(steps,route) in PLANS.items()}
    plans["unsupported"]=abstain("NO_MATCH_OR_DISAGREEMENT")
    for row in gold:
        i=row["id"];label=row["route"];text=questions[i]["text"];a,b=by[i,0],by[i,1]
        for p in row["payloads"]:
            _,ir_route,ir_out=solve(text,p)
            routes={"single":a,"agreement":a if a==b else "unsupported","ir":ir_route,"nb":learned(text,model),"keyword":keyword(text),"oracle":label}
            for arm,r in routes.items():
                plan=plans[r];r=guard(plan)
                output=dispatch(r,p);correct=r==label and verify(label,p,output)
                for s in (stats[arm],per[arm][label]):
                    s["n"]+=1;s["exact"]+=int(correct);s["false_dispatch"]+=int(label=="unsupported" and r!="unsupported");s["supported_abstain"]+=int(label!="unsupported" and r=="unsupported")
                records.append(dict(id=i,label=label,arm=arm,route=r,plan=plan,output=output,exact=correct))
    assert stats["oracle"]["exact"]==80
    a=stats["agreement"]
    passed=a["exact"]>=72 and per["agreement"]["compose"]["exact"]>=14 and a["false_dispatch"]==0 and a["exact"]>=stats["ir"]["exact"]+4
    result=dict(pin=raw["pin"],parameters=raw["parameters"],agreement_questions=sum(by[i,0]==by[i,1] for i in questions),totals=stats,per_class=per,primary_pass=passed,records=records)
    write(out,result);print("LLM_PLAN_RESULT",json.dumps({k:v for k,v in result.items() if k!="records"}),flush=True)
if __name__=="__main__":
    a=argparse.ArgumentParser();a.add_argument("mode",choices=["freeze","infer","score"]);a.add_argument("--out",required=True);a.add_argument("--questions");a.add_argument("--pin");a.add_argument("--gold");a.add_argument("--pred");r=a.parse_args()
    if r.mode=="freeze":freeze(r.out)
    elif r.mode=="infer":infer(r.questions,r.pin,r.out)
    else:score(r.questions,r.gold,r.pred,r.out)
