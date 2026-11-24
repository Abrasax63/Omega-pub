"""Bounded text-to-tool routing: supervised lexical learner, exact execution."""
import json,math,random,re
from collections import Counter
from fractions import Fraction as F
from pathlib import Path
from structure_contracts import execute

CLASSES=("projection","closure","inverse","compose","unsupported")
TRAIN={
"projection":[
"Projeter le vecteur sur le noyau des contraintes",
"Calculer la correction orthogonale minimale",
"Trouver le vecteur admissible le plus proche",
"Supprimer la composante normale aux contraintes",
"Imposer les équations linéaires par projection",
"Rendre le vecteur orthogonal aux lignes",
"Minimiser la distance euclidienne sous contraintes",
"Corriger les coordonnées pour satisfaire la matrice"],
"closure":[
"Détecter un conflit entre observations identiques et futurs différents",
"Auditer la fermeture de la dynamique observée",
"Chercher un contre exemple de déterminisme observable",
"Vérifier si les mêmes observations donnent des successeurs distincts",
"Repérer une perte information dans les traces",
"Comparer les évolutions des états indistinguables",
"Trouver deux états observés identiques aux sorties incompatibles",
"Tester la cohérence des observations et des futurs"],
"inverse":[
"Trouver la primitive périodique de moyenne nulle",
"Inverser les différences sur un cycle",
"Reconstruire les valeurs circulaires à partir des incréments",
"Résoudre la récurrence périodique avec jauge moyenne",
"Vérifier la compatibilité des incréments puis intégrer",
"Calculer une antiderivée discrète sur un cercle",
"Déterminer les valeurs dont les différences successives sont données",
"Intégrer les écarts sur la boucle ou signaler une obstruction"],
"compose":[
"Projeter les incréments sur la somme nulle puis reconstruire la primitive",
"Corriger le vecteur avant inversion périodique",
"Enchaîner correction orthogonale et intégration cyclique",
"Retirer la moyenne des différences puis intégrer sur le cycle",
"Rendre les incréments compatibles puis reconstruire les valeurs",
"Composer projection et primitive périodique",
"Réparer les écarts par projection avant de résoudre le cycle",
"Deux étapes : correction de somme puis inverse circulaire"],
"unsupported":[
"Prédire la météo de demain",
"Résoudre une équation différentielle non fournie",
"Calculer le déterminant symbolique général",
"Identifier une photographie",
"Trouver une preuve universelle sans données",
"Déterminer une intégrale impropre analytique",
"Simuler la turbulence tridimensionnelle",
"Traduire une phrase en anglais"]}
HOLDOUT={
"projection":[
"Quelle modification de moindre norme annule les produits avec les lignes ?",
"Approcher les données au sens euclidien dans le sous espace admissible",
"Restituer les coordonnées les plus proches qui respectent les contraintes",
"Éliminer la partie du vecteur portée par les lignes de la matrice",
"Sans primitive périodique, effectuer seulement la correction orthogonale",
"Trouver le point du noyau le plus près des coordonnées initiales",
"On souhaite annuler chaque produit scalaire par un ajustement minimal",
"Réparer les données pour obtenir un résidu linéaire nul, sans intégrer"],
"closure":[
"Une observation suffit elle à déterminer le lendemain de chaque état ?",
"Exhiber deux traces indiscernables au présent mais divergentes ensuite",
"Les mesures égales imposent elles une sortie commune ?",
"Rechercher une collision de mesures accompagnée de successeurs incompatibles",
"Sans projeter le vecteur, auditer les futurs pour une observation commune",
"Fournir un témoin que la représentation réduite ne ferme pas la dynamique",
"Comparer tous les états qui ont la même description et leurs évolutions",
"Signaler toute contradiction entre observations égales et transitions"],
"inverse":[
"Retrouver un signal centré à partir de ses écarts circulaires",
"Calculer les hauteurs sur la boucle dont on connaît les variations",
"Obtenir un antécédent de moyenne zéro pour la différence cyclique",
"Les incréments permettent ils un potentiel périodique ?",
"Sans correction du vecteur, tenter seulement la primitive des écarts",
"Reconstruire les niveaux avec les variations imposées sur un anneau",
"Résoudre la différence finie sur un cycle sans changer les données",
"Déduire les valeurs de la série fermée, ou donner le défaut de somme"],
"compose":[
"Ajuster au minimum les variations puis retrouver le signal circulaire",
"Ôter la composante moyenne et calculer les niveaux de la boucle",
"Réparer les données incompatibles avant de reconstruire le potentiel",
"Trouver une primitive après avoir rendu la somme des écarts nulle",
"Ne pas se limiter à la projection : restituer ensuite les valeurs cycliques",
"Corriger orthogonalement les incréments et inverser la différence",
"Rendre la série de variations intégrable puis produire le signal centré",
"Fournir les coordonnées corrigées ainsi que leur antécédent périodique"],
"unsupported":[
"Certifier la régularité globale de Navier Stokes",
"Calculer la primitive analytique de sin x sur la droite réelle",
"Déduire une observation manquante sans les états ni les futurs",
"Projeter une carte géographique sur une sphère",
"Déterminer la température de demain avec ces coordonnées",
"Prouver la fermeture universelle de toute dynamique à partir de deux traces",
"Calculer les valeurs propres complexes de la matrice",
"Inverser la transformée de Laplace d'une fonction continue"]}
KEYS={
"projection":"projeter projection orthogonale noyau contraintes euclidien matrice scalaire",
"closure":"observation observations futurs successeurs fermeture traces états dynamique",
"inverse":"primitive périodique cycle différences incréments boucle antécédent",
"compose":"puis ensuite avant enchaîner composer corrigées correction réparer",
"unsupported":"météo photographie anglais turbulence analytique universelle complexes laplace"}
def tokens(s):return re.findall(r"[^\W\d_]+",s.lower(),flags=re.UNICODE)
def fit():
    counts={c:Counter(w for s in TRAIN[c] for w in tokens(s)) for c in CLASSES}
    vocab=set().union(*(set(v) for v in counts.values()))
    return counts,vocab
def learned(s,model):
    counts,vocab=model
    score={c:sum(math.log((counts[c][w]+1)/(sum(counts[c].values())+len(vocab))) for w in tokens(s) if w in vocab) for c in CLASSES}
    ranked=sorted(CLASSES,key=lambda c:score[c],reverse=True)
    return ranked[0] if score[ranked[0]]>score[ranked[1]] else "unsupported"
def keyword(s):
    words=set(tokens(s));scores={c:len(words&set(KEYS[c].split())) for c in CLASSES}
    best=max(scores.values());winners=[c for c in CLASSES if scores[c]==best]
    return winners[0] if best and len(winners)==1 else "unsupported"
def payload(rng,i):
    n=rng.randint(3,8);v=[rng.randint(-5,5) for _ in range(n)]
    if i%3==0:v[-1]=-sum(v[:-1])
    scale=rng.choice([-3,-1,1,2,4]);rows=[[scale]*n]
    obs=[rng.randrange(3) for _ in range(6)]
    samples=[(j,o,(o+1)%3) for j,o in enumerate(obs)]
    if i%2==0:samples[-1]=(5,obs[0],(obs[0]+2)%3)
    return dict(vector=v,rows=rows,samples=samples)
def dispatch(route,p):
    if route=="unsupported":return {"status":"ABSTAIN"}
    if route=="projection":return execute("kernel_projection",p["rows"],p["vector"])
    if route=="closure":return execute("closure_audit",p["samples"])
    if route=="inverse":return execute("periodic_primitive",p["vector"])
    if route=="compose":
        u=execute("kernel_projection",p["rows"],p["vector"])
        return {"corrected":u,"inverse":execute("periodic_primitive",u)}
    raise ValueError("INVALID_ROUTE")
def gold_projection(p):
    v=p["vector"];row=p["rows"][0]
    k=F(sum(a*b for a,b in zip(v,row)),sum(b*b for b in row))
    return tuple(F(a)-k*b for a,b in zip(v,row))
def gold_inverse(v):
    v=tuple(map(F,v))
    if sum(v):return dict(status="INCOMPATIBLE",obstruction=sum(v))
    n=len(v);g=[-sum(v[i:]) for i in range(n)];avg=sum(g)/n
    return dict(status="SOLVED",primitive=tuple(x-avg for x in g))
def verify(label,p,out):
    if label=="unsupported":return out=={"status":"ABSTAIN"}
    if label=="projection":return out==gold_projection(p)
    if label=="inverse":return out==gold_inverse(p["vector"])
    if label=="compose":
        u=gold_projection(p)
        return out=={"corrected":u,"inverse":gold_inverse(u)}
    samples=p["samples"]
    bad={frozenset((a[0],b[0])) for a in samples for b in samples if a[1]==b[1] and a[2]!=b[2]}
    if bad:return out.get("status")=="REFUTED" and frozenset(out.get("witness",())) in bad
    return out.get("status")=="CONSISTENT_ON_SAMPLES"
def main(path):
    assert all(len(TRAIN[c])==len(HOLDOUT[c])==8 for c in CLASSES)
    assert not set(sum(TRAIN.values(),[]))&set(sum(HOLDOUT.values(),[]))
    model=fit();rng=random.Random(20261124);records=[]
    stats={a:{c:Counter() for c in CLASSES} for a in ("learned","keyword","oracle")}
    for c in CLASSES:
        for j,s in enumerate(HOLDOUT[c]):
            for i in range(3):
                p=payload(rng,i+j*3)
                for arm,route in [("learned",learned(s,model)),("keyword",keyword(s)),("oracle",c)]:
                    out=dispatch(route,p)
                    correct=route==c and verify(c,p,out)
                    t=stats[arm][c];t["n"]+=1;t["route_correct"]+=int(route==c);t["exact"]+=int(correct);t["false_dispatch"]+=int(c=="unsupported" and route!="unsupported")
                    records.append(dict(arm=arm,label=c,template=j,instance=i,text=s,payload=p,route=route,output=out,exact=correct))
    totals={a:dict(sum((v for v in by.values()),Counter())) for a,by in stats.items()}
    l=totals["learned"];k=totals["keyword"]
    assert totals["oracle"]["exact"]==120
    primary=l["exact"]>=108 and stats["learned"]["compose"]["exact"]>=22 and l["false_dispatch"]==0
    promote=primary and l["exact"]-k["exact"]>=6
    result=dict(training_templates=40,holdout_templates=40,totals=totals,per_class=stats,primary_pass=primary,promote=promote,records=records)
    Path(path).write_text(json.dumps(result,ensure_ascii=False,indent=2,default=str))
    print("TOOLROUTE_RESULT",json.dumps({k:v for k,v in result.items() if k!="records"}),flush=True)
if __name__=="__main__":
    import sys
    main(sys.argv[1])
