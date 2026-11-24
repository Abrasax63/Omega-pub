# OMEGA-HYBRID-TRANSFER-05 — préenregistrement et frontières de preuve

**23 novembre 2026 — branche expérimentale de PR #250. Statut lors de la rédaction : PROTOCOLE ET CODE SANS INFÉRENCE TRANSFER-05.**
Aucune modification de `main`, aucun entraînement de poids, pas de nouvelle automatisation récurrente et aucune API payante.

## Pourquoi une autre expérience malgré BENCH-04 ?

Le benchmark [OMEGA-REPAIR-BENCH-04](https://github.com/Abrasax63/Omega-pub/actions/runs/45118892999) a déjà comparé feedback générique, témoin unique et toutes les obligations dans une tâche de **réparation du même graphe**, sans observer le gain fixé au préalable. Le nouveau test pose une question distincte : un modèle peut-il **formuler lui-même une règle générale à partir d'une critique ancienne**, puis exploiter cette règle pour **classer des graphes inédits à quatre sommets**, au lieu de simplement réparer l'exemple montré ? Ce serait du **transfert en contexte**, pas une mise à jour durable des poids.

## Préenregistrement exact

### Première phase : règle apprise sur le seul ancien cas exposé

Point de départ unique : les arêtes du graphe produit par Qwen2.5-3B-Instruct Q4_K_M au [run #45274034725](https://github.com/Abrasax63/Omega-pub/actions/runs/45274034725) :
`(a,a),(b,b),(c,c),(a,b),(b,a),(b,c),(c,b)`.
Le graphe était annoncé comme une relation d'équivalence mais n'est pas transitif (`aRb` et `bRc` sans `aRc`). La notion et le graphe sont **déjà exposés** : leur réutilisation ne crée pas un nouveau holdout.

Trois conditions préenregistrées :
- **D** — réponse directe : aucune règle d'entraînement injectée ;
- **G** — feedback générique « refusé par le vérificateur, raison masquée ». Le modèle génère lui-même une `rule` au format JSON ;
- **W** — feedback exact « transitivité violée par `(a,b,c)` ». Le modèle génère lui-même une `rule` avec le **même contrat**, sans recevoir de graphe réparé.

Le modèle produit **un seul message de règle par bras G/W**, aucun réessai ni correction de sortie. Un JSON invalide ou une abstention donne une règle absente, conservée dans les résultats. L'appel de règle est enregistré en entier, SHA-256 du prompt et de la génération, tokens, durée.

### Deuxième phase : huit classifications nouvelles

Univers `m0,m1,m2,m3`, distinct de celui de l'entraînement. Générateur **déterministe** gelé dans `omega_hybrid_transfer05.py`, graine `omega-transfer05-predeclared-finite-relations-v1`, énumération des 64 graphes simples non orientés possibles, ajout explicite des quatre boucles puis symétrisation de toutes les arêtes non diagonales. Les relations sont donc réflexives et symétriques : le facteur discriminant est la transitivité.

Choisir **4 classes d'isomorphisme positives non triviales** (relations d'équivalence) et **4 classes négatives** (réflexives et symétriques, mais non transitives), toutes distinctes sous les **24 permutations** de `S4`. Sélection et ordre déterminés par SHA-256 de la graine et des masques *avant l'inférence*. Les noms, arêtes et ID sont stockés dans `model_inputs.json`. Les vérités, axiomes violés et témoins restent dans `oracle_only.json`, que le code **n'envoie jamais au LLM**. Les deux empreintes sont enregistrées avant toute génération.

Chaque tâche est posée identiquement trois fois à D/G/W ; chaque appel est sans historique conversationnel, seule la zone de règle précédente diffère. Les **six permutations** d'ordre des bras sont appliquées de manière fixe sur les huit tâches. Les prompts sont égalisés avant appel via le tokeniseur du serveur `llama.cpp` et le comptage réel de tokens d'entrée de chaque appel est contrôlé à **±5 %**. Remplissage neutre sans axiomes ni corrections mathématiques. Si budgets non comparables, la comparaison est **INDÉTERMINÉE**.

### Modèle et limite de coût

Réutiliser exactement **Qwen2.5-3B-Instruct Q4_K_M**, poids SHA-256 `9c9f56a391a3abbd5b89d0245bf6106081bcc3173119d4229235dd9d23253f94` ; `llama.cpp b12633`, CPU GitHub Actions, température 0, seed 9123, sorties JSON `max_tokens=260`, nombre maximal de **26 appels réels** (2 règles + 8 × 3 évaluations). Aucun modèle payant et aucun changement de poids.

### Métriques et seuils fixés

Pour chaque bras : réponses JSON valides, abstentions, réussite booléenne `holds`, et surtout réussite de la **liste complète des axiomes violés** ; les erreurs de format et abstentions restent dans le dénominateur **8**. Rapporter coût des tokens, secondes, nombre d'appels, ordre, règles produites, réponses brutes et empreintes.

**Signal exploratoire de transfert en contexte observé** si :
1. les budgets de prompt respectent ±5 % avant et après appels ;
2. W classe **au moins 6/8 tâches entièrement justes** ;
3. W dépasse **G et D de deux réussites complètes minimum** chacun ;
4. **zéro JSON invalide** en W.

Sinon : `PRE_REGISTERED_GAIN_NOT_OBSERVED` ou `INDETERMINATE_BUDGETS`. Même en cas de réussite, **ne pas annoncer « nouvelle compétence durable », « amélioration statistique », « entraînement des poids » ou « apprentissage autonome général »** : n=8, même modèle, rétroaction connue, leçon potentiellement déjà apprise à l'origine. Une vérification indépendante et des tâches supplémentaires sont nécessaires.

### Défenses contre faux positifs

- **Fuite de correction** : le code ne construit les questions que depuis `model_inputs.json` ; `oracle_only.json` n'est utilisé que pour noter les sorties. Les modèles ne reçoivent aucun résultat du holdout, y compris lors de la fabrication de la règle.
- **Réutilisation d'instances antérieures** : nouveau format de tâche (classification et non réparation de candidat), quatre sommets `m*`, graphes non isomorphes entre eux. Ce seul changement ne prouve pas une indépendance totale face aux données de préentraînement du modèle.
- **Difficulté trompeuse** : les négatifs satisfont déjà réflexivité et symétrie ; il faut vérifier la transitivité. Les positifs sont non triviaux.
- **Apprentissage de poids non confondu** : les appels sont stateless, et une règle dans le prompt n'est qu'une **mémoire externe temporaire**, pas une compétence paramétrique.
- **Contamination par la comparaison** : une fois ces huit cas exposés lors du premier run, aucune relance ne peut constituer une deuxième cohorte indépendante.
- **Reproducibilité** : source du modèle et SHA verrouillés, rapport conservé même si l'expérience bloque, workflow déclenché **une seule fois** par création d'un fichier de workflow filtré sur ce chemin, aucun cron.

### Livrables et verdict

`omega_hybrid_transfer05.py`, `test_omega_hybrid_transfer05.py`, ce protocole, workflow ponctuel `omega-hybrid-transfer05-once.yml`. Les tests du moteur **ne constituent pas une preuve de transfert**. Si le résultat est négatif, examiner les réponses et se concentrer sur l'enseignement de la transitivité plutôt que multiplier les appels sur le même jeu.
