# Audit de traçabilité des 32 fiches reconstituées — 4 novembre 2026

Branche : `migration/ravi2-ccs-public-2026-11-04`  
Base de référence : SQLite v33, consultée en lecture seule.  
Périmètre : les 32 fichiers de `research/bricks/reconstructed/`.

## Verdict

**TRAÇABILITÉ DOCUMENTAIRE PARTIELLE — AUCUNE REVALIDATION SCIENTIFIQUE.**

Les 32 fichiers de reconstitution sont présents dans l'arbre Git de la branche. La lecture des fiches confirme le marquage explicite « RECONSTITUTION — NON ORIGINALE », la copie du statut SQLite et une réserve indiquant que les audits/tests cités n'ont pas été rejoués dans le cadre de la reconstitution. Aucun des 32 fichiers ne se présente comme l'original restauré.

Cet audit contrôle la structure documentaire et les références déclarées. Il ne constitue pas une relecture mathématique indépendante de 32 preuves, ni une validation de la disponibilité de chaque archive historique binaire.

## Contrôles établis

1. **Présence dans Git :** 32/32 chemins de reconstitution sont présents sous `research/bricks/reconstructed/`.
2. **Distinction original/reconstitution :** les fiches contrôlées portent explicitement la mention « RECONSTITUTION — NON ORIGINALE ».
3. **Réserve épistémique :** les fiches indiquent que statuts, audits et tests sont recopiés de SQLite et n'ont pas été rejoués ou réaudités au moment de la reconstruction.
4. **Statuts :** aucun statut scientifique n'a été modifié dans SQLite v33 ; cette migration documentaire n'est pas une certification nouvelle.
5. **Sources hétérogènes :** les fiches renvoient selon les cas à des rapports internes, audits, sources primaires externes, scripts et sorties exactes. Ces catégories ne sont pas interchangeables.

## Regroupement des 32 fiches et réserves propres

| Groupe | Identifiants | Sources citées dans les fiches | Réserve à conserver |
|---|---|---|---|
| Observabilité clairsemée | APP-OBS-SPARSE-DISJOINT | Rapport de décomposition ; Dell–Husfeldt–Wahlén, ECCC TR10-078 | Application d'un théorème importé ; preuve globale de sparsification non réauditée ici. |
| Spectres Delta | DELTA-P3-N5 ; DELTA-SPECTRUM-CLASS | Rapport historique sur les spectres ; note ultérieure distincte | Ne pas confondre les périmètres ; calculs historiques non rejoués ici. |
| Détecteur somme | DESC-SUM-01 | Note détection corrélations ; audit de commit ; script et JSON de contrôles | Certification interne bornée ; aucune puissance après rupture démontrée. |
| Extraction OpenAI / diagrammes | EXT-OAI-MARG-REPAIR ; EXT-OAI-MATCH-CORNER ; EXT-OAI-MATCH-RANK ; EXT-OAI-REL-CORNER ; EXT-OAI-REL-SELECT ; EXT-OAI-UNIT-LIFT | Prépublications OpenAI citées ; rapport d'extraction/décomposition ; archives de preuves | Les fiches ne remplacent pas les PDF ni les preuves sources complètes ; pas de validation Lean générale. |
| Machines de Mealy | OBS-M27-BINARY ; OBS-M27-CONFLICT ; OBS-M27-FERTILE ; OBS-M27-SPECTRUM | DOCX « Adaptivity boundary - Mealy machines » ; audit de commit ; contrôles Python/JSON | Le dépôt contient une extraction textuelle du DOCX, non son binaire original ; limites de portée et absence de formalisation externe à préserver. |
| Restriction / observabilité | OBS-RESTRICT-COUNT ; OBS-RESTRICT-GREEDY ; OBS-RESTRICT-OVERLAP ; OBS-RESTRICT-PROFILE | Rapports multiagent et synthèse inverse ; archives de preuves et contrôles exacts | Preuves internes reconstruites et tests historiques cités ; ne pas convertir les résultats PASS en certification externe. |
| V19 C5 / L2 | OBS-V19-C5-13 ; OBS-V19-C5-ORIENTED14 ; OBS-V19-FORCED-P4 ; OBS-V19-GAMMA-CONNECTED ; OBS-V19-LOCAL-L2 ; OBS-V19-PAIR-COMPLETE14 ; OBS-V19-TRIPLE-COMPLETE13 ; OBS-V19-UNIVERSAL10 | Notes V19 ; rapports d'assemblage et de capacité ; scripts et CSV/JSON | Les périmètres et versions V19 doivent rester séparés. Le workflow C5 reproduit le calcul ciblé, pas l'intégralité de l'historique ni une comparaison octet par octet de tous les exports. |
| Audits historiques V8/V9 | OBS-V8-FACT-INF ; OBS-V9-RANK ; OBS-V9-STAB-N1 | AUDIT_V10 et sources historiques associées | L'audit historique est cité ; les artefacts sources complets ne sont pas tous restaurés comme fichiers autonomes dans ce contrôle. |
| Ω-O4.1 | OMEGA-O41-DET-V11 | Rapport PDF O41 ; audit Ω-AC | Le statut SQLite est conservé ; ne pas déduire de validation supplémentaire de la seule présence des rapports. |
| Quantique RQ4 | Q-RQ4-COMMON-RANK ; Q-RQ4-PAULI-ROBUST | Note de rang/recollement ; audit de commit ; script et JSON de contrôles | Résultat interne de domaine borné ; ne vaut pas validation externe ni transfert à d'autres cadres. |

## Points de vigilance transversaux

- Les références de fichiers internes qui commencent par `/Recherche/` désignent les chemins historiques de la Library. La restauration de certains documents dans Git ne prouve pas que toutes les archives ZIP, tous les binaires et toutes les versions sont présents dans le dépôt.
- Les références de sources externes sont des antécédents bibliographiques cités ; elles ne prouvent pas à elles seules la totalité de l'énoncé de la fiche.
- Un audit ou test marqué PASS dans SQLite est un événement historique rapporté, pas une exécution effectuée pendant cet audit documentaire.
- Les fiches Mealy dépendent d'une source DOCX dont le dépôt conserve une extraction Markdown signalée comme telle. Les différences de mise en page, tableaux ou objets incorporés ne sont pas garanties.
- Les fiches V19 et RQ4 peuvent citer les mêmes rapports, scripts ou sorties de contrôle pour plusieurs résultats. Cela documente une provenance partagée, mais ne doit pas être interprété comme autant de réplications indépendantes.
- Les 32 fiches restent dans le répertoire `reconstructed/`. Ne pas les déplacer dans les cartes originales et ne pas les compter comme 32 originaux retrouvés.

## Décisions

- Conserver les 32 fiches comme reconstitutions documentaires.
- Ne pas créer automatiquement de liens d'évidence dans SQLite v33.
- Ne modifier aucun statut, aucune dépendance et aucune conclusion scientifique.
- Ne pas fusionner la PR sur la base de cet audit seul.
- Pour une certification ultérieure, traiter les verrous par groupe : récupérer les archives et scripts sources manquants, vérifier leurs empreintes, rejouer les contrôles décisifs, puis conduire une revue adversariale indépendante de l'énoncé et de sa portée.

## Provenance de cet audit

Contrôle effectué sur l'arbre GitHub de la branche de migration et sur le contenu des fiches de reconstitution. Les conclusions ci-dessus sont strictement documentaires. Aucun calcul mathématique ni script historique n'a été présenté comme exécuté dans cette opération.
