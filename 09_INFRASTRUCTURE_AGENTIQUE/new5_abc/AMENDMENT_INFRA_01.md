# Amendement infrastructure après le premier run — 16 novembre 2026

**Run original :** https://github.com/Abrasax63/Omega-pub/actions/runs/43810936196.

Le job de gel a commencé sur les cinq checkouts historiques et a atteint l'exécution d'un patch sous Docker, puis a terminé en **FAILURE** par `TypeError` dans `Path(MountedPatch)`. Le second job historique a donc été **SKIPPED**. Aucune réparation ni score A/B/C complet n'a été enregistré. Ne pas interpréter comme « zéro réparation ».

Le problème exact : `abc_runner.py` construisait son argument Docker par `Path(patch_file)`, alors que `patch_file` est une instance interne `MountedPatch` qui expose `.resolve()` mais pas `__fspath__`. Le commit `7d5c17fe2987b1dace8bb6099da2b82225e7e759` emploie explicitement `patch_file.resolve()` et le commit `ceaf5543f9afeb2509afa41f4384e4cb7d3a72ef` ajoute un test de non-régression du montage. Le [workflow statique](https://github.com/Abrasax63/Omega-pub/actions/runs/43811300448) a ensuite passé **16/16 tests**.

**Second défaut anticipé :** l'upload GitHub Actions ne doit inclure que `selection.json` pour garantir que le second job le récupère au chemin annoncé. Le fichier manifeste source annexe avait été donné avec un autre répertoire parent, provoquant un risque de structure d'archive inattendue. Ce changement n'affecte ni candidats, ni corpus, ni tests ni seuils.

La reprise après correction est **un rejeu d'intégration**, PAS un nouveau protocole scientifique préenregistré. Si la première exécution a consommé une inférence avant de planter, cette consommation compte dans l'audit opérationnel, même si sa sortie n'a pas été archivée. On ne doit ni présenter le rejeu comme première exécution ni additionner ses observations comme deux expériences indépendantes.

Le comparateur reste A/B/C avec 4 tests de patch au maximum par bogue, corpus inchangé, mêmes références et même politique d'arrêt. Les correctifs historiques de production n'ont pas été ouverts par le job d'oracle, qui était SKIPPED.

**Statut scientifique actuel : INVALID_EXPERIMENT_INFRASTRUCTURE ; aucune réparation confirmée.** Pas de changement de `main` ni fusion.
