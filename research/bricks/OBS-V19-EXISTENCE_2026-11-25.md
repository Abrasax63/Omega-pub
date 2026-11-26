# V19 — Coût d'un premier témoin pour une requête existentielle

25 novembre 2026, 14 h 14–14 h 16 CET. Branche `work/omega-math-brick-pilot-2026-11-14`, départ `b10d357943dd4089e285faf56b03acb6d8fa1107`. Sources : audit L+1 blob `6caf1578029ec9b87974a8357f99e5816b217f27`, index #2 `2f71a6b8ed03914c0b5d308520d30e0133d9e9ad`, #5 `639dc01ca3ea58c61b075adb9a6d860bf41db7bc`, #18 `763d77f0aa735d90bb558b2c7fac056298d5313c`. L'ombre exige une extension globale. Le garde concorde avec la projection exhaustive sur deux projections du témoin à cinq états et 4 536 de la famille distincte.

Hypothèse : arrêter au premier noyau conserve l'identité du premier témoin et économise au moins 20 % sur les cartes positives ; sur les négatifs, surcoût au plus 10 %. Protocole `f8324bf4598d6ea122e3fca98e16bf4ed2ee73996cceb4413c2039cfbdcb76fe`. Même quotient signé par carte. Oracle : projections exhaustives pour chaque paire admissible. Cas adverse C4 pur, aucun témoin, six paires examinées. L'ordre inverse est un contrôle sur les mêmes cartes.

| Famille | Ordre | Cartes | Paires vérifiées fixe → candidat | µs/carte fixe → candidat |
|---|---|---:|---:|---:|
| C4, positives | Direct | 20 | 420 → 118 | 29,06 → 10,67 |
| C4, positives | Inverse | 20 | 420 → 122 | 27,89 → 9,26 |
| C6, négatives | Direct | 42 | 1512 → 1512 | 45,19 → 45,34 |
| C6, négatives | Inverse | 42 | 1512 → 1512 | 44,84 → 46,85 |

**VÉRIFIÉ, calcul fini.** Zéro désaccord sur 62 cartes, dans les deux ordres. Sur les cartes positives, réduction du temps de 63,3 % puis 66,8 % ; sur les négatives, surcoût de 0,3 % puis 4,5 %. Les familles sont séparées par leur résultat dans cette réserve : ni négatifs C4 à attaches ni positifs C6 observés. L'équivalence à ordre donné découle d'une liste parcourue par le même prédicat : une requête dont le seul résultat est le premier témoin peut s'arrêter sur son premier vrai ; une requête de décompte ne le peut pas. Le pilote est conservé pour l'usage existentiel. Aucune affirmation d'originalité bibliographique. Prochain test : comparer l'ordre lexicographique à un ordre établi sans connaître les labels sur un lot d'une même famille mêlant positifs et négatifs, coût du classement inclus.

`cd research/code && timeout 60s python3 v19_existence.py`, 4,209 s. Code `c76bd1623c7a2ae4699a5f7778cc50ed2689db28f8b6164a15644570b9c3d731`, agrégats `d8340042f5fb905e43e347600067cc7a33660eb6066ebca63b66a82c07fd219f`. Non-régression séparée `python3 test_v19_locality_l_plus_1.py`, PASS 325 468 comparaisons. Registre lu au SHA vérifié `184d8d9868ffb90a97c6f171693f3f54f5785d83`, `existing_math_pilot` considéré, pertinent, exécuté et utile pour distinguer recherche et décompte. Aucun nouveau composant et coût payant nul.
