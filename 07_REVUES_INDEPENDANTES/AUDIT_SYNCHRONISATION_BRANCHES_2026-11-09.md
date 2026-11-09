# Audit de synchronisation des branches — 9 novembre 2026

**Dépôt :** `Abrasax63/Omega-pub`  
**Référence de comparaison :** `main` au commit `0ca3c5f63998cf16cc84478c7735c03445a08669`  
**Nature :** photographie Git et triage documentaire. Aucun statut scientifique n'est modifié.

## 1. Sauvegardes de références

Des branches de checkpoint ont été créées sans réécrire les historiques :

- `checkpoint/main-2026-11-09`
- `checkpoint/maintenance-2026-11-09`
- `checkpoint/migration-2026-11-09`
- `checkpoint/architecture-2026-11-09`
- `checkpoint/site-2026-11-09`
- `checkpoint/colab-bridge-2026-11-09`

Elles servent de points de retour vers les têtes examinées le 9 novembre. Aucune branche source n'a été supprimée ou forcée.

## 2. Comparaison à main

| Branche | État | En avance | En retard | Décision |
|---|---:|---:|---:|---|
| `maintenance/reconciliation-bibliotheque-2026-11-05` | diverged | 131 | 1 | Base de consolidation via PR #5 ; revue des différences avant fusion |
| `architecture/memoire-agentique-native-2026-11-05` | diverged | 43 | 1 | PR #7 à conserver séparée ; pas de fusion directe |
| `migration/ravi2-ccs-public-2026-11-04` | diverged | 269 | 64 | Archive source ; migration sélective uniquement |
| `migration/ravi2-ccs-public-2026-11-04-clean-test` | behind | 0 | 64 | Aucun commit propre ; ne pas utiliser comme source |
| `site/vitrine-github-pages-2026-11-05` | diverged | 4 | 1 | PR #6 ; contrôler le contenu et la configuration Pages |
| `colab-bridge-2026-11-06` | ahead | 2 | 0 | Candidate séparée ; contient un notebook de test et un notebook de publication GitHub par secret Colab |
| `test/colab-runtime-2026-11-06` | ahead | 1 | 0 | Candidat le plus simple : un notebook de test sans secret |
| `pilot/ravi2-extraction-c4-20261104` | diverged | 14 | 1 | Apports repris en grande partie dans PR #5 ; garder comme provenance |
| `ravi2/methodes-openai-c4-pilot` | diverged | 7 | 1 | Apports repris en grande partie dans PR #5 ; garder comme provenance |

Les écarts « en retard » sont calculés contre la tête actuelle de `main`, et peuvent différer des nombres figurant dans des audits antérieurs.

## 3. Réconciliation des PR ouvertes

- **PR #5** : consolidation RAVI-2/C4/C5 et audit de migration ; sa liste de fichiers modifiés (47) correspond au périmètre de la branche maintenance. Elle reste la voie principale de revue, en brouillon.
- **PR #7** : architecture RCE/multi-agent et passerelle ; à examiner séparément de la consolidation scientifique.
- **PR #6** : vitrine GitHub Pages ; à examiner séparément, car le contenu public doit rester aligné sur les statuts et réserves de l'index.
- **PR #2** : migration historique de 226 fichiers ; à ne pas fusionner en bloc.
- **PR #3 et #4** : leurs apports sont documentés comme repris dans PR #5 ; les conserver comme provenance, ne pas les fusionner séparément.

## 4. Contrôles documentaires constatés

La branche maintenance porte l'index global version 0.3 et le registre transversal version 0.2, ajoutant le pilote C4/L=2 avec son périmètre et son statut de publication EXPÉRIMENTAL. Elle contient également :

- le rapport de réconciliation de la bibliothèque ;
- l'inventaire et la réconciliation détaillée des 226 fichiers de PR #2 ;
- les scripts et rapports C4/L=2 ;
- le dossier C5/L=3 et ses exports ;
- le noyau Lean V19 et ses workflows de compilation.

L'audit des 226 fichiers attribue : 3 « transféré et vérifié », 2 « transféré mais non vérifié », 183 « à transférer » et 38 « doublon ou archive ». Ces statuts décrivent la migration documentaire, pas la validité scientifique.

## 5. Colab — séparation des risques

Le notebook `notebooks/colab_runtime_smoke_test.ipynb` est un test local de runtime et d'arithmétique déterministe ; il ne demande aucun jeton.

Le notebook `notebooks/colab_github_bridge.ipynb` lit un secret Colab nommé `OMEGA_GITHUB_TOKEN` et peut publier un rapport sur la branche de test via l'API GitHub. Aucun jeton n'est inclus dans le fichier inspecté. Cette capacité d'écriture doit être revue séparément avant exécution ; ne jamais coller le secret dans une cellule ou dans le chat.

## 6. Décisions de synchronisation

1. Utiliser PR #5 comme voie de consolidation documentaire, sans fusion automatique et après contrôle des conflits et des workflows.
2. Maintenir PR #7 comme module indépendant ; aucun résultat scientifique ne doit être modifié par le RCE.
3. Maintenir PR #6 séparée jusqu'au contrôle des contenus publiés.
4. Proposer le notebook Colab minimal via une PR distincte ; ne pas intégrer le notebook à jeton dans la même opération.
5. Ne pas fusionner PR #2 en bloc. Migrer les 183 éléments restants par lots, après lecture, provenance, sécurité, liens et statut.
6. Conserver les branches pilotes et historiques comme traces, sans les supprimer.

## 7. État des écritures au moment de cet audit

Les seules écritures effectuées pour cette opération sont la création des six branches de checkpoint et l'ajout de ce rapport sur la branche maintenance. `main` n'a pas été modifiée. Aucune PR n'a été fusionnée, aucune branche source n'a été supprimée, et aucune base SQLite privée n'a été touchée.

**Verdict :** sauvegardes de branches effectuées ; cartographie et triage réalisés ; synchronisation par fusion non encore exécutée. Les PR constituent les points de revue avant toute intégration dans `main`.
