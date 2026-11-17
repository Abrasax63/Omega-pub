# Diagnostic de départ, avant expérience nouvelle — 17 novembre 2026

Ce document analyse **exclusivement** les archives existantes de [PR #140](https://github.com/Abrasax63/Omega-pub/pull/140), sans retester les cas ni modifier les stratégies antérieures. Source : [run #43975864458 (SUCCESS)](https://github.com/Abrasax63/Omega-pub/actions/runs/43975864458), [artefact brut #14281330711](https://github.com/Abrasax63/Omega-pub/actions/runs/43975864458/artifacts/14281330711), rapport JSON SHA-256 **5bb46f7c254cd2d568a87c8ab23318b9829a2561133159ee7423b769eccba300**.

## Validation de l'archive
- 48 machines, 4 bras, budgets 300/500, soit 384 apprentissages.
- Score exact à 500 : RANDOM 46/48, FIXED 45/48, OLD_OMEGA 45/48, COVER 45/48.
- Les seuls systèmes sur lesquels les quatre bras ne partagent pas le même statut d'équivalence exacte à 500 sont : **N4_6, N5_10, N6_7, N6_9, N6_14**. À 300, 17 systèmes présentent au moins une divergence.
- La comparaison COVER vs RANDOM au plafond 500 a W=0, L=1 ; **aucun gain de couverture robuste démontré**.

## Deux traces prioritaires à auditer
**N6_14, budget 500** : RANDOM, FIXED et OLD_OMEGA ont un modèle certifié équivalent avec 6 états ; COVER finit avec **4 états** et un contre-exemple exact **[0,0,1,1]** (longueur 4) fourni par le BFS externe. COVER a dépensé **400 MQ + 100 EQ**, en **7 tours EQ**, avec **10 mots EQ payés et 7 contre-exemples effectivement trouvés**. Ce n'est pas un problème d'absence totale de contre-exemples ; le modèle n'a pas convergé dans le budget. Causes possibles à falsifier : qualité des contre-exemples, dépense de mise à jour de l'observation table, séquence des hypothèses. *Aucune n'est démontrée causalement.*

**N4_6, budget 500** : seule FIXED réussit (469 symboles, 4 états). RANDOM dépense 500, OLD_OMEGA 500 et COVER **498** (248 MQ + 250 EQ) ; ces trois bras finissent sur un candidat à **3 états**, réfuté par le BFS avec **[0,1,0]**. COVER a trouvé **5 contre-exemples** sur 25 mots EQ, et est interrompu pour insuffisance de budget. On ne peut attribuer l'échec à un défaut de sélection sans intervention comparative.

## Limites
L'audit de traces ne permet pas de conclure que le prochain sélecteur fera mieux. Les machines de #140 sont publiques et ne doivent **jamais servir de holdout nouveau**. Le modèle L* provisoire et sa certification exacte par le produit BFS sont deux choses distinctes ; l'égalité des plafonds ne signifie pas égalité des coûts effectivement payés.

Suite préenregistrée indépendamment avant code : [OMEGA-DISAGREE-01](../../experiments/omega-disagreement-01/PREREG_2026-11-17.md). Statut scientifique du nouveau sélecteur : **INDÉTERMINÉ tant que nouveaux runs et preuves ne sont pas vérifiés**.
