# Inventaire exhaustif des artefacts RAVI-2 / CCS — branche historique — 9 novembre 2026

**Dépôt :** `Abrasax63/Omega-pub`  
**Branche source :** `migration/ravi2-ccs-public-2026-11-04`  
**Commit source inspecté :** `2f71a6b8ed03914c0b5d308520d30e0133d9e9ad`  
**Méthode :** lecture de l'arbre Git récursif complet (`truncated=false`), sans exécuter les scripts ni modifier la branche source.

## 1. Résultat de l'inventaire

L'arbre source contient **185 fichiers** dans les trois périmètres documentaires ciblés :

- `research/bricks/` : **94** fichiers, dont **32** sous le sous-dossier `reconstructed/`.
- `reviews/` : **47** fichiers.
- `reproducibility/` : **44** fichiers.

Le total de 32 reconstitutions est confirmé par le nombre de fichiers sous `research/bricks/reconstructed/`. Ce sont des reconstitutions documentaires et non 32 preuves originales retrouvées.

## 2. Contrôle d'intégration dans les branches

Comparaison de l'ensemble des 185 blobs source (SHA Git) avec les arbres complets des branches `maintenance/reconciliation-bibliotheque-2026-11-05` et `architecture/memoire-agentique-native-2026-11-05` au moment du contrôle :

- **0/185 chemin identique** dans la branche maintenance.
- **0/185 blob identique** (SHA Git) retrouvé dans la branche maintenance.
- **0/185 chemin identique** dans la branche architecture.
- **0/185 blob identique** (SHA Git) retrouvé dans la branche architecture.

C'est un constat sur les deux arbres et les 185 artefacts de ces trois dossiers, pas sur d'éventuelles copies renommées ou extraits incorporés dans d'autres documents. Le registre initial créé précédemment est un nouvel artefact d'inventaire, pas le transfert du corpus.

## 3. Convention de lecture des empreintes

La colonne SHA est l'identifiant du blob Git fourni par l'arbre source. Elle permet de retrouver et comparer le contenu dans Git. Elle ne constitue ni une empreinte SHA-256 locale des sources originales, ni un certificat de correction mathématique.

Les classifications automatiques ci-dessous portent uniquement sur l'emplacement du fichier : `RECONSTITUTION` signifie que le chemin est sous `reconstructed/`; `BRIQUE` désigne le reste de `research/bricks/`; `REVUE_AUDIT` désigne `reviews/`; `REPRODUCTIBILITE` désigne `reproducibility/`. Aucun statut scientifique n'est inféré du nom du fichier.

## 4. Fiches et index de briques

| Chemin | Type documentaire | Taille (octets) | SHA Git du blob |
|---|---|---:|---|
| `research/bricks/BR-ACC-01_CLOTURE_ACCESSIBLE.md` | BRIQUE | 1575 | `006a57586ae1e7f100c48d7bc4f159723c2b3352` |
| `research/bricks/BR-ACC-STATE-COMMUTE-01_BRIQUE.md` | BRIQUE | 3117 | `c4c89930f075983e085da5e38c956f12dc61186e` |
| `research/bricks/BR-AFFINE-GAUGE-CORE_BRIQUE.md` | BRIQUE | 1615 | `798ce8f646d9d283b7244410522c607c27f75f4c` |
| `research/bricks/BR-AFFINE-GAUGE-GLUE_BRIQUE.md` | BRIQUE | 2042 | `1520fd18f1f18bb85d9fe76abdff07712e687044` |
| `research/bricks/BR-AFFINE-GROUP-CORE_BRIQUE.md` | BRIQUE | 1627 | `6838a2e95ab64ae53406e4fc75abc267e4366745` |
| `research/bricks/BR-AFFINE-TREE-CORE_BRIQUE.md` | BRIQUE | 2047 | `ff8b35f41aca9de2d362f0bf4852f133527a479d` |
| `research/bricks/BR-AFFINE-TREE-GLUE_BRIQUE.md` | BRIQUE | 2588 | `e4145722b06102e104ddf6ff8faa027d3663d0e6` |
| `research/bricks/BR-CTRL-01_CERTIFICAT_MEMOIRE_INFINIE.md` | BRIQUE | 1839 | `3d52e5372f2eaecc6c66d960b0601e727325e2b2` |
| `research/bricks/BR-DESC-01_SUFFISANCE_VS_AUTONOMIE.md` | BRIQUE | 1970 | `fb584f81bdd285da480df1eafacea75d0ab77c19` |
| `research/bricks/BR-DESC-02_MARGINALE_VS_ORDRE_TEMPOREL.md` | BRIQUE | 2452 | `81a0d346c2299850c1ffd2e26783a9b983a38933` |
| `research/bricks/BR-MEALY-HELLY-01_BRIQUE.md` | BRIQUE | 1622 | `389957f14632fb253434202a46727ace8688b512` |
| `research/bricks/BR-OBS-01_ADAPTATIF_VS_PREDEFINI.md` | BRIQUE | 1550 | `aa8425b35c8d9ad2175b9f05d42d4b624f51e75d` |
| `research/bricks/BR-OBS-BAD-01_AFFINE_SIGNATURE.md` | BRIQUE | 2774 | `d7c22d06255ed39b5e69ecfc4e6a74447df1c81f` |
| `research/bricks/BR-OBS-CAP-01_DYNAMIC_CAPACITY.md` | BRIQUE | 3421 | `5cb676c73d385b557aa5282e9514848383c196bc` |
| `research/bricks/BR-OBS-CAP-02_SUPPORT_VS_WEIGHT.md` | BRIQUE | 2536 | `3b5f4a645de2520e7ddd461ef98dd116d3b5fbd7` |
| `research/bricks/BR-OBS-CAP-03_FIBER_BOX_TU.md` | BRIQUE | 3225 | `e2db670f4f9458a848b7d8719f2a656dbfdab46b` |
| `research/bricks/BR-OBS-CIRCUIT-01_2COVER_BIPARTITE.md` | BRIQUE | 2186 | `8f2b165a16b050423d340e06f3fd231edb6ed314` |
| `research/bricks/BR-OBS-KRYLOV-01_GENERATOR_RECOVERY.md` | BRIQUE | 2140 | `de2ecdd2ea5ded00261e92c77daaf260fc25189b` |
| `research/bricks/BR-OBS-REVEAL-KERNEL_BRIQUE.md` | BRIQUE | 1938 | `6c7dca87aab78f5986569daf48f0bd170b42dca1` |
| `research/bricks/BR-Q-01_AMBIGUITE_PROCESSUS_INSTRUMENTS.md` | BRIQUE | 1515 | `f2ffb7101f8e336fb4e81910b4300dc84e0832aa` |
| `research/bricks/BR-Q-PRED-HIDDEN-01_BRIQUE.md` | BRIQUE | 6010 | `d90deb72f530d626f1d2c05b40578e7e72258a96` |
| `research/bricks/BR-Q-SWAP-MEM-01_BRIQUE.md` | BRIQUE | 1739 | `2ba76078af4e1e20ccd7c3b52bf06f20eb4cfffa` |
| `research/bricks/BR-R90-01_NOYAUX_PERIODES.md` | BRIQUE | 984 | `5f05b98f301af8331c5fa0fe19448385c5c983fb` |
| `research/bricks/BR-R90-02_MAJORITY_WALSH.md` | BRIQUE | 1052 | `4319a4b78b8218b7aa1795245edbbd532ce92c8b` |
| `research/bricks/BR-STATE-01_ETATS_PREDICTIFS_REPARATION.md` | BRIQUE | 2086 | `b7f79410a589dd8ba62a997860c924593e85a73c` |
| `research/bricks/BR-STATE-COST-01_BRIQUE.md` | BRIQUE | 1519 | `428f7056a5345c5aa826042ed3ba9ace762157d6` |
| `research/bricks/BR-TIME-01_RESOLUTION_SANS_FLECHE.md` | BRIQUE | 1190 | `9c17df58ecda9940f39024bfd532ec2b1d29f156` |
| `research/bricks/BR-TIME-FACTOR-COMPLEX-01_BRIQUE.md` | BRIQUE | 3428 | `22b3edb62a5e9864af0062604746a236c652d8f9` |
| `research/bricks/BR-TIME-FINDET-BRIDGE-01_BRIQUE.md` | BRIQUE | 3141 | `b45f06100815bed0ebbcee3aea666dad93ed4d1b` |
| `research/bricks/BR-WORD-SINGLE-GAP-COMPLEX-01_BRIQUE.md` | BRIQUE | 4873 | `e52a7247c4aa761aa7ce09e504c89d307c06f12f` |
| `research/bricks/BR-WORD-TWO-EQUAL-GAPS-COMPLEX-01_BRIQUE.md` | BRIQUE | 1836 | `f6808ee1fad8ba6215695e2bd77867067660c8d4` |
| `research/bricks/C4-L2-COEXISTENCE-MINIMUM-9-CONDITIONAL.md` | BRIQUE | 9404 | `a5ae083bc1edc0fdb553f781eaeb31620d1b5dba` |
| `research/bricks/DESC-CLIP-01_BRIQUE.md` | BRIQUE | 1927 | `3bb00f533e833482baf8f81374bc3a223f98b7a4` |
| `research/bricks/DET-FIN-01_BRIQUE.md` | BRIQUE | 2029 | `2d320dc803533e75b77784aa2af3910eac25edd1` |
| `research/bricks/GLOBAL-LOC-01.md` | BRIQUE | 580 | `20ee97227215e02cc8f4d713fe79f4df71c22139` |
| `research/bricks/INDEX_BRIQUES.md` | BRIQUE | 28212 | `cca1a7416d138a0cdab735e48830cf6449217651` |
| `research/bricks/NAVIER_STOKES_BRIQUES_CERT_E_VERROUILLEES_2026-10-15.md` | BRIQUE | 4572 | `9b5e9fe6fca3466ab48f6d7fc5dfd23935343181` |
| `research/bricks/NAVIER_STOKES_BRIQUES_RAVI2_2026-10-15.md` | BRIQUE | 9170 | `558866c6ac91ea37b25339ba4b8a2f3f87b4ab0c` |
| `research/bricks/NS-CERT-E-10.md` | BRIQUE | 871 | `b0b805065e15dffc278a862c27b2c80d214875e6` |
| `research/bricks/NS-CERT-E-11.md` | BRIQUE | 1049 | `b59f06b98b762526bcbb8b19ba05e17b7649dfab` |
| `research/bricks/NS-CERT-E-12.md` | BRIQUE | 720 | `be6b13c3e44471e5b63dd6acaec33418e10d5b5f` |
| `research/bricks/NS-CERT-E-13.md` | BRIQUE | 896 | `81d9bb273a1f1ec3e13c9912861b11d1b78e8e98` |
| `research/bricks/NS-CERT-E-14.md` | BRIQUE | 815 | `601cd1d4eebaaf4ea9c61deba28f12b94623b5fe` |
| `research/bricks/NS-CERT-E-15.md` | BRIQUE | 741 | `aa116d4adf083a3254b54118bbe3543d2a138a96` |
| `research/bricks/NS-P55-COMP-01.md` | BRIQUE | 640 | `498cc5670c9efc235509ad1e04e5c90dbaf3b5ab` |
| `research/bricks/OBS-AFFINE-GROUP-CORE-VALIDATION_BRIQUE.md` | BRIQUE | 1915 | `f5f96d26fbce5e6fb5f8b45aa9d361a96d648d07` |
| `research/bricks/OBS-RESTRICT-AFFINE_BRIQUE.md` | BRIQUE | 1786 | `cfeb3e0fededf0de0f0b5dba8ceef9cbe9d99b86` |
| `research/bricks/OBS-RESTRICT-FORCED-QUOTIENT_BRIQUE.md` | BRIQUE | 2093 | `6306c81ae37038d4748d4e4f84eba3ea03180870` |
| `research/bricks/OBS-RESTRICT-MULTIMOMENT_BRIQUE.md` | BRIQUE | 1916 | `055fd39b7def5f49ebf656c93e50ed8ee047f24d` |
| `research/bricks/OBS-V19-BAD-FIBER2_BRIQUE.md` | BRIQUE | 6112 | `6aeb31c4e8b139896e4d721e4b44b86add0e8fc6` |
| `research/bricks/OBS-V19-C5-CAPACITY_BRIQUE.md` | BRIQUE | 3664 | `bc4b3eea112aeae4d7dcaac7bb79b52f0452d7d6` |
| `research/bricks/OBS-V19-COEX-REGION_BRIQUE.md` | BRIQUE | 4320 | `ca222769a64c630c213235bbd47f303789f1de97` |
| `research/bricks/OBS-V19-COEX-SMALLMODEL_BRIQUE.md` | BRIQUE | 3093 | `022d58fd7ca0c0fe77e83335ffb8940c632a6db2` |
| `research/bricks/OBS-V19-FIRST-OBSTRUCTION11_BRIQUE.md` | BRIQUE | 3564 | `0520f094003913ce0f53998409370af9459a2724` |
| `research/bricks/OBS-V19-N11-BADOBJECT_BRIQUE.md` | BRIQUE | 3924 | `e2ba7203487ea95bfda3f7d6acb6c420507462f7` |
| `research/bricks/OBS-V19-N11-MOMENT-GRAM_BRIQUE.md` | BRIQUE | 1984 | `b00d2c50740c352c7f560556f49519ca173b8215` |
| `research/bricks/OBS-V19-N11-THIRD-ORDER_BRIQUE.md` | BRIQUE | 2175 | `6350cf79fb40dcac70200aeb1e995d31e3135225` |
| `research/bricks/OSC-ITER-01.md` | BRIQUE | 619 | `e1a57ecd4bc8894a252d7232c4055eeb91459c47` |
| `research/bricks/OSC-REAL-01.md` | BRIQUE | 543 | `e56af60421af524cda947cba2978c860596307e0` |
| `research/bricks/README.md` | BRIQUE | 152 | `6f22f25921882cabaac62e330d5131632cdcdcf0` |
| `research/bricks/SCH-POLY-CLOSURE-01_BRIQUE.md` | BRIQUE | 1893 | `0458e97a04ce2d02b8c93be6378b0763844db7a3` |
| `research/bricks/SCH-SEXTIC-PARITY-01_BRIQUE.md` | BRIQUE | 1446 | `4cc8d8c167c6098c7cf4778a5e0850a425081692` |
| `research/bricks/reconstructed/APP-OBS-SPARSE-DISJOINT_RECONSTITUTION.md` | RECONSTITUTION | 3883 | `64c1bede0a0c324da40875cd484ef955bd22a962` |
| `research/bricks/reconstructed/DELTA-P3-N5_RECONSTITUTION.md` | RECONSTITUTION | 2552 | `f8f7105bec4b99879a44adcd45b045d3b2bd8ff3` |
| `research/bricks/reconstructed/DELTA-SPECTRUM-CLASS_RECONSTITUTION.md` | RECONSTITUTION | 3060 | `282d034d41141db156373286373b077d38315e46` |
| `research/bricks/reconstructed/DESC-SUM-01_RECONSTITUTION.md` | RECONSTITUTION | 4974 | `36235f7e7110654f5c0aaa1839a803398f4f98fc` |
| `research/bricks/reconstructed/EXT-OAI-MARG-REPAIR_RECONSTITUTION.md` | RECONSTITUTION | 4128 | `a1700bcd069d600b40a4308e94ff14c47c761836` |
| `research/bricks/reconstructed/EXT-OAI-MATCH-CORNER_RECONSTITUTION.md` | RECONSTITUTION | 3721 | `3c94173f78ebe55f9f7bec055b31839820d45cc8` |
| `research/bricks/reconstructed/EXT-OAI-MATCH-RANK_RECONSTITUTION.md` | RECONSTITUTION | 4040 | `e8d3900bd63d1585b2b551913297635283333c2e` |
| `research/bricks/reconstructed/EXT-OAI-REL-CORNER_RECONSTITUTION.md` | RECONSTITUTION | 3143 | `e20fd9069d2e6449c8fcae3f372ae246dcbcf646` |
| `research/bricks/reconstructed/EXT-OAI-REL-SELECT_RECONSTITUTION.md` | RECONSTITUTION | 3665 | `4938dff8ee6e60fd3c0e8888490500cfb2b33a71` |
| `research/bricks/reconstructed/EXT-OAI-UNIT-LIFT_RECONSTITUTION.md` | RECONSTITUTION | 3709 | `7d34aaafaf2110c0bf7c6cb4c99e7ada34eab637` |
| `research/bricks/reconstructed/OBS-M27-BINARY_RECONSTITUTION.md` | RECONSTITUTION | 4400 | `fddaf0725e08635d6b70fde89a4264f11244c14b` |
| `research/bricks/reconstructed/OBS-M27-CONFLICT_RECONSTITUTION.md` | RECONSTITUTION | 4630 | `fa772473c86cc53ed14cca070093ea487e00ad82` |
| `research/bricks/reconstructed/OBS-M27-FERTILE_RECONSTITUTION.md` | RECONSTITUTION | 4784 | `429227f3604cdc2270e3867671594b38b76ca081` |
| `research/bricks/reconstructed/OBS-M27-SPECTRUM_RECONSTITUTION.md` | RECONSTITUTION | 4686 | `6693bfdf83d708f2513e39c9fd4fde1a8f59f875` |
| `research/bricks/reconstructed/OBS-RESTRICT-COUNT_RECONSTITUTION.md` | RECONSTITUTION | 4499 | `87468306569381cc38566a4084124dd44bb146c6` |
| `research/bricks/reconstructed/OBS-RESTRICT-GREEDY_RECONSTITUTION.md` | RECONSTITUTION | 3545 | `156081acf5d989b7272041cf0afe3144f46bfbe1` |
| `research/bricks/reconstructed/OBS-RESTRICT-OVERLAP_RECONSTITUTION.md` | RECONSTITUTION | 4240 | `ac022feb475a7a8b8324760673de301b1a6ae579` |
| `research/bricks/reconstructed/OBS-RESTRICT-PROFILE_RECONSTITUTION.md` | RECONSTITUTION | 3706 | `d3e273760b01469f6ae7342b159cda53474fcba7` |
| `research/bricks/reconstructed/OBS-V19-C5-13_RECONSTITUTION.md` | RECONSTITUTION | 6887 | `ebb0ca081d71f79ac30854bb79301a762fc8f3df` |
| `research/bricks/reconstructed/OBS-V19-C5-ORIENTED14_RECONSTITUTION.md` | RECONSTITUTION | 5008 | `ed1b7fa3d310252eeda690177fba4a9607cc3551` |
| `research/bricks/reconstructed/OBS-V19-FORCED-P4_RECONSTITUTION.md` | RECONSTITUTION | 5067 | `0a70b998ee83dfec2d7b3cae3bb54e0e67204759` |
| `research/bricks/reconstructed/OBS-V19-GAMMA-CONNECTED_RECONSTITUTION.md` | RECONSTITUTION | 3282 | `fd031552de1a6dd6eaca0b31e0dbfecf87678dc1` |
| `research/bricks/reconstructed/OBS-V19-LOCAL-L2_RECONSTITUTION.md` | RECONSTITUTION | 5121 | `460869f7b0e629b4304ca3ca6294adbbc93c3f0d` |
| `research/bricks/reconstructed/OBS-V19-PAIR-COMPLETE14_RECONSTITUTION.md` | RECONSTITUTION | 5377 | `039b3c00b24a48e2bb51d9e72421a3a0f0651fdc` |
| `research/bricks/reconstructed/OBS-V19-TRIPLE-COMPLETE13_RECONSTITUTION.md` | RECONSTITUTION | 5427 | `aa1b7c8e08e63dccb9f75461973632cce7a4b63e` |
| `research/bricks/reconstructed/OBS-V19-UNIVERSAL10_RECONSTITUTION.md` | RECONSTITUTION | 4150 | `934ab7348691af75433dfdfe4b7a411d67920182` |
| `research/bricks/reconstructed/OBS-V8-FACT-INF_RECONSTITUTION.md` | RECONSTITUTION | 2940 | `ee1cede65234cf4405fa6fbb4052b2fc29068fda` |
| `research/bricks/reconstructed/OBS-V9-RANK_RECONSTITUTION.md` | RECONSTITUTION | 2641 | `84fbcb568092caa0c88d4521a7a1421a01307bfe` |
| `research/bricks/reconstructed/OBS-V9-STAB-N1_RECONSTITUTION.md` | RECONSTITUTION | 2538 | `e68c5bbbe964b4db9d40e49eaa63b4e946012dee` |
| `research/bricks/reconstructed/OMEGA-O41-DET-V11_RECONSTITUTION.md` | RECONSTITUTION | 4195 | `ec36e52dd5d0405ea9ea7b250ea3736e2e416774` |
| `research/bricks/reconstructed/Q-RQ4-COMMON-RANK_RECONSTITUTION.md` | RECONSTITUTION | 5124 | `9faebd51b685a057bb8022841c32c10805929b1d` |
| `research/bricks/reconstructed/Q-RQ4-PAULI-ROBUST_RECONSTITUTION.md` | RECONSTITUTION | 4837 | `4c069243284a747036f6908c1e2b067aefedfdec` |

## 5. Revues, certificats documentaires et audits

| Chemin | Type documentaire | Taille (octets) | SHA Git du blob |
|---|---|---:|---|
| `reviews/ADDENDUM_REVUE_17_CARTES_CANDIDATES_2026-11-04.md` | REVUE_AUDIT | 4898 | `afd29fa8660385091f295c231945bf0c4c666b76` |
| `reviews/AUDIT_ACC_STATE_COMMUTATION_2026-10-20.md` | REVUE_AUDIT | 3448 | `b19cbba729cbe80692e4c212ac85f71ece194329` |
| `reviews/AUDIT_CERTIFICATION_NAVIER_STOKES_2026-10-15.md` | REVUE_AUDIT | 6681 | `b866cc53cb47711af1c99a62a113190a709558dc` |
| `reviews/AUDIT_COMMIT_RATTRAPAGE_2026-10-19.md` | REVUE_AUDIT | 6236 | `adf23b54e85211756cd644620b41e63db2f64a28` |
| `reviews/AUDIT_CORRESPONDANCE_NS_PROP55_LEIREN_2026-10-15.md` | REVUE_AUDIT | 2637 | `6665ea3f5df5e0fe31c7b3db22c754e9a41518eb` |
| `reviews/AUDIT_COUVERTURE_HISTORIQUE_2026-11-04.md` | REVUE_AUDIT | 13849 | `fafd08523bf48276dfe07c4ea17c01471d14caa5` |
| `reviews/AUDIT_FINAL_PR2_2026-11-04.md` | REVUE_AUDIT | 8181 | `2aca06785c94b609ed6f998a16bc7b0c38b6e959` |
| `reviews/AUDIT_INDEPENDANT_V19_C5_L3_2026-11-04.md` | REVUE_AUDIT | 10467 | `68f8f311cc8efe943623876b19e5b88d50cfa7d4` |
| `reviews/AUDIT_MATHEMATIQUE_ET_BIBLIOGRAPHIQUE.md` | REVUE_AUDIT | 19688 | `c1038642c6da80c00741cf9b4b80db8b75dbecd7` |
| `reviews/AUDIT_Q_PREDICTIVE_HIDDEN_2026-10-20.md` | REVUE_AUDIT | 5421 | `929d57be88d8d9a52aac6913f999d53bb57e28a1` |
| `reviews/AUDIT_RAPPROCHEMENT_32_CARTES_2026-11-04.md` | REVUE_AUDIT | 9710 | `ad41325118325f58dd23fb6c58d267de9d008638` |
| `reviews/AUDIT_RATTRAPAGE_BRIQUES_2026-10-19.md` | REVUE_AUDIT | 7117 | `5e0fd197e5de838f4fde048b267d708922ee7a6a` |
| `reviews/AUDIT_SEMANTIQUE_C4_L2_2026-11-04.md` | REVUE_AUDIT | 13929 | `83f919f4eae7427fc8c767794ad18447712e3372` |
| `reviews/AUDIT_SINGLE_GAP_FACTOR_COMPLEXITY_2026-10-19.md` | REVUE_AUDIT | 6486 | `05200a99df13ebd91989251b6185e7c0af4ffe2b` |
| `reviews/AUDIT_TIME_PREDICTIVE_COMPLEXITY_2026-10-19.md` | REVUE_AUDIT | 4820 | `078552af23a4fa1ba5644c2e925af4ed2a22b954` |
| `reviews/AUDIT_TRACABILITE_32_RECONSTITUTIONS_2026-11-04.md` | REVUE_AUDIT | 6857 | `b09af559bb0f6cbd4de44c2fe3739de17c7ba2f3` |
| `reviews/AUDIT_TRACABILITE_SYNCHRONISATION_RAVI2_2026-10-27.md` | REVUE_AUDIT | 4884 | `8cea972bd8d4d08968e79c4a35ed991e20398aa3` |
| `reviews/CERTIFICAT_METHODE_RAVI2_SOURCE_2026-10-27.md` | REVUE_AUDIT | 2094 | `9806d39a1ea7f2a90d9e74810fc6955122299488` |
| `reviews/INVENTAIRE_SOURCES_32_CARTES_MANQUANTES_2026-11-04.md` | REVUE_AUDIT | 7647 | `c3d9812fe1101d256f05cd072c7bff9799a5e4f7` |
| `reviews/RAVI2_CONJECTURE_GRAPH_V01_AUDIT.md` | REVUE_AUDIT | 5167 | `b65135ff5f21ea8652bc323c1b38008af3492d8b` |
| `reviews/RAVI2_CONSOLIDATION_AUDIT_2026-11-04.md` | REVUE_AUDIT | 3922 | `3e5045fc0d09b4b85ab86c71d01420de6ed72459` |
| `reviews/RAVI2_DISCOVERY_V01_2026-10-19.md` | REVUE_AUDIT | 15174 | `348e71d723412a8713314abfd596357eade42537` |
| `reviews/RAVI2_DISCOVERY_V02_AUDIT.md` | REVUE_AUDIT | 4148 | `70291b1952645b624985df68760b4f87eadae869` |
| `reviews/RAVI2_PARALLEL_CONTRACT_TEST_2026-10-16.md` | REVUE_AUDIT | 2708 | `ba42bc7853e7ef33bc1cabc5bf5c3e490143397f` |
| `reviews/RAVI2_STRICT_CONTRACTS_PHASE1_2026-10-16.md` | REVUE_AUDIT | 5930 | `65865cd51737bd98fe3ce6a9a39020a65254ee12` |
| `reviews/RAVI2_STRICT_CONTRACTS_PHASE2_2026-10-16.md` | REVUE_AUDIT | 3753 | `1dfe235da1755d3d20c5939bb2dc0b394effaa88` |
| `reviews/RAVI2_STRICT_CONTRACTS_PHASE3_2026-10-16.md` | REVUE_AUDIT | 3489 | `7800cfc7e397f8d0f8327b0dbef129da255feb28` |
| `reviews/RAVI2_STRICT_CONTRACTS_PHASE4_2026-10-16.md` | REVUE_AUDIT | 1683 | `2e317f35bd8014cc526686c4c844a07bec5a1ec3` |
| `reviews/RAVI2_STRICT_CONTRACTS_PHASE5_2026-10-16.md` | REVUE_AUDIT | 1601 | `0fcd60a36ba511d6b365f0d6e47e058e1f784b91` |
| `reviews/RAVI2_STRUCTURAL_GRAPH_V02_AUDIT.md` | REVUE_AUDIT | 5844 | `f1ac228fcdd1db8d1689d818eb1a114bfdb9236a` |
| `reviews/RECHERCHE_ELARGIE_CARTES_ORIGINALES_2026-11-04.md` | REVUE_AUDIT | 2254 | `d88030fc7eb1da7a0caebe534158ee9587c38dfb` |
| `reviews/RECONCILIATION_CARTES_RESULTATS_SQLITE_V33_2026-11-04.md` | REVUE_AUDIT | 7306 | `b48b5b5fc448942e663b8e4f0f6bca925c20aed9` |
| `reviews/RECONCILIATION_DETAIL_42_RESULTATS_SQLITE_V33_2026-11-04.md` | REVUE_AUDIT | 13433 | `fc5809cafb64959682504a113fb5e87d39bd39c1` |
| `reviews/RECUPERATION_APPROFONDIE_V19_MEALY_DELTA_2026-11-04.md` | REVUE_AUDIT | 6391 | `b0cddfb1c2805156979c132d65a26fb6e154f7b3` |
| `reviews/RECUPERATION_HISTORIQUE_32_RESULTATS_2026-11-04.md` | REVUE_AUDIT | 6889 | `5221f3fa3605924f7236bde0ad38d967795b22a9` |
| `reviews/REGISTRE_RECUPERATION_SOURCES_SHA256_2026-11-04.md` | REVUE_AUDIT | 4154 | `36a7cd8031fab701d332e3a5e4e60e4e789c03cd` |
| `reviews/REJEU_INDEPENDANT_V19_MEALY_2026-11-04.md` | REVUE_AUDIT | 8363 | `63c4dea39863d62352bc2fa56f918c5537742c12` |
| `reviews/REVUE_INDEPENDANTE_TWO_EQUAL_GAPS_2026-10-21.md` | REVUE_AUDIT | 6083 | `e2c0b4c382c6f5d7b2880bb567ecdab886e7f3c8` |
| `reviews/REVUE_SEMANTIQUE_17_CARTES_CANDIDATES_2026-11-04.md` | REVUE_AUDIT | 4739 | `3743ad488b260914dc59c2a9a09a0fcdc62eaa4b` |
| `reviews/TWO_EQUAL_GAPS_COMMIT_VERIFY_2026-10-20.json` | REVUE_AUDIT | 623 | `065ffa71e0a2503583452dba896ec5391976d012` |
| `reviews/TWO_EQUAL_GAPS_RAVI2_CERTIFICATE_2026-10-20.json` | REVUE_AUDIT | 1995 | `2b95748ccf69cffaeca9f54d9f33b577025678cd` |
| `reviews/V19_ASSEMBLAGE_ORIENTE_2026-10-15.md` | REVUE_AUDIT | 6415 | `310b870ee1cb88bee15278970a93ed80824f1cb9` |
| `reviews/V19_BADOBJECT_FIBER2_2026-10-15.md` | REVUE_AUDIT | 6442 | `d23dca3e6cd6ca5082580e17e1654d1149461f01` |
| `reviews/V19_BADOBJECT_N11_2026-10-15.md` | REVUE_AUDIT | 5622 | `f142853ff96e2f9138d6eca377887f918b5e0f04` |
| `reviews/V19_MULTIPLICITE_CAPACITE_2026-10-15.md` | REVUE_AUDIT | 7317 | `10fd9011265018f4b96cd50771f608daba4542a8` |
| `reviews/V19_REGION_COEXISTENCE_2026-10-15.md` | REVUE_AUDIT | 6020 | `ecf92218c1e700e0abd9be6e604fb839b3bc61dd` |
| `reviews/VERIFICATION_SQLITE_V33_2026-11-04.md` | REVUE_AUDIT | 3322 | `a486342220dd979b71104453d578397cb4e94f30` |

## 6. Scripts, contrats, traces et sorties de reproductibilité

| Chemin | Type documentaire | Taille (octets) | SHA Git du blob |
|---|---|---:|---|
| `reproducibility/CCS/CCS_v09.lean` | REPRODUCTIBILITE | 765 | `aea1be2be86dee85eded3aadb3403abe76d13a1f` |
| `reproducibility/CCS/ccs_audit_provenance_v09.py` | REPRODUCTIBILITE | 615 | `6b00dff838dcd3ae09e7862a5c16e6c8432daeb9` |
| `reproducibility/CCS/ccs_audit_v10.py` | REPRODUCTIBILITE | 1071 | `9b574d91413793f5284787dedf826d5f6a3df2aa` |
| `reproducibility/CCS/ccs_certificat_exemple_v06.json` | REPRODUCTIBILITE | 1025 | `480712532c3ed37656b50e8aa33206a4e4a68dc0` |
| `reproducibility/CCS/ccs_certificat_formel_v07.json` | REPRODUCTIBILITE | 676 | `62de254311491943fd5e172bab937971191024b1` |
| `reproducibility/CCS/ccs_certificat_trace_v08.json` | REPRODUCTIBILITE | 1092 | `6334ad84e91fc6be5c31795428b5281151640863` |
| `reproducibility/CCS/ccs_certificat_v03.py` | REPRODUCTIBILITE | 2403 | `b7b6c9e2afa8a367e572f9af634fb6fe9590c56c` |
| `reproducibility/CCS/ccs_certificat_v03_resultats.json` | REPRODUCTIBILITE | 1847 | `6a865c8768f7ae42ce9ce2714090b7a92c4a0d59` |
| `reproducibility/CCS/ccs_contrats_v05.py` | REPRODUCTIBILITE | 2340 | `63c8437434b51eaace1d891e08c11af8a2d6a410` |
| `reproducibility/CCS/ccs_experiences_v02.py` | REPRODUCTIBILITE | 1908 | `9dab9d9bcbf2696cc348c5dfbffef6dba75b1e38` |
| `reproducibility/CCS/ccs_extrait_source_v08.txt` | REPRODUCTIBILITE | 221 | `d791910196de85e27de39f63c564ac2b260045b4` |
| `reproducibility/CCS/ccs_manifest_v09.json` | REPRODUCTIBILITE | 402 | `06144dab7fd74db2c126b7cafb093598d049ba4f` |
| `reproducibility/CCS/ccs_noyau_v04.py` | REPRODUCTIBILITE | 1838 | `2ce51dc55e190124795ff284408f52112f8dcaa5` |
| `reproducibility/CCS/ccs_prototype.py` | REPRODUCTIBILITE | 746 | `58b401b326e941f4e22193ff5876337aba8efa71` |
| `reproducibility/CCS/ccs_source_formelle_v07.py` | REPRODUCTIBILITE | 1939 | `5c15a0238bc3cb2ec9c9da8895123cb58b3f464f` |
| `reproducibility/CCS/ccs_trace_verifier_v08.py` | REPRODUCTIBILITE | 817 | `2aff92f101a06597576399e233cf3347edaefd2a` |
| `reproducibility/CCS/ccs_verificateur_independant_v06.py` | REPRODUCTIBILITE | 1435 | `e1ccb3c1bc46eec806fb84215905b1c47cbf5027` |
| `reproducibility/RAVI2/README.md` | REPRODUCTIBILITE | 3615 | `c014193d8ba6c54545b23c2df7b5c29e1b9299e8` |
| `reproducibility/RAVI2/checks/ACCESS_PREDICTIVE_BRIDGE_CHECK.json` | REPRODUCTIBILITE | 194 | `205946e4829fd815a60142d1f702ce5fcb3657c8` |
| `reproducibility/RAVI2/checks/ACC_STATE_COMMIT_CONTROLS_2026-10-20.json` | REPRODUCTIBILITE | 1498 | `5a4beea0ef5474196f59dd037112ddf7675cb45a` |
| `reproducibility/RAVI2/checks/DELTA_MEALY_V19_INTERFACE_CHECKS_2026-10-20.json` | REPRODUCTIBILITE | 2865 | `445c3031384e7d3b304f12a1673c50cfd59190cd` |
| `reproducibility/RAVI2/checks/MEALY_V19_MIN_OBSTRUCTION_CHECKS_2026-10-20.json` | REPRODUCTIBILITE | 6373 | `c04bded2ce9808c23824349bbe84b50939c4db1b` |
| `reproducibility/RAVI2/checks/Q_PREDICTIVE_HIDDEN_CHECKS_2026-10-20.json` | REPRODUCTIBILITE | 5384 | `bec26bbd800f75b451d2d58325a47715cc7c0d49` |
| `reproducibility/RAVI2/checks/Q_PREDICTIVE_HIDDEN_COMMIT_CONTROLS_2026-10-20.json` | REPRODUCTIBILITE | 13647 | `9a5fe03e58b97ec96d45f370ad51d1ddbcd349c6` |
| `reproducibility/RAVI2/checks/SINGLE_GAP_COMMIT_CONTROLS_2026-10-19.json` | REPRODUCTIBILITE | 1102 | `14d2c1b5ac9e0e6588ca9332f9efc5eb1170d68f` |
| `reproducibility/RAVI2/checks/SINGLE_GAP_FACTOR_COMPLEXITY_CHECKS_2026-10-19.json` | REPRODUCTIBILITE | 799 | `8e7dbf5723de10481f69c6f9b407ee2c15d1b1b3` |
| `reproducibility/RAVI2/checks/TIME_PREDICTIVE_CHECKS_2026-10-19.json` | REPRODUCTIBILITE | 2591 | `30bc80c186205ae92838822f72757ccd5f9ac5b1` |
| `reproducibility/RAVI2/checks/TIME_PREDICTIVE_COMMIT_CONTROLS_2026-10-19.json` | REPRODUCTIBILITE | 1206 | `1fe0514d236555d1446e302f36c4e209542d44a5` |
| `reproducibility/RAVI2/checks/V19_MIN_OBSTRUCTION_SPECTRUM_AUDIT_CHECKS_2026-10-19.json` | REPRODUCTIBILITE | 2883 | `1af718f3b8cca0974d607a10e64dd1d0ee280d1f` |
| `reproducibility/RAVI2/checks/audit_v19_min_obstruction_spectrum_2026-10-19.py` | REPRODUCTIBILITE | 6571 | `bf56aaea7ef799835ba4322f6b7991dd663b96f5` |
| `reproducibility/RAVI2/checks/check_q_predictive_hidden.py` | REPRODUCTIBILITE | 4528 | `6d6330444f0a2e4fce80822c921fb3b125526b21` |
| `reproducibility/RAVI2/checks/commit_q_predictive_hidden_20261020.py` | REPRODUCTIBILITE | 10598 | `dc133b66d914c5343d19fe622c9f6da375e8e603` |
| `reproducibility/RAVI2/checks/single_gap_factor_complexity_checks_2026-10-19.py` | REPRODUCTIBILITE | 4106 | `851b427610bf63f2ee5c9998c5d953985a8f39d4` |
| `reproducibility/RAVI2/checks/time_predictive_checks_2026-10-19.py` | REPRODUCTIBILITE | 4121 | `c70c71a03c53c4c2964229169be1fff380d46ff5` |
| `reproducibility/RAVI2/commit_acc_state_20261020.py` | REPRODUCTIBILITE | 9234 | `00a22bbdcd17f16308d2a4c1a7559456899bd8b7` |
| `reproducibility/RAVI2/commit_affine_gauge_core_bridge.py` | REPRODUCTIBILITE | 10687 | `9a76cc757908002c672a01ef25cbda4b8e0e3f78` |
| `reproducibility/RAVI2/commit_affine_tree_core_bridge.py` | REPRODUCTIBILITE | 11352 | `181878b5c9d8de3303776bed68a973cc37c07873` |
| `reproducibility/RAVI2/commit_audit_checks.json` | REPRODUCTIBILITE | 2953 | `22e8fe9093b6c6bab0bc8070b9ea5370d2a0e714` |
| `reproducibility/RAVI2/commit_audit_checks.py` | REPRODUCTIBILITE | 7579 | `be050d118351f1a20aa1faede0367866577ad887` |
| `reproducibility/RAVI2/commit_catchup_20261019.py` | REPRODUCTIBILITE | 17424 | `938fc48224e207fd6ecb089bb3bc6fcb1417379a` |
| `reproducibility/RAVI2/commit_mealy_helly_bridge.py` | REPRODUCTIBILITE | 9946 | `d9fad852a3a36d354e6e3c5c5227f33d92325ccb` |
| `reproducibility/RAVI2/commit_single_gap_complexity_20261019.py` | REPRODUCTIBILITE | 8086 | `a0b2d8a494e0f0171a1104058865a0e2840d4aa0` |
| `reproducibility/RAVI2/commit_time_predictive_20261019.py` | REPRODUCTIBILITE | 11935 | `40b7f6357dd1c753695ee950f9f6ebbb08ade923` |
| `reproducibility/RAVI2/commit_two_gap_20261020.py` | REPRODUCTIBILITE | 14623 | `8302c167d940b57138169f8a0fb65adec7ca0ebd` |

## 7. Conclusions et limites

1. L'inventaire des chemins des trois dossiers est exhaustif pour le commit source indiqué : l'API GitHub a retourné un arbre non tronqué.
2. Il établit l'identité des blobs présents dans ce commit, pas la validité ni l'exhaustivité de toutes les preuves attachées à chaque résultat.
3. Les 185 artefacts n'ont pas encore été transférés dans la branche architecture ou la branche maintenance. Les copies exactes par chemin et par blob sont nulles dans les deux arbres comparés.
4. Les fiches `reconstructed/` restent séparées des fiches originales. Aucun remplacement, fusion ou promotion de statut n'est autorisé par cet inventaire.
5. Les scripts n'ont pas été exécutés. En particulier, aucun script susceptible d'écrire dans SQLite n'a été lancé ; aucune base privée n'a été lue ou modifiée.
6. Étape suivante : classifier le contenu de chaque artefact (identifiant de résultat, statut explicitement déclaré, provenance, preuve, contrôles, dépendances, contradictions), puis proposer un transfert non destructif dans une branche dédiée avec revue par lots.

**Verdict :** inventaire des chemins et des empreintes Git complet pour `research/bricks/`, `reviews/` et `reproducibility/` au commit source indiqué ; réconciliation sémantique et intégration effective encore ouvertes.