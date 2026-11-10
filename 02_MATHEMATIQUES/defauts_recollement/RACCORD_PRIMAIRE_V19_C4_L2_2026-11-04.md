# Raccord primaire V19(2) ↔ C4, L=2 — audit de fermeture du verrou

Date : 2026-11-04  
Branche : `pilot/ravi2-extraction-c4-20261104`  
Statut : **RACCORD SÉMANTIQUE VÉRIFIÉ SUR LA SOURCE PRIMAIRE INTERNE** ; résultat global **CALCUL EXACT**.

## 1. Retrouvaille documentaire

La note primaire n'était pas absente. Elle se trouve à :

`/Recherche/02_PROGRAMMES_ACTIFS/Observabilite/Notes/NOTE_RECHERCHE_V19_GRAMMAIRE_ORBITALE(2).md`

Identifiant : `file_0000000018ec8211b9fee091c47e349f`. Document daté du 25 septembre 2026, 359 lignes, récupéré intégralement le 4 novembre.

L'audit de bibliothèque du 14 octobre indiquait déjà une lecture partielle de ses lignes 1–120. La reprise a lu le document complet, notamment les sections 2 à 4. L'ancien rapport de quotients affirmait à tort que la version (2) n'avait pas été retrouvée ; cette affirmation est corrigée.

## 2. Correspondance exacte des définitions

### A. Domaine

V19(2) traite une endofonction totale finie T, une observation binaire c, un cycle distingué B=Cq avec q≥3, une paire distincte {x,y} et un horizon L≥2.

Le dossier fixe q=4 et L=2 : les hypothèses de domaine du théorème primaire sont satisfaites.

### B. Mauvais événement

V19(2), section 4, définit les égalités du mauvais événement par :
`c(T^t x)=c(T^t y)` pour `0≤t<L`.

À L=2, cela donne exactement :
- c(x)=c(y) ;
- c(Tx)=c(Ty).

Les programmes omettent la comparaison si les deux états sont identiques : c'est la diagonale de la dynamique des paires, pas une contrainte supplémentaire.

### C. Contraintes forcées singleton

V19(2), section 2, démontre pour tout L≥2 :
`|H_L({u,v})|=1 iff T(u)=T(v) or {T(u),T(v)}={u,v}`.

En binaire, la paire singleton impose c(u)≠c(v). Les scripts utilisent exactement cette disjonction, y compris le cas invariant (points fixes distincts ou 2-cycle). Ils ne réduisent pas le critère aux seules fibres de même image.

### D. Cohérence globale

V19(2), section 3, démontre que les composantes du graphe forcé cohérent sont P1, P2, P3 ou P4. Les programmes globaux vérifient le graphe complet des contraintes forcées et sa bipartition, ainsi que la taille maximale 2 des fibres. C'est conforme au théorème de structure primaire.

### E. Projection et localité

V19(2), section 4, démontre que l'ombre sur B est entièrement déterminée par B et les deux préfixes :
`x,Tx,…,T^(L+2)x` et `y,Ty,…,T^(L+2)y`.

Pour L=2, les préfixes vont jusqu'à T^4 inclus. Le vérificateur indépendant `verify_c4_l2_9state.py` construit précisément ces préfixes, leur union avec le C4, puis énumère les contraintes de parité et les colorations projetées. Les deux autres vérificateurs calculent directement sur tous les états du système et n'ont pas besoin de la réduction locale pour le calcul de l'ombre.

### F. Quotient par rotations

La canonisation applique chaque rotation simultanément à tous les masques d'une ombre. L'audit du 28 octobre avait corrigé la version antérieure qui canonisait chaque masque indépendamment. Cette convention est maintenue dans les calculs et dans l'audit des quotients.

## 3. Exécutions vérifiées

- Deux vérificateurs globaux historiques matérialisés et relancés : huit ombres exactes ; énumération exhaustive des fonctions de tailles N=4,…,8 sans témoin.
- Vérificateur local indépendant `verify_c4_l2_9state.py` matérialisé et exécuté : PASS pour les huit classes sous le préfixe L+2.
- Audit des congruences : deux algorithmes distincts de génération donnent 49 congruences identiques ; 9 quotients conservent cycle, paires et cohérence ; un seul conserve les huit classes, la partition discrète à 9 états.
- 120 renommages des cinq états transitoires : les huit classes restent invariantes.

Note de provenance : l'algorithme de quotients a été réimplémenté dans une exécution Python séparée. Le script correspondant a été ajouté à GitHub et récupéré, mais ne doit pas être décrit comme exécuté tel quel tant que son exécution directe n'est pas enregistrée.

## 4. Verdict corrigé

- Critère singleton : **DÉMONTRÉ dans V19(2)** et encodé à l'identique.
- Structure P1–P4 : **DÉMONTRÉ dans V19(2)**.
- Mauvais événement L=2 : correspondance exacte, égalités aux temps 0 et 1.
- Petit modèle L+2 : **DÉMONTRÉ dans V19(2)** ; borne temporelle 4 inclus.
- Témoin simultané à 9 états : **CALCUL EXACT**, vérifié par deux programmes globaux et un vérificateur local indépendant.
- Absence de témoin N=4,…,8 : **CALCUL EXACT**, énumération exhaustive sous le prédicat primaire.
- Minimalité N=9 pour le problème C4, L=2 et le catalogue C4O-00…07 : **CALCUL EXACT**.
- Absence de quotient propre du témoin : **CALCUL EXACT** sous le contrat vérifié.
- Originalité bibliographique : **INDÉTERMINÉE**.
- Formalisation Lean : **NON RÉALISÉE**.

Le verrou sémantique « définition primaire ↔ contrat opérationnel » est **FERMÉ** pour ce périmètre. Cela ne constitue ni une revue bibliographique exhaustive ni un certificat Lean.

## 5. Correction de l'état antérieur

Le statut « À RÉEXAMINER » provenait d'une absence documentaire temporaire et d'une traçabilité incomplète, pas d'une contradiction mathématique. La note primaire était dans la bibliothèque et avait été partiellement lue le 14 octobre. Le 4 novembre, le document complet a été retrouvé, relu et raccordé explicitement au cas C4, L=2.

Aucune modification de `main` n'est effectuée. La PR reste en brouillon pour revue.
