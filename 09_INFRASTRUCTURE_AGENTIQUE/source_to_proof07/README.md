# Omega SOURCE-TO-PROOF-07 — prototype opérationnel mais borné

**Statut :** DRAFT / vérification de logique structurée seulement. Fonctionne avec Python 3.12, bibliothèque standard, sur la branche de [PR #153](https://github.com/Abrasax63/Omega-pub/pull/153), sans API et sans entraîner de modèle de langage. **N'est pas déployé dans le RCE natif, le site ou le cycle autonome.**

## Ce que fait effectivement la commande

1. Découvre les fiches Markdown existantes et une fiche de test nouvelle à partir de leur titre ; aucun identifiant de brique n'est codé dans la règle.
2. Vérifie que le Git blob de la source correspond exactement à celui annoncé par l'appelant.
3. Extrait des règles Horn à partir des phrases à syntaxe explicite `Si \`a\` et \`b\`, alors \`c\`.`, **ou** les préconditions et bornes de sélection `0≤m_ω≤ν(ω)` présentes dans une fiche mathématique réelle.
4. Calcule un verdict conditionnel, une trace de preuve reliant les prémisses et les lignes sources, et un contrôle indépendant : table de vérité ou énumération exhaustive des sous-ensembles.
5. Si la source n'est pas reconnue, les préconditions n'ont pas été fournies, la preuve est falsifiée ou la relation est hors grammaire, n'affirme rien.

## Utilisation directe sur une source historique

Sur la branche, créer hors du dépôt un fichier JSON `/tmp/omega-question.json` avec le contenu :

```json
{
  "id": "EXEMPLE01",
  "source_id": "BR-OBS-CAP-03",
  "expected_source_blob": "e2db670f4f9458a848b7d8719f2a656dbfdab46b",
  "kind": "capacity",
  "independent_selection": true,
  "witness_motifs": ["A", "A", "A", "B", "B"],
  "requested": {"A": 2, "B": 1}
}
```

Puis exécuter :

```sh
python3 09_INFRASTRUCTURE_AGENTIQUE/source_to_proof07/pipeline.py --query /tmp/omega-question.json
```

Résultat attendu sur cette instance : `SUPPORTED` avec les lignes sources, les capacités par motif, les indices de témoins choisis, `certificate_valid:true` et le résultat de l'oracle par énumération. Si on demande `{"A":2,"B":3}`, le verdict attendu est `CONTRADICTED` sous les mêmes hypothèses, non une règle générale sur les systèmes physiques.

Pour rejouer **le même jeu de développement, non aveugle** et son rapport inspectable :

```sh
python3 09_INFRASTRUCTURE_AGENTIQUE/source_to_proof07/pipeline.py --output /tmp/omega-source-to-proof07.json
```

## Limites techniques à ne pas masquer

- Les questions et les hypothèses sont actuellement fournies au format JSON structuré. Aucune traduction libre de la question en langage naturel n'est revendiquée.
- L'extracteur lit **uniquement** un langage de clauses contrôlé et un motif mathématique précis (borne de capacités, avec conditions d'application reconnues). Il n'extrait pas de façon autonome des théorèmes généraux depuis un Markdown quelconque.
- Un certificat d'instance vérifie le raisonnement **par rapport à la représentation extraite**. Il ne prouve pas que la formalisation de la source est sémantiquement complète ni que le statut historique de la fiche est correct.
- La cohorte de 12 exemples a été créée par le même auteur avant implémentation ; elle n'est ni externe, ni aveugle, ni représentative de la recherche mathématique réelle.
- Ni le petit Qwen ni les poids d'Omega ne sont améliorés par ce pilote. Le parseur Qwen de #150 doit être diagnostiqué séparément.
- Ne pas fusionner ni promouvoir `main` avant une évaluation prospective indépendante. La prochaine expérience décisive est de **traduire automatiquement une question libre en un tel JSON**, par un composant distinct, puis de mesurer les refus, erreurs de traduction, coûts et bénéfice par rapport à la référence sur des documents nouveaux.
