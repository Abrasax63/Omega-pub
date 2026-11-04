# PILOTE-EXT-C4-L2 — Extraction d'instruments et audit reproductible

- **Identifiant :** PILOTE-EXT-C4-L2-2026-11-04
- **Version :** 0.2
- **Domaine :** systèmes dynamiques finis / observation binaire / V19
- **Statut scientifique :** CALCUL EXACT sous la définition primaire V19(2) pour le problème C4, L=2 et le catalogue C4O-00…07
- **Statut de publication :** EXPÉRIMENTAL — branche pilote, non fusionnée
- **Date :** 2026-11-04

## 1. Question testée

Peut-on extraire d'un dossier de recherche antérieur une méthode reproductible, l'isoler comme instrument, la vérifier par une seconde implémentation et conserver clairement les limites de portée ?

Le cas choisi est le dossier C4, L=2 : réalisation des huit classes d'ombres C4O-00 à C4O-07 dans une même dynamique finie, puis vérification de la borne inférieure de taille.

## 2. Sources historiques récupérées

- `RESULTATS_C4_L2_CLASSES_2026-10-27.md` : catalogue local de huit classes.
- `AUDIT_V19_C4_L2_REPRISE_2026-10-28.md` : témoin à neuf états et énumération exhaustive jusqu'à huit états.
- `CERTIFICAT_CONDITIONNEL_V19_C4_L2_2026-10-28.md` : spécification opérationnelle et portée conditionnelle.
- `NOTE_RECHERCHE_V19_GRAMMAIRE_ORBITALE(2).md` : source primaire interne du critère singleton, du graphe forcé P1–P4 et du théorème de petit modèle L+2. Fichier de 359 lignes, récupéré intégralement et relu le 2026-11-04.
- `verify_c4_l2_9state.py` : vérificateur indépendant utilisant les préfixes jusqu'au temps 4.

L'audit du 14 octobre indiquait déjà une lecture partielle (lignes 1–120) de la note V19(2). La reprise du 4 novembre a retrouvé le fichier complet et fermé explicitement le raccord C4, L=2. Voir `RACCORD_PRIMAIRE_V19_C4_L2_2026-11-04.md`.

## 3. Instrument extrait

### EXT-FINITE-PROJECTION-COLORING v0.2

**Principe :** pour une endofonction totale finie T, une observation binaire et les contraintes forcées V19, calculer exactement l'ensemble des colorations projetées sur un cycle distingué.

**Définition des contraintes forcées (V19(2), section 2) :** pour u≠v, imposer c(u)≠c(v) si et seulement si T(u)=T(v) ou {T(u),T(v)}={u,v}.

**Mauvais événement à horizon L=2 :** imposer c(x)=c(y) et c(Tx)=c(Ty), en omettant les comparaisons diagonales.

**Projection :** ensemble des motifs binaires sur les quatre états du cycle C4 qui admettent une extension globale satisfaisant les contraintes forcées et les deux égalités de trajectoire.

**Préconditions :**
- endofonction totale finie ;
- observation binaire ;
- cohérence globale des contraintes forcées ;
- cycle distingué C4 ;
- horizon L=2.

**Réduction locale justifiée :** V19(2), section 4, prouve que l'ombre est déterminée par le cycle et les préfixes jusqu'au temps L+2, donc jusqu'à t=4 inclus ici.

## 4. Témoin global

Dynamique :
`T = (1,2,3,0,8,7,6,2,0)`

Cycle distingué : 0 → 1 → 2 → 3 → 0.

Les huit paires historiques :
- C4O-00 : (0,1)
- C4O-01 : (0,2)
- C4O-02 : (1,8)
- C4O-03 : (0,7)
- C4O-04 : (0,6)
- C4O-05 : (4,5)
- C4O-06 : (1,4)
- C4O-07 : (0,4)

Les ombres brutes recalculées sont :
- C4O-00 : {0,7,8,15}
- C4O-01 : {0,5,10,15}
- C4O-02 : {2,7,8,13}
- C4O-03 : {1,6,9,14}
- C4O-04 : {0,3,4,7,8,11,12,15}
- C4O-05 : {0,1,4,5,10,11,14,15}
- C4O-06 : {4,5,6,7,8,9,10,11}
- C4O-07 : {2,3,6,7,8,9,12,13}

## 5. Résultats des exécutions du 2026-11-04

### Vérificateur A — `code/audit_v19_c4_l2_equalites.py`

- témoin : PASS, 8/8 ombres brutes ;
- variante avec inégalités de trajectoire : 1/8 ombre brute identique ;
- N=4 : 1 fonction examinée, 1 cohérente, aucun témoin ;
- N=5 : 5 fonctions examinées, 5 cohérentes, aucun témoin ;
- N=6 : 36 fonctions examinées, 32 cohérentes, aucun témoin ;
- N=7 : 343 fonctions examinées, 263 cohérentes, aucun témoin ;
- N=8 : 4096 fonctions examinées, 2695 cohérentes, aucun témoin.

### Vérificateur B — `code/certificat_v19_c4_l2_global.py`

- témoin global : PASS, les huit masques bruts correspondent ;
- énumération N=4 à N=8 : mêmes totaux, mêmes nombres de fonctions cohérentes, aucun témoin.

### Vérificateur indépendant local — `verify_c4_l2_9state.py`

Matérialisé et exécuté le 2026-11-04. Il reconstruit les deux préfixes de trajectoire jusqu'à t=4, applique le critère V19 exact sur le petit modèle, puis énumère les colorations projetées du C4. Sortie : PASS pour les huit classes.

Les deux programmes globaux calculent directement sur tous les états. Le vérificateur local teste séparément le théorème de petit modèle L+2.

### Concordance et portée

Les trois vérifications concordent sur les huit ombres du témoin. Les deux programmes globaux sont des implémentations distinctes du même contrat ; le vérificateur local apporte une vérification séparée de la réduction temporelle.

## 6. Contre-test

La variante où les trajectoires imposent des inégalités au lieu des égalités ne reproduit qu'une seule des huit ombres brutes. Cette variante est réfutée comme interprétation du mauvais événement V19 dans ce dossier.

## 7. Verdict RAVI-2

- Critère singleton V19 : **DÉMONTRÉ dans la source primaire interne**.
- Structure P1–P4 : **DÉMONTRÉ dans la source primaire interne**.
- Localité temporelle L+2 : **DÉMONTRÉ dans la source primaire interne**.
- Témoin simultané à 9 états : **CALCUL EXACT**, reproduit par deux vérificateurs globaux et un vérificateur local.
- Absence de témoin pour N=4,…,8 : **CALCUL EXACT**, énumération exhaustive.
- Minimalité N=9 pour le catalogue C4O-00…07 : **CALCUL EXACT** sous la définition primaire V19(2).
- Originalité bibliographique : **INDÉTERMINÉE**.
- Certification Lean : **NON RÉALISÉE**.

Le verrou sémantique entre définition primaire et contrat opérationnel est fermé pour ce périmètre. Aucune généralisation à d'autres q ou L n'est revendiquée.

## 8. Dépendances et provenance

- Catalogue C4, L=2 du 27 octobre.
- Note primaire V19(2), sections 2–4.
- Audit de reprise C4 du 28 octobre.
- Deux vérificateurs globaux et un vérificateur local.

Les fichiers ont été récupérés depuis la bibliothèque de recherche et les programmes mentionnés ont été réellement matérialisés puis exécutés le 4 novembre 2026.

## 9. Verdict du pilote d'architecture

**PILOTE RÉUSSI pour la chaîne documentaire et le raccord scientifique dans le périmètre testé.**

La méthode d'extraction conserve les définitions primaires, distingue les calculs de leurs preuves, compare des implémentations différentes et ne promeut pas l'originalité bibliographique ni la formalisation Lean sans preuve.
