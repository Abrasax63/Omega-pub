# OMEGA-EXACT-ORACLE-05 — référence optimale certifiable sur banc fini

La [PR #160](https://github.com/Abrasax63/Omega-pub/pull/160) a comparé des variantes apprenantes à la référence déterministe PRICE_AWARE, sans savoir si cette référence était proche du minimum possible. Ce pilote ajoute **un solveur exact de la politique d'identification à coût moyen minimal** pour seize machines candidates équiprobables et 64 questions donnant un bit binaire chacune.

Le [préenregistrement](PREREG_2026-11-17.md) a été enregistré avant le code au commit `dc02ab735e314b106868faa49b284fb4e77e4b9b`. Le code ne retouche pas les résultats précédents.

## Ce que calcule l'optimum

Pour un ensemble S de n modèles possibles, et une question de prix c qui produit deux réponses pouvant séparer S en S0 et S1 :

```
F(S) = min_q [ n*c(q) + F(S0) + F(S1) ]
F({un seul modèle}) = 0
E[coût optimal | S] = F(S) / n
```

L'identification est **exacte pour l'hypothèse de distribution uniforme** sur les 16 candidats de ce problème, avec sondes réinitialisées, tarif synthétique et menu figé. C'est une minimisation de coût total de requêtes, pas une prédiction des paramètres cachés du monde avant de l'interroger. Le nom `OPTIMUM` n'implique aucune borne théorique sur le raisonnement mathématique général.

La recherche utilise des ensembles en masques binaires, mémorisation, groupement de partitions identiques, et élagage via une borne inférieure valide de longueurs de codes binaires. Tous les chemins de décision sont rejoués **sur les 16 machines possibles**, et la somme de leurs coûts est comparée au numérateur de Bellman. Les tests de 2–5 hypothèses utilisent un second algorithme exhaustif **sans élagage**.

## Banc réservé

**Le nouveau pool prévu de 32 modèles n'a pas pu être constitué.** Le run de précontrôles [#44158601275](https://github.com/Abrasax63/Omega-pub/actions/runs/44158601275) a rendu `INSUFFICIENT_NEW_MODELS` avec les exclusions préenregistrées. Le holdout inédit est donc **bloqué, sans score**. L'[avenant rétrospectif](POSTHOC_SCOPE_AFTER_EXHAUSTION_2026-11-17.md) `10b302ab` a été signé après constat du blocage. Il autorise seulement le **recalcul sur les 24 ensembles déjà exposés de la PR #160**. Cette étude rétrospective n'est ni un nouveau test aveugle ni une validation indépendante de gain. Dans chaque ensemble et sous chaque tarif public, OPTIMUM, PRICE_AWARE et BALANCED sont évalués **sur les 16 mondes**, pas seulement sur un seul monde échantillonné. Le coût moyen uniforme, les écarts et les profondeurs des arbres sont publiés.

Le seuil prospectif `HEADROOM_FOR_IMPROVEMENT` reste gelé mais **n'est pas applicable aux cas historiques déjà exposés**. La version rétrospective publie des moyennes et écarts descriptifs tout en conservant le statut `RETROSPECTIVE_ONLY_NO_FRESH_HOLDOUT`, quel que soit le score. Cela ne démontre pas la supériorité d'un apprentissage. Le plafond précédent de 12 sondes est séparé : si un arbre exige plus, le calcul illimité n'est pas qualifié comme optimum à horizon 12.

## Reproduction

Bibliothèque standard Python 3.11, sans API payante :

```bash
python -m unittest discover -s experiments/omega-exact-oracle-05 -p 'test_exact_oracle.py' -v
python experiments/omega-exact-oracle-05/exact_oracle.py --mode retrospective --output evidence/report.json
sha256sum evidence/report.json
```

Le workflow `push` exécute uniquement les tests de cohérence, sans évaluer les scores. Le workflow `pull_request` lance une fois l'évaluation exhaustive **post hoc sur le jeu #160 déjà exposé** et un audit indépendant des sorties de sondes, des chemins, prix, certificats et agrégats. Aucun résultat ne sera qualifié de prospectif. En cas de limite de ressources, refuser un énoncé d'optimalité.

**Limites :** distribution uniforme hypothétique, 64 questions disponibles, prix synthétiques, groupes finis, CPU non pris en compte, une seule cohorte. Aucune auto-amélioration de LLM démontrée, aucune preuve mathématique nouvelle produite. Conserver PR DRAFT, pas de fusion, `main` et CORE inchangés.
