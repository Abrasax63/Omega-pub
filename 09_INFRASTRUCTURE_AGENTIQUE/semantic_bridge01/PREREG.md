# SEM-BRIDGE-01 — test prospectif de correspondance mathématiques ↔ Lean

**Préenregistrement au 21 novembre 2026 avant développement de la nouvelle heuristique et avant consultation des 12 sources du holdout.**

## Motivation
Sur EXTERNAL-MEMORY-01 (PR #227), Qwen2.5-0.5B a reconnu **0/8 appariements positifs**, avec 4/12 réponses correctes OFF et 3/12 ON. Une optimisation KV n'a pas réglé le problème sémantique. Ne pas réutiliser ces huit énoncés comme une validation nouvelle.

## Approche falsifiable
1. Une **représentation intermédiaire typée légère (IR diagnostique)** extraite séparément de l'énoncé naturel et de la déclaration Lean : concepts mathématiques, quantificateurs, négations, égalités/inégalités, nombres explicites (en enlevant les identifiants d'exercices et les en-têtes). La signature ne dépend jamais de l'ID de source, du nom de fichier, du classement « A/B/NONE » ou de l'étiquette correcte.
2. Comparer les deux signatures à l'aide de règles lexicales/structurelles **fixées sur les huit fichiers déjà étudiés en #227 et des notions mathématiques standards**, avant toute ouverture des sources du holdout. Ne pas utiliser les textes du nouveau test pour adapter le dictionnaire après coup.
3. Conserver un **contrôle contradictoire** : si ni A ni B n'est étayé, retourner `NONE` (abstention). Si les deux le sont et que l'écart est trop faible, retourner `NONE` avec statut `AMBIGUOUS`, **pas** une correspondance certifiée.
4. Mesurer le modèle Qwen 0,5B OFF séparément avec les 18 mêmes questions, et le couplage sûr `LLM_proposal + IR_guard`. Le contrôle structural peut refuser ou remplacer une proposition du LLM seulement s'il dispose d'une meilleure correspondance **observable**. Tout résultat reste au statut `HEURISTIC_SOURCE_MATCH_NOT_PROOF` ; aucun Lean n'est recompilé. Cache LLM OFF pendant l'évaluation principale ; la différence ON/OFF déjà observée est une raison de ne pas en faire une variable de ce test.
5. Vérifier les entrées et les sorties, **sans** utiliser le jumelage gold pour prendre une décision, puis calculer les métriques seulement après : nombre d'appels/abstentions, exactitude globale, succès sur 12 appariements positifs et sur 6 négatifs, couverture, fausses admissions (faux positifs sur NONE), ambiguïtés, parité de la référence de source.
6. Effectuer un **test de non-régression sur les huit anciennes sources** à des fins de développement (on ne compte pas ce résultat comme un test aveugle), puis figer le code et les tests avant le premier accès à une source du holdout.

## Cohorte prospective immuable
Source `marcusm117/ProofNet-Verified` commit `b7ca411a2abaa6caf3580192b30d865e5bd10bc4` (Apache-2.0). Fichiers `proofnet-{12,18,35,56,78,100,142,182,23,43,153,263}.lean`. Ensemble **disjoint** des 16 sources ProofNet26 et des huit fichiers EXTERNAL-MEMORY-01.

`BLIND_HOLDOUT.json` est gelé AVANT la construction du parseur : **18 questions** (12 positives, 6 `NONE`; 6 A et 6 B). Distracteurs et ordres sont fixés, pas de remplacement si une source est inaccessible ; un échec d'accès reste un résultat d'infrastructure non concluant. Le lien correct A/B est fondé sur l'identité **du fichier externe original**, non sur une annotation de fidélité sémantique indépendante.

## Vérifications et limitations
- Chaque source doit correspondre à son Git blob, être téléchargée sur un commit immuable et être extraite par deux chemins différents. Le modèle ne reçoit ni le gold ni le chemin du fichier.
- Les références Lean de ce corpus contiennent généralement `sorry` : une déclaration n'est pas une preuve, et une correspondance de notions n'est pas une preuve d'équivalence NL/Lean.
- Le **score de correspondance** est un indicateur heuristique, pas une probabilité calibrée. Seuil minimum 2,5 et marge 1,0 en unités de score fixés en amont. Ces choix ne sont pas ajustés après visualisation du holdout.
- Un modèle 0,5B CPU et peu d'exemples ne prouvent rien sur la compréhension générale, ni sur la qualité d'un autre modèle. Pas d'amélioration revendiquée sans comparaison.
- Le coût de calcul, le pic RSS, l'impact sur la mémoire persistante, les erreurs, et **toutes les prédictions** doivent rester auditables. Aucune sortie LLM ni heuristique ne sera promue au registre des théorèmes.
- Si l'IR ne généralise pas, noter le résultat **négatif**, conserver le code en PR brouillon et proposer un nouveau test ciblé; ne pas retoucher le dictionnaire puis annoncer le même jeu comme « aveugle ».

## Décision de publication
Produire des artefacts JSON avec rapports sources, références et prédictions. L'interface de mémoire persistante de PR #228 reste **inchangée** : on peut conserver le bilan expérimental non certifiant dans une branche dédiée après revue, mais aucune écriture automatique sur `main`, aucune API payante.
