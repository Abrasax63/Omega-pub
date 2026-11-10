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

## Résultats et contre-tests après exécution CI

L'exécution [42912451824](https://github.com/Abrasax63/Omega-pub/actions/runs/42912451824)
a réussi : 81 tests du Prisme, ainsi que les tests RCE/MCP et les smoke tests.

Résultats **exacts dans ces modèles fictifs** :

- 24 nouveaux scénarios construits : profondeur 2 strictement meilleure
  dans 8 cas ; égalité dans 16 cas ;
- 96 scénarios synthétiques à graine fixe : profondeur 2 strictement
  meilleure dans 34 cas ; égalité dans 62 cas ;
- 120/120 concordances avec la recherche exhaustive indépendante ;
- aucune mesure de qualité réelle, aucun appel de modèle externe.

Le fait qu'une profondeur 2 optimisée ne soit jamais inférieure à
une profondeur 1 est garanti **dans le modèle** : toutes les politiques
de profondeur 1 restent réalisables à profondeur 2. Ce n'est pas une
preuve de fiabilité des hypothèses, ni un effet expérimental généralisable.

### Nouvelles falsifications adversariales

**Modèle d'observations erroné.** Dans le cas de synergie à quatre hypothèses
A,A,B,B, le modèle annonce deux contrôles complémentaires avec coût 0,01
chacun : perte prévue 0,02. Si, en réalité, le second contrôle duplique le
premier, les deux résultats restent inutiles pour trancher : même avec
une décision réoptimisée à posteriori sur les vraies observations, le
risque de classification vaut 0,5 et les deux coûts sont payés.
Perte réelle minimale 0,52, **supérieure à l'abstention immédiate 0,5**.
Ce contre-exemple démontre que l'optimisation n'est pas robuste à
une fausse modélisation de la valeur informative des contrôles.

**Synergie de longueur trois.** Sur huit hypothèses équiprobables de
trois bits, la décision est leur parité. Un ou deux tests qui révèlent
des bits laissent la décision parfaitement indéterminée. Les trois bits
ensemble la déterminent. La stratégie de profondeur 2 s'abstient donc
malgré une stratégie informative à trois tests de coût très faible.
Ce contre-exemple montre que **deux étapes ne sont pas suffisantes en
général**.

Ces deux contre-tests ont été intégrés au module de tests : ils ne sont
pas inclus dans les 120 scénarios du tableau comparatif et ne doivent
pas être comptés comme des gains supplémentaires.

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
