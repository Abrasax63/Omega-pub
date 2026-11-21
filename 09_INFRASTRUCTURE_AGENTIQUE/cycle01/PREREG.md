# OMEGA-CYCLE-01 — préenregistrement du premier cycle de bout en bout

Date : 2026-11-21. Préenregistré **avant de lancer le cycle réel**.

## Objectif et hypothèse falsifiable
Réunir effectivement les modules **source scientifique → routage déterministe → calcul exact OU LLM local → vérification indépendante → mémoire scientifique traçable → rapport de temps/RAM**. Comparer la sortie LLM avec son cache KV désactivé (OFF, mode conservateur) puis activé (ON, condition expérimentale mise en quarantaine). Toute divergence doit rester visible ; aucune réponse du LLM ne devient une preuve.

## Données figées
1. Document mathématique déjà présent dans Omega, `02_MATHEMATIQUES/defauts_recollement/sources/DELTA_H_RECOLLEMENT_INTERNE_2026-09-29.md` : Git blob `0d449a5911b7364d03b5557b24afc3dfc6eef292`. Quatre problèmes exacts définis explicitement dans `TASKS.json` et un de ces problèmes répété deux fois. Aucun modèle n'est appelé pour leurs réponses.
2. Les **six documents synthétiques gelés Reader18** `FROZEN_CASES.json` (Git blob `c522672789a811a3ffa574b6abe5c48599266e6e`) et leurs oracles arithmétiques. Les réponses du LLM servent seulement à sélectionner des lignes sous un parseur strict et le `source_selection()` existant. Ce ne sont **pas** six publications nouvelles ni des labels humains indépendants.
3. Modèle Qwen2.5-0.5B-Instruct Q4_K_M (GGUF SHA256 `74a4da8c9fdbcd15bd1f6d01d621410d31c6fc00986f5eb687824e7b93d7a9db`) ; moteur llama.cpp `5a4afd80779ba51166b59986e61a0bfbb9e1a4c6`.
4. Admission du modèle avec son **rapport de RAM réellement mesurée** dans SCALE01, job `44875280301`, artefact `omega-scale01-0p5b` (ID 14696031972), rapport brut SHA256 `f6f1fae5cae5c79a6c0145496f5f2456311ba76f3b8b7ce22bd3a7a464a34996`. Son statut est `FINISHED`, 709 288 Kio maximum de VmHWM dans le protocole SCALE01. Les 3B ne sont pas chargés par ce cycle ; les mesures SCALE01 3B sont indépendantes.

## Protocole
- Tout calcul exact passe par `AdaptiveBitsetRouter('adaptive-bitset')` de COMPRESS01, puis **deux oracles indépendants préexistants** (`delta_gluing_audit.words` / `trace` et `delta_gluing_crosscheck.matrix_accepts`). Sans accord des trois : erreur bloquante et aucune promotion. La clé de mémoire exacte contient `(T,π,w)` en entier et le Git blob de la source.
- Tous les résultats exacts sont étiquetés `CALCUL_EXACT_VERIFIE`, pour ces systèmes uniquement ; leurs témoins et première obstruction sont enregistrés. Dédoublonnage sur clés intégrales ; calcul répété pour tester la réutilisation, sans supprimer les observations.
- Tout passage du LLM réutilise `paired.prepare`, `paired.messages`, `paired.one_case`, `parse_selection` et `source_selection` **inchangés** ; la sélection admise est seulement une citation de ligne, pas une certification de theorem. Enregistrer texte brut, F1 sur labels synthétiques, refus, provenance et statut `PROPOSITION_LLM_NON_CERTIFIEE`. Une réponse refusée conserve son motif.
- Séquence : démarrer le même serveur Qwen à partir d'un profil contrôlé SHA+RSS, exécuter les 6 lectures OFF, libérer totalement le serveur, le redémarrer sur les mêmes poids puis répéter les 6 lectures ON. Température 0, `n_predict=64`, seed 42, même rendu chat Qwen par `/apply-template`, pas de partage KV entre exécutions. Enregistrement brut des tokens réévalués, du cache, des latences et du RSS.
- Le cache ON n'est **jamais** activé par défaut pour la production : la PR #221 a déjà trouvé des classifications différentes sur sources externes. Les résultats ON sont marqués `EXPERIMENTAL_QUARANTINE` et appariés aux résultats OFF. Divergence ≠ résultat de bonne qualité.
- Stockage scientifique **append-only dans l'artefact du run** (`memory.jsonl` + index + `report.json`) ; pas d'écriture durable sur `main`, aucune modification de pages ou de documents scientifiques. Un rapport inspectable doit contenir les entrées, hashes, décisions, témoins, contrôles, refus, coûts, et anomalies.
- Budget mémoire opérationnel explicite : 6 GiB + réserve 512 MiB ; si le profil source/RAM n'est pas vérifié ou si le serveur dépasse le budget, refuser. Un seul serveur local `127.0.0.1`. Aucun accès API payant ni installation d'un modèle 7B/14B.

## Critères préenregistrés et issues
- Le cycle est **techniquement complet** si tous les jobs s'achèvent, si chaque source est conforme à son Git blob, tous les calculs exacts passent les deux oracles, les 12 sorties LLM reçoivent un statut de parse+gate, et le rapport/mémoire sont archivés.
- Le cache LLM est **localement sans divergence** seulement si les 6 réponses brutes, sources, statuts et sélections ON/OFF sont identiques ; sinon `DIVERGENCE_OBSERVED` et références du cas.
- Les résultats exacts sont **CALCUL EXACT** seulement dans le cadre fini représenté. Ni certification Lean, ni validation humaine de la compétence du LLM, ni gain énergétique mesuré, ni mémoire scientifique persistante inter-runs.
- Régression, données absentes ou artefact inaccessible : `FAILED_OR_INDETERMINATE`, ne pas compenser par un score agrégé.
- Comparer durées, tokens et RSS, mais le coût de compilation/téléchargement des poids est indiqué séparément ; ne pas l'attribuer au cache.

## Sources
- Reader18 + SCALE01 #220/#223 (données/prompt et admission mémoire)
- COMPRESS01 #224 (témoins bitset et mode adaptatif)
- RESIDENCY01 #225 (gestionnaire local résident)
- KV-EXT01 #221 (contre-exemple de divergence sémantique).
