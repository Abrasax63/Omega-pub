# OMEGA-STATE-SPLIT-01 — version-space multiétats borné

**Question** : avec les seules observations entrées/sorties déjà acquises, Omega peut-il trouver des modèles compatibles ayant des nombres d'états différents et identifier des requêtes qui les distinguent ?

Préenregistrement antérieur au code : [commit 01521caa](https://github.com/Abrasax63/Omega-pub/commit/01521caa4cc19971b1322ca77a3da67b4295ca4f), [protocole](PREREG_2026-11-17.md).

Le synthétiseur `state_split.py` explore toutes les tables Mealy de 1 à 3 états, entrées/sorties binaires, et déduplique les états inaccessibles par forme canonique BFS. Il ne voit ni le système caché ni un oracle. Une diversité de prédictions sur des mots EQ à dix symboles sert à retenir jusqu'à 128 représentants et à choisir jusqu'à 32 sondes. L'ensemble complet borné est plus vaste que l'échantillon classé.

Les huit mondes retardés de contrôle partagent les mêmes six observations publiques ; ils ne constituent **pas des réplications indépendantes** ni un test de généralisation. La machine d'évaluation n'est utilisée qu'après la génération du calendrier de requêtes.

## Résultat du premier essai local

- **8/8 contrôles unitaires locaux réussis**.
- **634 modèles canoniques compatibles** : 1 à un état, 12 à deux états, 621 à trois états.
- **220 signatures de prédictions** sur les huit mots d'ancrage ; 128 représentants sélectionnés.
- **7/8 sources retardées distinguées** dans les 32 propositions ; le motif `111` est manqué.
- Verdict préenregistré : **`NOT_VERIFIED`**, malgré l'activation du mécanisme de désaccord. Il ne faut pas remplacer ce résultat par un succès au seul motif que la construction de modèles a fonctionné.

## Reproduction

```sh
python -m unittest discover -s experiments/omega-state-split-01 -p test_state_split.py -v
python experiments/omega-state-split-01/state_split.py --output /tmp/state-split-report.json
```

Dépendances : Python standard uniquement, aucune API payante. La CI archivera `report.json`, `summary.jsonl` et `report.sha256`. Garder cette PR **DRAFT**, sans fusion ni modification de `main`.

**Prochaine hypothèse**, sur une nouvelle version préenregistrée : distinguer la maximisation de diversité moyenne et la **couverture des motifs d'accès courts** ; utiliser un petit ensemble de requêtes garanties de couverture avant de classer les autres. Les huit cas de ce pilote sont désormais connus ; un gain éventuel obtenu en les couvrant ne serait pas un nouveau holdout indépendant.