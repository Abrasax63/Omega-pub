# OBS-COL-12 — Garde contradictoire à accès boîte noire, avant admission d'un modèle

**Date : 16 novembre 2026. Statut : CALIBRATION VÉRIFIABLE SUR ERREURS CONNUES, PAS DE CERTIFICATION.**
Branche `experiment/obs-col12-blackbox-conformance-gate-2026-11-16`, empilée sur PR #114 ; `main` et CORE inchangés.

## Déjà étudié et différence exacte

- **#81** : laboratoire de construction et d'évaluation de vérificateurs ; pas le test prospectif d'un automate appris à partir de seules observations.
- **#76** : coût des stratégies exactes sous modèles et partitions finis spécifiés.
- **#114** : audit exact *post hoc* connaissant le graphe de l'automate cible. Résultat 17/20 modèles exactement équivalents et 3 réfutés (registre5, modèles `coverage_only`, `omega_candidate`, `KV`).

**La pièce nouvelle** de #12 n'est pas un énième oracle parfait : c'est un contrôle d'une hypothèse `L#` / `KV` gelée, par appels `reset` et `step` au simulateur cible **sans lire son graphe**, utilisant des bibliothèques classiques connues et un budget compté. Il fonctionne en module indépendant **opt-in** : aucun branchement automatique au cycle horaire, à `main` ou à une autorité de certification.

## Engagement, versions et séparation post hoc

1. [Pré-enregistrement](PREREG.md), commit `9b8c6a39e4f28a8e8e0e076d6ffbdbdb74ff6430`, avant le code de l'expérience. Il fige **600 resets**, **8 000 symboles d'action** maximum par vérification, et six modèles appris issus de #114.
2. [Amendement après le premier run](AMENDMENT_POST_RUN_MEMORY_ABLATION.md), commit `693cd8e6283c149f24d3526e0f1b96e2467373d4` : ajouter la comparaison `Wp_coverage_ranked` **sans mémoire**, pour savoir si la mémoire améliore réellement le classement des sondes au-delà de la couverture classique.
3. [Amendement post-run de reproductibilité](AMENDMENT_POST_RUN_PYTHON_HASH_SEED.md), commit `02eaf4588d4da0b7d0cf3610bca8d79812e17f42` : `PYTHONHASHSEED=0` dans la CI finale. Une variation de témoins Wp est apparue entre les runs historiques ; l'attribuer avec certitude au hachage serait injustifié.

Le terrain est constitué de **deux automates publics universitaires déjà étudiés** : `register3.dot` (8 états, 2 modèles corrects) et `register5.dot` (32 états, 1 modèle correct et 3 incorrects). **Ce n'est pas un nouveau holdout, ni une preuve de généralisation.** Les six hypothèses et leurs compteurs d'apprentissage sont rejoués à l'identique en comparaison avec [FROZEN_FIRST_RUN.json](../obs_col11/FROZEN_FIRST_RUN.json).

## Vérificateurs et accès

Chaque vérificateur reçoit une **nouvelle instance indépendante** du système cible à consulter ; il **ne reçoit pas** sa table de transition, les sorties du témoin déjà connu ou le contrôle exact de #114 :

- **W** : vrai `aalpy.oracles.WMethodEqOracle`, aucune imitation.
- **Wp** : vrai `aalpy.oracles.WpMethodEqOracle`, aucune imitation.
- **Wp couverture seule (post hoc)** : les deux générateurs de tests Wp *originaux* d'AALpy, permutés par `coverage_ranking(hypothese, ..., memory=False)` de #110.
- **Wp couverture + mémoire** : mêmes tests et même code de permutation, avec `memory=True` et les préfixes réellement mesurés pendant l'apprentissage ; vrai `planner.plan_mission` P1 appelé avant chaque reset. P1 **n'invente pas la sonde** et le classement est une heuristique classique déjà écrite.

Wp couverture seule appelle également P1 avant chaque reset, pour isoler son effet de celui du classement. Chaque catalogue et chaque permutation possèdent des empreintes SHA-256.

Les bibliothèques W/Wp supposent une borne sur le nombre d'états de la cible pour leurs garanties. Ici, faute de borne fiable, nous leur donnons `nombre d'états hypothèse + 1`. **Cette borne est insuffisante pour les hypothèses à 27 états lorsque la cible en possède 32**. Une absence de contre-exemple ne permet donc jamais de conclure à une équivalence.

Le graphe exact n'est consulté **qu'après** la mesure, pour vérifier qu'un témoin retourné constitue bien une contradiction. La décision `admission_verdict` impose :
- `REJECT_MODEL` uniquement pour au moins un témoin mesuré puis confirmé ;
- `DEFER_UNVERIFIED` dans tout autre cas (y compris épuisement de budget ou absence de témoin) ;
- **jamais d'acceptation/certification automatique** dans cette expérience.

## Résultats historiques, sans effacer les échecs

- [Premier run #43841235628 — SUCCESS](https://github.com/Abrasax63/Omega-pub/actions/runs/43841235628), 6 tests et 18 contrôles (W, Wp, Wp+mémoire) : 3 modèles incorrects détectés par les trois méthodes, aucune fausse réfutation sur les trois modèles corrects.
- [Run d'ablation #43841813740 — SUCCESS](https://github.com/Abrasax63/Omega-pub/actions/runs/43841813740), 7 tests et 24 contrôles : sur les trois modèles incorrects de register5, la couverture seule et couverture+mémoire détectent tous les témoins à très faible coût ; **aucun gain de mémoire** sur `coverage_only` et `omega_candidate`, léger effet sur KV.
- [Run avec graine de hachage fixée #43842089337 — SUCCESS](https://github.com/Abrasax63/Omega-pub/actions/runs/43842089337) : 7 tests, 24 contrôles, même conclusion, avec ordonnancement rendu plus reproductible.

| Modèle incorrect du registre5 | W original | Wp original* | Wp couverture seule | Wp couverture + mémoire |
|---|---:|---:|---:|---:|
| Couverture | 119 resets | 120 resets | **4 resets** | **4 resets** |
| Candidat Omega | 119 | 120 | **4** | **4** |
| KV | 209 | 111 | **8** | **7** |

*Wp original a montré une certaine variation du premier témoin et des coûts entre runs Python. Le tableau utilise le run `PYTHONHASHSEED=0` ; les anciens runs et leurs différences restent visibles.*

Sur register3, **aucun témoin** n'est trouvé pour les deux hypothèses, sur aucune des quatre politiques. Sur le modèle correct `register5/fixed`, les quatre vérificateurs atteignent 600 resets sans contre-exemple. **Ce sont des contrôles silencieux ou incomplets, jamais des certificats positifs.**

La nouvelle heuristique de couverture détecte le défaut avec 4/4/8 resets contre 120/120/111 pour Wp original, **sur trois erreurs déjà divulguées**. L'ablation montre que la plus grande partie de l'effet n'est **pas causée par la mémoire**. Sur les deux modèles provenant des politiques de couverture et d'Omega, `memory=True` ne modifie même pas le nombre de resets ; sur KV elle économise 1 reset et 12 symboles.

**Conclusion :** un garde falsificateur à budget borné peut être ajouté en amont d'une admission dans le banc expérimental, avec des témoins observables et un refus explicite de faux certificats. Son efficacité est prometteuse mais il reste **un assemblage de méthodes classiques**. Le contrôle de causalité ne fournit pas de plus-value intellectuelle propre à Omega.

## Reproduction et vérification

```sh
python -m pip install aalpy==2.0.0
python 02_MATHEMATIQUES/pilotes/obs_col11/fetch_fixtures.py "$PWD/obs_col12_sources"
OBS_COL12_SOURCES=obs_col12_sources python -m unittest discover -s 02_MATHEMATIQUES/pilotes/obs_col12 -p 'test_blackbox_gate.py' -v
python 02_MATHEMATIQUES/pilotes/obs_col12/blackbox_gate.py "$PWD/obs_col12_sources" > obs_col12_result.json
```

Le workflow `.github/workflows/obs-col12-conformance.yml` exécute le banc, contrôle la présence d'un témoin pour les modèles fautifs, la conservation des six hypothèses, les plafonds et l'absence de certification. JSON et journaux GitHub constituent les preuves.

## Prochaine vérification décisive

**Ne pas réutiliser register5 comme un nouveau holdout.** Prendre une cohorte externe différente, scellée *avant* le choix des heuristiques ; appliquer `coverage_only` et `memory` avec mêmes candidats Wp, mêmes plafonds et vrai P1 sur des machines nouvellement apprises ; mesurer taux de détection des erreurs, fausses alarmes, abstentions, resets, symboles et CPU **avec répétitions**. Une politique de mémoire ne mérite d'être conservée que si son ablation prouve une contribution au-delà de la couverture simple. En attendant, ne rien promouvoir dans `main` ni CORE.
