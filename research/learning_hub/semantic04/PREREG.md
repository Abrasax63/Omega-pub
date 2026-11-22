# OMEGA-SEMANTIC-TRANSFER-04 — préenregistrement (22 novembre 2026)

**Fait avant le premier nouvel appel au modèle, avant lecture de ses réponses.**
**Statut : PROPOSÉ / nouveau benchmark gelé, résultats inconnus.**

## Pourquoi ce test

Le pilote [SFT01 / PR #236](https://github.com/Abrasax63/Omega-pub/pull/236)
a entraîné réellement SmolLM2-135M-Instruct par LoRA, 124 étapes :
norme L2 5,5832061325. Sur 12 exemples de *réparation syntaxique*,
le contrôle strict « code uniquement » était passé de 0/12 à 11/12.
Une partie du gain pouvait provenir de la conformité du format.
Ces 12 tâches sont désormais consommées.

Le prochain test doit **changer la nature du défaut**, pas seulement
changer les chaînes de test.

## Question et hypothèse falsifiable

L'adaptateur **inchangé** de SFT01 améliore-t-il sur des programmes
inconnus la réparation d'erreurs **sémantiques** dans du Python qui
**compile déjà**, face (a) au modèle de base et (b) à une recherche
symbolique classique des correctifs simples ?

Si SFT01 a principalement appris à produire une syntaxe/forme correcte,
le gain fonctionnel peut disparaître. Un résultat nul reste valide.

## Sources immuables

- Nouveau jeu \`HOLDOUT_SEMANTIC_FROZEN.json\` ; SHA1 de blob Git
  **60e17c1ac8dfa1d1f3ce2cc6468fcd471bda4869**, avant inférence.
- 12 tâches : **six familles fonctionnelles distinctes, deux défauts
  sémantiques par famille**. Chaque défaut est un programme Python
  **syntactiquement valide mais erroné**.
- Familles : doubler uniquement les voyelles, caractères uniques aux
  indices pairs, mots alphabétiques séparés par un pipe et mis en
  majuscules, chiffres non nuls parcourus de droite à gauche, paires
  contiguës de caractères, indices et majuscules des lettres.
- 2 exemples visibles avec sorties par tâche ; 5 tests cachés,
  non transmis au modèle ni au solveur symbolique ; soit 60 contrôles
  fonctionnels cachés. Le code oracle n'est jamais envoyé au modèle.
- Aucun de ces exemples n'est ajouté à TRAIN_FROZEN.json de SFT01.
  Aucun entraînement dans ce pilote.
- Origine de l'adaptateur gelée : SFT01,
  [run #45073297901](https://github.com/Abrasax63/Omega-pub/actions/runs/45073297901),
  artefact GitHub **14774003555**. Vérifier modèle, SHA du train,
  124 steps et empreintes de l'adaptateur avant chargement.

## Trois bras à comparer — même entrée du problème

1. **BASE** : SmolLM2-135M-Instruct de révision
   \`ee72e5415c002e8fc0566a191a07c0b2b708875a\`, sans adaptation.
2. **LORA-SFT01** : mêmes poids de base + adaptateur PEFT enregistré,
   aucun ajustement supplémentaire ; prompts identiques, génération
   greedy, max 220 nouveaux tokens et mêmes 12 tâches.
3. **SYM-1EDIT** : un *petit* correcteur Python déterministe qui ne voit
   que la source cassée et les deux exemples publics. Il tente des
   substitutions locales prédéfinies en taille bornée (une édition) :
   inverser comparaisons, remplacer \`in/not in\`, échanger
   \`lower/upper\`, changer \`split\` entre | : ,,
   changer direction d'itération, parité, quelques bornes et
   tranches, ajouter/retirer une ligne d'append consécutive,
   corriger un indice +/-1.
   Choisir le premier programme qui compile, reste autorisé par
   l'AST du laboratoire et réussit les **deux exemples publics**.
   Ne jamais consulter les cinq exemples cachés pendant la sélection.
   **Comparateur restreint**, pas un correcteur Python universel.

La comparaison SYM-1EDIT teste si des modifications locales et
exemples suffisent, sans prétendre à une supériorité générale.

## Deux lectures indépendantes du même texte du modèle

- **STRICT** : programme complet \`def transform(s)\` sans introduction,
  markdown, import ni autre code top-level, selon le contrat d'origine.
- **PERMISSIVE PRÉDÉFINI** : autoriser **un unique bloc de code Markdown**
  ou une unique fonction \`def transform(s)\` isolable dans un message
  avec explication. Exiger syntaxe, signature et AST restreint après
  extraction. Rejeter réponses avec plusieurs fonctions, syntaxe
  ambigüe ou opérations non autorisées.

Mesurer séparément pour chaque bras : validité stricte et permissive,
nombre de fonctions correctes sur les **cinq** tests cachés,
nombre total de tests cachés corrects, régressions, coût d'inférence.
**Le gain de format** = changement strict → permissif, sans
nouvelle génération. L'évaluation permissive est préenregistrée
avant examen des sorties ; elle ne constitue pas une nouvelle cohorte.

## Interdictions, limites et statuts

- Pas de nouvel entraînement ; le LoRA précédent reste inchangé.
- Pas d'API payante, pas de GPU cloud payant, pas de nouveaux cron.
- Pas de mutation de \`main\`, pas de fusion automatique, PR DRAFT.
- Les programmes proposés sont exécutés en sous-processus limité
  CPU/mémoire/temps avec AST restrictif ; l'oracle appartient
  seulement au runner de confiance.
- Les tests cachés sont évalués une seule fois après les générations
  et le choix symbolique ; ne pas les utiliser pour réparer un modèle
  ou un candidat dans la même expérience.
- Un gain sur ces 12 exemples synthétiques serait **exploratoire**,
  pas une généralisation de Python, ni une compétence autonome,
  ni un modèle qui s'est auto-entraîné.
- Si le SYM-1EDIT réussit autant ou mieux, cela montre l'intérêt
  d'une approche hybride ; pas la supériorité absolue de ce solveur.
- Le contrôle du format est essentiel : ne pas comparer un échec
  de formattage du modèle de base à une erreur algorithmique.

**Prochaine vérification après ce run :** nouvelles familles, autre
modèle/seed et collecte d'exemples d'erreurs sélectionnées par Omega,
sur tests indépendants. Ne pas réutiliser ce holdout comme
« nouveau » après inspection.
