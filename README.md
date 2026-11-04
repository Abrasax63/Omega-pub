# Omega-pub — Laboratoire public de recherche RAVI-2 / CCS / Omega-SRR

## Pourquoi ce dépôt existe

Omega-pub est un espace public destiné à présenter des travaux de recherche en cours ou déjà étudiés, à les rendre compréhensibles et vérifiables, puis à les soumettre à une critique extérieure.

L'objectif n'est pas de faire approuver des idées par principe. Il est de permettre à d'autres personnes de comprendre exactement ce qui est affirmé, de refaire les raisonnements et les calculs, de chercher des contre-exemples et, si nécessaire, de montrer qu'un résultat est faux ou trop général.

**La réfutation est une contribution utile. Une critique argumentée vaut davantage qu'une approbation sans vérification.**

Ce dépôt est un projet de recherche ouvert porté par ses contributeurs. Sa présence sur GitHub ne signifie ni qu'il est affilié à une université ou à un laboratoire institutionnel, ni que ses travaux ont fait l'objet d'une évaluation scientifique par les pairs. Toute validation doit être documentée dossier par dossier.

## Les trois axes présentés

### 1. RAVI-2 — Méthode de recherche et de vérification adversariale

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

### 2. CCS — Corpus de structures et de résultats associés

CCS désigne ici un axe de travaux et un corpus de structures mathématiques étudiées dans le cadre du projet.

Les dossiers publics devront préciser, pour chaque structure :
- sa définition exacte et sa notation ;
- le problème auquel elle répond ;
- les hypothèses nécessaires ;
- les résultats établis et ceux qui restent ouverts ;
- les preuves, calculs ou programmes permettant de les examiner ;
- les liens éventuels avec des résultats déjà publiés dans la littérature.

L'acronyme CCS ne doit pas être interprété comme une équivalence avec une théorie extérieure : son périmètre et ses définitions seront explicités dans les dossiers concernés. Aucun résultat ne sera présenté comme démontré sans justification consultable.

### 3. Omega-SRR — Axe de recherche distinct

Omega-SRR est un autre axe de travail conservé dans le projet. Il sera présenté selon ses propres définitions, sources et critères de validation.

Aucun lien mathématique entre Omega-SRR, CCS et RAVI-2 ne doit être supposé. Lorsqu'un rapprochement sera proposé, le dossier devra distinguer clairement :
- une analogie ou une piste d'interprétation ;
- une correspondance formelle définie ;
- une hypothèse testable ;
- un résultat effectivement démontré.

## Quels sujets peut-on examiner ?

Les dossiers seront publiés progressivement. Les travaux mathématiques déjà étudiés comprennent notamment des questions autour des systèmes dynamiques finis déterministes, de l'observation et de la perte d'information lors du passage d'une description microscopique à une description macroscopique.

Parmi les objets employés dans ces travaux figurent des espaces d'états observés, des relations macroscopiques et des comparaisons entre itérations d'une dynamique observée et observation de l'évolution microscopique. Les définitions précises, les domaines de validité et les résultats correspondants devront toujours être lus dans leurs fiches dédiées.

D'autres sujets exploratoires peuvent être présentés, mais ils seront séparés des résultats établis. Une question ouverte, y compris un problème majeur de mathématiques ou d'informatique théorique, ne sera jamais présentée comme résolue en l'absence d'une preuve vérifiable.

## Comment lire un résultat publié ici ?

Chaque résultat doit, dans la mesure du possible, être accompagné d'une fiche contenant :

- **Identifiant et version** : pour retrouver précisément l'énoncé examiné.
- **Énoncé** : ce qui est affirmé, sans ambiguïté.
- **Statut** : niveau réel de validation.
- **Périmètre** : ce qui est couvert et ce qui ne l'est pas.
- **Hypothèses** : conditions nécessaires.
- **Preuve ou certificat** : démonstration, calcul ou protocole reproductible.
- **Contre-tests** : cas limites et tentatives de réfutation.
- **Dépendances** : résultats utilisés par cet énoncé.
- **Provenance** : données, code, références et historique des modifications.

### Statuts épistémiques

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

Ces statuts ne sont pas des décorations : ils indiquent ce que le lecteur est en droit de conclure. Un calcul sur un nombre fini de cas ne démontre pas automatiquement une propriété générale. Une simulation n'est pas une démonstration. Une conjecture n'est pas un théorème.

## Vous souhaitez participer ?

Les contributions extérieures sont recherchées, qu'elles viennent de chercheurs, d'étudiants, de développeurs, de mathématiciens ou de lecteurs curieux.

Vous pouvez notamment :

- demander une définition ou une clarification ;
- signaler une erreur dans un raisonnement ;
- proposer un contre-exemple ;
- reproduire un calcul ou une simulation ;
- signaler un résultat déjà connu dans la littérature ;
- proposer une autre démonstration ;
- identifier une hypothèse oubliée ou une limite de validité.

**Pour commencer :**
1. Consultez le [protocole de revue](REVIEW_PROTOCOL.md).
2. Ouvrez une [discussion ou une question dans les Issues](../../issues).
3. Pour une correction documentée, proposez une [Pull Request](../../pulls).
4. Indiquez toujours le fichier, la version et l'énoncé précis que vous examinez.

Les contributions peuvent être rédigées en français ou en anglais. Les échanges doivent rester argumentés, respectueux et vérifiables.

## Comment les critiques seront-elles traitées ?

Une critique extérieure ne sera ni acceptée ni rejetée sur la seule autorité de son auteur. Elle sera examinée à partir de son contenu.

Lorsqu'une critique est pertinente, le traitement attendu est :
1. Identifier exactement l'affirmation contestée.
2. Reproduire indépendamment le raisonnement ou le calcul, si possible.
3. Tester le contre-exemple ou l'objection.
4. Déterminer si la conclusion est confirmée, limitée, corrigée ou réfutée.
5. Publier une réponse motivée et conserver l'historique.

Les auteurs d'un résultat peuvent répondre, mais leur réponse ne constitue pas à elle seule une validation indépendante. Le nombre d'étoiles, de commentaires ou de contributeurs ne constitue jamais une preuve.

## Organisation du dépôt

- `research/` — dossiers scientifiques et fiches de résultats.
- `reviews/` — rapports de vérification, critiques et réponses.
- `reproducibility/` — code, données partageables et instructions de reproduction.
- `templates/` — modèles de fiches et de rapports.

Les dossiers seront ajoutés après vérification de leur provenance, de leur contenu et de leur statut. Les archives privées ne sont pas automatiquement publiques : seules les pièces sélectionnées et autorisées seront transférées.

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

Une première migration documentaire est proposée dans la branche `migration/ravi2-ccs-public-2026-11-04` : 61 fichiers de briques/cartes, 5 documents méthodologiques, 31 audits/revues et 43 artefacts de reproductibilité RAVI-2/CCS. La base SQLite v33 et les mémoires de conversation ne sont pas incluses. Voir `MIGRATION_RAVI2_CCS_2026-11-04.md`.

Cette branche est soumise à revue avant toute intégration dans `main`. Le transfert ne vaut pas validation scientifique ; les statuts d'origine et les limites de réconciliation sont conservés.

---

**Bienvenue sur Omega-pub. L'objectif est simple : rendre les travaux examinables, faciliter leur reproduction et accepter leur réfutation lorsqu'elle est justifiée.**

### Reconstitutions documentaires — 4 novembre 2026

En complément des 61 cartes/fichiers annoncés ci-dessus, la branche contient maintenant **32 fiches reconstituées** sous `research/bricks/reconstructed/`, à partir des enregistrements scientifiques structurés de SQLite v33. Elles ne sont pas les fichiers Markdown originaux et sont explicitement marquées comme reconstitutions. Elles ne constituent ni une nouvelle certification ni une promotion des statuts. L'index détaillé est dans [research/bricks/INDEX_BRIQUES.md](research/bricks/INDEX_BRIQUES.md).


### Complément C4–L=2 (conditionnel)

Une fiche dédiée documente le témoin à 9 états et l'énumération exhaustive jusqu'à 8 états pour la coexistence des huit classes C4O. L'audit sémantique du 4 novembre a rapproché les contraintes du texte primaire V19 : le mauvais événement impose l'égalité des couleurs aux temps 0 et 1. Le résultat est **CALCUL EXACT sous la définition primaire** pour les huit classes cataloguées et leur minimum à 9 états. La preuve du lemme de localité L+2 a été reconstruite à partir de la structure P1–P4 et contrôlée exhaustivement sur 38 systèmes C4, 536 paires et 173 composantes sans divergence. La certification RAVI-2 finale reste à réexaminer pour la formalisation supplémentaire et la revue tierce. Voir [la fiche C4–L=2](research/bricks/C4-L2-COEXISTENCE-MINIMUM-9-CONDITIONAL.md), [le rapport d'audit](reviews/AUDIT_SEMANTIQUE_C4_L2_2026-11-04.md) et [le script indépendant](research/code/c4_l2_independent_local_audit_2026-11-04.py).


### Sources documentaires restaurées — 4 novembre 2026

Douze chemins de sources référencés dans SQLite v33 ont été retrouvés dans la Library : onze documents Markdown ont été transférés et un document DOCX est représenté par une extraction textuelle explicitement identifiée. Voir le [manifeste des sources](research/programs/README.md). La base SQLite elle-même reste privée et n'est pas incluse.

### Reproductibilité V19 C5–L=3

Les quatre entrées et les quatre sorties du contrôle C5–L=3 sont présentes sous [research/data/v19_c5/](research/data/v19_c5/README.md). Le script indépendant a été rejoué sur l'archive source et les exports de la branche ont passé les contrôles structurels de lignes, classes et témoins. L'exécution depuis un checkout GitHub propre a réussi via [GitHub Actions](https://github.com/Abrasax63/Omega-pub/actions/runs/41854918883). Les CSV transférés sont des exports textuels et ne revendiquent pas l'identité binaire des fichiers originaux.
