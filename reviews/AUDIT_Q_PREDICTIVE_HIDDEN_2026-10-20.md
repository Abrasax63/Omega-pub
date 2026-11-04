# Audit RAVI-2 — séparation prédictive cachée quantique

Date : 20 octobre 2026.

## Question bornée

Tester le candidat Discovery `BR-Q-SWAP-MEM-01 ↔ BR-STATE-01` sans tenter de redémontrer la théorie générale de la mémoire quantique.

Question initiale : peut-on quantifier l'écart entre état réduit instantané et état prédictif par le nombre de classes prédictives cachées ?

Budget : deux expériences décisives.

## Prémisses internes

- `BR-STATE-01` : quotient par égalité de toutes les réponses futures ; minimalité prédictive relative à une interface de tests.
- `BR-Q-SWAP-MEM-01` : deux histoires peuvent avoir le même réduit de `S` puis redevenir distinguables sous la même continuation SWAP.

Aucune prémisse certifiée n'est réauditée.

## Correction préalable de la métrique

La quantité brute `|H/~_pred|` n'est pas bornée par la dimension quantique : même avec `d_E=2`, une famille continue d'états environnementaux non orthogonaux donne, après SWAP, un continuum de lois futures distinctes. Le rapport cardinal proposé initialement n'est donc pas un bon témoin de dimension finie.

On introduit à la place `N_perf` : taille maximale d'une famille d'histoires ayant le même réduit instantané de `S` et parfaitement distinguables par une même expérience future admise.

## Expérience décisive 1 — produit versus corrélations

### Cas produit

À la coupure, `rho_i^{SE}=sigma_S⊗tau_i^E`. Si une continuation CPTP suivie d'une lecture classique distingue parfaitement les indices, les entrées doivent déjà être parfaitement distinguables. Avec `sigma_S` commun, cela impose des supports de `tau_i^E` orthogonaux, donc `N_perf<=d_E`.

Pour `d_S=d_E=d`, `|0>_S|i>_E` et SWAP saturent : `N_perf=d`.

### Cas corrélé

Pour `d_S=d_E=d`, les `d^2` Bell généralisés `|Phi_{m,n}>` ont tous le réduit `I/d`. Ils sont orthonormaux. Un décodeur commun de la base de Bell donne `|m,n>`, puis deux lectures successives de `S` (la seconde après reset+SWAP) restituent `(m,n)`.

La borne ambiante `N_perf<=dim(S⊗E)=d^2` est donc saturée.

### Contrôle exécuté

Le checker a reconstruit les familles pour `d=2..10` :

- orthogonalité Bell ;
- réduit local identique `I/d` ;
- décodeur unitaire ;
- action SWAP sur la famille produit.

Erreur numérique maximale observée : `<4e-15` ; zéro échec.

**Verdict expérience 1 : PASS.**

## Expérience décisive 2 — adversaire sur la cardinalité prédictive

Pour `d=2`, utiliser `|0>_S⊗|psi_theta>_E` avec `theta∈[0,pi/2]`. Après SWAP et mesure Z de `S`, `P(0|theta)=cos²(theta)`, strictement variable sur l'intervalle.

Il existe donc un continuum de classes prédictives distinctes avec environnement de dimension 2, alors que le nombre d'états parfaitement distinguables reste borné.

Le checker a échantillonné 1001 valeurs et obtenu 1001 probabilités distinctes ; la conclusion principale est analytique.

**Verdict expérience 2 : le cardinal brut des classes prédictives est RÉFUTÉ comme mesure de dimension mémoire.**

## Audit bibliographique

Verdict : **CONNU_OU_CLASSIQUE**.

- Le cadre des process tensors établit déjà que la mémoire de processus est transportée par un environnement effectif et reliée à la dimension de liaison MPO ; ce cadre subsume l'idée qu'un réduit instantané n'est pas, en général, suffisant pour les statistiques multitemporelles.
- Vieira et al., Quantum 8, 1224 (2024), construisent explicitement des témoins de dimension de l'environnement à partir de corrélations temporelles observées sur le système seul.
- Les `d^2` états maximalement intriqués parfaitement distinguables et la capacité correspondante sont le mécanisme standard du dense coding ; Bourdon & Gerjuoy, PRA 81, 022314 (2010), rappellent explicitement le nombre `d^2` pour l'état maximalement intriqué.
- Elliott, arXiv:2610.06519v2 (14 octobre 2026), développe une théorie récente de mémoire causale minimale pour des séquences quantiques corrélées ; portée différente mais confirme que la question générale de mémoire prédictive quantique est un domaine actif et déjà formalisé.

Aucun exact prior art n'est nécessaire pour conclure à la non-originalité générale : chaque composant structurel du théorème est standard. La valeur de la brique est l'interface interne et la séparation nette entre **classes prédictives**, **distinguabilité parfaite** et **corrélations cachées**.

## Redondance interne

`BR-Q-SWAP-MEM-01` ne contient que le témoin binaire `d=2` et la nécessité d'un environnement non trivial. `BR-STATE-01` ne donne aucune borne dimensionnelle quantique. Le nouvel énoncé ajoute :

1. la généralisation exacte produit `d` ;
2. l'amplification corrélée exacte `d^2` ;
3. la réfutation du cardinal brut comme coût mémoire.

Il est donc **non redondant comme brique de raccordement**, bien que connu/classique extérieurement.

## Décision RAVI-2

- vérité : **DÉMONTRÉE interne** ;
- contrôles : **PASS** ;
- originalité : **CONNU_OU_CLASSIQUE** ;
- redondance interne : **NON REDONDANT COMME INTERFACE** ;
- promotion : **OUI**, comme brique de raccordement classique, sans revendication de nouveauté ;
- `DEPEND_DE` nouveau : **AUCUN** ; la preuve est autonome ;
- relations informatives : `GENERALISE -> BR-Q-SWAP-MEM-01` et `ILLUSTRE -> BR-STATE-01`.

ID : `BR-Q-PRED-HIDDEN-01`.