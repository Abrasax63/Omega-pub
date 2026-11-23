# OMEGA-SELF-TEACH-03 — préenregistrement immuable AVANT code / inférence (23 novembre 2026)

## Motivation tirée des runs déjà consommés
PR #242 : 0/15 A=B strict, puis réanalyse du FORMAT 5/15 A=B (post-hoc).
PR #244 : A=12/18, P=12/18, B=13/18, **aucune leçon admissible**, pratique T1 1/8 → 2/8 → 1/8. Il manquait surtout la trace des codes et retours exacts de chaque correction. Aucun résultat de ces cohortes ne sera réutilisé comme test aveugle.

## Hypothèse falsifiable
Un diagnostic sur contre-exemples minimaux, journalisé **avant la réponse du modèle**, augmente-t-il les corrections réussies sur nouveaux exercices, et une leçon auto-produite et vérifiée améliore-t-elle des problèmes de **familles indépendantes** au-delà de la simple consigne générique ?

## Plan gelé avant tout nouveau modèle
- 2 familles de pratique, chacune avec 5 exemples publics + 10 cas de développement (oracles explicites créés par le concepteur). Choix du score initial le plus faible, départage par ID stable. 2 corrections au plus avec feedback sur **3 contre-exemples minimaux**, et un ensemble distinct de cas de rétention sur le même développement empêchant la régression (tous les 10 cas restent notés).
- **3 nouvelles familles de transfert**, 2 exemples publics chacune, plus **18 cas cachés** (6 × 3). `EVAL_SEALED_FROZEN.json` n'est lu par le scoreur qu'après la génération de A/P/B. Aucune famille ni entrée de l'ancien holdout #242/#244 n'est recyclée. Tous les ensembles sont gelés par SHA Git blob AVANT la construction du programme.
- **A (direct)** : une génération par tâche (plafond 660 nouveaux tokens).
- **P (contrôle de consigne)** : même nombre de générations, conseil fixe et générique.
- **B (leçon vérifiée)** : même plafond et nombre de générations, leçon issue de l'entraînement uniquement si la meilleure correction du cursus est sûre, strictement meilleure que le départ et réussit 10/10 cas de développement. Sinon B reçoit le même conseil fixe que P ; les variations entre P/B ne peuvent pas être qualifiées d'apprentissage.
- **C LoRA** : blocage explicite 0 poids mis à jour jusqu'à 24 solutions vérifiées/12 familles avec vérification indépendante et nouvelle cohorte dédiée.

## Changement technique ciblé
- Au moment de chaque tentative, écrire un enregistrement horodatage logique (index et précédent SHA256) conservant : prompt complet ou hash, raw réponse, raw SHA256, hypothèse formulée par le modèle (champ JSON), code validé sous AST, état strict / récupéré, 10 valeurs attendues et reçues en développement, nature des erreurs, code précédent, décision accepter/rollback et raisons.
- Trier les cas qui échouent par `(len(input), input)` ; ne montrer que les 3 plus petits et identifier les entrées/sorties, sans corriger soi-même l'algorithme ni exposer les tests cachés.
- Le même normaliseur étroit déjà validé par #242 s'applique à A/P/B, puis AST et sandbox #232.
- Les 10 cas de développement sont des données de pratique visibles dans les retours. Aucune note au modèle ne contient un cas caché.

## Mesures, verdicts et faux positifs
- Nombre de révisions 0..2, succès 10/10, taux d'erreurs de code/format, rollback, coûts (appels/tokens/temps), qualité de la trace chaînée.
- Sur le nouvel examen 18 cas : exactitude A/P/B, tâches totalement exactes, régressions, codes sûrs, erreurs silencieuses, variation P/B si aucun souvenir admis.
- Verdict **exploratoire** uniquement si une leçon issue de l'entraînement est admise, B>A et B>P et aucune tâche de base entièrement réussie ne régresse. Sinon **pas d'apprentissage autonome démontré**. Même un éventuel gain ne prouve pas une causalité générale.
- Une CI verte prouve seulement les invariants logiciels ; un test simulé ne constitue pas une nouvelle découverte du modèle.
- Branche/PR DRAFT, GitHub Actions CPU et modèles publics épinglés, zéro API payante, pas de changement de `main`. Après le premier score, le nouveau holdout est **consommé** et le job de modèle ne doit pas se relancer automatiquement.
