# OBS-COL-08 — Choix d'expériences à budget borné et comparateurs classiques

**Date :** 2026-11-15. **Statut :** CALCUL EXACT, SYNTHÉTIQUE, expérimental.
**Pré-enregistrement :** [PREREG_OBS_COL08.md](PREREG_OBS_COL08.md),
commit `1bb77250eef4eb2bb43b4ed3e0e941c32d290f8f`, créé AVANT le code.
**Branche de travail :** `experiment/obs-col08-budgeted-query-choice-2026-11-15`, base PR #91 ; aucune écriture directe sur `main`.

## Question réellement testée

Les travaux OBS-COL-07 produisaient 255 consultations par système et utilisaient P1
pour enregistrer les requêtes décidées par un apprentissage de type L*.
Ce pilote teste l'**activation réelle du choix des requêtes** dans la
chaîne **PR #23 (optimiseur exact) → Omega P1 (pont de planification)**.

Point crucial : **c'est le code d'optimisation PR23 qui choisit la sonde,
pas P1 isolément.** Le code du pilote ne crée pas de nouvel algorithme
d'apprentissage d'automates et ne bat pas L*, TTT ou L#.

## Modèles, accès et contrôle de fuite

- Catalogue fixe de **40 automates de Moore** synthétiques distincts
  sur les réponses à des mots de longueur <=7, générés avec la graine
  `20261115`. L'algorithme connaît les hypothèses candidates et
  leurs prédictions, mais jamais la vraie identité de la cible.
- **8 cibles connues pré-engagées** par indices `0,3,7,12,19,27,35,39`.
  **1 cible hors catalogue** : DELAY9_OOD, qui ne produit la sortie 1
  qu'après une histoire suffisamment longue.
- Au plus **6 requêtes distinctes** et **18 symboles d'action cumulés**
  par bras et par cible, avec reset exact et réponses binaires sans bruit.
- Le même générateur de **8 sondes présélectionnées** par réduction de
  Gini, longueur et ordre lexical alimente tous les bras. Cette
  construction exploite **les modèles proposés**, jamais les réponses
  futures réelles ; ce catalogue restreint fait partie du modèle imposé.
- La mesure réservée porte sur **1 792 mots de longueur 8 à 10**
  par cible, soit 16 128 observations réservées par bras ; elle n'entre
  ni dans le choix des sondes ni dans le filtrage des candidats.
- Les identifiants de mission P1 ont un nom neutre
  (`OBS-COL-08-UNLABELED-<iteration>`) : aucun index de monde caché.
- Évaluateur et hypothèses proviennent néanmoins du même banc synthétique
  conçu par le laboratoire : **pas de holdout externe réellement aveugle**.

## Stratégies

| Bras | Ce qui décide | Ce qui est réellement comparé |
|---|---|---|
| Omega | `plan_with_variable_horizon`, PR23 exact et vrai P1 | Optimisation à deux consultations conditionnelles sur huit sondes, plus pont P1 |
| Classique exact | `optimize_policy` PR23 sans P1 | Exactement la même optimisation classique |
| Greedy | Réduction de Gini par coût | Une seule étape ; sous le même plafond |
| Lexical | Premier mot lexical dans les huit sondes disponibles | Politique simple, également avec même plafond |

La perte de PR23 est contrôlée par une **autre énumération exhaustive
à deux étapes** héritée d'OBS-COL-04. Ce contrôle ne constitue pas
une validation extérieure du générateur ni un apprentissage TTT.

Les budgets sont des **plafonds identiques** et non une obligation
de dépenser exactement autant de symboles à chaque bras. Les coûts
d'exécution CPU de l'optimiseur et de P1 ne sont **pas** compris dans
les seuls compteurs de requêtes / symboles.

## Résultats vérifiés

[Premier run CI #43727604217](https://github.com/Abrasax63/Omega-pub/actions/runs/43727604217)
— **10/10 tests réussis**, neuf cibles, quatre bras, aucune API ni LLM externe.

[Run de correction de statut et d'attribution du choix #43727824992](https://github.com/Abrasax63/Omega-pub/actions/runs/43727824992)
— tests de non-régression réussis après ajout de l'avertissement
`OUT_OF_HORIZON_WARNING` lorsque les données réservées contredisent
la prédiction (même si un seul modèle survit à l'entraînement).

| Bras | Requêtes (9 cibles) | Symboles | Erreurs / 16 128 réservées |
|---|---:|---:|---:|
| Omega PR23 + P1 | 47 | 93 | 67 |
| Classique exact | 47 | 93 | 67 |
| Greedy | 47 | 93 | 67 |
| Lexical | 44 | 156 | 976 |

Sur les huit cibles du catalogue, Omega/PR23, classique exact et
greedy obtiennent **8 × 1 792 prédictions correctes** et identifient
chaque candidat dans cet espace. Sur DELAY9_OOD, ils prédisent
une autre machine après leurs observations admissibles et commettent
**67 erreurs** sur les données réservées ; la version finale émet
**OUT_OF_HORIZON_WARNING** au lieu d'un certificat de validité.

Le bras lexical présente davantage d'erreurs et dépense plus de symboles
dans le protocole **conçu par nous**. Ce n'est pas une preuve que la
stratégie Omega dépasse L*, TTT, L#, une stratégie gloutonne forte ou
l'optimiseur exact : **gain spécifique à Omega = NON DÉMONTRÉ**.

### Compétence fonctionnelle acquise

À la différence d'OBS-COL-07, le module PR23 de la chaîne Omega
**choisit une requête** selon les modèles candidats survivants et
les plafonds de coût ; l'oracle fournit ensuite une vraie observation
qui modifie les candidats et l'expérience suivante. Cela réalise la
**boucle décision–observation–révision**, mais dans un catalogue fermé.

P1 reste une couche de routage explicable. L'algorithme économique
est classique ; les huit sondes et les hypothèses lui sont fournies.

## Reproduction

~~~sh
python -m unittest discover -s 02_MATHEMATIQUES/pilotes/obs_col08 -p 'test_obs_col08.py' -v
python 02_MATHEMATIQUES/pilotes/obs_col08/obs_col08.py > obs_col08_result.json
~~~

## Verrou suivant, sans nouvelle PR automatique

Pour chercher un apport **scientifique et causal propre à Omega**,
confronter une politique de choix de sondes réellement nouvelle
à plusieurs comparateurs forts : L#, TTT/LearnLib, recherche
d'identification par séparateurs adaptatifs et tests de conformité.
Utiliser des systèmes externes au générateur du développement,
masquer la vérité terrain, compter les symboles, requêtes **et CPU**,
et publier un verdict même négatif.

**Conserver la PR en DRAFT** : ne pas fusionner, ne pas modifier
`main`, CORE, mémoire certifiée ou les anciens résultats.
