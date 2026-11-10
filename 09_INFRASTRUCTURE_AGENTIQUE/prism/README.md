# Prisme adaptatif — P1/P2

## P1 — Planification

`planner.py` expose `plan_mission(mission)`. Il retourne un plan explicable
avec les rôles RCE activés, les questions assignées, les motifs, les critères
d'échec, les conditions d'arrêt et les rôles écartés.

La mission peut également transporter `mission_id`, `domain`, `scope`,
`exclusions`, `known_ids` et `constraints`. Ces champs sont conservés pour
la préparation du contexte ; ils ne changent pas automatiquement les règles
de routage.

## P2 — Préparation des contextes

`context.py` expose `prepare_contexts(root, plan, max_documents=12)`.
La fonction réutilise directement les fonctions en lecture seule de la
passerelle MCP existante :

- `memory_search` une fois par rôle planifié ;
- `memory_get` pour les identifiants exacts explicitement fournis et ceux
  retrouvés dans les résultats d'index ;
- un paquet distinct par rôle, conservant le résultat de recherche, les
  enregistrements exacts, les statuts, les références, les candidats et les
  limites de couverture.

Exemple depuis ce dossier :

```python
from pathlib import Path
from planner import plan_mission
from context import prepare_contexts

mission = {
    "question": "Auditer le lemme sur les noyaux et périodes",
    "mission_type": "mathematical",
    "domain": "dynamique finie",
    "scope": "Énoncé et hypothèses explicitement fournis",
    "exclusions": ["aucune extrapolation hors du périmètre"],
    "known_ids": ["BR-R90-01"],
}
plan = plan_mission(mission)
bundle = prepare_contexts(Path("/chemin/vers/Omega-pub"), plan)
```

## Garanties et limites

- Le dépôt est lu localement ; aucune écriture n'est effectuée.
- Les identifiants exacts non trouvés restent explicitement non trouvés.
- Les éléments de migration en attente gardent leur type et leur statut.
- Les documents candidats ne deviennent pas des dépendances établies.
- Le moteur reste lexical et local ; il ne consulte pas le Web.
- Aucun modèle n'est appelé et aucune perspective n'est exécutée.
- Aucun verdict scientifique ni certificat RAVI-2 n'est produit.
- Les rôles restent des perspectives préparées pour l'agent principal, pas
  des agents autonomes ou indépendants.

## Tests

Depuis `09_INFRASTRUCTURE_AGENTIQUE/prism/` :

```bash
python -m unittest -v
```

Les tests d'intégration du workflow vérifient aussi le RCE, la passerelle MCP
et les tests de fumée des index du dépôt.

## P3 — Exécution supervisée et enregistrement

`execution.py` ajoute un registre d'exécution supervisée. Il démarre une
session à partir du plan P1 et du bundle P2, puis accepte uniquement les
sorties explicitement fournies pour chaque rôle. Une perspective terminée doit
contenir son texte réel ; une perspective bloquée ou non exécutée ne peut pas
être accompagnée d'une sortie fictive.

API :

- `start_execution(plan, context_bundle)` vérifie la correspondance de la
  mission et l'existence d'un paquet de contexte par rôle ;
- `record_perspective(run, role, status=..., output=..., evidence_refs=...,
  limitations=...)` enregistre une sortie ou un blocage explicite ;
- `close_execution(run)` ferme le registre et calcule la couverture, sans
  produire de synthèse ni de verdict scientifique.

**Limites essentielles :** le module n'appelle aucun modèle, ne lance aucun
agent externe et n'exécute aucun calcul. Les perspectives restent des angles
de travail du même agent principal ChatGPT ; elles ne sont pas indépendantes.
Le code enregistre les productions réelles de l'agent principal lorsqu'elles
sont fournies, mais ne les génère pas lui-même. Le registre reste en mémoire :
aucune persistance, écriture dans la bibliothèque, certification RAVI-2 ou
validation scientifique n'est effectuée.

Tests P3 :

```bash
python -m unittest -v
```

## P4 — Journal d'événements append-only

`event_store.py` ajoute un journal JSONL chaîné par empreintes SHA-256.
Il réutilise les objets P1/P2/P3 et produit les événements
`mission_planned`, `context_prepared`, `perspective_recorded` et
`execution_closed`.

- `lifecycle_events(plan, context_bundle, run)` construit les événements
  d'un cycle sans recopier le texte de la mission, les documents du contexte
  ni les sorties de perspectives : seuls les identifiants, statuts,
  références, métadonnées et empreintes sont journalisés.
- `append_events(path, events)` vérifie la chaîne existante puis ajoute un
  lot sans tronquer ni réécrire le journal.
- `read_ledger(path)` relit et vérifie l'intégrité de toute la chaîne.

Le chemin du journal est fourni explicitement par l'appelant. Le module ne
choisit pas de destination dans le dépôt et n'écrit rien automatiquement.
Un journal valide établit l'intégrité documentaire de la séquence, pas la
vérité des sorties, leur indépendance ou une certification RAVI-2.

Tests P4 :

```bash
python -m unittest -v
```

## P4 — Journal de provenance append-only

`event_store.py` réutilise le schéma commun
`schemas/research-event.schema.json` et son modèle d'événements. Le schéma
a été étendu avec `previous_hash` et `event_hash` pour détecter les
altérations et préserver l'ordre append-only.

- `lifecycle_events(plan, context_bundle, run)` convertit le cycle P1/P2/P3
  en événements conformes au schéma commun : planification, récupération du
  contexte, perspectives et clôture.
- Les événements gardent l'acteur, le rôle, le statut d'exécution, l'espace
  épistémique, les références, les empreintes et les limites.
- Les contenus bruts de mission, les documents du contexte et les sorties
  textuelles ne sont pas copiés dans le journal ; seules leurs empreintes
  peuvent être enregistrées.
- `append_events(path, events)` vérifie le journal existant et rattache le
  nouveau lot à sa dernière empreinte sans réécrire les lignes antérieures.
- `read_ledger(path)` vérifie toute la chaîne.

Le chemin est fourni explicitement par l'appelant. Aucun journal n'est écrit
automatiquement dans le dépôt ou dans la mémoire scientifique. Une chaîne
intègre atteste l'intégrité du journal, pas la vérité d'une perspective, son
indépendance ou sa certification RAVI-2.

Tests P4 :

```bash
python -m unittest -v
```


## P5 — Évaluation comparative A/B/C

Le protocole préenregistrable est décrit dans
[`P5_EVALUATION_COMPARATIVE.md`](../P5_EVALUATION_COMPARATIVE.md). Il compare
A (réponse directe), B (prisme fixe) et C (routage adaptatif) sur un jeu tenu
à l'écart, avec notation humaine aveugle, plusieurs évaluateurs, mesures de
qualité, traçabilité, coût et latence.

`evaluation.py` valide les enregistrements de notation (dimensions 0–4,
comptages d'erreurs, identifiants opaques et unicité des évaluations). Il ne
note pas les réponses, ne révèle pas les bras et ne produit aucun verdict
scientifique. Les notes initiales et les arbitrages doivent rester séparés.

**État P5 :** protocole et validateur ajoutés ; campagne non exécutée. Aucun
jeu tenu à l'écart, résultat A/B/C, évaluateur indépendant ou gain démontré
n'est revendiqué. Le jeu, les corrigés et la procédure d'arbitrage doivent être
gelés avant toute collecte.

Tests P5 :

```bash
python -m unittest -v
```
