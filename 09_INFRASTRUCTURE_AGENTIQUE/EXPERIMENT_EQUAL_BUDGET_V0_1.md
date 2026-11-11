# Omega — comparaison à budget égal contre un plan fixe optimal

11 novembre 2026. Statut : EXPÉRIMENTAL / calcul exact sur tableaux artificiels publics. Aucun appel de modèle, aucun problème scientifique inédit résolu automatiquement, aucun vrai outil documentaire consulté.

## Question falsifiable
Avec les mêmes hypothèses, observations déterministes disponibles, distribution a priori uniforme et un plafond dur de deux tests binaires par hypothèse cachée, la politique conditionnelle implémentée dans Omega (optimize_policy) identifie-t-elle davantage d'hypothèses que la meilleure paire fixe possible ? Le plan fixe est obtenu par énumération de toutes les paires, pas par une heuristique volontairement faible.

Comparaison de trois bras :
- A : décision directe sans observation (une identification exacte possible par problème, puisqu'un label unique est associé à chaque hypothèse).
- B : meilleure paire fixe de tests, choisie globalement avant toute observation.
- C : moteur Omega sur deux contrôles au maximum, avec second contrôle conditionnel et arrêt anticipé autorisé.

Toutes les hypothèses ont un poids 1, les observations sont sans bruit, et le coût fictif est fixé à zéro. Le score est le nombre de décisions exactes si chaque état caché est joué une fois. Un bras ne dépasse jamais deux tests par état. Le bras C peut utiliser moins de tests. Les coûts réels ne sont pas mesurés : l'équivalence porte sur le plafond de contrôles, pas sur la latence ou les euros.

## Matériel gelé et traçable
Le programme prism/equal_budget_pilot.py génère 260 tableaux reproductibles avec la graine 20261111. Empreinte SHA-256 attendue :

6b7e3f2c7392c61206d7ad86ea86e5a2ad738f94a5e4a4678ea03452da6f2faa

Deux strates séparées :
1. 200 tableaux aléatoires de 5 à 9 hypothèses et 3 à 6 contrôles, avec variation du nombre de candidats et des signatures d'observation.
2. 60 tableaux artificiellement construits pour rendre profitable un second choix conditionnel différent selon la première observation. Cette strate n'est pas une estimation de la fréquence naturelle d'un tel mécanisme.

Un oracle indépendant du planificateur énumère les premiers contrôles et les seconds tests par branche. Pour chaque état caché, le programme déroule effectivement la politique d'Omega sur les observations exactes, mesure les bonnes décisions et le nombre de tests, et vérifie l'accord avec l'oracle ainsi qu'avec le risque annoncé par Omega.

## Comptes attendus du jeu gelé (soumis à la CI)

| Strate | États cachés déroulés | Direct | Meilleur plan fixe | Omega conditionnel | Cas avec gain |
|---|---:|---:|---:|---:|---:|
| 200 aléatoires | 1391 | 200 | 777 | 793 | 16/200 |
| 60 complémentaires construites | 360 | 60 | 180 | 240 | 60/60 |

Taux de bonne identification par état caché :
- Aléatoire : fixe 777/1391 ≈ 55,86 %, Omega 793/1391 ≈ 57,01 %, écart +16 bonnes identifications soit +1,15 point. Les 1391 états ne constituent pas 1391 observations statistiquement indépendantes : les 200 tableaux sont les unités d'analyse.
- Construit : fixe 180/360 = 50 %, Omega 240/360 = 66,67 %, écart +60 soit +16,67 points.

Le gain provient du droit de choisir un second contrôle différent après observation. Les cas ne testent pas la recherche de preuves, l'authenticité, la justesse des priors ou la qualité des réponses de modèles. Dans un modèle exact, une politique conditionnelle qui contient tous les plans fixes ne peut obtenir un meilleur risque moins bon que celui du meilleur plan fixe ; ce n'est pas une conclusion sur le monde réel.

## Reproduction
Depuis 09_INFRASTRUCTURE_AGENTIQUE/prism, exécuter :
- python -m unittest -v test_equal_budget_pilot
- python equal_budget_pilot.py

La suite fige les 260 tableaux par hash, vérifie les 260 concordances entre l'oracle et Omega, les comptes par strate et la limite de deux contrôles. Le workflow RCE existant lance les tests unitaires du Prisme.

## Verrou avant toute conclusion de gain stratégique réel
Exécuter une expérience P5 à information initiale identique sur des tâches externes indépendantes : réponses du même modèle et snapshot dans les bras A (direct), B (routage fixe), C (adaptation), accès à des outils effectifs et coûts/latences mesurés ; corrections indépendantes aveugles ; sources trompeuses, transfert sur des cas inédits et contrôles négatifs sans gain.

Cette PR ne réalise pas cette campagne, ne lance aucun modèle externe et ne démontre aucune supériorité générale d'Omega. PR empilée sur #25, aucune fusion ni modification de main, pas d'ajout dans CORE.
