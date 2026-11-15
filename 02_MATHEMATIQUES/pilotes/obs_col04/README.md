# OBS-COL-04 — Découverte active et réfutation d'invariants apparents

**Date :** 2026-11-15  
**Statut :** CALCUL EXACT / pilote synthétique fini / PAS de découverte scientifique ouverte  
**Branche :** experiment/obs-col04-active-constraint-discovery-2026-11-15  
**Base de PR :** PR #40 (\`experiment/observer-gates-optin-transfer-2026-11-11\`), PAS \`main\`.  
**Engagement antérieur au code :** [PREREG_OBS_COL04.md](PREREG_OBS_COL04.md), commit \`b81ca1c35c61bb26dc76db3b50b7fe531a62a267\`.

## Objet

Une propriété collective peut-elle paraître conservée lorsque seules quelques
interactions ont été observées, puis être réfutée par une intervention sélectionnée
automatiquement ? Les changements d'interaction sont *conditionnés par l'état*,
pas par un calendrier fixé. Aucun individu de base hiérarchique n'est imposé.

## Réutilisations contrôlées

- Le **vrai** module \`09_INFRASTRUCTURE_AGENTIQUE/prism/action_planning_two_step.py\`
  (famille PR #23) et \`planner.py\` (Omega P1) sont hérités de la branche
  de base PR #40 : décision conditionnelle avec coût fictif, sans LLM.
- Le **vrai** \`observer_guard_bridge.inspect_observer_evidence\` (PR #40)
  fournit un avis non certifiant et reçoit \`declared_exhaustive=False\`.
- \`collective_observability.walsh\` est réutilisé depuis PR #86 :
  fichier recopié sans changement, SHA de blob Git
  \`a4c01358e24950d2d039fd1f561b4f433e0b6e1d\`.
- Aucun nouveau moteur exact, orchestrateur ou second registre scientifique.

## Construction, apprentissage et point de fuite à éviter

Monde synthétique à trois bits, deux interventions \`pulse\` et \`bind\`.
L'action \`pulse\` modifie un groupe de bits choisi selon l'état présent ;
\`bind\` modifie un autre groupe. La trajectoire \`pulse / bind / pulse\`
peut donc activer des groupes différents, même avec la même action.

Le laboratoire fournit **à l'avance** un catalogue de 36 fonctions de
transition candidates. L'environnement cache seulement l'identité de la
fonction réalisée. Les six cibles tests sont publiques et énumérées dans le
pré-enregistrement : **aucun holdout aveugle**.

Les observations initiales sont 6 mesures binaires à l'état 0 (trois
capteurs pour chacune des deux actions). Le candidat 'invariant apparent'
est calculé **uniquement à partir des mesures**, pas de la cible cachée.
L'algorithme conserve le sous-ensemble du catalogue compatible avec les
mesures et sélectionne, à travers le vrai P1 + PR #23, un nouveau test dans
une liste de huit consultations candidates. Un oracle exact distinct
énumère toutes les politiques de deux tests de cette même liste : sa perte
attendue est identique à celle de PR #23 sur les cas testés.

Enfin un capteur supplémentaire est utilisé pour chercher un **contre-exemple
directement mesuré** à l'invariant initial. Un avis PR #40 ne fournit jamais
un certificat de vérité ou de provenance.

## Résultats CI exécutés, sources

- **[Run GitHub Actions #43709826592 — SUCCESS](https://github.com/Abrasax63/Omega-pub/actions/runs/43709826592)** sur commit \`75fc512bc03d55017ba09b394b8323520a9220cc\`.
- Python 3.11.18 ; **10 tests unitaires réussis** et six épisodes réellement exécutés
  avec P1/PR23/PR40 ; aucune invocation de modèle.
- [Archive originale JSON](https://github.com/Abrasax63/Omega-pub/actions/runs/43709826592/artifacts/14159608258).
  Ne pas confondre « GitHub CI SUCCESS » avec la certification d'un résultat
  général.

| Cas | Invariant apparent après observations initiales | Invariant réel (post-hoc) | Contre-exemple direct ? | Nouvelles sondes Omega (dont contrôle) | Coût fictif Omega | Sondes fixes / coût fictif |
|---|---|---|---|---:|---:|---|
| C1 | 7 | aucun | oui | 2 | 48 | 3 / 108 |
| C2 | 7 | 7 | non | 2 | 48 | 3 / 108 |
| C3 | 1 | aucun | oui | 2 | 24 | 3 / 108 |
| C4 | 1 | 1 | non | 2 | 24 | 3 / 108 |
| C5 | 7 | aucun | oui | 2 | 48 | 1 / 36 |
| C6 | 7 | 7 | non | 2 | 48 | 3 / 108 |

Les nombres 1 et 7 sont des masques GF(2), **pas des valeurs ou rangs
universels d'invariants**. Les coûts sont des nombres conventionnels
\`cost_milli=12 × nombre de bits du masque du capteur\` ; aucune facture,
latence ou consommation énergétique n'est mesurée.

Les 6 décisions sont déterminées **relativement à la famille de 36 modèles
fournie**. 3 invariants apparents sont réfutés par une nouvelle mesure ;
3 restent compatibles avec une nouvelle mesure et le catalogue, ce qui
n'est pas une preuve naturelle universelle.

## Comparaison et verdict

La politique Omega/PR23 et **l'énumération exacte indépendante des deux
premières décisions** atteignent la même perte attendue sur la liste
des huit sondes : **pas de gain Omega par rapport au solveur classique exact**.
La politique fixe est un témoin exploratoire, non une comparaison causale
à budget strictement égal ; une supériorité d'Omega ne doit pas être
déduite de ses coûts plus bas ici.

Le véritable mécanisme ajouté est le raccord causal :
observations -> hypothèses compatibles -> plan Omega -> intervention
-> observation nouvelle -> filtrage -> test direct du faux invariant.

Limites supplémentaires : espace fini inventé ; modèles connus et
exhaustivité **supposée** par construction ; règles linéaires candidates,
aucune invariance non linéaire exhaustive ; aucun jeu naturel, aucune
génération de règle hors catalogue, aucune autonomie ouverte ;
source des données et de la vérité issue du même générateur expérimental ;
aucune revue externe indépendante.

## Reproduction

Depuis la racine du dépôt **sur cette branche**, sous Python 3.11+ :

~~~bash
python -m unittest discover -s 02_MATHEMATIQUES/pilotes/obs_col04 -p 'test_obs_col04.py' -v
python 02_MATHEMATIQUES/pilotes/obs_col04/obs_col04.py > obs_col04_result.json
~~~

## Prochaine vérification décisive

Proposer un ensemble de transitions généré par une source **indépendante**
des 36 modèles du pilote, puis tenter de découvrir de nouvelles
représentations et des contre-exemples avec le même budget d'observations
que l'algorithme exact le plus fort. Ajouter ensuite une vraie mémoire
d'échecs et un mécanisme qui peut modifier les classes de modèles,
sans utiliser la vérité cachée comme entrée du planificateur.

**Aucune modification de main, aucun changement de statut CORE, pas de
fusion automatique.**
