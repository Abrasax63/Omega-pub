# V19 — Détection fusionnée quand le quotient est partagé

25 novembre 2026, 12 h 44–12 h 46 CET. Branche `work/omega-math-brick-pilot-2026-11-14`, départ `99c077a442fcf4a059a6e01180c8c009aa19cc7f`. Sources : audit L+1 blob `6caf1578029ec9b87974a8357f99e5816b217f27`, index #2 `2f71a6b8ed03914c0b5d308520d30e0133d9e9ad`, #5 `639dc01ca3ea58c61b075adb9a6d860bf41db7bc`, #18 `763d77f0aa735d90bb558b2c7fac056298d5313c`. L'ombre requiert une extension globale. Le garde concorde avec le projecteur exhaustif sur 2 projections du témoin à cinq états et 4 536 d'une famille distincte.

Hypothèse : à quotient calculé une fois par carte dans chaque bras, la fusion gagne au moins 10 % dans les deux familles et deux tailles de lots, zéro erreur. Préenregistrement `a1cc231bfca37bd3eefd24d9e3aa96971cbc6fbd296fa6b51d569df6cd3b8fe7`. Fusion précoce de trajectoires et répétition inversée du même événement vérifiées comme des sorties négatives. La vérité est fournie par la projection exhaustive sur les traces de quatre événements. Les lots réduits sont des sous-ensembles des flux, leurs effectifs ne sont pas additionnés comme cas indépendants.

| Flux | Taille | Paires | Positifs | Sans crible (ns) | Séparé (ns) | Fusionné (ns) |
|---|---|---:|---:|---:|---:|---:|
| Point fixe | Complet | 720 | 80 | 1312,8 | 1588,3 | 1376,7 |
| Point fixe | Six paires par carte | 120 | 10 | 1487,0 | 1685,1 | 1446,8 |
| Transposition | Complet | 1080 | 88 | 1340,0 | 1682,9 | 1324,2 |
| Transposition | Six paires par carte | 144 | 5 | 1433,7 | 1750,6 | 1496,0 |

**RÉFUTÉ, calcul fini.** Zéro divergence sur les 1 800 paires uniques des flux. Variation du candidat de −2,7 % à +4,9 % face au meilleur fixe selon la cellule. Candidat archivé, référence conservée. Aucun résultat d'originalité bibliographique. Prochain test : changer de raccord et mesurer l'effet d'arrêter l'énumération à la première preuve dans une tâche existentielle explicitement séparée du décompte exhaustif.

`cd research/code && timeout 60s python3 v19_amortized_fused.py`, 5,590 s. Code SHA-256 `666c631771246d010f8a82e4b1e3b925840c015665b0a2329e26ea51684d837b`, agrégats `b3dd1c18d20ca48d798527e8bf548710760de07a70ea70f3fff3f549db89a682`. Test historique séparé `python3 test_v19_locality_l_plus_1.py`, PASS 325 468 comparaisons. Registre lu, SHA vérifié `184d8d9868ffb90a97c6f171693f3f54f5785d83` ; `existing_math_pilot` considéré, pertinent, exécuté par le banc local et utile pour écarter le candidat. Aucun nouveau composant et coût payant nul.
