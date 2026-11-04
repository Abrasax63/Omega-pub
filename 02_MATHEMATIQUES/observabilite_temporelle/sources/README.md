# Sources historiques V7–V11 — observabilité temporelle

Ce dossier conserve les sources retrouvées pour la fiche [OBS-V8-FACT-INF](../OBS-V8-FACT-INF.md). Les documents sont des pièces historiques, pas de nouvelles preuves créées lors de leur migration.

## Sources

- [V7 — polynôme temporel et première factorisation](NOTE_RECHERCHE_V7_POLYNOME_TEMPOREL.md)
- [V8 — factorisation exacte à horizon infini](NOTE_RECHERCHE_V8_FACTORIZATION_INFINITY.md)
- [V10 — audit systématique des preuves et de la littérature](AUDIT_V10.md)
- [V11 — seconde preuve indépendante et audit de nouveauté](AUDIT_V11_V8_PREUVE_ET_NOUVEAUTE.md)
- [Contrôle indépendant V8/V9](audit_independant_v8_v9.py)
- [Références V10](REFERENCES_AUDIT_V10.md)
- [Correspondance du cas unaire](correspondance_cas_unaire_connu.csv)
- [Contrôle symbolique de la spécialisation unaire](verification_specialisation_unaire.py)

Les manifestes [V10](manifest_AUDIT_V10.json) et [V11](manifest_AUDIT_V11.json) conservent les empreintes SHA-256 et tailles déclarées dans les archives historiques.

## Provenance et empreintes

- NOTE_RECHERCHE_V7_POLYNOME_TEMPOREL.md — SHA-256 2f0f3f78cfe0726c158ceaab2410a36246f8d3296c163e1e3819e886fe0b4904, 12 246 octets.
- NOTE_RECHERCHE_V8_FACTORIZATION_INFINITY.md — SHA-256 4a9958b65d95c50a3acd9e96f2f52ee16b030142877d6ec2605bdff52c2dce3e, 11 120 octets.
- AUDIT_V10.md — SHA-256 4c0f8c35db9e1acc3efe4e04541c4cb25ebf9c7713596423c81bc65dd5d01942, 13 278 octets. Identique au membre correspondant de l'archive V10.
- AUDIT_V11_V8_PREUVE_ET_NOUVEAUTE.md — SHA-256 90135bd86cc1899e260a84589d323489e9b0960ca36c99dbe3d8b438da16aa81, 6 673 octets. Identique au membre correspondant de l'archive V11.

Archives originales conservées dans la bibliothèque privée, non transférées comme binaires dans GitHub :
- audit_v10_preuves_bibliographie_2026-09-18.zip — SHA-256 a8a5265d54caaac54481f6efd3f93850688b0f1bc596c53f93d7ec284c004f06.
- audit_v11_v8_nouveaute_2026-09-23.zip — SHA-256 f4967197cc0525e87293c9515e3285a5c4f231be775628a88c48a46a4823d329.

## Portée

V10 rapporte une reconstruction indépendante et des contrôles finis. V11 fournit une seconde preuve par coloration des cycles puis propagation dans les arbres de préimages ; il corrige aussi l'appréciation bibliographique : le critère qualitatif et le cas « queue + cycle » sont connus, tandis que la nouveauté de la factorisation générale reste INDÉTERMINÉE.

Les scripts et données sont restaurés comme artefacts historiques. Ils n'ont pas été exécutés pendant cette migration. Aucune validation Lean, revue tierce ou promotion scientifique n'est revendiquée.
