# OMEGA-COUNTEREXAMPLE-COVER-03

**Protocole préenregistré [commit 2306aca](https://github.com/Abrasax63/Omega-pub/commit/2306aca73c7839c11f340f0102bda1f87548db71)** avant tout changement de politique, score ou exécution. Basé sur le correctif fail-closed et les vérifications de [PR #137](https://github.com/Abrasax63/Omega-pub/pull/137), sans toucher à cette PR ni à main.

## Ce qui change réellement

Le système à apprendre est une machine de Mealy **entièrement cachée** derrière l'interface réinitialisable `MeteredBlackBox`. Les quatre bras exécutent le **même AALpy 1.6.2 L*** ; seule la sélection des mots de test d'équivalence approchée varie.

Tous les **mots EQ ont exactement dix symboles**, pour éviter le confondant constaté dans la [PR #136](https://github.com/Abrasax63/Omega-pub/pull/136), où les mots Omega étaient moins coûteux surtout parce qu'ils étaient plus courts.

| Bras | Stratégie de contre-exemples |
|---|---|
| RANDOM_LEN10 | 10 symboles aléatoires |
| FIXED_LEN10 | compteur lexicographique cyclique sur 1024 mots |
| OLD_OMEGA_LEN10 | ancienne heuristique de transitions peu testées, prolongée/tronquée à dix symboles |
| COVER_DISTINGUISH_LEN10 | chemins d'accès de l'hypothèse L* + transition candidate + suffixe distinguant des états candidats, visités dans un ordre couvrant les transitions |

**Un mot choisi ne doit jamais consulter le vrai automate caché.** L'algorithme L* est inchangé; la couverture et les suffixes ressemblent à des techniques établies de test de conformance, et ne sont pas présentés comme inventions d'Omega.

Le vrai système est accessible à l'**évaluateur indépendant après apprentissage** ; il calcule la vraie équivalence comportementale en explorant le produit d'états, et renvoie un contre-exemple exact si le modèle proposé est faux. Les EQ de L* ne consultent que les sorties réelles des mots **facturés**, avec un plafond **32 mots par candidat** et arrêt fail-closed si le budget ne peut payer la requête suivante.

## Nouvelles cohortes et budgets contrôlés

Douze nouvelles machines, **quatre par taille 4, 5, 6**, n'ayant aucune signature canonique égale à celles des **1112 machines #127–#135**, des neuf cas #136 ni des trois cas stress #137. Tirages seed **36104 / 36105 / 36106**, transitions et sorties aléatoires, filtrées **uniquement** par état initial donnant accès à tous les états et distinction comportementale de chaque paire d'états. Les rejets structurels sont comptés; aucun filtre fondé sur une réussite de l'apprenant.

Plafonds de **900** (secondaire) et **1 800** (primaire) symboles effectivement interrogés **par machine et bras**. Le même seed de choix de requête est maintenu **entre plafonds** pour un bras et une machine donnés; cette fois, le plafond peut être étudié sans changer aussi le tirage. 128 mots de test inédits longueur 12–20 par machine, séparés de l'apprentissage, avec exclusion documentée des collisions exactes.

Les dépenses réelles peuvent différer à cause de l'effet des contre-exemples sur la construction L*. Comptabiliser les MQ/EQ, les interruptions, les mots d'origine tronqués ou complétés et les transitions candidates couvertes.

## Verdict principal fixé avant les tests

Au plafond **1 800**, pour déclarer `DESCRIPTIVE_COVER_GAIN`, la couverture doit produire **strictement plus de modèles équivalents exacts que chacun des trois comparateurs** sur les douze machines **et** avoir une précision moyenne sur mots réservés au moins égale à la meilleure référence. Tout autre résultat : `NO_DEMONSTRATED_COVER_GAIN`. CI verte ne signifie pas gain positif ; les négatifs restent archivés.

## Reproduction

```sh
python -m pip install aalpy==1.6.2
python -m unittest discover -s experiments/omega-cover-03 -p test_cover.py -v
python experiments/omega-cover-03/cover_lab.py --output /tmp/omega-cover-03-report.json
```

GitHub Actions impose **15 tests** puis **96 apprentissages** (12 machines × quatre bras × deux plafonds). Publie tous les Q/R d'apprentissage, réponses réelles, mesures et preuves `report.json`, `report.sha256`, `summary.jsonl`.

**Portée limitée :** 12 machines synthétiques fortement accessibles et distinguables, pas une preuve de supériorité générale, pas un L* nouveau, pas d'apprentissage de LLM ou d'auto-programmation de code. PR **DRAFT** empilée sur #137, aucun merge ni modification de `main`, aucune API payante.
