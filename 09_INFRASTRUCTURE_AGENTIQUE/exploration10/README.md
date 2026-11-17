# Omega Exploration 10 — deux voies séparées

Une **voie exploratoire** propose plusieurs pistes à partir d'un document, même lorsque les phrases ne correspondent à aucune grammaire logique connue. Un **sceptique documentaire** exige que chaque extrait cité existe dans la source et refuse les fausses certifications. La **voie scientifique stricte** conserve intégralement le comportement du traducteur de #155 : une hypothèse exploratoire ne devient jamais une réponse démontrée par simple similarité lexicale.

## Exécution

```bash
python3 09_INFRASTRUCTURE_AGENTIQUE/exploration10/explorer.py \
  --output /tmp/omega-exploration10.json
python3 -m unittest discover -s 09_INFRASTRUCTURE_AGENTIQUE/exploration10 \
  -p test_explorer.py -v
```

Le rapport présente les 30 questions extérieures consécutives FOLIO **31–60**, leurs sources verbatim, les hypothèses proposées et leurs extraits, les tests discriminants **proposés mais non exécutés**, les statuts, le verdict strict, les coûts et le verrou de hachage des décisions avant lecture des labels.

## Perspectives expérimentales

- **Rapprochement lexical** : une prémisse partage des termes avec la conclusion ; cela ne prouve aucune implication
- **Contre-modèle** : chercher une interprétation où une prémisse serait vraie mais pas la conclusion
- **Pont manquant** : repérer des concepts de la question absents des prémisses
- **Négation** : quand la source contient des négations, recommander de contrôler leur portée

Les propositions sont structurées et hiérarchisées pour être inspectables, mais **ne sont ni des preuves ni une intelligence sémantique générale**. Tous les tests de fidélité des citations sont exécutés ; aucun test de validité sémantique d'un théorème n'est exécuté par cette version. Chaque suggestion reste `HYPOTHESIS_UNVERIFIED`, avec une vérification suggérée et `NOT_EXECUTED`.

Un modèle de langage gratuit pourra ultérieurement servir de générateur de plusieurs interprétations, mais cette connexion **n'est pas présente**, pour séparer d'abord le comportement exploratoire du coût et des hallucinations d'un modèle. Ne pas affirmer que le programme apprend ou s'auto-améliore sur ce premier pilote.

## Analyse méthodologique

- Préenregistrement : `PREREG_2026-11-17.md` figé avant code
- Corpus extérieur : FOLIO/Yale v0.0, fichier validation source au commit `5d7bb84c`, Git blob amont `06244bd1`, lignes **31–60**, sans traduction humaine ; les labels sont lus **après** génération des hypothèses
- Attribution : [Han et al., FOLIO, licence CC BY-SA 4.0](https://github.com/Yale-LILY/FOLIO)
- Les 30 questions ne sont pas indépendantes si elles partagent le même jeu de prémisses
- Les labels d'origine sont des références publiées, pas des preuves mathématiques certifiées
- Le moteur conservateur, Qwen, les poids et le cycle autonome ne sont pas modifiés. Aucune fusion automatique.

La seule démonstration prévue est la **possibilité de conserver plusieurs pistes traçables sans leur attribuer un statut indu**. Le nombre d'hypothèses créées n'est **pas** une métrique de créativité scientifique ni une augmentation de précision.
