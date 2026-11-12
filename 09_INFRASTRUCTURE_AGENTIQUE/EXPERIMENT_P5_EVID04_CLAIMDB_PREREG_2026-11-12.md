# P5-EVID-04 — gel du corpus externe ClaimDB et audit des preuves disponibles

**12 novembre 2026 — protocole enregistré AVANT tout prélèvement de la cohorte et avant toute analyse de ses annotations.**

## Objectif et source externe

Construire une passerelle reproductible entre l'architecture de provenance/observabilité Omega et des **affirmations annotées par un tiers**, au lieu des exemples construits ou des défaillances simulées.

Source : **ClaimDB**, Theologitis et al., ACL 2026, https://aclanthology.org/2026.acl-long.1589/ ; code/données https://github.com/claimdb/claimdb ; vue du dataset https://claimdb.github.io/ ; dépôt https://github.com/claimdb/claimdb/blob/e06c3a22cc14a8ef6858bb5d40bca7925241b98d/final-benchmark/test-public.jsonl . Commit source GELÉ `e06c3a22cc14a8ef6858bb5d40bca7925241b98d`, blob Git `a017545623508c0090cf2148716b8d26a6f8c337`. Licence annoncée par le dépôt source : **CC BY-SA 4.0**, avec attribution complète, lien de licence, préservation des mentions et indication des transformations. Le jeu complet public a 1000 lignes d'annotations (à contrôler lors de l'ingestion) et est **public, donc aucun holdout aveugle**.

### Préparation et règle d'échantillonnage fixe

Choisir **36 affirmations** du fichier public, par procédure déterministe reproductible, sans consulter les résultats des exemples choisis :
- 12 avec label `ENTAILED`, 12 `CONTRADICTED`, et 12 `NOT ENOUGH INFO` ;
- parmi les 12 `NOT ENOUGH INFO`, **4 de chaque catégorie** `OUT-OF-SCHEMA`, `COUNTERFACTUAL`, `SUBJECTIVE` ;
- pour chaque strate, classer par `rank = (claim_id * 2654435761 + bird_id * 1597334677) mod 2^32` ascendant, puis `claim_id` ascendant ;
- itérer les strates dans cet ordre fixe : ENTAILED, CONTRADICTED, OUT-OF-SCHEMA, COUNTERFACTUAL, SUBJECTIVE ; garder les premiers éléments dont `(db_name,bird_id)` n'a pas déjà été pris, jusqu'aux quotas. Ne jamais combler une strate insuffisante par des éléments d'une autre classe ; marquer `INCOMPLETE` si les quotas sont impossibles ;
- conserver `claim_id`, `bird_id`, `db_name`, `claim`, `extra_info`, label **réservé à l'évaluateur**, catégorie **réservée à l'évaluateur**. Ne pas déposer de données privées ni inventer de preuves.
- Inclure l'origine et le commit exact dans le manifeste, avec nombre d'éléments par label et base. Les claims anglais attribués sont reproduits seulement pour cet échantillon de 36, selon CC BY-SA 4.0. Aucun contenu d'autres auteurs n'est ajouté aux prompts sans sa source.

## Verrou d'observabilité et contrôle indépendant

**Les lignes du fichier ClaimDB sont des affirmations + des annotations**, pas une copie des lignes SQL sous-jacentes ni une preuve calculée. `db_name` et `bird_id` sont des identifiants de base/question, **pas des extraits de tables**. Ne jamais présenter `label` comme un verdict calculé par Omega, ni `extra_info` comme un résultat SQL exécuté.

Implémenter un modèle de certificat à trois niveaux :
- `ANNOTATION_PRESENT` : une étiquette de tiers existe et l'attribution est traçable ; cela ne fait **aucune** validation de la vérité.
- `WITNESS_AVAILABLE` : des lignes/tables d'une **base source épinglée et identifiée** existent et une requête exécutable est fournie avec résultat vérifiable ; le fichier d'affirmations **seul** ne le satisfait pas.
- `INDEPENDENT_REPRODUCTION` : deux méthodes de vérification effectivement réalisées, avec sources/résultats horodatés et dépendance déclarée ; deux lectures des mêmes données BIRD ne sont pas **deux fournisseurs indépendants**.

Un contrôleur autorisé à voir seulement `claim, extra_info, db_name, bird_id` et **aucun témoin SQL** doit répondre **`ABSTAIN_MISSING_EVIDENCE`** sur les 36 cas. Ne pas confondre `NOT ENOUGH INFO` (une *classe du dataset* portant sur les données cibles) avec `ABSTAIN_MISSING_EVIDENCE` (une *incapacité du contrôleur à consulter ces données*). Préserver la distinction.

## Critères, contrôles falsifiables, frontières

Tests requis : échantillon de 36 ID uniques ; quotas et catégories NEI ; provenance vers le commit source ; aucune ambiguïté des champs de preuve ; impossibilité de promouvoir un label caché en décision, rejet des témoins non sourcés, rejet des conflits de version/snapshot, détection de plusieurs affirmations issues d'une même base sans les traiter comme fournisseurs indépendants ; répétition déterministe du calcul de cohorte.

**Cette étape est une validation d'ingestion, de provenance et de conditions nécessaires à l'évaluation. Ce n'est PAS encore un benchmark de vérification de faits par Omega**, faute de base(s) de données BIRD disponibles et de requêtes SQL exécutées. Ne pas comparer artificiellement son exactitude à une méthode ayant accès aux vrais labels. Aucun succès d'adaptation générale n'est revendiqué.

Le corpus [FEVEROUS](https://fever.ai/dataset/feverous.html) possède des IDs de cellules/phrases Wikipédia et une licence CC BY-SA 3.0 ; sa référence complète de texte/table nécessite aussi des pages Wikipédia de l'archive. On le garde comme **deuxième voie documentée** mais pas comme résultat exécuté tant que les témoins élémentaires ne sont pas présents.

## Exécution / gouvernance

Script Python 3.12 standard et GitHub Actions sans API, vérification reproductible sur un échantillon réellement prélevé à la source. Dépôt public et attribution. Statut `REAL_THIRD_PARTY_ANNOTATIONS_PROVENANCE_ONLY_NO_WITNESS`. PR DRAFT, base #59, aucun changement de `main` et aucune promotion scientifique dans CORE avant revue.
