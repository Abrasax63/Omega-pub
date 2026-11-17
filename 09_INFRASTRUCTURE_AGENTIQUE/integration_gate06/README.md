# OMEGA-INTEGRATION-06 — raccordement réel, mais périmètre borné

Cette expérience **DRAFT** est empilée sur [PR #149](https://github.com/Abrasax63/Omega-pub/pull/149) et ne modifie ni `main`, ni le moteur mathématique de PR #148, ni aucune fiche certifiée.

## Ce qui est réellement raccordé
- Registre de sources générique `SOURCES_FROZEN.json` : identifiant arbitraire → fichier relatif + hash Git blob ; protection contre modifications, chemins hors dépôt et liens symboliques.
- Lecture de quatre sources mathématiques historiques réelles avec leurs lignes exactes ; aucun `if source_id == ...` dans le chargeur.
- Qwen2.5-Coder-3B-Instruct quantifié via `llama.cpp` CPU déjà employé en PR #141 (mêmes épingles SHA), **sans API payante**.
- Deux appels modèles par question : A question seule, B même question avec sa source. C = verdict B filtré par un oracle fini après gel des réponses, sans troisième appel.
- Un contrôle symétrique `A+oracle` isole le bénéfice possible du filtrage, indépendamment de la mémoire.
- Douze questions inédites, gelées après le préenregistrement mais avant l'implémentation. Source documentaire déjà connue et cohorte de même auteur : **aucun aveugle externe**.

## Exécuter
Depuis un checkout de cette branche, sans installer de dépendance Python :
```bash
cd 09_INFRASTRUCTURE_AGENTIQUE/integration_gate06
python3 -m unittest -v test_integration.py
```

L'exécution du petit modèle dépend des poids GGUF et du binaire `llama-cli` épinglés :
```bash
python3 integration.py --llama-cli /chemin/llama-cli --model-file /chemin/model.gguf --output /tmp/omega-integration06.json
```

La CI `.github/workflows/omega-integration06.yml` réalise les tests CPU sans modèle, puis les appels réels et archive le rapport JSON brut. En cas d'échec CI, ne pas présenter le résultat scientifique comme vérifié.

## Interprétation des bras
| Bras | Source | Oracle pendant choix | Filtre après choix |
| --- | --- | --- | --- |
| A `solo` | non | non | non |
| B `memory` | oui | non | non |
| A+ `solo_checked` | non | non | oui |
| C `memory_checked` | oui | non | oui |

L'oracle fini connaît la réponse parce qu'il énumère les mots du petit automate à deux états ou les sous-ensembles de quatre témoins. L'absence d'erreur après filtrage n'établit **pas** que Qwen est devenu plus intelligent. Cet oracle n'est pas utilisable tel quel pour valider des théories arbitraires ; les comptes GitHub Actions sont des tests, pas une certification universelle.

Les résultats **déjà négatifs** des PR #147 et #149 demeurent inchangés. Les 12 cas de ce pilote deviennent contaminés dès la première lecture des scores : ne jamais les recycler comme un nouveau holdout.
