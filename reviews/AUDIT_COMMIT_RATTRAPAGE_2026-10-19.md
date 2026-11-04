# Audit RAVI-2 — commit de rattrapage des briques orphelines

Date : 19 octobre 2026  
Commit proposé : `COMMIT-RAVI2-2026-10-19-CATCHUP-20`

## 1. Objet

Comparer les résultats documentés des conversations et rapports récents avec le noyau structuré courant (`77` cartes, `73` admissibles) et promouvoir uniquement les résultats autonomes qui satisfont le protocole de commit : énoncé exact, domaine, hypothèses, preuve ou calcul reproductible, limites, provenance et contrôle adversarial.

## 2. Briques promues

### SCH-POLY-CLOSURE-01
Classification directe de l'invariance de `P_N` pour un opérateur différentiel d'ordre deux dans une représentation commune ; seuil deux/trois secteurs et contre-exemple exact à la généralisation « deux secteurs impliquent toute la suite ».

Statut : `DÉMONTRÉ` interne. Originalité : `INDÉTERMINÉ`. Les classifications générales d'opérateurs à sous-espaces polynomiaux invariants sont antérieures (Post–Turbiner 1993 ; Turbiner 1994). Aucune priorité exacte de la formulation T1–T3 n'est revendiquée.

### SCH-SEXTIC-PARITY-01
Condition exacte d'invariance de `x^σ exp(-g) P_N(x²)` pour la famille sextique régulière. Statut : `DÉMONTRÉ`; originalité `CONNU_OU_CLASSIQUE`.

### BR-STATE-COST-01
Coût minimal d'extension d'un dispositif déterministe total par fermeture sous dérivées : `|Der(F_old ∪ B_req) \ F_old|`, ou impossibilité finie si cet ensemble est infini. Statut : `DÉMONTRÉ`; mécanisme classique de quotient/comportements, aucune nouveauté revendiquée.

### DET-FIN-01
Sous risque total de fausse alarme `<1`, alphabet à probabilités nulles conditionnelles minorées et mémoire finie, la capacité conditionnelle de détecter un changement arbitrairement tardif tend vers zéro. Statut : `DÉMONTRÉ`; originalité historique exacte `INDÉTERMINÉE`.

### BR-Q-SWAP-MEM-01
Témoin SWAP : deux préparations ont le même état réduit intermédiaire mais une même continuation restitue l'information ; dimension d'environnement `1` impossible sans mémoire extérieure, `2` suffisante. Statut : `DÉMONTRÉ`; mécanisme quantique élémentaire connu. Ne prouve pas une mémoire irréductiblement quantique.

### DESC-CLIP-01
Projection `p*=clip(q,[ℓ,u])` du facteur d'évidence binaire robuste : validité de supermartingale, dominance pointwise de la règle conservatrice, ordre des temps de première alarme, optimalité logarithmique locale. Statut : `DÉMONTRÉ`; aucune nouveauté générale revendiquée.

## 3. Contrôles indépendants exécutés le 19 octobre

Artefact : `/Recherche/04_CODE_DONNEES/CATCHUP_SCIENTIFIC_CHECKS_2026-10-19.json`.

- `SCH_T1_images = 792`
- `SCH_T2_images = 880`
- `SCH_T3_images = 1092`
- `SCH_two_sector_counterexample_images = 483`
- `SCH_T4_images = 4752`
- `Q_SWAP_matrix_identities = 4`
- `DESC_CLIP_cases = 50`
- `DET_FIN_automata = 4181`
- `DET_FIN_state_graph_checks = 12454`
- `STATE_COST_closure_checks = 124`
- `all_pass = true`

Le checker est indépendant du code historique et utilise arithmétique rationnelle / algèbre symbolique pour les identités finies.

## 4. Résultats explicitement NON promus

- `CL-JET-01` : volontairement non dupliquée car recouvrement substantiel avec `NS-CERT-E-11`; différence exacte non auditée.
- `NS-CERT-E-01..09` : statut documentaire verrouillé, mais l'ancien commit dit explicitement que leurs énoncés détaillés n'avaient pas été reconstruits dans le cycle de migration. Ne pas inventer une correspondance canonique d'identifiants.
- `NS-X36`, `NS-X46`, `B.6`, critère B.2, `X42`, `X45` : certificats autonomes documentés, mais normalisation des identifiants et séparation des cartes encore à fermer. Ils restent dans le registre de staging et dans l'audit de rattrapage du 19 octobre.
- `P55-A..D`, `NS-P55-COMP-01`, `OSC-ITER-01`, `OSC-REAL-01`, `GLOBAL-LOC-01` : `CERT-V` composites/source-vérifiés, non promus comme prémisses autonomes.
- théorie générale « transformations primitives / états non fondamentaux » : cadre cohérent/reformulation, aucune théorie physique nouvelle ou prédiction quantitative démontrée.
- extensions temporelles au-delà de `BR-TIME-01` : aucune nouvelle brique autonome fermée identifiée dans cette passe.

## 5. Frontières épistémiques

- `DÉMONTRÉ` signifie démonstration interne/reconstruction exacte sous hypothèses déclarées, pas validation humaine externe.
- Les résultats Schrödinger sont algébriques/localement réalisés. Ils ne donnent ni domaine auto-adjoint général, ni normalisabilité globale, ni résolution générale de Schrödinger.
- `DET-FIN-01` porte sur le risque total de fausse alarme et non l'ARL classique.
- `DESC-CLIP-01` conserve la validité du test sous son contrat ; la dominance d'alarme n'est pas une garantie uniforme de puissance post-changement.
- `BR-Q-SWAP-MEM-01` montre l'insuffisance d'un résumé réduit instantané pour certaines continuations, pas une ontologie sans états ni une exclusivité quantique.

## 6. Bibliographie ciblée

- G. Post, A. Turbiner, *Classification of linear differential operators with an invariant subspace of monomials*, arXiv:funct-an/9307001 (1993) : classification complète annoncée pour les sous-espaces à base monomiale.
- A. Turbiner, *Quasi-Exactly-Solvable Differential Equations*, arXiv:hep-th/9409068 (1994) : classification générale des opérateurs possédant un sous-espace polynomial invariant et des opérateurs possédant une infinité de tels sous-espaces.
- A. V. Turbiner, *One-Dimensional Quasi-Exactly Solvable Schrödinger Equations*, arXiv:1603.02992 (2016) : revue des familles QES unidimensionnelles.

Ces sources empêchent toute revendication de nouveauté générale pour les deux briques Schrödinger. Elles ne déterminent pas la priorité historique exacte de chaque formule T1–T3 reconstruite ici.

## 7. Critère d'arrêt du rattrapage

La passe est fermée après deux niveaux de vérification : (1) comparaison index/snapshot ↔ rapports récents ; (2) contrôle indépendant des six briques retenues. Les candidats restants sont classés staging/composite/ambigu plutôt que de déplacer le verrou vers de nouvelles sous-dépendances.