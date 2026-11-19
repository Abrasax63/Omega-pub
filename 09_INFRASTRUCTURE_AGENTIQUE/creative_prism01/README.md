# Omega Creative Prism 01 — atelier reproductible des représentations

Cet atelier explore deux changements de représentation sur des systèmes finis, et les compare à la recherche directe, à une diversification superficielle et à de **vraies baselines optimisées**. Le code utilise uniquement Python standard et ne requiert ni GPU ni API payante.

**Important :** le système sélectionne parmi **deux transformations programmées à l'avance**. Il ne crée pas spontanément de nouvelle mathématique ou de nouveaux algorithmes. L'atelier ne fait pas partie de la boucle horaire de production et n'écrit pas dans la bibliothèque certifiée.

## Exécuter

Depuis la racine du dépôt :

```bash
python3 -m unittest -v \
  discover -s 09_INFRASTRUCTURE_AGENTIQUE/creative_prism01 \
  -p "test_experiment.py"

python3 09_INFRASTRUCTURE_AGENTIQUE/creative_prism01/experiment.py \
  --output /tmp/omega-creative-prism01.json
```

Le premier appel vérifie reproductibilité, invariance par renommage d'états, contrôle exact, deux contre-exemples, budget et refus de quatre problèmes mal formés.

Le second écrit un JSON contenant les **48 problèmes finis**, la représentation proposée, le verdict réel indépendant, les solutions A/B/C/D, leurs statuts, coût instrumenté et durée, ainsi que les témoins qui réfutent deux mauvaises conversions.

## Interface Python pour Omega

```python
from experiment import corpus, valid, propose, run_arm

task = corpus()[0]
valid(task)  # refuse le problème en cas de domaine mal formé
candidate = propose(task)  # seulement bibliothèque de transformations FIXE
result = run_arm(task, "C_change_representation")
```

Le registre de candidats rapporte un invariant à préserver et une transformation à refuser. **Il ne choisit pas encore via apprentissage autonome** ; les transformations ont été écrites par le concepteur et comparées au direct et à un algorithme fort.

Aucune méthode ci-dessus ne fournit un accès réseau, une possibilité de publication ou un droit de modification de `main`.

## Statuts
- `VERIFIED_TRUE`, `VERIFIED_FALSE` : vérifiés **dans la grammaire bornée** et comparés à l'oracle exact du jeu après génération des prédictions ;
- `ABSTAIN_BUDGET` : pas de verdict dans les 500 primitives instrumentées ;
- `ABSTAIN_UNSUPPORTED` : hypothèses invalides ou représentations impossibles ;
- `KNOWN_INVARIANT` : règle mathématique connue, pas un théorème nouvellement découvert.

Les coûts instrumentés ne sont pas comparables unité pour unité entre les algorithmes, et les latences submillisecondes ne sont pas une mesure fiable du matériel. Le corpus est ouvert, synthétique, non indépendant et ne doit pas être utilisé pour entraîner un modèle puis annoncer un score de validation.

## Preuves et limites
- [Protocole gelé avant code](PREREG.md)
- [Résultats exacts du run](RESULT_2026-11-19.md)
- [GitHub Actions du pilote](https://github.com/Abrasax63/Omega-pub/actions/workflows/omega-creative-prism01.yml)
- [PR #193 en brouillon](https://github.com/Abrasax63/Omega-pub/pull/193)

Sur le premier run, C résout 48/48 cas contre 25/48 et 24/48 pour A et B, mais **D résout également 48/48**. Il est donc prouvé par exécution que des représentations préprogrammées peuvent être utiles, **pas** qu'Omega invente de meilleures représentations que les méthodes classiques.

La prochaine étape est une proposition de transformation produite par un modèle sans accès aux réponses, puis audit exact sur un jeu véritablement tenu à l'écart, avec un témoin algorithmique fort.
