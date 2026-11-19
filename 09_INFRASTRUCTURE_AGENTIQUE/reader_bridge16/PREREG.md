# READER16 — préenregistrement du diagnostic de plafond (19/11/2026)

## Motivation et données gelées
Les runs Reader14 et Reader15 ont mesuré un classifieur 0,5B (abstention totale) et un 3B (4 vraies lignes selon une annotation auteur sur 5 sélectionnées), sans gain de 3B sur le témoin mécanique `first 3`. Le modèle ne peut sélectionner que parmi les lignes proposées par la baseline. **Question : quelle part de l'échec provient des paquets exclus et de la génération de candidats, indépendamment de la capacité du LLM ?**

Sources déjà vues — **post-hoc seulement**, pas un nouveau holdout :
- BR-R90-01 `478ca7c518ed1368a0bf35deb5f9be160bba581d`
- BR-R90-02 `0a9f6bab0b91a93f8fcc831c39a988171c169eb5`
- Références : `reader_bridge13/GOLD_PROVISIONAL.json`, statuts `AUTHOR_LABELS_UNREVIEWED_NOT_INDEPENDENT`.
- Base de la branche : code Reader15 de [PR #184](https://github.com/Abrasax63/Omega-pub/pull/184). Aucune modification de `main`, aucun nouveau LLM.

## Politiques de rappel candidates — figées avant code
A — **baseline actuelle** : `reader_bridge13.select_packets` puis `baseline` (lignes comportant `=` ou la formule fixe `est exactement uniforme`), puis `gate`.

B — **élargissement de lignes, paquets identiques** : même ensemble de paquets que A, mais toute ligne de 6–500 caractères (après `strip`) est proposée ; reconstruction de citation depuis le Git blob, rejet des contextes interdits par `gate`. Cette politique isole la perte due à l'heuristique `=`.

C — **élargissement de paquets et de lignes** : tous les paquets dont l'un des titres contient `énoncé` ou `enonce`, sans utiliser de référence de vérité, puis lignes de 6–500 caractères et même `gate`. Cette politique isole les pertes supplémentaires dues au sous-échantillonnage des paquets.

Aucun des trois générateurs ne lit les labels. Les annotations sont lues seulement après calcul des ensembles figés. Les propositions restent en quarantaine ; aucune certitude sémantique n'est attribuée.

## Mesures et règles d'interprétation
Pour chaque document et au total :
- nombre de lignes gold complètes (même celles non visibles dans le contexte Reader13) ;
- gold visibles dans les paquets sélectionnés Reader13 ;
- gold proposées par A, B, C ;
- total des lignes candidates admises et nombre d'autres lignes candidates, **pas des faux énoncés certifiés** ;
- plafonds théoriques à `k=3` : `min(3, gold_intersection_candidates)`, et rappel maximal par rapport au gold visible et au gold total ;
- couverture additionnelle et risque de dilution (taille du vivier de candidates) des stratégies B et C.

Tests : hachages Git, rejet des preuves et citations inventées par le gate, rejet de toute promotion, déterminisme, aucune modification des références ni du code de Reader13/14/15.

**Critère utile** : C couvre plus de gold que A sans certifier quoi que ce soit. Même si C couvre 100 % des sept lignes de référence, ce ne sera qu'un **plafond de récupération**, pas une performance du modèle. La vraie expérience suivante devra porter sur de nouveaux documents gelés avant l'inférence, avec annotations indépendantes, comparateurs à budget égal et métriques de fausses affirmations.

## Ce que le test ne démontre pas
Ni la véracité des théorèmes, ni la capacité d'Omega à les comprendre, ni une amélioration du modèle 3B, ni une capacité frontière. Tout résultat reste `POSTHOC_CANDIDATE_COVERAGE_AUDIT`.
