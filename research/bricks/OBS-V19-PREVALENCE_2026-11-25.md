# V19 — Prévalence du rejet brut sur deux flux non stratifiés

25 novembre 2026. Branche `work/omega-math-brick-pilot-2026-11-14`, départ `707cc1af527154e350e78faddc31791c8840dcec` (RAW SCREEN). Sources : audit L+1 blob `6caf1578029ec9b87974a8357f99e5816b217f27`, index #2 `2f71a6b8ed03914c0b5d308520d30e0133d9e9ad`, #5 `639dc01ca3ea58c61b075adb9a6d860bf41db7bc`, #18 `763d77f0aa735d90bb558b2c7fac056298d5313c`. L’ombre est la projection des colorations globalement cohérentes. Le garde concorde avec le projecteur exhaustif sur 2 projections du témoin à cinq états et 4 536 d’une famille distincte.

Question : la fréquence des rejets avant quotient suffit-elle à gagner 10 % sur le meilleur bras fixe dans chacun de deux flux non stratifiés ? Protocole préalable `a2b1ae087711de1f5099b1f3b17f1542c32f14590a42fbfffb2e3cb02a2b59ca`. Témoin adverse de parallèles opposés vérifié. Les 32 cartes sont choisies avant toute étiquette. Toutes les paires admissibles sont comptées. Référence indépendante : cinq projections exhaustives par paire. Quatre bras mesurés à budget égal.

| Famille | Rejets bruts | Paires | Complet (µs) | Non signé (µs) | Signé (µs) | Crible + signé (µs) |
|---|---:|---:|---:|---:|---:|---:|
| C6 + transposition et deux attaches | 73 (10,61 %) | 688 | 2,768 | 1,669 | 2,803 | 2,912 |
| C7 + transposition et deux attaches | 26 (3,07 %) | 848 | 2,917 | 1,779 | 2,987 | 3,454 |

**RÉFUTÉ — calcul fini.** 1 536 paires, zéro divergence pour chacun des bras, zéro noyau dans la réserve. Surcoût par rapport au meilleur fixe de 74,5 % et 94,2 %. Les taux observés ne suffisent donc pas à rentabiliser le crible. Une réserve sans vrais positifs ne renseigne pas sur les flux où ils abondent. Aucun changement du vérificateur ni revendication d’originalité. Prochain essai : estimer avant chronométrage si un flux non stratifié C4 avec arbres profonds présente assez de vrais noyaux pour départager l’effet de leur fréquence de celui des rejets bruts.

`cd research/code && timeout 60s python3 v19_prevalence.py`, 8,214 s. Code SHA-256 `c7506db00706f0d2809b97b1d572fc9bc2c6d70ef5556310f566fb8fc7a4bace`, agrégats `49f524212fc3c147d1bc472d5b16289da35a04ea0d00833bdddf768b57ca43fe`. Non-régression historique séparée `python3 test_v19_locality_l_plus_1.py`, PASS 325 468 comparaisons. Registre lu et SHA vérifié `184d8d9868ffb90a97c6f171693f3f54f5785d83`, capacité `existing_math_pilot` examinée, pertinente et exécutée via le banc existant, utile pour décider de conserver la référence. Aucun nouveau composant et coût payant nul.
