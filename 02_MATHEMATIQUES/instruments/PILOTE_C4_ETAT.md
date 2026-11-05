# Pilote d'extraction — dossier C4

**Version :** 0.2 — corrigée le 5 novembre 2026  
**Statut documentaire :** l'état préliminaire v0.1 est dépassé.

## Correction de l'état préliminaire

La version 0.1 indiquait qu'aucun calcul C4 n'avait été exécuté et que les sources primaires restaient à retrouver. Cet état était exact pour le premier instantané du pilote, mais il est désormais dépassé.

Le 4 novembre 2026, la note primaire interne V19(2) a été retrouvée intégralement (359 lignes), relue, puis raccordée explicitement au contrat C4, L=2. Les vérifications et limites sont consignées ici :

- [Pilote complet C4, L=2](../defauts_recollement/PILOTE_EXTRACTION_C4_L2_2026-11-04.md)
- [Raccord primaire V19(2) ↔ C4, L=2](../defauts_recollement/RACCORD_PRIMAIRE_V19_C4_L2_2026-11-04.md)
- [Audit des quotients du témoin à 9 états](../defauts_recollement/AUDIT_QUOTIENTS_TEMOIN9_C4_L2_2026-11-04.md)
- [Vérificateurs et scripts](../defauts_recollement/code/)

## État corrigé

- **Domaine :** endofonctions finies, observation binaire, cycle C4, horizon L=2.
- **Résultat :** CALCUL EXACT sous la définition primaire interne V19(2), pour les huit classes C4O-00 à C4O-07.
- **Témoin :** dynamique à 9 états, vérifiée par deux programmes globaux et un vérificateur local indépendant.
- **Borne inférieure :** énumération exhaustive N=4,…,8 sans témoin, dans le périmètre décrit par le raccord primaire.
- **Quotients :** 49 congruences produites par deux algorithmes ; un seul quotient préserve les huit classes, le quotient discret à 9 états. L'exécution directe du script d'audit de quotients n'est pas revendiquée ; une réimplémentation séparée a été exécutée.
- **Originalité bibliographique :** INDÉTERMINÉE.
- **Formalisation Lean :** NON RÉALISÉE.
- **Publication :** EXPÉRIMENTAL, en attente de revue.

## Limites

Ce résultat ne généralise pas automatiquement à d'autres tailles de cycle q ou à d'autres horizons L. Il ne ferme pas la question de l'originalité bibliographique et ne remplace pas une formalisation Lean.

Le pilote C4 est un cas issu de notre corpus interne V19. Il ne constitue pas, à lui seul, l'extraction démontrée d'un instrument depuis un manuscrit du corpus externe OpenAI.
