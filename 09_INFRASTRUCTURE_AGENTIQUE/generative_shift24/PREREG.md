# Omega GEN24 — préenregistrement de la transformation générée par un modèle local

Date : 2026-11-19. **Écrit avant toute génération de corpus, avant code et avant inférence.** Branche isolée créée depuis `main` ; aucune modification de `main`, aucun appel API payant.

## Objectif falsifiable
Tester si le petit modèle Qwen2.5-Coder-3B-Instruct Q4_K_M, en inférence CPU réelle, peut **proposer une autre représentation** d'un problème dont il ne reçoit ni la liste de stratégies connues, ni exemples résolus, ni les cas de test. Les transformations viables seront vérifiées par des oracles finis indépendants et comparées à un **algorithme classique fort**, sans conclure à une créativité autonome de frontière.

## Problème NOUVEAU pour ce pilote
« Jeu de commutateurs binaires » : un état est un entier `s` sur `n` bits; chaque action `m` dans une liste `moves` remplace `s` par `s XOR m`; les actions peuvent se répéter et être utilisées dans n'importe quel ordre. Déterminer si `target` est atteignable à partir de `start`.

**Interdiction de divulguer au modèle** : le solveur classique exact, la relation espace vectoriel / rang, les valeurs attendues, les fixtures, les expressions correctes et les échecs des essais. Les paramètres de validation (n, moves) ne sont pas dans le premier prompt sauf description générale. Le domaine a pu être vu en préentraînement du modèle; il n'est pas inédit en mathématiques.

## Deux temps d'inférence à geler avant oracle
1. **IDÉATION libre** : prompt français ou anglais décrivant seulement les règles du jeu et demandant « propose une représentation alternative utile (non une seule recherche état par état), décrit un invariant, ses limites; pas de code ». Aucune primitive de solution ni exemple de transformation montré. Réponse brute archivée.
2. **FORMALISATION guidée par langage, pas par solution** : second prompt avec réponse brute précédente (marquée données), demande une expression booléenne sur `moves,start,target`. La syntaxe autorise seulement `rank(matrix)`, `popcount(integer)`, `len(list)`, `moves`, `start`, `target`, `^` bitwise XOR, `+` concat de listes, `[expr]` singleton, comparaisons `==, !=, <, <=, >, >=`, `and,or,not`, littéraux numériques 0..1023. Ne pas donner de recette de rang. La présence de `rank` rend le langage favorable à un candidat de type algèbre linéaire ; cela limite la conclusion. Le programme n'exécute pas du Python produit par le LLM; il le **parse** et l'interprète sur un AST limité, sans eval, import, attribut, indexation, boucles ni fonctions d'extension.
3. Appeler le modèle avec **deux formulations préfixées P1 et P2** de l'étape d'idéation, identiques dans leurs règles, température zéro, `max_tokens=320` idéation puis `max_tokens=160` formalisation. Quatre appels, aucune réparation/adaptation après voir une erreur. Chaque génération est évaluée et archivée, même invalide; aucun choix humain du meilleur candidat. Le model sera identifié par SHA du poids et llama.cpp SHA du code (mêmes artefacts CPU utilisés dans Reader18).

## Jeu de validation et égalité des tests
**Avant les appels LLM**, figer et committer exactement 64 instances test dont 32 atteignables et 32 inatteignables, n dans [5,8], 2..5 actions à bits entiers; même corpus pour les deux sorties P1/P2 et le témoin. Générateur PRNG xorshift32 initialisé par `0x26A11E24` et algorithme de construction explicité dans le manifeste; les cas sont synthétiques et **les labels du gold ne sont jamais inclus dans les prompts ni dans l'entrée du modèle**. Figer les données source et gold séparément avant d'écrire l'évaluateur. Aucun ajustement du banc aux réponses du modèle.

Témoin indépendant **A (référence brute)** : parcours BFS des états accessibles parmi `2^n` états, sans algèbre linéaire. Témoin **D (fort)** : base GF(2) construite par élimination des pivots des masques, puis réduction de `start XOR target`; calculée dans un module distinct de l'interpréteur candidat. Vérifier BFS=D sur les 64 cas. Comparer C1/C2 pour exactitude, abstention, erreurs silencieuses, taux d'expressions acceptées, coûts tokens/latences. Conserver A et D même si C échoue. Le modèle ne doit jamais être comparé à une force brute seule pour annoncer une innovation.

**Contrôles hors distribution synthétique** : pour chaque cas, ajouter 3 métamorphismes (reordonnancement des actions, permutation de l'ordre des masques, translation XOR de start et target par le même masque); vérifier équivalence du gold et de chaque candidat, soit 192 contrôles. Le même modèle de formule reste figé.

## Contrôle d'attribution et nouveauté
La première idée doit contenir, avant la présentation des primitives, une famille reconnaissable `espace vectoriel / vector space / linear span / rang / rank / base linéaire / Gaussian / GF(2)` pour qu'une formule de rang dans la seconde réponse soit qualifiée de **cohérente avec l'idée première**. Cet indicateur à mots-clés est un proxy étroit : sans expertise humaine indépendante, ne pas revendiquer la fidélité sémantique.

**Classification** :
- `MODEL_PROPOSED_FORMULA_VALIDATED` : formule syntaxiquement acceptée et 64/64 décisions exactes + 192 métamorphismes + formulation initiale de même famille.
- `FORMULA_VALID_BUT_ORIGIN_UNVERIFIED` : formule exacte mais origine sémantique du second prompt incertaine.
- `FORMULA_REFUTED` : divergence contre BFS, témoin exact minimal.
- `ABSTAIN_PARSE_OR_SCOPE` : expression refusée, jamais un résultat faux.
- `NO_VALID_TRANSFORMATION` : rien ne passe, résultat négatif également utile.

**Ne pas promouvoir automatiquement** : formule juste sur 64 cas != théorème général, nouveauté mathématique, créativité autonome ouverte, apprentissage de poids, performance supérieure à D ou transfert scientifique. Si C=D en exactitude et inférieur en coût, le rapport doit clairement le signaler. Aucune fusion, aucun auto-déploiement. À la fin, recommander un test d'un domaine vraiment inhabituel et un annotateur indépendant, sans recyclage de ces fixtures.

## Conditions d'échec strictes
Environnement CPU Qwen non disponible → `MODEL_NOT_EXECUTED`, pas de réussite prétendue. Si les deux idées échouent, garder les sorties brutes et classer négatif. Si le banc est corrompu, interrompre, pas réécrire la cohorte. Interdiction de juger uniquement la validité du JSON ou une analogie en langue naturelle comme preuve d'équivalence.
