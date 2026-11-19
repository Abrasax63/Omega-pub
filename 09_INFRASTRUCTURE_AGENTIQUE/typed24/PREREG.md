# TYPED24 — formule typée, alternatives d'interprétation et garde de fidélité

**Préenregistrement figé le 19 novembre 2026 avant le code et les appels.** Branche expérimentale héritant de EXT23 #208, sur laquelle SEM22 #207 est présent ; pas de fusion ni modification de `main`.

## Besoin
SEM22 sait valider mathématiquement certaines propositions, mais pas les comprendre hors des documents normalisés. EXT23 a montré une couverture de 0/12 sur des textes extérieurs. Plutôt qu'un deuxième solveur, construire le **raccord entre un lecteur à citations et un vérificateur exact**, avec IR typée explicite, ambiguïtés et contre-interprétations.

## Contrat
- Entrée : bytes UTF-8, hash Git blob attendu, et chemin source ; même `Reader12` déjà présent pour prouver que les segments de définition et d'énoncé existent vraiment.
- Déclaration complète **finie et bornée** : domaine et codomaine explicites `Z/nZ` égaux, paramètres entiers canoniques bornés `2 <= n <= 64`, expression exclusivement affine `ax+b` ou quadratique `ax²+b`, modulo n explicite, aucune interprétation implicite d'un `n` libre ou d'un corps général.
- Compréhension : grammaire contrôlée pour quelques variants FR et EN, chaque sémantique exprimée sous un objet typé (fonction + prédicat + quantificateur + provenance). Un modèle peut proposer une IR mais ne peut jamais imposer la signification ; toute proposition doit être reconstruite et comparée à la source.
- **Ambiguïté** : une proposition comme « possède un point fixe » admet à la fois `exists >= 1` et `exactly 1`. Le système conserve les **deux alternatives**, calcule leurs conséquences, et **s'abstient même si leurs verdicts coïncident sur le cas particulier**. Deux interprétations structurées non équivalentes ne sont jamais résolues par simple vote.
- La vérification par calcul exact est **déléguée à `semantic22/checker.py`**, déjà audité, pas réécrite. Aucun texte de source inconnu ou implicite ne reçoit TRUE/FALSE. Les décisions sont `VERIFIED_TRUE`, `VERIFIED_FALSE`, `AMBIGUOUS`, `INDETERMINATE`, `INVALID_SOURCE` ; les deux derniers sont des refus, pas des erreurs calculées.
- Si la proposition est claire, le système prépare une citation littérale via `reader_bridge12/gate.py` et la conserve en statut quarantaine. **Jamais** de règles Horn, de certification Lean, ni de promotion automatique.
- Deux interprétations candidates issues du texte doivent être comparées sur *leurs formes typées*, pas seulement sur leur valeur booléenne pour un exemple. Le test doit montrer au moins un cas où elles diffèrent et un cas où leurs valeurs coïncident mais l'ambiguïté demeure.
- Aucun nouveau modèle nécessaire pour tester le raccord ; les expériences CPU Qwen antérieures restent séparées. Pas d'API payante.

## Tests
- Figés avant code : cas positifs/clairs vrais et faux, variantes d'expression, quantificateurs explicites, homographies/domaines invalides, incohérences de module, définitions multiples, absence de domaine, injection, consigne cachée, ambiguïtés.
- Comportements examinés : exactitude sur cas contrôlés, citations valides, 0 promotion ; **aucun faux `VERIFIED_TRUE`** sur cas négatifs ; aucune régression de SEM22 (168 propositions).
- EXT23 12 extraits **déjà vus** = uniquement contrôle de refus ; ne pas les compter comme nouveau holdout ni en tirer un succès de généralisation. Une épreuve externe réellement nouvelle devra être gelée et examinée séparément.
- Les cas contrôlés fabriqués par l'équipe sont un **test de contrat**, pas une évaluation aveugle de compréhension mathématique réelle. Ne pas modifier les cas après avoir vu les sorties pour annoncer un succès.

## Références méthodologiques
- Autoformalization with Large Language Models (Google Research / NeurIPS 2022), LeanDojo (NeurIPS 2023), Towards a Common Framework for Autoformalization (AAAI 2026), Improving Autoformalization Using Type Checking (2024), Validating Autoformalized Specifications via Contrapuntal Languages (2026).
- Intérêt : formalisme vérifiable, typage, recherche de prémisses, comparaison d'interprétations, et tests de fidélité. Ces travaux **ne prouvent pas** que l'implémentation locale est sémantiquement fidèle.

## États scientifiques
Périmètre normalisé = **CALCUL EXACT** ; fidélité à des textes humains complexes, transfert hors domaine et apprentissage d'un modèle = **INDÉTERMINÉ**. Le système doit toujours pouvoir répondre « je ne sais pas ».
