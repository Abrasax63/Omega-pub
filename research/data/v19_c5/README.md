# V19 C5 / L=3 — données et reproduction

Le script `../../code/audit_v19_c5_independent_2026-11-04.py` utilise quatre entrées et régénère trois CSV de sortie ainsi que le rapport JSON dans ce dossier.

## Entrées présentes

| Fichier | Lignes de données | Git blob SHA |
|---|---:|---|
| `V19_ORIENTED14_CLASSES_2026-10-15.csv` | 14 | 72a6dd3b95c7eb62d948b2711a80d7f595e91708 |
| `V19_PAIR_WITNESSES_C5O14_2026-10-15.csv` | 105 | 6cd64f2854d5b46ddefeb915cbb3bb6933e8760e |
| `V19_TRIPLE_WITNESSES_D5_13_2026-10-15.csv` | 455 | 09cb0fe7bfe3944ee70aacd8f0cf1642c301d99f |
| `V19_UNIVERSAL10_U42_2026-10-15.json` | — | 685d62a46f6e07c35aed80f1d45351ae8bdc0763 |

## Sorties présentes

| Fichier | Lignes de données / éléments | Git blob SHA |
|---|---:|---|
| `V19_PAIR_WITNESSES_C5O14_REPAIRED_2026-11-04.csv` | 105 | 1b89fd999eac948e342835853854816fdeacf0f6 |
| `V19_TRIPLE_WITNESSES_D5_13_REPAIRED_2026-11-04.csv` | 455 | 1a96aa36ab0ebe2bd7859153ec3fb88eec9767b2 |
| `V19_TRIPLE_WITNESSES_C5O14_U42_2026-11-04.csv` | 560 | 273a32f10e7076bde110288f2808c864f92ca3c3 |
| `AUDIT_V19_C5_INDEPENDENT_SUMMARY_2026-11-04.json` | résumé JSON valide | créé dans la consolidation |

Les identifiants ci-dessus sont des **Git blob SHA-1**, pas des SHA-256 de fichiers. Le rapport détaillé `AUDIT_V19_C5_INDEPENDENT_2026-11-04.json` est produit par le script à l'exécution ; le fichier homonyme de la branche source était tronqué et invalide, il n'a donc pas été importé.

## Provenance et limite d'intégrité binaire

Les contenus CSV ont été transférés depuis les fichiers structurés de la Library sous forme de texte tabulaire, puis débarrassés de leur en-tête de présentation. Les en-têtes CSV et nombres de lignes ont été contrôlés sur la branche GitHub. Cette opération conserve les champs et les enregistrements visibles, mais **ne prétend pas préserver l'identité octet par octet** des fichiers sources. Les SHA-256 historiques associés aux originaux ne doivent donc pas être appliqués à ces exports textuels.

L'archive source et les originaux restent conservés séparément dans la Library. Aucun fichier historique source n'a été écrasé.

## État de reproduction

Le programme a été exécuté avec succès sur l'archive source récupérée dans la Library. Résultats : 3 341 diagrammes locaux, 510 ombres propres, 13 classes D5, 14 classes C5 orientées, 105 paires réparées, 455 triples D5 réparés et 560 triples orientés U42 vérifiés.

### Reproduction sur la tête actuelle de la PR #5 — 5 novembre 2026

<badge>SUCCÈS CI</badge>

Le workflow GitHub Actions [run 41984528892](https://github.com/Abrasax63/Omega-pub/actions/runs/41984528892), déclenché sur la branche `maintenance/reconciliation-bibliotheque-2026-11-05`, commit `14e3881a63a977e9f511a636fea73bfc3fa340e9`, a terminé avec succès sous Python 3.12.

- Le script complet s'exécute sans erreur.
- Les assertions reproduisent 3 341 diagrammes locaux, 510 ombres propres, 13 classes D5, 14 classes C5 orientées, 2 réparations de paires, 26 réparations de triples D5 et les 560 triples U42.
- Un contrôle sémantique supplémentaire valide les exports committés **et** les sorties régénérées : 105 lignes de paires C5, 455 lignes de triples D5 et 560 triples orientés U42. Il vérifie les classes de chaque témoin, la cohérence des fonctions T, la distinction des paires et l'unicité/couverture des combinaisons.
- Le rapport JSON détaillé régénéré est conservé comme artefact du run.

Une première tentative de comparaison octet par octet avait échoué : les témoins choisis par le script ne sont pas tous les mêmes que ceux des exports versionnés, bien que les contrôles sémantiques ci-dessus passent. Le CSV de paires présente aussi une différence de terminaison de fichier. **Aucune sortie n'a été remplacée dans GitHub sur la base de cette différence.** L'identité binaire n'est donc pas revendiquée ; le résultat validé ici est la validité sémantique des témoins selon les vérifications codées.

Depuis la racine du dépôt :

```bash
python research/code/audit_v19_c5_independent_2026-11-04.py
```

## Contrôles structurels des exports GitHub — 4 novembre

Lecture des six CSV depuis la branche après transfert : les en-têtes et comptes de lignes attendus sont présents ; les 14 classes sont uniques ; les 105 multisets de paires et 455 multisets de triples D5 sont uniques ; les 560 triples orientés U42 sont uniques ; les paires d'états sont distinctes dans les fichiers réparés ; les étiquettes de classes sont conservées entre fichiers historiques et fichiers réparés.

Le workflow de la PR #5 répète désormais l'exécution et le contrôle sémantique sur les deux jeux de sorties. Le contrôle sémantique réutilise les fonctions d'évaluation `global_shadow`, `canonical` et `coherent` du script : il s'agit d'un contrôle supplémentaire des exports, pas d'une seconde implémentation indépendante de ces définitions.

Le script est corrigé dans cette consolidation pour écrire le rapport JSON détaillé dans `research/data/v19_c5/`, conformément à cette arborescence. Le résumé JSON versionné dans le dépôt ne se substitue pas à ce rapport détaillé généré.
