# RAVI-2 Discovery v0.1 — audit, comparaison externe et prototype

Date : 19 octobre 2026

## Verdict

La Bibliothèque dispose déjà d'une excellente couche de **certification et de mémoire scientifique**, mais sa couche de découverte reste trop étroite. Le moteur v1.3 produit des candidats de triage à partir des résultats admissibles, mais il exclut explicitement les paires appartenant à des projets différents. Il est donc structurellement incapable de découvrir les ponts transverses qui constituent précisément la prochaine étape du programme.

Un prototype séparé, **RAVI-2 Discovery v0.1**, a été construit sans modifier la base scientifique. Il lit seulement `certified_active_results`, extrait des signatures structurelles et propose des candidats inter-projets. Il ne peut ni certifier une brique ni créer une relation `DEPEND_DE`.

État d'entrée : 83 résultats, 79 admissibles. Sortie v0.1 : 40 candidats de triage diversifiés.

## 1. Limite exacte du moteur actuel

Le moteur `/Recherche/04_CODE_DONNEES/ravi2_v13_engine_base.py`, fonction `refresh_candidates`, contient la garde :

```python
if a["project_id"]!=b["project_id"]:
    continue
```

Le moteur actuel est donc adapté à la recherche de raccordements internes à un projet, mais pas à la recherche de ponts entre Δ_h, observabilité, quantique, temps, transformations, Schrödinger ou outils externes.

Il est également essentiellement lexical : tokens communs, Jaccard/couverture, préfixes d'identifiants et polarité obstruction/construction. Ce triage a déjà été utile, mais il ne représente pas encore les types mathématiques, morphismes, quantificateurs, invariants ou interfaces de preuve.

## 2. Ce qui se fait ailleurs

### Google AI Co-Scientist

Le système Google AI Co-Scientist (2025–2026) utilise des agents spécialisés de génération, réflexion, classement, évolution, proximité et méta-revue. Le point transférable ici n'est pas le nombre d'agents mais le **cycle compétitif d'hypothèses**, où une idée doit survivre à plusieurs critiques avant d'être conservée.

Référence : Google Research, *Accelerating scientific breakthroughs with an AI co-scientist*, 19 février 2025.

### ERA / Computational Discovery et AlphaEvolve

ERA recherche dans un espace de programmes par arbre de recherche avec une métrique objective. L'étude Nature 2026 rapporte aussi des recombinaisons systématiques de méthodes : 24 des 55 recombinaisons testées ont dépassé leurs deux méthodes parentes sur les métriques communes. AlphaEvolve pousse la même philosophie plus loin avec évolution de programmes et évaluateurs automatiques.

Le principe transférable est majeur : **générer beaucoup, mais n'accumuler que ce qui dispose d'un évaluateur objectif**.

Références : Nature 654, 909–916 (2026), *An AI system to help scientists write expert-level empirical software* ; Google DeepMind, *AlphaEvolve* (2025, suivi 2026).

### SciAgents

SciAgents combine un graphe ontologique scientifique, des LLM et un système multi-agent afin de chercher des relations interdisciplinaires inattendues. C'est le système externe le plus proche de l'idée d'un graphe de briques reliées par des structures communes.

Référence : Ghafarollahi & Buehler, *Advanced Materials* 37, 2413523 (2025).

### ResearchAgent et Scideator

ResearchAgent enrichit un article de départ par un graphe académique et des concepts partagés, puis fait réviser les idées par plusieurs agents. Scideator décompose les articles en facettes (but, mécanisme, évaluation), les recombine et ajoute une recherche de nouveauté dans la littérature.

Le principe transférable est la **recombinaison typée**, nettement plus intéressante que la simple similarité de texte.

Références : Baek et al., arXiv:2404.07738 ; Radensky et al., arXiv:2409.14634.

### Mathématiques : AlphaProof, LeanConjecturer, Ramanujan Machine

AlphaProof utilise Lean et l'apprentissage par renforcement afin de produire des preuves mécaniquement vérifiables. LeanConjecturer génère automatiquement des conjectures Lean à partir de Mathlib et filtre les énoncés syntaxiquement valides et non triviaux. La Ramanujan Machine sépare explicitement la génération de conjectures numériques de leur preuve.

Principe transférable : **ne jamais confondre génération, intérêt, vérité et preuve**. Cette séparation est déjà naturelle dans RAVI-2.

### Graphes bibliographiques

OpenAlex expose aujourd'hui un graphe de plus de 320 millions de travaux, auteurs, institutions, sujets et citations, avec recherche sémantique. Semantic Scholar fournit également son Academic Graph et des recherches de snippets. Ces services pourraient devenir la couche externe de détection d'antériorité et de voisinage bibliographique.

## 3. Ce que RAVI-2 a de particulier

Par rapport aux systèmes ci-dessus, la Bibliothèque possède déjà plusieurs gardes difficiles à ajouter après coup :

- statuts épistémiques séparés ;
- provenance et preuves persistantes ;
- versions historiques et rollback causal ;
- dépendances `DEPEND_DE` auditées ;
- interdiction d'utiliser les briques réfutées comme prémisses ;
- reconstruction indépendante ;
- fermeture contrôlée des verrous ;
- distinction entre validité interne et originalité bibliographique.

Le bon objectif n'est donc pas de copier un « AI Scientist » généraliste. Il est de greffer une **couche de découverte agressive au-dessus d'un noyau de certification conservateur**.

## 4. Architecture proposée

### Couche A — noyau scientifique

Entrée : uniquement les résultats admissibles et leurs contrats. Une conjecture ou un staging n'est jamais traité comme vérité.

### Couche B — signatures structurelles

Pour chaque brique : objets, type de dynamique, quantificateurs, hypothèses, invariants, obstruction, opération de composition, type de témoin, nature de la preuve, domaine et échelle (locale/globale, fini/asymptotique, déterministe/probabiliste/quantique).

### Couche C — opérateurs de découverte

1. **Pont structurel** : même motif abstrait dans deux domaines différents.
2. **Dual obstruction/construction** : une brique construit exactement ce qu'une autre interdit sous d'autres hypothèses.
3. **Transport d'invariant** : tester si un invariant survit à quotient, restriction, observation, révélation ou composition.
4. **Recombinaison** : A+B produit-il un énoncé plus fort que A ou B séparément ?
5. **Trou de diagramme** : trois côtés d'un diagramme sont connus, le quatrième manque.
6. **Frontière d'hypothèses** : deux théorèmes proches ont des conclusions différentes ; quelle hypothèse est décisive ?
7. **Spectre d'obstructions** : comparer les tailles/horizons des obstructions minimales dans plusieurs cadres.

### Couche D — classement

Un candidat reçoit des scores séparés, jamais un score de « vérité » :

- pertinence pour un verrou actif ;
- distance structurelle ;
- capacité à changer un verdict ;
- existence d'un test décisif ;
- coût de test ;
- risque de redondance bibliographique ;
- risque de boucle méthodologique.

### Couche E — falsification

Règle RAVI-2 : aucune nouvelle sous-dépendance si elle n'est pas nécessaire, ne peut pas changer le verdict ou ne possède pas de test indépendant décisif.

### Couche F — littérature

OpenAlex / Semantic Scholar / sources primaires pour rechercher : énoncé exact, synonymes, résultats plus généraux, contre-exemples et antériorités.

### Couche G — preuve / calcul

Selon le candidat : preuve symbolique, exhaustive finite search, simulation déclarée, Lean, solveur SAT/SMT, algèbre exacte ou expérience numérique indépendante.

### Couche H — commit RAVI-2

Seulement après les étapes précédentes. Le moteur de découverte ne reçoit aucun droit de promotion.

## 5. Prototype v0.1 effectivement construit

Artefacts :

- `ravi2_discovery_v01.py`
- `RAVI2_DISCOVERY_CANDIDATES_2026-10-19.json`

Le script lit la base principale en lecture seule et a analysé les 79 résultats admissibles. Il autorise les ponts inter-projets, utilise TF-IDF, motifs structuraux, recouvrement d'hypothèses et polarité obstruction/construction. Il produit 40 candidats avec explication et un gabarit de test décisif.

Garde fondamentale inscrite dans chaque candidat :

> TRIAGE_ONLY: candidate is not a theorem, dependency, novelty claim, or scientific premise.

Le prototype reste heuristique. Il sert à augmenter le rappel des bonnes idées, pas à décider lesquelles sont vraies.

## 6. Premier résultat concret du moteur : accès ↔ état prédictif

Le pont `BR-ACC-01` ↔ `BR-STATE-01` a été remonté comme candidat inter-projets. Il conduit à un énoncé précis.

### Énoncé de staging

Soit un système déterministe total avec actions `T_a:X→X`, observation `π`, ensemble initial `E`, et équivalence prédictive canonique

`x≈x' ⇔ π(T_u x)=π(T_u x')` pour tout mot d'actions `u`.

Soit `q:X→X/≈` le quotient, `H=Reach_T(E)` et `Hbar=Reach_Tbar(q(E))`. Alors :

1. `q(H)=Hbar` ;
2. l'équivalence prédictive calculée dans le sous-système accessible `H` est exactement la restriction de `≈` à `H` ;
3. par conséquent `H/(≈|H)` est canoniquement isomorphe au sous-système accessible du quotient global.

### Preuve

La stabilité de `≈` donne `q∘T_a=Tbar_a∘q`, donc par induction `q(T_u e)=Tbar_u(q(e))`. Prendre l'union sur `e∈E` et `u∈A*` donne immédiatement `q(H)=Hbar`.

Comme `H` est stable vers l'avant, toutes les continuations d'un état de `H` restent dans `H`. Deux états de `H` sont donc distinguables par une continuation dans le système global si et seulement s'ils le sont dans le sous-système `H`. L'équivalence se restreint exactement, d'où l'isomorphisme quotient/accessibilité.

### Falsification indépendante

Un checker indépendant a contrôlé :

- 41 018 cas exhaustifs pour `n≤3`, deux actions, observation binaire et tous les ensembles initiaux non vides ;
- 20 000 cas aléatoires supplémentaires pour `n=4..8`, une à trois actions et observations à deux ou trois symboles ;
- zéro violation.

Ce résultat est **DÉMONTRÉ en staging**, mais n'est pas promu dans le noyau pendant cette passe : son intégration exige encore le contrat strict des deux dépendances et un audit bibliographique final. L'idée générale est classique en théorie des automates/congruences ; aucune nouveauté n'est revendiquée.

Artefacts : `check_access_predictive_bridge.py`, `ACCESS_PREDICTIVE_BRIDGE_CHECK.json`.

## 7. Candidats scientifiques les plus intéressants à ce stade

### C1 — Complexe commun de compatibilité : Mealy ↔ V19

`BR-MEALY-HELLY-01` raisonne par non-faces minimales d'un nerf de compatibilité. V19 possède des résultats de compatibilité paire/ternaire, puis un premier ordre d'obstruction en multiplicité. Une abstraction commune par famille descendante de configurations compatibles pourrait produire un **spectre des obstructions minimales**. Le point délicat est que V19 travaille aussi avec des multisets ; ne pas identifier sans preuve simplicial complexe et multicomplexe.

Test décisif : définir le bon objet combinatoire, reconstruire les invariants Mealy et V19 comme deux instances, puis chercher un énoncé non tautologique qui transfère réellement une borne.

### C2 — État prédictif ↔ mémoire quantique SWAP

`BR-STATE-01` définit l'état par les réponses à toutes les continuations admises. `BR-Q-SWAP-MEM-01` exhibe deux histoires ayant le même réduit instantané mais des réponses futures différentes. Cela fournit un exemple exact où le réduit n'est pas une statistique suffisante pour l'interface de continuations.

Test : formaliser l'interface d'instruments et comparer le quotient prédictif au quotient par égalité du réduit. Ne pas conclure à une mémoire irréductiblement quantique.

### C3 — Détection locale optimale ↔ impossibilité globale finie

`DESC-CLIP-01` optimise localement la croissance logarithmique d'un facteur d'évidence robuste. `DET-FIN-01` impose une impossibilité asymptotique à toute machine finie à risque total borné. Leur combinaison peut fournir une frontière propre : **l'optimalité locale du score n'abolit pas la limite structurelle de mémoire**.

Test : vérifier que toute implémentation finie du détecteur projeté satisfait exactement les hypothèses de DET-FIN-01, puis dériver la limite sans hypothèse cachée d'horloge infinie.

### C4 — Temps de résolution ↔ mémoire finie de détection

`BR-TIME-01` donne une résolution `Θ(√T)` dans une dynamique réversible. `DET-FIN-01` montre une perte de sensibilité aux changements arbitrairement tardifs pour un détecteur fini. Une question testable est de chercher une borne mémoire–résolution pour les observateurs finis d'une dynamique périodique réversible.

Statut : piste, pas théorème.

### C5 — Δ_h ↔ spectres d'obstructions de compatibilité

`DELTA-SPECTRUM-CLASS` classifie un spectre temporel de défauts local→global ; Mealy/V19 possèdent des obstructions de compatibilité d'arité. Il faut tester s'il existe une construction commune par automates de témoins, ou si l'analogie est seulement terminologique.

Critère d'arrêt : si aucune transformation functorielle ou correspondance de témoins ne préserve les deux notions, classer l'analogie comme non productive.

## 8. Prochaine version recommandée

**RAVI-2 Discovery v0.2** devrait remplacer la majeure partie du lexical par des contrats typés :

- `input_objects`
- `output_claim`
- `quantifiers`
- `assumptions`
- `invariants`
- `operations`
- `failure_mode`
- `witness_type`
- `proof_mode`

Puis construire un graphe biparti `résultats ↔ concepts typés`. La découverte consisterait à chercher des motifs de graphe incomplets plutôt que des mots semblables.

En parallèle, une couche bibliographique peut interroger OpenAlex par recherche sémantique et voisinage de citations, puis Semantic Scholar pour les références/citations et snippets. Ces résultats doivent rester des preuves de recherche bibliographique, jamais des preuves mathématiques.

## 9. Critère d'arrêt

La couche Discovery ne doit jamais devenir une nouvelle source de boucle. Pour chaque candidat, budget par défaut :

1. une formalisation d'interface ;
2. au maximum deux expériences décisives ;
3. verdict `PROMETTEUR`, `RÉFUTÉ`, `REDONDANT` ou `INDÉTERMINÉ` ;
4. seuls les résultats démontrés passent ensuite dans le cycle RAVI-2 normal.

## Conclusion

L'architecture la plus prometteuse n'est pas un agent autonome qui « pense longtemps ». C'est un système à deux régimes :

**Discovery large et risqué → RAVI-2 étroit et conservateur.**

Le prototype v0.1 montre déjà que la contrainte « même projet » nous faisait perdre des ponts utiles, et le premier pont sélectionné a débouché sur un petit théorème exact de commutation accès/quotient prédictif. Cela suffit pour justifier la poursuite vers une v0.2 typée et connectée à la littérature.