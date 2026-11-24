# OMEGA-ATOM-08 — résultat réel, audit indépendant et décision

**24 novembre 2026. Statut scientifique : FOUNDATIONAL_GATE_NOT_PASSED.**
Ce document conserve un résultat négatif et ne constitue ni l'entraînement de poids ni la preuve d'une compétence nouvelle.

## Provenance primaire

- [Run réel GitHub #45344587826](https://github.com/Abrasax63/Omega-pub/actions/runs/45344587826) : précontrôle et exécution CPU **SUCCESS technique**, Qwen2.5-3B-Instruct Q4_K_M, SHA des poids fixé dans le workflow, **32 générations effectives**, zéro API de modèle payante, aucune modification de poids.
- [Artefact brut #14897696796](https://github.com/Abrasax63/Omega-pub/actions/runs/45344587826/artifacts/14897696796) : questions et corrigés séparés, réponses brutes et coûts. SHA-256 de la **copie ZIP inspectée** : \`2122e6949d89ef07d5c44b8448cdef346f9f0ba3eaae918fce2834adf69a9b00\`. SHA-256 du \`report.json\` : \`fb904bd058b595436bd6b93be2bb44545a92f7bd786e6421f8ad1dfdaeefbb21\`.
- Empreintes **internes, gelées avant la première réponse** : manifeste de questions \`fd08af7ace1d1422917a98cc90aa2d1c6c0f111429695796ef721c4b8ef951bc\`, réponses oracle \`cd539d7f8396c8649899d338b3844cdc5e63382a0da04c06af556b136a90510c\`.
- [Protocole préenregistré ATOM-08](https://github.com/Abrasax63/Omega-pub/blob/experiment/omega-hybrid-learning-gates-2026-11-23/09_INFRASTRUCTURE_AGENTIQUE/prism/OMEGA_HYBRID_ATOM08_PREREG_2026-11-24.md), source \`omega_hybrid_atom08.py\` ; double vérification \`omega_hybrid_atom08_audit.py\`.
- **Audit externe au processus GitHub**, en relisant les octets de l'artefact avec un autre script Python : les 24 réponses de lecture ont été confrontées directement à la présence des paires dans \`edges\` ; les huit réponses logiques ont été recalculées par \`xy and yz and not xz\` ; IDs, SHA bruts, scores et seuils concordent. Résultat : \`INDEPENDENT_ATOM08_AUDIT_PASSED_DESCRIPTIVE_ONLY\`. Rapport d'audit de cette relecture : \`omega_atom08_audit_independant.json\` (créé dans la conversation).

## Mesures réelles, sans réparation des JSON

| Sous-compétence | Triple complet exact | Bits exacts | JSON invalides | Tokens d'entrée | Tokens de sortie | Secondes CPU |
|---|---:|---:|---:|---:|---:|---:|
| Lire 12 graphes en **liste d'arêtes** | **2/12** | 22/36 | 0 | 2 004 | 240 | 38,284 |
| Lire les mêmes graphes en **matrice** | **3/12** | 23/36 | 0 | 2 352 | 242 | 39,282 |
| 8 lignes de la **table de vérité**, bits fournis | **7/8** | — | 0 | 848 | 56 | 10,778 |

Seuils de passage fixés avant le run : lecture LIST ≥10/12, lecture MATRIX ≥10/12, logique **8/8**, aucun JSON invalide. **Aucun des trois seuils n'est atteint.** La différence MATRIX-LIST de +1/12 ne prouve pas de supériorité de représentation ; les prompts diffèrent en longueur et la cohorte est très petite.

### Analyse des sorties brutes

- **LIST** : \`(xy,yz,xz)=(vrai,vrai,faux)\` sur **8/12** graphes, et \`(vrai,faux,faux)\` sur les quatre autres.
- **MATRIX** : \`(vrai,vrai,faux)\` sur **10/12** graphes ; les deux autres réponses sont \`(vrai,faux,vrai)\` et \`(vrai,vrai,vrai)\`.
- **LOGIC** : \`{"violates":false}\` sur **les huit motifs de bits**. Il manque donc le seul véritable contre-exemple \`xy=true,yz=true,xz=false\`. Le score 7/8 est celui d'un **classifieur constant « aucune violation »**, pas l'exécution correcte de la règle.

Les trois sorties sont valides en **syntaxe** : il n'y a pas d'échec du parseur ni de l'oracle sur ce run. Le modèle **ne lit pas les arêtes de manière fiable** et **échoue sur le cas crucial** de l'implication locale, même lorsque les bits et la règle sont donnés dans le prompt.

Ces observations sont **bornées à Qwen3B, aux consignes et au petit jeu du 24 novembre** ; elles ne prouvent ni un plafond général du modèle ni l'impossibilité de développer une compétence par formation.

## Décision architecturale après falsification

**Ne pas accroître la taille des graphes, ne pas répéter ces mêmes 12+8 cas et ne pas lancer immédiatement un entraînement SFT/LoRA sur des fiches LLM non vérifiées.** La suite prioritaire change de niveau :

1. **Introduire une interface exacte de lecture de relation** réutilisant \`omega_hybrid_tutor07.atomic_membership\` : pour un graphe et un triple donné par Omega, calculer sans ambiguïté les trois bits et leur provenance, sans croire une valeur générée par le modèle.
2. **Réifier la règle logique par un programme exécutable de trois booléens**, capable de trouver une violation \`xy∧yz∧¬xz\`. Étiqueter cette aide « capacité du système », **pas** « apprentissage des poids du LLM ».
3. **Pour développer une réelle compétence du modèle**, préparer des exercices de lecture et d'implication distincts et corrigés automatiquement, puis mesurer leur transfert sur une **nouvelle cohorte aveugle**, avec une comparaison direct/exact-tool/entraînement. Ne pas utiliser ces cas déjà exposés comme nouvelle évaluation.
4. Inclure la **preuve positive** : après recherche exhaustive, produire une partition contrôlée et distinguer « aucun témoin trouvé » d'une preuve complète. Publier les budgets totaux et les erreurs silencieuses.

Le gain instrumental de l'architecture est réel : les vérificateurs ont détecté les faux raisonnements. **Aucun nouveau savoir du modèle n'est démontré.** PR #250 reste DRAFT, \`main\` inchangée.
