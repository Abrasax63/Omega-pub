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


## Mesures CI vérifiées — 10 novembre 2026

La [CI 42916399373](https://github.com/Abrasax63/Omega-pub/actions/runs/42916399373)
a validé 94 tests du Prisme après mise à jour d'un ancien test qui
interdisait la profondeur 3. Les 480 comparaisons exactes indépendantes
ont réussi. Parmi 120 scénarios synthétiques, la profondeur 3 réduit
strictement l'objectif par rapport à 2 dans **3 scénarios**.

La [CI 42916623839](https://github.com/Abrasax63/Omega-pub/actions/runs/42916623839)
a ensuite validé **96 tests du Prisme**, les tests RCE/MCP et les
smoke tests des index ; elle reproduit les 480 comparaisons et la
répétition sur sources publiques.

### Petit pilote sur faits externes, non aveugle

Le fichier `prism/public_source_pilot.py` propose **huit questions réelles
à réponse vérifiable**, issues de sources primaires :

- RFC 9110, §13.1.3 : priorité d'If-None-Match sur If-Modified-Since,
  et cas d'une méthode POST ;
- RFC 9110, §13.1.4 : priorité d'If-Match sur If-Unmodified-Since ;
- RFC 3986, §5.2.4 et §5.4.1 : résolution des références relatives
  et suppression des segments de chemin ;
- documentation Python 3.11 du modèle de données : relation bool/int,
  et distinction entre `isinstance` et égalité exacte de type.

Références primaires, stables et consultables :
https://www.rfc-editor.org/rfc/rfc9110.html#section-13.1.3
https://www.rfc-editor.org/rfc/rfc9110.html#section-13.1.4
https://www.rfc-editor.org/rfc/rfc3986.html#section-5.2.4
https://www.rfc-editor.org/rfc/rfc3986.html#section-5.4.1
https://docs.python.org/3.11/reference/datamodel.html#the-standard-type-hierarchy

La sélection de la consultation primaire est correcte **8/8 par
construction du modèle** ; quatre vérités sont de plus vérifiées
directement par le runtime Python. Lorsque la source primaire n'est
plus disponible et que le résumé est non informatif, le planificateur
s'abstient.

**Limitation décisive :** ni les documents RFC/Python ni le Web ne
sont réellement consultés par Omega au cours de cette simulation.
La connaissance des bonnes réponses et des observations conditionnelles
est codée à l'avance. Ces faits sont externes, mais ce benchmark
n'est **pas une épreuve indépendante de compétence, ni un holdout**,
et ne prouve pas une amélioration de précision.

La suite pertinente est un protocole P5 gelé sur des cas réels
**non vus**, avec accès à des outils d'observation réels, déroulement
conditionnel et vérification des décisions finales par un tiers. Ne
pas avancer le statut CORE avant cette étape.
