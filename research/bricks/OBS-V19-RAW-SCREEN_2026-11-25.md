# V19 — Filtre avant la construction du quotient

25 novembre 2026, 09 h 17 CET. Branche `work/omega-math-brick-pilot-2026-11-14`, SHA initial `40761890962c1611ee8baafea79c35a62adf84ac` (STRATA). Sources : audit L+1 blob `6caf1578029ec9b87974a8357f99e5816b217f27`, index historique #2 `2f71a6b8ed03914c0b5d308520d30e0133d9e9ad`, PR #5 `639dc01ca3ea58c61b075adb9a6d860bf41db7bc`, PR #18 `763d77f0aa735d90bb558b2c7fac056298d5313c`. L’ombre est la projection des colorations globalement cohérentes. Le garde correspond à la projection exhaustive sur le témoin à cinq états (2 comparaisons) et la famille distincte (4 536), avec 2 et 276 divergences pour l’ancienne approximation.

Hypothèse : tester les boucles et arêtes parallèles sur les événements bruts avant de construire le quotient gagne ≥10 % sur la strate rejetée tôt et coûte ≤10 % sur chaque autre strate, zéro erreur. Protocole gelé `d2902cd004d77d3fee8cad9a96acc3a213df314a41ef8214deba35532ef0dabb`. Deux témoins adverses : parallèle contradictoire constituant déjà un noyau de deux arêtes, rejeté pour la recherche d'un noyau minimal à quatre arêtes ; couplage de quatre arêtes disjointes qui devient un cycle impair après contraction, accepté. Les verdicts des deux témoins correspondent au projecteur exhaustif. Une boucle brute reste une boucle dans le quotient. Deux arêtes parallèles brutes restent parallèles ou deviennent des boucles. C'est une justification du crible sous le critère de quotient C4 déjà utilisé, avec F cohérent. Ces relations ne dépendent pas de la mesure de vitesse.

| Réserve | Strate | Nombre | Complet (µs) | Non signé (µs) | Signé (µs) | Crible + signé (µs) |
|---|---|---:|---:|---:|---:|---:|
| C4 | Rejet brut | 12 | 4,170 | 1,748 | 2,465 | 0,372 |
| C4 | Rejet par quotient | 12 | 2,656 | 1,636 | 2,684 | 3,148 |
| C4 | Survivant négatif | 12 | 2,555 | 6,090 | 2,670 | 3,184 |
| C4 | Noyau | 12 | 10,827 | 14,696 | 3,070 | 3,553 |
| C5 | Rejet par quotient | 12 | 2,416 | 1,640 | 2,742 | 3,143 |

**RÉFUTÉ — calcul fini de performance.** 60 paires, 12 positives, 0 erreur par bras. Trois strates C5 non représentées. Crible 78,7 % plus rapide que le meilleur fixe sur les rejets bruts et 14,6 à 19,3 % plus lent que le signé dans les autres strates observées. Seuil global manqué. Candidat conservé comme harnais expérimental pour reproduction, vérificateur de référence conservé. Aucun résultat d’originalité. Prochain test : mesurer la prévalence brute sur un flux de cartes non stratifié et déterminer le taux de rupture d’équilibre avant d’étudier une fusion du crible dans la génération des événements.

Reproduction : `cd research/code && timeout 60s python3 v19_raw_screen.py` (1,917 s). SHA-256 du code `44550d8522f1e9cdd97bfdc139018c376a70eac2599ff7a3fa248cc56d89937d`, agrégats `c10fec0d9c2d5723f07b8219570e3d2231a76ed0ad5ebd77ba331709e61fb3b6`. Gel historique séparé `python3 test_v19_locality_l_plus_1.py` PASS, 325 468 comparaisons, SHA-256 `b4556e78b12edbd2467eb7166576d4202cfa1cdaa10a3113730a5be5d6487946`. Registre #239 lu et SHA vérifié `184d8d9868ffb90a97c6f171693f3f54f5785d83`. `existing_math_pilot` examiné, pertinent, exécuté, utile pour rejeter ce candidat. Aucun nouveau composant, aucun coût payant.
