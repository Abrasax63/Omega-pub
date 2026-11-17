# Omega 12 — formalisation automatique et recherche de contre-modèles

**Statut : expérimental / PR DRAFT.** Cette expérimentation succède au générateur Qwen de [PR #167](https://github.com/Abrasax63/Omega-pub/pull/167), en testant **le passage du texte à une représentation formelle**. Les idées librement générées par Qwen restent présentes dans leur propre journal ; elles ne sont pas assimilées à des assertions prouvées.

## Pipeline effectif

1. Le parseur traite une petite famille déclarée de phrases anglaises indépendamment des identifiants des fiches : par exemple `All cows are bovines.`, `Some pets are cows.`, `No domesticated animals are alligators.`, `Ted is an alligator.`, `If something is a bovine, then it is domesticated.`.
2. La formalisation crée des **clauses monadiques** avec leur extrait exact, numéro de prémisse, empreinte de la source et état `AUTO_SYNTAX_CANDIDATE_NOT_SEMANTICALLY_CERTIFIED`.
3. Si **toutes** les prémisses et la conclusion sont comprises, un second composant **énumère effectivement** des modèles de 1 ou 2 individus pour trouver une interprétation où les prémisses sont toutes vraies et la conclusion fausse. Le témoin est ensuite **rejoué** clause par clause.
4. Un texte non reconnu n'est jamais ignoré ou « deviné » : la question est **UNDETERMINED** et conserve les indices de toutes les prémisses non formalisées.
5. **Absence de contre-modèle fini ≠ preuve** : même un programme parfaitement exécuté ne peut certifier un théorème à partir de cet échantillonnage de domaines finis. Une traduction apparemment exacte peut aussi déformer la sémantique de l'anglais original.

## Cas externes et reproduction

L'échantillon a été figé **avant le code** : FOLIO validation **lignes 67–78**, v0.0 au commit `5d7bb84c7edab3fb358e057d2807f19cf5cf5e2d`, fichier d'origine blob `06244bd10b37eac73cba7aca6c336e96011ace58`, tranche blob `fdb0d5ef7752577d09d84acd58328e91b409aa0a`. Cela constitue 12 questions de cinq ensembles de prémisses. La v0.0 peut comporter des erreurs d'annotation ; les labels ne sont lus qu'après calcul des prédictions et empreinte des choix.

```bash
python3 -m unittest discover -s 09_INFRASTRUCTURE_AGENTIQUE/auto_countermodel12 \
  -p 'test_engine.py' -v
python3 09_INFRASTRUCTURE_AGENTIQUE/auto_countermodel12/engine.py \
  --output /tmp/omega12-raw-report.json
```

Code Python 3.12 standard library, **aucune API payante**, aucun modèle à télécharger pour ce pilote symbolique. Le rapport donne le nombre de prémisses traduites, les traductions complètes, les recherches de contre-modèles réellement effectuées, leurs témoins (si disponibles), les limites, les abstentions et la provenance.

## Interprétation scientifique

- La meilleure issue possible de ce programme est un **contre-modèle conditionnel à une formalisation obtenue automatiquement**, pas la certification d'un résultat scientifique.
- Le moteur n'a pas encore de théorie des quantificateurs arbitraires, des relations binaires, du langage non standard ou des connexions profondes entre nos briques.
- Les tests sur données synthétiques vérifient que la recherche trouve de vrais témoins et n'en invente pas, mais **ne prouvent pas un transfert sur un jeu extérieur**.
- Même en présence d'un contre-modèle vérifié, il faudrait confirmer indépendamment la fidélité de la traduction de **toutes** les prémisses.
- La mémoire de #167 et la génération Qwen ne sont **pas** raccordées automatiquement au moteur de cette PR : c'est la prochaine jonction expérimentale, à budget égal, une fois les résultats du premier test connus.

**Aucune fusion, aucun changement de main, aucun raccord au cycle horaire.**

Données externes : <https://github.com/Yale-LILY/FOLIO>, Han et al., FOLIO, licence CC BY-SA 4.0.
