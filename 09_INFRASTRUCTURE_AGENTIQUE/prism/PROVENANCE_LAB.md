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

## Cycle autonome de proposition

```bash
python3 provenance_cycle.py propose training.json incumbent.json proposal.json
python3 provenance_cycle.py check proposal.json incumbent.json reserved.json
python3 provenance_cycle.py run proposal.json incumbent.json observation.json
```

Le cycle compte les erreurs du vérificateur sur les traces annotées et
choisit un seul préfixe. Une fausse confirmation pèse deux fois une
confirmation manquée. Les égalités sont résolues par ordre lexical. Il
ajoute une règle soutenue par les observations ou restreint une règle
existante. La proposition consigne le choix, les erreurs et les empreintes
des données d'entrée. Elle peut être rejouée avec la référence d'origine.

Fournir les cas réservés seulement après la construction. Les empreintes
détectent la réutilisation exacte d'une observation, même réannotée.
L'opérateur doit établir la séparation des sources et conserver les
corrigés hors du processus de génération. L'évaluation accepte en option
`--direct predictions.json` pour une liste de verdicts établie séparément.
La recommandation exige zéro faux verdict, aucun verdict correct perdu et
un gain sur les confirmations correctes ou la suppression de faux verdicts.
Conserver aussi les candidats rejetés pour éviter de répéter le même essai.

### Rejeu du premier cycle

Sur le [run contrôlé 43489499229](https://github.com/Abrasax63/Omega-pub/actions/runs/43489499229),
la référence déclarative choisie pour le pilote connaissait uniquement
`cp`. Le constructeur a reçu la trace annotée de `evidence/train.json` et
a proposé `install -m → copie`. Le candidat a confirmé 1 cas sur les
3 traces d'évaluation, contre 0 pour la référence déclarative et 1 pour
la règle fixe du laboratoire. Les trois approches ont produit zéro faux
verdict. Ce corpus avait déjà servi au développement du laboratoire.

Sur le [journal externe déjà examiné](https://github.com/nexu-io/open-design/actions/runs/38714250159/job/116353498714),
le candidat et la référence déclarative se sont abstenus sur les deux
sorties. Le transfert positif et le gain par rapport à la règle fixe
restent à établir. La collecte et l'annotation ont été préparées dans
la session. Aucun bras LLM à budget égal n'a été exécuté.
