# OMEGA-REPRODUCTION-PROOF-10 — vérifier une reproduction de calcul, pas seulement son origine

Après les [PR #171](https://github.com/Abrasax63/Omega-pub/pull/171) et [#173](https://github.com/Abrasax63/Omega-pub/pull/173), ce pilote vérifie un **recalcul numérique effectué dans un second job GitHub Actions**, en refusant de certifier une reproduction à partir d'une simple égalité des sorties.

**Préenregistrement strict** enregistré avant code au [commit `e0e249e`](https://github.com/Abrasax63/Omega-pub/commit/e0e249e54900b3c77f3cd1a47902b606588304b9). Critères et contrôles négatifs fixés avant les résultats.

## Cinq exécutions réelles sur cinq jobs GitHub Actions

La CI `pull_request` lance une **matrice de cinq jobs distincts**. Chaque job repart d'un checkout, charge une dépendance Python réellement utilisée (`computation.py`), exécute `worker.py` dans un sous-processus, puis publie un artefact contenant ses entrées, son code, sa dépendance, ses logs d'exécution, un reçu avec toutes les empreintes et son résultat.

| Contrôle | Différence avec A | Résultat escompté | Verdict attendu |
|---|---|---|---|
| A | Référence | Somme + tirages déterministes | REFERENCE |
| B | Aucune, mais autre job | Résultat identique | SC_REPLAY_CERTIFIED |
| C | Entrées différentes, même somme | Résultat identique | NOT_SC_REPLAY_INPUT_DRIFT |
| D | Dépendance Python réellement modifiée mais équivalente | Résultat identique | NOT_SC_REPLAY_DEPENDENCY_DRIFT |
| E | Seed différente | Résultat différent | NOT_SC_REPLAY_SEED_DRIFT |

Le moteur ne connaît pas ces labels : un job d'assemblage renomme les cinq paquets avec une seed de permutation gelée (`60217`), lui fournit uniquement le paquet de référence et les octets. Le corrigé reste **dans un autre artefact**, téléchargé seulement par le job de notation.

Le moteur vérifie les SHA256, les deux événements `begin/complete` des journaux, les identifiants de processus, sessions, paramètres et environnement Python, puis **recalcule indépendamment la sortie à partir des entrées et de la seed**, sans charger la dépendance fournie comme preuve. Cela permet de détecter les octets falsifiés, une sortie impossible ou un changement caché des conditions.

## Reproduction

```bash
python -m unittest discover -s experiments/omega-reproduction-proof-10 \
  -p 'test_replay.py' -v
```

Sans API payante ni paquet tiers : Python 3.11, `actions/checkout@v4`, `actions/setup-python@v5`, `actions/upload-artifact@v4` et `actions/download-artifact@v4`. Sur `push`, seuls les contrôles sur des fixtures temporaires sont exécutés. Sur `pull_request`, la matrice est réellement exécutée et le scoring compare **B positif / C,D,E négatifs** avant archivage.

**Un résultat `SC_REPLAY_CERTIFIED` signifie uniquement : deuxième calcul dans un job GitHub distinct, conditions et octets comparables, résultat bit à bit identique et recalcul conforme à l'algorithme de référence.** Il ne signifie **pas** que le théorème, le modèle physique ou l'hypothèse scientifique a été validé indépendamment. Les jobs restent dans **le même workflow**, avec la même infrastructure et les mêmes auteurs, et ce banc est volontairement fabriqué. Par conséquent `scientific_independence=INDETERMINATE`.

Le corrigé d'un dépôt public n'est pas secret contre quelqu'un qui aurait accès à tous les artefacts GitHub ; la séparation est **fonctionnelle entre jobs**, non cryptographique contre un agent cherchant des indices extérieurs.

**Prochaine expérimentation décisive :** reproductions de calculs provenant de **deux workflows réellement distincts**, environnements non préarrangés et jeux d'entrée inconnus, avec vérificateur indépendant des conditions mathématiques et des erreurs de calcul. Aucun merge, aucune modification de `main` ou CORE.
