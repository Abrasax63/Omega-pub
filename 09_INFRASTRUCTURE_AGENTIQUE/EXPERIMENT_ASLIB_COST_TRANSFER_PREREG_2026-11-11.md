# OMEGA-ASLIB-002 — pré-enregistrement avant toute lecture des scores du deuxième scénario

**11 novembre 2026. Statut : validation externe historique ; scénario cible différent et non utilisé dans le réglage.**

## Objectif falsifiable
Après le résultat négatif d'ASLIB-001 sur MAXSAT-PMS-2016, tester un nouveau sélecteur sensible **aux coûts PAR10** sur le scénario distinct `MAXSAT-WPMS-2016`. Ne pas ajuster sa politique, ses seuils ou ses comparateurs à partir des scores cibles. Une victoire contre SBS mais une défaite contre KNN ou un arbre simple ne constitue PAS une supériorité spécifique d'Omega.

## Sources externes pré-identifiées (métadonnées seulement)
- Dépôt `coseal/aslib_data`, commit immuable **`551b22beef8df17de59286b4822ef720e0aa4d6f`** ;
- répertoire **`MAXSAT-WPMS-2016`**, dont on a constaté l'existence et les cinq métadonnées SHA Git, **sans lire les PAR10, les valeurs de caractéristiques ni les plis** :
  - `algorithm_runs.arff`: `45aec3038b4304714c8047ad79ff0171c59dc5c8`;
  - `feature_values.arff`: `4684f66e4111ce1dbef69e68a14367ce93293853`;
  - `feature_costs.arff`: `2e7b9bdbacab04a87b1ab4766c5841a47eae08e7`;
  - `cv.arff`: `a81207d105555c96a7278ee915f3ff3bd93377b2`;
  - `description.txt`: `a7693da4fdaf433e3f2c0107adabca9592e9b7a8`.
- Ne pas recopier ces fichiers upstream sous une autre licence dans le dépôt. Renvoyer vers ASlib et conserver l'attribution et les licences de la source.

## Schéma et qualité
Lire `description.txt` seulement après ce pré-enregistrement et refuser tout jeu ne déclarant pas des runtimes PAR10 minimisés et le `runstatus`. Vérifier les jointures instance/repetition/algorithm, statut des échecs, toutes les valeurs non finies, plis officiels, caractéristiques et coûts de `base`. La seule étape de caractéristiques `base`, si le scénario la définit, est payée **entièrement** pour chaque bras feature-based (pas de « coût par f_j » inventé). Utiliser toutes les instances avec mesures et caractéristiques communes ; **si suppression**, publier l'identifiant et le motif, jamais une élimination silencieuse. Rejet si source SHA divergent. Les répétitions multiples sont à agréger par médiane *au niveau instance/algorithme* (et vérifier qu'une instance appartient à un seul pli) ; si non pris en charge dans code, arrêter et rapporter.

## Divisions et opérations
Validation croisée sur les **10 plis officiels** si disponibles ; modèle entraîné sur neuf, testé sur le dixième. Pas d'imputation hors train ; standardiser par la moyenne et l'écart-type calculés exclusivement sur train, clip [-10,10], écart-type nul = 1. Toutes les politiques comparées connaissent les **mêmes variables initiales** et paient le coût complet du bloc de caractéristiques dès qu'elles les utilisent.

Fixer les bras suivants, avant tout résultat :
- **SBS** : solveur unique au meilleur PAR10 moyen sur train ;
- **KNN-5 et KNN-15** : distance euclidienne sur toutes les caractéristiques disponibles, algorithme minimisant le PAR10 moyen de k voisins (tie-break nom de solveur) ;
- **TREE-greedy2** : arbre de décision coût-sensible de profondeur au plus 2, utilisant tous les attributs disponibles. Pour chaque attribut, le seuil unique est **sa médiane train du pli** ; partition `x_j <= median_j` / `>`; choisir au nœud la séparation qui minimise la somme des PAR10 moyens optimaux des feuilles enfant, tant qu'elle améliore strictement le choix constant. À la racine et après une séparation, la sélection gloutonne regarde un seul niveau, avec tie-break plus petit index de caractéristique. Feuille = solveur minimisant la somme de PAR10 train, égalité lexicographique.
- **Omega-cost-sensitive-lookahead2** (nouvel adaptateur **expérimental**, PAS le `optimize_policy` original) : recherche à horizon 2 des mêmes séparations médianes fixes. Pour chaque première caractéristique, évaluer **la meilleure seconde séparation indépendante dans chaque sous-groupe**, avec mêmes choix de feuilles et sans prélever de vérité test. Choisir le meilleur premier test par coût empirique final, et préférer un arrêt précoce si aucun gain strict. C'est une forme supervisée bien connue d'induction d'arbres coût-sensible, non une nouvelle invention ni preuve de mémoire scientifique.
- **VBS rétrospectif** : minimum PAR10 par instance test, **borne inaccessible à tout bras**.
- Pour audit de représentation, **TREE-greedy1** (arbre un seul niveau) peut être rapporté séparément comme ablation prédéfinie.

Objectif d'optimisation pour les deux arbres : **somme des PAR10 des solveurs choisis**, sur train uniquement (moyenne équivalente puisque cardinal fixé). Les frais de caractéristiques sont identiques et indépendants du chemin pour tous les modèles feature-based, donc **ne changent pas les décisions internes** ; les ajouter toutefois aux scores finaux.

**Important** : tout algorithme a le droit de ne pas améliorer SBS. Il est interdit d'abaisser rétroactivement la profondeur, de choisir un sous-ensemble de caractéristiques, ou de modifier les seuils après observation de WPMS. Déclarer les paramètres d'entraînement dérivés des plis, les résultats et les échecs de calcul.

## Tests, indicateurs, verdict
Métriques principales : moyenne PAR10 + coût de `base`, fraction résolue / total, nombre de choix de solveurs par modèle ; par pli, nombre, moyenne, coût. Secondaires : médiane et regret vs SBS/VBS. Contrôle indépendant en JavaScript au moins pour SBS, KNN et VBS, et contre-tests déterministes en Python pour optimiser l'arbre sur quelques distributions fictives, invariance à l'ordre des lignes, et aucune fuite du jeu test.

**Pas de p-value ou de gain statistique déclaré** sans test sur différences appariées et analyse de dépendance des familles. Le critère d'avantage propre au projet nécessite de battre KNN-5/15 et TREE-greedy2, avec même information, coût et prédiction correcte sur un scénario effectivement non vu, et reproduction indépendante du nouveau modèle ; sinon verdict **NON DÉMONTRÉ** même si une politique a une petite avance.

## Limites pré-déclarées
Les mesures de solveurs sont historiques, non réexécutées. Les scénarios sont publics, les partitions sont préexistantes, ce n'est pas un holdout secret ou une expérience LLM. Le choix de famille d'arbres sensibles au PAR10 est motivé par la **défaite observée sur PMS** : l'évaluation sur WPMS constitue un transfert sur un scénario distinct, mais non une architecture figée indépendamment de tout retour antérieur.

## Gouvernance
PR DRAFT empilée sur #37, aucune fusion `main`, pas de mutation CORE, SQLite ou autre bibliothèque validée. Pas de promotion d'amélioration sans contre-validation supplémentaire.
