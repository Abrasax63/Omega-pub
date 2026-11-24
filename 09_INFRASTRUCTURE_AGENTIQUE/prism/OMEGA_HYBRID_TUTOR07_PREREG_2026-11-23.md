# OMEGA-ATOMIC-TUTOR-07 — apprentissage procédural sous supervision exacte

**Préenregistré le 23 novembre 2026, avant tout appel au modèle pour TUTOR-07.**
**État au préenregistrement : code et tests proposés, expérience réelle NON exécutée.**

La [PR #250](https://github.com/Abrasax63/Omega-pub/pull/250) reste expérimentale et en brouillon. Ni \`main\`, ni les poids du modèle, ni les automatisations existantes ne sont modifiés.

## Problème après PROCEDURE-06

[PROCEDURE-06, run #45279117106](https://github.com/Abrasax63/Omega-pub/actions/runs/45279117106) : 24/24 réponses ont dit « faux », 4/8 classifications binaires justes, 1/8 certificat mathématique accepté pour le bras procédural. Le taux de réussite booléen reflète un **classifieur constant**, sans discrimination des cas positifs. Les prompts plus longs ne suffisent pas.

**Hypothèse testée ici :** au lieu d'une définition verbale ou d'une obligation de preuve sans apprentissage préalable, est-ce qu'une **correction exacte des étapes atomiques de preuve** sur un domaine d'entraînement distinct aide Qwen à construire de lui-même un certificat correct sur de nouvelles relations ?

Il s'agit **d'apprentissage en contexte seulement**, avec le modèle Qwen2.5-3B-Instruct Q4_K_M gelé. Même un score positif ne démontrerait ni nouveaux poids, ni découverte autonome générale, ni apprentissage durable hors contexte. Les preuves certifient une réponse sur un graphe fini, pas la compréhension de la théorie par le LLM.

## Le « professeur » et le protocole de séparation

L'outil \`omega_hybrid_tutor07.py\` génère **deux exercices d'entraînement à QUATRE sommets**, jamais utilisés comme test scientifique final :

- **TRAIN_NEG** : relation réflexive, symétrique, non transitive, avec la chaîne a–b–c ; le modèle doit produire **lui-même** un triple \`(x,y,z)\` et trois bits \`xy,yz,xz\` indiquant si les arêtes existent. Le professeur extérieur calcule la vérité des trois prémisses et fournit un témoin exact **seulement après l'essai**.
- **TRAIN_POS** : relation d'équivalence non triviale composée des blocs {a,b} et {c,d}. Le modèle tente de la reconnaître et d'énumérer une partition. Le professeur calcule une partition exhaustive, **seulement après l'essai**.

Un retour corrigé est délibérément **de l'enseignement supervisé** ; il ne fournit jamais de réponse du jeu de test. Les tentatives, les erreurs, les retours, les règles formulées et tous les tokens sont conservés.

## Conditions comparées, même poids

- **D** : aucun exercice préparatoire, pas de règle ajoutée.
- **G** : deux tentatives sur les mêmes cas de formation, mais uniquement un accusé de réception **générique**, sans révéler ni classement ni prémisses ; le modèle synthétise ensuite lui-même une \`rule\`.
- **T** : mêmes deux tentatives, puis **correction atomique externe** de chaque relation (exactitude du certificat proposé, vrai statut de la relation, trois bits et témoin pour le négatif, partition exhaustive pour le positif). Le modèle synthétise lui-même une \`rule\`.

Chaque tâche d'entraînement est d'abord **tentée par le modèle** ; le professeur ne propose pas directement une réponse à une question non encore tentée. Pour G et T : 2 appels de tentative + 1 appel de synthèse, donc 3 appels par condition. **Total maximal : 30 appels** (6 pour entraînement et synthèse, 8 questions × 3 conditions). Les notes sont **du modèle**, non du programme.

## Évaluation aveugle — six sommets, un nouveau domaine

- L'ensemble de test comprend **8 graphes à six sommets** \`u0…u5\`, quatre équivalences de types de partition différents et quatre graphes réflexifs et symétriques mais **non transitifs** (chemin P3, chemin P4, étoile K1,3, cycle C4, complétés d'isolés).
- Les huit graphes ont des **classes d'isomorphisme distinctes sous les 720 permutations de six sommets**. Les sommets sont réétiquetés par SHA-256 et l'ordre de question est gelé par la graine \`omega-tutor07-sealed-six-node-v1\`.
- Les **deux oracles**, \`check_axioms\` (énumération des axiomes) et \`independent_oracle\` (cliques des composantes connexes) doivent être d'accord sur chaque cas, et sur un échantillon supplémentaire de 1 024 graphes indépendants des huit tâches.
- Les prompts contiennent **uniquement les sommets et arêtes**, puis éventuellement la *règle auto-générée* par G ou T. Les corrections et réponses de test sont conservées exclusivement dans \`oracle_only.json\`, jamais transmises au modèle.
- Chaque bras reçoit le **même contrat de sortie** : JSON \`holds, failed_axioms, certificate\`, avec une preuve négative \`kind=missing_transitive_edge\`, \`triple\` et les trois bits \`xy,yz,xz\`, ou une preuve positive \`kind=partition\`, \`blocks\`. Les vérificateurs rejettent les fausses prémisses et les partitions incomplètes même lorsque l'étiquette binaire est correcte.
- Les trois appels de chaque cas sont **stateless**, avec six ordres de bras prédéterminés et comptage du **vrai tokeniseur** du moteur local. Les prompts d'évaluation sont équilibrés à ±5 % de tokens d'entrée, mesurés **avant** et **après** les appels. Les tokens générés et temps CPU sont rapportés séparément.

## Seuil préfixé pour un signal de transfert **ponctuel en contexte**

Un signal exploratoire favorable n'est accordé que si :
1. le bras **T fournit ≥6/8 certificats ET classifications entièrement corrects** ;
2. les **positifs et négatifs atteignent chacun ≥3/4** dans T, afin d'exclure une stratégie constante « toujours faux » ;
3. T dépasse **D et G d'au moins deux réussites complètes** ;
4. T a **0 JSON invalide** et les budgets de prompts respectent ±5 %.

Sinon : \`REGISTERED_CONTEXT_GAIN_NOT_OBSERVED\` (si budget comparable) ou \`INDETERMINATE_BUDGET\`. L'effet reste descriptif, sans significativité générale sur n=8.

**Coût total non égal par conception :** D réalise seulement 8 appels ; G et T en réalisent 11 chacun, car les deux derniers « apprennent » une règle. Tous les coûts, entraînement inclus, doivent être publiés. Même un éventuel gain en T ne devra **pas** être présenté comme une victoire causale à budget total égal sur D.

## Garde-fous et verdicts

- Empreintes cryptographiques des deux manifestes de test écrites **avant** la première génération.
- Toutes les réponses brutes et prompts hachés sont enregistrés, y compris les erreurs.
- Des contrôles sur 1 024 relations à six sommets, tests de falsification de prémisses, de partitions fausses, de fuite d'oracle, de déséquilibre des coûts, de fuite de statut et de prédictions invalides doivent passer.
- Workflow GitHub Actions **à déclenchement unique sur création de son propre fichier** ; pas de cron, pas d'API externe de modèle payante, même poids SHA-256 \`9c9f56a391a3abbd5b89d0245bf6106081bcc3173119d4229235dd9d23253f94\` et \`llama.cpp b12633\` sur CPU.
- Si la CI, le modèle, les téléchargements ou la représentation structurée échouent : aucun score scientifique inventé, **archiver et classer le défaut technique**, sans rejouer le holdout pour l'améliorer.
- Ne promouvoir aucune fiche de compétence et ne lancer aucun entraînement des poids sur un signal ponctuel.

La **prochaine vérification décisive après le run** est une réanalyse des réponses brutes et des règles produites, puis éventuellement une réplication indépendante sur une cohorte nouvelle et un autre domaine de représentation. Si l'enseignement atomique ne donne aucun gain, tester la production d'un petit programme explicite d'énumération de prémisses avec contrôles exécutables, au lieu de multiplier les prompts de correction.
