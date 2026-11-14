# Raccord entre journal CMake et script épinglé

Cycle du 14 novembre 2026, base `219b5f6803db909b9fa50ea87894f9a31174a0c2`. Ce cycle rejoue le défaut du [diagnostic à deux lectures](PROVENANCE_TWO_READ_DIAGNOSTIC.md) sur les mêmes pièces autorisées. L'identifiant de la recette curl et son empreinte ont été choisis après examen du cas CMake. Les deux autres jobs sont des témoins de non-déclenchement déjà vus dans le diagnostic.

| Job | Référence précédente | Candidat | Comparateur fixe avec le même filtre | Lectures candidat / fixe |
| --- | --- | --- | --- | --- |
| [Tarball](https://github.com/curl/curl/actions/runs/43556794941/job/132331367026) | indéterminé | indéterminé | indéterminé | 1 / 1 |
| [CMake](https://github.com/curl/curl/actions/runs/43528101630/job/132238746665) | indéterminé | recalcul | recalcul | 2 / 2 |
| [Orthographe](https://github.com/curl/curl/actions/runs/43556794915/job/132331367147) | indéterminé | indéterminé | indéterminé | 1 / 1 |

Le script [tests/cmake/test.sh au commit épinglé](https://github.com/curl/curl/blob/1cfd324c184754414096997c541c6ba0973e1c37/tests/cmake/test.sh) montre la redirection de `git archive | gzip` vers `source.tar.gz`. Le candidat exige le checkout, la séquence journalisée, la même destination jusqu'à la vérification CMake et la concordance du hash transmis à CMake. Il demande ensuite le script épinglé et vérifie ses octets. Script contradictoire, cible différente, hash CMake différent et vérification absente donnent chacun une abstention des deux côtés. Seul le script contradictoire atteint la seconde lecture.

Empreintes SHA-256 des journaux dans le diagnostic précédent. Script curl `15bd0498374856547ac50d9324c8e85f30c7a335a3af1db237ff09e27a3a7513`. Candidat `755cb0f563b9ef462e7e12d8a6ce23c64baedf45ab469604728e22c1145a3fdb`. Harnais `efd0f7a92f7342491e96c930641f821d4c0f654d646b3373d90df3ba898037c6`.

Pour rejouer, lancer `python3 provenance_trials/curl_archive/compare.py manifeste.json` depuis prism. Le manifeste contient une liste d'objets `job`, `output`, `journal` (chemin du texte du journal) et, pour CMake uniquement, `script` (chemin des octets épinglés).

Verdict : une confirmation supplémentaire sur le cas de diagnostic, égalité avec la règle fixe. 24 tests locaux du laboratoire et 5 du prototype passent. Aucun cas réservé annoté distinct ni nouveau workflow externe admissible dans ce rejeu. Le parcours propose/check ne s'applique pas à ce diagnostic de journaux bruts. Le candidat reste archivé pour le prochain cycle et la référence active est conservée.
