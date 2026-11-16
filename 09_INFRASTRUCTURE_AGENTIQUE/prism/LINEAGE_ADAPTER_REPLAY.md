# Raccord du collecteur Omega au pilote de provenance — PR #94

## Ce qui est implémenté

`lineage_adapter.py` consomme le format **existant** `provenance_agent.JournalBundle` (métadonnées des jobs GitHub et journaux bruts), réutilise `provenance_xtrace.extract/fixed_verdict` et appelle le vrai `provenance_selection.select_verdict` de la PR #81. Le nouveau bras construit un graphe local de copies/recalculs et appelle `lineage_pilot.assess`.

Les deux bras reçoivent exactement la **même sélection de logs**, et chaque journal distinct compte pour **une lecture**. Le budget est refusé avant lecture si le nombre de jobs dépasse le plafond. Ce coût ne représente ni le temps CPU ni la taille en octets ; le coût de parsing supplémentaire n'est pas mesuré.

**Important :** `select_verdict` distingue `copie` et `recalcul`, alors que `assess` distingue une origine commune de deux exécutions distinctes. La colonne `selector_translation` est une **traduction prudente** : seuls deux recalculs explicites de même empreinte autorisent le verdict `executions_distinctes_resultat_identique`. Elle s'abstient dans les autres situations. Cette traduction est une extension de comparaison, **pas** la fonctionnalité native du sélecteur. Il serait trompeur de traiter les deux sorties comme des substituts directs.

## Rejeu d'un run public — données de développement, non holdout

Source : [GitHub Actions, run 43489499229, 13 novembre 2026](https://github.com/Abrasax63/Omega-pub/actions/runs/43489499229).

- `fixtures/lineage_dev_run_43489499229.json` contient une photographie textuelle de trois jobs publics : `132106598273`, `132106598116`, `132106598328`.
- `fixtures/lineage_dev_pairs.json` déclare quatre paires et leur signification.
- Les traces avaient déjà été utilisées pour construire et auditer le laboratoire. Malgré un job baptisé `reserved`, **aucune observation de ce corpus ne peut servir de validation indépendante pour la PR #94**.

Attentes falsifiables pour le rejeu :

| Paire | Sélecteur traduit | Graphe d'ascendance | Lectures par bras |
| --- | --- | --- | ---: |
| Recalcul `build-a` / recalcul `reserved-b`, empreinte identique | exécutions distinctes | exécutions distinctes | 2 |
| Deux copies `reserved-a` / `reserved-c` depuis `original.json` non tracé | indéterminé | indéterminé | 1 |
| Copie `reserved-a` / recalcul `reserved-b` | indéterminé | indéterminé | 1 |
| Install/copie depuis des sources non reliées entre jobs | indéterminé | indéterminé | 2 |

Le dernier cas est soumis à contrôle par test, et non une preuve de la dépendance réelle des sources.

**Résultat attendu : aucune plus-value sur ce corpus déjà vu.** Si les tests ne confirment pas ces verdicts, le raccord est à corriger, pas à promouvoir.

## Reproduction

Depuis `09_INFRASTRUCTURE_AGENTIQUE/prism` :

```sh
python -m unittest -v test_lineage_pilot test_lineage_adapter test_lineage_real_replay
python lineage_adapter.py fixtures/lineage_dev_run_43489499229.json fixtures/lineage_dev_pairs.json --budget 2
```

Le test `--budget 1` doit s'abstenir sur les paires utilisant deux jobs. Un journal absent, incomplet ou incohérent doit provoquer `indetermine`, jamais une certification.

## Frontière de confiance et limitations

- Le champ `attested=True` construit par l'adaptateur signale que la forme de la trace fournie a été analysée ; **il ne constitue PAS une attestation signée ou indépendante**. La sortie affiche toujours `DECLARED_SNAPSHOT_NOT_AUTHENTICATED`.
- Le parseur ne reconnaît qu'un sous-ensemble de `cp`, `install` et `python3 -c`; des écritures non tracées ou des pipelines/renommages restent invisibles. Une copie dont le producteur ne peut être lié dans le **même job** entraîne l'abstention.
- Les identifiants de job et les empreintes proviennent du dossier fourni ; ils ne sont pas vérifiés cryptographiquement contre l'API au moment du rejeu.
- Deux jobs distincts ne prouvent **pas** l'indépendance scientifique de leurs programmes, données ou hypothèses.
- Les données de développement et les cas synthétiques ne prouvent aucun gain propre à Omega.
- L'exécution reste locale et en lecture seule ; aucune décision de certification, publication, fusion ou planification autonome.

## Prochain verrou décisif

Pré-enregistrer **avant lecture** des cas non utilisés pour concevoir #81 ou #94 ; obtenir leurs journaux complets par une collecte distincte ; vérifier les racines par une méthode indépendante ; imposer les mêmes budgets et mesurer les **fausses confirmations, bonnes confirmations, abstentions et surcoût** face à une référence forte. Tout verdict scientifique reste indéterminé tant que sa provenance n'est pas authentifiée. Passer ensuite par le verrou de la [PR #83](https://github.com/Abrasax63/Omega-pub/pull/83), uniquement pour une recommandation de revue. Ne pas fusionner sans preuve de transfert.
