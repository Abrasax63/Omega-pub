# Omega RH-READING-01 — premier benchmark de lecture mathématique

**Date : 22 novembre 2026. Résultat exécuté. Branche expérimentale PR #230, pas de fusion, aucun appel payant et aucune suppression de preuve historique.**

## Sources et limites documentaires

- Source A (déclaration primaire) : [Lean and Mathlib, 21 novembre 2026](https://leanprover-community.github.io/blog/posts/riemann-hypothesis/). Les communautés Lean/Mathlib déclarent avoir vérifié le développement formel d'Alpöge. **Nous n'avons ni téléchargé, ni compilé, ni vérifié les 17 millions de lignes.**
- Source B : [Michael Rubinstein, guide de 164 pages (brouillon du 21 novembre 2026)](https://www.math.uwaterloo.ca/~mrubinst/alpoge_claude_grh/zeta-paper.pdf). Voir Introduction p. 2 et Part I.0 p. 3. Il indique que le raisonnement présenté déduit RH d'une inégalité principale (M) et des estimations (B) et (C). Les estimations B et C sont démontrées dans ce guide à partir de résultats cités, mais **la preuve complète de (M) y reste importée du développement Lean**, sans démonstration autonome dans le guide.

Le contrôle distingue un théorème formellement certifié par des tiers de son exposé humain encore incomplet. Un moteur qui conclurait « (M) est prouvé dans ce guide » ou « le benchmark a démontré RH » échouerait épistémiquement.

## Protocole exact

Les données sont dans `riemann_reading_cases.json`, les calculs dans `riemann_reading_benchmark.py`, les tests dans `test_riemann_reading_benchmark.py`.

1. La réduction conditionnelle **M et B et C => RH** est traduite **manuellement**, avant le test, dans un langage d'implications Horn à deux prémisses maximum. Le nœud `mb` est une **conjonction administrative**, absolument pas un lemme original du guide.
2. Seize requêtes préenregistrées : hypothèses présentes, retirées ou inversées ; inversion illicite de la conclusion, permutation des règles, paraphrase contrôlée, texte non supporté et prémisses sans lien.
3. Moteur testé **sans modification** : `09_INFRASTRUCTURE_AGENTIQUE/controlled_entailment/engine.py` du programme Omega 100. Comparaison avec le mode existant `one_pass` (une seule passe synchrone) et un oracle indépendant **par énumération de valuations booléennes** à partir des règles annotées manuellement.
4. Les certificats Horn retournés sont revérifiés sur les 14 cas de logique admissibles.
5. Contrôle arithmétique indépendant : `math.comb(2*n, n)` et nombres premiers dans `n < p <= 2*n` pour `1 <= n <= 48`. Il est vérifié que tous ces premiers divisent le coefficient binomial central et que ce coefficient est inférieur ou égal à `4**n`. Un contre-exemple réfute la réciproque abusive (n=4, p=2), un autre montre la nécessité de la frontière stricte (n=3, p=3), et n=5 réfute la borne plus forte `3**n`.
6. Aucun résultat fini n'est considéré comme preuve ou vérification numérique de RH.

## Résultat effectivement observé

[GitHub Actions run 45054327471](https://github.com/Abrasax63/Omega-pub/actions/runs/45054327471), commit `f7ff119418ca23228d47ad9b55e01e3fabf087bf`, **SUCCÈS**.

| Méthode | Correct / 16 | Abstentions | Conclusions abusives (« entailed ») |
| --- | ---: | ---: | ---: |
| Moteur Omega 100 à clôture Horn complète | **16 / 16** | 2 / 2 attendues | 0 |
| Référence `one_pass` (une seule passe) | **12 / 16** | 2 / 2 attendues | 0 |

**14/14 certificats logiques vérifiés**, dont les contre-modèles sur les cas sans conséquence logique. **276 vérifications de divisibilité** sur les intervalles finis et 48 contrôles de la borne du coefficient binomial central, sans erreur.

Les **37 tests logiciels** du workflow (4 raccord, 7 file, 7 réflecteur, 6 synthèse, 6 benchmark RH et 7 provenance existante) sont verts, ainsi que la restauration du registre scientifique inter-runs.

## Statut épistémique et véritable portée

- **VÉRIFIÉ (calcul fini)** : les 16 verdicts Horn du test contrôlé, comparés à l'oracle indépendant de la clôture ; les valeurs du coefficient binomial et divisibilités.
- **VÉRIFIÉ (intégration)** : le moteur Omega 100 est réutilisé tel quel et conserve des certificats rejouables ; les 37 tests du workflow passent.
- **NON DÉMONTRÉ** : extraction de la dépendance M+B+C depuis le texte original du PDF ; lecture autonome de la preuve Lean ; capacité générale à expliquer la preuve et à résoudre de nouveaux lemmes mathématiques ; découverte originale ; amélioration face à un autre modèle de langage.
- **LIMITATION CRITIQUE** : les 16 situations sont créées par l'expérimentateur à partir d'un même schéma logique ; elles ne constituent **ni un holdout externe, ni un benchmark de compréhension sémantique libre, ni une validation de la preuve de Riemann**. La référence `one_pass` est volontairement réduite et ne constitue pas un modèle concurrent solide.
- Les URLs de sources sont indiquées, mais le pipeline CI n'a pas importé ni épinglé l'intégralité du PDF ou du dépôt Lean. La fidélité des annotations à la source primaire requiert donc une revue externe.

## Prochaine expérience discriminante

Utiliser un extrait brut et daté du texte de Rubinstein (sans indices ajoutés), faire produire par Omega **lui-même** une interprétation M/B/C, « M importée de Lean », les hypothèses exactes et le statut de chaque section. Pré-enregistrer séparément les annotations de référence. Tester des variantes en changeant une hypothèse et demander un contre-exemple. Vérifier si la sortie survit à des réordonnancements et à une paraphrase externe. Ce test nécessitera un moteur de lecture sémantique réellement raccordé, pas le seul moteur Horn sur texte déjà normalisé.

**Décision** : garder l'expérience comme référence de calcul exact et de prévention d'inférences abusives, sans promouvoir une compétence générale ni activer un cycle autonome de 15 minutes sur `main`.
