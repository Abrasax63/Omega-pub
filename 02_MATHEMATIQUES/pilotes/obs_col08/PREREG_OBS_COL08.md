# OBS-COL-08 — Pré-enregistrement des sondes adaptatives à budget égal
15 novembre 2026 — ENGAGEMENT avant code, résultats et choix de mondes observés.

## Hypothèse réfutable
La première version Omega ayant un **choix effectif des expériences** via la politique PR #23 et le pont P1, peut-elle obtenir des prédictions hors échantillon avec moins de consultations qu'une politique passive, **sans battre artificiellement** une baseline exacte classique qui optimise le même objectif ?

## Univers expérimental et distribution
- Automates de Moore déterministes, alphabet `p,r`, sortie binaire, reset q=0.
- Un catalogue **de 40 modèles distincts sur les mots <=7** sera généré par `random.Random(20261115)`, 2 à 4 états et transitions/sorties tirées par cette graine ; éliminer les modèles sans sortie 0 et 1 et les doublons de signatures observables. Méthode de génération elle-même connue et non apprise.
- Cibles fixées par leurs **indices** dans ce catalogue avant calcul : 0, 3, 7, 12, 19, 27, 35, 39. Contrôle hors catalogue : DELAY9_OOD de la PR #91.
- Le module de choix ne recevra jamais l'indice de la cible, le graphe du vrai modèle ni les mots réservés à l'évaluation. Les identifiants P1 sont neutres.
- Six sondes au maximum et **18 symboles d'action cumulés au maximum** par politique et cible, même règle de facturation pour tout le monde (une requête = un mot ; coût en symboles = longueur du mot). Les données de l'évaluateur sont exclues de l'apprentissage.
- Ensemble de sondes candidates = tous les mots non vides sur p,r de longueur <=6. À chaque étape, présélection déterministe jusqu'à huit mots classés par gain de réduction de risque d'identification dans le catalogue de modèles survivants, puis longueur et ordre lexical ; inclure diversité de longueur si possible. Le catalogue et cette présélection sont fournis à toutes les stratégies : ce sont **des hypothèses stipulées**, pas des découvertes par Omega.
- Sortie lorsque le budget est épuisé : modèle de tête lexicographique parmi les survivants, mais noter l'incertitude et **interdire les certificats universels**. Si aucun candidat ne survit, alerte hors catalogue.
- Évaluation strictement différée : les 1 792 mots de longueur 8..10 pour chaque cible, réponses provenant du générateur uniquement après arrêt des décisions.

## Bras et comparaisons
A : **Omega P1/PR23** `plan_with_variable_horizon` à profondeur 2 sur les huit sondes présélectionnées, avec coût `5 × longueur` milli et plafond séquentiel 18 symboles/6 consultations ; P1 doit enregistrer le mot réellement choisi.
B : **classique fort** même optimisation PR23 sans P1, et contrôle indépendant exact en énumération de deux tests. Mesurer l'égalité A/B et ne pas compter le code PR23 comme une création d'Omega.
C : **greedy information/cost** choix de gain d'erreur de Bayes à une étape parmi les huit mêmes sondes, sous le même budget.
D : **ordre lexical** choix du premier mot disponible parmi les mêmes sondes, sous le même budget.
Des baselines TTT/L# sont des **références de l'état de l'art**, pas implémentées dans ce pilote. Aucun qualificatif « meilleure méthode classique » pour B hors des huit sondes et du coût déclaré.

## Statuts, métriques, conditions d'échec
- Toutes les politiques reçoivent les mêmes modèles, mêmes fonctions d'observation et mêmes ressources.
- Mesurer : consultations, nombre total de symboles, nombre de candidats restants, exactitude sur 1 792 mots réservés, abstentions, faux certificats (=0 requis), avis P1, accords avec optimiseur classique et son oracle indépendant.
- Vérifier que tout candidat retenu a réellement produit toutes les observations de l'entraînement ; aucun résultat réservé dans la politique.
- Conditions d'échec : cible connue éliminée, identifiant caché transmis à P1, coût/budget inégal entre les bras, prélèvement anticipé de vérité sur les mots réservés, simulation de P1 par un faux objet, affirmation de gain contre un comparateur plus fort que celui exécuté.
- Cas OOD : si l'environnement ne peut pas être distingué d'un modèle du catalogue avec le budget permis, signaler **INDÉTERMINÉ** ; une erreur réservée doit devenir un avertissement, non un certificat.
- Succès technique : CI, tests de budget/anti-fuite/provenance; écart éventuel C/D documenté, A=B conforme au modèle PR23. Résultat scientifique : même si A surpasse C/D, **aucun avantage propre à Omega sur la baseline B** ; aucune généralisation à des systèmes naturels/agents autonomes.

Références méthodologiques : Angluin 1987 (L*), Isberner et Steffen 2014 (analyse de contre-exemples), Vaandrager et al. 2022 (L#), méthodes TTT. Distinguer « auteur classique » de « intégration Omega ».
Gouvernance : PR en DRAFT basée sur #91, sans fusion, sans écriture directe sur `main` ni promotion CORE.
