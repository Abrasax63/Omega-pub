# Guide de lecture et de navigation

Ce guide indique où commencer selon ce que vous cherchez. L'index global reste la référence pour savoir quelles fiches de résultats existent réellement dans le dépôt.

## Accès rapides

- [Index global des résultats](INDEX_GLOBAL.md) — fiches présentes, statuts et liens directs.
- [Référentiel des statuts](STATUTS.md) — sens des statuts scientifiques et éditoriaux.
- [Architecture du dépôt](../ARCHITECTURE.md) — rôle des modules et règles communes.
- [Protocole de revue](../REVIEW_PROTOCOL.md) — examiner ou contester un résultat.
- [Modèle de fiche](../templates/RESULTAT.md) — structure à utiliser pour documenter un résultat.

## Choisir son parcours

### Je veux consulter un résultat

1. Ouvrir l'[index global](INDEX_GLOBAL.md).
2. Suivre le lien de la fiche.
3. Lire d'abord l'énoncé exact, le périmètre et les hypothèses.
4. Vérifier le statut scientifique **et** le statut de publication.
5. Consulter les preuves, contre-tests, dépendances et sources.

Une mention « DÉMONTRÉ » décrit le statut scientifique rapporté par la fiche ; elle ne signifie pas automatiquement que tout le dossier justificatif est reproduit dans cette version publique.

### Je veux vérifier ou réfuter un résultat

1. Identifier l'ID et la version exacte dans l'index.
2. Consulter les hypothèses et les cas exclus.
3. Refaire indépendamment l'étape décisive ou chercher un contre-exemple minimal.
4. Décrire précisément les données, le raisonnement ou le programme utilisés.
5. Ouvrir une [issue](../../issues) ou proposer une [pull request](../../pulls), en citant le fichier et la version examinés.

Une objection documentée est conservée même si elle est ensuite réfutée. Une réponse de l'auteur ne remplace pas une vérification indépendante.

### Je veux ajouter un résultat

1. Choisir le module correspondant au périmètre scientifique.
2. Copier le [modèle de fiche](../templates/RESULTAT.md).
3. Attribuer un identifiant stable et une version.
4. Renseigner l'énoncé, les hypothèses, la justification, les contre-tests, les dépendances et la provenance.
5. Laisser le statut **INDÉTERMINÉ** si les éléments ne permettent pas de conclure.
6. Ajouter la fiche à l'index seulement lorsqu'elle existe dans le dépôt.

Ne pas publier de contenu privé, de données personnelles ou de secrets. Ne pas présenter une exécution comme réalisée si elle ne l'a pas été.

## Comprendre les deux statuts

- **Statut scientifique** : niveau de justification de l'énoncé (DÉMONTRÉ, CALCUL EXACT, SIMULÉ, EMPIRIQUE, CONJECTURÉ, RÉFUTÉ, INDÉTERMINÉ ou À RÉEXAMINER).
- **Statut de publication** : état du dossier dans le dépôt (PUBLIC, EXPÉRIMENTAL, PRIVÉ ou ARCHIVÉ).

Ces deux axes sont indépendants. Par exemple, une fiche peut rapporter un résultat scientifiquement démontré tout en restant publiée à titre expérimental parce que son audit source n'est pas encore reproduit dans le dépôt.

## Règle de navigation

Le chemin normal est :

**Index → fiche de résultat → preuve / calcul / données → contre-tests → dépendances et sources.**

Les fichiers de gouvernance expliquent comment lire et contribuer ; ils ne constituent pas des preuves scientifiques.
