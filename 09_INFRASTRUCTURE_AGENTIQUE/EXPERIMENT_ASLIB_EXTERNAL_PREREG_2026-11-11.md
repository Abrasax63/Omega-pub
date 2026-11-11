# OMEGA-ASLIB-001 — Pré-enregistrement sur mesures externes de solveurs

Date 2026-11-11. **Statut : audit et comparaison externe historique, non prospectif.** Aucun score n'a été calculé avant le présent gel. Branche expérimentale fondée sur PR #36.

## Pourquoi cette expérience
Les résultats STRAT-001..004 proviennent pour l'essentiel d'exemples construits. La sélection d'algorithmes est une discipline préexistante, étudiée notamment dans Hydra (Xu et al., AAAI 2010) et ASlib (Bischl et al., Artificial Intelligence, 2016). Il faut vérifier Omega face à des scénarios externes comprenant des *mesures réelles* de solveurs et des partitions de validation publiées.

## Données primaires et provenance immuable
ASlib, dépôt `coseal/aslib_data`, commit figé **`551b22beef8df17de59286b4822ef720e0aa4d6f`**, répertoire `MAXSAT-PMS-2016/`.
- `algorithm_runs.arff` : PAR10 et statut de chaque solveur, arrêt fixé à **1800 secondes** ; temps pénalisé timeout = **18000**.
- `feature_values.arff` : 37 caractéristiques numériques par instance.
- `feature_costs.arff` : coût mesuré de l'unique étape `base`, commune aux 37 caractéristiques. Il est **interdit** de présenter les caractéristiques comme 37 requêtes indépendantes à coût séparé.
- `cv.arff` : pli 1..10 établi par le fournisseur du benchmark, à respecter.
- `description.txt` : métadonnées et définition de performance.

Sources : https://github.com/coseal/aslib_data/tree/551b22beef8df17de59286b4822ef720e0aa4d6f/MAXSAT-PMS-2016 et https://github.com/coseal/aslib-spec/blob/master/format.md. Attribution et licence des données : `coseal/aslib_data` **GPLv3**. Ne pas copier les fichiers de données sous une nouvelle licence dans Omega ; fournir du code de lecture des fichiers upstream verrouillés.

## Population, erreurs, imputations
Évaluer **toutes les instances présentant** une ligne de caractéristiques, un pli de validation officiel, au moins une mesure PAR10 par algorithme ; si la jointure n'est pas exhaustive, en rapporter les ID et **ne pas cacher les exclusions**. Vérifier absence de doublons par `(instance, algorithm, repetition)`, cohérence des étiquettes `runstatus`, valeurs non finies, coût manquant et plis absents. Si répétitions : agréger les PAR10 par médiane entraînement et test, puis démontrer séparément qu'aucune répétition n'est mélangée entre plis. Absence de caractéristiques numériques imputée **par médiane de l'entraînement uniquement** et centrage/normalisation **par moyenne/écart-type calculés sur l'entraînement uniquement** ; écart-type nul -> 1 ; composantes normalisées tronquées à [-10,10] pour stabilité numérique.

Entraîner chaque bras sur les **neuf autres plis** officiels, évaluer sur le dixième ; répéter pour 10 plis. Ne jamais optimiser les hyperparamètres en consultant les valeurs de test d'aucun pli. Il s'agit de CV standard sur un benchmark connu publiquement, **pas de holdout secret**. Les caractères du nom du fichier d'instance sont exclus des variables du sélecteur.

## Méthodes pré-définies sans retouche
- **SBS** : meilleur solveur unique sur les 9 plis d'entraînement en moyenne PAR10, ordre lexicographique pour départager.
- **KNN-1, KNN-5, KNN-15** : choisir pour chaque test le solveur minimisant la moyenne PAR10 des `k` voisins euclidiens de l'espace normalisé des 37 caractéristiques. Les voisins sont sélectionnés par distance, puis ID pour départager ; algorithme choisi par coût moyen, puis nom lexicographique. `k` est fixé avant tout résultat.
- **KNN-5-small** : même protocole, mais **les 8 premières** caractéristiques seulement, avec l'étape `base` entière tout de même facturée, conformément au fichier de coûts.
- **Omega finite v0** : véritable `action_planning_two_step.optimize_policy` du dépôt, horizon **3**, coût de chaque contrôle symbolique `cost_milli=1`, maximum 8 contrôles. Construire **64 hypothèses représentatives** à partir de 64 indices régulièrement espacés des IDs TRAIN triés, aucune donnée TEST. La `decision` de chaque hypothèse est le solveur qui minimise son PAR10 train (égalité lexicographique), poids 1. Pour les contrôles, binariser **f_1 à f_8** selon les médianes TRAIN. Le planificateur apprend un arbre adaptatif sur les résultats `low/high`. Au terme de la branche, choisir le solveur minimisant le PAR10 moyen des hypothèses restantes ; en cas de branche inconnue, utiliser le SBS. Ce programme est explicitement un **pont expérimental** entre un planificateur de risque 0–1 et l'objectif de runtime PAR10, *pas une solution complète au problème de sélection de solveurs*. Inclure tous les choix de paramètres et les échecs.
- **VBS rétrospectif** : `min` des PAR10 sur l'instance test, calculé après révélation des résultats et affiché seulement comme **borne non admissible**, jamais comme modèle concurrent.

Tous les bras feature-based ont accès au même bloc `base` et supportent sa **totalité** du coût enregistré. SBS et VBS ne paient pas `base`. La métrique principale est **la moyenne du PAR10 réalisé + coût `base` si utilisé**, en secondes pénalisées, ainsi que taux de résolution (runstatus ok). Une politique qui choisit un solveur à runtime PAR10=18000 garde la pénalité, et le coût de feature est ajouté au total ; c'est une convention conservatrice. Rapporter aussi la médiane et la variance par pli, l'écart SBS–KNN, et le regret contre VBS sans présenter VBS comme modèle possible.

## Tests de falsification / qualité
1. Contrôler indices uniques, nombres de plis, algorithmes, caractéristiques, lignes, jointures, trous et duplicats avant score.
2. Garantir que tous les paramètres/imputations et sélection SBS/KNN/Omega sont entraînés sur les autres plis ; chaque vérité de test n'est lue qu'au moment du score, pas pour choisir le solveur.
3. Comparer une implémentation auxiliaire `SBS` et `VBS` en Python standard à un calcul indépendant en JS ou autre si possible ; vérifier les valeurs limites (tous timeout, distances égales, caractéristiques manquantes).
4. Le `runstatus` doit être cohérent avec `PAR10`, ne pas confondre 1800 cutoff et 18000 pénalité.
5. Tout dépassement, exclusion ou source indisponible interdit d'affirmer un score externe complet.
6. Comparer à **tous les KNN** et pas seulement au SBS ; aucun bénéfice propre à Omega n'est établi si KNN le bat ou l'égale. Ne pas qualifier ces baselines de state-of-the-art : ASlib/AutoFolio, SATzilla et Hydra sont plus forts ou spécialisés.
7. Code de référence disponible et attribution/licence explicites. **Pas de promotions CORE** sur la seule base de ces simulations de sélection (les runtimes sont réels, mais les politiques sont rejouées).

## Arrêt
Un seul examen externe 10 plis et ses audits pré-définis. Aucun changement de k, profondeur, fonctions d'imputation, mesures ni choix de scénario après les résultats. Si bugs, versionner les correctifs puis conserver l'ancien verdict explicite. Les mesures upstream sont historiques ; ne pas prétendre avoir rerun les solveurs eux-mêmes.

PR DRAFT empilée sur #36 ; conserver `main`, SQLite et bibliothèque certifiée intacts.
