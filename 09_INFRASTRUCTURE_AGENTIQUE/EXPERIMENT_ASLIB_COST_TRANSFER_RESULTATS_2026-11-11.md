# OMEGA-ASLIB-002 — Transfert coût-sensible sur MAXSAT-WPMS-2016 : verdict contrôlé

**11 novembre 2026 — EMPIRIQUE REPRODUCTIBLE sur mesures historiques externes + CALCUL EXACT sur procédures de sélection. Verdict de supériorité adaptative : NON DÉMONTRÉ.**

## Question et engagements avant examen des scores

Le programme Omega, après l'échec du pont à risque 0–1 sur MAXSAT-PMS-2016 (#37), peut-il améliorer les décisions en choisissant directement les solveurs sur leur **PAR10 attendu** et en anticipant deux divisions de l'espace des caractéristiques ?

- **Pré-enregistrement avant lecture des scores WPMS :** commit `30331b960d91d23642628dee8713e09a10f9b30c`, fichier `09_INFRASTRUCTURE_AGENTIQUE/EXPERIMENT_ASLIB_COST_TRANSFER_PREREG_2026-11-11.md`.
- Source amont `coseal/aslib_data` figée au commit `551b22beef8df17de59286b4822ef720e0aa4d6f` ; répertoire `MAXSAT-WPMS-2016`. Les fichiers `algorithm_runs.arff`, `feature_values.arff`, `cv.arff`, `feature_costs.arff` et `description.txt` sont lus par GitHub Actions et **contrôlés via empreintes Git blob**, sans recopier le dataset dans Omega. Attribution et licence restent celles du dépôt COSEAL.
- **630 instances, 18 solveurs, 37 caractéristiques, 11 340 mesures historiques** (4 775 `ok`, 6 565 `timeout`), coût de `base` disponible pour toutes les instances. **Dix plis officiels, 63 instances chacun**, nine-to-one CV ; chaque scénario et ses étiquettes restent publics : le test est **externe et distinct de PMS, mais ni aveugle ni prospectif au sens temporel**.
- PAR10 : pénalité 18 000 pour timeout, seuil original 1 800 secondes. Tous les bras avec caractéristiques utilisent les 37 variables et payent **le même coût réel d'acquisition de l'étape `base`**, ajouté à leur score. SBS et VBS ne payent pas cette étape.
- L'arbre `OMEGA_cost_lookahead2` est **un adaptateur expérimental de sélection d'algorithmes coût-sensible**, pas le composant historique `optimize_policy` et ne constitue pas une preuve d'émergence stratégique. Les arbres ont les mêmes seuils médianes (TRAIN uniquement), même profondeur maximale 2 et mêmes données d'entraînement. Le critère d'entraînement est la **somme des PAR10** des feuilles. L'anticipation examine plusieurs premières divisions possibles, chacune suivie de ses meilleures secondes divisions. Aucune valeur de runtime d'un pli test n'est utilisée pour construire son arbre.

## Comparaison finale vérifiée

| Modèle | PAR10 moyen + coût caractéristiques (secondes pénalisées ; plus faible meilleur) | Résolues/630 | Taux |
|---|---:|---:|---:|
| SBS, meilleur solveur unique TRAIN | 3 892,782984 | 498 | 79,05 % |
| KNN-5, 37 caractéristiques | **2 975,554635** | **529** | **83,97 %** |
| KNN-15, 37 caractéristiques | 3 071,103095 | 526 | 83,49 % |
| TREE-greedy1, profondeur 1 | 3 387,380556 | 515 | 81,75 % |
| TREE-greedy2, profondeur 2 | **3 263,893429** | 519 | 82,38 % |
| OMEGA-cost-lookahead2, profondeur 2 | **3 265,585349** | 519 | 82,38 % |
| VBS, oracle rétrospectif **NON ADMISSIBLE** | 2 629,888016 | 541 | 85,87 % |

- L'arbre anticipatif est **627,198 secondes PAR10 en moyenne meilleur que SBS** (environ 16,1 %), mais **290,031 secondes de PAR10 plus mauvais que KNN-5** (environ 9,7 %), avec **10 instances résolues de moins**.
- Face au concurrent à la même famille, profondeur et information, `TREE-greedy2`, l'anticipation est au final **1,691921 seconde PAR10 moins bonne par instance**, avec exactement **519 résolutions** pour chacun. Cet écart de 1,69 sur une moyenne de 3264 est très faible et ne constitue pas une preuve statistique de différence ; il est **négatif par rapport à l'hypothèse directionnelle de gain de la prévision**.
- Sur **630 décisions appariées**, l'anticipation est meilleure que l'arbre glouton pour 94 instances, pire pour 55 et strictement égale pour 481 ; elle sélectionne un solveur différent pour 167 instances. Les grosses pénalités de timeout peuvent dominer le score moyen. Par pli, les effets sont hétérogènes et ne constituent pas dix expériences indépendantes.
- KNN-5 bat SBS sur la moyenne PAR10 **dans chacun des dix plis**, résultat descriptif seulement. L'anticipation fait moins bien que KNN-5 en moyenne dans huit des dix plis, mieux dans deux. Les valeurs de chaque pli et les prédictions par cas figurent dans l'artefact.
- **Dans chacun des dix plis**, l'objectif d'entraînement anticipatif est `<=` celui de l'arbre glouton, vérifié par CI. L'inversion du classement en test montre qu'un avantage d'optimisation empirique sur TRAIN n'entraîne pas automatiquement un meilleur transfert.

## Reproduction et voies indépendantes

- [GitHub Actions WPMS #43070449506](https://github.com/Abrasax63/Omega-pub/actions/runs/43070449506) — **SUCCESS**, cinq types de contrôle : tests Python hors connexion, téléchargement des données SHA-vérifiées, entraînement CV dix plis, recalcul indépendant JS et audit des écarts appariés.
- [Tests du Prisme #43070449500](https://github.com/Abrasax63/Omega-pub/actions/runs/43070449500) — **SUCCESS**, 187 tests du Prisme, plus tests MCP/RCE et index.
- [Artefact complet du registre d'instances et politiques](https://github.com/Abrasax63/Omega-pub/actions/runs/43070449506/artifacts/13876524563).
- `aslib_wpms_independent_crosscheck.mjs` reproduit **indépendamment** SBS, KNN-5, KNN-15 et VBS sur les mêmes enregistrements sources, avec les moyennes à (10^{-5}) près et les nombres résolus identiques.
- `aslib_wpms_tree_independent.mjs`, **seconde implémentation algorithmique en JavaScript**, recalcule **30 objectifs d'entraînement** (3 arbres × 10 plis) et retrouve exactement **1 890 choix de solveurs** (3 arbres × 630 instances) issus de l'implémentation Python. Elle vérifie aussi les empreintes Git des entrées. Cela ne rend pas les mesures upstream indépendantes : deux implémentations partagent les mêmes données de référence.
- `aslib_wpms_paired_audit.py` vérifie l'identité du coût des caractéristiques à travers tous les bras utilisant des variables, les 630 jointures de résultats et l'optimalité de la perte TRAIN du lookahead sur son domaine de recherche.
- Un contre-test synthétique XOR de quatre cas démontre simplement que le lookahead **peut** battre un choix glouton sur les données où l'interaction de deux attributs est essentielle : coût train 4 contre 22. Ce contre-test n'est **pas** une mesure de supériorité sur WPMS.

## Interprétation, réfutation et limites

1. **Fait reproductible :** le sélecteur à recherche à deux étapes optimise mieux (ou aussi bien) l'objectif de train, mais sur WPMS n'améliore pas la performance externe face à l'arbre glouton de même capacité, et reste nettement derrière KNN-5.
2. **Pas une généralisation de négation absolue :** nous n'avons testé qu'un scénario externe de transfert après un scénario PMS de développement antérieur. L'algorithme choisi appartient à une famille déjà connue d'arbres supervisés ; une mémoire scientifique certifiée, un portefeuille d'outils de preuve et une capacité d'invention de méthodes n'ont **pas** été testés ici.
3. **PAR10 est fortement sensible aux timeouts** : la moyenne peut être dominée par de grosses pénalités, et un gain moyen infinitésimal n'indique pas une supériorité robuste sans dispersion, appariement et scénario supplémentaire. La proportion résolue demeure une métrique indispensable.
4. **Baseline forte :** les KNN-5/15 sont reproductibles et d'information comparable mais ne représentent **pas** tout l'état de l'art (AutoFolio, SATzilla, Hydra, sélection algorithmique coût-sensible plus élaborée). Aucune affirmation `Omega supérieur aux outils existants` n'est autorisée.
5. **Épistémologie :** CALCUL EXACT sur la fonction de perte du modèle train et les tests synthétiques ; EMPIRIQUE REPRODUCTIBLE sur les résultats issus des mesures historiques de solveurs ; INDÉTERMINÉ sur avantage général du planificateur scientifique et sa capacité à raisonner stratégiquement face à des preuves contradictoires.
6. **Pas de coûts trompeurs :** les frais du bloc complet `base` sont inclus pour tout modèle exploitant les caractéristiques ; il n'a pas été inventé de coûts de récupération par attribut, de tokens ni de nouveaux temps réseau. Les solveurs n'ont pas été réexécutés.

## Décision stratégique après deux résultats externes

**Ne pas promouvoir une couche de planification purement plus profonde comme propriété nécessaire d'Omega.** Deux scenarios externes (PMS et WPMS) ont maintenant montré qu'une représentation et une fonction de sélection simples peuvent être plus efficaces que nos ponts.

À présent, le verrou le plus discriminant n'est pas de trouver une autre variante de l'arbre qui batte KNN après ajustement. Tester plutôt une capacité que la sélection supervisée standard **ne capture pas entièrement** : la mémoire de preuves et la vérification de provenance des résultats, avec des informations nouvelles qui peuvent invalider une ancienne décision. Pré-enregistrer des problèmes naturels indépendants de l'expérimentateur, mesurer le coût d'acquisition d'une preuve et les erreurs confiantes. Comparer Omega à un processus simple avec la **même bibliothèque**, la même origine de preuves et des contrôles de qualité égaux.

La PR reste expérimentale en DRAFT, empilée sur #37 ; **pas de fusion dans main, aucune mutation de SQLite ou promotion CORE**.

## Sources et bibliographie
- [COSEAL ASlib, dépôt des données et fichiers MAXSAT-WPMS-2016](https://github.com/coseal/aslib_data/tree/551b22beef8df17de59286b4822ef720e0aa4d6f/MAXSAT-WPMS-2016).
- Bischl et al., [*ASlib: A Benchmark Library for Algorithm Selection*](https://www.sciencedirect.com/science/article/pii/S0004370216300388), *Artificial Intelligence* 237 (2016), 41–58.
- [ASlib, spécification](https://github.com/coseal/aslib-spec/blob/master/format.md).
