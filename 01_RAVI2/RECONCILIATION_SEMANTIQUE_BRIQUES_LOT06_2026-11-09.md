# Réconciliation sémantique des briques — lot 06 — 9 novembre 2026

**Branche source :** `migration/ravi2-ccs-public-2026-11-04`  
**Commit source inspecté :** `2f71a6b8ed03914c0b5d308520d30e0133d9e9ad`  
**Branche de publication :** `maintenance/reconciliation-bibliotheque-2026-11-05`

## 1. Périmètre et nature des documents

Quinze fiches de `research/bricks/reconstructed/` ont été lues. Toutes sont explicitement des **RECONSTITUTIONS NON ORIGINALES** : les fiches Markdown originales ne sont pas retrouvées ; les contenus sont reconstruits depuis SQLite v33 et des compléments documentaires. Les statuts cités ci-dessous sont des statuts historiques recopiés, non des validations effectuées dans ce lot.

## 2. Classification des quinze fiches

| Fiche | Sujet et contrat essentiel | Statut historique | Limites et précautions |
|---|---|---|---|
| OBS-M27-CONFLICT | Sous-famille minimale de langages de résolution à intersection vide ; arité 2 à q−1 sous r_IO=1 | DÉMONTRÉ | Résultat candidat selon la note source, sans vérification formelle ni revue externe certifiée |
| OBS-M27-FERTILE | Au plus q−1 sorties fertiles par entrée dans une machine de Mealy sous r_IO=1 | DÉMONTRÉ | Mécanisme matriciel décrit ; les calculs de familles ne remplacent pas une preuve universelle indépendante |
| OBS-M27-SPECTRUM | Construction C(q,k), pour chaque 2≤k≤q−1, réalisant un noyau de conflit minimal de taille k | DÉMONTRÉ | Les constructions et 228 sous-familles sont rapportées ; pas rejouées ; originalité indéterminée |
| OBS-RESTRICT-COUNT | Probabilité exacte de collision après précoloration et CNF exacte de largeur ≤2L | DÉMONTRÉ | Résultat conditionnel à l'encodage et à la restriction homogène ; 506 556 contrôles historiques non rejoués |
| OBS-RESTRICT-GREEDY | Espérances conditionnelles : si B initial <1, une complétion sans collision est garantie | DÉMONTRÉ | B≥1 est inconclusif ; pas de gain comparatif établi ; exemples historiques non rejoués |
| OBS-RESTRICT-OVERLAP | Formule de covariance par intersection d'espaces binaires, poids de code et polynôme de Tutte | DÉMONTRÉ | Covariance nulle n'implique pas indépendance ; aucun transfert aux contraintes forcées V19 |
| OBS-RESTRICT-PROFILE | Loi exacte de Q et reconstruction du profil des tailles via une courbe p↦E(Q²) | DÉMONTRÉ | Nécessite n,k et la courbe exacte ; ne reconstruit pas la topologie ; données bruitées insuffisantes |
| OBS-V19-LOCAL-L2 | Petit modèle temporel L+2 pour les ombres sur cycle sous cohérence forcée | DÉMONTRÉ | Les tests aléatoires rapportés ne remplacent pas la preuve ; définition primaire de l'ombre à contrôler |
| OBS-V19-TRIPLE-COMPLETE13 | Compatibilité ternaire des 455 multisets de trois classes parmi les 13 classes D5 | CALCUL EXACT | Résultat sur classes D5, non sur les 14 classes orientées C5 ; certificats et CSV non rejoués |
| OBS-V8-FACT-INF | Caractérisation et factorisation du polynôme d'observabilité à horizon infini | DÉMONTRÉ | Reconstruction/audit historiques rapportés, non rejoués ; originalité bibliographique indéterminée |
| OBS-V9-RANK | Stabilisation du rang du graphe d'orbite de paire : min(L,r_p) | DÉMONTRÉ | 50 069 systèmes rapportés dans l'audit historique ; pas de contre-test nouveau |
| OBS-V9-STAB-N1 | Stabilisation de χ_obs à horizon N−1 | DÉMONTRÉ | Explicitement redondant avec un théorème antérieur de raffinement des partitions ; conserver l'étiquette REDONDANT |
| OMEGA-O41-DET-V11 | Détection de changements sous séparation Δ∞>2τ et durée minimale de séjour | DÉMONTRÉ | Audit historique « survécu » ; simulations finies et seuils testés ne sont pas des seuils universels ; pas de validation tierce |
| Q-RQ4-COMMON-RANK | Identifiabilité par rang commun et factorisation sous hypothèses instrumentales | DÉMONTRÉ | La conclusion physique exige complétude tomographique et existence du peigne ; n'exclut pas les mécanismes de fuite d'information non modélisés |
| Q-RQ4-PAULI-ROBUST | Borne Pauli |f(0)-f(1)|≤2δ/t et dégénérescence à t=0 | DÉMONTRÉ | Optimalité annoncée pour une question finale scalaire seulement ; aucune réalisation CPTP globale revendiquée |

## 3. Dépendances et distinctions à préserver

- Les fiches `OBS-M27-CONFLICT`, `OBS-M27-FERTILE` et `OBS-M27-SPECTRUM` forment une chaîne conceptuelle : la borne de largeur fertile intervient dans la borne d'arité du noyau ; la famille C(q,k) réalise les arités permises. Garder le résultat nécessaire et la construction de sharpness séparés.
- `OBS-RESTRICT-GREEDY` dépend de `OBS-RESTRICT-COUNT`. `OBS-RESTRICT-PROFILE` dépend également de la loi conditionnelle de COUNT. `OBS-RESTRICT-OVERLAP` illustre COUNT, mais sa preuve de recouvrement est autonome.
- `OBS-V19-LOCAL-L2` est une dépendance de plusieurs résultats V19. Il ne faut pas remplacer la preuve du petit modèle par les essais aléatoires de localité.
- `OBS-V19-TRIPLE-COMPLETE13` porte sur les 13 classes D5. Ne pas le confondre avec la classification orientée C5 à 14 classes ; le quotient par réflexion peut masquer la chiralité.
- `OBS-V9-STAB-N1` est correct selon la source mais redondant dans le programme ; il ne doit pas être présenté comme une découverte autonome.
- `OMEGA-O41-DET-V11` corrige une lecture monotone erronée : 480, 768 et 1536 sont des premières longueurs testées pour des critères différents, non une loi de seuil monotone universelle.
- `Q-RQ4-COMMON-RANK` et `Q-RQ4-PAULI-ROBUST` ont des contrats complémentaires mais distincts. La borne scalaire Pauli n'est pas une preuve de factorisation tomographique globale.

## 4. Contrôles et statut de vérification du lot

- Les 15 fiches ont été récupérées et lues sur la branche source historique indiquée.
- Les déclarations de preuve, d'audit et de test présentes dans les fiches sont historiques. Elles n'ont pas été rejouées dans cette opération.
- Aucun script, notebook, calcul exact, vérificateur Lean ou contre-test n'a été exécuté.
- Aucune base SQLite privée n'a été lue ou modifiée.
- Aucun statut scientifique n'est renouvelé. Aucune reconstitution n'est promue au rang de fiche originale.
- Les fiches restent dans `research/bricks/reconstructed/`.

## 5. Traçabilité

- `research/bricks/reconstructed/OBS-M27-CONFLICT_RECONSTITUTION.md`
- `research/bricks/reconstructed/OBS-M27-FERTILE_RECONSTITUTION.md`
- `research/bricks/reconstructed/OBS-M27-SPECTRUM_RECONSTITUTION.md`
- `research/bricks/reconstructed/OBS-RESTRICT-COUNT_RECONSTITUTION.md`
- `research/bricks/reconstructed/OBS-RESTRICT-GREEDY_RECONSTITUTION.md`
- `research/bricks/reconstructed/OBS-RESTRICT-OVERLAP_RECONSTITUTION.md`
- `research/bricks/reconstructed/OBS-RESTRICT-PROFILE_RECONSTITUTION.md`
- `research/bricks/reconstructed/OBS-V19-LOCAL-L2_RECONSTITUTION.md`
- `research/bricks/reconstructed/OBS-V19-TRIPLE-COMPLETE13_RECONSTITUTION.md`
- `research/bricks/reconstructed/OBS-V8-FACT-INF_RECONSTITUTION.md`
- `research/bricks/reconstructed/OBS-V9-RANK_RECONSTITUTION.md`
- `research/bricks/reconstructed/OBS-V9-STAB-N1_RECONSTITUTION.md`
- `research/bricks/reconstructed/OMEGA-O41-DET-V11_RECONSTITUTION.md`
- `research/bricks/reconstructed/Q-RQ4-COMMON-RANK_RECONSTITUTION.md`
- `research/bricks/reconstructed/Q-RQ4-PAULI-ROBUST_RECONSTITUTION.md`

**Verdict du lot 06 :** 15/15 reconstitutions restantes classées. La totalité des 32 fiches de reconstitution est désormais couverte par les lots de réconciliation. Cela ne signifie pas que les 62 fiches originales sont toutes classées, ni que les résultats ont été revalidés.
