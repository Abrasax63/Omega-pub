# Théorie opérationnelle des transformations et de l'autonomie
**Version 0.2 — 12 octobre 2026.**

Le noyau initial est conservé ; les précisions et restrictions de l’audit 0.2 en fin de document font autorité.

## Résultat et portée
Un noyau cohérent relie états dérivés, mémoire prédictive, fermeture, futurs fantômes et coûts de réalisation. Il ne constitue pas une théorie fondamentale de la matière. La composition, les tests et leur valuation restent primitifs ; les états sont ensuite reconstruits.

Statuts : DÉFINITION ; PREUVE dans le domaine indiqué ; CALCUL EXACT exécuté ; CONNU dans la littérature ; HYPOTHÈSE ; INDÉTERMINÉ. Aucune nouveauté ou validation par une personne indépendante n'est certifiée.

## Corpus
Les échanges retrouvés couvrent objets invariants de juin–juillet, équivalence d'histoires Ω-50–51 du 21 juillet, composition et temps d'août, quotients du 19 août, événements asynchrones du 21 août, fermeture et contrôle de septembre, puis mémoire quantique et réalisation relative.

Documents lus : QUANTIQUE_SWAP_MEMOIRE_RELATIVE_2026-09-29.md (version 1) ; audit_empirique_memoire_multitemps_2026-09-30.md ; DELTA_H_COUT_RELATIF_RELAIS_2026-09-29.md ; DELTA_H_INTERFACES_CONTROLEES_REPARABILITE_2026-09-29.md ; DELTA_H_AUDIT_QUANTIQUE_PROBABILISTE_2026-09-29.md ; astra_fermeture_2026-10-02.md ; astra_fermeture_ordre_variable_2026-10-02.md ; fermeture_robustesse_2026-10-02.md ; omega_chapitre_3_fermeture_enrichie.md ; omega_chapitre_10_quantaloide_budgetaire.md ; état courant et premières itérations de OMEGA_W03_EMERGENCE_OPERATIONNELLE.md (version 8).

Le fichier DELTA_H_RECOLLEMENT_CONTROLE_COUT_ARBRES_2026-09-29.md n'a pas fourni de texte lisible. La branche d'observabilité d'octobre n'est connue ici que par les échanges. Le corpus intégral n'a pas été relu ; les résultats historiques non rejoués restent rapportés.

## 1. Thèse
Une description est autonome lorsque ses distinctions suffisent à composer les opérations et à prédire les expériences autorisées. Sa mémoire manquante se manifeste lorsque des continuations séparent les histoires qu'elle fusionne.

L'état peut être absent des primitives de cette présentation. Cela ne prouve pas qu'aucun état physique ne soit fondamental. Une table de réponses peut contenir autant d'information qu'un modèle d'états. La matière et le temps physique issus de la seule composition restent indéterminés.

## 2. Primitives
Fixer actions A, résultats Y, histoires accessibles H et tests futurs E, éventuellement adaptatifs. Poser composition admissible, accès aux préparations, valuation normalisée P(r|h,e), ressources et précision.

Aucun espace X de micro-configurations n'est postulé. Une réalisation par machine ou espace de Hilbert vient ensuite. La valuation et la causalité opérationnelle sont données ; ni Born ni la relativité ne sont dérivées. Une intervention omise n'est pas nécessairement une mesure dont on ignore le résultat : la cohérence des processus contrôlés exige le cadre de [R4].

## 3. États dérivés
Définir :
\[
h\sim_Eh'\iff\forall e,r,\ P(r|h,e)=P(r|h',e).
\]
L'état est [h]. L'égalité des lois constitue une équivalence.

**P1 — minimalité prédictive.** Si q(h) restitue toutes les réponses, q(h)=q(h') implique h~h'. Chaque classe distincte doit être séparée ; réciproquement les classes suffisent, puisque les lois sont constantes sur chacune.

C'est une minimalité de séparation, pas de coût algorithmique ou de dimension quantique. Antécédents : états causaux et PSR [R1–R2].

**P2 — mise à jour.** Si E est fermé sous précomposition par les interventions permises et continuations conditionnées admissibles, avec probabilités cohérentes et branches positives, h~h' implique hay~h'ay.

Preuve : les tests « a, résultat y, puis e » ont mêmes probabilités jointes ; les probabilités de y sont égales. Diviser donne les mêmes réponses conditionnelles. La mise à jour [h]→[hay] est indépendante du représentant. Sans fermeture des tests, la conclusion peut échouer.

**P3 — visibilité.** E⊆F implique que l'équivalence relative à F raffine celle relative à E. L'application [h]_F→[h]_E existe. Cela raccorde la visibilité relative à la reconstruction des états.

## 4. Fermeture
Un comportement déterministe est un arbre τ:A*→Y. Définir :
\[
(\partial_a\tau)(u)=\tau(au).
\]
Un ensemble fermé sous dérivées devient une machine : sortie τ(ε), action vers ∂_aτ. Réciproquement, les comportements d'une machine totale sont fermés. Construction connue et déjà présente dans la note du relais.

Pour T_a:X→X et π:X→Y, autonomie exacte signifie :
\[
\pi(x)=\pi(x')\Rightarrow\pi(T_ax)=\pi(T_ax')\quad\forall a.
\]
Cela équivaut à πT_a=\bar T_aπ sur l'image de π.

**P4 — réparation canonique.** Poser x≈x' si π(T_ux)=π(T_ux') pour tout mot u. C'est la plus grossière équivalence stable et raffinant π.

Preuve : le mot vide respecte π ; précomposer un mot par a donne stabilité ; tout quotient stable respectant π préserve les observations après tous les mots, donc raffine ≈.

**Calcul présent :** 5 898 machines de Moore étiquetées à 1–3 états, deux actions, deux observations ; 17 560 comparaisons de paires. Raffinement et recherche de témoins dans le produit concordent. 2 874 observations sont fermées. La preuve générale demeure distincte de ce contrôle fini.

## 5. Mémoire et coût relatif
Influence du passé, stockage et réalisation sont distincts. Nombre de classes, entropie, dimension de registre et coût de programme ne sont pas interchangeables. Une dimension quantique finie peut supporter une infinité de classes ; les états non orthogonaux n'exigent pas chacun une dimension distincte.

Soit F_old fermé sous dérivées et B_req des comportements imposés ; poser C=Der(F_old∪B_req).

**P5.** Si C\F_old est fini, le coût minimal en états ajoutés sans modifier les anciens vaut |C\F_old|. Chaque dérivée nouvelle exige un comportement distinct ; un état par dérivée atteint la borne. Si l'ensemble est infini, aucune extension déterministe finie ne convient.

Cette tâche désignée n'est pas automatiquement une complétion de langage multi-départs, qui minimise sur les couvertures admissibles.

Le relais **κ=1<m=2** illustre couvrir versus composer. Le nouveau programme retrouve 21 configurations, 54 transitions, rejette les 72 extensions à un état et trouve sept comportements distincts. C'est un modèle classique.

La borne uniforme à ordre 2 et κ=ℓ,m=2ℓ à ordre variable restent des résultats rapportés dans les notes du 2 octobre, avec leurs domaines ; tous leurs calculs ne sont pas recertifiés.

## 6. Probabilités et approximation
Γ_L et Δ_h concernent réalisabilité globale et raccordement local dans leurs cadres. Les résiduels R_u={v:uv∈L} gardent les futurs possibles. La note d'interfaces distingue défaut d'accès et défaut de recollement ; un langage enraciné n'est pas un langage multi-départs.

Même support ne signifie pas mêmes probabilités, comme l'avaient établi les audits probabiliste et empirique. Définir :
\[
d_E(h,h')=\sup_e{\rm TV}(P(\cdot|h,e),P(\cdot|h',e)).
\]
Pseudométrique standard ; son noyau exact est l'équivalence des histoires.

**Contre-exemple :** d≤ε n'est pas transitif. Pour Bernoulli(0), Bernoulli(2/5), Bernoulli(4/5), ε=1/2 : distances successives 2/5, extrême 4/5.

Le conditionnement peut amplifier : deux lois ont TV=ε, mais une branche commune de probabilité ε porte des sorties opposées, donc TV conditionnelle=1. Une faible erreur moyenne ne garantit pas une bonne prédiction après sélection.

Les erreurs de relais p^r et |p^r−p^k| sont contrôlées par **756 comparaisons rationnelles** aux horizons déclarés. Le test dirigé b^ra révèle ce qu'une distribution aléatoire rencontre rarement. Pas d'optimalité générale sous bruit physique.

## 7. Pont quantique
Pour SWAP V :
\[
H=\frac{\pi\hbar}{2\tau}(I-V),\quad V^2=I.
\]
P_-=(I−V)/2 donne U(τ)=I−2P_-=V et U(2τ)=I. Depuis |b,0⟩, τ donne |0,b⟩ : le réduit de S est identique pour b=0,1, mais la même continuation restitue b.

Sous absence de mémoire extérieure, dimension environnementale 1 est impossible et 2 suffit. Le code vérifie la permutation et les sorties (0,0), puis (0,1).

Cela ne réfute pas Schrödinger et ne prouve pas une mémoire irréductiblement quantique : deux étiquettes classiques reproduisent ces deux préparations. Les critères de [R6] sont plus exigeants.

Retenir « mêmes réponses à toutes les continuations » plutôt que « même réduit ». Les tenseurs de processus [R4,R9] donnent le cadre quantique existant ; ils ne sont pas dérivés du seul quotient. La mémoire dépend des instruments [R5]. Les expériences [R7–R8] contraignent les modèles multitemporels, sans prouver l'absence ontologique d'états. Les comptes bruts internes ne sont pas recalculés ici.

## 8. Objet et temps
Un objet demande identité observable i, opérations de maintien, perturbations et horizon. Séparer réidentification, autonomie prédictive et robustesse. Une définition probabiliste possible exige conservation de i pendant H avec probabilité ≥1−ε sous les protocoles déclarés.

Une oscillation imposée peut persister sans autonomie ; une projection autonome n'est pas forcément un objet localisé. Exiger invariance sous toutes les transformations rend souvent le résultat trivial.

Pistes : histoires décohérentes [R10], étude numérique de certaines histoires macroscopiques d'un modèle isolé ; darwinisme quantique [R11], disponibilité redondante de traces. Ce sont deux cadres distincts supposant déjà une structure quantique.

Le préfixe donne avant/après ; un poset évite un temps global mais suppose encore une causalité. Une durée additive t(g∘f)=t(g)+t(f) n'a pas d'échelle canonique : ct est également additive. Une horloge ou métrique physique reste nécessaire.

Permuter ab et ba exige égalité dans tous les contextes τ(pabv)=τ(pbav), en conservant l'admissibilité. Une observation immédiate commune ne suffit pas. Les ensembles causaux [R12] postulent une causalité ; ils ne dérivent pas tout le temps.

## 9. Corrections
- La formule x~y ssi t(x)=t(y) pour tout t d'un monoïde donne x=y si l'identité est incluse. Comparer O(t(x)) et O(t(y)). Correction de la formule littérale retrouvée.
- Chapitre 3 : Kleene A*=∨A^m est correct ; Floyd–Warshall sans étoile de boucle est trop général. Dans P(N), union et addition de Minkowski, un sommet avec identité {0}, boucle {1}, donne D initial={0,1}, puis {0,1,2}. La vraie fermeture contient 3 et tous les entiers. Contre-exemple exécuté. Réparer avec étoile des boucles ou absorption démontrée.
- Chapitre 10 : budgets et flèches ne définissent pas seuls un quantaloïde. Il manque suprema arbitraires des flèches et préservation par composition ; ∞−∞ est aussi à traiter.
- W03 actuel ne certifie pas une émergence forte. Compression≠émergence, adaptation≠autonomie, performance≠nouveauté. Ces calculs de développement ne relancent pas son confirmatoire.

## 10. Programme
**A — autonomie multitemporelle.** Comparer description instantanée et prédictive fermée sous interventions ; SWAP, modèle sans mémoire et modèles de même support mais lois différentes ; ajouter ensuite bruit déclaré. Calculer témoins et coûts avec contrat d'accès. Si tout se réduit aux invariants standards sans gain, conserver une reformulation.

**B — objets approximatifs.** Fixer observables lentes, maintien, perturbations et horizons. Calculer séparément défaut prédictif et perte d'identité. Si l'identité est fournie arbitrairement, on définit un objet choisi plutôt qu'émergent.

**C — coût relatif robuste.** Relais existant, tests dirigés versus distribués, p>1/2 puis sorties bruitées. Une séparation uniquement portée par événements rares reste un théorème exact, pas un coût physique robuste.

A est prioritaire : cadre, témoin exact et expériences de comparaison. B traite ensuite l'objet. Masse, charge, Born et espace-temps ne sont pas dérivés.

## Registre
| Énoncé | Statut |
|---|---|
| États par réponses futures | Preuve ; connu |
| Mise à jour | Preuve sous fermeture, cohérence, branches positives |
| Tests plus riches → quotient plus fin | Preuve |
| Autonomie déterministe ↔ fermeture | Preuve ; connu |
| Coût requis = dérivées nouvelles | Preuve dans la tâche désignée |
| Relais κ=1,m=2 | Preuve historique ; calcul rejoué |
| SWAP : même réduit, futurs distincts | Preuve ; Schrödinger ordinaire |
| Mémoire implique objet | Non retenu |
| Matière et temps par composition seule | Indéterminé |
| Originalité de la synthèse | Indéterminée |
| Floyd général sans étoile | Réfuté |

## Références primaires vérifiées le 12 octobre 2026
R1. Shalizi, Crutchfield, Computational Mechanics (1999/2001). https://arxiv.org/abs/cond-mat/9907176

R2. Littman, Sutton, Singh, Predictive Representations of State (NIPS 2001, volume 2002). https://papers.nips.cc/paper_files/paper/2001/hash/1e4d36177d71bbb3558e43af9577d70e-Abstract.html

R3. Abramsky, Coecke (2008). https://arxiv.org/abs/0808.1023 ; Coecke, Kissinger, Causal Quantum Processes (2015–2016). https://arxiv.org/abs/1510.05468

R4. Milz et al., extension theorem for controlled processes (2020). https://quantum-journal.org/papers/q-2020-04-20-255/

R5. Taranto et al., Structure of Quantum Stochastic Processes with Finite Markov Order (2018/2019). https://arxiv.org/abs/1810.10809

R6. Taranto et al., Hierarchy of Multi-time Quantum Processes with Classical Memory (2024). https://quantum-journal.org/papers/q-2024-05-02-1328/

R7. Guo et al., Instrument-specific Quantum Memory Effects (publication 2021). https://arxiv.org/abs/2003.14045

R8. Giarmatzi et al., Multi-time tomography on a superconducting qubit (publication 2025). https://arxiv.org/abs/2308.00750

R9. Keeling et al., Process Tensor Approaches to Non-Markovian Quantum Dynamics (2025/2026). https://arxiv.org/abs/2509.07661

R10. Strasberg, Reinhard, Schindler, Emergent Decoherent Histories (publication 2024). https://arxiv.org/abs/2304.10258 — simulation de modèles, pas validation empirique de notre hypothèse.

R11. Zurek, Quantum Darwinism (2009). https://arxiv.org/abs/0903.5082

R12. Surya, Causal set approach (2019), revue de la proposition de 1987. https://arxiv.org/abs/1903.11544

## Vérification reproductible
Code original pour cette synthèse, sans importer les scripts historiques. Ce n'est pas une reconstruction aveugle par un chercheur indépendant. Bibliothèque standard Python. Copier le code annexé dans checks.py ; exécuter python3 checks.py.


```json
{
  "exhaustive_moore": {
    "models": 5898,
    "pair_comparisons": 17560,
    "closed_observers": 2874,
    "max_shortest_distinguishing_word": 1,
    "sizes": [
      1,
      2,
      3
    ],
    "actions": 2,
    "observations": 2,
    "scope": "All labelled total Moore machines, all states treated as possible starts."
  },
  "relay": {
    "product_states": 21,
    "legal_transitions": 54,
    "one_state_extensions_rejected": 72,
    "distinct_response_behaviors": 7,
    "scope": "Finite product certificate for all word lengths; relative relay kappa=1,m=2."
  },
  "rare_tests": {
    "exact_checks": 756,
    "orders": "2..5",
    "candidate_costs": "0..6",
    "horizons": "1..9 observations",
    "probabilities": [
      "1/3",
      "1/2",
      "3/4"
    ],
    "scope": "Checks candidate errors; not an exhaustive minimality proof."
  },
  "counterexamples": {
    "floyd_warshall_without_loop_star": [
      0,
      1,
      2
    ],
    "misses_walk_length": 3,
    "epsilon_equivalence_transitive": false,
    "swap_present_outputs": [
      0,
      0
    ],
    "swap_future_outputs": [
      0,
      1
    ]
  }
}
```

```python
"""Finite exact checks for the 2026-10-12 synthesis. Python standard library only."""
from itertools import product
from collections import deque
from fractions import Fraction as F
from pathlib import Path
import json

def canonical(labels):
    keys={}
    return tuple(keys.setdefault(v,len(keys)) for v in labels)

def refine(obs,tr):
    labels=canonical(obs)
    while True:
        nxt=canonical((obs[x],tuple(labels[t[x]] for t in tr)) for x in range(len(obs)))
        if nxt==labels:return labels
        labels=nxt

def distinguish(obs,tr,x,z):
    queue=deque([(x,z,())]);seen={(x,z)}
    while queue:
        x,z,w=queue.popleft()
        if obs[x]!=obs[z]:return w
        for a,t in enumerate(tr):
            nxt=(t[x],t[z])
            if nxt not in seen:
                seen.add(nxt);queue.append((*nxt,w+(a,)))
    return None

def exhaustive():
    models=0;pairs=0;closed=0;max_length=0
    for n in (1,2,3):
        for entries in product(range(n),repeat=2*n):
            tr=(entries[:n],entries[n:])
            for obs in product((0,1),repeat=n):
                labels=refine(obs,tr)
                stable=all(obs[x]!=obs[z] or all(obs[t[x]]==obs[t[z]] for t in tr)
                           for x in range(n) for z in range(n))
                semantic=True
                for x in range(n):
                    for z in range(x+1,n):
                        witness=distinguish(obs,tr,x,z);pairs+=1
                        assert (labels[x]==labels[z])==(witness is None)
                        if witness is not None:
                            max_length=max(max_length,len(witness))
                            assert len(witness)<=n-1
                        if obs[x]==obs[z] and witness is not None:semantic=False
                assert stable==semantic
                for x in range(n):
                    for z in range(n):
                        if labels[x]==labels[z]:
                            assert all(labels[t[x]]==labels[t[z]] for t in tr)
                closed+=stable;models+=1
    return {'models':models,'pair_comparisons':pairs,'closed_observers':closed,
            'max_shortest_distinguishing_word':max_length,'sizes':[1,2,3],
            'actions':2,'observations':2,
            'scope':'All labelled total Moore machines, all states treated as possible starts.'}

def relay(k):
    o=[0,0,0,1,1];a=[4,1,1,4,1];b=[0,4,2,0,4]
    if k:
        o += [1]+[0]*(k-1);a += [4]*k
        b += [2 if k==1 else k+4]+[2 if i==1 else i+4 for i in range(1,k)]
    return o,(a,b),5 if k else 3

def response(machine,word):
    o,tr,x=machine;result=[o[x]]
    for aa in word:x=tr[aa][x];result.append(o[x])
    return tuple(result)

def rare_tests():
    checks=0
    for r in range(2,6):
        for k in range(7):
            for horizon in range(1,10):
                counts=[0]*horizon
                for word in product((0,1),repeat=horizon-1):
                    if response(relay(r),word)!=response(relay(k),word):counts[sum(word)]+=1
                for p in (F(1,3),F(1,2),F(3,4)):
                    actual=sum((count*p**b*(1-p)**(horizon-1-b)
                                for b,count in enumerate(counts)),F(0))
                    low=r if k==0 else min(r,k)
                    upper=horizon-1 if k==0 else min(max(r,k),horizon-1)
                    expected=p**low-p**upper if upper>low else F(0)
                    assert actual==expected,(r,k,horizon,p,actual,expected)
                    checks+=1
    return {'exact_checks':checks,'orders':'2..5','candidate_costs':'0..6',
            'horizons':'1..9 observations','probabilities':['1/3','1/2','3/4'],
            'scope':'Checks candidate errors; not an exhaustive minimality proof.'}

def relay_language():
    old=relay(0);new=relay(2);alphabet=tuple(product((0,1),(0,1)))
    def words(m,length):
        o,tr,_=m;out=set()
        for x0 in range(len(o)):
            for aa in product((0,1),repeat=length):
                x=x0;w=[]
                for a in aa:w.append((o[x],a));x=tr[a][x]
                out.add(tuple(w))
        return out
    allowed={k:words(old,k) for k in (1,2,3)}
    assert all(words(new,k)==allowed[k] for k in allowed)
    def update(belief,sym):
        y,a=sym;o,tr,_=new
        return frozenset(tr[a][x] for x in belief if o[x]==y)
    start=((),frozenset(range(7)));queue=deque([start]);seen={start};edges=0
    while queue:
        context,belief=queue.popleft()
        for sym in alphabet:
            window=context+(sym,);legal=window in allowed[len(window)]
            dest=update(belief,sym)
            assert bool(dest)==legal
            if legal:
                edges+=1;nxt=(window[-2:],dest)
                if nxt not in seen:seen.add(nxt);queue.append(nxt)
    witness=((1,1),(0,1),(0,0),(0,0))
    assert witness not in words(old,4) and witness in words(new,4)
    one_added_rejected=0
    for y in (0,1):
        for a,b in product(range(6),repeat=2):
            candidate=(old[0]+[y],(old[1][0]+[a],old[1][1]+[b]),5)
            if witness not in words(candidate,4) or not words(candidate,3)<=allowed[3]:
                one_added_rejected+=1
    assert one_added_rejected==72
    labels=refine(new[0],new[1]);assert len(set(labels))==7
    return {'product_states':len(seen),'legal_transitions':edges,
            'one_state_extensions_rejected':one_added_rejected,
            'distinct_response_behaviors':len(set(labels)),
            'scope':'Finite product certificate for all word lengths; relative relay kappa=1,m=2.'}

def hostile_checks():
    d={0,1};computed=d|{x+y for x in d for y in d}
    assert computed=={0,1,2} and 3 not in computed
    epsilon=F(1,2);p,q,r=F(0),F(2,5),F(4,5)
    assert abs(p-q)<=epsilon and abs(q-r)<=epsilon and abs(p-r)>epsilon
    swap=(0,2,1,3)
    assert all(swap[swap[i]]==i for i in range(4))
    first=[swap[2*b]//2 for b in (0,1)]
    second=[swap[swap[2*b]]//2 for b in (0,1)]
    assert first==[0,0] and second==[0,1]
    return {'floyd_warshall_without_loop_star':sorted(computed),'misses_walk_length':3,
            'epsilon_equivalence_transitive':False,
            'swap_present_outputs':first,'swap_future_outputs':second}

if __name__=='__main__':
    results={'exhaustive_moore':exhaustive(),'relay':relay_language(),
             'rare_tests':rare_tests(),'counterexamples':hostile_checks()}
    Path(__file__).with_suffix('.json').write_text(json.dumps(results,indent=2)+'\n')
    print(json.dumps(results,indent=2))
```


## Audit de compatibilité — version 0.2, 12 octobre 2026

**Verdict :** le noyau de reconstruction est cohérent avec les cadres connus sous les hypothèses précisées. Il est largement une reformulation. La classe générale de réponses admise en version 0.1 est trop large pour constituer à elle seule une théorie de la physique quantique. Aucune nouvelle prédiction empirique ni adéquation quantitative aux données n'a été démontrée.

### A. Portée des propositions

P1 est une preuve de quotient suffisant minimal au sens de la séparation des histoires, pour une même interface de tests. Elle ne transfère pas tous les théorèmes entropiques des états causaux : le travail de Shalizi–Crutchfield étudié suppose des processus stationnaires, discrets en temps et à valeurs discrètes. Notre construction ponctuelle ne demande pas stationnarité ; les quantités entropiques et limites asymptotiques demandent leurs hypothèses propres.

P2 exige une interface commune, avec tests de résultats intermédiaires compris. Comparer les histoires à une même frontière expérimentale typée ; si les instants, interfaces ou horizons diffèrent, déclarer leurs identifications ou les inclure dans le type de l'état. Poser explicitement :
P(y,r|h,a;e)=P(y|h,a)P(r|hay,e).
C'est la cohérence utilisée dans la preuve. Pour des résultats continus, préciser des noyaux conditionnels réguliers et raisonner presque sûrement ; conditionner sur chaque valeur ponctuelle n'est pas automatiquement valide.

P3 reste une monotonie des possibilités de discrimination sous ajout de tests. Elle n'est pas une monotonie universelle d'une mesure de mémoire sous toute intervention.

P4 est correct pour les machines déterministes totales et l'observation déclarée. L'importer dans une chaîne stochastique exige un critère distinct.

P5 exige un ancien dispositif déterministe total fini, des réponses requises exactes, tous leurs prolongements sous les actions admises et un coût comptant uniquement les états ajoutés. Le résultat ne s'applique pas directement aux automates probabilistes, registres quantiques ou coûts algorithmiques.

### B. Correction de l'extension stochastique

Pour une chaîne finie à noyau K_a et partition π, l'autonomie de la projection pour toutes les distributions initiales est la lumpabilité forte :
\[
\pi(x)=\pi(x')\Rightarrow
\sum_{\pi(z)=y}K_a(x,z)=
\sum_{\pi(z)=y}K_a(x',z)
\quad\forall a,y.
\]
Il faut l'égalité des probabilités par bloc, pas seulement l'égalité du support des transitions.

Contre-exemple exécuté : trois états, partition {0,1}|{2},
K(0,·)=(1/10,0,9/10),
K(1,·)=(9/10,0,1/10),
K(2,·)=(0,0,1).
Les deux premiers états ont le même support, mais les probabilités vers le bloc {2} valent 9/10 et 1/10. La projection n'est pas fortement lumpable. Les versions faibles, valables seulement pour certaines distributions initiales, ne sont pas équivalentes à ce critère universel.

Source primaire : Testing lumpability in Markov chains (2003), article vérifié :
https://www.sciencedirect.com/science/article/pii/S0167715203001263

### C. Obstruction décisive : probabilités cohérentes ne sélectionnent pas la mécanique quantique

La version 0.1 ne spécifie pas de composition spatiale quantique. Si l'on étend sa valuation abstraite à deux laboratoires locaux indépendants, normalisation et non-signalisation ne suffisent pas.

Construire des entrées x,y∈{0,1}, sorties a,b∈{0,1}, avec
\[
P(a,b|x,y)=
\begin{cases}
1/2,&a\oplus b=xy,\\
0,&\text{sinon}.
\end{cases}
\]
Les probabilités sont positives et normalisées. Chaque marginale locale est uniforme et indépendante du réglage distant. Les corrélations sont E00=E01=E10=1,E11=−1, donc CHSH=4.

Pour deux parties dans le modèle quantique tensoriel standard, |CHSH|≤2√2. Le calcul rationnel confirme 4²=16>8. Il contrôle le tableau ; la borne quantique provient du théorème, pas du script.

C'est la boîte PR connue. Elle ne réfute pas les propositions de quotient, et aucune observation d'une boîte PR n'est alléguée. Elle réfute la suffisance des seules probabilités cohérentes et du non-signalling pour retrouver la classe quantique. Si l'on interprète la table comme un appareil central recevant les deux entrées, la conclusion sur deux laboratoires séparés ne s'applique pas : le contrat spatial fait partie des hypothèses.

Source primaire : Popescu–Rohrlich, Nonlocality as an axiom for quantum theory, prépublication 1995, discussion d'un résultat publié en 1994, pp.2–3 :
https://arxiv.org/pdf/quant-ph/9508009

### D. Réparation possible du secteur quantique

Pour un modèle quantique fini à ordre causal fixé, imposer :
- des opérations d'instruments complètement positives, de trace non croissante, dont la somme est un canal ;
- une valuation multilinéraire physiquement cohérente sur ces opérations ;
- un tenseur de processus positif et des contraintes de normalisation causale ;
- une composition avec systèmes auxiliaires qui conserve l'admissibilité.

Ce sont des conditions du cadre connu des tenseurs de processus, et non des lois nouvelles obtenues dans notre programme. Les adopter construit un secteur quantique compatible ; cela importe une structure quantique au lieu de la dériver.

Source primaire : Milz et al., Kolmogorov extension theorem for (quantum) causal modelling and general probabilistic theories (2020), §§sur le secteur quantique :
https://arxiv.org/pdf/1712.02589

Une route alternative serait une reconstruction axiomatique. Chiribella, D'Ariano et Perinotti (2011) dérivent la théorie quantique à partir de principes informationnels explicitement déclarés :
https://arxiv.org/abs/1011.6451
Cette source montre la nécessité d'un travail d'axiomatisation supplémentaire ; elle ne prouve pas que nos seules primitives suffisent.

### E. Confrontation aux expériences

Guo et al. (2021) utilisent deux processus à cause commune. Ils sont CP-divisibles dans leurs descriptions à deux temps, mais non markoviens multitemporellement. Certains instruments bloquent les corrélations histoire-futur. Cela concorde avec la distinction de la version 0.1 entre observation partielle, continuation et classe d'instruments.

Ce n'est pas le même mécanisme dynamique que notre retour par SWAP. La ressemblance porte sur l'insuffisance de certains résumés et la dépendance aux interventions.

Source primaire complète : https://arxiv.org/html/2003.14045v3, introduction, section Markov Order et annexe.

Les expériences de White (2020) et Giarmatzi (2025) fournissent des méthodes et des données de processus multitemporels. Notre version n'a pas produit de paramètres ajustés, de vraisemblance, de prédictions tenues à part ou de comparaison de modèles sur ces données. Le verdict empirique est donc « rapprochement conceptuel compatible », pas « théorie validée ».

Les histoires décohérentes (2024) sont une étude numérique de modèles déjà quantiques ; leur émergence approximative de classicalité ne démontre ni notre notion d'objet autonome ni une élimination des états fondamentaux.

### F. Registre révisé

| Question | Verdict |
|---|---|
| Quotient prédictif et mise à jour cohérente | Corrects sous hypothèses précisées ; antécédents connus |
| Fermeture déterministe | Correcte dans sa classe |
| Extension stochastique | Ajouter la lumpabilité et le contrat de distribution initiale |
| Mémoire accessible dépendant des instruments | Accord avec théorie et expériences publiées |
| Réponses générales nécessairement quantiques | Faux sans contraintes supplémentaires |
| Même mécanisme que les expériences photoniques | Non : cause commune versus échange SWAP |
| Objet, matière et temps émergent démontrés | Non établis |
| Ajustement empirique quantitatif | Non effectué |
| Nouveauté de la synthèse | Non établie |

**Décision :** conserver le noyau comme cadre de représentation et de réalisation relative, avec secteurs déterministe, stochastique et quantique explicitement typés. La prochaine contribution doit être un résultat additionnel ou un diagnostic prédictif mesurable qui dépasse une traduction de cadres connus.

### Calculs adversariaux nouveaux


```json
{
  "pr_box": {
    "normalized": true,
    "no_signalling": true,
    "CHSH": "4",
    "CHSH_squared": "16",
    "quantum_CHSH_squared_upper_bound": 8
  },
  "support_vs_lumpability": {
    "same_support": true,
    "macro_probability_from_state0": "9/10",
    "macro_probability_from_state1": "1/10",
    "strong_lumpability": false
  },
  "scope": "Mathematical counterexamples, not observations of these laws in nature."
}
```

```python
"""Exact adversarial checks; not experimental data or quantum simulation."""
from fractions import Fraction as F
from itertools import product
import json

pr={(x,y,a,b):F(1,2) if (a^b)==x*y else F(0)
    for x,y,a,b in product((0,1),repeat=4)}
for x,y in product((0,1),repeat=2):
    assert sum(pr[x,y,a,b] for a,b in product((0,1),repeat=2))==1
for x,a in product((0,1),repeat=2):
    assert all(sum(pr[x,y,a,b] for b in (0,1))==F(1,2) for y in (0,1))
for y,b in product((0,1),repeat=2):
    assert all(sum(pr[x,y,a,b] for a in (0,1))==F(1,2) for x in (0,1))
corr={(x,y):sum((-1)**(a+b)*pr[x,y,a,b]
                for a,b in product((0,1),repeat=2))
      for x,y in product((0,1),repeat=2)}
chsh=corr[0,0]+corr[0,1]+corr[1,0]-corr[1,1]
assert chsh==4 and chsh**2>8

# Same transition support from two states in one macro block,
# different total probabilities toward the other block.
k=((F(1,10),F(0),F(9,10)),
   (F(9,10),F(0),F(1,10)),
   (F(0),F(0),F(1)))
assert all(sum(row)==1 for row in k)
assert tuple(p>0 for p in k[0])==tuple(p>0 for p in k[1])
assert k[0][2]!=k[1][2]
out={'pr_box':{'normalized':True,'no_signalling':True,
               'CHSH':str(chsh),'CHSH_squared':str(chsh**2),
               'quantum_CHSH_squared_upper_bound':8},
     'support_vs_lumpability':{'same_support':True,
                              'macro_probability_from_state0':str(k[0][2]),
                              'macro_probability_from_state1':str(k[1][2]),
                              'strong_lumpability':False},
     'scope':'Mathematical counterexamples, not observations of these laws in nature.'}
print(json.dumps(out,indent=2))
```