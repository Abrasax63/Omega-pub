# Omega — pilote de dépendances entre pièces de provenance (lecture seule)

## Intention

Tester une hypothèse inspirée des réorganisations de réseaux physiques **sans simuler des bulles**, ni installer un second orchestrateur : les liens d'ascendance des artefacts peuvent aider à choisir la prochaine vérification et à ne pas compter deux miroirs comme deux calculs distincts.

**Portée exacte :** ce pilote classe des **origines d'exécution déclarées**. Deux exécutions distinctes ne prouvent ni une reproduction scientifique indépendante ni l'exactitude de leurs résultats. Un verdict positif demande une revue indépendante. Aucune certification, aucune modification de `main`, aucun appel LLM ni action externe.

## Usage

Depuis ce dossier :

```sh
python3 -m unittest -v test_lineage_pilot.py
```

`lineage_pilot.assess(dossier)` renvoie :

- `meme_origine` si toutes les sorties observées remontent à une même exécution ;
- `executions_distinctes_resultat_identique` si au moins deux identifiants d'exécution racines distincts ont produit des résultats de même empreinte ;
- `indetermine` en cas de lien manquant, non attesté, cyclique, ambigu ou de résultats incompatibles.

`next_verification(dossier)` fournit une **suggestion**, sans lancer de tâche. Le pilote ne vérifie **pas** cryptographiquement les attestations : le booléen `attested` est une entrée déclarative, à alimenter à terme à partir d'une collecte vérifiée indépendamment. Les `run_id` ne sont pas authentifiés. Les cas de test ne sont que des cas construits.

## Comparaisons et non-régression

Deux comparateurs faibles sont fournis : regroupement par empreinte de contenu, et regroupement par identifiant de la dernière tâche productrice. Aucun n'est présenté comme le routage d'Omega existant. Les tests sont adversariaux : miroirs recopiés avec nouveaux identifiants, sorties différentes d'un même calcul, calculs distincts donnant des empreintes égales, parent manquant, faux drapeau d'attestation, cycle, sortie divergente. On vérifie aussi l'invariance à l'ordre des lignes du dossier.

## Critère de décision avant toute intégration

Le prochain verrou est une comparaison **sur des traces GitHub réelles et distinctes des traces de développement** : conserver les journaux bruts, lier chaque morceau à un run/job/artifact vérifiable et établir les racines indépendamment du pilote ; geler la cohorte et ses réponses avant l'évaluation ; comparer les trois méthodes sur les mêmes dossiers et à budget de lectures équivalent, en consignant les abstentions et fausses confirmations. Utiliser le verrou de promotion de la PR #83, **sans supposer cette PR intégrée**. Toute tentative d'accès à un artefact inaccessible doit se terminer par `indetermine`.

**Conditions d'arrêt :** source non authentifiable ; fuite entre développement et holdout ; nouvelle fausse confirmation ; coût de lecture supérieur à la référence sans meilleure fiabilité ; absence de gain face à un comparateur fort.

## Dépendances

Code expérimental, empilé sur la branche de la PR #81 (`work/omega-provenance-lab`). Ni la PR #81 ni la PR #83 n'est modifiée par ce pilote. Ne pas fusionner automatiquement ; évaluation indépendante requise.
