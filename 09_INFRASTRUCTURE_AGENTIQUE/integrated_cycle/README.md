# OMEGA-CYCLE-01 — raccord de bout en bout (expérimental)

**Statut : branche DRAFT ; non intégré à main ; aucun résultat scientifique certifié.**

Ce pilote constitue un raccord minimal **sans nouvel orchestrateur** : il réutilise les modules existants de planification P1, contexte RCE P2, supervision P3, journal de provenance par SHA-256, laboratoire AutoResearch, oracle mathématique indépendant et vérificateur de coût/régression de la PR #83. Les modules RCE/P1/P2/P3 sont copiés à l'identique depuis le commit PR #89 `83d6d62e6bc090c04a379c678da000bf2c886c44` et isolés sur cette branche. Le modèle Qwen et le protocole d'exécution viennent de la PR #85.

## Chaîne réalisée par `integrated_cycle.py`

1. `plan_mission` : active des perspectives réfutateur, formaliste et calculateur pour la mission Q^h/Δ_h, sans exécuter d'agent indépendant.
2. `prepare_contexts` : lit le checkout en lecture seule, prépare un paquet P2 par rôle, calcule une empreinte SHA-256 et conserve la couverture des recherches.
3. **Mode plan** : aucun programme évalué ; les trois perspectives restent `not_executed`.
4. **Mode templates** : quatre sources déterministes auditables (linéaire ou exponentiation binaire, scan ou lowbit), sélection sur *trois cas de développement*, choix d'une seule référence classique forte **sur le développement**, vérification sur *trois autres graines gelées* ; exactitude `Q^h` par programmation dynamique ensembliste et `Δ_h` via trajectoires directes. `gate.py` contrôle coûts, erreurs et non-régressions. **Décision forcée `REJECTED_TEMPLATE_ONLY`** même en cas de vitesse supérieure au témoin : ce n'est pas une invention.
5. **Mode model** : deux appels réellement nouveaux à Qwen2.5-Coder-3B GGUF avec llama.cpp (poids et code de l'inférence épinglés), analyse AST de la source produite, tests de développement, exécution dans Docker sans réseau et lecture seule. Les cas réservés sont préparés et leur empreinte imprimée avant l'inférence. Deux classiques forts sont requis, `square-scan` et `square-lowbit`, ainsi qu'une absence de duplication de source. Si le modèle échoue ou si la référence gagne, **REJECTED** ; sinon **REVIEW_REQUIRED**, jamais `CORE`.
6. L'exécution effectivement réalisée est enregistrée comme perspective `computational` par P3 ; les rôles non exécutés restent déclarés. Le journal d'événements construit des liens SHA-256 pour plan, contexte et sortie ; la chaîne est vérifiée avant d'émettre le JSON.
7. La CI est **en lecture seule sur le dépôt**, archive les traces, n'appelle aucune API de modèle payante et ne fusionne rien.

## Sources, tests et commandes

- [Pré-enregistrement](PREREG_2026-11-15.md), déposé avant tout run nouveau.
- [Entrées réservées au mode templates](CYCLE_INPUTS.json), gelées avant les exécutions.
- [Code d'intégration](integrated_cycle.py) et [tests d'intégration](test_integrated_cycle.py).
- [Workflow complet](../../.github/workflows/omega-integrated-cycle.yml) — job de test rapide, suivi d'un job Qwen **uniquement si le premier job réussit** ; limites de durée strictes, artefacts JSON.
- Exécution locale (Python 3.12, aucun modèle nécessaire) depuis la racine :

```sh
python -m unittest discover -s 09_INFRASTRUCTURE_AGENTIQUE/integrated_cycle -p 'test_integrated_cycle.py' -v
python 09_INFRASTRUCTURE_AGENTIQUE/integrated_cycle/integrated_cycle.py --mode plan --output cycle-plan-result.json
python 09_INFRASTRUCTURE_AGENTIQUE/integrated_cycle/integrated_cycle.py --mode templates --output cycle-template-result.json
```

La commande `--mode model` exige `--llama-cli` et `--model-file` ; elle refuse un repli silencieux vers un programme manuel. Les téléchargements du poids Qwen et le Docker sont gérés par la CI.

## Frontières non franchies

- P1/P2 préparent le contexte et **le journalisent** : la boucle `model_pilot.py` emploie son **prompt public fixe**, **sans injection des résultats RCE dans la proposition**. Le module de contexte ne modifie donc pas la stratégie actuelle ; un gain attribué à la mémoire serait abusif.
- La mémoire n'est pas mise à jour automatiquement ; P3 est un enregistreur supervisé et non un essaim indépendant.
- Les empreintes d'événements établissent l'intégrité du journal local, mais pas l'authenticité indépendante d'une preuve externe.
- Les jeux de développement et de réserve sont synthétiques et/ou internes. Le protocole n'est pas scellé par un évaluateur tiers.
- Une source de modèle correcte ne signifie pas une innovation ; la maîtrise du coût CPU est bruitée. Aucun gain de compétence ou de généralisation ne peut être revendiqué à partir d'un seul pilote.
- **Le nombre de tests, les statuts CI et les verdicts exacts ne seront publiés qu'après inspection des runs effectifs.**

## Critère de décision

Le test est techniquement réussi si le rapport contient plan+contexte+exécution+deux références+preuve exacte+porte+chaîne d'événements valide et qu'une défaillance bloque le run.

Le candidat scientifique n'est **pas promu automatiquement** même si `REVIEW_REQUIRED`. Sa promotion exige une nouvelle cohorte externe, indépendamment scellée, le même budget, au moins une amélioration face à un classique fort **sans aucune régression**, et reproduction indépendante.

Pas de modification de `main`, ni des branches des PR #81/#83/#85/#89.
