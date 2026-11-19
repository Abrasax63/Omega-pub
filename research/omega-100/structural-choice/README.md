# Sélection déterministe de méthode à partir de la structure

19 novembre 2026, 14 h 52 (Paris). **IMPLÉMENTÉ / EXÉCUTÉ / VÉRIFIÉ sur réserve synthétique.** Branche `experiment/omega-100-2026-11-18`, départ `27b44d8aec9e5020b7c7dd3fa1631ace40daefbf`. Pilote hors numérotation, suite du [comparatif Qwen](../choice-pilot.md).

## Hypothèse et protocole

Le [protocole figé](protocol.md) demande si une décision déterministe peu coûteuse peut récupérer au moins deux cas par rapport à B fixe, sans erreur ni perte des réussites de B. Sur le lot croisé précédent utilisé en développement, les méthodes fixes résolvent chacune 8/16 et la règle 16/16. Cette mesure de développement ne compte pas comme gain réservé.

La règle choisit A si toutes les relations de parité sont des égalités ou, pour une somme, si la cible figure parmi les valeurs. Elle choisit B ailleurs. Les solveurs sont ceux du pilote précédent. A énumère des masques, avec un essai préalable des valeurs seules pour les sommes. B propage les parités par graphe ou maintient les sommes atteignables. Le sélecteur ne rend pas le verdict. L'oracle indépendant énumère exhaustivement les possibilités et vérifie les témoins. Le témoin contradictoire (une égalité et une inégalité sur la même paire) et le contrôle de somme impossible sont rejetés avant le test. Chaque politique applique au plus un solveur, avec un plafond de 64 étapes de résolution. Le temps de décision est facturé à chaque politique. L'oracle d'évaluation est hors des coûts pour toutes.

Réserve de 24 nouvelles instances synthétiques, 12 de chaque famille, créée après gel du code et avant évaluation. Elle comprend des cas favorables aux deux méthodes, des cas où la règle peut échouer et des cas hors budget. Qwen reçoit uniquement l'instance et le descriptif des méthodes. Les étiquettes et les sorties des solveurs ne figurent pas dans l'invite.

## Résultats

| Politique | Parité correcte | Somme correcte | Total correct | Abstentions | Erreurs | Temps décision + résolution |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| A fixe | 7/12 | 6/12 | 13/24 | 11 | 0 | 0,154 ms |
| B fixe | 5/12 | 7/12 | 12/24 | 12 | 0 | 0,182 ms |
| Règle structurelle | 8/12 | 9/12 | 17/24 | 7 | 0 | 0,157 ms |
| Qwen, choix en une lettre | 5/12 | 6/12 | 11/24 | 13 | 0 | 35,659 s |

La règle récupère cinq cas face à B sans perte. Elle donne quatre résultats corrects de plus que A au total, mais perd deux cas résolus par A seul. Ces deux cas sont des graphes denses signés où un masque précoce satisfait les relations avant le plafond. Cinq autres cas dépassent les possibilités des deux méthodes sous le plafond. Le plafond d'un choix parfait a posteriori est donc 19/24 sur ce lot.

Les temps déterministes sont des médianes sur 200 passages complets du même lot. La règle prend 9,22 µs par résultat correct dans ce banc, contre 15,15 µs pour B et 11,82 µs pour A. Les différences de temps sur ces petites instances restent indicatives. Qwen2.5-Coder-3B-Instruct Q4_K_M choisit B 23 fois et N une fois. Il utilise 7 315 jetons d'entrée et 24 de sortie, à raison d'un appel par problème. Ses 35,659 s incluent 35,659 s de sélection arrondies et moins de 1 ms de résolution. Chaque méthode déterministe n'utilise aucun jeton. Aucun entraînement.

Le [diagnostic de budget](sensitivity.md), fixé séparément après la comparaison principale, facture une étape pour chaque signe ou valeur inspectée par la règle dans le plafond de 64. Sur la même réserve, elle conserve 16/24, gagne quatre cas sur B et n'en perd aucun. Ce diagnostic ne constitue pas une nouvelle réserve. Les [résultats principaux](results.json), le [développement](development.json) et le [diagnostic](sensitivity.json) sont fournis en agrégats.

**Décision.** Conserver la règle comme candidat expérimental et comparateur pour ce type d'instances. Les 16 tests métier passent, ainsi que les contrôles du pilote. La réserve a été construite pour exposer les compromis entre les méthodes, donc les proportions ne mesurent pas la fréquence de ces cas sur des tâches réelles. Prochain essai : un test borné des tout premiers masques suivi de B avec le budget restant, afin de traiter les graphes denses signés. Le comparer à la règle actuelle sur des familles séparées.

## Reproduction

Reprendre le solveur à une lettre du [pilote précédent](../choice-pilot.md) en appliquant les deux patchs documentés. L'enregistrer sous `solver.py`, remplacer 18727 par 18728 et lancer le même serveur sur 18728. Les mêmes poids locaux et paramètres sont utilisés, dont température 0, graine 71 et sortie limitée à une lettre.

```sh
python run.py CAS_DEVELOPPEMENT.json --development
python run.py CAS_RESERVES.json
python charge.py CAS_RESERVES.json
```

Le format des entrées est celui du pilote précédent, avec 12 objets parity (n, edges) et 12 subset (values positives, target) pour la réserve. Corrigés et cas individuels conservés hors commit. SHA-256 : réserve locale `40b89864c51a8ed608e9524e06670efb590490400e10386b7ea9a5af99feb229`, solveur `75438267effaa92effc00bd78ca2452ee0b4e82dadb3971c7371580a7373dac7`, règle `9bbeee746094e3e04deecebd8743675ecdcf90cb098650028466b156afa24854`, harnais `d26703c21dc6c54b8d7fea950b9946f8f61a4d29d93ba3e234c5a818d2a5e5ca`, résultats `2c19a4b6b6ac66bb9d80b045d2dba4549163301106e5e9bb8855591d829c6e11`.
