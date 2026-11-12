# Revue sémantique indépendante requise — P5-EVID-05 et EVID-06

**État : À FAIRE. Aucun évaluateur tiers n'a approuvé ces correspondances.** Ce fichier formalise l'examen à demander ; il ne simule pas la signature d'un réviseur.

## Objectif du contrôle contradictoire

Un examinateur qui **n'a pas écrit** les SQL doit recevoir (a) les textes ClaimDB originaux, (b) leur `extra_info`, (c) les schémas de tables BIRD épinglés par SHA, puis formuler **sa propre interprétation de la proposition avant de lire les sorties SQL et les labels ClaimDB**.

Cohorte principale de la [PR #62](https://github.com/Abrasax63/Omega-pub/pull/62) : #4267, #4179, #4324, #3930, #4419. Nouvelle cohorte distincte de la [PR #63](https://github.com/Abrasax63/Omega-pub/pull/63) : #15601, #3730, #3971.

Source ClaimDB : [fichier officiel du jeu test public au commit fixe](https://github.com/claimdb/claimdb/blob/e06c3a22cc14a8ef6858bb5d40bca7925241b98d/final-benchmark/test-public.jsonl).
Base BIRD : [superhero.sqlite au commit fixe](https://github.com/Tarzanagh/QAFD-RAG/tree/2a3a42c8ea4e9c416de0a7fe53c04fab50b756ef/data/text2sql/bird/databases/superhero), SHA-256 `75e94a2c3236ee3bb2c01fb97a1c4b4c1c269bcefd4eab1d04be323d2d0825b1`.

Les SQL exacts sont intégralement dans `prism/p5_evid05_bird_sql.py` et `prism/p5_evid06_bird_extra_sql.py` et leurs résultats dans les artefacts des runs [#43233326446](https://github.com/Abrasax63/Omega-pub/actions/runs/43233326446) et [#43237122391](https://github.com/Abrasax63/Omega-pub/actions/runs/43237122391).

## Points adversariaux à examiner

1. **#15601** : les « tied at the top Speed » signifient-elles réellement `MAX(attribute_value)` parmi les lignes `hero_attribute` de type `Speed` ? Les doublons `hero_id` doivent-ils être dédupliqués ? Le calcul dit 40 héros, score max 100.
2. **#3730** : « have the Super Strength power » désigne-t-il la table `hero_power` et non un seuil `Strength` de `hero_attribute` ? `height > 200` est strict, non `>=`. Le calcul donne 56 héros et contredit le nombre 42.
3. **#3971** : « most widely held » est un prédicat **global** ; la comparaison Invisibility/Super Strength seule est **nécessaire mais pas suffisante**. Ici Super Strength compte 358 héros contre 22 Invisibility et arrive premier au classement. Une inférence positive à partir du seul test par paire serait illicite.
4. **#4179** : dans l'annotation ClaimDB, « without a publisher » est défini par `publisher.id=1` ; une lecture `NULL/unknown/nom vide` est différente en théorie mais a donné ici le même résultat booléen. Revoir la convention, ne pas inventer un conflit numérique.
5. **#3930** : une ligne Human de 185 cm suffit à réfuter « no human hero ... » même si la clause « so no hair color can be provided » n'est pas prouvée universellement.
6. **#4267** : vérification qu'« blue-haired male mutant » porte sur `hair_colour_id`, `gender_id`, `race_id` du **même héros**, pas trois héros différents.
7. **#4324** : restriction `Marvel Comics`, `Female`, distinct `hero_id` et prise en compte des valeurs manquantes.
8. **#4419** : un monde hypothétique où les éditeurs renommeraient des personnages ne peut pas être déduit d'une simple base statique.

## Grille de vérification indépendante

Pour **chaque claim**, la personne chargée de la revue devra renseigner :

| Champ | Valeur attendue |
|---|---|
| ID ClaimDB | Identifiant |
| Interprétation du texte naturel | Formulation par le réviseur, sans lecture préalable du résultat |
| Hypothèses supplémentaires | Conventions de nulls, jointures, quantificateurs |
| SQL A correspondant au sens ? | oui / non / partiellement |
| SQL B réellement indépendant comme calcul ? | oui / non / partiellement |
| SQL A et B même fournisseur de données ? | **oui** |
| Témoin ou contre-témoin vérifiable ? | ID de ligne + chemin de provenance |
| Conclusion établie, réfutée, ou indéterminée ? | Une des trois |
| Désaccords/questions ouvertes | Expliciter |
| Identité et date du réviseur | **À renseigner par la personne qui effectue la revue** |

Le réviseur doit indiquer avant validation si les preuves **suffisent pour la totalité de la proposition**, pas seulement une sous-clause, et effectuer une requête supplémentaire de son choix si la preuve est ambiguë.

**La validation externe est un verrou non satisfait** tant que ces champs n'ont pas été complétés par une personne réellement indépendante. Les évaluations actuelles demeurent **EXPLORATOIRES**. Aucune présence artificielle de « sous-agent » ou de revue humaine n'est revendiquée.

## Dépendance à ne pas masquer

Même avec deux requêtes différentes et un second analyste, les faits restent dérivés de la **même base BIRD**. L'indépendance du *raisonnement* n'implique pas l'indépendance de la *source des données*. Documenter ces deux relations de provenance séparément.

Pas de fusion de PR en attente de revue ; `main` inchangée.
