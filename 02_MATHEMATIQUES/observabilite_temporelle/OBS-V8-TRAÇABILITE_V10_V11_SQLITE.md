# OBS-V8-FACT-INF — traçabilité des audits V10/V11 et de la base RAVI-2

**Date de contrôle :** 2026-11-04

## 1. Enregistrement dans SQLite v33

La base RESEARCH_MEMORY.sqlite version 33 contient une entrée active OBS-V8-FACT-INF, version 1 :
- type : THEOREM ;
- statut épistémique : DÉMONTRÉ ;
- originalité : INDÉTERMINÉ ;
- périmètre : endofonction finie T:X→X et colorations finies ;
- version active et autorisée comme prémisse dans le snapshot examiné.

La table evidence contient EVID-OBS-V8-FACT-INF-SRC-HIST-OBS-V10, de type DOCUMENT, locator SRC-HIST-OBS-V10, statut SOURCE_REVIEWED. La table audits contient AUD-HIST-V10-V8, de type INDEPENDENT_RECONSTRUCTION, outcome PASSÉ, exécuté par audit interne indépendant. La source SRC-HIST-OBS-V10 pointe vers l'artefact interne AUDIT_V10.md.

Contrôle local de la copie SQLite v33 effectué le 4 novembre 2026 : PRAGMA integrity_check = ok ; PRAGMA foreign_key_check = aucune anomalie. La base n'a pas été modifiée.

## 2. Contrôles indépendants V10

L'audit V10 documente une reconstruction indépendante des preuves V8 et un comptage brut des colorations par signatures de longueur N−1 :
- toutes les endofonctions pour N≤5, alphabets m=1,2,3 : 10 239 comparaisons, zéro contre-exemple ;
- toutes les 46 656 endofonctions pour N=6, m=2 : zéro contre-exemple ;
- 1 000 endofonctions aléatoires de taille 7, m=2 : zéro contre-exemple ;
- 1 000 endofonctions aléatoires de taille 8, m=2 : zéro contre-exemple ;
- 300 endofonctions aléatoires de taille 6, m=3 : zéro contre-exemple.

Ces calculs sont rapportés dans l'audit interne ; ils n'ont pas été réexécutés pendant la migration GitHub.

## 3. Contrôle indépendant V11

L'audit V11 fournit une seconde preuve de la factorisation : choix de mots primitifs sur les cycles, distinction des rotations pour les cycles de même longueur, puis attribution des couleurs aux arbres de préimages en respectant les fibres. Cette preuve évite l'argument historique du premier instant de fusion pour le comptage.

V11 maintient le statut mathématique DÉMONTRÉ interne, mais l'originalité de la factorisation générale reste INDÉTERMINÉE. Le critère qualitatif et le cas queue + cycle sont identifiés comme connus dans la littérature.

## 4. Portée de la vérification du 4 novembre

- La base v33 a été matérialisée en lecture seule et contrôlée ; aucune ligne n'a été modifiée.
- Les documents V7, V8, V10 et V11 ont été retrouvés et examinés.
- Les scripts historiques n'ont pas été retrouvés ni exécutés.
- La fiche GitHub est une transcription documentaire, pas une nouvelle certification.
- Aucun mapping entre OBS-V8-FACT-INF et CL-DYN-01..04 n'est établi : ces identifiants ne figurent pas dans les entrées results ni historical_claims de la base v33 examinée, et les documents de migration consultés ne donnent pas de correspondance explicite.

## Sources internes

- RESEARCH_MEMORY.sqlite, version 33 ;
- AUDIT_V10.md ;
- NOTE_RECHERCHE_V7_POLYNOME_TEMPOREL.md ;
- NOTE_RECHERCHE_V8_FACTORIZATION_INFINITY.md ;
- AUDIT_V11_V8_PREUVE_ET_NOUVEAUTE.md.

## 5. Sources originales et artefacts restaurés — 4 novembre 2026

Les documents V7, V8, V10 et V11 ont été retrouvés dans la bibliothèque privée puis copiés dans [le dossier sources](sources/README.md), sans réécriture scientifique :

- [Note V7 — polynôme temporel](sources/NOTE_RECHERCHE_V7_POLYNOME_TEMPOREL.md)
- [Note V8 — factorisation à horizon infini](sources/NOTE_RECHERCHE_V8_FACTORIZATION_INFINITY.md)
- [Audit V10 — preuves et bibliographie](sources/AUDIT_V10.md)
- [Audit V11 — preuve alternative et nouveauté](sources/AUDIT_V11_V8_PREUVE_ET_NOUVEAUTE.md)
- [Script indépendant V8/V9](sources/audit_independant_v8_v9.py)
- [Références de l'audit V10](sources/REFERENCES_AUDIT_V10.md)
- [Correspondance du cas unaire](sources/correspondance_cas_unaire_connu.csv)
- [Contrôle symbolique de la spécialisation unaire](sources/verification_specialisation_unaire.py)

Les manifestes d'origine sont conservés dans le même dossier. Les deux fichiers Markdown V10 et V11 ont été comparés aux membres correspondants de leurs archives ZIP : leurs SHA-256 concordent exactement. Les archives binaires restent dans la bibliothèque privée ; elles ne sont pas présentées comme transférées dans GitHub.

**Limite d'exécution :** les scripts restaurés sont des sources historiques. Ils n'ont pas été exécutés pendant cette opération. Leur présence ne vaut ni rejeu des résultats, ni certification Lean, ni validation externe.
