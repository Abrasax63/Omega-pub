# DET-FIN-01 — Perte asymptotique de sensibilité d’un détecteur fini à risque total borné

**Statut : DÉMONTRÉ interne. Version 1.0 — 2026-10-19.**

## Domaine
Automate déterministe fini de surveillance, état d’alerte absorbant, alphabet fini, toute mémoire persistante et toute horloge incluses dans l’état. Sous le nul, chaque symbole admissible a une probabilité conditionnelle au moins \(\eta>0\) après toute histoire réalisable. Le risque total satisfait \(\Pr_0(T<\infty)\le\alpha<1\).

## Énoncé
Soit \(Q_n\) une loi de changement qui coïncide exactement avec le nul pendant les \(n\) premières observations, puis peut choisir arbitrairement une loi sur le même alphabet. Alors
\[
\sup_{Q_n}\Pr_{Q_n}(n<T<\infty\mid T>n)\longrightarrow0\qquad(n\to\infty).
\]
Ainsi, un détecteur à mémoire finie et risque total de fausse alarme strictement inférieur à 1 perd sa capacité conditionnelle à détecter des changements arbitrairement tardifs, même sans imposer de borne de délai après le changement.

## Preuve
Avec \(M\) états non-alertes, tout état depuis lequel l’alerte est atteignable possède un chemin simple vers l’alerte de longueur au plus \(M\). Sous le nul, ce chemin a probabilité au moins \(\eta^M\). Or \(\Pr_0(n<T<\infty\mid T>n)\to0\), puisque \(\Pr_0(T>n)\to\Pr_0(T=\infty)>0\). La masse conditionnelle des états encore capables d’atteindre l’alerte tend donc vers zéro, uniformément sur toute stratégie post-changement. Un contrôle exhaustif indépendant a vérifié le lemme de graphe sur 4181 automates binaires à 1–3 états non-alertes et 12454 couples automate/état.

## Limites
Le résultat vise le contrôle de probabilité totale de fausse alarme, pas les critères classiques de type ARL. Il suppose un automate fixe fini et un plancher \(\eta>0\). L’originalité historique exacte n’est pas établie.

## Provenance
`/Recherche/02_PROGRAMMES_ACTIFS/Transformations_Autonomie/detection_correlations_2026-10-14.md`, résultat `DET-FIN-01`.