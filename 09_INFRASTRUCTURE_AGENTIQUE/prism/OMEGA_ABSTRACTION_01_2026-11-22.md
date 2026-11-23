# OMEGA-ABSTRACTION-01 — généralisation et changement de représentations

**22 novembre 2026 — expérimentation sur la branche de la PR #231.**

## Pourquoi cette expérience

Un agent qui ajoute simplement des définitions n'apprend pas nécessairement à
les dépasser. Nous séparons donc deux capacités :

1. **Proposition créative** : le modèle sélectionne dans son propre registre
   deux concepts qu'il souhaite rapprocher et fournit **ses propres exemples
   structurés**, sans qu'on lui présente les conclusions attendues.
2. **Contrôle indépendant borné** : un programme sans modèle examine la
   validité des propriétés sur ces exemples, cherche ce qui est commun,
   montre ce qui a été perdu par l'abstraction et tente des contre-exemples.

L'intuition mathématique est qu'une intersection de conditions observées sur
plusieurs structures peut définir une **classe candidate plus générale**.
Cela n'en fait ni une définition optimale ni un théorème universel.

## Moteur exactement implémenté

`concept_abstraction_lab.py` propose une première grammaire **bornée de
relations binaires finies**, sans noms de théorèmes précalculés :

- deux représentations : listes d'arêtes et matrices d'adjacence booléennes ;
- univers de 2 à 4 objets, 2 à 8 spécimens distincts ;
- huit propriétés vérifiées avec témoins de réfutation :
  réflexivité, irréflexivité, symétrie, antisymétrie, transitivité,
  totalité (sur les couples distincts), sérialité, fonctionnalité ;
- invariance par transformation arêtes ↔ matrice et par **toutes les
  permutations des étiquettes** de chaque spécimen (24 au plus) ;
- construction de la liste des propriétés communes et conservation de celles
  propres à chaque spécimen, au lieu d'écraser leurs descriptions ;
- contre-modèles finis sur 2 ou 3 éléments pour certaines propriétés
  distinctives qui ne sont pas imposées par la définition commune ;
- possibilité de soumettre des propriétés conjecturées par le modèle et
  de les réfuter par témoins sur les entrées ;
- essais sur des **holdouts indépendants** quand ils sont fournis.

Le contrôle est exact sur les spécimens finis et exhaustif dans son petit
espace de contre-modèles, mais **NE PROUVE RIEN sur toute une classe
mathématique**.

## De la bibliothèque à une tentative d'abstraction non prémâchée

`from_library(...)` lit le registre vérifié par chaînage de la PR #231,
retient au maximum huit fiches admissibles (toujours en quarantaine) et
demande au modèle local :

- de choisir **de lui-même deux concepts** candidats ;
- d'inventer une petite illustration de relation binaire pour chacun ;
- de proposer les propriétés à explorer ou de s'abstenir.

L'algorithme ne préremplit aucun nom de concept, aucune paire de références et
aucun exemple dans l'invite de ce mode. Il ne demande pas non plus une
conclusion pré-écrite. Le format contraint les sorties à un petit domaine
calculable ; les représentations et la ressemblance sémantique sont
**fournies par le modèle, NON vérifiées par les sources**.

Par défaut, le système **ne publie aucune nouvelle définition comme
vérité**. La sortie conserve le JSON brut, le SHA, les témoins, les
propriétés perdues, le statut et les IDs des fiches originales. Les
interprétations parallèles restent disponibles : aucune fusion destructive.

## Première expérience reproductible (hors ligne, données synthétiques)

Exemple de deux relations sur `a,b,c` :

- spécimen A : diagonale + `aRb` + `bRa` ;
- spécimen B : diagonale + `aRb` + `bRc` + `aRc`.

Le moteur doit observer la réflexivité et la transitivité communes, tout
en refusant de généraliser la symétrie du premier spécimen au second. Il
fournit un contre-exemple `(a,b)` dans le second.

Ces données sont choisies **pour tester le logiciel**, PAS pour prétendre
qu'Omega a redécouvert seul la théorie des préordres.

## Commandes de test

Dans `09_INFRASTRUCTURE_AGENTIQUE/prism` :

```bash
python -m unittest -v test_concept_abstraction_lab
```

Sur un registre éducatif existant, avec un vrai modèle local déjà lancé :

```bash
python concept_abstraction_lab.py \
  --library memoire_educative_candidates.jsonl \
  --output tentative_abstraction.json \
  --server http://127.0.0.1:8080
```

On peut aussi fournir un fichier JSON externe contenant `specimens`,
`proposed_axioms` et `holdout`, via `--specimens`, sans utiliser de LLM.

**Ce code ne lance aucun serveur, ne contacte aucune API payante, ne modifie
pas les poids et ne démarre pas de tâches automatiques.**

## Risques, falsification et conditions d'extension

- Le vocabulaire des huit propriétés est fixé par l'expérimentateur. Cela
  permet de tester un **changement de représentation dans une grammaire
  limitée**, mais pas l'invention d'un nouveau langage mathématique.
- Les exemples générés par le modèle peuvent être inventés, mal représentés,
  incohérents avec leurs sources ou incapables d'illustrer réellement les
  définitions : un succès logique sur ces exemples n'est **pas** une
  compréhension des textes.
- Une source citée littéralement ne prouve pas la correspondance des
  représentations. Il faut un vérificateur indépendant de cette correspondance
  ou une évaluation externe avant promotion dans une bibliothèque certifiée.
- Des relations peuvent partager des propriétés par accident sur un petit
  nombre de spécimens. Des holdouts et contre-modèles doivent attaquer
  l'abstraction, puis des preuves seront nécessaires pour toute généralisation.
- Si les nouvelles définitions ne procurent pas un gain reproductible sur
  des problèmes nouveaux à budget égal, l'hypothèse d'amélioration est
  **NON DÉMONTRÉE**, même si les tests logiciels passent.

**Prochaine expérience décisive** : faire fonctionner le vrai modèle sur
plusieurs fiches documentaires qu'il a produites, sans lui donner les couples
ni les propriétés attendues. Comparer : (A) sans abstraction ; (B) avec
abstraction suggérée ; (C) avec abstraction + réfutateur exact. Maintenir un
holdout indépendant, mesurer exactitude, abstentions, erreurs silencieuses,
coût et changements de décision.

Références internes : PR #230 (recherche Web), PR #231 (bibliothèque
incrémentale), PR #228 (registre durable de faits **vérifiés séparément**),
laboratoire de provenance #81, oracle fini #82.
