# P5-EVID-04 — corpus réel ClaimDB : import contrôlé, provenance et impossibilité de conclure sans témoin

**12 novembre 2026. Statut : ANNOTATIONS EXTERNES AUTHENTIFIÉES / ÉCHANTILLON REPRODUCTIBLE / AUCUNE VÉRIFICATION FACTUELLE INDÉPENDANTE EFFECTUÉE.**

## Provenance scientifique, licence et protocole gelé

**Corpus externe authentique :** Theologitis, Dammu, Shah & Suciu, *ClaimDB: A Fact Verification Benchmark over Large Structured Data*, ACL 2026, https://aclanthology.org/2026.acl-long.1589/ . Code et données des auteurs : https://github.com/claimdb/claimdb ; jeu du test public : https://github.com/claimdb/claimdb/blob/e06c3a22cc14a8ef6858bb5d40bca7925241b98d/final-benchmark/test-public.jsonl . Cette publication propose trois classes `ENTAILED / CONTRADICTED / NOT ENOUGH INFO`, et des affirmations concernant des bases relationnelles BIRD.

**Licence déclarée par les auteurs : [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/)**. Les 36 affirmations anglaises du sous-ensemble restent attribuées à Theologitis et al. et à leur dépôt ; la transformation est la sélection déterministe et l'ajout de métadonnées Omega. Les conditions de partage à l'identique s'appliquent ; ne pas réutiliser ce fichier sous licence incompatible.

- Protocole **publié avant sélection** : [EXPERIMENT_P5_EVID04_CLAIMDB_PREREG_2026-11-12.md](EXPERIMENT_P5_EVID04_CLAIMDB_PREREG_2026-11-12.md), commit `da9bf4316a7f0197b711cdddc9470498f4493b29`.
- Commit externe épinglé : `e06c3a22cc14a8ef6858bb5d40bca7925241b98d`.
- **Empreinte Git blob du fichier original** : `a017545623508c0090cf2148716b8d26a6f8c337`.
- SHA-256 du fichier original téléchargé dans GitHub Actions : `b87d7062307cfcf5ae862bf03bd7e82f7123ff39cf0b69d3dc5cc25caaaea810`.
- [GitHub Actions : SOURCE VALIDÉE](https://github.com/Abrasax63/Omega-pub/actions/runs/43228597484). **8 tests spécialisés réussis**, source complète réelle (1000 lignes) téléchargée depuis l'URL à commit fixe, empreinte vérifiée, **sélection des 36 cas exactement reproduite** à partir du fichier externe. La suite générale RCE a aussi réussi.
- [Sous-ensemble de 36 affirmations et provenance](prism/evid04_claimdb_public_sample_36.json), [code d'ingestion et garde-fou](prism/p5_evid04_claimdb_adapter.py), [tests négatifs](prism/test_p5_evid04_claimdb_adapter.py).

## Cohorte réellement prélevée

Sélection déterministe déclarée avant extraction : classe `ENTAILED` 12, `CONTRADICTED` 12, `NOT ENOUGH INFO` 12, ces dernières réparties **4 OUT-OF-SCHEMA / 4 COUNTERFACTUAL / 4 SUBJECTIVE**. 36 identifiants de claim distincts et 36 couples `(db_name,bird_id)` distincts ; **11 bases de données** représentées. Le jeu initial du test public contient **1000 exemples : 333 ENTAILED, 331 CONTRADICTED, 336 NOT ENOUGH INFO**. L'échantillon stratifié n'est pas représentatif de l'ensemble ni des 80 bases de la publication.

## Frontière de connaissance : une étiquette n'est pas une preuve

Les fichiers publics de **claims** contiennent `claim_id`, `bird_id`, `db_name`, `claim`, `extra_info`, `label`, `category`. **Ils ne contiennent pas dans chaque ligne l'ensemble des lignes de SQL exécutées établissant la vérité.**

La fonction `policy_input` **supprime le label et la catégorie** avant tout passage au contrôleur ; les étiquettes restent réservées à l'évaluateur. Sans ligne de base source, plan SQL exécuté ni témoin de correspondance entre requête et affirmation, le contrôleur donne **36/36 `ABSTAIN_MISSING_EVIDENCE`**. Cela ne veut **pas** dire que les 36 claims sont `NOT ENOUGH INFO` selon ClaimDB : seuls **12/36** portent cette étiquette de benchmark. Les 24 autres peuvent être tranchées avec les vraies tables, mais Omega ne les a **pas** consultées ici.

La preuve requiert au minimum : une base source réellement accessible et identifiée par empreinte, une requête *exécutée* qui parle de l'affirmation, un résultat traçable, le contrôle du champ et du périmètre de version, et la déclaration des dépendances. Notre adaptateur fournit une **interface de démonstration SQL en lecture seule** testée sur une base SQLite **synthétique locale** (distincte de ClaimDB). Deux requêtes donnant la même sortie sur **une seule base** constituent **deux méthodes de calcul et un seul fournisseur**, jamais deux sources factuelles indépendantes. Leur accord n'est **pas encore un certificat de vérification de la sémantique** de l'affirmation naturelle : un `SELECT` sans référence à une table est désormais explicitement rejeté et le résultat inclut `claim_semantics_independently_reviewed=false` et `independent_fact_verification=false`.

**Aucune véritable base BIRD de ClaimDB n'a été téléchargée dans cette PR ; aucune des 36 étiquettes n'a été recalculée par SQL.** Il n'existe donc aucun score de vérification d'Omega à annoncer.

### Contrôles adversariaux

Le test refuse : la divulgation du label au contrôleur, l'injection d'un faux reçu `verified=true`, une licence ou source non reconnue, une base SQLite modifiée après empreinte, deux requêtes identiques, un SQL d'écriture, une requête multicommande, une requête ne produisant pas un booléen et la divergence de deux résultats calculés. Ce sont des **tests logiciels et de sécurité épistémique**, pas des observations empiriques de défaillances de fournisseurs.

## Raccord avec les résultats de l'autre PR expérimentale OBS-04

La [PR #60, OBS-04](https://github.com/Abrasax63/Omega-pub/pull/60), **branche distincte**, exploite déjà un corpus plus large de **1000 paires de prédictions réelles** du même modèle GPT-5-mini, avec/sans accès aux outils SQL, publié par les auteurs ClaimDB. Son [run #43228587453](https://github.com/Abrasax63/Omega-pub/actions/runs/43228587453) a produit les résultats suivants : **357/1000** réponses correctes pour le mode sans outils, **827/1000** avec outils SQL, **692 désaccords** ; le filtre classique « publier seulement si les deux modes concordent » publie **308/1000**, dont **17 erreurs**. Les logs comprennent **5172 appels/outils et leurs sorties**, mais ceci n'est **pas un recalcul indépendant des données BIRD ni une inspection humaine de chaque requête**. Ce sont deux modes du **même modèle**, avec un **même fournisseur de benchmark**. De plus, aucune comparaison causale de temps, coût en tokens ou indépendance de sources ne résulte automatiquement de ces chiffres.

OBS-04 établit une **divergence empirique réellement observée** entre deux modes de travail ; EVID-04 établit une **frontière de preuve et une cohorte source reproductible**. Les deux PR peuvent être auditées séparément sans fusion préalable ni double comptage des résultats.

## Choix méthodologique pour la prochaine itération

**Ne pas prétendre qu'une note du benchmark mesure la vérité indépendamment.** Le prochain verrou est d'exécuter **deux requêtes SQL réellement différentes et sémantiquement vérifiées** sur une base source BIRD accessible et épinglée, de journaliser leur sortie ainsi que la revue de conformité à l'énoncé, puis de comparer les conclusions avec et sans filtre de provenance. Une même BIRD DB reste **une origine de données**, même si deux calculateurs s'y appliquent. Une autre voie documentée est [FEVEROUS](https://fever.ai/dataset/feverous.html), mais elle nécessite les unités de preuves Wikipédia (phrases/cellules) en plus des labels et pointeurs.

**ÉTABLI :** source 1000/1000 authentifiée, cohorte 36/36 reproduite, attribution et tests anti-fuite, abstention justifiée. **INDÉTERMINÉ :** factualité recalculée sur les 36 claims, apprentissage des dépendances entre vérificateurs et supériorité d'Omega.

**Gouvernance :** conserver PR DRAFT, `main` inchangée, aucune promotion CORE ni score de benchmark non justifié.
