# OMEGA-RAW-PROVENANCE-LAB-08 — producteur de véritables traces de calcul

**But :** mettre à l'épreuve le regroupement de preuves d'origine en lui donnant des **fichiers de calcul bruts** (sorties des sous-processus, reçus, entrées, résultats, événements de copie), **sans le corrigé**.

## Producteur et honnêteté du périmètre

Quatre **vrais sous-processus Python** sont lancés dans **un seul job GitHub Actions**. Ils partagent donc l'environnement du runner, mais ont chacun `pid`, `execution_id` aléatoire, empreinte du programme, empreinte des données d'entrée, empreinte des résultats, `run_id/run_attempt` hérités du workflow et logs `begin/complete`. Deux sous-processus utilisent volontairement **les mêmes entrées et la même seed** et produisent le **même fichier de résultat** : la simple égalité d'un hash de résultat ne prouve donc pas une exécution unique.

Le générateur fait **deux vraies copies** de bundles avec `shutil.copyfile` et consigne `copy_events.jsonl`; il conserve un septième dossier contenant seulement un résultat non attribuable car celui-ci pourrait venir de l'un ou l'autre des deux sous-processus de même résultat.

**Il ne s'agit pas de quatre runs GitHub indépendants, ni d'une reproduction scientifique indépendante.** C'est un test de filiation de fichiers et processus sous un protocole contrôlé ; aucune identification fiable des origines scientifiques de sources externes n'est encore démontrée.

## Séparation GitHub Actions

La [CI dédiée](../../.github/workflows/omega-raw-provenance-lab-08.yml) suit trois frontières :

1. `produce-raw` : génère quatre calculs et publie **deux artefacts différents** : `raw-evidence` (7 dossiers de pièces) et `answer-key` (corrigé `gold.json`).
2. `blind-inference` : **télécharge exclusivement l'artefact `raw-evidence`**, examine les octets des fichiers et publie `predictions.json`; n'a ni le gold ni le droit de télécharger le second artefact dans son workflow.
3. `independent-scoring` : télécharge les trois artefacts, compare chaque `origin_id` attendu, les deux copies, le résultat orphelin et l'absence de faux certificat scientifique ; publie les chiffres et échecs.

Le résultat du test est visible dans les artefacts publics : le gold **n'est pas un secret cryptographique**, seulement **un fichier que le processus de prédiction ne reçoit pas**. Le dépôt est public et un agent possédant d'autres accès GitHub pourrait consulter ce gold ; il ne s'agit pas d'une évaluation adversariale indépendante contre un moteur qui chercherait activement les réponses.

Le dossier brut contient `inventory.json`, `copy_events.jsonl` et sept sous-dossiers `cases/packet-***`. Les noms sont des alias opaques mélangés. Les champs `gold`, `origin_id` attendu et `role` ne sont pas fournis par le manifeste d'entrée.

Les preuves vérifiées comportent **les deux événements de logs, les reçus, les bytes et leurs SHA256**, mais aucun scellement cryptographique externe contre la falsification conjointe de ces pièces.

## Exécution locale, sans API de modèle payante

```bash
python -m unittest discover -s experiments/omega-raw-provenance-lab-08 -p 'test_raw_lab.py' -v

python experiments/omega-raw-provenance-lab-08/generate.py \
  --raw-dir /tmp/omega-raw-evidence \
  --gold-file /tmp/omega-answer-key/gold.json

python experiments/omega-raw-provenance-lab-08/infer.py \
  --raw-dir /tmp/omega-raw-evidence \
  --output /tmp/omega-predictions.json

python experiments/omega-raw-provenance-lab-08/score.py \
  --raw-dir /tmp/omega-raw-evidence \
  --predictions /tmp/omega-predictions.json \
  --gold /tmp/omega-answer-key/gold.json \
  --output /tmp/omega-score.json
```

Le score `RAW_PROVENANCE_PIPELINE_VERIFIED` signifie seulement : **4 exécutions de sous-processus regroupées correctement, 2 miroirs détectés, 1 abstention, 0 fausse attribution sur ce dossier contrôlé et 0 prétention d'indépendance scientifique**. L'exécution du code ne constitue aucun entraînement d'un LLM.

**Prochain verrou :** pièces ZIP et logs **non préparés** issus de workflows différents, gold préparé par une source indépendante et audit de véritable reproductibilité des calculs, des entrées et des dépendances.

[Préenregistrement initial](PREREG_2026-11-17.md) au commit `3034e63865f6acd11b4e5fda96563f79a3aeec53`. PR DRAFT, aucune fusion ni modification de `main`.
