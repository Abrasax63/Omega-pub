# OMEGA-ABSTRACTION-REAL-01 — protocole figé AVANT inférence

Date : 2026-11-22. Statut : **préenregistré, un seul essai réel, aucun résultat connu au moment de ce fichier**. PR #231, branche expérimentale uniquement.

## Questions falsifiables

1. Un modèle local de 3B paramètres choisit-il de lui-même des notions à chercher dans trois pages extérieures non préparées, et peut-il conserver **au moins deux fiches avec une citation textuelle exacte** ?
2. Sans couple préparé par le chercheur, choisit-il deux fiches et des exemples de relations finies exploitables ?
3. L'intersection des propriétés proposées tient-elle quand on change d'encodage et d'étiquettes ? Les conjectures trop fortes sont-elles rejetées sur les exemples ?
4. Sur quatre nouvelles relations finies, un contexte d'abstraction non certifié (B) change-t-il l'exactitude par rapport à la lecture directe (A) et à la garde exacte (C) ? **Le contexte supplémentaire rend les budgets d'entrée inégaux : ne pas attribuer causalement un gain.**

## Source scientifique primaire et absence de prémâchage

Livre externe accessible publiquement, qui n'est pas le PDF Rubinstein utilisé dans les essais précédents :
Richard Hammack, **Book of Proof, third edition**,
https://richardhammack.github.io/BookOfProof/Main.pdf .
La source possède une licence CC BY-NC-ND 4.0 ; ne pas republier le livre ni ses pages extraites.

La sélection de pages physiques est déterministe mais inconnue du modèle et de la PR au moment de l'écriture : `Random(SHA256(pdf_bytes + OMEGA-ABSTRACTION-REAL-01-2026-11-22))`, trois indices distincts entre 30 et `min(total_pages-10,240)`.
Le modèle ne reçoit QUE les trois pages sélectionnées, sans annotations, réponses, thèmes choisis, solution ou représentation pré-élaborée.
Aucune nouvelle page ne remplace une page mal extraite : l'expérience s'arrête.

Le modèle choisit une recherche par page. Le récupérateur fixé de la PR #230 peut retourner jusqu'à deux extraits encyclopédiques avec ID de révision, URL et empreinte.
`incremental_math_library.run(...max_hops=1)` produit jusqu'à trois fiches brutes. Toutes restent en **quarantaine**.
Aucune amélioration de la fidélité sémantique ne peut être inférée d'une citation correcte.

## Modèle et calcul

- **Qwen2.5-3B-Instruct Q4_K_M** de `bartowski/Qwen2.5-3B-Instruct-GGUF`, poids ouverts, environ 1,93 Go ; repo source identifié. Le téléchargement initial via l'URL `resolve/main` ne garantit pas à lui seul une révision figée ; conserver et afficher le SHA-256 du fichier utilisé et le commit distant si disponible.
- llama.cpp b12633, release `llama-b12633-bin-ubuntu-x64.tar.gz`.
- Runner Ubuntu GitHub Actions, CPU seulement `-ngl 0`, `-c 6144`, `-t 2`, une seule instance, pas d'API payante.
- température zéro, seed 9123, sortie plafonnée : requêtes 52 tokens, fiches 550, abstraction 1000, exercices 260.
- `response_format=json_object` uniquement pour les réponses structurées (pas les recherches), afin de limiter les erreurs de JSON. Ce mode ne fournit pas de concepts ni d'axiomes mathématiques pré-résolus.
- Temps, nombre d'appels, métriques de tokens retournées par le serveur, versions et SHA archivés.

Ce nouvel essai n'est PAS une comparaison causale avec le 0,5B : taille, modèles et format changent simultanément.

## Construction d'abstraction

Le modèle choisit lui-même deux des fiches admises, ou s'abstient.
Les identifiants SHA longs peuvent être exposés comme alias opaques `C1`, etc. (sans information mathématique).
Le modèle dessine ses propres exemples finis et conjecture une liste de propriétés dans une grammaire de huit propriétés **fixée à l'avance**. Le moteur `concept_abstraction_lab` teste les propriétés, les permutations, matrice/arêtes, contre-exemples.

**Un rapprochement de texte et une représentation choisie par le modèle ne sont pas une interprétation démontrée de la source.**

## Évaluation aveugle sur quatre tâches nouvelles

Un oracle exact génère quatre relations finies sur trois sommets, aléatoirement depuis le SHA du PDF et un sel fixe `blind-finite-holdout-v1`. Les relations ne sont pas vues pendant l'acquisition de sources.
Le modèle est interrogé avec la même question de classification d'axiomes :
- A : relation + définitions des huit propriétés ;
- B : la même relation + définitions + résumé d'abstraction inventé par le modèle, explicitement non vérifié ;
- C : contrôle exact de la réponse B et abstention si erreur (oracle explicite). **C ne représente pas un gain cognitif**.

L'oracle déterministe est exécuté après les appels A/B pour chaque relation. Aucun score ou étiquetage de vérité ne figure dans les prompts.
Si l'abstraction manque, la comparaison A/B/C est **bloquée**, sans remplacement synthétique.
Mesures : sorties brutes, JSON valides, concepts et requêtes choisis, exactitudes A/B, abstentions, tokens en entrée/sortie, calcul indépendant, coût.

## Conditions d'arrêt et intégrité

- Un seul run PR; aucun cron, aucune fusion vers `main`, aucune écriture Git, aucun accès aux secrets.
- Documentation, rapport et registres en artefact GitHub avec 7 jours de rétention ; pas de publication automatique en mémoire certifiée.
- Aucune falsification automatique des entrées de test : toute erreur de source, modèle, format ou transport reste visible.
- Éviter de rejouer les mêmes sources après examen : une nouvelle expérience exige de nouvelles pages et préenregistrement.
- Les résultats peuvent être négatifs ou indéterminés. Aucune découverte mathématique nouvelle ni autonomie générale revendiquée.

**Critère de progrès** : au moins deux fiches réellement citées et un essai d'abstraction ne prouve que la faisabilité de la chaîne. Seule une fidélité sémantique indépendante et une amélioration reproductible sur des tâches inédites pourraient soutenir une amélioration scientifique.
