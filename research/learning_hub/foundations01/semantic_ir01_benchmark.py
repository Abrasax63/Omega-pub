"""Fresh template test, frozen semantic_ir01 imported unmodified."""
import json,random
from collections import Counter
from pathlib import Path
from toolroute01 import TRAIN,HOLDOUT,CLASSES,fit,learned,keyword,payload,dispatch,verify
from semantic_ir01 import solve,guard

CASES={
"projection":[
"Ramener le point initial dans le sous-espace défini par les équations, avec le déplacement le plus court.",
"Trouver le meilleur ajustement euclidien du vecteur aux contraintes.",
"Les lignes fournies doivent toutes être orthogonales au résultat, qui doit rester au plus près de l'entrée.",
"Annuler le résidu de la matrice avec une correction de norme minimale.",
"Ne pas calculer de primitive, mais projeter les coordonnées sur le noyau.",
"Obtenir le point admissible le moins éloigné selon la norme usuelle.",
"Sans intégration, fournir une correction orthogonale du vecteur.",
"Réduire à zéro les produits scalaires avec chacune des lignes par le plus petit déplacement.",
"Quelle est la composante du vecteur dans l'espace nul de la matrice ?",
"Les contraintes linéaires sont impératives ; minimiser la distance au vecteur original.",
"Corriger les coordonnées, pas les incréments d'un cycle.",
"Enlever la partie normale aux lignes sans modifier les composantes tangentielles."
],
"closure":[
"Les états donnant la même mesure ont-ils nécessairement le même successeur ?",
"Existe-t-il une paire de traces avec un présent identique mais une suite différente ?",
"Contrôler la fermeture des transitions sur les observations disponibles.",
"Un même résumé peut-il annoncer deux évolutions distinctes dans ces relevés ?",
"Sans corriger les coordonnées, chercher une collision entre observations aux futurs incompatibles.",
"Les mesures sont-elles suffisantes pour prédire la prochaine sortie sur cet échantillon ?",
"Comparer les suites des états indiscernables et signaler une différence.",
"Vérifier si la transition observée est une fonction de la mesure actuelle.",
"Deux descriptions identiques mais deux lendemains distincts réfutent-ils la fermeture ici ?",
"Chercher un témoin de non-déterminisme des observations et de leurs successeurs.",
"Ne pas projeter le vecteur, mais comparer les traces et les transitions.",
"Les relevés identiques d'aujourd'hui sont-ils associés à des valeurs différentes demain ?"
],
"inverse":[
"Calculer les niveaux sur un anneau sachant les variations successives, avec moyenne zéro.",
"Retrouver une primitive discrète des différences cycliques.",
"Construire un signal de somme nulle sur le cercle avec les écarts donnés.",
"Résoudre le problème inverse des incréments périodiques sans les modifier.",
"Sans correction des données, calculer leur primitive cyclique.",
"Déterminer les valeurs centrées dont les différences sur la boucle sont celles fournies.",
"Est-il possible de reconstruire un potentiel périodique à partir de ces écarts ?",
"Intégrer les variations sur un anneau, en signalant toute incompatibilité.",
"Retrouver les hauteurs sur un circuit fermé à partir des différences.",
"Fournir un antécédent de moyenne nulle pour les incréments circulaires.",
"Ne pas projeter, mais inverser la différence périodique.",
"Calculer une suite cyclique centrée dont les variations sont imposées."
],
"compose":[
"Soustraire la moyenne des incréments puis retrouver une primitive périodique.",
"Corriger les variations pour que leur somme soit nulle, ensuite reconstruire le signal sur la boucle.",
"Donner les écarts les plus proches de somme zéro puis leur antécédent circulaire.",
"Après avoir annulé la moyenne des différences, intégrer sur le cycle.",
"Projeter les incréments sur les contraintes de somme nulle puis calculer les niveaux périodiques.",
"Réparer les écarts pour les rendre compatibles avant de reconstruire le potentiel cyclique.",
"D'abord enlever la moyenne, ensuite inverser la différence circulaire.",
"Les variations sur l'anneau sont incompatibles : les ajuster au minimum puis retrouver les valeurs centrées.",
"Calculer les deux résultats : correction de somme zéro puis primitive sur la boucle.",
"Reconstruire le signal périodique après avoir retiré la moyenne des incréments.",
"Il faut rendre la somme nulle par correction orthogonale avant d'intégrer les variations cycliques.",
"Rendre les différences intégrables sur le cercle, puis restituer les niveaux."
],
"unsupported":[
"Calculer une primitive analytique de cosinus sur la droite réelle.",
"Projeter les coordonnées sur une carte géographique.",
"Certifier la fermeture universelle de toutes les dynamiques.",
"Inverser les différences périodiques puis corriger la moyenne des incréments pour les rendre compatibles.",
"Effectuer simultanément une projection et une recherche de collision de traces, sans ordre imposé.",
"Déduire le futur de chaque observation sans les états ni les transitions.",
"Résoudre un problème de Navier Stokes avec le vecteur fourni.",
"Calculer les valeurs propres d'une matrice complexe.",
"Trouver la primitive périodique et la correction de somme nulle, sans préciser laquelle faire d'abord.",
"Ne pas utiliser la projection ni la primitive ; obtenir tout de même le potentiel cyclique.",
"Estimer les variations de température sur un cycle annuel.",
"Calculer le déterminant des lignes de la matrice."
]}
def mutation_checks():
    good=dict(domain="cyclic_zero_sum",goals=["projection","inverse"],forbidden=[],steps=["projection","inverse"],reason=None)
    assert guard(good)=="compose"
    variants=[dict(good,steps=["inverse","projection"]),dict(good,forbidden=["projection"]),dict(good,domain="finite_cycle"),dict(good,steps=["unknown"]),dict(good,reason="AMBIGUOUS"),dict(good,goals=["inverse"]),dict(good,domain="unknown"),dict(good,extra=True)]
    checks=[]
    for v in variants:
        try:guard(v);checks.append(False)
        except ValueError:checks.append(True)
    return checks
def main(path):
    old=set(sum(TRAIN.values(),[])+sum(HOLDOUT.values(),[]))
    alltext=sum(CASES.values(),[])
    assert len(set(alltext))==60 and not old.intersection(alltext)
    assert all(len(v)==12 for v in CASES.values())
    rng=random.Random(20261125);model=fit();records=[]
    stats={a:{c:Counter() for c in CLASSES} for a in ("ir","learned","keyword","oracle")}
    for c in CLASSES:
        for j,s in enumerate(CASES[c]):
            for i in range(2):
                p=payload(rng,2*j+i)
                ir,route,out=solve(s,p)
                arms=[("ir",route,out,ir)]
                for a,r in [("learned",learned(s,model)),("keyword",keyword(s)),("oracle",c)]:
                    arms.append((a,r,dispatch(r,p),None))
                for a,r,out,plan in arms:
                    ok=r==c and verify(c,p,out)
                    st=stats[a][c];st["n"]+=1;st["exact"]+=int(ok)
                    st["false_dispatch"]+=int(c=="unsupported" and r!="unsupported")
                    st["supported_abstain"]+=int(c!="unsupported" and r=="unsupported")
                    records.append(dict(arm=a,label=c,template=j,instance=i,text=s,payload=p,route=r,plan=plan,output=out,exact=ok))
    totals={a:dict(sum(v.values(),Counter())) for a,v in stats.items()}
    checks=mutation_checks()
    assert totals["oracle"]["exact"]==120
    primary=totals["ir"]["exact"]>=108 and stats["ir"]["compose"]["exact"]>=22 and totals["ir"]["false_dispatch"]==0 and totals["ir"]["exact"]>=max(totals["learned"]["exact"],totals["keyword"]["exact"])+6 and all(checks)
    result=dict(totals=totals,per_class=stats,guard_checks=checks,primary_pass=primary,records=records)
    Path(path).write_text(json.dumps(result,ensure_ascii=False,indent=2,default=str))
    print("SEMANTIC_IR_RESULT",json.dumps({k:v for k,v in result.items() if k!="records"}),flush=True)
    print("IR_ERRORS",json.dumps([dict(label=r["label"],text=r["text"],route=r["route"],plan=r["plan"]) for r in records if r["arm"]=="ir" and not r["exact"] and r["instance"]==0],ensure_ascii=False),flush=True)
if __name__=="__main__":
    import sys
    main(sys.argv[1])
