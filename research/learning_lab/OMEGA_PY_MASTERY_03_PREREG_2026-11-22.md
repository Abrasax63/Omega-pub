# OMEGA-PY-MASTERY-03 — protocole gelé avant modèle réel

Date : 22 novembre 2026, programme scientifique Omega.
**État au dépôt : hypothèse et méthode, aucun résultat V3 connu.**

## Audit de non-duplication (état antérieur)

- PR #79 : boucle de révision d'un vérificateur de provenance (sans
  génération libre de code ni modèle entraîné).
- PR #81 : laboratoire de vérificateurs et contrôle de provenance, réutilisé
  conceptuellement mais ne démontre pas l'apprentissage de Python.
- PR #232 (V1) : Qwen3B reconstruit deux programmes, B_direct=0/36,
  B_transfer=0/36. Python fréquemment invalide.
- PR #233 (V2) : formation sur trois exemples, D_direct=11/40,
  D_transfer=0/40 ; politique Python interdisant une méthode sûre,
  et une correction auparavant valide perdue.

V3 NE RÉINVENTE PAS le runtime : il importe les contrôles d'AST, le processus
restreint et le client local de V1, et le diagnostic de compilateur de V2.
Nous n'acceptons pas la répétition des 40 holdouts déjà divulgués.

## Modification minimale de méthode

1. **Cursus de trois micro-exercices** différents de V2 : deux-points d'un
   if, indentation du bloc, guillemets triples non terminés. Deux essais par
   exercice, diagnostic réel de Python et tests publics.
2. **Conservation non destructive de la meilleure version** : choix uniquement
   selon la validité AST/politique puis le score sur les exemples publics;
   jamais selon le test caché. Même une sortie JSON incohérente ne peut effacer
   une version valide. Toujours archiver TOUTES les tentatives, y compris
   régressions.
3. **Examen de maîtrise** : 3 entrées inédites par exercice non transmises
   au modèle. Seuil gelé : **au moins 2 des 3 exercices** intégralement corrects
   sur ces entrées, et compilables. Sans ce seuil, arrêter l'essai;
   ne pas lancer une « généralisation » fictive.
4. **Diagnostiques distingués** : JSON/transport, SyntaxError exact,
   restrictions de sécurité AST et erreurs de comportement.
5. **Correction de l'évaluateur** : autoriser les méthodes Python sûres
   str.isalnum et list.insert pour éviter de qualifier leur usage comme
   une incapacité à programmer.
6. **Nouveaux programmes cachés** : E, extraction de groupes numériques avec
   normalisation; F, sélection de segments alphabétiques distincts.
   Descriptions destinées UNIQUEMENT à l'évaluateur.

## Test aveugle / plan

- F_direct avant tous les cours : 7 observations + jusqu'à 3 sondes du
  modèle + une écriture et une correction après feedback de développement.
- 3 micro-exercices : 6 appels.
- Si seuil non atteint : STOP, rapport publié avec F_direct seulement.
- Si seuil atteint : E_training (3 appels), synthèse de leçons (1),
  F_transfer (3), même 7 observations et 40 entrées cachées F, mêmes limites.
- 40 entrées cachées inédites par E/F, graine 281119, aucune récupération
  des anciens C/D ou A/B. Aucune sortie cachée au modèle.
- Budget maximal : 16 appels du même Qwen2.5-3B-Instruct Q4_K_M;
  le nombre réel dépend du seuil. Graine modèle 47621, température 0.

**Critères** :
- progrès syntaxique (programmes valides),
- maîtrise de l'exercice (3/3 cas inconnus),
- score fonctionnel sur E,
- score F_direct vs F_transfer sur les mêmes 40 cas cachés.
- « gain durable » NON ÉTABLI même si les scores augmentent :
  pas de mise à jour des poids, coûts totaux différents et une seule
  réalisation; il faudra un second protocole avec données nouvelles
  et entraînement/séparation appropriés.

## Sécurité, coût et gel des paramètres

- Projet branché sur #233, main inchangée, PR DRAFT, aucune fusion.
- Le dépôt reste PUBLIC : aucun dépôt privé créé.
- Aucun secret ni donnée confidentielle; programmes artificiels.
- Aucun cron nouveau, aucune modification par le modèle des fichiers Git.
- Sandbox Python AST restreint, subprocessus à durée/CPU/mémoire limités,
  interdiction import/IO/network/introspection; fichiers temporaires locaux
  au runner seulement.
- GitHub Actions runner CPU, llama.cpp b12633, modèle connu Qwen2.5-3B GGUF
  Q4_K_M, SHA fixé :
  9c9f56a391a3abbd5b89d0245bf6106081bcc3173119d4229235dd9d23253f94
- Aucun appel à une API payante, aucun gradient/LoRA.
- Archive des sorties brutes, décisions de sélection, scores cachés, tokens
  et temps. Aucun changement a posteriori des exemples, du seuil ou du prompt
  pour présenter un même test comme indépendant.

## Point d'attention épistémique

Les exercices de formation restent supervisés par leurs exemples publics.
Le score de maîtrise sur exemples inconnus vérifie le transfert local
d'une règle Python; il n'atteste pas la compréhension du langage au sens large.
Une PR verte ne suffit pas : il faut lire les sorties et les échecs.

**Après ce run** : décider si un apprentissage de paramètres à partir de
corrections validées serait pertinent. Si le cursus et la maîtrise échouent,
ne pas nourrir un entraînement LoRA avec des pseudo-corrections fausses.
