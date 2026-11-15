# OBS-COL-07 — Synthèse active d'automates à états cachés, sans catalogue de modèles

**Date :** 2026-11-15.
**Statut :** CALCUL EXACT, expérimental synthétique ; PAS de découverte de loi naturelle ni de gain propre à Omega démontré.
**Branche :** experiment/obs-col07-active-automaton-synthesis-2026-11-15
**Base :** PR #90 (ne modifie ni \`main\`, ni CORE, ni mémoire certifiée).
**Pré-enregistrement avant code :** [PREREG_OBS_COL07.md](PREREG_OBS_COL07.md), commit \`be19e777f76b77ba3cb464b9a8ed12ce9fa81de4\`.

## Objectif

Contrairement à OBS-COL-06 qui sélectionnait parmi cinq modèles fixés,
l'apprenant ne reçoit ici **ni les identités des familles, ni le nombre
d'états cachés**. Il observe seulement la réponse binaire aux mots d'actions
\`p\` et \`r\`, chaque essai repartant d'un reset du simulateur.

Il construit un automate à états résiduels via une table d'observation
**fermée et cohérente** (algorithme classique proche de L*), enrichie
à partir de contre-exemples mesurés.

**Référence scientifique fondamentale :** Dana Angluin, « Learning regular
sets from queries and counterexamples », *Information and Computation*,
75(2), 87–106 (1987), DOI
[10.1016/0890-5401(87)90052-6](https://doi.org/10.1016/0890-5401(87)90052-6).

Attention : L* classique suppose un oracle d'équivalence capable de
certifier les hypothèses ou fournir des contre-exemples. **Notre code
remplace cet oracle par une recherche exhaustive de mots seulement jusqu'à
la longueur 7.** Il ne peut donc pas certifier la correction générale.

## Protocole, contrôles et absence de fuite

Six dynamiques déterministes à états cachés sont générées par le laboratoire
(les règles sont publiques pour audit, donc pas un holdout véritablement
aveugle). L'apprenant n'accède qu'à une interface \`membership(word)\` ;
le simulateur interdit les histoires longues de 8 à 10 actions pendant
l'entraînement. Aucune identité de monde, dimension ou table de transition
n'est transmise à \`BoundedLStar\` ou à Omega P1.

Une **variante Omega** appelle le véritable \`planner.plan_mission\` issu
de la base de PR #90 pour autoriser chaque nouveau mot interrogé.
Ce P1 n'a **ni choisi les mots, ni synthétisé les états** : toutes les
décisions algorithmiques appartiennent au moteur classique \`BoundedLStar\`
introduit dans ce pilote.

Une **baseline classique forte** réexécute ce même moteur sans P1, sur
un oracle de même monde et au même quota de consultations. Le programme
affirme et vérifie une identité **octet de modèle / ordre de requêtes**.
Un raffinement de partitions indépendant sur le générateur calcule,
uniquement **post hoc**, le nombre d'états minimal réel pour les contrôles.
Ces nombres ne sont pas communiqués à l'apprenant.

Toutes les histoires de longueurs 8,9,10 sont réservées à l'évaluation :
\`2^8+2^9+2^10=1792\` trajectoires par monde. Aucune de ces réponses ne
participe à la sélection ou à l'apprentissage. Les données demeurent
néanmoins synthétiques et issues du même simulateur.

## Exécution et résultats primaires

**[GitHub Actions #43721571099 — SUCCESS](https://github.com/Abrasax63/Omega-pub/actions/runs/43721571099)**,
Python 3.11, **10/10 tests réussis** et
[archive des sorties JSON](https://github.com/Abrasax63/Omega-pub/actions/runs/43721571099/artifacts/14164223090).

| Monde (vérité post hoc) | États inférés | États minimaux réels | Requêtes uniques | P1 réel | Erreurs sur 1792 prédictions |
|---|---:|---:|---:|---:|---:|
| TOGGLE2 | 2 | 2 | 255 | 255 | 0 |
| CYCLE3 | 3 | 3 | 255 | 255 | 0 |
| CYCLE4 | 4 | 4 | 255 | 255 | 0 |
| SET2 | 2 | 2 | 255 | 255 | 0 |
| MIX3 | 3 | 3 | 255 | 255 | 0 |
| DELAY9_OOD | 1 provisoire | 9 | 255 | 255 | 67 |

**Total : 1530 consultations du simulateur pour l'apprenant, 1530 appels
au module réel P1, 1530 consultations comparables pour la baseline
classique**, plus les consultations de l'évaluateur après apprentissage.
La réponse au mot vide est mesurée lors du contrôle de l'apprenant,
mais ne figure pas dans les 255 demandes de requêtes effectivement
nécessaires dans cette implémentation.

Pour CYCLE3, CYCLE4 et MIX3, une contradiction détectée au mot \`ppp\`
entraîne un raffinement de la table, et la représentation gagne des
états. Pour DELAY9_OOD, toutes les observations jusqu'à 7 actions
donnent zéro : l'apprenant ne distingue donc pas cette machine d'une
machine constante à un état. Un premier contre-exemple de longueur
8 apparaît dans les données réservées, puis 67 erreurs sur les 1792
histoires réservées : statut **OUT_OF_HORIZON_WARNING**.

**Important :** constater 0 erreur sur les 1792 tests réservés pour un
modèle n'établit toujours pas son équivalence universelle. Cette
équivalence est vraie pour les cinq générateurs du pilote selon le
contrôle structurel post hoc, mais elle n'a pas été démontrée à partir
des seules observations de l'apprenant.

## Verdict et limite cruciale

La nouveauté **fonctionnelle dans notre pile Omega** est de produire
des états résiduels sans fournir préalablement une liste de familles ni
une dimension cachée. La nouveauté **mathématique** est NULLE : cette
méthode appartient à l'apprentissage actif classique d'automates.

**Gain spécifique à Omega : NUL sur ce pilote.** Les modèles
construits, requêtes et prédictions sont strictement identiques à ceux
du comparateur classique ; P1 apporte seulement un plan explicable
par consultation et un coût de calcul supplémentaire, non mesuré ici.

Règles, simulateur, horizon, alphabet, algorithme d'apprentissage
et évaluateur ont été élaborés par nous. Aucun cas naturel, aucun
holdout réellement indépendant, aucun modèle externe, aucun
agent autonome ni nouveau théorème scientifique certifié.

## Reproduction

~~~sh
python -m unittest discover -s 02_MATHEMATIQUES/pilotes/obs_col07 -p 'test_obs_col07.py' -v
python 02_MATHEMATIQUES/pilotes/obs_col07/obs_col07.py > obs_col07_result.json
~~~

## Prochain verrou

La sélection des mots aujourd'hui est guidée par L*, pas Omega. Nous
devons vérifier si une couche Omega qui réutilise mémoire, observabilité
et hypothèses concurrentes sait **proposer de meilleures expériences**
avec un budget strict, face à un apprenant classique solide ayant accès
aux mêmes requêtes. Sur des systèmes issus d'un générateur externe ou
d'un jeu réel, fournir les contre-exemples seulement après engagement
de la méthode. La première réfutation doit conserver son statut
jusqu'à correction vérifiée, sans promotion automatique.
