# OBS-COL-11 — Transfert externe prospectif et audit exact des automates appris

**Date du protocole et des expériences : 16 novembre 2026.**
**Statut : ÉVALUATION PROSPECTIVE SUR MODÈLES PUBLICS ; CALCUL EXACT POST HOC ; PAS DE SUPÉRIORITÉ GÉNÉRALE D'OMEGA.**
**Branche :** `experiment/obs-col11-prospective-radboud-transfer-2026-11-16`, empilée sur #110. Pas de changement direct de `main`, CORE ou des politiques de #110.

## Pourquoi cette expérience n'est pas un doublon

- **#47 et #55** avaient déjà étudié des holdouts et l'adaptation réelle sans plus-value propre établie ; domaine des réponses/verificateurs, pas de découverte d'automates.
- **#92** utilisait PR23/P1 avec un catalogue fourni : même décision que l'optimiseur exact.
- **#96** exécutait L*/KV/L#/TTT authentiques sur trois machines déjà connues ; l'ajout de P1 ne changeait aucune sonde.
- **#110** ajoutait une **politique de choix réellement différente** mais ne la testait que sur trois automates de calibration.
- **#105 et #108** portent sur la correction prospective de bogues logiciels, un autre objectif.

OBS-COL-11 réutilise **sans modification** la politique source #110 et l'apprenant L# original, avec une nouvelle source universitaire d'automates jamais utilisée dans les pilotes du laboratoire.

## Provenance et verrouillage

1. [Pré-enregistrement avant téléchargement](PREREG.md) au commit [6a37ca2e](https://github.com/Abrasax63/Omega-pub/commit/6a37ca2e7b10c5222f17dd5058ccf701e15c64e8) : six noms de fichiers choisis à l'avance, sans remplacement après inspection, politiques A/B/C/L*/KV, plafonds, métriques, règle de verdict.
2. Source extérieure : [Automata Wiki de l'université Radboud, Moore/Rivest–Schapire](https://automata.cs.ru.nl/BenchmarkMoore-RivestShapire1993/Moore). Les fichiers publiés sont publics, **pas un jeu aveugle indépendant**.
3. [Récupération #43821245653](https://github.com/Abrasax63/Omega-pub/actions/runs/43821245653) : six fichiers téléchargés ; SHA-256 archivés puis [verrouillés avant le code de test](SOURCE_SHA_LOCK.json) au commit [8ea4be0f](https://github.com/Abrasax63/Omega-pub/commit/8ea4be0fb911df10296ea5d17203dd3c4d827630). L'adaptateur refuse tout octet modifié.
4. Après vérification : `crossword2x2.dot` possède un état dépourvu de transitions F/L/R, `crossword3x3.dot` en possède trois. Ils sont **BLOCKED_INPUT_INCOMPLETE**, sans réparation silencieuse ni substitution. Les registres 2,3,4,5 bits sont complets et possèdent 4,8,16,32 états.
5. Le modèle vrai est utilisé uniquement par l'oracle d'observation et l'évaluateur, jamais comme argument du classement de sondes ; le vrai P1 relaie les resets du candidat Omega. La politique utilise seulement l'hypothèse courante et les préfixes déjà interrogés.

## Première exécution : cinq méthodes, mêmes coûts maximum et même oracle borné

[CI initiale #43822021430 — SUCCESS](https://github.com/Abrasax63/Omega-pub/actions/runs/43822021430), commit `380eaa5f25089cb7a4da003023cd76b5a0aea1f0`.
**7 tests réussis**, 20 apprentissages réels (5 stratégies × 4 automates). [Artefact original](https://github.com/Abrasax63/Omega-pub/actions/runs/43822021430/artifacts/14204458663) comprenant les 6 sources, SHA, coûts, modèles, conclusions et journaux.

Les 5 méthodes sont L# ordre fixe, L# couverture hypothétique classique, L# couverture+préfixes observés (`omega_candidate`, vrai P1), L* et KV de AALpy 2.0.0. Toutes utilisent 512 sondes candidates EQ identiques par source et 256 mots de contrôle par source, testés seulement après entraînement. Plafonds : 10 000 resets / 50 000 symboles par apprentissage ; aucune API de modèle payante.

| Modèle | Politique | Réinitialisations | Symboles | États appris | Erreurs sur 256 mots non vus |
|---|---|---:|---:|---:|---:|
| Registre 2 bits | fixe / couverture / candidat | 549 / 533 / 533 | 5093 / 5060 / 5060 | 4 / 4 / 4 | 0 / 0 / 0 |
| Registre 3 bits | fixe / couverture / candidat | 848 / 566 / 566 | 6021 / 5065 / 5065 | 8 / 8 / 8 | 0 / 0 / 0 |
| Registre 4 bits | fixe / couverture / candidat | 1073 / 675 / **631** | 7650 / 6449 / **5967** | 16 / 16 / 16 | 0 / 0 / 0 |
| Registre 5 bits | fixe / couverture / candidat | 2383 / 853 / 854 | 16971 / 8759 / 8783 | 32 / 27 / 27 | **0 / 1 / 1** |

Résumé sur 4 registres, à ne **pas** traiter comme 4 réplications indépendantes puisqu'il s'agit d'une famille mathématique unique :

| Méthode | Resets | Symboles | Erreurs sur 1 024 mots non vus |
|---|---:|---:|---:|
| L# fixe | 4 853 | 35 735 | 0 |
| L# couverture classique | 2 627 | 25 333 | 1 |
| L# candidat Omega/P1 | 2 584 | 24 875 | 1 |
| L* | 3 241 | 27 784 | 0 |
| KV | 8 139 | 56 093 | 2 |

**Lecture correcte :** le candidat présente une économie de consultations agrégées mais ne domine pas la couverture sur tous les modèles ; sur le registre5 il utilise **un reset et 24 symboles de plus** tout en produisant la même erreur. Le routage P1 et le classement adaptatif ont un coût de calcul supplémentaire. Cette cohorte ne démontre **pas** une intelligence supérieure.

## Deuxième phase, audit EXACT post hoc : séparer apprentissage et vérité

[Amendement explicite APRÈS les résultats](AMENDMENT_POST_RUN_EXACT_EQ.md), commit [e6096430](https://github.com/Abrasax63/Omega-pub/commit/e60964303b7de24b0721296f8e061cf0c79a8e9e). L'évaluateur connaît le graphe fini **uniquement après gel** ; aucune politique/sonde/modèle apprenant n'est retouché.

Algorithme mathématique : BFS sur l'**automate produit** (états source, état appris). Si une paire accessible possède deux sorties distinctes, extraire le **mot le plus court** qui y mène : contre-exemple exact. Si toutes les paires accessibles ont les mêmes sorties, toute trajectoire sur l'alphabet donne la même sortie par induction — équivalence exacte pour ces deux automates finis, complets et déterministes. Méthode classique, aucune nouveauté théorique.

[CI exacte #43822489266 — SUCCESS](https://github.com/Abrasax63/Omega-pub/actions/runs/43822489266) : **4 tests réussis**, les 20 apprentissages rejoués avec **resets, symboles et tailles d'automates exactement identiques au premier run** (verrou [FROZEN_FIRST_RUN.json](FROZEN_FIRST_RUN.json)), [artefact JSON exact](https://github.com/Abrasax63/Omega-pub/actions/runs/43822489266/artifacts/14204313579).

| Modèle | L# fixe | Couverture classique | Candidat Omega | L* | KV |
|---|---|---|---|---|---|
| Registre 2 bits | Exact | Exact | Exact | Exact | Exact |
| Registre 3 bits | Exact | Exact | Exact | Exact | Exact |
| Registre 4 bits | Exact | Exact | Exact | Exact | Exact |
| Registre 5 bits | **Exact** | **Réfuté** | **Réfuté** | **Exact** | **Réfuté** |

**Contre-exemple minimal identique pour les trois modèles du registre5 :**
`F, L, F, L, F, L, F, L, L` (longueur **9**) → sortie originale **1**, sortie prédite **0**. Tous les mots de longueur strictement moindre donnent les mêmes réponses sur les automates respectifs (vérification exhaustive du produit). Sur les 20 modèles appris, **17 sont exactement équivalents, 3 réfutés**.

Ce résultat explique pourquoi **une oracle d'équivalence bornée à 512 sondes d'une longueur possible jusqu'à 18 ne donne PAS une garantie d'équivalence totale**, même lorsque les modèles entraînés sur cette suite affichent zéro contre-exemple EQ. Le fait que le témoin soit de longueur 9 n'implique pas qu'une politique aurait dû le trouver sans autre stratégie ou coût.

## Verdict et prochaines actions

- **VÉRIFIÉ :** choix adaptatif réel de sondes, transfert vers une source indépendante de données publiques, verrouillage préalable, blocage correct de deux formats incomplets, métriques comparées, un gain **local** du candidat sur registre4 et une **réfutation exacte** sur registre5.
- **NON DÉMONTRÉ :** supériorité générale d'Omega face à un classique solide, certification d'une théorie naturelle, découverte autonome, évaluation privée réellement aveugle.
- **Limite de validité :** quatre registres apparentés, source universitaire publique, politique et oracle de longueur bornée, résultats déterministes avec une seule graine. Le résultat exact est une propriété de ces automates connus **après** l'apprentissage, pas une preuve de capacité générale du système.
- **Ne pas retoucher la politique sur ce témoin**, ne pas relancer les quatre registres comme un nouveau holdout. Le prochain travail pertinent serait de verrouiller une nouvelle source extérieure avant toute proposition de stratégie supplémentaire et de tester une **stratégie de contrôle de conformité plus robuste** (p. ex. tests de séparation/états) face aux mêmes algorithmes classiques, en comptant les coûts intégralement.

**Gouvernance : PR DRAFT empilée sur #110, aucun changement de `main`, CORE, aucune fusion ni promotion automatique.**
