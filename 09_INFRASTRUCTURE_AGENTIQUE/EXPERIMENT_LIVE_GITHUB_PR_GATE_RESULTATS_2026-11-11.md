# P5 — Premier pilote à observations externes réelles : 12 PR GitHub

11 novembre 2026. **Statut : EMPIRIQUE LIMITÉ / comparaison de politiques de vérification sur données réelles, sans appel LLM ni correction humaine aveugle**.

## Gel préalable et traçabilité
- Pré-enregistrement et liste des 12 cas : `EXPERIMENT_LIVE_GITHUB_PR_GATE_PREREG_2026-11-11.md`.
- Commit de pré-enregistrement : `ace72167f2a024871b5e4fee062db359488b8099`, écrit avant l'observation des statuts et des chemins.
- Données brutes utiles, empreintes des branches consultées, durées de consultation : `prism/live_github_pr_gate_observations_2026-11-11.json` ; collecte enregistrée à 2026-11-11T10:39:31Z.
- Rejeu avec **l'implémentation réelle** de la politique Omega : `prism/test_live_github_pr_gate.py`, sous GitHub Actions une fois la CI passée.
- Sources : `get_pr_info`, `list_pr_changed_filenames`, puis second contrôle `fetch_pr` sur les métadonnées. Les trois sont des lectures GitHub, **pas des fournisseurs indépendants**.

## Résultats observés

| Bras | Réponses correctes /12 | Appels de source | Consigne |
|---|---:|---:|---|
| A : réponse sans outil, rejet conservateur | 11/12 | 0 | `reject` |
| B : plan fixe, toujours deux lectures | 12/12 | 24 | Lire statut ET fichiers |
| C : plan Omega conditionnel, au plus deux lectures | 12/12 | 17 | Lire statut ; si fusionné seulement, lire fichiers |

- 5 PR fusionnées parmi les 12 ; une seule répond à la conjonction « fusionnée et modifie un fichier de test ».
- Sur les 7 PR non fusionnées, Omega s'est arrêté après la lecture du statut. Il économise **7 consultations**, soit 7/24 ≈ 29,17 % des appels du plan fixe.
- Les 12 lectures B et C ont donné le même état `merged` et le même SHA de tête pour chaque PR. Une seconde récupération par `fetch_pr` a confirmé les 12 statuts de fusion.
- Aucun appel de modèle de langage, aucun outil de recherche scientifique, aucune donnée volontairement trompeuse. Le bras C n'a pas eu un taux d'exactitude supérieur au bras B ; l'écart concerne seulement le nombre de lectures effectuées.

### Durées mesurées : ne pas surinterpréter
L'instrumentation `Date.now()` entourait les appels du connecteur. La somme des intervalles observés vaut **21 567 ms** pour B et **13 757 ms** pour C. Les cas ont été exécutés par paquets concurrents : ces intervalles incluent orchestration et attente partagée, et ne représentent pas des latences API isolées comparables. **Aucun gain causal de temps n'est revendiqué** ; la métrique primaire validée est le nombre d'appels réellement effectués. Aucun coût monétaire, token, CPU ou énergie de modèle n'a été mesuré.

## Planification et falsifiabilité
Le modèle fourni à Omega est le produit de deux booléens théoriques : `merged` et `touched_tests`. Il connaît la logique de la question et les issues **possibles** des deux contrôles, mais pas la valeur des 12 PR. Chaque état abstrait reçoit un poids 1 ; les contrôles ont une pénalité fictive de 5 millièmes et un plafond total de 10 millièmes par branche. L'optimum théorique choisit le statut de fusion en premier, puis les fichiers uniquement si le statut est positif.

**Un résultat contradictoire qui réfuterait la conformité du pilote** : la politique Omega demande les fichiers d'une PR non fusionnée, produit `accept` sans les deux observations, diffère du statut vérifié, ou dépasse deux appels sur un cas. Ces propriétés sont vérifiées dans les tests.

## Limites déterminantes
1. Le jeu n'est **pas aveugle** : les titres ont été consultés pendant la sélection, puis les règles ont été figées avant la collecte des réponses.
2. Le critère « fichiers de test » est syntaxique ; son interprétation n'est pas une évaluation de la qualité des tests.
3. Les PR peuvent être modifiées après la collecte. Les SHA de tête et la date de capture sont conservés ; les valeurs ne sont pas une vérité éternelle.
4. Un seul cas positif : **puissance discriminante insuffisante** pour évaluer la qualité du raisonnement, la calibration des sources ou la robustesse.
5. Le choix conditionnel ne prouve pas une intelligence générale. Le plan optimisé partage le modèle d'observations pré-déclaré ; les valeurs réelles sont acquises par les appels mais la structure logique est fournie.
6. La vérification indépendante correspond ici à un **chemin de récupération et à un évaluateur distincts**, mais tous les faits proviennent du même fournisseur GitHub. Aucun correcteur humain externe n'est intervenu.
7. La comparaison contre un plan fixe non conditionnel est une ablation utile, **pas une comparaison contre un agent concurrent adaptatif fort**.

## Verrou suivant réellement nécessaire
Pré-enregistrer sur une nouvelle source un corpus équilibré, contrôles positifs et négatifs, avec **plusieurs tâches hétérogènes** et des observations imparfaites. Exécuter ensuite des modèles réellement isolés sous mêmes plafonds : direct, rôle fixe, plan adaptatif, plan adaptatif avec provenance vérifiée. Mesurer réponses finales, abstentions, latence/tool-use réels et coûts fournisseur. Une double correction humaine aveugle externe doit précéder le décodage des bras. Sans ces conditions, ne pas revendiquer de supériorité d'Omega.

**Aucun transfert en CORE, aucune fusion vers `main`, aucun changement du registre SQLite.**
