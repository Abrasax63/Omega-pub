# Amendement avant premier SQL — signification de « sans éditeur »

**12 novembre 2026. Ajouté AVANT téléchargement/exécution de la base BIRD.** Le protocole initial [EXPERIMENT_P5_EVID05_BIRD_SQL_PREREG_2026-11-12.md](EXPERIMENT_P5_EVID05_BIRD_SQL_PREREG_2026-11-12.md), commit `63471285be2c271b2671537be0b908ae0de3918b`, prévoyait pour ClaimDB #4179 une convention `NULL, référence étrangère absente, N/A, Unknown, None`. La consultation de l'annotation `extra_info` du ClaimDB public avant accès à la DB révèle explicitement **`didn't have any publisher refers to publisher.id = 1`**.

Ce n'est **pas** un résultat empirique et ne justifie aucune correction de verdict a posteriori. Le contrôle de #4179 enregistrera donc **deux prédicats séparés** :
- **SENS_NATURELLE pré-enregistrée** : une identité d'éditeur manquante au sens `NULL/clé absente/nom vide/N/A/Unknown/None`, deux requêtes indépendamment structurées ;
- **SENS_ANNOTATION ClaimDB** : association `publisher_id = 1` ou jointure sur `publisher.id = 1`, également deux requêtes.

Leurs résultats ne seront **jamais substitués l'un à l'autre**. Le verdict publiable du contrôle de provenance reste `ABSTAIN_SEMANTIC_CONVENTION` tant qu'aucune revue sémantique indépendante ne confirme la convention pertinente pour l'affirmation naturelle. Ce statut est appliqué même si les deux valeurs calculées sont égales et même si le label du benchmark concorde. Le contrôle classique ayant seulement les sorties SQL est montré pour référence, mais pas annoncé comme preuve autonome de l'énoncé. L'objectif est la cohérence de l'information, pas la maximisation rétrospective d'une note.

L'étiquette ClaimDB reste réservée à l'évaluation. Toutes les autres contraintes, hypothèses, IDs, sources et politiques restent gelés. **Aucune nouvelle inference LLM ni accès à une base source n'a été effectué à ce stade.**
