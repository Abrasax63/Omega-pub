# V19 — Détecter les doublons pendant la génération des événements

25 novembre 2026, 11 h 30–11 h 33 CET. Branche `work/omega-math-brick-pilot-2026-11-14`, départ `61d53f92475f250e0d6bfe31e6aa7a85a7d35f55`. Sources : audit L+1 blob `6caf1578029ec9b87974a8357f99e5816b217f27`, index #2 `2f71a6b8ed03914c0b5d308520d30e0133d9e9ad`, #5 `639dc01ca3ea58c61b075adb9a6d860bf41db7bc`, #18 `763d77f0aa735d90bb558b2c7fac056298d5313c`. La définition de l'ombre exige une extension globale. Le garde concorde avec la projection exhaustive sur le témoin à cinq états (2 projections) et la famille distincte historique (4 536).

Hypothèse : sortir dès une répétition non orientée ou une fusion avant quatre événements économise au moins 10 % face au meilleur fixe, coût de génération compris. Protocole SHA-256 `41098ae2a6c9f8950d4e700e5b197678929ad274e479b8aff4ed452ae862ae05`. Deux nouvelles familles de fourches, toutes les paires. Témoin de la transposition : deux occurrences de même paire en ordre opposé, rejet confirmé. Projection exhaustive pour les paires à quatre événements. Le verdict des paires à moins de quatre événements reste négatif pour cette certification.

| Famille | Paires | Positifs | Fusions précoces | Signé seul (µs) | Crible séparé (µs) | Candidat (µs) |
|---|---:|---:|---:|---:|---:|---:|
| C4 + transposition | 1260 | 80 | 148 | 3,152 | 3,270 | 2,966 |
| C4 + point fixe | 864 | 72 | 128 | 2,822 | 2,875 | 2,595 |

**RÉFUTÉ au seuil fixé, calcul fini.** Zéro erreur des trois bras sur 2 124 paires. Les gains mesurés de 5,9 % et 8,0 % sont inférieurs aux 10 % préenregistrés. Candidat archivé, référence applicative conservée. Aucune revendication bibliographique. Prochain essai : mesurer le coût complet en amortissant le quotient une fois par carte, avec un témoin de lots mixtes qui peut invalider le bénéfice.

`cd research/code && timeout 60s python3 v19_fused_build.py`, 6,897 s. Code `6cb63affed9874537929592516060b9e9c32ed04149a87c46f0fd4fe7630239f`, agrégats `3cd711be2b6fed989f22d7c2fcbdd8dab7f012b172e4375c594fba457f4ad03d`. Non-régression séparée `python3 test_v19_locality_l_plus_1.py`, PASS 325 468 comparaisons. Registre lu au SHA vérifié `184d8d9868ffb90a97c6f171693f3f54f5785d83`. `existing_math_pilot` considéré, pertinent et exécuté via les outils du pilote, utile pour quantifier le gain insuffisant. Aucun nouveau composant et coût payant nul.
