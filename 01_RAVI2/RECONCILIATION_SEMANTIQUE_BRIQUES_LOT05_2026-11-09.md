# Réconciliation sémantique des briques — lot 05 — 9 novembre 2026

**Dépôt :** `Abrasax63/Omega-pub`  
**Branche source :** `migration/ravi2-ccs-public-2026-11-04`  
**Commit source inspecté :** `2f71a6b8ed03914c0b5d308520d30e0133d9e9ad`  
**Branche de publication :** `maintenance/reconciliation-bibliotheque-2026-11-05`

## 1. Périmètre

Lecture des 11 reconstitutions ci-dessous dans `research/bricks/reconstructed/`. Elles sont toutes explicitement marquées **RECONSTITUTION — NON ORIGINALE** : les fiches Markdown originales ne sont pas retrouvées ; les fiches sont reconstruites à partir des enregistrements SQLite v33 et compléments documentaires. Leur présence ne prouve pas que les sources originales ni les preuves complètes sont présentes dans le dépôt.

| Fiche | Sujet / énoncé résumé | Statut recopié | Provenance / limites saillantes |
|---|---|---|---|
| APP-OBS-SPARSE-DISJOINT | Sparsification disjointe de la CNF d'observabilité binaire, largeur ≤2L, décomposition exacte des comptes/sommes pondérées | DÉMONTRÉ | Application d'un théorème externe Dell–Husfeldt–Wahlén (2010), dépend de OBS-RESTRICT-COUNT ; preuve importée non reconstruite ici, constantes et gain solveur non établis |
| DELTA-P3-N5 | À n=5, spectre fini non vide D={2}, témoin explicite P3 sans P2 | CALCUL EXACT | Énumération exhaustive rapportée dans le rapport du 17 septembre (162 500 couples) ; pas de test ou énumération rejoués |
| DELTA-SPECTRUM-CLASS | Spectres Δ_h exactement sous-ensembles ultimement périodiques de N≥1 ne contenant pas 1 | DÉMONTRÉ | Rapport historique avec automate unaire, construction à trois macro-états ; comparaison de 13 984 systèmes rapportée, non rejouée ; originalité bibliographique indéterminée |
| DESC-SUM-01 | Somme de 16 évidences de blocs, seuil β^7382 et risque global ≤16β^-7382≤1 % sous le nul spécifié | DÉMONTRÉ | Preuve interne et contrôle rationnel décrits dans les sources ; aucun contrôle rejoué ; aucune amélioration de puissance après rupture garantie |
| EXT-OAI-MARG-REPAIR | Réparation simultanée de deux marginales de permutations, borne TV ≤ ε1+ε2+3ε_part | DÉMONTRÉ | Préprint OpenAI cité et preuve reconstruite ; deux implémentations du même assistant, pas d'audit humain/Lean/réplication tierce ; constante optimale non établie |
| EXT-OAI-MATCH-CORNER | Compression fidèle du coin eD_me d'un diagramme de Brauer et support commun | DÉMONTRÉ | Lemme 2.2(i),(iii) du préprint OpenAI cité ; tests degrés 0..4 rapportés, non rejoués ; ne concerne pas un automate arbitraire |
| EXT-OAI-MATCH-RANK | Inégalités de rang/support des diagrammes de Brauer, borne spéciale pour idempotents | DÉMONTRÉ | Lemme 2.1 et 2.2(ii) du préprint OpenAI cité ; rang = nombre de transversaux, non rang matriciel ; preuves et tests historiques non rejoués |
| EXT-OAI-REL-CORNER | Isomorphisme du coin de relations QR_HQ vers R_F sous P²=P et iPi=i | DÉMONTRÉ | Lemme 2.4 du préprint OpenAI cité ; 448 couples, 1 955 éléments et 275 869 produits annoncés pour 0..3 points, non rejoués ; aucune transposition V19 certifiée |
| EXT-OAI-REL-SELECT | Sélecteurs singleton séparant deux relations binaires distinctes | DÉMONTRÉ | Lemme 5.2 du préprint OpenAI cité ; propriété contextuelle conditionnée à l'autorisation de ces sélecteurs ; toute transposition méthodologique reste non démontrée |
| EXT-OAI-UNIT-LIFT | Relèvement d'un idempotent et réduction des unités dans un coin de rang minimal | DÉMONTRÉ | Lemme 2.3 du préprint OpenAI cité ; ne fournit pas de section homomorphe ; finitude et minimalité essentielles |
| OBS-M27-BINARY | En Mealy binaire sous r_IO=1, collapse ADS/PDS et égalité des profondeurs maximales | DÉMONTRÉ | Note interne du 27 septembre et audit du 14 octobre cités ; formulations plus générales signalées candidates ; ni vérification formelle ni priorité bibliographique certifiées |

## 2. Dépendances et distinctions à préserver

- `APP-OBS-SPARSE-DISJOINT` dépend explicitement de `OBS-RESTRICT-COUNT`. Ne pas confondre l'application du théorème externe de sparsification avec une preuve nouvelle de ce théorème.
- `EXT-OAI-MATCH-CORNER` dépend de `EXT-OAI-MATCH-RANK` ; `EXT-OAI-UNIT-LIFT` dépend de ces deux résultats. Garder distincts compression du coin, bornes de rang/support et relèvement d'idempotent.
- `EXT-OAI-REL-CORNER` concerne le seul coin QR_HQ, pas l'ensemble de R_H.
- `EXT-OAI-REL-SELECT` suppose que les sélecteurs singleton sont des contextes admis.
- `DELTA-P3-N5` est un résultat fini à n=5 ; `DELTA-SPECTRUM-CLASS` est l'énoncé de classification générale. Le premier ne remplace pas le second et les calculs historiques ne sont pas rejoués.
- `DESC-SUM-01` et `OBS-M27-BINARY` sont issus du même ensemble de travaux Mealy/calendriers mais portent sur des contrats différents ; ne pas les fusionner.

## 3. Contrôles adversariaux / état de vérification

Cette opération est une **réconciliation documentaire**, pas une certification mathématique.

- Les 11 fiches ont été récupérées depuis la branche source historique ; leur contenu et les compléments de provenance ont été lus.
- Les statuts SQLite et les mentions PASS/EXECUTED sont rapportés comme déclarations historiques, jamais comme tests exécutés aujourd'hui.
- Aucun script, notebook, vérificateur Lean, calcul exact ou contre-test n'a été exécuté dans ce lot.
- Les liens de sources externes sont des références bibliographiques recopiées ; leur contenu intégral n'a pas été vérifié dans cette opération.
- Aucune base SQLite privée n'a été lue ou modifiée.
- Aucun statut scientifique n'est renouvelé. Les 11 fiches restent des reconstitutions non originales et doivent rester dans `reconstructed/`.

## 4. Traçabilité

Source documentaire : commit `2f71a6b8ed03914c0b5d308520d30e0133d9e9ad` de `migration/ravi2-ccs-public-2026-11-04`.  
Chemins examinés :
- `research/bricks/reconstructed/APP-OBS-SPARSE-DISJOINT_RECONSTITUTION.md`
- `research/bricks/reconstructed/DELTA-P3-N5_RECONSTITUTION.md`
- `research/bricks/reconstructed/DELTA-SPECTRUM-CLASS_RECONSTITUTION.md`
- `research/bricks/reconstructed/DESC-SUM-01_RECONSTITUTION.md`
- `research/bricks/reconstructed/EXT-OAI-MARG-REPAIR_RECONSTITUTION.md`
- `research/bricks/reconstructed/EXT-OAI-MATCH-CORNER_RECONSTITUTION.md`
- `research/bricks/reconstructed/EXT-OAI-MATCH-RANK_RECONSTITUTION.md`
- `research/bricks/reconstructed/EXT-OAI-REL-CORNER_RECONSTITUTION.md`
- `research/bricks/reconstructed/EXT-OAI-REL-SELECT_RECONSTITUTION.md`
- `research/bricks/reconstructed/EXT-OAI-UNIT-LIFT_RECONSTITUTION.md`
- `research/bricks/reconstructed/OBS-M27-BINARY_RECONSTITUTION.md`

**Verdict du lot 05 :** 11/11 reconstitutions classées sur la base des fiches récupérées ; aucun certificat renouvelé et aucune validation indépendante nouvelle. Les reconstitutions ne deviennent pas des briques originales par cette opération.
