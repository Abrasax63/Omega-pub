# P5-FALSIFY-05 — trois vérificateurs imparfaits **réels**, acquisition sous budget et contrôle Bellman empirique

**12 novembre 2026 — GEL AVANT LECTURE DES TROIS FICHIERS LFS DE RÉSULTATS ET AVANT LE PREMIER CALCUL SUR LA COHORTE.** Ceci prolonge [PR #67](https://github.com/Abrasax63/Omega-pub/pull/67), où les vérificateurs sont simulés, en utilisant des **résultats de modèles réellement produits par des auteurs indépendants du projet Omega**.

## Portée, absence de faux holdout

Les résultats ont été publiés par [ClaimDB, Theologitis et al., ACL 2026](https://aclanthology.org/2026.acl-long.1589/). Les vérificateurs sont des **modèles de langage réels**, mais leurs étiquettes de réponse ne constituent **pas** des preuves SQL exactes ou relues indépendamment. Les trois traces sont issues d'un **unique dépôt de benchmark**, dont les annotations sont publiques et les modèles potentiellement corrélés. **Pas de nouvel appel LLM, pas de nouveau holdout aveugle, pas de fournisseur de vérité indépendant**. En revanche, les erreurs et désaccords des vérificateurs ne sont **pas simulés**.

### Cinq fichiers source fixes (Git LFS réels, pas les pointeurs)

Tous au commit ClaimDB `e06c3a22cc14a8ef6858bb5d40bca7925241b98d` :
- `final-benchmark/test-public.jsonl`, 1000 annotations publiques, SHA-256 `b87d7062307cfcf5ae862bf03bd7e82f7123ff39cf0b69d3dc5cc25caaaea810`;
- `experiments/public/no_tools/gpt-5-mini.jsonl`, 1000 prédictions initiales sans SQL, SHA-256 `552531cba335298816a998f7a2b6fb548d9cd0eb7f9b47e5d1272809620a9aa6`;
- `experiments/public/gpt-5-nano.jsonl`, sorties GPT-5-nano avec outils SQL, LFS SHA-256 `c41127fc6a5d1105f582ec876dccec2c685ecd3a01a651ac4033d9c6058816c0`, **14 046 314 octets** ;
- `experiments/public/gemini-2.5-flash.jsonl`, sorties Gemini-2.5-Flash avec outils, LFS SHA-256 `8c2107a3f9cea8bfd37a8305441541c3566627640f47f7d63d3bdd93a3fc5b4c`, **8 019 644 octets** ;
- `experiments/public/claude-haiku-4-5.jsonl`, sorties Claude-Haiku-4.5 avec outils, LFS SHA-256 `2bf7a999dd853a16e5aa40e6fbf65879952d076fbdfa02968c3e80e4f3fa2130`, **20 487 460 octets**.

**Interdiction d'ouvrir ou de noter les réponses de test avant la définition des politiques.** Vérification du SHA, count 1000, ID commun et labels `ENTAILED/CONTRADICTED/NOT ENOUGH INFO` obligatoire, sinon fail-closed. Si le LFS retourne un pointeur ou un fichier corrompu, échec; pas de remplacement post-hoc.

## Partition de calibration, inédite au sens logiciel mais pas scientifique

Échantillon externe des **1000 cas**, regrouper par `db_name`, ordonner les noms des bases par SHA-256(`"P5-FALSIFY05-DB-GROUP|"+db_name`) croissant, **60 % des bases** en calibration (premiers `round(0.60 * number_of_db_names)`), autres bases réservées à l'évaluation. **Aucune base de données partagée entre calibration et évaluation**, aucun regroupement selon gold, qualité, désaccord ou résultat du modèle. Les modèles, heuristiques et coûts sont gelés ici. L'annotation du test n'est révélée qu'à l'évaluateur final, jamais à la politique.

**Information initiale :** texte de l'affirmation, `extra_info`, base source, réponse sans outil de GPT-5-mini (si valide). Le texte sert seulement à la famille contextuelle heuristique `numeric` si chiffre arabe ou indicateurs « exactly / at least / more than / average / percentage / how many / number of » ; sinon `other`. Aucun label source, verdict des trois outils ni indicatrice de correction dans cette entrée.

**Information après achat :** `reported_verdict` du vérificateur réel et `tool_output_count` issu de la trace originale. `gated` ne conserve le verdict que si `tool_output_count > 0` ; sinon il observe `NO_SQL_OUTPUT`. Ce filtre est **une convention de provenance**, pas une preuve que le SQL est mathématiquement correct. Les éventuelles traces de tokens/temps sont résumées en métadonnées observées, sans leur attribuer de prix rétrospectif.

## Coûts, ressources et décision

- Deux achats **au maximum** parmi trois vérificateurs, coût fictif conventionnel choisi **avant l'analyse**, `nano=0.08`, `gemini=0.12`, `claude=0.16` unités d'utilité ; budget **0.24** par affirmation. Ces coûts **NE SONT PAS** les coûts API réels de production, ni des durées CPU mesurées à cette date. Les résultats historiques étaient déjà calculés par les auteurs. Ne pas dire « à coût monétaire égal ».
- Choix final `ENTAILED / CONTRADICTED / NOT ENOUGH INFO / ABSTAIN`. Récompense +1 si publication égale l'annotation, −2 sinon, +0.05 si abstention, moins **tous** les achats. L'abstention ne signifie pas le label `NOT ENOUGH INFO`.
- Les modèles historiques donnent un outcome potentiel pour chaque outil et chaque claim, donc on peut simuler l'achat séquentiel **sans appel caché au gold**. Les données futures de ce claim sont révélées **uniquement après** décision d'achat.
- Dépendance entre vérificateurs explicitement modélisée par un **tableau JOINT** de comptages calibration `P(gold, outil1, outil2, outil3 | base_verdict, context)` avec pseudocompte Dirichlet **alpha=0.10 par cellule**. Pour le canal de preuve `gated`, chaque résultat d'outil appartient à 4 classes (3 labels ou NO_SQL_OUTPUT); pour raw, 3. Le modèle n'impose **pas** l'indépendance conditionnelle des trois réponses. Priorisation de la version contextuelle seulement si `n_calibration_context >= 80`, sinon repli sur globale. Les priors de calibration sont accessibles à tous les témoins forts.

## Politiques à comparer

- `no_tool` : décision bayésienne terminale optimisant les 4 réponses depuis la réponse initiale.
- `fixed_cheapest_two` : achète d'abord nano, puis gemini, dans le budget, ensuite décide par la même postérieure (canal gated).
- `bayes_global_exact` : programmation dynamique Bellman exacte horizon 2, coût/budget, tableau JOINT global calibration, et **canal gated**.
- `bayes_context_exact` : même méthode avec conditionnement contextuel quand il y a ≥80 calibrations, mêmes observations gated.
- `bayes_raw_exact` : témoin fort supplémentaire, même optimiseur avec toutes les sorties raw même si aucun outil SQL n'a été journalisé.
- `omega_like_no_memory` : heuristique préfixée achetant nano puis éventuellement gemini selon un test de désaccord avec la réponse sans outil, sans les probabilités historiques contextuelles ; posterior de référence global pour la décision finale. Il s'agit d'une **ablation proxy**, pas du P1/P2/P3 réel.
- `omega_like_no_observability` : politique myope d'amélioration d'utilité espérée avec tableau JOINT contextuel, mais observation raw même sans trace d'outil.
- `omega_like_full` : même heuristique myope avec tableau contextuel et canal gated ; consigne un certificat `same ClaimDB ground-truth source; different model organisations, no independently replayed SQL`. **Ce n'est pas le vrai planificateur P1 exécutant la mémoire RCE.**
- `hindsight_oracle` : connaît les vrais labels et tous les résultats possibles avant d'agir, pour référence **non déployable**, sans le faire passer pour un algorithme scientifique.

**Équité importante :** le témoin Bellman contextuel `bayes_context_exact` dispose du **même** historique et des **mêmes** observations gated qu'`omega_like_full`. Bellman optimise l'utilité espérée sous le modèle joint estimé ; toute supériorité ex ante d'Omega sous **ce** modèle serait une anomalie mathématique. Sur le jeu test, des erreurs de calibration peuvent inverser l'ordre; cela ne prouve pas une supériorité générale. Les 3 modèles sont faillibles et le benchmark peut être non discriminant ; signaler tout score négatif honnêtement.

## Métriques et falsification

- Primaire descriptive : utilité moyenne test appariée `U(omega_like_full)-U(bayes_context_exact)`, effectifs de vérifications, erreurs, abstentions, taux de verdict publiés, différence des actions, détérioration par source.
- Secondaire : `omega_like_full` contre `omega_like_no_memory` et `omega_like_no_observability`, `bayes_raw_exact`, fixed baseline; **ces ablations d'heuristiques ne sont pas des ablations de l'orchestrateur Omega réel**.
- Intervalles de confiance par bootstrap **sur les groupes de bases de données**, 2000 tirages **seed=20261112** sur le score apparié, avec description si la population n'est pas assez grande; ne pas en faire une preuve indépendante de nouveaux labels. Aucune optimisation des seuils à partir du test.
- Test de non-régression des coûts / fuite gold / duplicate claim_id / même accès au calibrateur, et cas où un outil manque de trace authentique. Toute validation dont les 3 sources ne sont pas présentes = `NOT_RUN`, pas une simulation substituée.

## Sorties et gouvernance

Script Python standard sans clés/API, GitHub Actions effectue checkout LFS des 5 fichiers à source fixe et conserve **uniquement le JSON agrégé, les trajectoires et empreintes**, pas l'ensemble des 45 MB de traces originales. Aucun accès aux bases BIRD, aucune preuve SQL recalculée, aucune revue humaine indépendante dans cette PR.

**Ce pilote est empirique sur de véritables erreurs de trois modèles différents, mais NON aveugle, avec coûts fictifs et une heuristique Omega-like expérimentale. Ne pas revendiquer « Omega réel bat Bellman » même en cas de score favorable.** Toujours DRAFT, base PR #67, `main` inchangée, aucune promotion CORE.
