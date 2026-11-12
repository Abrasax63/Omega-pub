# Omega P5 v0.5 — comptabilité USD et réutilisation d'une clé API existante

**12 novembre 2026 — Implémentation proposée sur PR #47.** Le code et les tests sont publics; les questions privées, la clé API et les réponses restent privées.

## Portée

- **Aucune nouvelle clé API requise.** Le runner utilise `OpenAI()`, qui lit la clé de l'environnement d'exécution (`OPENAI_API_KEY`). Ne jamais coller cette valeur dans Git, les arguments de ligne de commande, les logs, les tickets ou une conversation.
- L'extension `prism/p5_v05_costs.py` calcule des estimations **USD par requête**, par bras A/B/C et pour l'ensemble des 96 générations. Elle n'accède **ni aux factures ni au compte de crédits**.
- Une **fiche tarifaire explicite**, propre à l'identifiant exact du modèle, vérifiée sur la [page tarifaire officielle](https://platform.openai.com/pricing), avec date UTC de vérification, est obligatoire pour toute génération. La fiche refuse une vérification vieille de plus de sept jours. **Ce contrôle de date ne prouve pas l'exactitude du prix saisi** : l'opérateur doit la vérifier.
- Les prix sont fixés en USD par million de tokens et calculés avec `Decimal`. Chaque token d'entrée est compté au tarif **non mis en cache**, sans supposer une réduction de cache. La réservation préalable ajoute le plafond de tokens de sortie entier sur chacune des 96 requêtes. Il faut respecter `--max-estimated-usd` avant la première génération.
- Un dépassement ou une différence entre compte initial et usage réel stoppe l'exécution. Une requête déjà émise reste potentiellement facturable; ce contrôle interne n'est **pas** un plafond de facturation garanti au niveau de la plateforme.
- Les coûts d'autres services, taxes, surcharges régionales/tiers, remises, opérations de comptage et éventuelles particularités contractuelles sont hors estimation. Utiliser uniquement un modèle et un mode de traitement conformes à la fiche tarifaire; en cas de doute, **ne pas lancer**.
- Les coûts **réellement facturés** doivent ensuite être rapprochés avec un export officiel du [tableau de bord API Usage](https://platform.openai.com/usage), filtré sur le bon projet/la bonne clé et la bonne plage de dates UTC. Les exports peuvent être regroupés par clé API ou projet; le journal local permet d'attribuer les dépenses estimées à A/B/C, pas nécessairement la facture au niveau de chaque bras.

## Fiche privée de tarifs (exemple de structure, valeurs à vérifier)

Créer un JSON **hors du dépôt Git**, avec la structure suivante, en remplaçant les valeurs et l'horodatage par les tarifs officiels du modèle choisi :

```json
{
  "model": "IDENTIFIANT_EXACT_MODELE",
  "currency": "USD",
  "processing_mode": "standard",
  "input_usd_per_million": "TARIF_ENTREE",
  "output_usd_per_million": "TARIF_SORTIE",
  "source_url": "https://platform.openai.com/pricing",
  "checked_at_utc": "2026-11-12T07:00:00Z"
}
```

Les valeurs `TARIF_ENTREE` et `TARIF_SORTIE` ci-dessus sont des placeholders et **ne doivent jamais être utilisées pour lancer le runner**.

## Commande côté opérateur authentifié, hors CI publique

Dans un environnement privé disposant **déjà** de `OPENAI_API_KEY` (clé existante), avec les entrées privées vérifiées contre leur manifeste :

```bash
cd 09_INFRASTRUCTURE_AGENTIQUE/prism
python -m unittest -v test_p5_v05_costs test_p5_v05_private_runner
python p5_v05_private_runner.py \
  --inputs /private/P5V05/inputs_private.json \
  --manifest ../evaluation/p5_v05_candidate_public_manifest.json
```

Ce préflight n'appelle **aucun modèle**. Pour une exécution réelle après validation des prix et du budget par l'opérateur :

```bash
python p5_v05_private_runner.py \
  --inputs /private/P5V05/inputs_private.json \
  --manifest ../evaluation/p5_v05_candidate_public_manifest.json \
  --execute --allow-billable-api \
  --model "IDENTIFIANT_EXACT_MODELE" \
  --total-token-cap 4096 --output-token-cap 1200 \
  --max-generation-calls 96 \
  --pricing-json /private/P5V05/rate_card.json \
  --max-estimated-usd "BUDGET_USD_APPROUVE" \
  --output-dir /private/P5V05/outputs/unique-run-id
```

Les plafonds `4096`/`1200` illustrent la syntaxe, ne sont pas pré-approuvés et doivent être vérifiés avec le modèle. La commande volontairement non exécutable tant que l'identifiant exact et le budget ne sont pas renseignés.

## Statut scientifique et comptable

- **Tests mock** : 0 requête de génération réelle; aucune dépense réelle vérifiée; coût simulé seulement.
- **Live, non noté** : tokens observés, prix gelés, estimation USD par bras et total; `billed_usd: null` jusqu'à rapprochement.
- **Coût confirmé** : montant du relevé OpenAI sur la période et le projet/clé correspondants, enregistré séparément avec date, source et limites d'attribution.
- **Gain scientifique** : non établi par la seule existence de cette instrumentation. P5 v0.5 reste une cohorte candidate interne qui nécessite une revue indépendante.

La branche de PR #47 seulement a été modifiée. `main`, la cohorte privée et les engagements SHA antérieurs sont inchangés.
