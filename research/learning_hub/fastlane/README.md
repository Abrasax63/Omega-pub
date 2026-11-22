# Omega Fast Lane — accélérer la qualité sans démultiplier les modèles

**22 novembre 2026 — branche expérimentale empilée sur PR #237 ; main inchangée.**

## But concret

Le coût principal d'un nouveau cycle ne doit pas être l'écriture manuelle de chaque exercice. Nous avons déjà le compilateur, le laboratoire d'exécution sûr, la banque d'exemples SFT01, le LoRA entraîné, et les contrôles d'intégrité. Ce pilote fournit **une fabrique déterministe de réparations sémantiques supervisées**, contrôlées sans appel de modèle, pour alimenter un futur entraînement si de nouvelles évaluations le justifient.

**Ce que la fabrique fait vraiment** : réutiliser les **20 familles synthétiques de référence déjà utilisées comme entraînement dans SFT01**. Elle y injecte des erreurs **logiques** et valide la correction par le code de référence, sur les exemples visibles et des contrôles de qualité **déjà consommés comme entraînement**, sans prétendre constituer un nouveau benchmark ni inventer de nouvelles familles de fonctions.

**Ce qu'elle ne fait pas** : lire le holdout SFT01, lire le holdout sémantique #237, faire des appels à Qwen/SmolLM, modifier des poids, concevoir une nouvelle architecture ou promouvoir automatiquement une compétence.

## Génération et qualité

\`fastlane.py\` propose des mutations bornées : inversion de conditions, changement de casse, confusion caractères/chiffres, ordre inversé, erreurs de parité et d'appartenance, et modifications de constantes simples. Chaque candidat :

1. part d'une solution de référence déjà admise dans **le train SFT01** ;
2. produit un programme Python syntaxiquement valide et conforme à l'AST autorisé ;
3. se trompe sur au moins un des exemples **publics du train** ;
4. se trompe également sur au moins un contrôle qualité de l'ancien train ;
5. conserve une solution qui réussit tous les exemples ;
6. est dédupliqué, limité à 4 mutations par famille, traçable par empreinte et rangé comme **supervision synthétique**, jamais « autodécouverte d'Omega ».

La taille et la diversité réellement produites sont calculées par l'exécution CI, **pas inventées dans les descriptions**.

\`\`\`sh
python research/learning_hub/fastlane/fastlane.py \
  --output /tmp/omega-fastlane/candidates.json
\`\`\`

Une nouvelle tentative de généralisation exigera **un autre ensemble d'évaluation, gelé avant entraînement**, constitué de fonctions/erreurs différentes et idéalement de problèmes logiciels externes. Les tests anciens A–F, les tests SFT01 et la cohorte sémantique04 **ne peuvent plus être présentés comme inédits**. Un regain de score sur ces cohortes n'est pas une deuxième confirmation.

## Plan d'accélération en deux vitesses

**Voie rapide (gratuite, CPU, automatique)** : génération d'exercices → vérification AST et comportement → déduplication par famille → proposition de nouveaux blocs pédagogiques → rapport qualité et coût. **Aucun appel LLM nécessaire.**

**Voie de validation (coûteuse en inférence/entraînement)** : la lancer **seulement après** lecture du benchmark sémantique04, préparation d'un véritable holdout neuf, et choix préenregistré de modèle, du nombre de mises à jour et du budget comparatif. Réutiliser le LoRA existant plutôt que réentraîner en continu le même modèle sur des variantes quasi-identiques.

Cette distinction évite de confondre accélération du pipeline avec amélioration réelle de compréhension. Le produit du pilote reste en quarantaine, l'ancien code de TRAIN26 et l'adaptateur SFT01 ne sont pas écrasés.

## Évolutions possibles après vérification

- Ajouter des **nouvelles familles de fonctions** à partir de sources libres (licences, traçabilité et correctifs de référence) et d'exercices proposés par Omega, filtrés par tests indépendants.
- Donner au modèle la possibilité de choisir ses sondes et les notions à étudier, sans livrer l'oracle ni les scores cachés.
- Étudier regroupement de séquences (packing), masquage de perte sur réponses et distillation plus efficace ; **ne pas attribuer de gain de vitesse non mesuré**. Références : https://huggingface.co/docs/trl/sft_trainer et https://huggingface.co/docs/transformers/peft.
- Évaluer côte à côte : base, LoRA, mémoire de séance, correcteur symbolique et système hybride, à budget total comparable.
- Conserver le refus de promotion tant que les nouveaux programmes n'ont pas réussi des tests réellement inconnus.

**Statut épistémique initial** : générateur implémenté, tests à faire ; aucune nouvelle amélioration du modèle démontrée.
