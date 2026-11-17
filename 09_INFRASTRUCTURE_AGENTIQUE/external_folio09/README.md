# OMEGA — épreuve extérieure FOLIO-09

**Objectif : tester la capacité actuelle, pas l'améliorer en regardant les réponses.**

Ce dossier évalue le traducteur français figé de [PR #155](https://github.com/Abrasax63/Omega-pub/pull/155), dont le blob Git est `385aca9258d69c4545df891a31f1c4ae719a82b8`, sur un corpus publié indépendamment : [Yale-LILY/FOLIO](https://github.com/Yale-LILY/FOLIO), `data/v0.0/folio-validation.jsonl` au commit `5d7bb84c7edab3fb358e057d2807f19cf5cf5e2d`, blob `06244bd10b37eac73cba7aca6c336e96011ace58`.

Le fichier `FOLIO_VALIDATION_FIRST30_FROZEN.jsonl` contient **exactement les lignes 1 à 30**, sans sélection en fonction du label, des conclusions ni des capacités du pilote, immuable par blob `7aedc646fb2c3588ebd04335fbf74cb56fb32688`. Les 30 cas appartiennent à 10 ensembles de prémisses distincts ; ce n'est pas une étude statistique sur 30 histoires indépendantes. Les labels publiés : True 11, False 6, Uncertain 13. Ce sont des labels de dataset, **pas des vérités nouvellement certifiées**.

## Chaîne d'évaluation

Chaque ensemble de prémisses est enregistré **tel quel** dans une fiche Markdown temporaire, avec un en-tête de transport et une empreinte Git. La conclusion originale, **en anglais, sans traduction ni backticks ajoutés**, est présentée au traducteur figé. Aucune annotation formelle `-FOL` ni aucun label n'est fourni aux composants d'Omega. Les décisions et leur empreinte SHA-256 sont gelées avant la lecture des labels.

Si la grammaire ou une condition de sécurité n'est pas reconnue, Omega doit explicitement `ABSTAIN`. La notation True→SUPPORTED, False→CONTRADICTED, Uncertain→ABSTAIN ne sert qu'à comparer les sorties aux références publiées. L'abstention correcte sur Uncertain n'est pas une preuve mathématique ; le contrôle exige **au moins une bonne réponse affirmative ou réfutative et aucune erreur affirmée** pour un résultat favorable.

### Reproduction

Depuis la racine du dépôt, dans cette branche expérimentale :

```bash
python3 09_INFRASTRUCTURE_AGENTIQUE/external_folio09/evaluate_external.py \
  --output /tmp/omega-folio-external09.json
python3 -m unittest discover -s 09_INFRASTRUCTURE_AGENTIQUE/external_folio09 -p 'test_external.py' -v
```

L'expérience utilise uniquement Python 3.12 et le code existant du dépôt ; pas de dépendance payante ni de modèle externe. Les rapports se trouvent en dehors du checkout et sont archivés via GitHub Actions.

## Portée et attribution

**Provenance des données :** FOLIO, Han et al., *FOLIO: Natural Language Reasoning with First-Order Logic*, [dépôt et licence CC BY-SA 4.0](https://github.com/Yale-LILY/FOLIO). La copie des 30 entrées reste attribuée à ses auteurs, sous les mêmes conditions de partage. Le code expérimental est distinct des données de FOLIO.

Le jeu FOLIO v0.0 peut comporter des annotations contestables ; même un résultat positif exigerait une revue d'échantillons. Le test vérifie le transfert **de l'interface actuelle**, pas les capacités cachées du petit modèle Qwen, qui n'est pas exécuté ici. Les éventuelles erreurs de traduction anglaise et d'import documentaire sont distinguées de celles du vérificateur. Aucune adaptation du traducteur sur ces 30 cas ne doit être présentée comme validation indépendante.

Statut : expérimental, DRAFT, `main` inchangé, aucune fusion automatique.
