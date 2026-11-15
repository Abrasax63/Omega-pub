# OBS-COL-06 — Amendement après le premier run (non pré-enregistré initialement)
Date : 2026-11-15.

**Constat avant modification :** exécution #43719763333, 10/10 tests OK,
cinq modèles connus reconnus, avertissement OOD correct ; toutefois le monde
`MEMORY_TOGGLE` est identifié avec seulement les sondes `q03` et `q05`,
dont les traces ne donnent **pas encore** de témoin direct de non-Markov.
Le monde `MEMORY_SET` en fournit un.

**Correction méthodologique explicitement post hoc :** après la sélection
et **avant** toute ouverture des observations réservées, si la famille
provisoire est à mémoire et qu'aucun contre-exemple de Markov n'a été
observé, choisir la moins coûteuse des sondes d'entraînement déjà déclarées
qui **devrait** produire, selon le modèle candidat, deux successeurs visibles
différents pour le même couple (état visible, action). Demander à Omega P1
de préparer la vérification, consulter l'oracle réel, puis émettre le
certificat seulement si les deux transitions mesurées le prouvent.
Si cette sonde contredit également la famille, réviser les survivants.

Ne pas confondre cette épreuve de falsification avec le score de
planification comparé à l'oracle classique : elle utilise une requête
**supplémentaire** et sera comptée à part.

Prochain contrôle décisif : obtenir un témoin direct sur MEMORY_TOGGLE
sans introduire d'information réservée, tout en conservant l'alerte OOD
et les contrôles antérieurs. Aucun gain de performance Omega revendiqué.
