# OMEGA-PY-LEARN-02 — protocole préenregistré avant inférence

Date : 22 novembre 2026. PR expérimentale empilée sur #232.
Aucun résultat de ce pilote n'était connu lors de l'écriture du protocole.

## Pourquoi ce pilote

Le précédent essai réel OMEGA-PROG-LEARN-01 a obtenu B_direct=0/36,
B_transfer=0/36. Plusieurs programmes étaient syntaxiquement invalides,
avec SyntaxError, et le modèle recevait seulement INVALID_PYTHON_SYNTAX,
non le message du compilateur.

Nous testons une pédagogie explicite : réparer du Python, lire les messages
exacts du compilateur, puis tenter un transfert à des programmes inconnus.

## Trois notions à distinguer

1. Syntaxe : ast.parse accepte le code, l'API restreinte autorise ses
   appels, et l'exécution reste dans les quotas.
2. Comportement : réussite sur les exemples et holdout d'un programme inconnu.
3. Transfert : changement de réussite sur un autre programme inconnu,
   après l'atelier syntaxique et un épisode de reconstruction.

Aucun de ces niveaux ne prouve un apprentissage de poids.

## Exercices pédagogiques — source visible et feedback exact

Trois exercices de correction dont la source erronée est donnée au
modèle, sans solution :
- chaîne avec barre oblique inversée non échappée ;
- boucle for sans deux-points ;
- accolade fermante superflue.

Deux tentatives par exercice. Après la première : SyntaxError exact,
message, ligne source et position, et résultats sur deux cas publics.
Le modèle produit lui-même les corrections. Mesures de validité
syntaxique et de comportement séparées.

Ces exemples sont distincts des deux programmes inconnus C et D.

## Nouveaux programmes cibles — pas les anciens A/B

- C : transformation de chaînes par fragments alphabétiques adjacents,
  normalisation de casse et séparateurs.
- D : transformation de chaînes maintenant un inventaire de lettres
  sans répétition, par ordre de première occurrence.

Les descriptions précédentes sont destinées à l'évaluateur, jamais au
modèle. Le modèle voit sept observations d'entrées/sorties et peut
choisir au maximum trois sondes supplémentaires.

Graine pour les cas cachés : 98537. Alphabet ASCII défini dans le
script; 40 cas cachés par tâche, disjoints des sept exemples et sept
cas de développement. Aucun résultat caché n'est divulgué au modèle.
Une seule correction après feedback de développement (quatre échecs max).

## Bras comparatifs et budget

- D_baseline : 3 appels avec feedback Python précis.
- Syntaxe : 6 appels (2 par exercice).
- C_training : 3 appels.
- Synthèse de leçons générales : 1 appel.
- D_transfer : 3 appels, mêmes exemples et 40 cas cachés que D_baseline,
  mêmes plafonds de sortie et mêmes diagnostics de compilateur.

Total prévu : 16 appels; température zéro, seed modèle 47621.
Caps : 120 sondes, 720 code, 720 réparation, 450+480 par cours,
220 pour la leçon.

D_transfer bénéficie de 10 appels supplémentaires et d'un contexte
plus long, donc les budgets totaux ne sont pas égaux. Une différence de
score serait un signal exploratoire, PAS une preuve d'effet causal ni
d'apprentissage neuronal.

## Environnement et intégrité

- Branche expérimentale sur Abrasax63/Omega-pub, main inchangée;
  pas de dépôt privé créé. Matériel exclusivement artificiel.
- Python généré dans un subprocessus, AST restrictif, quotas CPU,
  mémoire/temps, environnement sans secrets, imports interdits.
- Github Actions CPU, llama.cpp b12633, Qwen2.5-3B Q4_K_M.
- SHA-256 du modèle vérifié :
  9c9f56a391a3abbd5b89d0245bf6106081bcc3173119d4229235dd9d23253f94
- Sans API payante, sans nouveau cycle, sans entraînement de paramètres,
  sans promotion automatique, sans fusion.
- Sorties brutes, code, scores, tokens archivés. Un nouveau protocole
  doit utiliser un autre holdout; pas de relecture opportuniste.

## Critères de progrès

- Ateliers : nombre de codes Python valides sur trois, et réussite sur
  les cas publics.
- C : syntaxe, première réussite, correction, 40 tests cachés.
- D_baseline vs D_transfer : résultats sur 40 tests cachés identiques,
  validité syntaxique et coût.
- Zéro gain => aucune preuve de transfert. Gain => signal exploratoire
  non causal. Seul un entraînement séparé avec poids mis à jour pourrait
  démontrer cette autre forme d'apprentissage.

Ne jamais transformer une exécution CI verte en preuve d'apprentissage.
