# Réconciliation sémantique des briques — lot 01 (11 fichiers)

Date : 9 novembre 2026  
Branche source en lecture seule : `migration/ravi2-ccs-public-2026-11-04`  
Commit source : `2f71a6b8ed03914c0b5d308520d30e0133d9e9ad`  
Branche de publication : `maintenance/reconciliation-bibliotheque-2026-11-05`

## Portée et méthode

Lecture directe du contenu de 11 fichiers individuels de `research/bricks/`, plus lecture de `INDEX_BRIQUES.md` comme index transversal. Les scripts, notebooks et contrôles cités dans ces fichiers n'ont pas été exécutés dans cette passe. Aucun accès ni écriture à SQLite. Aucun fichier source n'a été modifié.

Les statuts ci-dessous sont **les statuts déclarés par les documents sources**, pas des statuts revalidés au 9 novembre. « Non réaudité » signifie que cette passe n'a pas refait la preuve, le calcul, la formalisation ou la revue bibliographique. Les tailles et SHA Git sont repris du manifeste exhaustif et identifient les blobs du commit source.

## Fiches lues

### 1. `BR-CTRL-01_CERTIFICAT_MEMOIRE_INFINIE.md`
- ID : `BR-CTRL-01`, v1 selon l'index.
- Statut déclaré : DÉMONTRÉ ; le fichier revendique CERT-V dans sa source.
- Domaine : système fini déterministe contrôlé, actions totales, mots action-observation.
- Énoncé/mécanisme : automate de trois croyances `(B_w,B_p,B_s)`; infinitude des interdits minimaux caractérisée par un cycle accessible pouvant atteindre un état acceptant.
- Provenance déclarée : `DELTA_H_ACCES_INTERVENTIONS_V1_1_2026-09-29.md`, sections 3–5.
- Dépendances : aucune dépendance formelle explicite indiquée dans la fiche.
- Limites déclarées : ne pas confondre avec profondeur ADS/PDS ni avec une mesure portant seulement sur les observations.
- Contrôle de cette passe : contenu lu ; preuve et borne `8^K` non recalculées ; non réaudité.
- SHA Git source : `3d52e5372f2eaecc6c66d960b0601e727325e2b2`.

### 2. `C4-L2-COEXISTENCE-MINIMUM-9-CONDITIONAL.md`
- ID : résultat complémentaire C4/L=2, fiche créée le 4 novembre ; pas une carte originale retrouvée.
- Statut déclaré : CALCUL EXACT sous la définition primaire V19 ; certification RAVI-2 finale À RÉEXAMINER ; originalité INDÉTERMINÉE.
- Domaine : endofonction totale, cycle distingué C4, observation binaire, huit classes C4O-00…07, contraintes forcées précisées dans la fiche.
- Résultat déclaré : minimum 9 états pour la coexistence des huit classes cataloguées, avec témoin explicite et énumération négative N≤8.
- Provenance déclarée : rapports C4 des 27–28 octobre et audit sémantique du 4 novembre ; scripts nommés dans la fiche.
- Dépendances/conditions : la complétude du catalogue local utilise le lemme L+2 ; la borne globale N≤8 est décrite séparément comme énumération directe.
- Réserves déclarées : formalisation et revue humaine tierce ; la fiche distingue le calcul global du statut du lemme de localité.
- Contrôle de cette passe : aucune exécution des scripts ; non réaudité. Conserver le statut conditionnel et la provenance de fiche reconstruite.
- SHA Git source : `a5ae083bc1edc0fdb553f781eaeb31620d1b5dba`.

### 3. `NAVIER_STOKES_BRIQUES_CERT_E_VERROUILLEES_2026-10-15.md`
- ID : registre de sous-briques NS-CERT-E-01 à 10 ; six fiches E-10 à E-15 figurent séparément dans le corpus.
- Statut déclaré : registre « verrouillé — CERT-E / V-EL » ; portée explicitement limitée aux sous-briques élémentaires.
- Domaine : le contenu détaillé de E-10 porte sur la stabilité d'une marge admissible sous perturbation relative.
- Énoncé E-10 : si la perturbation est bornée par `ε m(T0)`, avec `ε<1`, la marge reste au moins `(1-ε)m(T0)`, sous la norme définissant la marge.
- Provenance déclarée : audits NS du 15 octobre, notamment audit de certification et correspondance Prop. 5.5 / Lei–Ren.
- Dépendances / verrous : P55-A à P55-D, puis P75 et les propositions ultérieures ; la fiche précise que l'existence de la marge dans la construction n'est pas établie par E-10 seul.
- Limite essentielle : ne certifie ni les cartes composites NS-01…26 ni le théorème principal de blow-up.
- Contrôle de cette passe : aucun audit du manuscrit ni de la preuve E-10 ; non réaudité. Ne pas étendre la certification à Navier–Stokes complet.
- SHA Git source : `9b5e9fe6fca3466ab48f6d7fc5dfd23935343181`.

### 4. `NAVIER_STOKES_BRIQUES_RAVI2_2026-10-15.md`
- ID : extraction candidate LIT-NS-01…26 ; ces identifiants sont documentaires, non des IDs de résultats certifiés SQLite.
- Statut déclaré : EXTRACTION CANDIDATE, NON CERTIFIÉE.
- Source primaire déclarée : manuscrit OpenAI *Finite Time Blowup for Navier–Stokes* ; le document précise que les sections 4–10 et annexes A–C n'ont pas été vérifiées ligne à ligne.
- Contenu : 26 éléments classés CLASSIQUE, MÉCANISME SOURCE ou OUTIL ; graphes de dépendances explicitement proposés et non certifiés.
- Contrôles déclarés : quelques identités algébriques et cohérences d'échelle de premier niveau ; elles ne certifient pas le théorème.
- Limite essentielle : le résultat rapporté concerne un système forcé et ne résout pas la régularité non forcée.
- Contrôle de cette passe : aucun manuscrit source externe ouvert ni preuve revue ; non réaudité.
- SHA Git source : `558866c6ac91ea37b25339ba4b8a2f3f87b4ab0c`.

### 5. `OBS-V19-COEX-SMALLMODEL_BRIQUE.md`
- ID : `OBS-V19-COEX-SMALLMODEL` v2.
- Statut déclaré : DÉMONTRÉ, certification interne RAVI-2 ; originalité INDÉTERMINÉE.
- Domaine : endofonction finie, observation binaire, cycle Cq, horizon L≥2, k paires non ordonnées distinctes.
- Énoncé : borne de taille `N ≤ q + 2k(L+3) + max(3,2k)` pour un témoin de coexistence des mêmes k paires.
- Dépendances déclarées : `OBS-V19-LOCAL-L2` puis `OBS-V19-FORCED-P4`.
- Contrôles déclarés : 1 347 familles de 2 ou 3 paires, sans divergence ; ces tests ne remplacent pas la preuve.
- Limites : ne caractérise pas les familles coexistantes ; ne se généralise pas automatiquement hors du domaine indiqué.
- Contrôle de cette passe : preuve et dépendances non vérifiées indépendamment ; non réaudité.
- SHA Git source : `022d58fd7ca0c0fe77e83335ffb8940c632a6db2`.

### 6. `OBS-V19-C5-CAPACITY_BRIQUE.md`
- ID : `OBS-V19-C5-CAPACITY` v2.
- Statut déclaré : DÉMONTRÉ, certification interne RAVI-2 ; originalité INDÉTERMINÉE.
- Domaine : cycle orienté C5, observation binaire, horizon L=3, contraintes forcées cohérentes.
- Résultat déclaré : 70 ombres orientées exactes ; 50 capacités finies, 20 infinies ; spectre fini {2,4,8,12,16,32}.
- Dépendances déclarées : `BR-OBS-CAP-01`, `OBS-V19-C5-ORIENTED14`, `OBS-V19-FORCED-P4`.
- Limites : une capacité individuelle ne résout pas les contraintes de ressources partagées entre ombres différentes ; distinction explicite entre occurrences et coefficients de circuits.
- Contrôle de cette passe : tables, preuves et données non recalculées ; non réaudité.
- SHA Git source : `bc4b3eea112aeae4d7dcaac7bb79b52f0452d7d6`.

### 7. `BR-WORD-TWO-EQUAL-GAPS-COMPLEX-01_BRIQUE.md`
- ID : `BR-WORD-TWO-EQUAL-GAPS-COMPLEX-01` v1.
- Statut déclaré : DÉMONTRÉ interne ; originalité INDÉTERMINÉE.
- Domaine : mots cycliques paramétrés par g, δ≥1 et 1≤a<b ; longueur T=(a+b)g+2δ.
- Énoncé : formule fermée de complexité cyclique et description des facteurs spéciaux, dans le domaine de paramètres indiqué.
- Provenance déclarée : preuve autonome dans `REPRISE_MULTI_GAP_2026-10-20.md`, certificat JSON et scripts de reproduction datés du 20 octobre.
- Contrôles déclarés : deux campagnes de familles/longueurs ; le document reconnaît une revue interne par le même assistant et l'absence de revue humaine, d'autre modèle ou de vérification formelle.
- Limites : cas a=b exclu ; originalité non déterminée.
- Contrôle de cette passe : aucune reproduction ni vérification de la preuve ; non réaudité.
- SHA Git source : `f6808ee1fad8ba6215695e2bd77867067660c8d4`.

### 8. `BR-OBS-CAP-03_FIBER_BOX_TU.md`
- ID : `BR-OBS-CAP-03`.
- Statut déclaré : DÉMONTRÉ, interne RAVI-2 ; originalité décrite comme reformulation spécialisée d'un principe général.
- Domaine : ensemble fini de témoins P et application `σ:P→Ω`, chaque témoin affecté à un motif unique.
- Énoncé : pour un système fixé, les multiplicités sélectionnables forment la boîte produit des intervalles `{0,…,ν(ω)}`; la matrice d'incidence à un 1 par colonne est TU.
- Dépendance déclarée : `BR-OBS-CAP-01`.
- Limite essentielle : les témoins sont sélectionnables indépendamment ; les états sous-jacents peuvent se recouvrir entre témoins, donc ne pas les traiter automatiquement comme ressources exclusives.
- Application déclarée : `OBS-V19-COEX-REGION), sous hypothèse cofinale supplémentaire.
- Contrôle de cette passe : preuve élémentaire non rejouée formellement ; non réaudité.
- SHA Git source : `e2db670f4f9458a848b7d8719f2a656dbfdab46b`.

### 9. `BR-AFFINE-GAUGE-CORE_BRIQUE.md`
- ID : `BR-AFFINE-GAUGE-CORE` v1.
- Statut déclaré : DÉMONTRÉ interne ; originalité/classicité : application interne, aucune priorité revendiquée.
- Domaine : espaces vectoriels finis sur F₂, sous-espaces et phases linéaires relevant du contrat GAUGE-GLUE.
- Énoncé : compatibilité d'une translation commune équivalente à la compatibilité des équations sur les bases ; noyau minimal par inclusion de taille ≤d+1, borne annoncée serrée.
- Dépendances déclarées : `BR-AFFINE-GAUGE-GLUE`, `BR-AFFINE-GROUP-CORE`.
- Contrôles déclarés : 242 270 familles exhaustives, 10 000 aléatoires, 5 000 changements de base, trois méthodes.
- Limite : minimalité par inclusion, pas nécessairement cardinalité minimale.
- Contrôle de cette passe : calculs et trois implémentations non relancés ; non réaudité.
- SHA Git source : `798ce8f646d9d283b7244410522c607c27f75f4c`.

### 10. `BR-MEALY-HELLY-01_BRIQUE.md`
- ID : `BR-MEALY-HELLY-01` v1.
- Statut déclaré : DÉMONTRÉ interne ; originalité INDÉTERMINÉE.
- Domaine : machine de Mealy finie, complète, déterministe, q sorties et `r_IO=1), état de connaissance accessible.
- Énoncé : toute non-face minimale du nerf de compatibilité a taille ≤q−1 ; borne annoncée atteinte pour q≥3.
- Dépendances déclarées : `OBS-M27-FERTILE`, `OBS-M27-SPECTRUM`.
- Contrôles déclarés : 21 machines C(q,k), 492 états accessibles, 1 337 nerfs, zéro violation.
- Limites : aucune borne sur longueur/complexité du PDS ; pas d'extension sans r_IO=1.
- Contrôle de cette passe : preuve et recherche indépendante non relues/rejouées ; non réaudité.
- SHA Git source : `389957f14632fb253434202a46727ace8688b512`.

### 11. `BR-R90-01_NOYAUX_PERIODES.md`
- ID : `BR-R90-01`.
- Statut déclaré : DÉMONTRÉ dans l'audit cité.
- Domaine : règle 90 sur cycle de taille N, opérateur `A_N=z+z^{-1}` sur F₂, décomposition N=2ᵃm avec m impair.
- Énoncés : formule de dimension du noyau transitoire ; période maximale de la composante récurrente.
- Provenance déclarée : audit règle 90 du 22 août 2026, sections 2 et 4.
- Limite : ne donne pas la période de chaque état ni celle d'une observation particulière.
- Contrôle de cette passe : audit source non relu et formules non recalculées ; non réaudité.
- SHA Git source : `5f05b98f301af8331c5fa0fe19448385c5c983fb`.

## Constats transversaux et anomalies à garder ouvertes

1. **Divergence de compte dans l'index.** L'index conserve un texte historique « 83 cartes admissibles », tandis que son en-tête de migration rapporte 85 résultats SQLite (74 DÉMONTRÉ, 11 CALCUL EXACT). Le fichier précise que le compte 83 n'est pas courant. Ce n'est pas résolu par la lecture des briques ; conserver les deux énoncés avec leurs dates et ne pas recalculer un total à partir de cet index.
2. **Certificats Navier–Stokes : portée strictement atomique.** Le registre verrouillé interdit explicitement d'étendre E-01…E-10 au théorème principal ou aux 26 cartes composites. Le document d'extraction RAVI-2 est lui-même candidat et non certifié ; les deux fichiers ne doivent pas être amalgamés.
3. **C4/L=2 : statut conditionnel, pas certification finale.** La fiche décrit un calcul exact sous une définition primaire et réserve formalisation/revue tierce. La lecture seule de cette fiche ne valide pas le lemme L+2.
4. **C5 : dépendances non transférées.** La fiche de capacité cite plusieurs briques et rapports. L'existence des noms de dépendances dans le texte n'établit pas que leurs preuves sources sont déjà liées au modèle agentique.
5. **Niveau de contrôle.** Les nombres de tests rapportés sont des déclarations des artefacts historiques. Aucun de ces tests n'a été relancé pendant ce lot.

## Verdict du lot

- 11/11 fichiers individuels lus intégralement (l'index `INDEX_BRIQUES.md` a été lu séparément comme index transversal).
- Classification documentaire effectuée pour ces 11 fichiers : IDs, statuts déclarés, domaine, énoncés, provenance, dépendances, contrôles déclarés et limites.
- 0 preuve ou script réexécuté ; 0 statut scientifique revalidé ; 0 certificat renouvelé.
- 0 fichier de la branche historique modifié ; 0 écriture SQLite.
- Les 83 autres fichiers de `research/bricks/`, les 47 revues et les 44 artefacts de reproductibilité restent à classifier sémantiquement.

Ce lot est une annexe de traçabilité, pas une promotion de statut et pas une intégration du corpus au moteur agentique.
