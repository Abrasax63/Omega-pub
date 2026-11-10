# Omega — horizon de décision variable 0–4, contrôles exacts

**Statut : EXPÉRIMENTAL, calcul exact sur modèles de preuves artificiels.**

## Objectif

La [PR #23](https://github.com/Abrasax63/Omega-pub/pull/23) a montré
un bénéfice possible de deux étapes, mais aussi une synergie exigeant trois.
Cette expérience étend le **même** planificateur, au lieu d'introduire un
nouvel orchestrateur ou une mémoire concurrente.

L'algorithme `prism/action_planning_two_step.py` accepte :
- `max_depth` entre 0 et 4, **maximum** de contrôles sur toute branche ;
- `max_cost_milli` entre 0 et 4000, plafond **dur par branche**, facultatif ;
- arrêt anticipé dès qu'aucune vérification améliore l'objectif exact.

Les coûts (millièmes de perte 0/1) ne sont **ni des euros, ni des tokens,
ni une latence observée**. Les hypothèses, probabilités et distributions
d'observations sont fournies ; aucun outil n'est exécuté.

## Critère exact

Minimiser : probabilité résiduelle de mauvaise décision + somme
**espérée** des coûts de vérification.

Le budget, lui, est une contrainte dure de somme des coûts sur **chaque**
chemin. L'algorithme utilise `Fraction`, un cache de sous-problèmes et
les mêmes statuts de P1. L'augmentation de la profondeur ne peut augmenter
l'optimum *dans ce modèle*, car elle permet toujours de conserver le plan
plus court. Les contrôles à coût nul restent possibles avec budget nul,
s'ils apportent de l'information.

## Reproductibilité et oracle indépendant

`prism/variable_horizon_oracle.py` énumère explicitement les arbres
conditionnels, sans appeler le programme dynamique, pour les scénarios
à trois contrôles maximum et profondeurs 0,1,2,3.

Le test doit comparer **120 modèles × 4 profondeurs = 480 confrontations**.
Il valide la perte totale exacte, le premier contrôle et le nombre moyen
d'étapes. Il conserve les 24 scénarios construits et les 96 scénarios
synthétiques à graine fixe de la PR #23 : ces cas ne sont pas un holdout
indépendant, ni une évaluation d'un modèle linguistique.

Tests positifs/négatifs supplémentaires :
1. Trois bits, décision par parité : aucune profondeur inférieure à 3
   n'améliore la décision, tandis que trois contrôles de coût 0,01 chacun
   donnent une perte 0,03.
2. Quatre bits : trois contrôles ne suffisent pas ; quatre coûtent 0,04
   et déterminent la décision.
3. Un plafond de coût par branche peut interdire un plan pourtant utile ;
   avec budget 0, un contrôle informatif gratuit reste autorisé.
4. La profondeur 4 doit pouvoir s'arrêter au premier contrôle dès qu'il
   suffit : pas de calcul supplémentaire imposé.
5. L'invariance des hypothèses, des contrôles et la croissance
   monotone des budgets/profondeurs sont testées.

La profondeur 4 est contrôlée sur les cas particuliers par un certificat
combinatoire simple (parité), **pas** par l'oracle exhaustif indépendant
sur les 120 scénarios. Les performances sur données réelles restent
entièrement à tester.

## Verrous non résolus

- Faux modèle d'observations ou de coûts => stratégie parfois pire
  qu'une abstention ; contre-exemple documenté dans la PR #23.
- Horizon 4 non universel : cinq bits de parité exigeraient cinq
  observations, même avec contrôles exacts.
- L'algorithme suppose les observations déterministes conditionnellement
  à l'hypothèse, sans erreur de mesure.
- Aucun processus de génération/notation A/B/C, ni appel de modèles,
  n'est inclus ici. Une vraie validation exige des problèmes externes,
  un jeu gelé par un tiers, des réponses aveugles et des coûts réels.

Commande depuis `09_INFRASTRUCTURE_AGENTIQUE/prism` :

```bash
python -m unittest -v test_variable_horizon
python variable_horizon_oracle.py
```

Le workflow RCE de GitHub Actions exécute tous les tests unitaires du
dossier, dont ceux-ci. **Ne revendiquer les comptes qu'après inspection
des journaux CI.**

Aucun effet sur main, aucune promotion en bibliothèque certifiée,
aucune preuve de gain scientifique.
