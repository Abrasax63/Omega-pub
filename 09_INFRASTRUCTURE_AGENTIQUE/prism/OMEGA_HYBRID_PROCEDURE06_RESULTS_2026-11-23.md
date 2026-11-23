# OMEGA-PROCEDURE-06 — résultats réels et audit indépendant (23 novembre 2026)

**STATUT : EXPÉRIENCE EXÉCUTÉE ; CRITÈRE DE GAIN PRÉENREGISTRÉ NON ATTEINT.**
**Aucune nouvelle compétence, aucune mise à jour des poids et aucun entraînement autonome démontrés.**

## Sources inspectées et empreintes

- [Workflow GitHub réel #45279117106](https://github.com/Abrasax63/Omega-pub/actions/runs/45279117106) — deux jobs SUCCESS, pré-contrôle + **24 appels CPU effectifs** sur Qwen2.5-3B-Instruct Q4_K_M, vérification du SHA des poids, **aucune API de modèle payante**.
- [Artefact brut #14869256476](https://github.com/Abrasax63/Omega-pub/actions/runs/45279117106/artifacts/14869256476), contenant \`model_inputs.json\`, \`oracle_only.json\`, \`report.json\`, \`model.sha256\`, \`llama-version.txt\`, \`summary.log\` et \`server.log\`. Empreinte SHA-256 du **ZIP téléchargé** : \`c28b53603adfe4fbc6a2f5ac3f6f2060940dc47e7cf4a5c245f357b87fd62ae5\`.
- SHA-256 de **\`report.json\`** : \`e15c9469c785acc16a44a6bdf4a7979afe64283913c32157f5807d0b3e7d6ab7\`.
- Empreintes du protocole, gelées dans le journal **avant** l'inférence : questions \`158011147a8c231a2b078399353148b1532c590140d51939b9a6835024a47414\` ; corrigés \`054b1d29256d465452504fc41a5ee2d485901d2aedddbaa89450d2c011161f85\`.
- [Préenregistrement](https://github.com/Abrasax63/Omega-pub/blob/experiment/omega-hybrid-learning-gates-2026-11-23/09_INFRASTRUCTURE_AGENTIQUE/prism/OMEGA_HYBRID_PROCEDURE06_PREREG_2026-11-23.md) : 8 relations **à cinq sommets**, quatre positives et quatre négatives, non isomorphes, trois bras D/R/P, seuil préfixé.
- **Audit indépendant réellement exécuté**, depuis le ZIP lu en dehors de la CI et sans interroger le LLM : recalcul des empreintes, des huit vérités par l'algorithme des composantes-cliques, des **24 réponses brutes**, de la correction des axiomes, de la validité des certificats et des comptes de tokens. Statut \`INDEPENDENT_AUDIT_PASSED_DESCRIPTIVE_ONLY\`. Cette deuxième voie ne vérifie pas le préentraînement de Qwen ni la représentativité statistique.

## Résultats du modèle, n = 8

| Mesure | D : Direct | R : règle verbale | P : certificat exigé |
|---|---:|---:|---:|
| Verdict vrai/faux correct | 4/8 | 4/8 | 4/8 |
| Verdict et **tous** les axiomes corrects | **0/8** | **4/8** | **4/8** |
| Certificat mathématique exact | Non demandé | Non demandé | **1/8** |
| Certificats invalides | — | — | **7/8** |
| JSON invalide | 0 | 0 | 0 |
| Tokens de prompt réellement consommés | 2528 | 2536 | 2520 |
| Tokens produits | 148 | 124 | **428** |
| Secondes d'inférence mesurées | 56,747 | 52,702 | **81,620** |

Les budgets d'entrée de chaque triple étaient comparables à ±5 % (rapport : \`model_prompt_cost_balanced=true\` et \`actual_input_budget_comparable=true\`). Le bras P demande néanmoins un certificat plus long : ses **sorties sont 2,89 fois** plus longues que D en nombre de tokens, et son inférence mesurée environ **1,44 fois** plus lente. Le budget TOTAL de tokens/temps n'est donc **pas** égal. Les résultats sont exploratoires, pas une estimation causale générale.

**Verdict gelé : \`PRE_REGISTERED_GAIN_NOT_OBSERVED\`.** Le seuil d'admission était P≥6/8 classifications complètes, ≥6/8 certificats, P−D≥2, P−R≥2, aucun JSON invalide et budgets comparables. P ne remplit **ni la précision ni la preuve** ; il égalise R et ne dispose que d'un certificat valide.

## Révélation principale dans les 24 sorties

**Les trois bras ont classé LES HUIT relations comme \`holds=false\`.** Tous les positifs (4/4) ont été rejetés par D, R et P, et tous les négatifs (4/4) ont été reconnus dans leur réponse binaire. Le 4/8 binaire reflète donc uniquement une **stratégie constante « toujours négatif »**, aucun pouvoir discriminant constaté sur ces huit cas.

- D : dans ses huit réponses, le modèle énumère presque toujours des défauts de symétrie et de transitivité, alors que les cas sont **tous réflexifs et symétriques** par construction. Cela explique **0/8** au score complet, malgré 4/8 au booléen.
- R : la règle verbale amène le modèle à étiqueter les négatifs avec \`failed_axioms=["transitive"]\` de manière plus exacte (**4/8** au score complet). Mais il continue à rejeter **tous les cas positifs**.
- P : même comportement au verdict : huit « faux », quatre listes d'axiomes correctes ; il fournit un certificat sur chacun. **Un seul témoin est mathématiquement valide** : le 5e cas (négatif) avec le triple \`(v1,v2,v3)\`. Il échoue à justifier les trois autres négatifs et invente quatre violations pour des relations pourtant transitives.
- Exemples de fausses preuves que l'oracle bloque : 1er cas négatif \`(v1,v2,v3)\` **n'est pas** une violation valide dans ce graphe ; 3e cas positif \`(v0,v1,v0)\` **ne peut pas** être une violation sur cette relation réflexive et symétrique. Les cas effectivement observés sont conservés comme tests de **non-régression** \`test_omega_hybrid_procedure06_real.py\` ; ces cas sont à présent **exposés** et ne peuvent pas servir de nouvelle cohorte aveugle.

**Ceci ne prouve pas que le modèle est incapable de comprendre la transitivité en général.** Cela établit plus étroitement que, dans ce protocole préenregistré et sur huit relations nouvelles, l'instruction de produire une procédure **n'a pas généré une compétence opérationnelle fiable**, alors que le vérificateur a correctement écarté les preuves invalides.

## Diagnostic causal prudent

- La contrainte de format JSON n'est **plus le blocage** de ce pilote : toutes les sorties sont structurées.
- La présence du vocabulaire mathématique et de la règle ne suffit pas : **les 24 verdicts restent négatifs** indépendamment des arêtes.
- Le vérificateur d'exemples proposé par le modèle détecte parfois une vraie violation, mais **ne contrôle pas systématiquement si les deux prémisses sont présentes et la conclusion absente**.
- Aucun cas positif n'a déclenché de **certificat de partition** ; le modèle ne démontre pas qu'il sait confirmer exhaustivement une absence de contre-exemple.
- Le système hybride possède un **outil fiable de vérification bornée** (deux oracles concordants exhaustivement sur 1 024 graphes), mais cette fiabilité appartient au **logiciel**, pas au raisonnement interne du LLM.

## Prochaine expérience discriminante, proposée (NON exécutée ici)

Ne pas rejouer les huit cas ni adapter le seuil sur eux.

**PRIORITÉ : construire un enseignement procédural supervisé sur des cas distincts**, où le modèle doit lui-même :
1. produire une chaîne candidate \`(x,y,z)\` **et trois bits contrôlables** : \`xRy\`, \`yRz\`, \`xRz\` ;
2. recevoir la correction de ces **prémisses atomiques** sur un ensemble d'apprentissage, plutôt que seulement un rejet global ;
3. rechercher une **preuve positive** via une partition complète, autant qu'une preuve négative via un témoin ;
4. passer une évaluation aveugle **sur une nouvelle famille d'exercices**, de préférence de taille et de notation variées, avec contrôle à budget égal.

Comparer apprentissage procédural avec contre-exemples, simple règle, et un bras où **l'outil exact** fait lui-même la vérification. Les performances assistées par l'outil doivent être étiquetées « capacités du système », et **non** « capacité du modèle ». Réserver SFT/LoRA aux données générées par une source externe vérifiée et aux exercices réellement transférables, avec test de non-oubli.

**Décision :** PR #250 demeure DRAFT, aucune fusion vers \`main\`, aucune certification de savoir ou entraînement de poids à partir de ce résultat négatif.