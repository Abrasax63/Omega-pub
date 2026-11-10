# P5 v0.3 — audit initial du nouveau holdout

**Date :** 2026-11-10  
**Branche :** `audit/p5-hardening-2026-11-09`  
**Statut :** candidat créé ; non gelé ; pilote non autorisé.

## 1. Origine et décision de version

La recherche dans les fichiers de conversation et la bibliothèque a retrouvé les corrigés privés v0.2, mais pas les cinq énoncés originaux. L'inspection GitHub du répertoire `evaluation/holdout_v0_2/` confirme qu'il ne contient que le manifeste et l'audit intermédiaire, sans `cases.jsonl`.

Les énoncés v0.2 n'ont donc pas été reconstruits depuis le corrigé. Un nouveau candidat v0.3 a été rédigé séparément. Les cas v0.3 ne sont pas des reformulations des réponses v0.2. Cela ne suffit toutefois pas à certifier l'indépendance statistique ou conceptuelle vis-à-vis de v0.1 : cette vérification reste ouverte.

## 2. Contenu public

Le fichier `cases.jsonl` contient cinq cas, un par strate :
- `P5V3-FORMAL-001` : conséquence logique de la surjectivité d'une composition ;
- `P5V3-COMPUTE-001` : fibres, cycles, points fixes, distances d'entrée en cycle et bassins d'une application finie ;
- `P5V3-DOC-001` : normalisation des URI selon RFC 3986 ;
- `P5V3-EXPL-001` : déterminisme d'un quotient observé et insuffisance d'une trajectoire unique ;
- `P5V3-ADV-001` : limite d'une vérification d'injectivité sur un sous-ensemble propre.

## 3. Contrôles effectivement exécutés

Un script Python local a :
- parsé les cinq lignes JSONL ;
- vérifié l'unicité des cinq identifiants ;
- vérifié l'égalité de l'ensemble des identifiants entre énoncés et corrigé privé ;
- reconstruit les fibres de la fonction du cas COMPUTE ;
- vérifié que les tailles des fibres totalisent huit états ;
- retrouvé les cycles `(2)`, `(3,4,5)` et `(7)`.

Le contre-modèle FORMAL a été contrôlé algébriquement : la composition est surjective, tandis que (g) n'est pas surjective et (f) n'est pas injective.

Pour EXPL, les deux états de fibre observée (R) ont des successeurs d'observations différentes : (π(T(s0))=S) et (π(T(s1))=R). Le quotient déterministe échoue donc bien.

Pour ADV, le contre-exemple fini minimal utilise un domaine de cardinal deux et un sous-ensemble propre non vide de cardinal un.

La source primaire RFC Editor a été consultée pour DOC. RFC 3986 §2.1 confirme l'insensibilité à la casse des chiffres hexadécimaux ; §2.2 protège les caractères réservés contre une normalisation qui changerait leur interprétation ; §6.2.2.2 prévoit la normalisation par décodage des seuls caractères non réservés. Source : https://www.rfc-editor.org/rfc/rfc3986.html.

## 4. Empreintes

- SHA-256 de `cases.jsonl` : `f017aa007c4f89a4790434c813b6174589ea39a0e86e42dd6fa93568cbcb343d`.
- SHA-256 du corrigé privé local : `e5ca5caba84ff3f5f6d11d01bcd4e23752f58b47e495af43f39f1561340907d1`.
- Le corrigé privé n'est pas dans le dépôt. Le manifeste ne publie que son nom et son empreinte.

## 5. Limites et portes encore ouvertes

- Audit de proximité/fuite contre le jeu public v0.1 : non certifié.
- Revue humaine indépendante des cinq énoncés et du corrigé : à faire.
- Barème détaillé et tests négatifs du validateur : à finaliser.
- Configuration A/B/C, snapshots, budget, randomisation, aveuglement et évaluateurs : non gelés.
- Aucun bras expérimental n'a été exécuté.

**Verdict :** `V0_3_CANDIDATE_CREATED / INTERNAL_CHECKS_PARTIAL / HOLDOUT_NOT_FROZEN / PILOT_NOT_READY`.
