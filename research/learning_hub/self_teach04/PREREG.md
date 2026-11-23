# OMEGA SELF-TEACH-04 — protocole préenregistré avant code et inférence

Statut initial : PROPOSÉ / NON EXÉCUTÉ. Parent figé : `eb8ce727acc114c41e832edd868d8c703968c709` (SELF-TEACH-03, résultats négatifs 2026-11-23).
Ce premier commit fige les données et critères; aucun appel modèle n'a eu lieu pour SELF-TEACH-04 au moment du gel.

## Question falsifiable
Une leçon générale tirée par Qwen2.5-3B après correction de tâches de segmentation en *runs contigus* améliore-t-elle son exactitude sur trois fonctions de segmentation inconnues, au-delà d'une réponse directe ET d'un conseil neutre ?
Il ne s'agit pas de proposer des tâches sans rapport : le concept commun est explicitement la fin d'un run, mais les cinq familles et les règles de sortie sont distinctes. Les données sont synthétiques, construites par le développeur, non découvertes par Omega.

## Ensembles fixes et partitions
- Pratique : 2 familles R1/R2, 5 exemples publics et 10 cas de développement par famille ; le modèle choisit la tâche la plus faible selon score initial.
- Test : 3 nouvelles familles Q1/Q2/Q3, 2 exemples publics et 6 tests cachés par famille, soit 18 tests. Les entrées du holdout ne sont pas montrées au modèle, aucune annotation n'est incluse dans la génération.
- Données JSON gelées dans ce commit Git initial, puis empreintes Git blob vérifiées par le générateur, par le scoreur et par les tests.
- Les familles et exemples ne sont pas réutilisés des PR #242, #244, #245; les anciens scores ne servent pas à choisir les cas.

## Plan d'exécution et limites
- Un seul essai Qwen2.5-3B-Instruct Q4_K_M local, SHA-256 fixé dans le workflow (modèle du run #45132083501), CPU, 0 API payante.
- Le générateur est basé sur le runner #245 : A réponse directe ; deux débuts de pratique ; 2 réparations max sur la tâche sélectionnée ; 3 échecs minimaux visibles par réparation ; une leçon candidate uniquement après amélioration stricte à 10/10 ; P consigne neutre ; B avec leçon.
- **Nouvelle garde SELF-TEACH-04** : si aucune leçon n'est admissible, B est un alias auditable des réponses P, sans appel de génération redondant ni comparaison stochastique P/B.
- Une correction n'est conservée que si elle améliore les 10 cas publics de développement sans écraser l'ancienne meilleure version. Un échec identique doit être identifié dans la trace, sans divulguer de tests cachés.
- Réponses JSON + Python sûr sous sandbox AST; mêmes plafonds de 660 tokens par sortie pour A/P/B si B est effectivement généré; une seule génération par tâche et par bras, sauf réparation de pratique. Conditions A/P/B NON causales à budget total différent. Pas d'entraînement LoRA (0 mise à jour de poids).
- Sauvegarder réponses brutes, SHA256, diagnostics exacts, prompts, rapport de score et temps/tokens mesurables, contre-exemples et retour arrière.

## Critères d'acceptation établis AVANT l'évaluation
1. Les tests logiciels et contrôles de séparation/sûreté passent ; zéro lecture de holdout par le générateur.
2. Une leçon propre doit être admise après amélioration stricte jusqu'à 10/10 sur pratique.
3. **B > A et B > P** sur les mêmes 18 tests cachés, et aucune tâche entièrement réussie initialement par A ou P ne doit régresser en B.
4. Si une garde échoue, verdict `NO_AUTONOMOUS_LEARNING_GAIN_DEMONSTRATED`; aucune leçon promue en mémoire certifiée.
5. Même si 2-4 passent, qualifier le résultat au maximum `EXPLORATORY_LESSON_TRANSFER_ONLY` : une seule petite cohorte synthétique ne prouve ni causalité, ni entraînement de poids, ni maîtrise générale.

Une CI verte vérifie l'exécution, pas l'apprentissage. Premier score consomme définitivement ces 18 tests. Pas de relance pour les qualifier de nouveaux. Pas de fusion ou écriture `main`.
