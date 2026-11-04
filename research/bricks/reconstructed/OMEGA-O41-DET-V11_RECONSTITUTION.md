# OMEGA-O41-DET-V11 — Ω-O4.1 v1.1 — détection empirique sans noyaux diagnostiques

> **RECONSTITUTION — NON ORIGINALE.** Le Markdown source n’a pas été retrouvé. Fiche reconstruite depuis l’enregistrement SQLite v33 ; elle ne constitue ni une nouvelle validation, ni une promotion du statut, ni une preuve complète.

## Énoncé enregistré

Pour un horizon T, une fenêtre w et un risque δ, si Δ∞=||P_A-P_B||∞>2τ avec τ=sqrt(log(2|A|T/δ)/w), et si chaque régime dure au moins 2w+dδ, alors avec probabilité au moins 1-δ le détecteur à deux fenêtres déclenche exactement une transformation par changement réel, sans fausse transformation, et M≤S dδ. Dans l’instance auditée, Δ∞=29/40; L=480 est le premier L testé satisfaisant le certificat, le gain moyen devient positif à L=768 et la borne certifiée à L=1536.

## Cadre

- Projet `OMEGA_OBSERVATEURS` ; type `THEOREM` ; version `1`.
- Domaine : Cadre fini binaire, canal diagnostique conditionnellement indépendant, ruptures abruptes, deux régimes alternants, classe structurelle candidate fournie.
- Hypothèses : horizon T fixé; fenêtre w; séparation Δ∞>2τ; durée minimale de séjour; canal diagnostique indépendant conditionnellement au calendrier
- Statut SQLite : **DÉMONTRÉ** ; originalité : `NON_EVALUE`.
- Note de confiance SQLite : Version 1.1; le noyau a SURVÉCU_AUDIT avec redérivation indépendante architecturale et énumération finie. Ni vérification formelle ni validation humaine indépendante.

## Preuves et provenance SQLite

- `EVID-OMEGA-O41-DET-V11-SRC-HIST-O41-REPORT` — `DOCUMENT` / `SOURCE_REVIEWED` ; `SRC-HIST-O41-REPORT`.
- `EVID-OMEGA-O41-DET-V11-SRC-HIST-O41-AUDIT` — `DOCUMENT` / `SOURCE_REVIEWED` ; `SRC-HIST-O41-AUDIT`.
- Source `SRC-HIST-O41-AUDIT` (PRIMARY_OR_AUDIT) : rapport_omega_ac_v1_audit_o41.md — `file_000000006094820ca39b996a1030bc12`.
- Source `SRC-HIST-O41-REPORT` (PRIMARY_OR_AUDIT) : rapport_omega_o41_detection_apprise.pdf — `file_00000000048c81f5b7f4dfd323e053bf`.

## Audits et tests enregistrés

- Audit `AUD-HIST-O41-AC` : `SURVÉCU_AUDIT` / `ADVERSARIAL` ; `SRC-HIST-O41-AUDIT`.

## Relations et versions

- `CORRIGE` : `OMEGA-O41-DET-V11` → `OMEGA-O41-MONO480`. La v1.1 remplace la lecture monotone erronée par « première longueur parmi celles testées ».
- Version 1 : `ACTIVE`, prémisse `1`, commit `BASELINE-PRE-COMMIT`.

## Limites

Les statuts, audits et tests sont recopiés de SQLite ; ils n’ont pas été rejoués ni réaudités ici. Les localisateurs ne garantissent pas l’accessibilité des sources. Aucun contenu de preuve absent n’a été inventé. Conserver cette fiche dans `research/bricks/reconstructed/` et ne pas la substituer à l’original. Toute correction ultérieure doit être versionnée selon RAVI-2.

*Reconstitution du 4 novembre 2026 — `RESEARCH_MEMORY.sqlite` v33 — `OMEGA-O41-DET-V11`.*


## Sources retrouvées — complément documentaire

Sources retrouvées : `rapport_omega_o41_detection_apprise.md` et `rapport_omega_ac_v1_audit_o41.md` (audit Ω-AC v1.1). Le cadre est un calendrier déterministe à deux régimes alternants, avec diagnostics conditionnellement indépendants et stationnaires par segment, fenêtres adjacentes de taille w et statistique D_t=||P̂_R−P̂_L||∞. Sous Δ∞>2τ, τ=sqrt(log(2dT/δ)/w), et durée minimale de séjour Γ≥2w+d_δ, le rapport prouve avec probabilité ≥1−δ l'égalité du nombre d'alarmes au nombre de changements, l'absence de fausses alarmes et M≤S d_δ. L'audit Ω-AC rapporte une redérivation architecturale indépendante et une énumération de 2^18 flux sur un modèle réduit, avec zéro violation sur l'événement de concentration. Deux formulations périphériques v1.0 ont été réfutées et corrigées : monotonie erronée du seuil à fenêtre fixe, et mélange preuve/simulation dans un booléen. Verdict du rapport : SURVÉCU_AUDIT, non vérifié formellement ni validé par un tiers. Les seuils L=480/768/1536 sont les premières longueurs testées correspondantes, pas des seuils monotones universels.

> Complément non original ; pas de réaudit indépendant. Statut SQLite inchangé.