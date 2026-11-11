# OMEGA — Cartographie de l'art antérieur et verrous d'avantage stratégique (2026-11-11)

**Statut BIBLIOGRAPHIE CONTRÔLÉE, pas preuve de performance d'Omega.**
Note liée à ASLIB-001 / PR #37. Aucun travail antérieur cité ne doit être présenté comme une invention de ce projet.

## Références vérifiables et rapprochement honnête

1. **Sélection de portefeuille et configuration de nouveaux solveurs : Hydra.**
   Xu, L., Hoos, H., Leyton-Brown, K., *Hydra: Automatically Configuring Algorithms for Portfolio-Based Selection*, AAAI 2010. https://ojs.aaai.org/index.php/AAAI/article/view/7565
   Le modèle pré-existe : configuration itérative de solveurs complémentaires au portefeuille en place. Le programme Omega ne doit pas revendiquer comme invention l'idée générale de sélection ou de spécialisation de méthodes. Différence possible à **tester** : compléter le portefeuille par des moyens de preuve, des réfutations et une mémoire traçant la validité scientifique, non uniquement le runtime.

2. **Bancs externes et coût des caractéristiques : ASlib.**
   Bischl et al., *ASlib: A Benchmark Library for Algorithm Selection*, *Artificial Intelligence* 2016, https://arxiv.org/abs/1506.02465 ;
   données https://github.com/coseal/aslib_data ; format https://github.com/coseal/aslib-spec/blob/master/format.md .
   Le scénario MAXSAT-PMS-2016 fournit des mesures et plis CV préexistants. Les publications distinguent meilleure politique globale (SBS), oracle virtuel rétrospectif (VBS), coûts d'observation, performances pénalisées. Ne pas compter VBS comme rival admissible. Les données upstream sont sous **GPLv3**, attribuées au dépôt original.

3. **Sélection coût-sensible : AutoFolio.**
   Lindauer, Hoos, Hutter et Schaub, *AutoFolio: An Automatically Configured Algorithm Selector*, JAIR 2015 ; https://github.com/automl/AutoFolio .
   Référence plus forte à implémenter ou répliquer si l'environnement le permet ; comparer Omega aux KNN seuls ne suffit pas pour une affirmation de supériorité vis-à-vis de l'état de l'art.

4. **Apprentissage des politiques de mémoire d'agents : AEL.**
   Xu et al., *AEL: Evolving Agent Harness in Open-Ended Environments*, Findings of EMNLP 2026, https://aclanthology.org/2026.findings-emnlp.1316/ .
   Deux échelles : sélection en ligne de politiques de récupération par bandit (Thompson Sampling) et adaptation plus lente par réflexion. Les avantages rapportés concernent les tâches **de leur étude**, pas Omega. À tester contre eux : valeur de la mémoire scientifique certifiée au-delà d'un cache, et décision de consulter/ignorer une mémoire selon sa provenance et sa fiabilité.

5. **Planification réelle avec outils imparfaits : PlanBench-XL.**
   Liu et al., *PlanBench-XL: Evaluating Long-Horizon Planning of LLM Tool-Use Agents in Large-Scale Tool Ecosystems*, arXiv 2026, https://arxiv.org/abs/2606.22388 .
   Le cadre mesure l'accès à des outils inconnus, les dépendances d'information, les pannes, les changements de stratégie. Un score Omega sur un graphe artificiel `probe -> tool` n'est pas automatiquement transférable à ces conditions.

6. **Savoir s'abstenir : AgentAbstain.**
   Liu et al., *AgentAbstain: Do LLM Agents Know When Not to Act?*, NeurIPS 2026, https://agentabstain.github.io/ .
   Des tâches appariées distinguent agir et s'abstenir à bon escient. La qualité d'un certificat, la possibilité de refus et les faux positifs confiants doivent être des métriques de première importance, pas uniquement le taux de résolution.

## Constat empirique de PR #37 (sans généralisation)
Le pont Omega v0 utilise vraiment `optimize_policy`, mais avec 64 mondes représentatifs et 8 caractéristiques binarisées. Sur ASlib MAXSAT-PMS-2016, il bat SBS (PAR10 moyen 2030,663 contre 2231,818), mais KNN-15 est meilleur (1782,146). Les statistiques externes des références ont été recalculées indépendamment en JS. **La nouveauté ni la supériorité de l'architecture ne sont démontrées par ce résultat.**

## Verrous prioritaires avec conditions d'arrêt

**V1 — Alignement de l'objectif.** Remplacer le risque 0–1 d'« identifier le meilleur solveur » par l'espérance du coût de résolution, du coût d'acquisition de caractéristiques et de l'absence de certificat. Tester les méthodes sur un **AUTRE scénario gelé avant les scores**. Contrôle : optimiseur coût-sensible simple + KNN/AutoFolio, mêmes données et budget. Arrêt : si aucune amélioration après deux tests discriminants, classer `INDÉTERMINÉ` ou `RÉFUTÉ POUR LE DOMAINE`, ne pas complexifier pour sauver la thèse.

**V2 — Vérification indépendante des connaissances.** Tester des faux contenus malgré métadonnées correctes, provenance des outils, éditions des normes, et signaux intermédiaires trompeurs. Contrôle : stratégie non adaptative utilisant exactement les mêmes validations, mêmes ressources. Aucun gain de provenance attribuable au planificateur si simple filtre identique égale le score.

**V3 — Adaptation après changement de distribution.** Séparer entraînement, validation et déploiement temporel ; enregistrer coût de réentraînement et de changement d'outil. Comparer sans mémoire, mémoire historique simple, mémoire certifiée, et sélection bandit/AutoFolio. L'égalité avec un modèle linéaire ou règle conditionnelle simple est un résultat **négatif utile**.

**V4 — Qualité des tâches.** Fixer des tâches naturelles sans indices artificiellement masqués et sans choisir les cas par leurs réponses. Recherche, calcul, preuve, réfutation et édition de sources peuvent être complémentaires, mais la capacité à identifier le type de problème depuis l'énoncé doit être accessible **aux concurrents**. Une amélioration due seulement à une condition synthétique d'opacité ne mesure pas une stratégie transférable.

**V5 — Coûts et calibration.** Reporter coût PAR10/latence/tokens réels quand disponibles, précision et abstentions, confiance sur erreurs, et effet des pannes. Vérifier les comparaisons avec des implémentations indépendantes, en gardant une borne oracle explicitement rétrospective.

## Règle de décision
**La prochaine promesse d'Omega ne doit pas être « adaptatif > fixe ». Elle doit être « une combinaison de mémoire certifiée, sélection de méthode et vérification des preuves > meilleur concurrent ayant les mêmes informations, outils, moyens et droits », puis falsifier cette différence dans plusieurs domaines réellement externes.**

Ne pas promouvoir cette note bibliographique au rang de preuve de supériorité ; garder PR en brouillon, `main` et CORE inchangés.
