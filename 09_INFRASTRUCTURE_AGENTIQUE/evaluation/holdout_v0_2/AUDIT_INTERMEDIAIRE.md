# P5 v0.2 — audit intermédiaire du corrigé et de la disponibilité du holdout

**Date :** 2026-11-10  
**Branche :** `audit/p5-hardening-2026-11-09`  
**Statut :** audit partiel ; aucun pilote exécuté.

## 1. Intégrité du corrigé privé

Fichier contrôlé dans l'environnement de travail : `answer_key.private.corrected.json`.

- JSON : parse réussi.
- Cinq identifiants présents : `P5V2-FORMAL-001`, `P5V2-COMPUTE-001`, `P5V2-DOC-001`, `P5V2-EXPL-001`, `P5V2-ADV-001`.
- SHA-256 recalculé sur les octets du fichier : `4963c72faafbab9bc0abfdb963b3de6e3142f4e9ea1307af88f4358e27ee043a`.
- Le digest correspond à celui publié dans `evaluation/holdout_v0_2/manifest.json`.

## 2. Vérifications exactes reproductibles réalisées

### P5V2-COMPUTE-001

Les fibres du corrigé déterminent la fonction totale sur X={0,…,6} :
`0↦1, 1↦2, 2↦1, 3↦2, 4↦5, 5↦6, 6↦6`.

Un script indépendant a reconstruit la fonction à partir des fibres et recalculé :
- image {1,2,5,6} ;
- multiplicités (0,2,2,0,0,1,2) ;
- point fixe {6} ;
- cycles (1 2) et (6) ;
- distances à un cycle atteint : (1,0,0,1,2,1,0) dans l'ordre 0,…,6 ;
- partition des sept états et somme des tailles de fibres égale à 7.

Tous ces contrôles concordent avec le corrigé.

### P5V2-FORMAL-001

Le contre-modèle fourni a été instancié explicitement. Le script confirme que f est injective sur le singleton A, que g n'est ni injective ni surjective, et que g∘f est injective.

### P5V2-EXPL-001

Les deux applications sont totales sur les quatre états. Les deux parcours partant de a1 projettent sur A→B→A. Le quotient macroscopique de T1 est déterministe ; celui de T2 ne l'est pas, car les successeurs observés des états d'une même fibre ne coïncident pas.

## 3. Vérifications restant à faire

- P5V2-DOC-001 : contrôler la formulation normative et les conclusions contre le texte primaire RFC 8259 §4.
- P5V2-ADV-001 : reconstruire les deux extensions sur le même ensemble et vérifier formellement les propriétés annoncées.
- Relire les cinq énoncés exacts et les confronter un à un au corrigé.
- Auditer la proximité conceptuelle et les fuites possibles avec v0.1.

## 4. Blocage principal découvert

Le répertoire public `evaluation/holdout_v0_2/` ne contient actuellement que `manifest.json`. Aucun `cases.jsonl` v0.2 n'y est présent. Le fichier privé retrouvé est le corrigé ; il ne suffit pas à reconstruire avec certitude les énoncés exacts.

En conséquence, il est impossible de vérifier complètement l'alignement énoncé/corrigé, de préparer des sessions A/B/C reproductibles ou de conclure que le holdout est indépendant du jeu public v0.1. Ne pas fabriquer les énoncés à partir du corrigé.

## 5. Comparaison limitée avec le v0.1 public

Les cinq strates se recoupent nécessairement, mais les thèmes visibles des corrigés ne sont pas identiques aux cas v0.1 connus. Cette comparaison de thèmes ne prouve pas l'indépendance : sans les cinq énoncés v0.2 exacts et leur provenance, l'audit anti-fuite reste ouvert.

**Verdict :** `ANSWER_KEY_INTEGRITY_PARTIALLY_CHECKED / HOLDOUT_NOT_AUDITABLE_YET / PILOT_NOT_READY`.
