# SELF-TEACH-03 — résultat et diagnostic de la première exécution réelle (23 novembre 2026)

## Preuves et provenance
- [Run #45132083501](https://github.com/Abrasax63/Omega-pub/actions/runs/45132083501) : deux jobs réussis, tests logiciels **10/10**.
- [Artefact brut #14797723836](https://github.com/Abrasax63/Omega-pub/actions/runs/45132083501/artifacts/14797723836), contenant raw.json, score.json, log, empreintes SHA.
- SHA-256 `raw.json` : `eaeec79c11124b7360679af7f23384cf31f3671b4954e7c14e37a67b17e8b163`.
- SHA-256 `score.json` : `814af6009a46aed319710c149bb4146bf91a9bc08e7d07dd8ae7b627ffd7c1b2`.
- Tête du registre chaîné : `c9c5d3a7c22a9f8cf34996e414bb45b4864f6233253a609b5dc215c73ea3fe78`.
- Qwen2.5-3B CPU, **13 appels réels**, durée génération 178,399 s, aucune API payante, aucun changement de poids.

## Verdict falsifiable sur le holdout NOUVEAU (18 cas, désormais consommés)

| Bras | Exact sur 18 | Détail par famille Q1/Q2/Q3 | Code sûr |
|---|---:|---|---:|
| A — direct | **13/18** | 1/6, 6/6, 6/6 | 3/3 |
| P — conseil générique | **7/18** | 0/6, 1/6, 6/6 | 2/3 |
| B — après pratique | **4/18** | 0/6, 1/6, 3/6 | 2/3 |

**Aucune leçon admise**. Les trois prompts des bras P et B ont des empreintes identiques ; B reçoit strictement la même consigne neutre que P, pas de mémoire issue du cursus. L'écart P/B signale une instabilité de la génération ou de son contexte d'inférence, **pas un effet d'apprentissage**. Les données de 18 cas ont été utilisées une fois, un rejeu ne pourrait pas devenir une réplication aveugle.

## Le diagnostic désormais possible grâce au nouveau journal de toutes les tentatives

Tâche d'apprentissage retenue par Omega : L1, alternance minuscule/majuscule parmi les lettres ASCII en comptant **à partir de zéro**.

- **Première version** : **1/10**, code Python sûr. Le programme fait `count += 1` avant de comparer la parité, puis choisit `lower()` quand `count % 2 == 0`, ce qui inverse le résultat attendu dès la première lettre.
- **Premier retour** : trois contre-exemples minimaux (par exemple `a1b` attendu `['a','B']`, obtenu `['A','b']`). Le modèle modifie surtout le parenthésage du test ASCII ; la parité reste inversée, **1/10**, `ROLLBACK_NO_GAIN`.
- **Deuxième retour** : mêmes trois témoins. Le modèle reformule sa cause supposée, mais **ne modifie pas** le test de parité ni la solution ; **1/10**, `ROLLBACK_NO_GAIN`.
- L'autre exercice de pratique L2 : **10/10** dès le premier essai. La sélection adaptative choisit bien le plus faible L1.
- **Leçon : aucune**, conformément au verrou 10/10. Nombre d'essais de pratique enregistrés : quatre (deux premiers essais et deux réparations), dont tous les codes bruts, diagnostics, hashes et décisions de retour arrière sont conservés.

Problème Q1 (compter et indexer certaines lettres dans une chaîne) :
- A : code sûr mais une erreur d'indice/compteur, 1/6.
- P et B : code produit contenant `.index(char)` que le sandbox AST interdit, 0/6, malgré une syntaxe Python licite. `.index` peut aussi donner une position erronée si une lettre apparaît plusieurs fois : **ce n'est pas une preuve que desserrer la politique AST résoudrait le problème**.

## Portée de l'expérience
**IMPLÉMENTÉ / EXÉCUTÉ / TESTS LOGICIELS PASSÉS / NON-GAIN AUTONOME CONFIRMÉ SUR CETTE COHORTE.** Le laboratoire a gagné une capacité d'observation vérifiable : le blocage n'est plus un simple score, c'est un cas de **reconnaissance partielle de l'erreur sans correction effective de l'expression responsable**.

### Prochaine vérification décisive proposée (non exécutée ici)
Avant un nouveau holdout, introduire en pilote **un contrôle de modification sémantique de la zone supposée fautive** : demander au modèle de tracer explicitement les variables à la première entrée qui échoue, puis rejeter comme nouvelle réparation un programme qui ne change pas le comportement sur ce contre-exemple de développement. Comparer cette méthode au retour de test actuel avec des tâches nouvelles préenregistrées et budgets égaux. Cela ne doit pas `prémâcher` la correction (ne pas fournir la condition parité ni un programme solution).

**Aucun changement à `main`, aucun entraînement LoRA.**
