# Addendum — revue sémantique des 17 correspondances nominales SQLite v33

Date : 4 novembre 2026  
Périmètre : branche `migration/ravi2-ccs-public-2026-11-04`, PR #2.  
Base comparée : `RESEARCH_MEMORY.sqlite` v33, SHA-256 `ef3e9a0de51a44b30599f73f027829751a2eb144e4468175c0f290b5e0159bf4`.

## Méthode

Pour chacun des 17 candidats initialement classés `FILENAME_MATCH_ONLY_REVIEW_REQUIRED`, comparaison en lecture de :
1. l'identifiant, le titre, l'énoncé, le domaine et les hypothèses de la ligne `results` dans SQLite ;
2. le contenu de la carte correspondante sur la branche GitHub ;
3. les locateurs de preuve et de source enregistrés dans `evidence` / `result_sources`, confrontés à la section Provenance de la carte.

Les fichiers GitHub ont été relus individuellement. Les SHA indiqués ci-dessous sont les identifiants de blob Git retournés par GitHub (SHA-1 Git), **pas** des empreintes SHA-256 des fichiers source.

## Résultat

**17/17 correspondances de contenu confirmées** : identifiant et titre concordants, énoncé et domaine compatibles avec la ligne SQLite, et références de provenance de la carte cohérentes avec les locateurs source/audit/code présents dans SQLite.

| Résultat SQLite | Carte relue sur GitHub | Git blob SHA |
|---|---|---|
| `BR-OBS-BAD-01` | `research/bricks/BR-OBS-BAD-01_AFFINE_SIGNATURE.md` | `d7c22d06255ed39b5e69ecfc4e6a74447df1c81f` |
| `BR-OBS-CAP-01` | `research/bricks/BR-OBS-CAP-01_DYNAMIC_CAPACITY.md` | `5cb676c73d385b557aa5282e9514848383c196bc` |
| `BR-OBS-CAP-02` | `research/bricks/BR-OBS-CAP-02_SUPPORT_VS_WEIGHT.md` | `3b5f4a645de2520e7ddd461ef98dd116d3b5fbd7` |
| `BR-OBS-CAP-03` | `research/bricks/BR-OBS-CAP-03_FIBER_BOX_TU.md` | `e2db670f4f9458a848b7d8719f2a656dbfdab46b` |
| `BR-OBS-CIRCUIT-01` | `research/bricks/BR-OBS-CIRCUIT-01_2COVER_BIPARTITE.md` | `8f2b165a16b050423d340e06f3fd231edb6ed314` |
| `NS-CERT-E-10` | `research/bricks/NS-CERT-E-10.md` | `b0b805065e15dffc278a862c27b2c80d214875e6` |
| `NS-CERT-E-11` | `research/bricks/NS-CERT-E-11.md` | `b59f06b98b762526bcbb8b19ba05e17b7649dfab` |
| `NS-CERT-E-12` | `research/bricks/NS-CERT-E-12.md` | `be6b13c3e44471e5b63dd6acaec33418e10d5b5f` |
| `NS-CERT-E-13` | `research/bricks/NS-CERT-E-13.md` | `81d9bb273a1f1ec3e13c9912861b11d1b78e8e98` |
| `NS-CERT-E-14` | `research/bricks/NS-CERT-E-14.md` | `601cd1d4eebaaf4ea9c61deba28f12b94623b5fe` |
| `NS-CERT-E-15` | `research/bricks/NS-CERT-E-15.md` | `aa116d4adf083a3254b54118bbe3543d2a138a96` |
| `OBS-V19-BAD-FIBER2` | `research/bricks/OBS-V19-BAD-FIBER2_BRIQUE.md` | `6aeb31c4e8b139896e4d721e4b44b86add0e8fc6` |
| `OBS-V19-C5-CAPACITY` | `research/bricks/OBS-V19-C5-CAPACITY_BRIQUE.md` | `bc4b3eea112aeae4d7dcaac7bb79b52f0452d7d6` |
| `OBS-V19-COEX-REGION` | `research/bricks/OBS-V19-COEX-REGION_BRIQUE.md` | `ca222769a64c630c213235bbd47f303789f1de97` |
| `OBS-V19-COEX-SMALLMODEL` | `research/bricks/OBS-V19-COEX-SMALLMODEL_BRIQUE.md` | `022d58fd7ca0c0fe77e83335ffb8940c632a6db2` |
| `OBS-V19-FIRST-OBSTRUCTION11` | `research/bricks/OBS-V19-FIRST-OBSTRUCTION11_BRIQUE.md` | `0520f094003913ce0f53998409370af9459a2724` |
| `OBS-V19-N11-BADOBJECT` | `research/bricks/OBS-V19-N11-BADOBJECT_BRIQUE.md` | `e2ba7203487ea95bfda3f7d6acb6c420507462f7` |

## Références de provenance recoupées

- `BR-OBS-BAD-01` et `BR-OBS-CIRCUIT-01` : audit N11 et checker exact `v19_badobject_n11_exact.py`.
- `BR-OBS-CAP-01` et `BR-OBS-CAP-02` : audit de théorie des capacités V19 et catalogue des 85/70 ombres.
- `BR-OBS-CAP-03` : audit de région de coexistence V19 et code `v19_coexistence_region.py`.
- `NS-CERT-E-10` à `NS-CERT-E-15` : audits internes Navier–Stokes individuels ou groupés, identiques aux chemins cités dans SQLite.
- `OBS-V19-BAD-FIBER2` : audit, checker et régression fibre≤2.
- `OBS-V19-C5-CAPACITY` : audits multiplicité/capacité, code et sorties exactes.
- `OBS-V19-COEX-REGION` et `OBS-V19-FIRST-OBSTRUCTION11` : audit de coexistence, checker et sorties de projection.
- `OBS-V19-COEX-SMALLMODEL` : audit d'assemblage orienté, checker indépendant et audit de multiplicité.
- `OBS-V19-N11-BADOBJECT` : audit N11, checker, mappings historiques et sorties de reconstruction.

## Limite à conserver

Cette revue confirme la **correspondance de contenu et de provenance documentaire** des 17 cartes candidates. Elle ne crée pas rétroactivement une ligne `evidence` ni un lien `result_sources` de type carte individuelle dans SQLite v33. Le classement d'origine de la base demeure donc distinct : 26 liaisons explicites préexistantes ; 17 correspondances maintenant relues mais sans lien de carte explicite dans SQLite ; 42 résultats sans carte individuelle trouvée.

Aucune écriture dans SQLite n'a été effectuée. Aucun statut scientifique, aucune dépendance et aucune version de résultat n'ont été modifiés. Cette revue n'est pas une validation mathématique externe.
