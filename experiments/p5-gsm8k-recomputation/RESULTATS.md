# Recalcul à partir de l’énoncé seul

Le corpus GSM8K est réutilisé. L’échantillon comprend 24 questions tirées par hachage parmi les 719 réservées dans l’expérience arithmétique. Le candidat est Llama 8B. Deux politiques autorisent sa publication, soit si Llama 1B produit la même réponse extractible, soit si le résultat du programme rédigé à partir de l’énoncé coïncide. Chaque politique dispose d’un contrôle par question. Le travail humain de traduction et le coût d’une inférence n’ont pas été mesurés.

Les programmes ont été consignés au commit [8ad2701](https://github.com/Abrasax63/Omega-pub/commit/8ad2701c957af618bc717faf5ba35d0998c46a62) avant ouverture des réponses et des références. Ils sont spécifiques à chaque question. Le parseur est celui de la [PR #71](https://github.com/Abrasax63/Omega-pub/pull/71). [Exécution de préparation](https://github.com/Abrasax63/Omega-pub/actions/runs/43309000277).

| Politique | Publications | Exactes selon GSM8K | Divergences |
|---|---:|---:|---:|
| Accord des modèles | 6 | 6 | 0 |
| Recalcul de l’énoncé | 18 | 17 | 1 |

Deux recalculs divergent du corrigé. En 19, un camion transporte au maximum 26 dalles entières. Trois camions en transportent 78 sur 80. En 21, « by 5 hours » indique une économie de cinq heures par jour, soit 135 kWh sur 30 jours à 0,9 kW. La référence 81 kWh correspond à une économie de trois heures par jour. Le tableau conserve les références archivées. La question 15 est ambiguë et le recalcul s’abstient.

| Cas | Candidat 8B | Témoin 1B | Recalcul | Référence GSM8K | Publier sur accord | Publier sur recalcul |
|---:|---:|---:|---:|---:|---|---|
| 1 | 200 | — | 120 | 120 | — | — |
| 2 | 60000 | 6000 | 60000 | 60000 | — | oui |
| 3 | 34 | 34 | 34 | 34 | oui | oui |
| 4 | 800 | 800 | 800 | 800 | oui | oui |
| 5 | 16 | 147/10 | 16 | 16 | — | oui |
| 6 | 13 | 13 | 13 | 13 | oui | oui |
| 7 | 40 | — | 40 | 40 | — | oui |
| 8 | 50 | — | 50 | 50 | — | oui |
| 9 | 156 | — | 156 | 156 | — | oui |
| 10 | 23 | 23 | 23 | 23 | oui | oui |
| 11 | 153 | 36 | 153 | 153 | — | oui |
| 12 | 480 | 80 | 320 | 320 | — | — |
| 13 | 75 | 300 | 75 | 75 | — | oui |
| 14 | 15 | 15 | 15 | 15 | oui | oui |
| 15 | 500 | 500 | — | 500 | oui | — |
| 16 | 141 | — | 89 | 89 | — | — |
| 17 | 8 | 20 | 8 | 8 | — | oui |
| 18 | 90000 | — | 90000 | 90000 | — | oui |
| 19 | 3 | 9 | 4 | 3 | — | — |
| 20 | 18 | — | 1800 | 1800 | — | — |
| 21 | 135 | 27/8 | 135 | 81 | — | oui |
| 22 | 44 | 36 | 44 | 44 | — | oui |
| 23 | 2100 | 900 | 2100 | 2100 | — | oui |
| 24 | 6 | — | 6 | 6 | — | oui |

## Recoupement sur le test arithmétique antérieur

Sur 82 questions où les deux modèles s’accordent, deux réponses communes sont fausses selon GSM8K. Dans les deux cas, au moins une des deux traces contient une erreur arithmétique détectable. Sur 254 questions où les deux réponses extraites divergent, une seule trace est cohérente jusqu’à la réponse finale dans 169 cas. Cette réponse est exacte dans 140 cas. Ce recoupement est descriptif et n’établit pas le risque d’une règle combinée sur un nouveau corpus. [Trajectoires sources](https://github.com/Abrasax63/Omega-pub/actions/runs/43307617478/artifacts/13983608929).
