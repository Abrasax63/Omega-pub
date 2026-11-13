# Laboratoire Omega de provenance

Le laboratoire construit un vérificateur déclaratif à partir de traces de
processus structurées et annotées. Il lit les commandes comme du texte.
Les seules décisions apprises sont `copie` et `recalcul`. Les traces incomplètes,
les écritures multiples et les commandes inconnues donnent `indéterminé`.

Depuis ce répertoire :

```bash
python3 provenance_lab.py build training.json candidate.json
python3 provenance_lab.py check candidate.json reserved.json --baseline incumbent.json
python3 provenance_lab.py run candidate.json observation.json
python3 -m unittest -v test_provenance_lab
```

Les fichiers d'entraînement et d'évaluation sont des listes de traces
distinctes, avec un champ `expected` par trace. Exemple de trace :

```json
{"complete":true,"output":"result.json","writers":[{"command":"cp original.json result.json","exit_code":0,"output":"result.json"}],"expected":"copie"}
```

Le fichier d'évaluation est fourni à `check` après la génération.
Pour un premier passage, omettre `--baseline` compare à l'abstention systématique.
Une recommandation exige zéro fausse confirmation, davantage de confirmations
correctes et la conservation des confirmations correctes du programme précédent.
La recommandation permet une revue. Le candidat peut ensuite servir de référence
au cycle suivant. Le laboratoire ne publie pas automatiquement les candidats.

Les fixtures testent le parcours avec des traces construites. Un préfixe de
commande peut couvrir des opérations différentes, comme le montre le test de
rejet. L'extraction depuis des journaux bruts et l'évaluation externe restent
à réaliser.
