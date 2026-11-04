# Bibliothèque des instruments mathématiques

**Version :** 0.1  
**Date :** 2026-11-04  
**Statut :** EXPÉRIMENTAL — registre initial vide.

## Objet

Ce sous-module conserve les méthodes intermédiaires isolables : constructions, lemmes, réductions, invariants, estimations, schémas de preuve et certificats de calcul.

Il est distinct du registre des théorèmes. L'instrument peut être connu dans la littérature, dépendre d'hypothèses fortes ou ne pas être transférable au-delà de son application d'origine.

## Navigation

- [Registre des instruments](REGISTRE_INSTRUMENTS.md)
- [Modèle de fiche d'instrument](MODELE_INSTRUMENT.md)
- [Protocole d'extraction RAVI-2](../../01_RAVI2/PROTOCOLE_EXTRACTION_METHODES.md)
- [Pilote C4 : état documentaire](PILOTE_C4_ETAT.md)

## Règles

1. Un instrument reçoit un ID stable et une version.
2. Sa source exacte et son emplacement doivent être indiqués.
3. Les hypothèses d'application font partie de l'instrument.
4. Nouveauté, validité, formalisation Lean et transférabilité sont évaluées séparément.
5. Un instrument candidat n'est pas une brique certifiée.
6. Aucun résultat C4 historique n'est reconstitué à partir d'un simple résumé.
