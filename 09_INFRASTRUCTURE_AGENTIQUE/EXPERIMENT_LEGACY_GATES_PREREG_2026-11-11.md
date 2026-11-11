# OMEGA-LEGACY-GATE-001 — pré-enregistrement de l'intégration opt-in des garde-fous historiques

11 novembre 2026. **Protocole gelé avant résultat expérimental de l'intégration**. Branche distincte de l'ancien solveur et de `main`.

## Objectif falsifiable

Récupérer, sans modifier leur sémantique, les fonctions d'audit de l'archive `experiment/legacy-observer-transfer-2026-11-11` :
- `terminal_probe_guard` : signaler qu'un arrêt de raffinement est **sous-informatif relativement aux modèles de sondes explicitement fournis** ;
- `reconfiguration_gate` : signaler `keep/refine/replace/infeasible` pour une représentation de travail soumise à une capacité finie.

Les exposer via **une entrée opt-in facultative de `planner.plan_mission`**, en conservant la sortie du planificateur à l'identique quand cette entrée manque. Aucun effet d'exécution, de modification du champ `next_action`, de validation scientifique ou d'écriture en mémoire durable.

## Provenance, dépendances et invalidité possible

Code d'origine accessible dans la branche GitHub `experiment/legacy-observer-transfer-2026-11-11`, fichier `09_INFRASTRUCTURE_AGENTIQUE/prism/legacy_observer_transfer.py` (Git blob `f1fd030015d43b033ad3ec9883aeae7c2b903e32`), plus tests `test_legacy_observer_transfer.py`. Copier les fichiers **sans réinventer leurs algorithmes** ; toute retouche ultérieure sera commitée séparément. Il ne s'agit pas de `GeoCertPro` ni d'une récupération du solveur géodésique.

Les anciennes archives Ω-W04 présentent un **désaccord 656 vs 848** sur le nombre d'arrêts sous-informatifs ; deux implémentations dans la branche reprise trouvent 848 selon le protocole exactement spécifié, sans que l'écart avec 656 ait été élucidé. Ne pas promouvoir cet énoncé ancien en CORE.

Ces fonctions manipulent des **partitions explicites**. Elles ne savent ni extraire automatiquement une partition d'un texte, ni authenticifier un document, ni découvrir toutes les sondes possibles. La provenance des entrées reste une affirmation du fournisseur : `declared_exhaustive=true` est une **hypothèse déclarée**, PAS une certification d'exhaustivité.

## Contrat d'interface sûr

Option `observer_audit` dans `plan_mission`, facultative et **purement consultative**. Forme :

```json
{
  "termination": {
    "current_partition": [0,0,1],
    "selected_probe_partition": [0,0,0],
    "listed_probe_partitions": [[0,0,0],[0,0,1]],
    "declared_exhaustive": false
  },
  "reconfiguration": {
    "current_partition": [0,0,1,1],
    "target_partition": [0,1,0,1],
    "capacity": 2
  }
}
```

Les deux sous-tâches peuvent être données séparément. Les étiquettes sont des entiers non négatifs, les tailles doivent être compatibles, les partitions canoniques sont vérifiées/normalisées, les champs inconnus ou booléens à la place d'entiers sont rejetés, les listes de sondes ne doivent pas être vides. Une entrée `termination` indiquant `closed_relative_to_listed_probes` avec `declared_exhaustive=false` produit impérativement `closure_unknown`, jamais une fermeture générale. Même avec `declared_exhaustive=true`, produire seulement `closed_assuming_declared_probe_list`, jamais `verified/certified`.

La sortie signale `read_only`, `sources_authenticated=false`, `scientific_certificate_issued=false`, `durable_memory_writes=0`, `working_representation_only=true`. Le contrôle de représentation ne peut ni supprimer une preuve ni remplacer la mémoire scientifique durable.

## Deux tests discriminants gelés

**T1 — fermeture / coût des sondes sur univers fini exact.** Enumérer indépendamment les 5 partitions de 3 états pour chacune des 3 positions : partition initiale P, sonde a, sonde b (5³ = 125 cas ordonnés). Appliquer une fois a. Comparer :
- `naive` : arrêt après a, coût **1 sondage** (souvent sous-informatif) ;
- `guarded` : après a, appliquer b **uniquement si** le garde-fou trouve un raffinement supplémentaire (coût 1 ou 2 sondages) ;
- `fixed_both` : appliquer a puis b, coût **2 sondages**, modèle relatif de référence.
Dans chaque cas, le critère de complétude est `P ∧ a ∧ b` ; communiquer résolutions exactes, faux arrêts et consultations. **Les modèles des deux sondes sont fournis gratuitement aux politiques guard/fixed, et le coût du raisonnement du garde-fou n'est pas inclus dans les appels**. Les éventuelles économies de consultations ne sont donc pas une preuve de moindre coût total ni un avantage informationnel général face à une baseline forte.

**T2 — substitution de représentation sous capacité.** Enumérer les 7 partitions à deux blocs sur 4 états, soit 49 couples ordonnés sous capacité C=2. Vérifier `keep=7`, `replace=42`, l'invariant de permutation et `joint_blocks=4` pour des partitions orthogonales. Le verdict `replace` signifie la faisabilité du changement **de représentation de travail**, sans coûts réels d'entraînement, récupération ni migration durable.

Tests négatifs obligatoires : aucun audit sans opt-in, aucune suggestion de prochaine action écrasée, aucune fermeture lorsque l'énumération n'est pas déclarée exhaustive, aucune preuve d'authenticité proclamée, pas de troisième sondage, aucun effet sur les tâches RCE ou les écritures mémoire, permutation de noms de blocs, erreur sur longueur/mauvais types, contradiction d'entrée.

## Arrêt et statut

Une itération et deux tests discriminants T1/T2 seulement. Si l'intégration ou les contre-tests échouent, bloquer l'activation et publier l'échec. Exiger la CI Python, les tests du Prisme, RCE/MCP et une deuxième voie de calcul T1 sans réutiliser les fonctions de l'archive. **Ne pas attribuer de gain de réponses sur de vrais problèmes tant que ceux-ci ne sont pas testés dans une expérience ultérieure**, à information et budget équivalents.

PR brouillon empilée sur #38, aucune écriture `main`, CORE ou SQLite.
