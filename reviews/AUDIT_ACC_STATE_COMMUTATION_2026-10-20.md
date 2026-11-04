# Audit RAVI-2 — commutation accessibilité / quotient prédictif

Date : 20 octobre 2026

## Objet
Fermer le premier pont remonté par RAVI-2 Discovery entre `BR-ACC-01` et `BR-STATE-01` sans promouvoir une analogie lexicale ni revendiquer une nouveauté connue de la littérature.

## Énoncé audité
Pour un système fini déterministe total avec observation `π` et ensemble initial non vide `E`, si `≈` est l’équivalence prédictive canonique par égalité de toutes les continuations observées, `H=Reach(E)` et `q:X→X/≈`, alors : `q(H)=Reach(q(E))`, l’équivalence prédictive du sous-système `H` est `≈|_H`, et `H/(≈|_H)` est canoniquement isomorphe à la partie accessible du quotient global.

## Audit de preuve
PASS. La preuve est directe : stabilité de `≈` sous les actions, commutation `q∘T_a=Tbar_a∘q`, induction sur les mots, puis invariance avant de `H`. Aucun argument probabiliste, asymptotique ou numérique n’est requis.

## Falsification indépendante
PASS. Artefact existant : `/Recherche/04_CODE_DONNEES/RAVI2_DISCOVERY/ACCESS_PREDICTIVE_BRIDGE_CHECK.json`.

- 41 018 cas exhaustifs (`n≤3`, deux actions, observation binaire, tous ensembles initiaux non vides) ;
- 20 000 cas aléatoires (`n=4..8`, 1–3 actions, 2–3 symboles d’observation) ;
- zéro violation.

Le budget de fermeture reste borné : aucune nouvelle expérience n’est ouverte car la preuve et un contrôle indépendant couvrent déjà le verrou.

## Audit de redondance interne
Le résultat n’est pas écrit comme théorème autonome dans les cartes actives : `BR-ACC-01` traite la fermeture accessible et la séparation défaut d’accès / défaut de recollement ; `BR-STATE-01` traite le quotient prédictif canonique. Leur commutation explicite est donc utile comme interface transversale.

## Audit bibliographique externe
Verdict : **CONNU_OU_CLASSIQUE**.

Références principales :
1. Jiří Adámek, Stefan Milius, Lawrence S. Moss, Lurdes Sousa, *Well-Pointed Coalgebras*, Logical Methods in Computer Science 9(3), 2013, DOI `10.2168/LMCS-9(3:2)2013`, en particulier Example 3.19 / Remark 3.20 : pour les automates déterministes, minimisation comportementale et élimination des états inaccessibles peuvent être effectuées dans les deux ordres sous les hypothèses indiquées.
2. Thorsten Wißmann, *Minimality Notions via Factorization Systems and Examples*, Logical Methods in Computer Science 18(3):31, 2022, DOI `10.46298/LMCS-18(3:31)2022`, qui formalise l’interaction entre reachability et observability/minimization et les critères permettant de les séquencer dans un ordre arbitraire.

Le théorème interne est une spécialisation transparente à nos notations `BR-ACC-01` / `BR-STATE-01`. Aucune revendication de nouveauté externe n’est défendable.

## Contrats stricts
Les deux raccords sont classés `DEFINITION_REFERENCE`, pas `COMPOSITION` :
- vers `BR-ACC-01` pour `Reach(E)` ;
- vers `BR-STATE-01` pour l’équivalence prédictive stable et le quotient.

Cette classification évite de gonfler artificiellement le nombre de compositions certifiées.

## Verdict RAVI-2
- vérité interne : **DÉMONTRÉE** ;
- robustesse : **PASS** ;
- redondance interne : **NON REDONDANT comme interface** ;
- originalité externe : **CONNU_OU_CLASSIQUE** ;
- décision : **PROMOUVABLE comme brique de raccordement classique**, sans revendication de découverte.

ID : `BR-ACC-STATE-COMMUTE-01`.