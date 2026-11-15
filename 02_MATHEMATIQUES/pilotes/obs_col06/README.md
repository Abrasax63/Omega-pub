# OBS-COL-06 — Modèles collectifs concurrents et mémoire cachée

**Date :** 2026-11-15.
**Statut :** CALCUL EXACT, expérimental synthétique, **aucune certification de loi universelle**.
**Branche :** \`experiment/obs-col06-competing-representations-2026-11-15\`, empilée sur la PR #88.
**Engagement original :** [PREREG_OBS_COL06.md](PREREG_OBS_COL06.md), commit \`4961a9a5a5d81e0eb85d76c71f00893e95a8756e\` avant code.
**Amendement post-run déclaré :** [AMENDEMENT_POST_RUN_01.md](AMENDEMENT_POST_RUN_01.md), commit \`6ca2544a779e73dd44c3ae5429bf5e3ea39f0296\` ; ne pas le confondre avec une hypothèse entièrement pré-enregistrée.

## Pourquoi cette expérience ?

Nos tests précédents savaient ajuster une représentation polynomiale choisie à l'avance.
Ici plusieurs **descriptions concurrentes non hiérarchiques** sont disponibles :

- une interaction paire des bits 0 et 1 ;
- une interaction paire des bits 0 et 2 ;
- une interaction simultanée des bits 0, 1 et 2 ;
- un modèle avec mémoire binaire pouvant basculer à chaque action \`prime\` ;
- un modèle avec mémoire binaire qui reste activée après \`prime\`.

Un sixième monde utilise **une mémoire ternaire absente des candidats**.
Le simulateur émet des trajectoires observables de quatre bits. Le planificateur
ne reçoit ni le monde caché ni ses paramètres.

## Architecture réellement raccordée

1. Le jeu de cinq modèles candidats génère des prédictions de traces.
2. **Omega P1 + PR #23**, via \`plan_with_variable_horizon\`, choisit une nouvelle
   consultation selon sa politique exacte à deux étapes et une contrainte de coût.
3. Le simulateur retourne alors la vraie trace pour cette intervention.
4. Les candidats incompatibles sont éliminés.
5. La PR #40 donne un avis consultatif sur les partitions de réponses,
   avec \`declared_exhaustive=False\` ; elle ne certifie rien.
6. La fonction Walsh de la PR #86 calcule certains coefficients d'observation,
   sans prétendre à des invariants physiques.
7. Un **oracle combinatoire indépendant** existant dans OBS-COL-04 retrouve
   la même perte attendue à chaque étape.
8. Six consultations par monde sont **réservées jusqu'à la fin du choix
   des modèles et des interventions**.

Le catalogue des familles et des sondes est connu. P1 participe au choix
des sondes **dans ce catalogue**, mais ne construit pas lui-même une nouvelle
grammaire mathématique. Il ne faut pas présenter cela comme une découverte
scientifique ouverte.

## Théorème local : un certificat de non-Markov déterministe

Si l'on observe deux transitions réalisables \`x -> y\` et \`x -> z\`
pour la même action \`a\`, le même état visible \`x\` et \`y != z\`, alors
**aucune fonction déterministe** \`F_a(x)\` sur les seuls états visibles ne
peut reproduire les deux expériences, sous l'hypothèse de la même dynamique
et d'un reset contrôlé. Preuve immédiate : une fonction ne peut associer
deux images différentes au même argument.

Exemple direct du monde \`MEMORY_TOGGLE\` (après diagnostic séparé) :
- reset \`x=0\`, \`read\` -> observations \`(0,0)\` ;
- reset \`x=0\`, \`prime,read\` -> observations \`(0,0,8)\`.

La seconde transition \`read\` part à nouveau de \`x=0\`, mais finit à
\`x=8\`. Le modèle sans mémoire visible est donc réfuté **indépendamment
de l'exhaustivité des cinq familles candidates**. Cette observation peut
s'expliquer par un état caché, mais ne prouve pas que l'état caché a
exactement la forme de notre modèle jouet.

**Point audité :** le premier run ne produisait pas ce témoin pour
\`MEMORY_TOGGLE\`, malgré son identification par élimination des modèles.
L'amendement post-run ajoute une consultation diagnostique d'entraînement
spécifiquement coûtée et exécutée **avant toute lecture des données
réservées**, avec P1 consulté. Elle n'est pas intégrée dans la comparaison
des coûts de sélection avec la baseline classique.

## Résultats vérifiables

- [CI initiale #43719763333](https://github.com/Abrasax63/Omega-pub/actions/runs/43719763333) : 10 tests réussis, six modèles testés ; défaut de certificat direct dans un cas à mémoire.
- [CI amendée #43720039260](https://github.com/Abrasax63/Omega-pub/actions/runs/43720039260) : 11 tests réussis, certificat supplémentaire.
- Correctif de traçabilité : le nom du monde caché a initialement été transmis
  **dans l'identifiant de mission** au planificateur P1. Les choix mathématiques
  n'en dépendaient pas dans le code inspecté, mais cette fuite de métadonnées
  violait notre exigence d'isolation. Le commit \`552157a2370c6914eb548b34a3f1868b401b3d22\`
  le remplace par \`UNLABELED\` ; un test de non-régression contrôle l'identifiant.
  Tout run antérieur au correctif reste marqué **risque de fuite de contexte**.
- [Tests ultérieurs](https://github.com/Abrasax63/Omega-pub/actions?query=workflow%3A%22OBS-COL-06+competing+representations+exact+audit%22) : vérifier la CI à la tête de branche avant de citer un résultat final.

| Monde caché (évaluateur seulement) | Famille obtenue après entraînement | Sondes actives | Contrôle réservé | Témoin direct de non-Markov |
|---|---|---:|---:|---|
| PAIR01 | PAIR01 | 2 | 6/6 | non |
| PAIR02 | PAIR02 | 3 | 6/6 | non |
| TRIPLE012 | TRIPLE012 | 3 | 6/6 | non |
| MEMORY_TOGGLE | MEMORY_TOGGLE | 3 dont 1 diagnostic post-run | 6/6 | oui |
| MEMORY_SET | MEMORY_SET | 2 | 6/6 | oui |
| OUTSIDE_TERNARY | MEMORY_SET **provisoire**, puis \`OUT_OF_CATALOG_WARNING\` | 2 | 3/6 | oui |

Sur les cinq mondes dans le catalogue : **5 classifications exactes et
30/30 prédictions réservées**. Sur le monde hors catalogue : la mémoire
ternaire a été confondue avec la mémoire binaire sur les données
d'entraînement, puis la différence apparaît aux trois sondes de longueur
4 réservées : **3/6** prédictions, avertissement explicite.

Les essais ne constituent pas une reproduction indépendante des données
naturelles. Les mondes et la réserve sont publics et construits par
l'auteur ; l'évaluateur appelle le **même générateur** que l'oracle
d'entraînement sur d'autres entrées. Aucune génération LLM.

## Verdict et absence de gain spécifique

- **Technique :** sélection effective entre règles collectives et mémoire,
  tests de généralisation isolés, avis PR40 consultatif, enregistrement des
  témoins de non-Markov, et avertissement hors catalogue.
- **Comparaison :** les pertes attendues de PR23 et du meilleur oracle
  combinatoire exact à deux étapes sont **identiques**. Il n'existe donc
  **aucune démonstration d'avantage propre à Omega**.
- **Scientifique :** le catalogue de modèles, les sondes, l'environnement
  et les générateurs sont tous construits par l'expérimentateur. Il ne
  s'agit pas de découverte autonome d'une théorie ou d'un langage universel.
- **Gouvernance :** aucun changement direct de \`main\`, aucune fusion,
  aucune certification ou mutation CORE.

## Reproduction

~~~sh
python -m unittest discover -s 02_MATHEMATIQUES/pilotes/obs_col06 -p 'test_obs_col06.py' -v
python 02_MATHEMATIQUES/pilotes/obs_col06/obs_col06.py > obs_col06_result.json
~~~

## Prochaine vérification décisive

Introduire une **vraie procédure de synthèse de grammaires** : lorsqu'une
contradiction réfute toutes les familles disponibles, proposer une
construction de modèle non préchargée parmi les cinq candidats.
Isoler cette phase sur un ensemble d'environnements conçus indépendamment,
avec verrouillage des données et audit des requêtes. Comparer à
l'identification d'automates actifs (par exemple L* et variantes
d'observation symbolique), aux solveurs SAT/SMT de synthèse et aux modèles
classiques à états cachés, à budget et oracle identiques.

Aucune revendication de « gain d'intelligence » sans comparaison causale,
généralisation et reproductions indépendantes.
