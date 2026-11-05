# Omega-pub — Laboratoire public de recherche RAVI-2 / CCS / Omega-SRR

## Pourquoi ce dépôt existe

Omega-pub est un espace public destiné à présenter des travaux de recherche en cours ou déjà étudiés, à les rendre compréhensibles et vérifiables, puis à les soumettre à une critique extérieure.

L'objectif n'est pas de faire approuver des idées par principe. Il est de permettre à d'autres personnes de comprendre exactement ce qui est affirmé, de refaire les raisonnements et les calculs, de chercher des contre-exemples et, si nécessaire, de montrer qu'un résultat est faux ou trop général.

**La réfutation est une contribution utile. Une critique argumentée vaut davantage qu'une approbation sans vérification.**

Ce dépôt est un projet de recherche ouvert porté par ses contributeurs. Sa présence sur GitHub ne signifie ni qu'il est affilié à une université ou à un laboratoire institutionnel, ni que ses travaux ont fait l'objet d'une évaluation scientifique par les pairs. Toute validation doit être documentée dossier par dossier.

## Architecture modulaire

Le dépôt est organisé en modules scientifiques séparés, reliés par un socle commun de gouvernance documentaire.

- [Architecture générale](ARCHITECTURE.md) — principes, modules, dépendances, versions et reproductibilité.
- [Index global des résultats](00_GOUVERNANCE/INDEX_GLOBAL.md) — inventaire des résultats effectivement documentés.
- [Référentiel des statuts](00_GOUVERNANCE/STATUTS.md) — statuts scientifiques et statuts de publication.
- [Modèle de fiche de résultat](templates/RESULTAT.md) — structure commune des dossiers scientifiques.

### Modules

| Module | Périmètre |
|---|---|
| [01_RAVI2](01_RAVI2/) | Méthode, protocoles, certifications et audits |
| [02_MATHEMATIQUES](02_MATHEMATIQUES/) | Systèmes dynamiques, observation et invariants |
| [03_INFORMATIQUE_THEORIQUE](03_INFORMATIQUE_THEORIQUE/) | SAT, complexité, réductions et P/NP |
| [04_CCS](04_CCS/) | Définitions, structures et résultats CCS |
| [05_OMEGA_SRR](05_OMEGA_SRR/) | Littérature, définitions et recherches Omega-SRR |
| [06_CALCUL_SCIENTIFIQUE](06_CALCUL_SCIENTIFIQUE/) | Programmes, simulations, données et reproductions |
| [07_REVUES_INDEPENDANTES](07_REVUES_INDEPENDANTES/) | Critiques, contre-exemples et réponses |
| [08_ARCHIVES](08_ARCHIVES/) | Versions et dossiers conservés pour traçabilité |

La création d'un module ne certifie aucun résultat. Les dossiers sont alimentés progressivement après vérification de leur contenu, de leur provenance et de leur statut.

## RAVI-2 — Méthode de recherche et de vérification adversariale

RAVI-2 est le cadre méthodologique utilisé pour examiner les résultats. Il vise à réduire les erreurs de raisonnement, les conclusions prématurées et les confirmations circulaires.

Sa démarche consiste notamment à :

1. Partir du dernier état effectivement vérifié, plutôt que de recommencer sans raison une exploration déjà close.
2. Identifier le point incertain qui pourrait le plus changer la conclusion.
3. Tenter d'abord de réfuter l'hypothèse séduisante : rechercher les contre-exemples et les cas limites.
4. Séparer les preuves mathématiques, les calculs exacts, les simulations, les observations empiriques et les conjectures.
5. Faire vérifier les étapes décisives par une méthode ou un raisonnement indépendant.
6. Conserver les hypothèses, les limites, les dépendances, les versions et les résultats négatifs.
7. Ne pas remplacer un résultat antérieur validé par une variante qui n'a pas encore été vérifiée.

RAVI-2 n'est pas une garantie automatique de vérité. C'est un protocole de travail dont l'application et les conclusions doivent elles-mêmes pouvoir être examinées.

## CCS — Corpus de structures et de résultats associés

CCS désigne ici un axe de travaux et un corpus de structures mathématiques étudiées dans le cadre du projet.

Les dossiers publics devront préciser, pour chaque structure :
- sa définition exacte et sa notation ;
- le problème auquel elle répond ;
- les hypothèses nécessaires ;
- les résultats établis et ceux qui restent ouverts ;
- les preuves, calculs ou programmes permettant de les examiner ;
- les liens éventuels avec des résultats déjà publiés dans la littérature.

L'acronyme CCS ne doit pas être interprété comme une équivalence avec une théorie extérieure : son périmètre et ses définitions seront explicités dans les dossiers concernés. Aucun résultat ne sera présenté comme démontré sans justification consultable.

## Omega-SRR — Axe de recherche distinct

Omega-SRR est un autre axe de travail conservé dans le projet. Il sera présenté selon ses propres définitions, sources et critères de validation.

Aucun lien mathématique entre Omega-SRR, CCS et RAVI-2 ne doit être supposé. Lorsqu'un rapprochement sera proposé, le dossier devra distinguer clairement :
- une analogie ou une piste d'interprétation ;
- une correspondance formelle définie ;
- une hypothèse testable ;
- un résultat effectivement démontré.

## Comment lire un résultat publié ici ?

Chaque résultat doit, dans la mesure du possible, être accompagné d'une fiche contenant un identifiant et une version, un énoncé exact, un statut scientifique, un statut de publication, son périmètre, ses hypothèses, une preuve ou un certificat, des contre-tests, ses dépendances, les éléments de reproductibilité et sa provenance.

Le modèle commun est disponible dans [templates/RESULTAT.md](templates/RESULTAT.md). Les statuts sont définis dans [00_GOUVERNANCE/STATUTS.md](00_GOUVERNANCE/STATUTS.md).

### Statuts scientifiques

| Statut | Sens |
|---|---|
| **DÉMONTRÉ** | Une preuve est disponible et son périmètre est explicite. |
| **CALCUL EXACT** | Le résultat découle d'un calcul exact dont les entrées et la méthode sont vérifiables. |
| **SIMULÉ** | Le résultat provient d'une simulation ; il ne constitue pas à lui seul une preuve générale. |
| **EMPIRIQUE** | Le résultat repose sur des observations ou des données décrites. |
| **CONJECTURÉ** | Proposition plausible ou piste de recherche non démontrée. |
| **RÉFUTÉ** | Un contre-exemple ou un argument invalide l'énoncé dans le périmètre annoncé. |
| **INDÉTERMINÉ** | Les éléments disponibles ne permettent pas de conclure. |
| **À RÉEXAMINER** | Un résultat antérieur nécessite un nouvel examen ou une clarification. |

Le statut scientifique est distinct du statut de publication. Un résultat peut être démontré mais pas encore publié ; un document public peut présenter une conjecture.

## Vous souhaitez participer ?

Les contributions extérieures sont recherchées, qu'elles viennent de chercheurs, d'étudiants, de développeurs, de mathématiciens ou de lecteurs curieux.

Vous pouvez notamment demander une définition ou une clarification, signaler une erreur, proposer un contre-exemple, reproduire un calcul, signaler un résultat antérieur dans la littérature, proposer une autre démonstration ou identifier une hypothèse oubliée.

**Pour commencer :**
1. Consultez le [protocole de revue](REVIEW_PROTOCOL.md).
2. Ouvrez une [discussion ou une question dans les Issues](../../issues).
3. Pour une correction documentée, proposez une [Pull Request](../../pulls).
4. Indiquez toujours le fichier, la version et l'énoncé précis que vous examinez.

Les contributions peuvent être rédigées en français ou en anglais. Les échanges doivent rester argumentés, respectueux et vérifiables.

## Comment les critiques seront-elles traitées ?

Une critique extérieure ne sera ni acceptée ni rejetée sur la seule autorité de son auteur. Elle sera examinée à partir de son contenu : identification de l'affirmation, reproduction indépendante, contre-tests, examen des conséquences sur les dépendances et réponse motivée. Les auteurs d'un résultat peuvent répondre, mais leur réponse ne constitue pas à elle seule une validation indépendante.

Le [protocole de revue](REVIEW_PROTOCOL.md) détaille cette procédure. Le nombre d'étoiles, de commentaires ou de contributeurs ne constitue jamais une preuve.

## Limites et engagements

- Ne pas annoncer comme exécuté un calcul ou un programme qui ne l'a pas été.
- Ne pas transformer une simulation en preuve.
- Ne pas masquer les contre-exemples ou les résultats négatifs.
- Ne pas confondre une analogie avec une correspondance mathématique.
- Ne pas présenter une conjecture comme un résultat établi.
- Citer les publications et sources externes utilisées.
- Protéger les données privées, les identifiants, les secrets et les contenus dont la diffusion n'est pas autorisée.
- Versionner les corrections afin de conserver la traçabilité.

## État actuel du dépôt

L'architecture modulaire et ses documents de gouvernance sont en place. Deux fiches Règle 90 sont publiées à titre expérimental et un pilote C4, L=2 est maintenant documenté comme **CALCUL EXACT sous la définition primaire interne V19(2)**, avec publication **EXPÉRIMENTALE**. L'originalité bibliographique reste indéterminée et aucune formalisation Lean n'est revendiquée. Les autres résultats historiques sont migrés progressivement, sans promotion automatique de leur statut.


## Accès rapide

- **Consulter les résultats :** [index global](00_GOUVERNANCE/INDEX_GLOBAL.md).
- **Rechercher une brique :** [registre transversal](00_GOUVERNANCE/REGISTRE_TRANSVERSAL.md).
- **Voir le pilote C4, L=2 :** [dossier, raccord V19(2) et scripts](02_MATHEMATIQUES/defauts_recollement/PILOTE_EXTRACTION_C4_L2_2026-11-04.md).
- **Consulter le protocole d'extraction RAVI-2 :** [protocole](01_RAVI2/PROTOCOLE_EXTRACTION_METHODES.md).
- **Comprendre les statuts :** [référentiel](00_GOUVERNANCE/STATUTS.md).
- **Vérifier ou contribuer :** [protocole de revue](REVIEW_PROTOCOL.md).
- **Ajouter une fiche :** [modèle de résultat](templates/RESULTAT.md).
- **Naviguer dans le dépôt :** [guide de lecture](00_GOUVERNANCE/GUIDE_LECTURE.md).

Le guide de lecture propose un parcours distinct pour les lecteurs, les personnes qui souhaitent vérifier un résultat et les contributeurs.

---

**Bienvenue sur Omega-pub. L'objectif est simple : rendre les travaux examinables, faciliter leur reproduction et accepter leur réfutation lorsqu'elle est justifiée.**
