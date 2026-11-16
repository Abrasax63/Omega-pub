# OMEGA-REPAIR-COVERAGE-01 — hypothèse fixée avant le test complémentaire

Date : **16 novembre 2026**. Branche empilée sur [PR #106](https://github.com/Abrasax63/Omega-pub/pull/106), commit de départ `4989de316c3db56e64213cb48c0e9c0553d389b2`. **Aucune modification de `main` ni du protocole de génération de correctifs existant.**

## Constat indépendant de ce nouveau test

Le [run #43777810810](https://github.com/Abrasax63/Omega-pub/actions/runs/43777810810) a :
- vérifié les deux régressions historiques `B2 tqdm-2` et `B3 cookiecutter-2` dans Docker historique sans réseau ;
- classé le fichier corrigé en amont au **premier rang pour B2 (1/10) et B3 (1/6)** à partir de traces des vrais tests échoués ;
- généré **20 propositions AST par problème**, limitées à deux lignes d'une fonction au maximum, avant consultation de l'oracle de réussite ;
- exécuté **les 6 premières propositions par projet** : **0/12 réparations réussies**.

**Question falsifiable :** y a-t-il, parmi les **14 candidates restantes de chaque liste déjà figée**, une modification qui réussit le vrai test de régression ? Ce test permet de séparer les explications « budget de tests/classification insuffisant » et « la bonne transformation est absente du langage généré », au moins pour ces cas.

## Intervention strictement contrôlée

1. **Ne pas modifier** `bounded_patch.py`, les 20 candidats ni leur ordre, `rank_suspects.py`, la capture des traces, les dépendances Docker ou le test cible.
2. Réutiliser les **listes gelées** `trace-evidence/B2-patches.json` et `B3-patches.json` générées dans le workflow **avant l'accès aux résultats des patchs**. Vérifier que chaque liste contient 20 entrées, des IDs uniques, des sources initiales et résultantes identifiées par SHA-256, et au plus deux lignes modifiées dans une seule fonction.
3. Test complémentaire **exclusivement en lecture d'hypothèses** : exécuter avec les **mêmes vrais tests Docker** les candidats de rangs **7 à 20**, jusqu'à 14 par projet. Ne pas sélectionner de nouveaux patchs après avoir observé les résultats. Chaque score exige une exécution réelle, pas une prédiction.
4. Conserver journaux, codes de sortie, raisons `TEST_PASSED` / `TEST_FAILED` / `ENVIRONMENT_ERROR`. Une erreur d'infrastructure ne vaut pas échec scientifique. Rapprocher des résultats précédents des rangs 1 à 6 ; **ne pas compter un même candidat deux fois**.
5. **Décision :**
   - au moins une candidate tardive réussit → `SUCCÈS TARDIF / BUDGET LIMITANT`, vérification de non-régression nécessaire ;
   - 20 candidates testées, toutes échouent sur un vrai test reproduit → `ABSENCE DE RÉPARATION DANS LE POOL BORNÉ` ;
   - échec d'environnement, source non vérifiée ou résultat manquant → `INDÉTERMINÉ`.

## Restrictions scientifiques

Ces deux bugs ont déjà été examinés, avec leurs correctifs historiques connus des expérimentateurs. **Il ne s'agit pas d'une cohorte aveugle**, mais d'un audit *post-hoc* du langage de réparation déjà défini. Réussite d'un test cible ne garantit pas la non-régression sur la suite complète du projet. Aucun appel à Qwen ni promotion scientifique. La comparaison de coût reste un comptage d'appels et de durée, sans prétention de performance algorithmique supérieure.

**Condition d'arrêt :** le fichier de candidates diffère, l'empreinte source ne se vérifie pas, le vrai test buggy/fixed n'est pas reproduit, ou Docker échoue : déclarer le dossier indéterminé, ne pas modifier la grammaire pour sauver la campagne.
