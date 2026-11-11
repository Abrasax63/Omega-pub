# OMEGA-ASLIB-001 — audit externe des politiques de sélection de solveur

**Date : 11 novembre 2026. Statut : EMPIRIQUE sur mesures historiques externes et CALCUL REPRODUCTIBLE sur 10 plis officiels. Pas de preuve d'intelligence adaptative supérieure.**

## Protocole scellé avant les scores

- Pré-enregistrement `09_INFRASTRUCTURE_AGENTIQUE/EXPERIMENT_ASLIB_EXTERNAL_PREREG_2026-11-11.md`, commit **`b2c03f48b7acb9c7a33f98978863ec712416ade1`**, antérieur à l'évaluation.
- Source externe `coseal/aslib_data` au commit **`551b22beef8df17de59286b4822ef720e0aa4d6f`** ; scénario `MAXSAT-PMS-2016`. Cinq fichiers téléchargés dans CI et vérifiés par leur empreinte **Git blob SHA**. Aucune copie des données sources rééditée ni relabellisée dans ce dépôt ; données amont sous **GPLv3**, attribution : Bischl et al., « ASlib: A Benchmark Library for Algorithm Selection », *Artificial Intelligence* 2016.
- Le scénario contient **601 instances**, **19 solveurs**, **37 caractéristiques numériques**, **11 419 mesures** de solveurs, dont **6 922 statut ok** et **4 497 timeout**. Le coût enregistré de l'étape de caractéristiques `base` est imputé **entièrement** à toutes les politiques qui utilisent une caractéristique.
- Les 10 plis officiels sont utilisés : 61 instances au pli 1, 60 dans chacun des neuf autres. Modèles ajustés sur les **neuf plis restants uniquement**, jamais sur le pli évalué ; les prédictions sont rejouées sur les résultats historiques, les solveurs ne sont **pas** réexécutés.
- PAR10 : seuil de temps 1 800 secondes, temps de pénalité 18 000. Un échec de solveur reçoit PAR10=18 000. Conformément au protocole, les méthodes avec caractéristiques ajoutent le coût de `base` **même à une pénalité**.

## Résultats confirmés en CI

| Politique | PAR10 moyen + coût de caractéristiques, plus petit meilleur | Instances résolues / 601 | Taux résolu |
|---|---:|---:|---:|
| Meilleur solveur unique entraîné (SBS) | **2231,818** | 529 | 88,02 % |
| KNN-1, 37 caractéristiques | 2377,612 | 523 | 87,02 % |
| KNN-5, 37 caractéristiques | **1784,855** | **543** | 90,35 % |
| KNN-15, 37 caractéristiques | **1782,146** | **543** | 90,35 % |
| KNN-5, 8 premières caractéristiques | 1814,162 | 542 | 90,18 % |
| Omega finite v0, 64 hypothèses représentatives, 8 tests binaires, horizon 3 | **2030,663** | 535 | 89,02 % |
| VBS : meilleur solveur réel **a posteriori** (BORNE NON ADMISSIBLE) | 1383,196 | 556 | 92,51 % |

Le pont expérimental Omega bat le SBS d'environ **9,0 % en moyenne PAR10**, mais il reste **13,9 % plus lent que KNN-15**, et résout **8 instances de moins**. KNN-15 bat SBS d'environ **20,1 %**. VBS est une borne rétrospective obtenue avec les mesures du pli test et **n'est pas une politique réalisable**.

Les statistiques reposent sur les **runtimes mesurés et publiés** pour les solveurs du scénario, et non sur des temps chronométrés pendant ce travail. Les 10 plis partagent beaucoup de cas d'entraînement ; ils ne sont pas 10 expériences indépendantes.

## Double voie de vérification

- **GitHub Actions externe [43065407063](https://github.com/Abrasax63/Omega-pub/actions/runs/43065407063)** : SUCCESS. Pipeline Python `aslib_external_benchmark.py` ; cinq tests unitaires hors réseau ; source verrouillée, calcul des 10 plis et génération d'un **registre par instance**, archivé comme [artefact GitHub Actions](https://github.com/Abrasax63/Omega-pub/actions/runs/43065407063/artifacts/13875032438).
- **CI du dépôt [43065407043](https://github.com/Abrasax63/Omega-pub/actions/runs/43065407043)** : SUCCESS, **183 tests du Prisme** et contrôles RCE/MCP/index.
- **Double calcul supplémentaire [43066025435](https://github.com/Abrasax63/Omega-pub/actions/runs/43066025435)** : SUCCESS. Le script **JavaScript indépendant** `prism/aslib_independent_crosscheck.mjs` recalcule directement sur les mêmes fichiers **SBS, VBS, KNN-1, KNN-5, KNN-15, KNN-5-small** et donne les mêmes moyennes à `1e-5` près, exactement les mêmes nombres résolus.
- **CI du dépôt [43066025446](https://github.com/Abrasax63/Omega-pub/actions/runs/43066025446)** : SUCCESS. Le résultat interne d'`OMEGA_finite_v0` n'a PAS fait l'objet d'une deuxième implémentation indépendante ; il bénéficie de contrôles de programme, de non-fuite et de reproductibilité mais sa comparaison reste moins certifiée que celle des références à double calcul.

Les deux échecs de CI initiaux sont explicitement documentés : (1) une erreur de traitement des guillemets simples dans une fixture ARFF, corrigée sans changer les politiques ; (2) une mauvaise transcription de l'empreinte du fichier officiel `cv.arff`, corrigée après vérification des métadonnées amont. Aucun score réussi antérieur n'a été conservé pour dissimuler ces défauts. Les deux pipelines passent maintenant.

## Conclusions strictes et points de vigilance

- **EMPIRIQUE REPRODUCTIBLE** : sur le benchmark externe choisi et les dix plis publiés, le pont Omega est meilleur que le solveur unique sans caractéristiques, mais est inférieur aux KNN-5/KNN-15 dans les métriques principales.
- **PAS UNE COMPARAISON ARCHITECTURALE PARFAITEMENT ÉQUITABLE** : KNN utilise 37 caractéristiques et toutes les instances de train, alors que le pont Omega se limite volontairement aux huit premières caractéristiques binarisées, 64 hypothèses représentatives et 3 vérifications. Toutes les méthodes paient **le même coût complet** du bloc de caractéristiques lorsque des caractéristiques sont utilisées, mais la **capacité de représentation est différente**. On ne peut pas conclure qu'un Omega mieux adapté ne pourrait pas égaler KNN.
- **OBJECTIF MAL ALIGNÉ** : le planificateur Omega d'origine optimise d'abord un risque **0–1 d'identification du meilleur solveur** sur un modèle fini ; or l'objectif de ce benchmark est le coût PAR10, qui punit sévèrement le choix d'un solveur lent. La littérature d'algorithm selection insiste déjà sur ce décalage. Il ne faut pas revendiquer une nouvelle découverte scientifique sur cette seule observation.
- **LIMITES** : benchmark public, historique (MaxSAT 2016), non aveugle ; CV non nested pour le choix éventuel d'hyperparamètres, mais ici les choix `k=1,5,15` sont pré-fixés ; pas de validation sur plusieurs scénarios/domaine, pas de tests de modèles de langage, pas de provenance indépendante des mesures ASlib, pas de preuve statistique d'un avantage Omega.
- **ÉTAT EPISTÉMIQUE** : `CALCUL EXACT` pour les tests du programme, `EMPIRIQUE REPRODUCTIBLE` pour la comparaison de performances historiques, `INDÉTERMINÉ` pour la supériorité générale ou la capacité de transfert d'Omega.

## Prochain verrou utile — à tester sur UN AUTRE scénario encore non exploité

Une stratégie d'Omega orientée vers le coût réel de ses choix plutôt qu'une erreur 0–1 et capable de choisir **à quelle représentation/sous-ensemble de solveurs faire confiance**. Elle doit se comparer à des baselines fortes de sélection coût-sensible (KNN compétitif, règles et AutoFolio si exécutable), et être figée AVANT la découverte des scores d'un scénario externe différent (par exemple `MAXSAT-WPMS-2016`).

L'ajustement sur ce scénario PMS après avoir observé les scores ne constituerait plus une épreuve aveugle et ne doit pas être revendiqué comme telle. Comparer également l'efficacité des mémoires validées et la résistance à des caractéristiques manquantes et aux changements de distribution. Conserver les échecs et les coûts.

**Ce rapport reste sur la PR brouillon #37, sans fusion dans `main` ni promotion automatique CORE/SQLite.**
