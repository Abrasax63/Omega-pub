# P5-FALSIFY-04 — Pré-enregistrement : preuves imparfaites, coût et mémoire

Date : 2026-11-12. Statut : **PROTOCOLE AVANT CODE / CALCUL**, aucun résultat numérique annoncé.

## Question falsifiable
Omega (mémoire/provenance + filtrage de possibilités) apporte-t-il un gain de décision à budget **réellement égal** face à une politique classique forte ? Ce premier pilote **synthétique** examine une condition nécessaire : un environnement avec vérificateurs imparfaits et coûts distincts où choisir une preuve peut changer la décision. Il ne prouve aucune supériorité d'Omega réel.

## Proposition mathématique et témoin fort
Dans un POMDP fini dont les probabilités, observations, coûts et utilités sont identiques pour les politiques, l'optimiseur Bellman exact maximise la valeur espérée parmi toutes les politiques admissibles. Par définition, aucune politique Omega disposant du même ensemble d'informations/actions ne peut le dépasser en espérance. **Une supériorité contre cet optimum connu serait une erreur de calcul ou un protocole inéquitable.**

Le candidat « Omega-like » est une **heuristique expérimentale distincte des composants Omega P1/P2/P3**. Le comparer à Bellman permet d'éprouver la conception, pas de démontrer l'originalité scientifique.

## Monde fini fixe — aucun choix des paramètres après inspection des résultats
- Variables cachées indépendantes : vérité binaire Y ~ Bernoulli(1/2), régime de fiabilité R ~ Bernoulli(1/2). Le modèle initial M égale Y avec probabilité 2/3. Un indice historique H égale R avec probabilité 3/4. **M et H sont accessibles à toutes les politiques** ; l'indice H est une mesure simulée, pas la véritable mémoire RCE.
- Trois vérificateurs conditionnellement indépendants sachant Y,R et avec réponses binaires : A correct avec probabilité 9/10 si R=0 sinon 11/20 ; B correct avec probabilité 11/20 si R=0 sinon 9/10 ; C correct avec probabilité 4/5 pour les deux régimes.
- Coût de chaque achat (unité d'utilité) : A=B=3/50 (0,06), C=13/100 (0,13). Deux achats au plus, sans répétition d'une même source. Un résultat d'outil révèle uniquement un verdict binaire, jamais Y ou R.
- Sortie : prédire Y=0, prédire Y=1, ou s'abstenir. Utilité terminale : +1 juste, -2 faux, +1/20 abstention, **moins les coûts réellement payés**. Aucun oracle exact offert comme action. Critère de non-décision : on peut toujours s'abstenir.
- Baselines : (i) arrêt sans outil optimisé par Bayes, (ii) ordre fixe A puis C et décision bayésienne de fin de parcours, (iii) politique **Bellman exacte**, prenant en compte Y, R, M, H et les résultats possibles des tests.
- Candidat heuristique (préfixé) : choisir A si H=0, sinon B ; ensuite, si son premier signal s'accorde avec M, s'arrêter ; sinon acheter C. La décision finale maximise l'utilité terminale selon la **vraie croyance conditionnelle calculée**, sans accès aux variables cachées Y,R. Aucun changement des seuils après résultat.
- L'ensemble des politiques dispose des mêmes M,H, loi probabiliste, vérificateurs, horizon et coûts. L'algorithme classique exact a le droit d'utiliser le même H ; il ne faut jamais attribuer à Omega une exclusivité sur cet indice.

## Calcul primaire
Énumération rationnelle exacte (fractions Python) sur les quatre contextes M,H. Bellman horizon 2, espérance pondérée initiale ; politique heuristique évaluée sans simulation, par intégration sur toutes les observations ; vérification indépendante par sommation sur les 4 états (Y,R) pour chaque observation ; vérification obligatoire Bellman ≥ chacune des politiques.

**Critère de succès limité** : si la politique heuristique améliore l'arrêt sans outil, bénéfice de vérification sous cette loi artificielle ; **pas** une innovation Omega. Si elle égale ou dépasse Bellman, vérification de calcul nécessaire (dépassement impossible). Résultat signalé NEGATIVE_SPECIFIC_ADVANTAGE par défaut, sauf nouvelle preuve indépendante ultérieure.

## Prochain test empirique (non exécuté dans ce pilote)
- Corpus nouveau et indépendant de tâches avec sorties d'au moins deux vérificateurs réels faillibles, vérité/audit distinct, coûts de latence et d'appels mesurés, dérive de fiabilité et provenance explicite. Aucun test auto-construit ne doit être présenté comme holdout externe.
- Pré-enregistrer le schéma, les paramètres et les métriques avant le dernier jeu ; séparation calibration/évaluation par source, pas seulement par lignes ; comparateurs : Bayes stationnaire, Bayes décoté, décision active exacte/approchée, ablations Omega sans mémoire/sans observabilité, et Omega entier **réellement exécuté**.
- Budget égal **consommé**, pas seulement plafond nominal. Mesurer utilité appariée, couverture, risque parmi les verdicts, intervalles de confiance par groupe indépendant, taux d'abstention, temps et dépenses. Aucune revendication scientifique si le candidat ne change aucune action ou si les labels sont fournis aux contrôleurs.

## Gouvernance
Aucune clé API ni ressource locale utilisateur requise ; ce pilote ne fait pas d'inférences LLM. Branche expérimentale dérivée de PR #66, sans fusion main, sans promotion CORE. Les nombres synthétiques ici sont des **hypothèses choisies** et non des mesures de performances de fournisseurs réels.
