# Omega 14 — libre exploration, logique compositionnelle et contre-modèles contrôlés

**Pilote de recherche expérimental ; aucun résultat scientifique certifié.**

Le [premier raccord neuronal #174](https://github.com/Abrasax63/Omega-pub/pull/174) a effectué six appels Qwen locaux et produit cinq JSON syntaxiquement valides mais zéro formalisation exécutable. Il est conservé, négatif, sans correction après coup. Ses sorties montraient notamment la nécessité de représenter les opérateurs ET/OU/NON et des relations plus complexes au lieu d'inventer un seul prédicat pour une disjonction.

## Deux voies séparées dans ce pilote

**Exploration :** le modèle peut librement énoncer jusqu'à deux idées ou questions alternatives, même si sa formalisation ne passe pas le contrôle. Elles restent enregistrées, avec les erreurs de traduction et l'empreinte du texte généré. Le logiciel ne prétend jamais les certifier.

**Formalisation calculable :** les clauses proposées par Qwen utilisent une AST récursive avec `atom` (prédicats unaires ou binaires), `and`, `or`, `not`, `implies`, `forall`, `exists`. Les références de phrases sont des extraits exacts, et toutes les phrases doivent être prises en compte avant de chercher un contre-modèle fini. Les variables, types, arités, profondeurs et tailles sont vérifiés avant calcul.

Si la traduction est complète, `finite_logic.py` explore exhaustivement les modèles de taille 1 ou 2 sous un budget de 12 atomes fondés. Lorsqu'un contre-modèle apparaît, **un second interprète** vérifie de nouveau les prémisses et l'échec de la conclusion. Cela vérifie les calculs sur l'AST, **mais pas la fidélité de l'AST au texte anglais** ; aucune nouvelle découverte scientifique n'est revendiquée. Si aucun témoin n'est trouvé, le statut reste indéterminé.

Les alertes entre surface linguistique et formules (négation, disjonction, quantification) restent des *indicateurs de suspicion*, non des preuves d'erreur. Elles n'effacent pas les idées générées.

## Jeu nouveau et gel méthodologique

Les six entrées FOLIO/Yale **validation lignes 85–90**, sans tri et jamais utilisées dans les PR antérieures, ont été gelées dans `FOLIO_VALIDATION_ROWS85_90_FROZEN.jsonl` avec le blob `50762a7e830cf7df2ff445ab6d5e8220e5ad73f8` avant prompt/code. Source [Yale-LILY/FOLIO](https://github.com/Yale-LILY/FOLIO), validation v0.0, commit `5d7bb84c7edab3fb358e057d2807f19cf5cf5e2d`, licence CC BY-SA 4.0. Les labels et formules de référence **ne sont pas fournis au modèle ou au solveur**.

Chaque question reçoit un appel Qwen2.5-Coder-3B-GGUF exécuté en local sur CPU par `llama-server` avec 900 tokens maximum et température 0,2. Aucun API payante. La référence stricte est le moteur figé de #172 appliqué aux mêmes six textes.

## Reproduire

Tests hors modèle :

```bash
python3 -m unittest discover -s 09_INFRASTRUCTURE_AGENTIQUE/compositional_logic14 \
  -p 'test_compositional.py' -v
```

Les tests incluent un décompte exhaustif comparant deux interprètes logiques distincts, un contre-modèle portant sur une relation binaire, le refus des variables libres, des prédicats malformés, des citations inventées et des conclusions incompletes.

Le workflow `.github/workflows/omega-compositional-logic14.yml` restaure les poids Qwen et le modèle local épinglés, restaure le checkpoint de 12 événements Qwen antérieurs, génère les AST et conserve le rapport et le journal étendu **en artefact**. Un artefact n'est pas automatiquement la mémoire permanente du prochain cycle : il faut enregistrer/faire reprendre explicitement le nouveau checkpoint avant de parler d'apprentissage.

Exécution locale avec serveur actif :

```bash
python3 09_INFRASTRUCTURE_AGENTIQUE/compositional_logic14/runner.py \
  --ledger /tmp/omega14-hypotheses.jsonl \
  --output /tmp/omega14-raw-evidence.json
```

## Interprétation stricte

Un résultat `FINITE_WITNESS_REPLAYED` signifie seulement qu'il existe un contre-modèle à la **formule proposée**. La qualité de la traduction naturelle, l'indépendance des évaluations et la généralisation à d'autres sciences restent **indéterminées**. Une sortie intéressante mais non formalisable reste conservée comme hypothèse et non effacée. Pas d'entraînement des poids, pas de raccord au site, pas de mise à jour du cycle horaire, aucune fusion ou modification de `main`.