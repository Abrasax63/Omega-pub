# OMEGA-COVER-CONSTRAINED-04 — budget réellement limitant

[**Préenregistrement avant code et mesures**](https://github.com/Abrasax63/Omega-pub/commit/ae6a29814d8678e969c903cbc013ae895a80bfe5).

La [PR #138](https://github.com/Abrasax63/Omega-pub/pull/138) a fait réussir les quatre méthodes d'équivalence AALpy L* sur ses douze machines à 900 et 1800 symboles par bras, **mais aucune méthode n'a atteint 900**. Le choix des nouveaux seuils **300 et 500** est donc **postérieur aux résultats de #138**, mais ce pilote utilise un **nouveau holdout totalement inédit** pour ne pas réutiliser ses machines pour des conclusions nouvelles.

Aucun changement de la logique des méthodes de #138 : RANDOM_LEN10, FIXED_LEN10, OLD_OMEGA_LEN10, COVER_DISTINGUISH_LEN10 ; EQ longueur **10 exactement**, AALpy 1.6.2, même gestion fail-closed de budget. Le seul changement est un **jeu de douze nouvelles machines**, quatre de chaque taille 4/5/6, générées seed **37104/37105/37106**, entièrement accessibles et comportementalement minimales. Déduplication canonique contre **1 136 signatures historiques**, dont les douze machines déjà vues de #138. Les nouveaux jeux sont distincts entre eux.

Le vrai automate est caché pendant l'apprentissage et accessible au **seul évaluateur indépendant**. Chaque query et son coût réel sont journalisés ; l'oracle exact produit une équivalence comportementale par BFS du produit après la reconstruction, ou un contre-exemple. Les 128 mots réservés par machine (seed `970000+100*n+j`, longueur 12–20) sont exclus de l'entraînement.

**Critère préenregistré** à 500 symboles : la nouvelle méthode COVER doit reconstruire **strictement plus d'automates exactement équivalents que chacun des trois comparateurs**, sans détériorer la précision moyenne des mots réservés. Sinon `NO_DEMONSTRATED_CONSTRAINED_GAIN`. Le plafond 300 reste secondaire. Même graine par méthode à travers les budgets. Si tous les plafonds sont encore non contraignants, le protocole le dira sans prétendre améliorer Omega.

Exécution :
```sh
python -m pip install aalpy==1.6.2
python -m unittest discover -s experiments/omega-cover-constrained-04 -p test_constrained.py -v
python experiments/omega-cover-constrained-04/constrained_lab.py --output /tmp/omega-constrained-04.json
```

La CI exécute 8 tests techniques et 96 vrais apprentissages, conserve les journaux bruts, coûts, sorties, contre-exemples, scores et empreintes SHA256 même en cas de résultat négatif. Python 3.11, aucune API payante, pas de LLM ni nouvelle autonomie agentique. PR DRAFT empilée sur #138, `main` inchangée.
