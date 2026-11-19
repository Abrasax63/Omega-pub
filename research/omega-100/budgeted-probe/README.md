# Prétester des colorations avant la propagation sous budget partagé

19 novembre 2026, 14 h 57 (Paris). **IMPLÉMENTÉ / EXÉCUTÉ / non-régression globale RÉFUTÉE par un témoin construit.** Branche `experiment/omega-100-2026-11-18`, départ `8ee38a37a81059bee9f4cbb0bfcc36485a7d011c`. Pilote hors numérotation, suite de la [règle structurelle](../structural-choice/README.md).

[Protocole](protocol.md) figé avant test. Question : une courte recherche directe améliore-t-elle la couverture sans épuiser le budget nécessaire à la propagation ? Sur les graphes signés d'au moins 22 arêtes, le candidat essaie les masques 1 puis 2. Il rend une réponse seulement après avoir testé toutes les relations pour le masque accepté. Sinon, il appelle la propagation B avec le budget restant. Plafond de prétest 42, plafond commun 64, une unité par masque ou relation explorée. Le reste des cas passe par la règle inchangée. Les inspections du routage sont facturées en temps aux deux politiques, sans unités de solveur, comme au pilote précédent. Le prétest, lui, débite chaque opération. Aucun modèle ni API.

Le contrôle négatif avec deux contraintes incompatibles sur une paire passe : aucune fausse déclaration de cohérence. L'oracle exhaustif étiquette à part les 28 entrées réservées (24 graphes de six classes et quatre sommes), puis vérifie aussi les témoins positifs. Les cas ont été créés après gel du harnais et du candidat. La comparaison de temps utilise 300 passages complets, ordre tournant, décision et résolution incluses, oracle de notation exclu pour tous.

| Réserve appariée | Corrects | Abstentions | Erreurs | Étapes cumulées | Temps médian lot |
| --- | ---: | ---: | ---: | ---: | ---: |
| Règle structurelle de référence | 19/28 | 9 | 0 | 1 046 | 180,16 µs |
| A fixe | 12/28 | 16 | 0 | 1 339 | 151,22 µs |
| Prétest puis B | 23/28 | 5 | 0 | 928 | 170,43 µs |

Le seuil de la réserve est atteint : quatre gains, zéro perte et zéro erreur. Les gains sont concentrés sur les quatre graphes construits autour d'un masque précoce. Les quatre sommes restent à 3/4 dans le même protocole. La médiane par résultat exact passe de 9,48 à 7,41 µs. Cette mesure dépend du mélange de cas et de ce poste.

[Falsification supplémentaire](stress-protocol.md) figée après la réserve, candidat inchangé. Sur un graphe de 10 sommets et 25 arêtes, les sommets 0 et 1 sont isolés. Les masques 1 et 2 satisfont les 24 premières relations, toutes nulles, avant l'inégalité finale qui contredit une égalité sur la même paire. Le prétest consomme 42 unités et laisse 22 unités. La construction de B nécessite déjà 25 insertions. Le candidat s'abstient à 64 unités. B seul donne le bon verdict en 36 unités. L'oracle exhaustif confirme l'incohérence. Ce témoin explique la perte par le budget et non par une erreur de verdict. Il est construit après la réserve et n'est pas compté dans le tableau.

**Décision.** La référence reste la règle structurelle. Le candidat est archivé comme preuve d'un gain local et d'une perte reproductible de couverture. Les 16 tests métier et les contrôles du harnais passent. Prochain test proposé : remplacer l'ordre « essayer puis reconstruire le graphe » par une propagation de parité incrémentale qui traite aussi les contradictions pendant la lecture, puis la comparer sur de nouvelles familles de graphes sous le même plafond, avec ce témoin comme non-régression de développement.

Reproduction : reprendre `solver.py` et `rule.py` comme dans la [règle structurelle](../structural-choice/README.md). Placer ces modules avec le candidat et les harnais dans un dossier temporaire.
```sh
python probe_trial.py CAS_RESERVES.json
python stress.py
```
Le fichier de réserve est une liste d'objets avec `group` (nom de la classe) et `case` (format du pilote précédent). Les corrections et les entrées individuelles ne sont pas publiées. Seul le témoin de falsification explicitement construit est fourni dans `stress.py`. Sources et mesures : [réserve agrégée](results.json) SHA-256 `ddbae19e2cc1d90676c6576e8b8e400d28883ea216ed16b5ca2bf67abf75a9`, [témoin](stress.json) `a8176da04a0f7462fcccfebed1ed49a47c01044352525c7f5f1d0095c9a140d1`, [empreintes gelées](freeze.sha256).
