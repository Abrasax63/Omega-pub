# Audit de rapprochement des 32 cartes historiques — 4 novembre 2026

## Objet et correction de vocabulaire

Le rapport de couverture historique précédent recensait 32 identifiants dont les fiches Markdown originales autonomes n'avaient pas été retrouvées. La vérification des 32 fichiers `research/bricks/reconstructed/<ID>_RECONSTITUTION.md` de la branche de migration montre que chacun contient désormais un complément intitulé « Sources retrouvées » qui rattache la carte à un ou plusieurs artefacts historiques.

Il faut donc distinguer trois choses :

1. **Fiche originale autonome** : toujours non retrouvée pour les 32 identifiants au cours de cet audit.
2. **Trace/source documentaire** : une référence explicite à un document, rapport ou artefact historique est maintenant présente dans les 32 reconstitutions.
3. **Rejeu ou certification** : non effectué par le présent rapprochement. Les statuts SQLite copiés dans les reconstitutions ne sont pas promus et les anciens calculs ne sont pas réputés reproduits.

La formulation « 32 résultats sans source » serait donc incorrecte. La formulation exacte est : **32 fiches originales autonomes non retrouvées ; 32 reconstitutions documentées par des références de sources ; disponibilité octet-par-octet et réexécution non établies pour toutes les sources.**

## Matrice des 32 identifiants

| Identifiant | Source(s) historique(s) référencée(s) dans la reconstitution | Réserve principale |
|---|---|---|
| APP-OBS-SPARSE-DISJOINT | `DECOMPOSITION_BRIQUES_LOT2_2026-10-15.md`, §4 ; Dell–Husfeldt–Wahlén, ECCC TR10-078 (2010), appendice A, lemme 6 | Preuve asymptotique importée ; pas de reconstruction/recompilation dans cet audit. |
| DELTA-P3-N5 | `rapport_spectre_defauts_iteration_1.md`, §5 | Énumération historique de 162 500 couples rapportée ; non rejouée ici. |
| DELTA-SPECTRUM-CLASS | `rapport_spectre_defauts_iteration_1.md`, §§1–5 | Classification documentée ; contrôles historiques non rejoués ici, originalité indéterminée. |
| DESC-SUM-01 | `detection_correlations_2026-10-14.md` ; `COMMIT_AUDIT_RAVI2_2026-10-14.md` ; `commit_audit_checks.json` | Preuve/contrôles rationnels historiques non rejoués dans cette mise à jour. |
| EXT-OAI-MARG-REPAIR | `EXTRACTION_BRIQUES_OPENAI_2026-10-15.md`, carte 2 ; préprint *Random coordinate frames and partial permutation laws*, §16.1, lemme 16.2 | Reconstruction interne rapportée ; pas de réplication tierce ni d'optimalité établie. |
| EXT-OAI-MATCH-CORNER | `DECOMPOSITION_BRIQUES_LOT2_2026-10-15.md`, §1 ; préprint OpenAI, lemme 2.2(i),(iii) | Résultat limité au coin idempotent ; pas de transfert universel. |
| EXT-OAI-MATCH-RANK | `EXTRACTION_BRIQUES_OPENAI_2026-10-15.md`, carte 3 ; préprint OpenAI, lemmes 2.1–2.2(ii) | Rang transversal, non rang matriciel ; originalité non revendiquée. |
| EXT-OAI-REL-CORNER | `DECOMPOSITION_BRIQUES_LOT2_2026-10-15.md`, §3 ; préprint OpenAI, lemme 2.4 | Isomorphisme du seul coin spécifié ; pas de transfert automatique à V19. |
| EXT-OAI-REL-SELECT | `EXTRACTION_BRIQUES_OPENAI_2026-10-15.md`, carte 1 ; préprint OpenAI, §5, lemme 5.2 | Dépend de contextes/sélecteurs autorisés ; toute transposition méthodologique reste séparée. |
| EXT-OAI-UNIT-LIFT | `DECOMPOSITION_BRIQUES_LOT2_2026-10-15.md`, §2 ; préprint OpenAI, lemme 2.3 | Finitude et choix d'un idempotent de rang minimal indispensables ; pas de section de groupe. |
| OBS-M27-BINARY | `Adaptivity boundary - Mealy machines.docx`, note du 27 septembre 2026, §§1–5 | Le document qualifie certaines extensions de candidates ; pas de revue externe/formalisation. |
| OBS-M27-CONFLICT | Même document, §§4–5 | Résultat de conflict core candidat ; revue externe en attente. |
| OBS-M27-FERTILE | Même document, §§1 et 3 | Originalité non établie ; mécanisme rapproché de l'ambiguïté bornée classique. |
| OBS-M27-SPECTRUM | Même document, §§5–6 | Famille constructive rapportée ; résultats généraux encore candidats en attente de revue externe. |
| OBS-RESTRICT-COUNT | `CYCLE_MULTIAGENT_OBSERVABILITE_2026-10-15.md`, section OBS-RESTRICT-COUNT | Contrat CNF/largeur documenté ; largeur bornée ne suffit pas à conclure une taille polynomiale en L. |
| OBS-RESTRICT-GREEDY | Même document, section OBS-RESTRICT-GREEDY | Contrôle conditionnel documenté ; si la borne initiale est ≥1, le critère est inconclusif. |
| OBS-RESTRICT-OVERLAP | `TEST_SYNTHESE_INVERSE_2026-10-15.md`, brique 2 | Covariance nulle ne prouve pas l'indépendance ; pas d'extension aux oppositions forcées V19. |
| OBS-RESTRICT-PROFILE | Même document, brique 1 | Profil des tailles récupérable, pas la topologie du graphe ; données bruitées insuffisantes. |
| OBS-V19-C5-13 | `NOTE_RECHERCHE_V19_GRAMMAIRE_ORBITALE(2).md` ; `NOTE_RECHERCHE_V19_FORME_NORMALE_13_OMBRES.md` | Distinguer la version 13 types de l'ancienne version 12 ; énumération historique non rejouée ici. |
| OBS-V19-C5-ORIENTED14 | `V19_ASSEMBLAGE_ORIENTE_2026-10-15.md` ; `V19_MULTIPLICITE_CAPACITE_2026-10-15.md` | 14 classes orientées modulo rotations ; ne pas quotienter par réflexion sans preuve. |
| OBS-V19-FORCED-P4 | `NOTE_RECHERCHE_V19_GRAMMAIRE_ORBITALE(2).md` ; `COMMIT_AUDIT_RAVI2_2026-10-14.md` | Les 50 069 endofonctions et 29 742 cas cohérents sont des contrôles historiques, non rejoués ici. |
| OBS-V19-GAMMA-CONNECTED | `NOTE_RECHERCHE_V19_GRAMMAIRE_PROFONDEUR_PHASE.md` | Contrat distinct à 12 types sur bassin connecté ; ne pas fusionner avec la classification globale à 13. |
| OBS-V19-LOCAL-L2 | `NOTE_RECHERCHE_V19_GRAMMAIRE_ORBITALE(2).md` ; `V19_ASSEMBLAGE_ORIENTE_2026-10-15.md` | Les comparaisons global/local ne remplacent pas la preuve de localité ; vérifier l'encodage de l'ombre. |
| OBS-V19-PAIR-COMPLETE14 | `V19_ASSEMBLAGE_ORIENTE_2026-10-15.md` ; `V19_MULTIPLICITE_CAPACITE_2026-10-15.md` | Compatibilité des labels de classes ; pas une loi générale pour toutes copies géométriques. |
| OBS-V19-TRIPLE-COMPLETE13 | Mêmes deux rapports V19 | Complétude au niveau des 13 labels D5 ; chiralité des 14 classes orientées non capturée par D5. |
| OBS-V19-UNIVERSAL10 | `V19_MULTIPLICITE_CAPACITE_2026-10-15.md` ; `V19_UNIVERSAL10_U42_2026-10-15.json` | Témoin constructif jusqu'à k=10 ; ne prouve pas que 10 soit une capacité maximale générale. |
| OBS-V8-FACT-INF | `AUDIT_V10.md`, section V8 | Reconstruction et contrôles historiques rapportés ; originalité indéterminée, non rejoués ici. |
| OBS-V9-RANK | `AUDIT_V10.md`, section V9 | Exhaustivité historique n≤6 rapportée ; non rejouée ici. |
| OBS-V9-STAB-N1 | `AUDIT_V10.md`, section V9 stabilisation | Résultat explicitement redondant avec le théorème antérieur de raffinement des partitions. |
| OMEGA-O41-DET-V11 | `rapport_omega_o41_detection_apprise.md` ; `rapport_omega_ac_v1_audit_o41.md` | Verdict documentaire SURVÉCU_AUDIT ; pas de vérification formelle ni validation tierce. |
| Q-RQ4-COMMON-RANK | `NOTE_RANG_RECOLLEMENT_CONTEXTUEL_2026-09-30.md`, RQ-Q-4, §2 | Hypothèses de factorisation et complétude tomographique indispensables ; pas de conclusion causale sur les acquisitions publiques. |
| Q-RQ4-PAULI-ROBUST | Même note, §3 | Borne optimale pour une question scalaire seulement ; pas une réalisation CPTP tomographique complète. |

## Vérification de la branche GitHub

- La branche examinée est `migration/ravi2-ccs-public-2026-11-04`, via la PR brouillon #2 vers `main`.
- Les 32 chemins correspondants présents dans la PR sont les 32 fichiers `research/bricks/reconstructed/*_RECONSTITUTION.md`.
- Chacun des 32 fichiers a été relu sur la branche et son empreinte GitHub a été relevée pendant le contrôle.
- Les fiches originales autonomes correspondantes ne sont pas présentes dans la liste des fichiers modifiés de la PR ; les reconstitutions portent explicitement la mention « RECONSTITUTION — NON ORIGINALE ».
- Des rapports V19 complémentaires sont déjà dans la PR, notamment `reviews/V19_ASSEMBLAGE_ORIENTE_2026-10-15.md`, `reviews/V19_MULTIPLICITE_CAPACITE_2026-10-15.md` et `reviews/V19_BADOBJECT_*.md`. Plusieurs sources historiques identifiées ci-dessus demeurent dans la Bibliothèque et ne sont pas intégrées à la PR.
- Aucune modification de `main`, aucune fusion, aucune écriture dans SQLite et aucune promotion de statut n'ont été effectuées.

## Verdict

**Rapprochement documentaire : COMPLET pour les 32 identifiants au niveau des références de source inscrites dans les reconstitutions.**

**Récupération des 32 fiches originales : NON RÉALISÉE.** Une référence à un artefact source n'est pas l'artefact lui-même ; la disponibilité binaire, l'identité octet-par-octet et les empreintes des documents historiques ne sont pas établies pour les 32 cas dans ce passage.

**Rejeu scientifique : NON EFFECTUÉ.** Les résultats historiques restent à leurs statuts antérieurs. Ce rapport n'est ni une validation mathématique ni une nouvelle certification RAVI-2.

## Suite sûre

1. Matérialiser les sources historiques de la Bibliothèque une par une, calculer leurs empreintes et les comparer aux empreintes enregistrées dans SQLite quand elles existent.
2. Prioriser les sources qui portent plusieurs cartes : rapport spectre Δ, note Mealy27, note V19 grammaire, audit V10, rapports d'assemblage V19, documents RQ-Q-4 et rapports OAI.
3. Rejouer uniquement les tests discriminants manquants, sans exécuter les scripts historiques qui écrivent dans SQLite.
4. Ne remplacer aucune reconstitution par un original tant que le fichier original et son empreinte ne sont pas effectivement retrouvés.
