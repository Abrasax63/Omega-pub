# BR-Q-PRED-HIDDEN-01 — Séparation prédictive cachée : produit, corrélations et cardinalité

**Statut : DÉMONTRÉ interne. Version 1.0 — 20 octobre 2026.**  
**Originalité : CONNU_OU_CLASSIQUE.** Brique de raccordement interne ; aucune priorité revendiquée.

## Domaine

Système quantique fini `S` et environnement fini `E`, avec `dim S = dim E = d >= 2` pour les constructions exactes ci-dessous. Les histoires sont comparées à un instant de coupure où elles ont le même état réduit sur `S`. Les continuations futures autorisées peuvent contenir l'évolution conjointe fixe `S⊗E`, des mesures de `S` et la réinitialisation de `S` entre deux temps de mesure.

On utilise l'équivalence prédictive relative de `BR-STATE-01` : deux histoires sont équivalentes si tous les tests futurs admis ont les mêmes lois de résultats.

Définir `N_perf` comme le cardinal maximal d'une famille d'histoires ayant le même réduit instantané de `S` et qui sont **parfaitement distinguables par une même expérience future**.

## Énoncé A — mémoire produit

Pour une famille au temps de coupure de la forme

`rho_i^{SE} = sigma_S ⊗ tau_i^E`

avec le même `sigma_S`, si les histoires sont parfaitement distinguables dans le futur, alors les supports des `tau_i^E` doivent être mutuellement orthogonaux. Donc

`N_perf <= d_E`.

Pour `d_S=d_E=d`, la borne est atteinte par

`|0><0|_S ⊗ |i><i|_E`, `i=0,...,d-1`,

puis une continuation SWAP et une mesure dans la base de calcul de `S`. Ainsi `N_perf=d` dans cette classe.

## Énoncé B — amplification par corrélations

Autoriser des corrélations `S-E` tout en gardant le même réduit local. Les `d^2` états de Bell généralisés

`|Phi_{m,n}> = d^{-1/2} sum_j omega^{mj} |j>_S |j+n mod d>_E`

ont tous le même réduit `I_S/d` et sont orthonormaux.

Une même continuation peut les distinguer parfaitement : appliquer le décodeur unitaire de la base de Bell, mesurer `S` pour obtenir `m`, réinitialiser `S` à `|0>`, appliquer SWAP, puis mesurer `S` pour obtenir `n`.

Comme `dim(S⊗E)=d^2`, aucune famille d'états parfaitement distinguables ne peut dépasser `d^2`. Donc, pour cette classe corrélée,

`N_perf = d^2`.

Les corrélations peuvent donc amplifier d'un facteur `d` le nombre d'histoires parfaitement prédictivement distinguables cachées derrière un même réduit local, par rapport au cas produit.

## Énoncé C — le nombre brut de classes prédictives n'est pas une dimension mémoire

Déjà pour `d_E=2`, considérer

`|0>_S ⊗ |psi_theta>_E`, avec `|psi_theta>=cos(theta)|0>+sin(theta)|1>` et `theta in [0,pi/2]`.

Après SWAP, une mesure de `S` dans la base de calcul donne

`P(0|theta)=cos(theta)^2`.

Ces lois sont distinctes pour une infinité non dénombrable de valeurs de `theta`. Le quotient prédictif peut donc avoir un continuum de classes malgré une mémoire physique de dimension 2.

Par conséquent, la quantité brute `|H / ~_pred|` ne constitue pas une mesure finie de dimension de mémoire quantique. Pour une lecture dimensionnelle opérationnelle, il faut distinguer au minimum le nombre de classes prédictives du nombre de classes **parfaitement distinguables**.

## Preuve et contrôle

- La borne produit vient de la contractivité de la distinguabilité sous canal : une sortie parfaitement distinguable exige déjà des supports orthogonaux pour les mémoires `tau_i^E`; il ne peut y avoir plus de `d_E` supports orthogonaux non nuls.
- La borne corrélée `d^2` est la borne dimensionnelle de l'espace `S⊗E`; la base de Bell généralisée la sature tout en gardant le même réduit `I/d`.
- Le checker du 20 octobre 2026 vérifie les constructions pour `d=2..10`, l'orthogonalité, l'égalité des réduits, le décodeur et SWAP, avec erreur numérique maximale `<4e-15`, et teste 1001 valeurs de `theta` pour la branche continue.

## Portée et limites

- Ce résultat **ne** définit pas la dimension mémoire minimale d'un process tensor général.
- `N_perf` dépend de l'interface de continuations autorisées ; il s'agit ici d'une construction existentielle et d'une borne exacte dans le modèle déclaré.
- La branche `d^2` exploite des corrélations `S-E`; elle ne doit pas être interprétée comme `d^2` états stockés dans `E` seul.
- Le continuum de classes prédictives ne signifie pas une mémoire classique infinie : des états quantiques non orthogonaux peuvent être distincts sans être parfaitement distinguables.
- Aucune « mémoire irréductiblement quantique » générale n'est démontrée.

## Originalité / bibliographie

Les ingrédients sont connus : états prédictifs/causaux, processus quantiques avec mémoire, bases de Bell/dense coding et témoins de dimension temporelle. Références principales :

- Vieira, Milz, Vitagliano, Budroni, *Witnessing environment dimension through temporal correlations*, Quantum 8, 1224 (2024), DOI 10.22331/q-2024-01-10-1224.
- Pollock et al. / Milz et al., cadre process tensor et dimension effective de l'environnement ; synthèse dans *Quantum Stochastic Processes and Quantum non-Markovian Phenomena*, PRX Quantum 2, 030201 (2021).
- Bourdon & Gerjuoy, *Overcoming a limitation of deterministic dense coding with a nonmaximally entangled initial state*, Phys. Rev. A 81, 022314 (2010), rappelant la capacité `d^2` avec état maximalement intriqué.
- Elliott, *Causal memory and structural complexity of correlated quantum sequences*, arXiv:2610.06519v2 (2026), pour le contexte récent sur mémoire causale minimale des séquences quantiques.

La contribution ici est une **mise en interface exacte** de ces mécanismes avec `BR-STATE-01` et le témoin `BR-Q-SWAP-MEM-01`. Elle est classée `CONNU_OU_CLASSIQUE`.

## Provenance

Audit : `/Recherche/03_AUDITS_CERTIFICATS/AUDIT_Q_PREDICTIVE_HIDDEN_2026-10-20.md`  
Checker : `/Recherche/04_CODE_DONNEES/RAVI2_RESEARCH/Q_PREDICTIVE_HIDDEN_CHECKS_2026-10-20.json`  
Script : `/Recherche/04_CODE_DONNEES/RAVI2_RESEARCH/check_q_predictive_hidden.py`