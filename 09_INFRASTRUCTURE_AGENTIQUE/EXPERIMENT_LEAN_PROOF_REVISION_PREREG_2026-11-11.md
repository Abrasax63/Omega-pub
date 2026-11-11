# OMEGA-LEAN-001 — pré-enregistrement formel, gel AVANT code et exécution

**2026-11-11. Corpus synthétique gelé au commit `de4a08399a0f99d420f13e360fbf1deed5785161`** ; 4 scénarios, 24 états (11 calibration, 13 test), 91 jugements. Une nouvelle PR brouillon sera empilée sur #43.

## Hypothèse, nul et vrai objet de preuve

Après la réussite finie de CONG-001, vérifier par un **véritable compilateur de preuve Lean 4** qu'un graphe d'implications théorématiques reste bien typé, que ses dépendances sous hypothèses sont explicites, et que les preuves encore applicables sont conservées après révision.

**Hypothèse nulle prioritaire :** un moteur classique ATMS / index de dépendances correctement implémenté, ayant les mêmes hypothèses et le même budget, obtient les mêmes verdicts et les mêmes économies de revérification qu'un registre de preuve « Omega ». Aucun crédit d'innovation propre à Omega si l'indicateur et le nombre d'invocations Lean sont identiques.

**Portée :** les théorèmes Lean prouvent uniquement des implications **conditionnelles** sous hypothèses `n % m = r`. Ils ne certifient ni la vérité du fait source, ni une source externe, ni une capacité de raisonnement ouvert, ni l'authenticité d'un auteur. En Lean, des hypothèses mutuellement contradictoires permettent par ex falso de prouver n'importe quelle proposition ; un **garde de cohérence distinct** doit donc interdire la promotion de ces preuves comme conclusions globales.

## Données fixées avant algorithme

Source : `09_INFRASTRUCTURE_AGENTIQUE/formal_congruence/cases_lean_001.json`, identifiants `ALT`, `CONTRA` (calibration), `SOURCE_REVISION`, `ALTERNATIVE_BRANCHES` (test). 24 états ordonnés, prémisses modulaires `n ≡ r (mod m)`, avec `m | 60`, événements `activate`, `retract`, `replace` explicites et 91 questions. L'inclusion d'une prémisse remplacée est liée à **l'identifiant et au contenu exact** de sa version, jamais au seul nom ; après rétractation elle peut rester dans l'archive mais jamais être présentée comme actuellement applicable.

Versions gelées : **Lean 4 `leanprover/lean4:v4.26.0`**, disponible à https://github.com/leanprover/lean4/releases/tag/v4.26.0 . Utiliser la chaîne de confiance du compilateur Lean 4 installé sur un runner GitHub Actions. Bannir des preuves générées `sorry`, `admit`, `axiom`, `unsafe` et `native_decide`; interdire les imports Mathlib si non nécessaires. Vérifier la sortie de chaque invocation Lean et arrêter la CI au premier échec inattendu.

## Expérience et trois comparateurs

1. **Oracle arithmétique indépendant** : énumérer tous les résidus `n=0,...,59` après chaque événement et classer les questions en `entailed/refuted/undetermined/inconsistent_environment`.
2. **Baseline ATMS+INDEX (forte)** : maintenir les ensembles minimaux de prémisses versionnées justifiant localement une implication ou une réfutation, analyser la cohérence de l'ensemble actif, et ne réexaminer avec Lean que les **termes de preuve nouveaux non certifiés**, indexés par l'énoncé et les versions exactes de leurs supports. Après un retrait, les théorèmes conditionnels restent en archive, mais leur application courante est suspendue ; une justification alternative encore active reste utilisable.
3. **Omega proof ledger** : même ensemble de justifications, même filtrage, même cache de certificats et mêmes compilations Lean que l'index fort. L'intérêt incrémental éventuel devra venir d'un mécanisme **supplémentaire effectivement exécuté et testé** ; l'égalité doit être rapportée comme résultat nul.
4. **Recompile-full** (référence non strictement à coût égal) : regénérer et compiler avec Lean toutes les preuves actives à chaque état cohérent ; même exactitude attendue, plus d'invocations. Les états incohérents ne doivent pas produire de réponses globales démontrées.
5. **No-revision** (contrôle négatif) : conserver tous les vieux certificats comme s'ils étaient actuels ; en présence de rétractations ou remplacements il doit produire des affirmations périmées détectables. Ce contrôle ne sert pas d'adversaire fort.

Un **fichier Lean généré** contient trois théorèmes par support actif, liés par des applications explicites : `premise_to_claim` → `derived` → `final`, sous les variables des prémisses. C'est une vraie chaîne de dépendances dans le noyau Lean, mais elle est **générée de façon programmée** ; les preuves Lean vérifiées ne deviennent pas des découvertes nouvelles.

Coûts primaires : **nombre de fichiers Lean réellement compilés**, **nombre de triplets de théorèmes réellement compilés**, **nombre de vérifications de certificats nouveaux**. Secondaires : temps wall-clock mesuré sur le runner, rapporté descriptivement sans prétention statistique ; coût de calcul CRT/ATMS et de lecture des états compté séparément ou indiqué explicitement non imputé. Une compilation de fichier contenant K preuves n'équivaut pas à K opérations indépendantes ; rapporter les deux mesures.

## Négatifs et conditions d'arrêt

- Dans les scénarios test, vérifier que le retrait de A n'efface pas une conclusion démontrée par B, et que le retrait des deux fait disparaître le support.
- Remplacement de `A:n%6=2` par `A:n%6=1` en présence de B incohérent : toutes les conclusions globales sont suspendues, même si Lean accepte une preuve par explosion depuis les deux hypothèses.
- Restaurer le contenu original permet de réutiliser **le même certificat conditionnel historique**. Comparer précisément les versions et empreintes.
- Compiler intentionnellement un **faux théorème non démontrable** depuis une prémisse insuffisante doit échouer ; le succès inattendu échoue le protocole.
- Compiler un théorème arbitraire depuis deux hypothèses contradictoires peut **réussir** : ce diagnostic devra rester étiqueté `EX_FALSO_NOT_AUTHORIZED`, et le registre ne doit jamais le promouvoir.
- Une preuve mentionnant une prémisse inactive ou d'une version périmée est refusée avant Lean, une preuve dont le terme échoue dans le noyau est refusée après Lean.
- La validité des justifications et des réponses doit être recalculée sans importer CRT via l'énumération des 60 résidus.
- Tests stricts de modules invalides, de versions, de conflit, de justifications alternatives et d'intégrité de l'historique. Pas d'injection de code Lean depuis un texte libre : toutes les entrées passent une validation stricte d'identifiants, nombres et grammaire.

## Mesures et décision

Rapporter calibration et test séparément, nombre de jugements, erreurs confiantes, versions réutilisées, preuves alternatives et changements d'état,  erreurs de noyau inattendues, et les coûts d'index vs recompilation complète.

**Verdict de projet :** si les résultats du registre Omega sont identiques à ATMS+INDEX, absence d'avantage propre démontré. Si un test Lean échoue : ne pas présenter l'expérience comme réussie. En cas d'incompatibilité d'outil ou d'impossibilité d'exécuter Lean, classer `NON VÉRIFIÉ`. Toute affirmation de « démonstration formelle » exige un vrai log de Lean compilant les théorèmes sur la version fixée.

Pas de fusion main, CORE ou SQLite. Pas de revendication d'émergence agentique.
