# P5 v0.3 — audit de proximité avec le holdout public v0.1

**Date :** 2026-11-10  
**Branche :** `audit/p5-hardening-2026-11-09`  
**Périmètre :** comparaison des cinq énoncés v0.3 avec les cinq énoncés publics v0.1 présents dans le dépôt sur cette branche.  
**Verdict :** `ANTI_LEAK_NOT_CERTIFIED / THREE_HIGH_SIMILARITY_CASES / HOLDOUT_NOT_FROZEN`.

## 1. Sources examinées

- v0.1 : `evaluation/holdout_v0_1/cases.jsonl`.
- v0.3 : `evaluation/holdout_v0_3/cases.jsonl`.
- Corrigé privé v0.3 local : `answer_key.private.v0.3.json` ; SHA-256 vérifié : `e5ca5caba84ff3f5f6d11d01bcd4e23752f58b47e495af43f39f1561340907d1`.
- Source documentaire du cas v0.3 DOC : RFC 3986, RFC Editor, https://www.rfc-editor.org/rfc/rfc3986.html.

## 2. Comparaison cas par cas

| v0.3 | Cas v0.1 le plus proche | Appréciation |
|---|---|---|
| FORMAL-001 — surjectivité de (f\circ g) | FORMAL-001 — injectivité équivaut à surjectivité pour un endomorphisme fini | **Faible à modérée** : domaine de logique des fonctions et propriétés injective/surjective commun, mais question, structure logique et preuve attendue différentes. |
| COMPUTE-001 — fibres, multiplicités, cycles et bassins d'une application finie | COMPUTE-001 — image, fibres, points fixes et cycles d'une application finie | **Très élevée** : même type d'objet, même représentation par table de fonction, mêmes opérations principales et même style de vérification. Ajouter les distances et bassins ne rend pas ce cas suffisamment indépendant. |
| DOC-001 — encodage et normalisation URI (RFC 3986) | DOC-001 — méthodes HTTP safe/idempotent (RFC 9110) | **Faible** : documentation normative et citation de RFC sont communes au format, mais les normes, concepts et raisonnements techniques sont distincts. |
| EXPL-001 — trajectoire observée et quotient déterministe caché | EXPLORATORY-001 — trajectoire finie observée et non-identifiabilité des propriétés globales | **Très élevée** : même problème épistémique central, à savoir ce qu'une observation de trajectoire permet ou ne permet pas d'inférer sur le système caché. Le quotient ajoute une formalisation, mais ne rompt pas la proximité. |
| ADV-001 — injectivité testée sur un sous-ensemble propre | ADVERSARIAL-001 — injectivité n'implique pas surjectivité en général | **Élevée** : les deux cas testent une inférence abusive autour de l'injectivité et attendent un contre-exemple fini. Les formulations diffèrent, mais le concept et la stratégie de réfutation se recouvrent fortement. |

## 3. Conclusion anti-fuite

L'indépendance de v0.3 par rapport à v0.1 **n'est pas certifiée**. Trois cas sur cinq (COMPUTE, EXPL, ADV) sont des proches voisins conceptuels du jeu public. Ils ne doivent pas être utilisés comme épreuves aveugles pour mesurer une capacité indépendante de v0.1.

Cette conclusion ne signifie pas qu'une fuite effective de réponses est démontrée. Elle signifie que la séparation conceptuelle requise pour un holdout indépendant n'est pas établie et que le risque de contamination est trop élevé.

## 4. Réparations nécessaires

1. Remplacer COMPUTE par un problème de calcul exact d'une autre famille (par exemple arithmétique modulaire, combinatoire ou optimisation discrète), sans fonction d'itération, fibres ni cycles.
2. Remplacer EXPL par un problème d'explication où l'enjeu n'est pas l'inférence à partir d'une trajectoire observée ni la reconstruction d'un quotient.
3. Remplacer ADV par un contre-exemple sur une autre propriété logique ou mathématique, sans injectivité/surjectivité.
4. Faire relire les cinq nouveaux énoncés et leurs corrigés par un évaluateur qui n'a pas participé à leur rédaction.
5. Recalculer le digest du fichier final après chaque modification et mettre à jour le manifeste depuis les octets effectivement gelés.

## 5. Décision opérationnelle

- Ne pas lancer le pilote A/B/C sur v0.3 dans son état actuel.
- Ne pas présenter le holdout comme indépendant ou aveugle.
- Ne pas modifier le corrigé v0.2 ni prétendre avoir retrouvé ses énoncés.
- Garder la PR #9 en brouillon et ne pas fusionner dans `main`.

**Statut :** `V0_3_REQUIRES_REVISION / ANTI_LEAK_NOT_CERTIFIED / PILOT_NOT_READY`.
