# Amendement P5-FALSIFY-05 — abstention du vérificateur réel (avant tout score primaire)

**12 novembre 2026, après premier contrôle de source et AVANT toute analyse des scores.**

Le premier lancement [GitHub Actions #43262333944](https://github.com/Abrasax63/Omega-pub/actions/runs/43262333944) a réussi le SHA-256 de **tous les cinq fichiers LFS authentiques**, les **9 tests préparatoires**, et a interrompu le programme à `ValueError: UNPARSED_claude_MODEL_OUTPUT:884` **avant tout résultat de performance ou comparaison des politiques**. Le protocole initial [prereg FALSIFY-05](EXPERIMENT_P5_FALSIFY05_CLAIMDB_MULTI_VERIFIERS_PREREG_2026-11-12.md) supposait naïvement un verdict textuel valide pour chacun des 1000 cas et indiquait un fail-closed lorsque ce n'était pas le cas.

Nous devons reconnaître qu'une **absence de réponse exploitable est un résultat AUTHENTIQUE et faillible d'un vérificateur**, non un motif pour exclure après coup un exemple défavorable ou changer de fournisseur de modèle. Cet amendement change uniquement le **codage des observations manquantes**, sans modifier cohortes, outils, prior, coûts, objectifs, seuils, nombre d'achats, modèle joint, planificateurs, labels, ou données sources.

## Règle corrigée et pré-déclarée avant reprise

- Si `verdict` appartient à `ENTAILED / CONTRADICTED / NOT ENOUGH INFO`, il s'agit d'un verdict brut utilisable ; sinon encoder **`NO_VERIFIER_LABEL`** et conserver le claim dans les 1000 cas.
- Si la trace `to_input_list` contient zéro `function_call_output` ou zéro `tool_result`, alors **le canal gated observe `NO_SQL_OUTPUT`** lorsqu'un verdict texte valide existe; sinon **`NO_VERIFIER_LABEL`** s'il n'y a aucun verdict. Le canal raw distingue aussi `NO_VERIFIER_LABEL` de toute étiquette de vérité.
- Le posterior joint connaît explicitement **trois étiquettes de contenu + une abstention du modèle**, auxquelles le canal de provenance gated ajoute la classe `NO_SQL_OUTPUT`. Les pseudocomptes Dirichlet restent `alpha=0.10` **par cellule**, aucune réestimation post-hoc.
- **Ne jamais attribuer `NOT ENOUGH INFO` à un `NO_VERIFIER_LABEL`** : le premier est un label de benchmark, le second une observation sur l'échec d'une sortie de modèle. Les achats infructueux coûtent toujours leur coût intégral.
- Ne jamais inférer un verdict depuis les traces SQL ou depuis le gold pour « réparer » un modèle.
- Le résultat doit publier le **nombre de cas sans verdict** par modèle, sur calibration et sur évaluation, ainsi que le taux de traces d'outil réelles.
- Un `claim_id` manquant du fichier, un fichier LFS pointer, une empreinte erronée, une incohérence des identifiants ou un gold invalide demeurent **des erreurs bloquantes**.

**Statut : AMENDEMENT APRÈS INSPECTION DE LA QUALITÉ DU FICHIER, AVANT PREMIER SCORE.** Cela dégrade l'aveuglement méthodologique et doit rester déclaré ; aucun gain d'Omega ne pourra être présenté comme indépendant de cette inspection. Pas de modification de la version initiale du fichier prereg pour masquer l'incident.
