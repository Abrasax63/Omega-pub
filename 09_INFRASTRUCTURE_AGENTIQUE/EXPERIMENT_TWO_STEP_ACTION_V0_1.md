# Omega — comparaison des stratégies à une et deux étapes (v0.1)

**Statut : EXPÉRIMENTAL — calcul exact sur modèles fictifs.**
Aucun résultat scientifique général, aucun gain réel sur des réponses de modèle,
aucune réduction mesurée de coût ou latence.

## Question et protocole

La PR #22 a mis en évidence un verrou : deux contrôles individuellement
inutiles pour la décision peuvent devenir décisifs ensemble. Ce travail teste
si le fait de considérer **deux contrôles consécutifs** corrige ce défaut.

On compare, sur un même modèle probabiliste fini et un même barème :
- profondeur 1 : meilleure décision ou meilleur contrôle **unique** ;
- profondeur 2 : meilleure décision ou contrôle suivi d'un second contrôle
  **choisi conditionnellement** au résultat observé ;
- un oracle indépendant qui énumère tous les premiers contrôles et tous
  les choix de second contrôle conditionnels, y compris l'arrêt.

Les trois voies reçoivent les **mêmes hypothèses, masses, partitions
d'observations et coûts**. Les coûts en millièmes représentent une pénalité
hypothétique de perte de décision 0/1, pas des euros, secondes ou tokens.

## Fonction objectif

Pour des hypothèses h de poids entiers strictement positifs et une
décision d(h) par hypothèse, l'erreur d'arrêt optimale correspond à
la masse totale moins la masse de la décision majoritaire. À chaque
contrôle, le coût est ajouté sur la branche où le contrôle est effectué.
L'objectif exact minimisé est :

  E[perte finale de décision 0/1] + E[somme des coûts de contrôle].

Le calcul emploie `fractions.Fraction` ; aucun arrondi n'intervient dans
les choix. Un contrôle n'est choisi que s'il améliore **strictement**
l'objectif par rapport à l'arrêt. Les égalités préfèrent l'arrêt puis
l'identifiant lexical du contrôle. Une vérification n'est jamais répétée.

**Portée : horizon maximum de deux contrôles, pas de recherche illimitée.**

## Jeu de validation

`prism/action_planning_challenge.py` contient :
- **24 nouveaux scénarios publics** : 4 catégories (mathématiques,
  documentation, calcul, exploration) × 6 constructions de décision.
  Ils couvrent une synergie à deux contrôles, des secondes actions
  différentes par branche, un contrôle directement utile, une absence de
  gain, une décision déjà déterminée, une synergie trop coûteuse ;
- **96 scénarios synthétiques reproductibles**, générés avec une graine
  fixe, en faisant varier décisions, poids, observations, coûts et
  disponibilités des contrôles.

Ce sont des scénarios nouveaux **par rapport aux 24 cas de la PR #22**,
mais ils ont été conçus et implémentés pendant la même expérience.
Ils ne constituent ni un holdout secret ni une validation externe.
Les catégories nommées ne changent pas l'algorithme de décision.

`exhaustive_policy_reference` calcule toutes les politiques à deux
étapes par produits cartésiens des seconds contrôles possibles pour chaque
observation du premier. Il ne réutilise pas la programmation dynamique
du planificateur. La concordance compare l'objectif exact et le choix
de première action ; des tests spécifiques contrôlent les branches.

## Cas discriminants

- **Synergie :** quatre hypothèses A,A,B,B. Les contrôles
  `xyxy` et `xyyx` ont chacun un gain de décision immédiat nul,
  mais leur paire identifie la décision. La planification à une étape
  s'abstient, celle à deux étapes peut agir.
- **Choix conditionnel :** six hypothèses, un premier test `xxxyyy`.
  Dans chaque branche, un second contrôle **différent** élimine
  l'incertitude. Une liste d'actions fixe ne suffit pas à décrire
  la politique optimale.
- **Abstention justifiée :** si deux tests complémentaires coûtent
  plus que le risque de décision initial, même la profondeur 2 s'abstient.
- **Invariance :** inverser l'ordre des hypothèses ou contrôles ne doit
  modifier ni l'objectif ni l'arbre de décision, à conventions égales.

## Exécution

Depuis `09_INFRASTRUCTURE_AGENTIQUE/prism` :

```sh
python -m unittest -v test_action_planning_two_step
python action_planning_challenge.py
```

Le workflow RCE existant lance également `python -m unittest -v`.
Consulter les logs GitHub Actions avant de revendiquer une exécution réussie.

Le connecteur `plan_with_two_step_evidence` ne change pas Omega P1.
Il lui fournit seulement le contexte de la **première** action et restitue
la politique conditionnelle comme objet distinct. Rien n'est exécuté,
aucun modèle n'est appelé, aucune mémoire scientifique n'est modifiée.

## Risques et limites

- La valeur attendue est exacte **conditionnellement au modèle fourni**.
  Aucune vérification de la fiabilité du modèle ou du coût n'est effectuée.
- Les observations sont supposées déterministes par hypothèse ; aucun
  bruit de mesure, corrélation externe, apprentissage des priors ou
  acquisition réelle de données.
- Profondeur 2 : on peut construire une synergie de profondeur 3,
  donc l'optimalité au-delà de deux tests n'est pas acquise.
- Comparer des objectifs optimisés sur des données synthétiques ne prouve
  pas que les réponses d'Omega sont meilleures dans la réalité.
- Un vrai essai exige de geler avant toute utilisation un ensemble
  indépendant de problèmes et un barème de décisions finales, puis de
  mesurer A (direct), B (prisme fixe) et C (politique adaptative) à
  budget équivalent avec notation aveugle et coûts réels.

Aucune fusion vers `main`, aucune certification RAVI-2 et aucune
dépendance externe de calcul.
