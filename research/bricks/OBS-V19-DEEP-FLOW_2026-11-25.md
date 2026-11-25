# V19 — Crible brut sur deux flux profonds avec des noyaux

25 novembre 2026, 11 h 10–11 h 12 CET. Branche `work/omega-math-brick-pilot-2026-11-14`, départ `3ac010e836cab0e78b450c952d644a940c8a20ac`. Sources épinglées : audit L+1 blob `6caf1578029ec9b87974a8357f99e5816b217f27`, index #2 `2f71a6b8ed03914c0b5d308520d30e0133d9e9ad`, #5 `639dc01ca3ea58c61b075adb9a6d860bf41db7bc`, #18 `763d77f0aa735d90bb558b2c7fac056298d5313c`. L’ombre requiert une extension globale. Le garde concorde avec le projecteur exhaustif sur le témoin à cinq états (2 projections) et la famille distincte (4 536).

Le protocole SHA-256 `393b2571fae21aef8b1ca8daa5e4e5d18045bb2b3e5aa8a470ff8021d14370bf` demande si le crible brut peut gagner 10 % sur le meilleur bras fixe dans deux flux C4 contenant des noyaux. Toutes les paires admissibles sont mesurées, sans trier par vérité terrain. Le témoin à parallèles opposés échoue bien au critère de minimalité à quatre événements. Oracle de projection exhaustif sur chaque paire. Temps en µs par paire.

| Flux | Cartes | Paires | Noyaux | Rejets bruts | Complet | Non signé | Signé | Crible + signé |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| C4 + transposition | 32 | 1300 | 88 | 152 | 3,456 | 3,317 | 2,877 | 3,058 |
| C4 + point fixe | 28 | 884 | 80 | 100 | 3,474 | 3,696 | 2,784 | 3,189 |

**RÉFUTÉ, calcul fini.** Zéro erreur des quatre bras sur 2 184 paires. Le surcoût du crible face au signé vaut 6,3 % et 14,5 %. Le résultat couvre deux flux contenant des positifs, sans proposition de généralité bibliographique. Référence conservée, aucune intégration. Le prochain test doit changer le mécanisme : évaluer une détection de doublon fusionnée à la construction des événements, coût total depuis la paire d'états, avant tout nouvel essai de filtre séparé.

`cd research/code && timeout 60s python3 v19_deep_flow.py`, 8,217 s. SHA-256 code `403879ef3449c216e239320c2b61c02b20df2bc9291872d5c99fec84a85af22b`, agrégats `7d549c3a36d31b47ec8e7fa698e00733baebd9fedb5ee56a69030744d78e0b77`. Contrôle historique séparé `python3 test_v19_locality_l_plus_1.py`, PASS 325 468 comparaisons. Registre lu au SHA vérifié `184d8d9868ffb90a97c6f171693f3f54f5785d83`, `existing_math_pilot` examiné, pertinent et banc local exécuté ; utile pour écarter le filtre séparé. Aucun nouveau composant, aucun coût payant.
