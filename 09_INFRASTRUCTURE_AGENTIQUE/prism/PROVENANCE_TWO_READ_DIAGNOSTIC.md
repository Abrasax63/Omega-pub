# Comparaison figée à deux lectures — 14 novembre 2026

Base `fad3b9626907dc47ac131bd84a657852fe406b8a`. Le script joint et les deux modules ont été hachés avant la recherche des jobs : `123be6c20def7089a3923760f8407a3b59299675d6340b12efdac26647439f9f` (script), `13cc918f6bd9d1aacb6b07221b24706810f5f93751de3cffe4f10e4481cba1e9` (sélection), `f78e1c77edf6f24fae8b751a7e191dc9da55f38d31a04ee1c328174a944641b9` (extracteurs). L'inventaire a été fourni et les cibles ont été choisies après examen des logs. Les programmes ont reçu les journaux complets sans étiquettes. Les trois essais ont été collectés en lecture GitHub autorisée.

| Job | SHA-256 du journal | Omega / fixe |
|---|---|---|
| [Vérification tarball](https://github.com/curl/curl/actions/runs/43556794941/job/132331367026) | 3fb7c610471b33d9c11b7a82a5a8d3f11a6ec4ca1f69e23dfdf79eb2dd2bec92 | indéterminé / indéterminé |
| [Intégration CMake](https://github.com/curl/curl/actions/runs/43528101630/job/132238746665) | 9f4a17da21e71e75127f2b44b6ace5b43138c2405e056fdbb8303c1135e76bad | indéterminé / indéterminé |
| [Orthographe](https://github.com/curl/curl/actions/runs/43556794915/job/132331367147) | 627906f7365f085f9c0e5a7853f99d72d4fd9e8270306b9903b46419fcb8bd14 | indéterminé / indéterminé |

Le cas CMake fournit un recalcul documenté : le [script épinglé](https://github.com/curl/curl/blob/1cfd324c184754414096997c541c6ba0973e1c37/tests/cmake/test.sh) redirige la sortie de git archive | gzip vers source.tar.gz, tandis que le journal rapporte l'exécution et la vérification du fichier. Les deux méthodes manquent ce cas. Le lot ne contient pas de copie évaluée avec une vérité terrain distincte.

Les deux méthodes utilisent les mêmes extracteurs Bash et BuildKit. Dans ce harnais, seul le journal produit une observation : la pièce script lue par la règle fixe est ignorée par le code et le même fichier avait été fourni aux trois cas. Les trois lectures Omega contre six lectures fixes ne comptent donc pas comme un gain. L'essai est un diagnostic de couverture, sans comparaison valide d'une politique qui exploite réellement la seconde pièce. Les 24 tests locaux passent.
