# Audit de rattrapage des briques — 19 octobre 2026

## Objet

Comparer l'état scientifique persistant courant avec les certificats et briques documentés dans les cycles récents, afin d'identifier les résultats démontrés/certifiés restés hors de `RESEARCH_MEMORY.sqlite` sans promouvoir les composites, redondances ou résultats indéterminés.

## État de référence

- Base principale avant rattrapage : 77 cartes, 73 admissibles.
- Dernier commit scientifique enregistré : `COMMIT-RAVI2-2026-10-16-MEALY-HELLY-19`.
- Aucune promotion scientifique n'est effectuée par le présent audit.

## Correction d'audit : CL-JET-01

`CL-JET-01` ne doit pas être considérée comme une omission certaine. Le commit `COMMIT_NS_E10_E15_2026-10-15.md` indique explicitement qu'elle n'a pas été ajoutée comme carte séparée car son mécanisme recouvre substantiellement `NS-CERT-E-11`. Décision active : éviter le doublon jusqu'à audit précis de non-redondance.

`CL-FIL-01` est également explicitement conservée comme principe méthodologique et non comme prémisse mathématique autonome.

## A. Briques autonomes verrouillées mais absentes de la base structurée

### A1. NS-CERT-E-01 à NS-CERT-E-09

Le registre `NAVIER_STOKES_BRIQUES_CERT_E_VERROUILLEES_2026-10-15.md` affirme que neuf sous-briques autonomes ont été reconstruites indépendamment sous hypothèses explicites et peuvent être réutilisées sous leurs hypothèses exactes. Elles sont toutefois explicitement restées hors du commit E10–E15 faute de reconstruction de leurs énoncés détaillés dans ce cycle de commit.

Le dossier d'audit `AUDIT_CERTIFICATION_NAVIER_STOKES_2026-10-15.md` décrit les neuf résultats élémentaires :

1. dérivée matérielle le long d'une trajectoire classique ;
2. divergence cylindrique en axisymétrie, avec restriction à l'axe ;
3. identité d'énergie pour solutions forcées régulières ;
4. construction inverse du résidu/forçage ;
5. comptabilité anisotrope volume–énergie sous les échelles supposées ;
6. changement de viscosité par mise à l'échelle ;
7. comptabilité de Reynolds anisotrope ;
8. moyenne nulle avec flux quadratique non nul ;
9. monotonie de la coordonnée de similarité sous les hypothèses indiquées.

**Statut de rattrapage :** candidats prioritaires au prochain commit, mais ne pas attribuer automatiquement les numéros E01..E09 aux énoncés ci-dessus tant que la correspondance canonique exacte n'est pas reconstruite depuis le registre source versionné.

### A2. Certificats autonomes postérieurs explicitement placés en staging

Le registre `NAVIER_STOKES_STAGING_REGISTRY_2026-10-15.md` désigne explicitement plusieurs certificats autonomes à intégrer lors d'un futur commit :

- **NS-X36 — algèbre pondérée** : règles abstraites de produit pour classes pondérées et perte d'ordre sous opérateurs à coefficients contrôlés. Statut documentaire : DÉMONTRÉ / CERT-E autonome. Proposition 6.6 complète : INDÉTERMINÉE.
- **NS-X46 — compensation dérivée–intégration** : estimation dans la norme pondérée, notamment `||∂η I(F)|| <= (80/ρ)||F||`, avec bornes associées. Statut documentaire : DÉMONTRÉ / CERT-E autonome. Le label proposé `NS-CERT-E-16` est en collision et ne doit pas être normalisé automatiquement.
- **B.6 — estimation bilinéaire** : certificat autonome `CERT-C` pour l'estimation explicite dans l'espace pondéré `B_ρ`; ne certifie ni le lemme B.1 complet ni la proposition B.2.
- **Critère abstrait de contraction issu de B.2** : théorème de contraction quantitatif sur une boule de Banach, DÉMONTRÉ / CERT-E autonome ; application intégrale à B.2 encore conditionnelle.
- **NS-X42 — matrice de moments de type Tchebychev** : inversibilité sous exposants distincts et supports strictement ordonnés ; CERT-E autonome admissible, classique.
- **NS-X45 — inverse radial analytique local** : formule coefficient par coefficient pour `Y G'' + ν G' = F`, `ν>0`, solution analytique unique avec `G(0)=0`; CERT-E autonome pour l'identité locale.

**Compte minimal confirmé : 6 certificats autonomes postérieurs absents de la base structurée.**

Avec les neuf sous-briques E01..E09, le backlog autonome minimal est donc de **15 résultats** à auditer pour commit.

## B. Résultats composites/source-vérifiés absents de la base par décision conservatrice

Les artefacts suivants existent et portent un statut `CERT-V composite`, mais ils ne doivent pas être assimilés à des briques démontrées indépendamment admissibles comme prémisses :

- `NS-P55-COMP-01` ;
- `OSC-ITER-01` ;
- `OSC-REAL-01` ;
- `GLOBAL-LOC-01` ;
- sous-certificats P55-A, P55-B, P55-C, P55-D dans l'audit composite.

L'audit composite source-vérifié confirme notamment P55-C pour le mécanisme suffisant des cinq moments et P55-B seulement sur secteurs fixes `|Z| <= 1-ε`. Le théorème principal reste non promu / à réexaminer.

**Décision :** conserver ces éléments en staging documentaire ; ne pas les injecter dans `certified_active_results` sans reconstruction indépendante adaptée au contrat exact.

## C. Éléments à ne pas compter comme nouvelles briques

- `CL-JET-01` : redondance probable avec `NS-CERT-E-11`, audit de différence requis.
- `CL-FIL-01` : principe méthodologique.
- X34, X35, X38 : conséquences abstraites démontrées mais explicitement non promues comme nouveaux CERT-E (classiques/redondantes ou correspondance source incomplète).
- X43, X44 : candidats, non certifiés dans la passe examinée.
- X47 : corollaire probablement redondant.
- X48 : candidat composite, non certifié.
- Proposition B.2 intégrale, lemme B.1 complet, proposition 6.6 complète et théorème principal Navier–Stokes : non certifiés.

## Verdict de rattrapage

1. La première hypothèse « CL-JET-01 oubliée » est réfutée par le journal de commit : non-promotion volontaire pour éviter un doublon.
2. Il existe néanmoins un **backlog minimal confirmé de 15 résultats autonomes certifiés/documentés hors de la base structurée** : neuf E01..E09 plus six certificats autonomes ultérieurs.
3. Il existe en plus une couche de résultats composites/source-vérifiés hors noyau, volontairement non promue.
4. Les 77 cartes / 73 admissibles de la base restent inchangées par cet audit.

## Prochaine opération sûre

Avant tout commit :

1. reconstruire la correspondance canonique exacte de `NS-CERT-E-01..09` ;
2. résoudre les collisions d'identifiants, en particulier autour de `NS-CERT-E-16` ;
3. attribuer des identifiants stables aux six certificats autonomes postérieurs sans réutiliser un numéro ambigu ;
4. créer pour chaque candidat un contrat exact (énoncé, domaine, hypothèses, preuve, limites, source, originalité) ;
5. exécuter un commit RAVI-2 transactionnel, puis reconstruire le miroir v1.3 et vérifier intégrité, clés étrangères, versions, index et snapshot.

Aucune promotion automatique ne doit concerner les composites `CERT-V`, les résultats seulement source-vérifiés, les redondances ou les éléments indéterminés.