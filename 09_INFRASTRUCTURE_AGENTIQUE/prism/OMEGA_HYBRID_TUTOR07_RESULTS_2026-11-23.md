# OMEGA-ATOMIC-TUTOR-07 — résultat réel, audit et correction méthodologique

**23 novembre 2026 — rapport après exécution réelle.**
**Statut expérimental : \`REGISTERED_CONTEXT_GAIN_NOT_OBSERVED\`; audit indépendant concluant à un résultat négatif, mais à une isolation causale imparfaite des retours pédagogiques.**
**Pas d'entraînement des poids, aucune nouvelle compétence scientifique certifiée.**

## 1. Données d'origine et preuves

- [GitHub Actions #45290017753](https://github.com/Abrasax63/Omega-pub/actions/runs/45290017753) : précontrôle réussi, expérimentation CPU Qwen2.5-3B-Instruct Q4_K_M terminée avec succès **technique** ; **30 générations effectives**, soit 4 essais d'entraînement, 2 synthèses de règle, 24 évaluations (8 tâches × 3 bras). Aucune API de modèle payante, aucune modification de poids.
- [Artefact brut GitHub #14872619853](https://github.com/Abrasax63/Omega-pub/actions/runs/45290017753/artifacts/14872619853), contenant \`training_inputs.json\`, \`model_inputs.json\`, \`oracle_only.json\`, \`report.json\`, empreinte du GGUF, version du moteur et journaux.
- SHA-256 du ZIP réellement téléchargé : \`a575b0a56aa2cf5a25ad953a2c9c656ae5b61d59ba849911e063a897896acae5\` ; SHA-256 de \`report.json\` : \`6933434e98e22c8622ea8bfac61864a3bf494fe0acb1381b2ddf456876da3fff\`.
- SHA-256 du manifeste de questions gelé : \`01a0224715e0345eb2132a3c65c8afc1fb8f330b9a15f71f3b6802a4627c91ea\` ; manifeste d'oracle : \`54fa6ce7411351b798c409b0791d6db56845c7d57bbfd414ddcb65a8df5299fc\`. L'audit a retrouvé **les mêmes deux empreintes que celles du rapport pré-inférence**.
- Préenregistrement : [OMEGA_HYBRID_TUTOR07_PREREG_2026-11-23.md](https://github.com/Abrasax63/Omega-pub/blob/experiment/omega-hybrid-learning-gates-2026-11-23/09_INFRASTRUCTURE_AGENTIQUE/prism/OMEGA_HYBRID_TUTOR07_PREREG_2026-11-23.md). **8 relations à 6 sommets**, 4 équivalences positives et 4 relations réflexives symétriques non transitives, pairwise non isomorphes. Les sources des corrections du holdout ont été séparées du modèle.

## 2. Scores réels, critère fixé à l'avance

| Métrique | D : direct | G : retour générique | T : professeur atomique |
|---|---:|---:|---:|
| Décisions booléennes correctes / 8 | **4** | **3** | **4** |
| Décision **et tous les axiomes** corrects / 8 | **4** | **3** | **4** |
| Certificats mathématiques complets valides / 8 | **0** | **0** | **0** |
| Réponses entièrement certifiées / 8 | **0** | **0** | **0** |
| Réponses JSON au contrat invalide | 0 | **1** | 0 |
| Tokens d'entrée pendant l'évaluation | 2 656 | 2 648 | 2 672 |
| Tokens de sortie pendant l'évaluation | 424 | 460 | 424 |
| Secondes CPU d'inférence pour l'évaluation | 72,908 | 67,509 | 64,946 |

Le seuil préenregistré exigeait pour T ≥6/8 preuves et classements entièrement justes, au moins 3/4 sur chaque signe, gain ≥2 par rapport à D et G, zéro JSON invalide et budgets d'évaluation comparables ±5 %. Le seuil n'est **pas atteint**. Les budgets d'entrée de l'évaluation sont comparables ; les budgets totaux, **non** :

| Bras | Total d'appels | Tokens d'entrée **entraînement inclus** | Tokens de sortie **entraînement inclus** |
|---|---:|---:|---:|
| D | 8 | 2 656 | 424 |
| G | 11 | 3 461 | 629 |
| T | 11 | 3 662 | 566 |

Sur ce pilote exploratoire de 8 cas, il n'y a **aucune réussite avec preuve complète**, même en T malgré un coût supérieur. La différence entre méthodes n'est **pas identifiable causalement avec rigueur**, notamment parce que le bras D n'a pas de coût de formation et pour la fuite méthodologique identifiée ci-dessous.

## 3. Pourquoi 0 certificat ne veut PAS dire 0 chaîne mathématique pertinente

Un second calcul des fichiers bruts, indépendant des compteurs du rapport et basé sur les composantes-cliques des relations, confirme :

- **D et T disent « faux » sur les 8 cas** ; **G fournit 7 réponses négatives conformes et une sortie négative non conforme**. Aucun bras ne reconnaît un seul des **4 cas positifs**.
- Les certificats négatifs de **D, G et T omettent tous le champ \`premises\`**, censé contenir les trois booléens de présence des arêtes. Sous le contrat gelé, aucun n'est admissible.
- En ignorant **uniquement à titre de diagnostic** le champ manquant, les triples proposés par le modèle sont de vrais témoins de non-transitivité sur **2 cas pour D, 3 pour G et 2 pour T** (sur les 4 négatifs). **Ces succès partiels ne remplacent pas les 0 preuves complètes**, et ils ne doivent pas être promus comme corrects sous les règles originales.
- Le professeur avait pourtant montré, **après deux essais échoués de T**, un vrai témoin \`(a,b,c)\` avec \`xy=true, yz=true, xz=false\` et une vraie partition positive \`{a,b},{c,d}\`. Sa règle de synthèse verbale évoque une partition positive et des triples de transitivité, mais les productions suivantes n'exécutent ni la reconnaissance du positif ni la trace atomique.
- Sur les huit cas, T obtient 4/8 pour le booléen **uniquement parce qu'il répond « faux » systématiquement** et que 4/8 graphes sont négatifs. On ne peut pas interpréter ces 4 bonnes étiquettes comme capacité de discrimination.

**Diagnostic borné** : à cette échelle et avec ces consignes, nous avons testé une progression « tentative → feedback → règle → nouveaux graphes » ; elle n'a **pas** converti les règles en une preuve systématique. Le protocole souffre en partie d'un défaut de sortie (omission des trois bits) et en partie de classification (toujours « faux ») ; ces deux problèmes doivent rester séparés.

## 4. Faille méthodologique découverte après l'essai, corrigée seulement pour l'avenir

**Un vrai défaut de construction a été détecté en audit :** le texte envoyé au générateur de note dans les deux bras G/T contenait l'objet d'entraînement complet avec des IDs **\`TRAIN_NEG\`** et **\`TRAIN_POS\`**, qui indiquaient la vérité même dans le bras G, censé recevoir uniquement un feedback générique. Par ailleurs, le prompt de synthèse mentionnait explicitement la méthode attendue « partition positive et triple négatif », ce qui guidait les deux bras **même sans enseignement détaillé**.

**Conséquence :** le résultat descriptif négatif reste observé et archivé, mais la comparaison G versus T n'isole **pas proprement** l'effet du feedback atomique. Ne pas parler de réfutation générale de l'enseignement par preuves. Cette limite n'invalide pas les 0 certificats complets ni les 24 réponses réellement produites, seulement leur interprétation comme un essai causal parfait.

**Correctif minimal après l'expérience** sur la PR #250 :
1. **Retirer les IDs de vérité** de l'historique transmis au synthétiseur ; les conserver seulement dans le journal d'audit.
2. **Neutraliser le prompt de synthèse**, qui ne fournit plus lui-même « partition positive » ni « triple négatif ».
3. Ajouter une assertion de non-régression sur les prompts du faux modèle ; mettre à jour les doubles de test de la CI, après les premières régressions de contrôle dues à l'ancien libellé.

La cohorte TUTOR-07 de **six sommets est désormais exposée**. **Aucun nouvel appel sur ces huit cas avec le correctif ne devra être présenté comme une réplication indépendante.** Le workflow one-shot initial a été exécuté sur le code de commit \`109a5f9924dc833d20e02e07ae8b56faf2221b3e\` ; les corrections ultérieures ne réécrivent ni ses prompts ni ses sorties d'origine.

[Dernière CI de correction #45291174421](https://github.com/Abrasax63/Omega-pub/actions/runs/45291174421) : **90/90 tests logiciels** sur la branche corrigée. Les premiers runs après changement de prompt avaient échoué parce que le faux modèle des tests reconnaissait l'ancienne formulation ; les deux doubles ont été corrigés, et la CI finale est verte. Aucun modèle réel n'a été relancé.

## 5. Décision scientifique et nouveau verrou

**Ne pas augmenter aveuglément la difficulté ni lancer SFT/LoRA sur ces données**. Le modèle ne semble pas exécuter fidèlement une définition universelle même lorsqu'il peut la formuler, et le feedback atomique ne suffit pas à lui imposer une vérification exhaustive. Avant d'inférer un « manque de compréhension », distinguer par tests minimaux :

- **A. Lecture des arêtes :** sur des exercices **neufs et de petite taille**, le modèle donne-t-il correctement les valeurs atomiques de \`xRy\`, \`yRz\`, \`xRz\` pour un triple fixé ? Si non, corriger d'abord l'interface de représentation ou confier ces bits à un lecteur exact.
- **B. Règle locale :** sachant trois bits **vérifiés**, peut-il identifier correctement une violation de transitivité ? Si oui, le goulet principal se situe dans la lecture des graphes ou le parcours, et non dans l'implication logique.
- **C. Complétude du parcours :** peut-il produire **tous** les triples candidats, ou une partition exhaustive, sans manquer des cas ? Vérifier un certificat **positif** indépendamment de la détection des contre-exemples négatifs.
- **D. Assemblage et transfert :** comparer une procédure réellement exécutée par un programme déterministe à la procédure verbale du modèle, sur un nouveau domaine d'évaluation ; afficher séparément performances du **système assisté** et du **modèle seul**.

La prochaine expérience devrait être **plus élémentaire**, pas plus ambitieuse en taille : diagnostiquer la lecture de trois arêtes, puis la validité d'une implication locale. Si les compétences élémentaires sont acquises avec une interface plus simple et tiennent sur des graphes neufs, seulement alors réétendre à la preuve de transitivité complète.

**Verdict final de cette itération : progrès de l'instrumentation et du diagnostic, pas de gain autonome prouvé sur Omega.** PR DRAFT ; \`main\` inchangée.
