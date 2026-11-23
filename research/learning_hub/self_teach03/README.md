# OMEGA-SELF-TEACH-03 — apprendre de ses erreurs : le journal et le contre-exemple

**23 novembre 2026. PR expérimentale ; aucune fusion dans `main`.**

## Résultat source vérifié
La PR #244 a démontré le fonctionnement du pilote CPU, mais pas l'apprentissage : 12/18 direct, 12/18 avec conseil, 13/18 après pratique, sans aucune leçon vérifiée. L'entraînement sur la tâche difficile n'a pas dépassé 2/8 cas de développement. Les anciennes sorties ne conservaient pas tous les programmes bruts successifs : une erreur ne pouvait pas être reconstruite de façon complète.

## Mécanisme expérimental
1. Le modèle choisit lui-même le plus mauvais résultat parmi **deux nouveaux exercices** (10 tests de développement par exercice).
2. Le vérificateur lui présente **trois contre-exemples minimaux** (taille de l'entrée puis ordre lexicographique) : entrée, sortie attendue et sortie réellement obtenue. Aucune solution d'oracle n'est fournie.
3. Il propose une hypothèse et un programme corrigé ; l'AST et le sandbox déjà utilisés dans #232 le contrôlent.
4. Une correction n'est conservée que si elle améliore strictement le score **sur les dix mêmes cas de développement**, en annulant les régressions. Il peut faire deux tentatives.
5. Chaque tentative sauvegarde texte brut, code, format, hypothèse, dix résultats détaillés, décisions d'acceptation ou rollback, et empreintes. Le journal est chaîné par SHA-256. Ce chaînage détecte les changements d'un enregistrement sans preuve d'origine externe ; ce n'est ni une signature ni une certification scientifique.
6. Une leçon de contexte n'est créée que si le modèle passe **10/10** sur son exercice le plus difficile, avec gain sur son score initial. Sinon **aucune mémoire** n'est autorisée.
7. Sur **18 nouveaux cas cachés préenregistrés** et trois familles différentes, comparaison : A (direct), P (conseil générique), B (leçon acquise ou, si aucune leçon, même texte que P). Le même normaliseur de sauts de ligne et la même validation AST s'appliquent aux trois bras. Le scoreur relit d'abord les journaux de pratique, vérifie chaque résultat et recalcule les décisions.

## Entrées figées avant tout code ou inférence
[PREREG.md](./PREREG.md), TRAIN_FROZEN.json, EVAL_PUBLIC_FROZEN.json, EVAL_SEALED_FROZEN.json, épinglés par SHA Git blob dans `runner.py`. Les cohortes #242 et #244 sont consommées. Les données de cette PR sont **synthétiques écrites par le concepteur**, pas une découverte de connaissances par Omega.

## Exécution reproductible sans paiement

```sh
python -m unittest discover -s research/learning_hub/self_teach03 -p test_self_teach03.py -v
# Qwen2.5-3B GGUF épinglé servi en CPU local par llama.cpp :
python research/learning_hub/self_teach03/runner.py --server http://127.0.0.1:8080 --output /tmp/omega03-raw.json
python research/learning_hub/self_teach03/score.py --raw /tmp/omega03-raw.json --output /tmp/omega03-scored.json
```

La workflow `.github/workflows/omega-self-teach03.yml` n'exécute qu'une première expérience sur PR ouverte : pas de relance automatique lors des commits. CPU, serveur loopback, pas de secrets, pas d'API payante, 0 poids modifié et sauvegarde des résultats bruts. La cohorte devient **consommée dès la première notation**.

## Limites scientifiques
Une correction validée sur dix tests n'est pas une preuve universelle ; un gain A/P/B peut provenir de l'inférence ou du contexte. Le modèle peut réussir sans acquérir de leçon, et peut échouer malgré deux retours de test. `C` LoRA est explicitement `TRAINING_NOT_AUTHORIZED` : aucune boucle d'entraînement automatique sur ses propres productions n'est lancée. `main` demeure inchangée.
