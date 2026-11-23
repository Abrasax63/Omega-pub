# OMEGA-ABSTRACTION-REAL-01 — résultats du PREMIER run réel, 22 novembre 2026

**Statut : EXÉCUTÉ / ÉCHEC DU SEUIL D'ADMISSION / ABSTRACTION NON TESTÉE.**
Aucun théorème certifié ni gain démontré. Aucune modification de `main`.

## Provenance

- Run complet **SUCCESS technique** : https://github.com/Abrasax63/Omega-pub/actions/runs/45059812537
- Archive brute : https://github.com/Abrasax63/Omega-pub/actions/runs/45059812537/artifacts/14769476203
- Prérégistration : `09_INFRASTRUCTURE_AGENTIQUE/prism/OMEGA_ABSTRACTION_REAL_01_PREREG.md` (créée AVANT l'exécution).
- Source : Richard Hammack, *Book of Proof*, third edition,
  https://richardhammack.github.io/BookOfProof/Main.pdf ;
  SHA-256 PDF : `e0e471ca794ddda7bc46704b22885e1582350b7fc5881f8ba9a61b3747ec79fd`.
- Pages physiques choisies par graine SHA, sans choix de concept : **68, 120, 180**.
- Modèle local **Qwen2.5-3B-Instruct Q4_K_M**, SHA-256 des poids :
  `9c9f56a391a3abbd5b89d0245bf6106081bcc3173119d4229235dd9d23253f94`.
  `llama.cpp b12633`, CPU GitHub sans GPU, aucun appel API payant.
  Provenance initiale du modèle : `bartowski/Qwen2.5-3B-Instruct-GGUF/resolve/main`
  avec SHA exact archivé ; la branche `main` du fournisseur n'était pas épinglée avant ce run.

## Mesures observées — rapport et registre bruts relus

| Mesure | Résultat |
|---|---:|
| Pages primaires jamais utilisées dans les RAW/WEB précédents | 3 |
| Recherches formulées par le **modèle** | 3/3 |
| Recherches ayant retourné deux pages Web | 3/3 |
| Réponses fiche en JSON valide | 3/3 |
| Fiches de recherche archivées en quarantaine | 3 |
| Citations verbatim admissibles de la **page Web indiquée** | **0/3** |
| Fiches admissibles au regroupement sémantique | **0** |
| Appel réel à `from_library` | Oui — blocage prudent : `INSUFFICIENT_GROUNDED_LIBRARY_CANDIDATES` |
| Appel du modèle pour proposer une abstraction | **0** (précondition de confiance échouée) |
| Tests A/B/C sur relations inconnues | **0**, bloqués et non inventés |
| Nouvelles propriétés générales démontrées | **0** |
| Appels au modèle réalisés | **6** |
| Tokens de prompt (tels que reportés par le serveur) | **6 568** |
| Tokens générés | **1 020** |
| Temps cumulé d'inférence (mesuré par client) | **305,399 secondes** |

Les sorties ne sont pas détruites : elles sont préservées à l'identique dans
`outputs/math_library_candidates.jsonl`, avec IDs de révisions et SHA des
extraits consultés, visibles dans l'artefact. Le résultat logiciel vert ne
signifie pas que les assertions mathématiques soient justes.

## Trace des choix réels du modèle

| Page physique | Terme de recherche du modèle | Sources Web (titres) | Validation de citation |
|---:|---|---|---|
| 68 | `universal quantifier in conditional statements` | Universal quantification ; Quantifier (logic) | **REJET** |
| 120 | `k-element subsets of S` | Steiner system ; Subset | **REJET** |
| 180 | `perfect number definition` | Perfect number ; 6 | **REJET** |

**Erreur de fidélité de provenance.** Sur les pages 120 et 180, le champ
`exact_quote` reprend visiblement le contenu du livre primaire, mais
`source_page_id` désigne une page encyclopédique récupérée : il n'est donc
pas honnête de présenter cette citation comme venant de l'article Web. Pour la
page 68, la prétendue citation ajoute notamment un commentaire éditorial et
une ellipse et ne satisfait pas le contrôle exact. Cela explique les rejets
sans prétendre qu'aucune source littérale n'existe.

**Erreur sémantique indépendante et décisive.** Sur le concept de
`perfect number`, le modèle écrit qu'un nombre est parfait lorsque la somme
de ses **diviseurs propres**, hors lui-même, vaut **deux fois le nombre**.
C'est **FAUX** : le contre-exemple immédiat est 6.
Ses diviseurs propres 1,2,3 donnent **1+2+3=6**, tandis que tous ses diviseurs
donnent **1+2+3+6=12=2×6**.
La source primaire page physique 180 explique justement la différence entre
les deux formulations équivalentes. Le modèle a **mélangé les deux
représentations**, produisant une définition plus forte erronée. Ce défaut est
le blocage sémantique recherché, pas simplement une sortie JSON incorrecte.

## Attribution causale prudente

- **Fonctionnel / EXÉCUTÉ :** téléchargement, sélection des pages, CPU réel,
  requêtes choisies, récupérateur Web, génération JSON, archive rémanente,
  détection d'inadmissibilité.
- **ÉCHEC DOCUMENTAIRE :** les trois citations externes sont invalides
  selon la référence indiquée.
- **RÉFUTÉ sur un cas :** la définition fusionnée de nombre parfait est
  erronée ; les deux versions originales doivent rester séparées et être
  vérifiées avant tout rapprochement.
- **NON TESTÉ :** généralisation autonome par `concept_abstraction_lab`
  sur ces sources ; aucun couple réel n'a passé le seuil d'admission.
- **INDÉTERMINÉ :** contribution des sources externes, bénéfice de la
  bibliothèque, transfert vers d'autres mathématiques et changement réel de
  représentation. Ni gain ni impossibilité établis.

## Prochaine vérification décisive (nouveau jeu, jamais ce holdout exposé)

Ne pas affaiblir le garde-fou pour faire passer ces trois fiches.

**Deux correctifs d'architecture proposés, à préenregistrer sur une nouvelle
cohorte indépendante :**

1. Une citation peut provenir **soit du document primaire, soit du document
   Web**, mais il faut un champ `source_kind` et un identifiant/révision qui
   correspondent à son véritable texte exact ; jamais l'ID de Wikipédia
   attribué à une phrase du livre. Conserver deux validations séparées et
   les versions originales, sans les fusionner.
2. Avant de généraliser deux définitions, imposer un **test de contraste
   d'hypothèses** : exemple positif commun, cas où une propriété manque,
   contre-exemple numérique exact, justification des implications dans
   chaque sens si l'on prétend à une équivalence. La validation ne doit pas
   provenir du même modèle seul.

Évaluer ensuite sur d'autres pages vierges avec même architecture gelée :
taux de citations fidèles, erreurs mathématiques silencieuses, bonnes
abstentions, capacité à choisir lui-même des concepts, exactitude des
contre-exemples et intérêt du contexte d'abstraction.

**Ne pas rejouer ces pages 68, 120, 180 pour annoncer une nouvelle mesure
indépendante après avoir vu ces sorties.** Leur rôle devient diagnostic.

Ce rapport est une analyse post-run, pas une certification mathématique par
Omega.
