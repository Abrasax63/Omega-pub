# P5-ADAPT-02 — résultats de calibration, validation et conservation des observations

**12 novembre 2026 — statut : CALCUL REPRODUCTIBLE / GAIN ADAPTATIF PROPRE NON DÉMONTRÉ / SIMULATIONS UNIQUEMENT.**

## Provenance

- [Pré-enregistrement avant le code](EXPERIMENT_P5_ADAPT02_PREREG_2026-11-12.md), commit `dfaf638ff56a91671fb70ba95ebd49fe5a01a23a`.
- [GitHub Actions #43194323286 — SUCCESS](https://github.com/Abrasax63/Omega-pub/actions/runs/43194323286) : 10 tests de non-fuite, calibration séparée, révision conditionnelle et conservation du journal réussis ; simulation et archive complètes.
- [Archive JSON brute, 2048 trajectoires de politiques](https://github.com/Abrasax63/Omega-pub/actions/runs/43194323286/artifacts/13931219469) — rétention GitHub limitée.
- 128 épisodes de calibration (32 graines × 4 régimes) ; **256 épisodes de test distincts** (64 nouvelles graines × 4 régimes), **2 048 exécutions de politique** et 180 décisions par exécution = **368 640 décisions simulées de test**.
- Monde : même générateur public que P5-ADAPT-01. **0 modèle de langage, 0 OpenAI API, aucune dépense API, aucune donnée privée, aucun calcul sur téléphone**.
- Ce découpage est une séparation **par graine**, non une validation externe : le générateur et les mondes étaient connus avant le test. Le P1 original ne contient ni apprentissage ni détecteur ; `omega_gated` est une nouvelle **extension expérimentale**.

## Calibration exécutée sans consulter le test

Seuils prédéfinis `0,375`, `0,50`, `0,625` et `0,75`. Avec la règle du pré-enregistrement (maximum 0,5 alarme stationnaire/épisode, puis plus faible regret moyen sur les trois mondes changeants), **le seuil 0,75 a été choisi**.

| Seuil | Alarmes stationnaires / épisode de calibration | Regret moyen calibration des 3 mondes changeants |
|---|---:|---:|
| 0,375 | 0,969 | 53,464 |
| 0,50 | 0,219 | 50,779 |
| 0,625 | 0,125 | 47,199 |
| **0,75 retenu** | **0,031** | **45,246** |

Aucune information des graines de test 100–163 n'a été utilisée pour choisir le seuil. Cette optimisation sur le générateur connu n'est pas une preuve de généralisation.

## Résultat primaire sur les 64 nouvelles graines par régime

**Pseudo-regret dynamique moyen : plus faible = meilleur.**

| Monde | Omega validé | SW-UCB (témoin principal préfixé) | Meilleur témoin classique a posteriori |
|---|---:|---:|---:|
| Stable | 49,173 | 49,173 | UCB stationnaire **22,856** |
| Ruptures brusques | **41,718** | 41,930 | Vérifier toujours **16,800** |
| Récurrences | 52,862 | **51,284** | UCB stationnaire **44,354** |
| Graduel | 45,010 | **44,864** | Vérifier toujours **1,097** |

Contraste apparié `Omega - SW-UCB` :

- Stable : **0,000** (0 victoire, 64 égalités, 0 défaite).
- Brusque : **−0,212** (8 victoires, 49 égalités, 7 défaites).
- Récurrent : **+1,578** (6 victoires, 49 égalités, 9 défaites).
- Graduel : **+0,146** (0 victoire, 61 égalités, 3 défaites).

Les écarts sont petits et **l'extension ne satisfait pas le critère pré-enregistré** d'amélioration sur les trois mondes changeants sans perte en stationnaire. Aucune preuve de gain adaptatif propre à Omega, même dans ce simulateur.

## Diagnostic des alarmes et de la validation avant adoption

| Monde | Alarmes Omega (64 épisodes) | Promotions | Propositions rejetées |
|---|---:|---:|---:|
| Stable | **0** | 0 | 0 |
| Brusque | 23 | 6 | 16 |
| Récurrent | 20 | 3 | 14 |
| Graduel | 4 | 2 | 0 |

**Succès local de contrôle :** zéro fausse alarme observée sur les 64 épisodes stationnaires de test, malgré les 90 alarmes sur 32 épisodes dans le *précédent protocole* (seuils et population différents : ne pas les comparer comme un essai apparié).

**Coût important : le détecteur est devenu peu sensible**. Sur les changements cachés, seuls **5 changements sur 128** (3,9 %) en monde brusque et **15 sur 192** (7,8 %) en monde récurrent ont été suivis d'une alarme sous 30 décisions. Les délais moyens sur les événements effectivement détectés sont 20,8 et 13,3 décisions. Pour le monde graduel, il n'existe pas de point unique de rupture ; ce taux n'est donc pas défini.

Le « rollback » est désormais **un refus de promotion avant adoption**, et non une suppression rétroactive des observations. Les 180 récompenses de chaque épisode restent dans l'archive append-only ; les tests valident ce comportement. Ce progrès d'intégrité ne se traduit **pas encore par un gain d'utilité**.

## Ablations et témoins

| Monde | Omega validé | Sans validation (adoption immédiate) | Mémoire courte |
|---|---:|---:|---:|
| Stable | 49,173 | 49,173 | 49,173 |
| Brusque | 41,718 | 42,853 | **41,313** |
| Récurrent | 52,862 | 53,848 | **52,465** |
| Graduel | 45,010 | **44,714** | 45,010 |

La validation semble améliorer ce candidat face à l'adoption immédiate en monde brusque et récurrent, mais l'approche **à mémoire courte fait légèrement mieux** que la mémoire longue dans ces deux mondes ; la validation dégrade légèrement le monde graduel. Aucun effet robuste propre à la mémoire n'est démontré. **SW-UCB et UCB stationnaire restent des témoins essentiels**.

## Décision scientifique

- **VALIDÉ logiciel :** protocole indépendant des graines de test pendant la calibration ; journal immuable ; refus conditionnel sans effacer les observations ; tests d'absence d'accès à l'oracle.
- **OBSERVÉ :** suppression des fausses alarmes sur les 64 épisodes stationnaires ; mais pertes majeures de rappel des ruptures.
- **RÉFUTÉ dans ces simulations :** l'objectif pré-enregistré de battre le témoin SW-UCB dans les trois mondes changeants.
- **INDÉTERMINÉ hors simulation :** valeur sur de véritables erreurs de modèle, vraies preuves, mémoire scientifique, ressources et contextes non stationnaires réels.

**Ne pas fusionner la couche adaptative dans `main` ou P1.** Conserver cette expérience comme un résultat négatif documenté, distinct des PR #47–51. Prochaine hypothèse : détection multi-échelle ou budget d'exploration explicite avec une meilleure mesure du compromis faux positifs / détection, puis confrontation à des retours authentiques **avant** tout ajustement sur un nouvel ensemble d'évaluation.
