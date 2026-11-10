# Calibration publique P5 — décision de prochaine action, v0.1

**Statut : EXPÉRIMENTAL / calcul exact sur modèles synthétiques.**
Aucune donnée scientifique réelle, aucun holdout privé, aucun appel à un
modèle externe et aucune preuve de gain général d'Omega.

## Question falsifiable

Sur un **modèle fini fourni** (hypothèses pondérées, décisions associées,
observations possibles et coûts des vérifications), Omega choisit-il l'action
qui maximise la réduction attendue du risque de mauvaise décision, nette
du coût ? Le prototype est dans `prism/action_selection.py` ; il **réutilise
le planificateur P1** via `plan_with_evidence`, sans changer ses règles.

Il ne remplace pas le jugement sur la fiabilité des hypothèses, les poids,
les observations ni les coûts, qui sont fournis par l'appelant.

## Méthode et convention

Pour un ensemble d'hypothèses H, de poids entiers strictement positifs w(h),
et d'une décision d(h) par hypothèse :

- risque actuel = 1 - max_d P(d) (perte de classification 0/1) ;
- un contrôle c partitionne les hypothèses par observation annoncée ;
- risque après c = somme sur observations o de P(o) [1 - max_d P(d|o)] ;
- gain net(c) = risque actuel - risque après c - coût(c)/1000.

L'algorithme utilise les fractions exactes, choisit le contrôle disponible
avec gain net strictement positif maximal, et départage les égalités par
identifiant lexical. Si toutes les hypothèses conduisent à la même décision,
il propose `answer`. Si aucune action disponible n'a de gain net positif,
il renvoie `insufficient_evidence`. Le cas contraire propose `verify` ou
`ask` avec la prochaine étape explicite.

**Les coûts sont des pénalités fictives exprimées en millièmes de perte 0/1,
et non des coûts mesurés en temps, tokens ou euros.** Les partitions
d'observations sont également hypothétiques. L'algorithme est à horizon
d'une étape ; il peut échouer lorsqu'une suite de deux tests serait utile
mais qu'aucun test seul n'apporte de gain, ou si les probabilités sont fausses.

## Jeu public de 24 cas

`prism/action_selection_benchmark.py` génère 4 domaines (mathématiques,
documentation, calcul et exploration), croisés avec 6 structures :
décision déjà certaine, vérification bon marché, clarification seulement,
contrôle non informatif, vérification distrayante et arbitrage coût/gain.

Les 24 modèles sont **synthétiques et visibles dans le code**. Ils ne doivent
pas être qualifiés de test aveugle, de jeu de généralisation ni d'un résultat
expérimental sur des réponses de modèles.

Une seconde voie de calcul énumère les observations et la décision bayésienne
optimale sous chacune ; elle vérifie le résultat de l'implémentation. Le
contrôle de comparaison `first_positive` choisit le premier test disponible
de gain positif sans optimiser entre tests ; il dispose donc des mêmes modèles
et du même critère de risque, mais pas du choix global du meilleur test.

## Exécution reproductible

Depuis `09_INFRASTRUCTURE_AGENTIQUE/prism` :

```sh
python -m unittest -v test_action_selection
python action_selection_benchmark.py
```

Résultats attendus **si les tests passent** :

- concordance avec la seconde voie exacte : 24/24 ;
- contrôle `first_positive` : 20/24 ;
- sélection : 4 `answer`, 4 `verify`, 12 `ask`,
  4 `insufficient_evidence` ;
- tests de perturbation : suppression de vérification, suppression de
  clarification, résolution d'incertitude, permutation des états et actions,
  rejet de neuf catégories d'entrées malformées.

Ces résultats n'établissent **aucun gain sur des problèmes réels** :
l'optimisation est définie par le même modèle qui sert à évaluer le résultat.
Les scénarios sont construits pour couvrir les décisions et la comparaison
avec le contrôle ; il ne s'agit pas d'une fréquence observée dans la nature.

## Étape réellement discriminante suivante

1. Geler avant collecte 24 nouveaux problèmes **indépendants**, avec
   données d'évidence, coûts et critères de correction élaborés séparément.
2. Comparer, sous mêmes informations et budget, réponse directe A, routage
   fixe B, et choix d'action optimisé C ; distinguer une bonne décision d'un
   bon simple intitulé d'action.
3. Évaluer la vérité des éléments vérifiés, la décision finale, le taux
   d'abstention justifiée, le temps et le coût réels. Produire les rapports
   d'échecs, cas contraires et contre-exemples ; ne pas donner un gain
   scientifique sur la seule base des 24 cas synthétiques.

Aucune écriture dans les espaces de mémoire scientifique, aucune
certification RAVI-2, aucune modification de `main`.
