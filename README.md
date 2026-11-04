# Omega-pub — RAVI-2 / CCS / Omega-SRR

**Espace public de discussion, de reproduction et de réfutation de travaux de recherche.**

Ce dépôt accueille progressivement des dossiers de recherche issus des travaux RAVI-2, CCS et Omega-SRR. Son objectif est de permettre à des lecteurs extérieurs — chercheurs, mathématiciens, informaticiens et personnes intéressées — d'examiner les définitions, les démonstrations, les calculs et les limites annoncées.

> **Principe central : publier n'est pas certifier.** Aucun résultat n'est réputé démontré du seul fait qu'il figure ici. Les statuts épistémiques doivent être explicitement indiqués et justifiés.

## Périmètre

- **RAVI-2** — méthode de recherche adversariale, vérification indépendante, contre-exemples et traçabilité des résultats.
- **CCS** — corpus de structures et de travaux associés, publiés uniquement après vérification de leur provenance et de leur statut.
- **Omega-SRR** — travaux conservés sous leur périmètre propre ; aucune équivalence avec RAVI-2 ou CCS n'est présumée.

Les rapprochements entre ces axes doivent être explicitement argumentés. Une analogie n'est pas une correspondance formelle.

## Comment participer

1. Lire le [protocole de revue](REVIEW_PROTOCOL.md).
2. Ouvrir une [Issue](../../issues) pour une question, une erreur possible, un contre-exemple ou une demande de clarification.
3. Proposer une correction par Pull Request, avec justification et références.
4. Pour une démonstration ou un calcul, fournir suffisamment d'éléments pour permettre une vérification indépendante.

Les critiques sont bienvenues, y compris lorsqu'elles invalident une affirmation. Les désaccords doivent porter sur des énoncés précis et vérifiables.

## Statuts utilisés

| Statut | Signification |
|---|---|
| DÉMONTRÉ | Preuve examinée dans le périmètre et sous les hypothèses indiqués |
| CALCUL EXACT | Résultat obtenu par calcul exact reproductible |
| SIMULÉ | Résultat issu d'une simulation, avec protocole et limites |
| EMPIRIQUE | Observation issue de données ou d'une expérience décrite |
| CONJECTURÉ | Proposition non démontrée |
| RÉFUTÉ | Contre-exemple ou argument décisif établi |
| INDÉTERMINÉ | Éléments insuffisants pour conclure |
| À RÉEXAMINER | Résultat antérieur nécessitant un nouvel audit |

Un statut s'applique à un énoncé délimité, pas à un domaine entier.

## Organisation prévue

- research/ — dossiers de recherche publics, classés par sujet.
- reviews/ — rapports de revue et réponses documentées.
- reproducibility/ — scripts, données minimales et instructions de reproduction.
- templates/ — modèles de fiches de résultat et de rapports de critique.

Les contenus seront ajoutés progressivement. L'absence d'un dossier signifie qu'il n'a pas encore été publié ici ; elle ne signifie pas qu'il n'existe pas dans les archives de travail.

## Garanties de méthode

- Préserver les résultats antérieurs validés ; toute révision est versionnée.
- Distinguer preuve, calcul, simulation, observation et conjecture.
- Publier les hypothèses, le périmètre, les dépendances et les limites.
- Ne jamais présenter une exécution comme réalisée si elle ne l'a pas été.
- Documenter les contre-tests et les résultats négatifs.
- Ne pas exposer de données privées, secrets, identifiants ou archives internes.

## Langues

Les contributions peuvent être rédigées en français ou en anglais. Les termes mathématiques, notations et énoncés formels doivent rester stables entre traductions.

---

**État du dépôt :** mise en place de l'espace public et de son protocole de revue. Les dossiers scientifiques seront publiés séparément, après contrôle de leur contenu et de leur statut.
