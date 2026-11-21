# EXTERNAL-MEMORY-01 — préenregistrement avant le test du 21 novembre 2026

## Objectif et périmètre
Faire tourner le cycle Omega **sur huit nouveaux fichiers mathématiques tiers** (pas utilisés dans ProofNet26 #211 ni KV-EXT01 #221), contrôler les associations entre énoncé naturel et théorème Lean de référence, relever les erreurs du vrai Qwen local puis **publier uniquement les observations vérifiées** dans une mémoire Git durable, à part du journal des propositions incertaines. Aucune écriture sur `main`, aucune API payante.

## Corpus gelé
- Dépôt externe `marcusm117/ProofNet-Verified`, commit `b7ca411a2abaa6caf3580192b30d865e5bd10bc4`. Source Apache-2.0.
- Huit fichiers **nouveaux pour cette cohorte Omega** : `proofnet-11, 17, 34, 55, 77, 99, 141, 181.lean`, empreintes Git blob déjà recueillies dans `FROZEN_NEW.json` au moment du préenregistrement.
- Sources originales téléchargées **une seule fois**, SHA Git recalculé depuis les octets, extraction par deux chemins indépendants (regex + lecture structurée de lignes), association énoncé naturel / référence Lean conservée sans réécriture. Pas de substitution de fichier.
- Ce corpus n'est **pas** inédit pour l'entraînement des modèles ; il peut exister une contamination. Aucun score de généralisation à tous les théorèmes ne sera revendiqué.
- Les fichiers du dépôt contiennent des **déclarations Lean avec `sorry`** : la référence peut être fournie par l'équipe externe comme vérifiée, mais notre CI ne recompile PAS les preuves Lean et ne vérifie PAS l'équivalence sémantique langage naturel / Lean. Ce point doit rester explicite.

## Tâche du LLM, gold et contrôles indépendants
- Douze questions : huit appariements vrais et quatre **distracteurs** sans bonne réponse parmi deux candidats, construits avant les inférences. Réponse stricte `A`, `B` ou `NONE`. Équilibre A/B imposé, ordre et distracteurs figés par `FROZEN_NEW.json`.
- La « vérité » de cette tâche est **l'identité de fichier et le jumelage déjà établi par les auteurs du corpus**, PAS une preuve de fidélité mathématique. Un modèle peut choisir la bonne référence par indices superficiels ; un match n'est pas une preuve de compréhension.
- Les instructions de chaque document sont du texte **non fiable** ; elles ne peuvent pas modifier la consigne de sélection.
- Vérifier séparément la proposition arithmétique de l'index 99 (congruence pour deux nombres premiers impairs distincts) par énumération exacte de petits nombres premiers et `pow(n,q-1,p*q)`, uniquement pour les cas qui satisfont les hypothèses ; tester des contre-exemples lorsque les hypothèses sont retirées. Pour l'index 11 vérifier les conditions arithmétiques du critère d'Eisenstein sur `x³+6x+12`. Cela ne valide **ni la preuve universelle, ni le texte Lean recompilé**.

## Modèle et exécution
- Même Qwen2.5-0.5B-Instruct Q4_K_M SHA256 `74a4da8c9fdbcd15bd1f6d01d621410d31c6fc00986f5eb687824e7b93d7a9db` et llama.cpp `5a4afd80779ba51166b59986e61a0bfbb9e1a4c6` que OMEGA-CYCLE-01 #226.
- Un modèle local résident à la fois, budget 6 Gio et réserve 512 Mio ; profil RAM mesuré SHA256 vérifié depuis l'artefact SCALE01 `44875280301`. Pas de 3B ou plus dans le premier cycle.
- Deux passages complets sur les 12 **mêmes** questions, serveur redémarré et KV froid : cache `OFF` comme référence sûre, `ON` comme expérience **quarantinée**. Température 0, seed 42, n_predict 12, le rendu chat natif identique. Les sorties et erreurs ne seront jamais corrigées/réinterprétées après coup.
- Rapporter exactitude par rapport au jumelage source (matched et distractor), refus de parser, `NONE`, divergences ON/OFF, latences, tokens évalués/cachés, taille modèle, RSS max, temps de contrôle indépendant.

## Mémoire et règle de promotion
- Produire l'artefact `verified_candidates.jsonl` **uniquement** pour : intégrité réelle des huit fichiers (git blob + double extraction concordante), jumelages établis par la source, résultats de tests arithmétiques bornés **explicitement bornés**, et mesures exécutées de qualité comme faits d'expérimentation.
- Ne jamais transformer des références externes en « théorèmes prouvés par Omega ». Même en cas d'accord LLM et jumelage, l'état du résultat scientifique reste `UNVERIFIED_SEMANTIC_FIDELITY`.
- Produire séparément `model_quarantine.jsonl` avec toutes les sorties brutes LLM, bonnes, mauvaises ou refusées. Aucun résultat LLM n'est certifié.
- Journal de mémoire **persistant** proposé dans une branche/PR dédiée `09_INFRASTRUCTURE_AGENTIQUE/scientific_memory01/` : fichier JSONL append-only + manifeste chaîné SHA256. *Publication seulement après vérification de l'artefact réel*, en ajoutant les records vérifiés sur la branche expérimentale. Elle n'est jamais automatique vers `main` ou une bibliothèque externe. Les entrées antérieures ne sont jamais modifiées.
- La mémoire durable n'est **pas** un apprentissage de poids ou une mémoire capable de comprendre automatiquement la sémantique.

## Sorties négatives et critères
- Source corrompue, double parse non concordant, rapport de RAM modifié, contrôle d'arithmétique échoué, ou absence de logs : **fail closed**, mémoire vérifiée non publiée.
- Si une sortie OFF/ON diverge : `DIVERGENCE_OBSERVED` (ne pas annoncer parité), conserver les deux.
- Si modèle ne relie aucun énoncé correctement : noter le résultat négatif, ne pas présenter une ingestion réussie comme compréhension.
- Démonstration de cycle sur énoncés externes : 8/8 blobs vérifiés + 12 réponses modèle tracées + gardes + mémoire vérifiée durable.
- Tests sur une cohorte de seulement 8 sources, sans évaluation humaine indépendante nouvelle, Lean non recompilé. Aucun gain énergétique garanti.

Références : [ProofNet-Verified](https://github.com/marcusm117/ProofNet-Verified), [Omega #226](https://github.com/Abrasax63/Omega-pub/pull/226), [Omega #211](https://github.com/Abrasax63/Omega-pub/pull/211).
