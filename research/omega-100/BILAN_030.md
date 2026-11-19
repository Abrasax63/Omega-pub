# Omega 100 — revue au jalon 30

19 novembre 2026. Branche `experiment/omega-100-2026-11-18`. Revue documentaire des001–029 au SHA [6a2a37edfd12371de076281b018b030115e42b48](https://github.com/Abrasax63/Omega-pub/commit/6a2a37edfd12371de076281b018b030115e42b48), puis exécution effective de030 dans ce passage. [Manifeste des fiches relues et blobsGit](030-review-manifest.json).

**30 expériences numérotées documentées comme exécutées ; ce bilan n'est pas une réplication indépendante des30.** Les001–029 ont été relues avec leurs résultats chiffrés, commandes et limites ;030 a été exécutée ici. Les préparations séparées ne sont pas comptées. Les résultats négatifs et contrôles conformes comptent comme expériences, jamais comme améliorations.

001–020 ont traité la lecture Markdown, l'abstention sur contexte incomplet, les doublons/conflits de revendications, les types de ligne et l'intégrité des fichiers. Le premier cycle rapportait des tests historiques incomplets dans une copie partielle ; les correctifs ultérieurs et les gels épinglés sont évalués séparément. Ne pas transformer rétrospectivement ce premier état en suite entièrement passée.

| Cycles21–30 | Résultat établi | Limite principale |
| --- | --- | --- |
| 021,023,027 | Citations exactes, conformité au contrat et validité arithmétique ne garantissent pas la restitution des hypothèses | Les pertes de portée peuvent rester mathématiquement vraies |
| 022 | Complétude des prémisses contrôlée par contrat manuel | Un contrat incomplet peut masquer une omission |
| 024,026 | Contre-exemples finis et vacuité dans le domaine explicitement signalés | Formalisation manuelle, aucune preuve universelle |
| 025 | Invariances testées et témoin hors domaine distingué | Aucune fidélité automatique au texte |
| 028 | Citations et sous-AST associés au contrat épinglé | Contrat humain de confiance, égalité syntaxique stricte |
| 029,030 | Faux rejets d'égalités commutées reproduits puis corrigés sur nouvelles réserves | Normalisation très limitée, surcoût mesuré |

Gain du jalon030 : deux équivalences réservées récupérées, zéro altération admise, environ2,25fois le temps de la référence stricte. Ce gain n'est pas additionnable aux TP/FP des22,24,26ou28 : leurs tâches et dénominateurs diffèrent.

Les gains établis restent des propriétés de logiciels déterministes et de fixtures annotées. Cette revue n'établit aucune amélioration de poids de modèle, de compréhension automatique, d'invention scientifique ou d'apprentissage autonome. Les sources et traductions AST de cette phase sont fournies manuellement. Aucun succès de parsing ou de CI ne devient une preuve scientifique.

Décision : garder les candidats expérimentaux, leurs références et leurs résultats sur cette branche ; aucune fusion ou promotion automatique. Le premier verrou à traiter est le raccord de ces composants avec des statuts cohérents et des refus explicites, puis une évaluation de fidélité indépendante du contrat manuel. Prochain essai031 défini dans030 ; prochaines revues aux jalons40et suivants. Le programme continue jusqu'à100expériences vérifiées comme exécutées, pas jusqu'à100correctifs ni100succès.
