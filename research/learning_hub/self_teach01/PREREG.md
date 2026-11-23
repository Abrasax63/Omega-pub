# OMEGA-SELF-TEACH-01 — préenregistrement (23 novembre 2026)
 
## Hypothèse falsifiable
Sur trois familles Python nouvelles, un modèle local Qwen2.5-3B peut-il obtenir plus de cas cachés exacts avec une mémoire de correction produite lors d'un micro-cursus autonome qu'en réponse directe ? Un gain est exploratoire, pas une preuve de généralisation ni de causalité ; les tokens de contexte et le coût total diffèrent.

## Trois bras et budget
A : une génération de code par problème, sans mémoire (max 660 nouveaux tokens).
B : une génération de code par **même** problème, même plafond de 660 tokens, avec mémoire de pratique admise uniquement après exécution des tests publics de développement.
C : LoRA sur des corrections autonomes vérifiées, **désactivé** tant que le Learning Hub n'autorise pas un entraînement et qu'un nouveau jeu de test indépendant n'est pas gelé. Ne jamais recycler l'adaptateur SFT01 en prétendant qu'il a appris ce curriculum.

Un micro-cursus choisit de façon reproductible le plus faible résultat parmi deux tâches d'entraînement, produit une nouvelle proposition après feedback public, et ne retient la mémoire que si la version finale est sûre, exécutable et meilleure **sur les cas de développement du curriculum uniquement**. Aucune information issue de l'évaluation cachée ne peut guider la sélection ou une révision.

## Séparation des données
TRAIN_FROZEN.json : deux familles d'entraînement, observations et cas de développement.
EVAL_PUBLIC_FROZEN.json : trois familles distinctes, descriptions et deux exemples publics par problème.
EVAL_SEALED_FROZEN.json : cinq tests cachés nouveaux par famille, accessibles **seulement au script de notation, après génération des deux bras**.
Les données sont synthétiques et créées par le concepteur : aucune découverte autonome revendiquée. Les textes exacts, le modèle et les limites sont figés avant la première inférence. Les trois fichiers sont établis **avant le programme et le run du modèle**; ensuite les empreintes Git blob sont contrôlées par le code. Les anciens holdouts A-F, SFT01 et S04 sont consommés et interdits à ce test.

## Critères et contrôles
Mesurer par bras : programmes sûrs, tests exacts / 15, problèmes entièrement exacts / 3, erreurs silencieuses, abstentions et coûts en nombre d'appels/tokens/temps. La mémoire doit être produite sans lecture des réponses cachées ; le scoreur refuse une incohérence d'identité/hash. Contrôles négatifs : programme interdit, mémoire conservée sans réussite, contenu des tests cachés visible dans une requête, altération des fichiers figés, régression par correction.
Verdict "gain exploratoire" uniquement si B > A sur les 15 tests cachés **sans régression sur les problèmes A déjà entièrement réussis** ; sinon "aucun gain démontré". Un seul premier run; l'ensemble caché devient consommé et les relances ne sont pas des répétitions indépendantes.

## Sûreté et frontière
Réutiliser le sandbox AST restreint et le client Qwen CPU de #232, la logique de retour arrière de #234 et le verrou de préparation LoRA de #235. Ne pas exécuter de code généré en dehors du sandbox existant. Accès à des sources publiques épinglées seulement pour l'inférence CPU; aucune API payante, aucun service externe, pas de secrets, pas de fusion et aucun changement de main.
