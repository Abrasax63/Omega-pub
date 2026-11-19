# READER17 — préenregistrement prospectif de trois documents non utilisés dans Reader13–16

**Date : 2026-11-19.** Ce document est commité **avant lecture des trois sources** et avant rédaction du code expérimental. Aucun réglage des prompts ou des règles en fonction des textes/réponses.

## Question scientifique locale
Sur des documents mathématiques différents des deux fiches R90, le pipeline Reader13/Reader16 généralise-t-il à une extraction de lignes candidates et à une sélection par un modèle 3B, sans citations inventées ni promotion ? Comparer plusieurs politiques sources-only et quantifier le coût d'entrée, **sans prétendre mesurer la vérité mathématique**.

## Cohorte figée à partir de la liste de noms, tailles et Git blobs uniquement
Les fichiers sont présents sur l'arbre de base de PR #185 et sur `main` ; ils n'ont pas servi au classement Reader13–16 BR-R90. L'absence de toute exposition historique à Omega ou au modèle préentraîné **n'est pas garantie**.

1. `02_MATHEMATIQUES/defauts_recollement/RECONCILIATION_CL_DYN_01_04.md` — Git blob `93a66d75605060a4a70185eabc04e07c1fd3f06b`, 10100 octets.
2. `02_MATHEMATIQUES/observabilite_temporelle/RECONCILIATION_CL_DYN_OBS_V8.md` — Git blob `3716a258530a7f7aefecddd18acd7d7ae694c1f7`, 3093 octets.
3. `02_MATHEMATIQUES/observabilite_temporelle/sources/AUDIT_V11_V8_PREUVE_ET_NOUVEAUTE.md` — Git blob `bf10028da39306aedec6c4e1567d501172552258`, 6672 octets.

## Politiques fixées avant lecture des fichiers
A : `select_packets` Reader13 + ancienne extraction des seules lignes `=` / `est exactement uniforme` + `gate`. C'est le témoin existant.

C : politique Reader16 — toutes lignes de 6–500 caractères appartenant aux paquets sous un titre `énoncé` ou `enonce`, filtrées par `gate`.

D : généralisation syntaxique *préengagée* de C à des titres comportant `énoncé`, `enonce`, `proposition`, `théorème`, `theoreme`, `résultat`, `resultat`, `lemme` ou `corollaire`. Le filtre `gate` de Reader12 reste identique.

Chaque politique prend au maximum les **12 premières lignes candidates** selon l'ordre source. Le cap s'applique **après** `gate`. Des lignes hors cap ne peuvent pas être sélectionnées. Aucun gold ne participe à ce choix. A, C, D gardent les mêmes 3 documents, et reportent le pool complet et le pool tronqué ; aucune modification du filtre source.

## Sélecteur 3B unique et budget
- Modèle **Qwen2.5-Coder-3B-Instruct Q4_K_M**, fichier GGUF SHA256 `724fb256bec1ff062b2f65e4569e871ad2e95ab2a3989723d1769c54294730b7` ; binaire llama.cpp au commit `5a4afd80779ba51166b59986e61a0bfbb9e1a4c6`.
- Un seul appel de Qwen par document ET par politique non vide (0–9 appels), glouton, max 128 jetons en sortie, pas de nouvelle requête/réparation si invalide. **Un seul prompt** de classement strict d'IDs pour toutes les politiques, avec consigne de choisir au plus 5 lignes de conclusions. Les entrées sont des listes de `line, section, source_text`, la source reste du matériau non fiable.
- Le sélecteur retourne `NONE` ou jusqu'à 5 numéros séparés de virgules. S'il produit Markdown, prose, ID étranger, doublons ou plus de 5 choix : REFUS. Source `literal` et `packet_id` reconstruits uniquement du blob Git puis passés à `gate`.
- **Budget non parfaitement égalisé** entre politiques (nombre et longueur de candidats variables) : consigner jetons d'entrée/sortie, durée, nombre d'appels, pool size. Aucune comparaison causalement à coût égal ne peut être revendiquée.
- Comparateurs sans modèle pour **chaque politique** : `select first five`, `select all up to cap`, `always NONE` ; ils sont des contrôles de couverture, pas des scores de vérité.

## Mesures et critères
Pour chaque document × politique : source_blob vérifié, nombre de paquets et lignes visibles, candidats avant/après cap, raison de rejet gate, raw Qwen, parsing strict, ID hors source, lignes acceptées, abstentions, alarmes, jetons, secondes, nombre de certifications (doit être 0). Tous les résultats y compris `NO_CANDIDATES`, infra-failure et retours malformés doivent être archivés.
**Faisabilité réussie** si : 3 blobs identiques au gel, tests de sécurité réussis, au moins une politique produit des candidats, inférences réelles exécutées pour tous les pools non vides, 0 citation fictive admise et 0 promotion. **Amélioration sémantique** : non revendiquée sans annotations humaines réellement indépendantes sur les lignes de ces sources. Réponses acceptées `QUARANTINE` ne prouvent rien.
Aucune modification `main`, aucun entraînement de poids, aucune fusion, aucune API payante. Prochaine validation scientifique : gold/annotation indépendante **à constituer avant** de comparer les réponses à ce gold, sans exposer les réponses à l'annotateur. L'indépendance de l'annotation n'est actuellement **pas vérifiée**, donc toute conclusion de supériorité est interdite.
