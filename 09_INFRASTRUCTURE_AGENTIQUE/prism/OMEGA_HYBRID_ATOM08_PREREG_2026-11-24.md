# OMEGA-ATOM-08 — protocole de diagnostic des compétences élémentaires

**24 novembre 2026 — préenregistré AVANT tout appel réel à Qwen pour ATOM-08.**
PR expérimentale [#250](https://github.com/Abrasax63/Omega-pub/pull/250), hors \`main\`. Le protocole est **diagnostique et non un programme de SFT/LoRA**.

## Base vérifiable et motif du pivot

[TUTOR-07](https://github.com/Abrasax63/Omega-pub/actions/runs/45290017753) : 30 générations Qwen2.5-3B, pré-enregistrées ; D 4/8, G 3/8, professeur exact T 4/8, et **0/8 preuve complète valide pour les trois groupes**. Le modèle dit « faux » sur les huit graphes, même lorsqu'ils sont positifs. Ses certificats négatifs omettent tous les bits \`premises\`, mais certains triples proposés sont des vrais témoins sur des cas négatifs. Audit brut et conclusion dans \`OMEGA_HYBRID_TUTOR07_RESULTS_2026-11-23.md\`.

**Fuite méthodologique détectée dans TUTOR-07** : les IDs \`TRAIN_NEG\` / \`TRAIN_POS\` divulguaient le signe au bras témoin générique ; la synthèse demandait explicitement « partition positive » / « triple négatif ». Ces défauts ont déjà été corrigés pour les futures expériences, **sans réexécuter TUTOR-07**. L'essai reste un résultat descriptif négatif ; il n'est pas une réfutation causale propre de tous les professeurs de preuves.

La question de ce protocole n'est **pas** « Omega a-t-il appris ? », mais :
1. Omega sait-il lire les trois arêtes dirigées \`x→y\`, \`y→z\`, \`x→z\` dans une relation **sans les inventer** ?
2. Une fois ces trois valeurs vraies/fausses **données séparément** — sans lecture de graphe — applique-t-il la règle \`xy AND yz AND NOT xz\` ?
3. Le mode de représentation **liste d'arêtes versus matrice d'adjacence** affecte-t-il les erreurs de lecture ?

Sans réussite sur ces blocs, poursuivre directement le grand entraînement des preuves serait peu informatif.

## Jeu figé et budget

Code \`omega_hybrid_atom08.py\`, graine \`omega-atom08-atomic-reading-logic-before-training-v1\`.

**Lecture : 12 graphes dirigés inédits** sur \`p0,p1,p2,p3\`. Chaque cas désigne un triple ordonné de **trois sommets distincts**. Les trois arêtes consultées \`xy\`, \`yz\`, \`xz\` sont présentes ou absentes selon un masque préfixé et un ordre pseudo-aléatoire reproductible. Quatre à six arêtes distractrices existent sans jamais modifier l'un de ces trois bits. Aucune hypothèse de symétrie, de transitivité ou d'équivalence n'est imposée.

Chaque graphe est présenté **DEUX FOIS**, dans des appels sans historique, avec ordre des deux formats alterné et contrat identique : un JSON strict avec trois booléens \`xy,yz,xz\`.

- **LIST** : arêtes dirigées exhaustives en liste de couples ;
- **MATRIX** : même relation sous forme de matrice d'adjacence 4×4, indices de lignes/colonnes déclarés.

Les questions et IDs ne contiennent **ni les trois bits attendus ni la vérité**. Ceux-ci sont uniquement dans \`oracle_only.json\`. On mesure les **36 bits** de chaque représentation, les 12 triples entièrement justes et les invalidités JSON. Les deux représentations ne doivent pas être présentées comme strictement contrôlées causalement : longueurs et facilité d'accès différentes ; tous les coûts réels sont reportés.

**Logique locale : 8 autres appels**, un pour **chacun des huit motifs** de vérité possibles des trois bits (2³), fournis directement au modèle, en **ordre gelé**, sans graphe à lire. Il doit donner \`{"violates":true|false}\`. Un seul des huit motifs (vrai, vrai, faux) est un contre-exemple ; le contrôle exige donc expressément que **ce motif soit correctement reconnu**. Toujours répondre « faux » ne peut pas constituer une réussite.

Le budget total est **32 appels réels maximum** (12 LIST + 12 MATRIX + 8 LOGIC), température 0, seed 9123 via \`RealClient\`, Qwen2.5-3B-Instruct Q4_K_M GGUF et empreinte des poids \`9c9f56a391a3abbd5b89d0245bf6106081bcc3173119d4229235dd9d23253f94\`, llama.cpp b12633 CPU, sans API d'inférence payante. Attention : le temps de calcul GitHub Actions reste une ressource, même sans paiement d'API.

## Critères préenregistrés

Le résultat n'est **pas** un classement d'AGI ni une preuve d'apprentissage durable. Il désigne le prochain goulet :

- **READING_GATE** : chacun des formats liste et matrice atteint ≥10/12 triples entièrement justes et 0 JSON invalide.
- **LOGIC_GATE** : les huit lignes de la table de vérité sont exactement justes, dont \`110 → violates=true\`, et 0 JSON invalide.
- Tous les contrôles sont exacts, sans tolérance post-hoc ni réparation des sorties.

\`FOUNDATIONAL_GATES_PASS_DESCRIPTIVE_ONLY\` si les deux portes passent. Sinon \`FOUNDATIONAL_GATE_NOT_PASSED\`. Si le run ne termine pas, \`TECHNICAL_FAILURE\` : ne pas conclure à un défaut scientifique. Les nombres de tokens, temps, formats et erreurs doivent être conservés, ainsi que les réponses brutes.

**Interprétation prévue, non tautologique** : logique correcte mais lecture incorrecte suggère de chercher du côté de la représentation et de l'extraction de données ; lecture correcte mais logique incorrecte suggère un problème d'application de l'implication ; les deux échouent signalent un besoin de décomposition et d'outillage dans les deux domaines. Il s'agit de diagnostics de ces questions, pas de causalités générales démontrées.

## Sécurité et reproductibilité

- \`model_inputs.json\` / \`oracle_only.json\` sont conservés **séparément**, hachés et enregistrés dans le rapport **avant tout appel au modèle**.
- Pas de recherche Web ni de transmission de données de projet privées au modèle.
- Aucune vérité d'une question de lecture n'est insérée dans le prompt ; les trois bits d'une question de logique sont fournis *volontairement* pour isoler cette opération.
- JSON strict : pas d'explication ou de clé supplémentaire admise ; booleans stricts, abstentions/invalides dans le dénominateur.
- Modèle identique et stateless pour les 32 appels, sans poids entraînés ni mémoire scientifique promue.
- Aucun cas TUTOR-07 à 6 sommets ni PROCEDURE-06 à 5 sommets n'est réutilisé. Les 12 graphes nouveaux ne peuvent plus servir de holdout indépendant après le premier run.
- Workflow GitHub Actions déclenché **une seule fois** par création de son propre fichier \`omega-hybrid-atom08-once.yml\`, aucun cron, aucune rediffusion automatisée ; des tests hors ligne précèdent toute inférence.
- Les artefacts bruts, les prompts hachés, coûts, empreintes du modèle et vérités séparées sont conservés même lors des échecs partiels ; verdict seulement après audit indépendant.

## Ensuite

Si la lecture échoue, créer une **interface de perception explicite** (représentation normalisée ou fonction exacte de lookup) et comparer son coût aux performances du modèle seul. Si la logique échoue alors que les bits sont corrects, créer un **petit programme exécutable** pour la table de vérité. Si les deux réussissent, tester l'exhaustivité des parcours sur un ensemble neuf avant de lancer un entraînement procédural sur des données sûres. Aucune auto-certification, aucun re-test de cette cohorte pour améliorer artificiellement le verdict.
