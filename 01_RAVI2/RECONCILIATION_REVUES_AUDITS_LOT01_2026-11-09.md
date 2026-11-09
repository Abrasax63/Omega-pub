# Réconciliation des revues et audits historiques — lot 01 (10 fichiers, 9 novembre 2026)

**Dépôt :** `Abrasax63/Omega-pub`  
**Branche source immuable :** `migration/ravi2-ccs-public-2026-11-04`  
**Branche de publication :** `maintenance/reconciliation-bibliotheque-2026-11-05`  
**Périmètre :** 10 fichiers de `reviews/`, sélectionnés pour couvrir les ponts conceptuels, les résultats finis V19/C5, l'observabilité temporelle et les audits de certification/comptabilité.  
**Nature :** lecture et réconciliation documentaire. Les résultats de calcul mentionnés sont ceux rapportés par les audits historiques ; ils ne sont pas réexécutés dans ce lot.

## 1. Documents examinés et empreintes Git source

| Document | SHA Git source |
|---|---|
| `ADDENDUM_REVUE_17_CARTES_CANDIDATES_2026-11-04.md` | `afd29fa8660385091f295c231945bf0c4c666b76` |
| `AUDIT_ACC_STATE_COMMUTATION_2026-10-20.md` | `b19cbba729cbe80692e4c212ac85f71ece194329` |
| `AUDIT_CERTIFICATION_NAVIER_STOKES_2026-10-15.md` | `b866cc53cb47711af1c99a62a113190a709558dc` |
| `AUDIT_COMMIT_RATTRAPAGE_2026-10-19.md` | `adf23b54e85211756cd644620b41e63db2f64a28` |
| `AUDIT_CORRESPONDANCE_NS_PROP55_LEIREN_2026-10-15.md` | `6665ea3f5df5e0fe31c7b3db22c754e9a41518eb` |
| `AUDIT_INDEPENDANT_V19_C5_L3_2026-11-04.md` | `68f8f311cc8efe943623876b19e5b88d50cfa7d4` |
| `AUDIT_MATHEMATIQUE_ET_BIBLIOGRAPHIQUE.md` | `c1038642c6da80c00741cf9b4b80db8b75dbecd7` |
| `AUDIT_Q_PREDICTIVE_HIDDEN_2026-10-20.md` | `929d57be88d8d9a52aac6913f999d53bb57e28a1` |
| `AUDIT_RAPPROCHEMENT_32_CARTES_2026-11-04.md` | `ad41325118325f58dd23fb6c58d267de9d008638` |
| `AUDIT_RATTRAPAGE_BRIQUES_2026-10-19.md` | `5e0fd197e5de838f4fde048b267d708922ee7a6a` |

Les SHA ci-dessus sont les identifiants de blobs Git retournés par GitHub, pas des empreintes SHA-256 locales.

## 2. Résultats par famille

### A. Correspondance cartes ↔ SQLite : 17 candidats

**ADDENDUM_REVUE_17_CARTES_CANDIDATES** rapporte une revue individuelle de 17 correspondances initialement classées `FILENAME_MATCH_ONLY_REVIEW_REQUIRED`. L'audit affirme que les identifiants/titres, énoncés/domaines et locateurs de provenance concordent pour les 17 cas.

**Limite majeure explicitement conservée :** cette revue confirme une correspondance documentaire de contenu et de provenance, mais ne crée pas rétroactivement les liens de carte dans `evidence` ou `result_sources` de SQLite v33. Le rapport distingue donc les liaisons explicites préexistantes, les 17 correspondances relues sans lien individuel explicite, et les résultats sans carte individuelle retrouvée. Aucun changement SQLite n'est autorisé par cette revue.

### B. Accessibilité et quotient prédictif

**AUDIT_ACC_STATE_COMMUTATION** formule un pont entre l'accessibilité `Reach(E)` et le quotient par équivalence prédictive. L'audit rapporte une preuve directe par stabilité de l'équivalence et commutation du quotient avec les transitions, ainsi qu'un contrôle exhaustif/aléatoire historique (41 018 cas exhaustifs et 20 000 cas aléatoires, zéro violation).

La recherche bibliographique conclut explicitement **CONNU_OU_CLASSIQUE**, avec des références à Adámek–Milius–Moss–Sousa (2013) et Wißmann (2022). La valeur retenue est une interface utile entre deux briques, pas une découverte nouvelle. Les raccords sont classés comme références/définitions et non comme compositions certifiées.

### C. Certification Navier–Stokes : frontière stricte entre identité élémentaire et preuve globale

**AUDIT_CERTIFICATION_NAVIER_STOKES** sépare neuf sous-briques élémentaires vérifiées sur papier (règle de chaîne, divergence cylindrique sous conditions, énergie forcée régulière, résidu inverse, comptabilité anisotrope, changement d'échelle de viscosité, Reynolds anisotrope, moyenne quadratique, monotonie d'une coordonnée) des cartes composites dont les preuves profondes ne sont pas reconstruites.

Le document indique :
- 9 sous-briques élémentaires avec preuve courte dans le périmètre exact décrit ;
- aucune des 26 cartes globales promue dans la table des résultats scientifiques certifiés ;
- aucune certification indépendante du théorème principal ;
- la source OpenAI concerne un problème **forcé**, et non le problème classique non forcé.

Les identités élémentaires ne doivent donc jamais être présentées comme une preuve du théorème principal. Les restrictions de régularité, d'axe, de support et d'échelles font partie des énoncés.

### D. Rattrapage des briques orphelines

**AUDIT_COMMIT_RATTRAPAGE** rapporte six briques promues dans le cycle historique, avec contrôles exacts/rationnels, et identifie explicitement les non-promotions : CL-JET-01 pour risque de doublon avec NS-CERT-E-11 ; NS-CERT-E-01..09 non reconstruits dans le cycle concerné ; six certificats ultérieurs encore en staging ; composites CERT-V non admissibles comme prémisses autonomes.

Les contrôles annoncés (images polynomiales, automates finis, graphes d'états, etc.) sont des exécutions historiques rapportées. Ils ne sont pas rejoués ici. La règle épistémique du rapport est conservée : « DÉMONTRÉ » signifie démonstration interne sous hypothèses, pas validation humaine externe.

**AUDIT_RATTRAPAGE_BRIQUES** précise un backlog historique minimal de 15 résultats autonomes à auditer pour un éventuel commit (E01..E09 et six certificats postérieurs), plus des composites source-vérifiés qui doivent rester en staging. Il interdit de normaliser automatiquement des identifiants ambigus, notamment autour de NS-CERT-E-16. CL-JET-01 est une non-promotion volontaire, pas une omission certaine.

### E. Correspondance OpenAI Prop. 5.5 / Lei–Ren

**AUDIT_CORRESPONDANCE_NS_PROP55_LEIREN** conclut à une correspondance structurelle forte, mais pas à une équivalence logique intégrale certifiée. Il identifie P55-A comme priorité active : suivre Prop. 13.3(13.31) → Assumption 13.1(v) → Lemma 17.1 → Prop. 17.2, en contrôlant marge, uniformité, domaine et circularité.

Le document rappelle que :
- le contrôle pondéré seul est insuffisant près des bords ;
- la platitude sur ‖Z‖≤1−ε ne vaut pas uniformité jusqu'aux bords ;
- la réalisation des cinq moments est un verrou distinct ;
- Proposition 5.5 entière et théorème principal restent NON CERTIFIÉS.

La brique NS-CERT-E-10 peut rester une brique abstraite séparée ; elle ne certifie pas l'assemblage.

### F. V19–C5, horizon L=3

**AUDIT_INDEPENDANT_V19_C5_L3** rapporte une reproduction indépendante de la classification locale par propagation directe, sans DSU/parité-union : 3 341 diagrammes canoniques, 510 ombres propres, 13 classes D5 et 14 classes orientées C5. Il signale que deux lignes de paires et 26 lignes de triples réutilisaient des paires d'états ; des fichiers réparés sont décrits.

Le point structurel important est que les 455 témoins D5 ne couvrent que 455 des 560 multisets orientés C5, les 105 manquants contenant C5O-09. Le quotient par réflexion masque donc une classe chirale. L'audit rapporte ensuite que le témoin U42, à 42 états, contient au moins 10 paires distinctes dans chacune des 14 classes, permettant de réaliser les 560 triples orientés.

**Réserve décisive :** la reproduction du catalogue local ne re-prouve pas le lemme général de localité L+2 de la note primaire V19. La portée universelle de la classification reste conditionnée à ce lemme. L'optimalité des capacités et l'originalité bibliographique restent INDÉTERMINÉES. L'addendum signale en outre que les fichiers de données nécessaires au rejeu depuis le seul dépôt GitHub n'étaient pas tous présents au moment de sa rédaction.

### G. Profil d'observabilité temporelle des endofonctions finies

**AUDIT_MATHEMATIQUE_ET_BIBLIOGRAPHIQUE** présente deux énoncés centraux :

1. À horizon infini, le nombre minimal de symboles est caractérisé par la ramification maximale Δ(T) et le nombre de cycles de chaque période comparé au nombre de colliers primitifs (P_d(m)).
2. À horizon fini, le coût minimal d'alphabet est équivalent à l'immersion injective du graphe fonctionnel dans un graphe de de Bruijn (B(m,L)).

Le document rapporte un test exhaustif historique sur les 50 069 endofonctions de taille (N\le6), sans contre-exemple. Il souligne que les concepts de générateur unilatéral, observabilité par sorties, graphes observables et de Bruijn ont des antécédents classiques. La caractérisation exacte par Δ(T) et colliers primitifs est présentée comme candidat à nouveauté, **non comme nouveauté établie**.

Ce résultat est un candidat mathématique important, mais ce lot ne reconstitue pas sa preuve de manière indépendante et ne rejoue pas les 50 069 cas. La revue bibliographique citée dans la source est une recherche ciblée, non une preuve d'absence d'antériorité.

### H. Mémoire prédictive quantique cachée

**AUDIT_Q_PREDICTIVE_HIDDEN** corrige une métrique initiale : le cardinal brut des classes prédictives ne borne pas la dimension mémoire, car une famille continue d'états environnementaux non orthogonaux peut produire un continuum de lois futures avec (d_E=2).

La métrique remplacée, (N_{perf}), compte des histoires ayant le même réduit instantané et parfaitement distinguables par une même expérience future. Le rapport donne :
- cas produit : (N_{perf}\le d_E), avec saturation ;
- cas corrélé : (N_{perf}=d^2) pour une famille de Bell généralisée ;
- contrôle numérique historique pour (d=2..10), erreur maximale annoncée < (4\times10^{-15}), zéro échec.

Le rapport conclut **CONNU_OU_CLASSIQUE** au niveau conceptuel, en reliant la structure aux process tensors, au dense coding et à la littérature de mémoire quantique. La valeur est la séparation entre classes prédictives, distinguabilité parfaite et corrélations cachées. Les contrôles ne sont pas rejoués ici.

### I. Traçabilité des 32 reconstitutions

**AUDIT_RAPPROCHEMENT_32_CARTES** corrige un vocabulaire potentiellement trompeur : 32 fiches originales autonomes n'ont pas été retrouvées, mais les 32 reconstitutions contiennent des références de sources historiques. Il ne faut donc pas dire « 32 résultats sans source ».

Il faut distinguer :
- fiche originale autonome non retrouvée ;
- source documentaire référencée dans une reconstitution ;
- disponibilité binaire et rejeu, non établis pour toutes les sources.

Le rapprochement documentaire est déclaré complet au niveau des références, mais la récupération des originaux et le rejeu scientifique ne sont pas réalisés.

## 3. Contradictions, réserves et verrous transversaux

1. **Lien documentaire ≠ lien structuré SQLite.** Les 17 correspondances de cartes ne créent pas les relations de preuve absentes de la base.
2. **Brique élémentaire ≠ carte composite ≠ théorème principal.** Les neuf identités NS élémentaires ne certifient aucune des 26 cartes globales ni le théorème principal.
3. **Source vérifiée ≠ équivalence logique.** Prop. 5.5 / Lei–Ren demeure une correspondance structurelle, avec P55-A comme verrou.
4. **Classification locale ≠ théorème universel.** V19–C5 reste conditionné au lemme L+2 non re-prouvé dans cet audit.
5. **D5 ≠ C5 orienté.** La réflexion fusionne une paire chirale ; les témoins D5 ne couvrent pas les 560 multisets orientés.
6. **Cardinal des classes prédictives ≠ dimension mémoire.** La première métrique est explicitement réfutée comme proxy ; (N_{perf}) est la métrique corrigée.
7. **Recherche bibliographique ciblée ≠ preuve de nouveauté.** Les candidats observabilité et V19 ne doivent pas être présentés comme nouveaux avant vérification bibliographique indépendante.
8. **Rejeu historique ≠ rejeu présent.** Les volumes de tests cités sont des déclarations de provenance, non des exécutions de ce lot.

## 4. Décision de réconciliation

- Conserver les statuts historiques déclarés, sans les promouvoir.
- Maintenir P55-A comme verrou prioritaire si reprise NS.
- Maintenir le lemme L+2 comme dépendance critique pour la portée universelle V19–C5.
- Maintenir la formule Δ(T)+colliers primitifs comme candidat mathématique à auditer, pas comme nouveauté démontrée.
- Ne pas modifier SQLite, ne pas fusionner les branches, ne pas écraser les sources historiques ou les fichiers réparés.
- Les documents originaux de la branche migration restent la référence de provenance ; le présent rapport est une couche de lecture.

## 5. Limites de ce lot

Aucun script, notebook, checker, calcul exact ou preuve Lean n'a été exécuté. Aucune preuve n'a été reconstruite ligne par ligne. Les contrôles numériques mentionnés proviennent des audits historiques. Aucune base SQLite privée n'a été consultée ou modifiée. Aucune validation humaine tierce n'a été effectuée.

**Verdict :** 10 revues/audits ont été réconciliés documentairement. Les principaux verrous et limites sont identifiés, mais aucune certification scientifique n'est renouvelée.
