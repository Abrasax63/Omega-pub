# OMEGA-FORMAL-SKELETON-09 — préenregistrement avant code et avant lecture des 2 nouvelles fiches

Date : 2026-11-17. Base PR #161 commit `0e656077d8c62a938cbd01f662af9df6f329882a`. Une PR de plus sans fusion de `main`. Aucun LLM externe, aucune API payante.

## Motivation / verrou
PR #161 : sûreté du sas d'entrée vérifiée (14 tests), mais 0/8 éléments importants sur 2 holdouts, car les sources parlent en termes de **domaines**, **formules** et **si et seulement si**, et non de « Si ... alors ... ». Ne pas corriger la PR précédente ni retester les mêmes fiches comme nouveau holdout.

## Nouveaux documents choisis à l'aveugle avant lecture
Holdout F1 : `research/bricks/BR-AFFINE-GROUP-CORE_BRIQUE.md` à PR #2 commit `2f71a6b8ed03914c0b5d308520d30e0133d9e9ad`.
Holdout F2 : `research/bricks/BR-ACC-STATE-COMMUTE-01_BRIQUE.md` au même commit. Leur contenu ne doit pas être lu avant dépôt et validation de la calibration du parseur v09.
Calibration connue/nécessaire : BR-CTRL-01 (biconditionnel explicite), BR-MEALY-HELLY-01 (bornes sous hypothèses), BR-OBS-CAP-02 (théorème versus non-théorème). Les scores sur ces sources sont **post-hoc**.

## Contrat de représentation et garde-fous
Construire des *propositions formelles SANS SÉMANTIQUE* :
1. `BICONDITIONAL_SYNTAX`: découper une occurrence littérale unique de « si et seulement si » en deux propositions textuelles non interprétées, uniquement sur une même ligne, sans contresens de signe.
2. `RELATION_CHAIN_SYNTAX`: repérer les expressions mathématiques entre accents graves et conserver, dans l'ordre, les opérateurs littéraux (`=`, `≤`, `>=`, etc.) et les termes **non interprétés**. Une chaîne n'est ni une preuve ni une règle, et une relation figurant dans « Non-théorème » doit être explicitement marquée BLOCKED.
3. `IMPLICATION_SYNTAX`: conserver les propositions du traducteur gelé #161, mais ne jamais forcer une inférence entre fiches ni généraliser hors contexte.
4. `DOMAIN_AND_LIMITS`: exposer les titres de domaine/limitation comme contraintes contextuelles brutes. Le lecteur ne doit JAMAIS déclarer qu'il a vérifié toutes les hypothèses de portée.
5. Les sorties sont vérifiées par un second parcours du texte, avec plages de caractères, lignes, SHA Git et type. Toute conclusion reste `UNREVIEWED`; `horn_rules=[]` et fonction de promotion qui refuse. **Zéro théorème certifié, zéro croyance mathématique nouvelle**.

## Tests/mesures gelés avant expérience
Suite de tests synthétiques contre inversion `x≤y`, équivalence devenue implication, détournement du « non-théorème », références fabriquées, changements de SHA, caractères Unicode, section ambiguë, coûts d'exécution et déterminisme. Noter explicitement toute expression hors grammaire comme ABSTAIN.
Après code/calibration figés, lire F1 et F2 ; geler un gold manuel du même auteur fondé sur les lignes sources (au moins 8 éléments saillants, si disponibles) avant tout run holdout. Résultats par document : couverture brute de ces éléments, typage, fausses promotions et citations incorrectes.
Succès local STRUCTUREL si au moins 1 candidat relation/équivalence sur les deux fiches nouvelles, au moins 25 % des éléments saillants capturés, zéro fausse citation, zéro promotion dangereuse et aucun élément automatiquement injecté au solveur. Si aucune relation syntaxique observable : `INÉVALUABLE`, pas réussite.

## Statut épistémique
Le gold humain est préparé après gel du code mais par le même expérimentateur : il ne constitue pas un arbitrage aveugle indépendant. Même si le score est élevé, cela n'établit pas la correction mathématique, la validité sémantique ou la valeur d'un agent autonome ; il faudra une revue explicite texte→règles avec preuves/exemples avant activation.
