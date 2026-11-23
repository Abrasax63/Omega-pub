# OMEGA-REPAIR-BENCH-04 — comparatif préenregistré, 2026-11-23

**Statut à la création : PROPOSÉ, aucune inférence BENCH-04.** Branche PR #231 `experiment/omega-self-growing-math-library-2026-11-22`. Ce document, les métriques, le vérificateur et les six tâches doivent précéder la première génération. Pas de modification de `main`, pas d'API de modèle payante, pas de certification scientifique sur de la prose.

## Recherche externe et limites de transfert

- Self-Refine (NeurIPS 2023) https://papers.nips.cc/paper/2023/hash/91edff07232fb1b55a505a9e9f6c0ff3-Abstract-Conference.html : boucle interne auto-critique et révision ; sans oracle garanti.
- CRITIC (ICLR 2024) https://proceedings.iclr.cc/paper_files/paper/2024/hash/fef126561bbf9d4467dbb8d27334b8fe-Abstract-Conference.html : vérification par outil externe et révision.
- CEGIS(T) (CAV 2018) https://www.cs.ox.ac.uk/publications/publication12086-abstract.html : synthèse/contre-exemple itératifs, contraintes accumulées.
- Huang et al. (ICLR 2024) https://proceedings.iclr.cc/paper_files/paper/2024/hash/8b4add8b0aa8749d80a34ca5d941c355-Abstract-Conference.html : correction sans retour fiable parfois dégradante.
- AlphaProof (Nature 2025) https://www.nature.com/articles/s41586-025-09833-y : vérificateur formel avec recherche et apprentissage, non transposable directement au matériel modeste d'Omega.

Ce benchmark est seulement une comparaison de **politiques de retour et de réparation en temps d'inférence** ; il ne transpose ni apprentissage par renforcement, ni preuve Lean, ni théorèmes nouveaux.

## Six tâches immuables et spécifications mathématiques

Six tâches nouvelles, jamais utilisées dans REAL-03. Chaque domaine comporte quatre sommets étiquetés sans chevauchement (pas de cas avec lettres p,q,r,s;u,v,w,x;k,l,m,n;d,e,f,g déjà vus). `R1`: equivalence (a1,a2,a3,a4), réflexif/symétrique/transitif ; `R2`: partial_order (b1,b2,b3,b4), réflexif/antisymétrique/transitif ; `R3`: preorder (c1,c2,c3,c4), réflexif/transitif ; `R4`: symmetric (h1,h2,h3,h4) ; `R5`: transitive (j1,j2,j3,j4) ; `R6`: antisymmetric (t1,t2,t3,t4). Exigence constante : **au moins deux arcs hors-diagonale** et aucune paire répétée. Les prompts donnent seulement les définitions des propriétés : aucun ensemble d'arêtes cible, aucune solution.

1 seul appel produit le candidat initial par tâche. S'il est correct, ne pas provoquer artificiellement une erreur ; s'il est mal formé, compter un échec de format et l'exclure des comparaisons de réparation appariées. Les cas initialement faux mais bien formés sont comparés, **tous, sans sélection post-hoc**, dans trois bras réinitialisés depuis la *même* génération initiale.

## Trois bras, même budget nominal

- `G` : message «candidat invalide» générique (contrôle négatif, ne transmet aucune propriété).
- `S` : premier axiome faux + **un seul témoin exact** ; à l'itération suivante, nouvelle violation du candidat précédent, en conservant le témoin antérieur (analogue CEGIS local).
- `A` : **tous les axiomes faux et tous leurs témoins** (énumérés dans l'ordre déterministe des sommets et de `reflexive,symmetric,antisymmetric,transitive`) jusqu'à 64 tuples ; itération 2 sur le dernier candidat, avec conservation des violations de l'itération 1.

Maximum **deux appels de réparation pour chaque bras**, arrêt au premier succès vérifié ; les appels économisés sont comptabilisés. Ordre équilibré des bras parmi les six permutations, prédéfini par rang de tâche. Chaque appel : même Qwen2.5-3B-Instruct Q4_K_M que REAL-03 (poids SHA-256 `9c9f56a391a3abbd5b89d0245bf6106081bcc3173119d4229235dd9d23253f94`), `llama.cpp b12633`, CPU, température 0, seed 9123, JSON, sortie max 260 tokens, source et prompts gelés avant run. Sur chaque trio d'appels au même rang, égalisation par `/tokenize` des tokens d'entrée à +/-5 % à l'aide d'un marqueur administratif neutre ; si non comparable, marquer le résultat causal **INDÉTERMINÉ**, garder les données brutes. Temps, tokens réels et appels rapportés séparément ; le calcul de vérification est externe au modèle.

## Quatrième approche : synthèse déterministe et vérification exacte

Un synthétiseur non-LLM parcourt les 2^16 relations finies sur les quatre sommets, en ordre de distance de Hamming au candidat initial, jusqu'à trouver une solution non dégénérée satisfaisant **toutes** les propriétés. Refaire la vérification finale par `check_axioms`. Cette borne est une référence mathématique valable dans ce domaine fini uniquement, sans qualité linguistique ni apprentissage ; reporter distance optimale et coût CPU. Pas de modèle ni d'API pour cette approche. Ne pas confondre succès déterministe et réussite d'Omega à raisonner.

## Mesures et critères fixés avant exécution

Indicateurs : 6 candidats initiaux, admissibles, corrects, erreurs mathématiques; `E` nombre erroné mais bien formé; succès `G,S,A` à 1 et 2 tentatives / E, échecs de formats, exactitude des témoins, nombre de **violations restantes**, réparations locales incomplètes, distances d'édition par rapport à l'initial, coût (appels, tokens, secondes), synthèse exacte `D` et distance minimale, budget comparable, traçabilité complète SHA-256 des prompts et réponses.

Critère de gain ponctuel : `E >= 3`, budgets comparables, `A >= 2` corrections exactes, **A-G >= 2** et **A-S >= 1** corrections, **0 erreur acceptée** par le vérificateur (le logiciel ne doit jamais promouvoir une relation incorrecte). Dans les autres cas avec `E>=3` et budgets comparables : `CRITÈRE DE GAIN NON SATISFAIT`. Si `E<3`, erreur de transport, code, source ou budgets : `INDÉTERMINÉ` pour l'effet comparatif. Un échantillon aussi petit ne suffit pas à inférer un gain général ou statistiquement significatif ; les dépendances entre quatre notions sont importantes.

Prévoir un unique run scientifique réel, au plus `6+6×3×2=42` appels, aucune recherche post-hoc pour sauver les seuils. Exécuter d'abord les tests logiciels avec modèle simulé et contre-exemples exacts, puis le run CPU SHA-pinné. Si erreur révélée après inférence, ne jamais relancer avec ces mêmes six tâches pour afficher une réussite indépendante. Comparaison contrôlée mais pas randomisation double aveugle ; l'ordre de bras est équilibré, pas choisi selon les réponses.

## Reproductibilité et sécurité

Seuls les rapports et artefacts de la branche expérimentale contiennent les générations, prompts, témoins, métriques, hash et correctifs de transport. Le moteur exact ne doit pas être modifié pour «faire réussir» un candidat ; tout échec devient une observation. Aucune mise à jour des poids, aucune mémoire scientifique promue, aucun changement des schedules Omega, aucune suppression automatique de fichiers ou de travaux. Source pédagogique des définitions d'Oscar Levin (CC BY-NC-SA 4.0), commit amont `1a2005c6797bec10289f09e706f81c6c4b809a52`, Git blob `75bebda318694bb4712d60380b0e183e77f1e757`.
