# OMEGA-REAL-PROVENANCE-07 — premiers contrôles sur métadonnées GitHub réelles

Ce pilote vérifie que des **artefacts GitHub publics** peuvent être reliés à leur exécution d'origine sans fournir à l'algorithme le regroupement attendu. Les sources sont de **vraies projections figées de réponses GitHub REST** (cinq runs et sept artefacts), consultables aux URLs listées dans [le manifeste](fixtures/github_artifact_metadata.json). Ce ne sont ni les journaux de jobs, ni les contenus ZIP, ni un échantillon aveugle.

Le [préenregistrement](PREREG_2026-11-17.md) au commit `bc667631fca36fb992c4e26f2d700195f6462def` précède le code et conserve la connaissance préalable des sources.

Le regroupement accepté requiert `repository + run_id + run_attempt`, avec concordance de l'identifiant et du commit SHA entre la fiche du run et l'artefact. Une référence dupliquée au même `artifact.id` est dédupliquée ; deux artefacts du même run restent dans un groupe ; deux runs différents partageant le même commit restent deux invocations distinctes. Les champs manquants déclenchent une abstention, les contradictions une erreur, **sans aucune promotion automatique de validité scientifique**.

**Différence déterminante** : deux `run_id` différents peuvent prouver deux invocations GitHub distinctes (sous réserve de la fiabilité des métadonnées), **pas** deux calculs scientifiques méthodologiquement indépendants. Sans étude des codes, données d'entrée, modèles, seeds, dépendances et traces, `scientific_independence` doit rester `INDETERMINATE`.

## Reproduction

```bash
python -m unittest discover -s experiments/omega-real-provenance-07 -p 'test_resolve.py' -v
python experiments/omega-real-provenance-07/resolve.py \
  --fixture experiments/omega-real-provenance-07/fixtures/github_artifact_metadata.json \
  --output evidence/report.json
```

Bibliothèque standard Python 3.11 et GitHub Actions ; aucune API payante, aucun changement de `main`, pas de fusion. La CI n'a pas besoin de réseau : elle utilise uniquement les réponses publiques projetées et archivées. Les tests adversariaux incluent miroirs simulés (clairement marqués comme ajoutés au test, non présents dans les sources), run_attempt manquant, identifiant falsifié, SHA discordant et doublons de nom.

**Prochaine expérience réellement décisive** : utiliser en entrée des dossiers de logs/ZIP bruts, reconstruire les liens à des identifiants de jobs et d'exécutions, et exiger un gold indépendant avant notation. Ce pilote est la première couche de **traçabilité des métadonnées**, pas une preuve d'analyse automatique des journaux.
