# V19 — minimum de cinq états et priorité par quotient

19 novembre 2026, vers 14 h 04 (Paris). **EXÉCUTÉ / VÉRIFIÉ**. Branche `work/omega-math-brick-pilot-2026-11-14`, SHA initial `b706ce15614e38a8f494f3017e22fd7a876d9046`, suite du [témoin à sept états](OBS-V19-FOUR-EVENT-CORE_2026-11-19.md). Le [protocole](../code/v19-pivot-protocol.md) a fixé familles, budget, témoin et seuil avant test. L'ombre est la projection des colorations extensibles à toutes les contraintes, dans le sens de [l'audit source](OBS-V19-LPLUS1-AUDIT_2026-11-14.md). Horizon 4, quatre égalités orbitales non triviales, cycle distingué de longueur au moins trois et contraintes forcées F cohérentes. Minimalité signifie qu'en enlevant n'importe laquelle des quatre égalités tout le système redevient cohérent.

## Taille minimale : cinq états

T=(1,2,3,0,0), cycle (0,1,2,3), paire (0,4). Le seul XOR forcé est c3 XOR c4=1. Les quatre égalités forment le chemin 4–0–1–2–3 et imposent c4=c3. La suppression d'une arête coupe ce chemin. Colorer les deux composantes en valeurs opposées satisfait le XOR restant. Projection exhaustive : 0 ombre avec toutes les égalités, 2 colorations du cycle après chacune des quatre suppressions.

**Borne inférieure.** Quotienter les composantes de F et fixer dans chacune un représentant. Comme F est cohérent, toute couleur d'origine est la couleur libre du représentant plus une constante de parité déterminée. Chaque égalité d'événement devient une relation XOR signée entre représentants. En présence d'une contradiction, choisir dans chaque composante de ce multigraphe un arbre couvrant, puis propager les parités de ces arêtes. Une relation non satisfaite impose, avec le chemin de l'arbre entre ses extrémités, un cycle de XOR total impair. Les boucles et les arêtes parallèles donnent éventuellement un cycle de taille 1 ou 2. Si l'ensemble de quatre relations est minimalement incohérent, ce cycle doit utiliser les quatre relations. Il nécessite par conséquent quatre composantes distinctes de F. Dans le système d'origine, F doit contenir au moins une arête entre états distincts, car sans F les égalités seules admettent la coloration constante. Il faut donc au moins cinq états. Le témoin atteint la borne.

Le balayage exhaustif séparé confirme : 0 noyau sur les 3 requêtes admissibles à trois états, 0/27 à quatre états, 8/244 à cinq états, tous les huit dans la famille C4. Fixer le cycle sur les q premiers états dans son ordre orbital est licite par renommage des états. La preuve est relative aux hypothèses ci-dessus. L'originalité bibliographique n'a pas été examinée.

## Comparaison à budget égal

Référence lexicographique et candidat stable donnant la priorité à un cycle simple de quatre arêtes dans le graphe quotient. Le classement ignore les signes. Chaque requête consomme exactement cinq projections exhaustives, système intact puis les quatre suppressions. Plafond commun de 32 requêtes par famille. Témoin négatif : C4 pur, auquel le candidat donne la priorité mais que l'oracle rejette comme obstruction. Les ordres aléatoires fixes sont évalués séparément sur les mêmes requêtes, avec les graines 0 à 7.

| Mesure | Référence fixe | Priorité quotient |
| --- | ---: | ---: |
| Familles avec découverte sous plafond | 2/9 | 2/9 |
| Requêtes cumulées sur ces deux familles | 8 | 6 |
| Projections cumulées sur ces deux familles | 40 | 30 |
| Requêtes sur les neuf familles | 156 | 154 |
| Temps cumulé, préparation commune et tri inclus | 26,67 ms | 33,11 ms |

Dans chaque famille positive sous plafond, passage de la quatrième à la troisième requête. Les huit ordres aléatoires découvrent les mêmes deux familles et demandent ensemble, par graine, 12, 6, 6, 15, 18, 14, 2 et 6 requêtes sur ces familles. Le candidat égale trois de ces ordres et en perd un. Les absences de détection sous plafond ne donnent pas de borne d'inexistence à six états. Temps ponctuels, sans répétition de chronométrage. Aucun corpus de développement extrait du balayage.

Le seuil de réduction du nombre de requêtes face à l'ordre lexicographique est atteint. Le coût du tri augmente le temps mesuré et le candidat ne domine pas les autres ordres fixes. Conserver le résultat comme preuve d'un gain local en appels, sans remplacer l'ordre de référence. Il s'agit d'une priorité explicite codée pour ce problème.

[Résultats](../code/v19-pivot-results.jsonl) SHA-256 `c65fc2ecb31a502ab0c11cc396fb1db489bb4e4f5b56117425987e31fb7201e6`. Harnais `cbc644b59eda85ee7180f22b839e35a5930912b171e538b90baec2052f4f98d6`. Le garde existant est inchangé et confirme 0 désaccord sur les 2 projections du témoin historique à cinq états et 4 536 projections de la famille C5 réservée. [Log](../code/v19-pivot-guard.txt).

```sh
cd research/code
timeout 30 python audit_v19_pivot.py
timeout 30 python audit_v19_shadow_guard.py
```

Prochain test : comparer une insertion des relations de parité en un seul passage, sans tri global, à une référence fixe qui filtre déjà les cycles sans signe. Réserver de nouvelles familles et mesurer le temps total ainsi que les erreurs de certification.
