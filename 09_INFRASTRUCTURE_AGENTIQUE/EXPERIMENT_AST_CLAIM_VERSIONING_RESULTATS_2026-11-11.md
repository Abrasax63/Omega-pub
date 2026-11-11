# OMEGA-AST-001 — continuité des déclarations syntaxiques à travers 40 révisions Git externes

**11 novembre 2026. Statuts : CALCUL REPRODUCTIBLE sur des déclarations AST réelles, EMPIRIQUE HISTORIQUE pour les changements Git, SUPÉRIORITÉ PROPRE À OMEGA NON DÉMONTRÉE.**

## 1. Source et gel avant calcul

Pré-enregistrement : `09_INFRASTRUCTURE_AGENTIQUE/EXPERIMENT_AST_CLAIM_VERSIONING_PREREG_2026-11-11.md`, commit **`4bd76dcec5904ac4680c63db73fd0af1ad4730f4`**, antérieur à l'implémentation de l'expérience et à ses résultats.

Source historique réelle : [Flask, `pallets/flask`, commit `49943b5a94413a530761350f04e896f76e8d620e`](https://github.com/pallets/flask/commit/49943b5a94413a530761350f04e896f76e8d620e), 41 commits consécutifs par **premiers parents**, exactement les mêmes 40 transitions que dans EVIDENCE-001. On sélectionne à la première révision tous les fichiers Python sous `src/flask/` et `tests/` : **65 fichiers**, sans filtrage selon le futur comportement. Vingt transitions de calibration descriptive, vingt transitions de TEST.

Les **922 faits figés** se répartissent en **65 empreintes AST de modules** et **857 déclarations de classes, fonctions et méthodes initialement présentes**. Un fait de signature exclut le corps des fonctions et les décorateurs. L'analyse ne porte ni sur les déclarations ajoutées après le premier commit ni sur la véracité des comportements à l'exécution.

### Précision épistémique essentielle

Un certificat signifie : « dans ce commit Git et ce fichier, le parseur Python observe cette déclaration AST ou cette empreinte syntaxique ». Une déclaration peut conserver exactement sa signature lorsque le corps, la documentation, les commentaires ou d'autres éléments du fichier ont changé. Un certificat de signature **ne prouve pas** que la fonction s'exécute, que son comportement n'a pas changé, que ses dépendances d'exécution sont stables, ni qu'une proposition scientifique est vraie.

## 2. Résultats sur les vingt transitions TEST

Nombre d'occurrences de faits fixes : `922 × 20 = 18 440` pour chaque politique.

| Stratégie | Faits présentés courants et exacts | Faits faussement présentés courants | En attente | Indisponibles | Lectures + parsings AST facturés |
|---|---:|---:|---:|---:|---:|
| `stale_no_refresh` (aucune revalidation) | 17 741 | **699** | 0 | 0 | 0 |
| `file_path_invalidate` (invalidation conservatrice sans reparsing) | 7 471 | 0 | **10 969** | 0 | 0 |
| `full_ast_reverify` (hors budget, référence haute couverture) | **18 164** | 0 | 0 | 276 | 1 300 |
| **`ast_dependency_index_8`** (baseline forte) | **18 164** | **0** | 0 | 276 | **31** |
| **`omega_ast_ledger_8`** (mémoire historique expérimentale) | **18 164** | **0** | 0 | 276 | **31** |
| `invalidate_all_8` (sans index pertinent) | 3 248 | 0 | **15 175** | 17 | 160 |

Les **276 occurrences indisponibles** concernent des déclarations initiales absentes à certaines versions ; ce ne sont pas 276 nouveaux faits différents ni nécessairement 276 changements. Les 31 analyses sont des **unités logiques de lecture + `ast.parse`**, pas des temps CPU mesurés ; les métadonnées Git communes sont exclues du coût. La réanalyse complète excède la limite de 8 consultations par transition et sert **uniquement de référence non admissible à coût égal**.

**Verdict principal :** l'index AST et le registre Omega produisent **les mêmes choix, les mêmes lectures et les mêmes résultats sur les 40 transitions**. Ils conservent **18 164 attestations applicables et exactes** sur les 20 tests sans faux positif, pour 31 parsings, contre 1 300 parsings à la revérification complète. Le bénéfice provient de l'**index des dépendances et de la vérification AST ciblée**, réalisables sans agent intelligent. **Aucun gain spécifiquement attribuable à Omega n'est démontré.**

La politique `file_path_invalidate` est sûre mais beaucoup plus abstentionniste : elle ne peut pas réaffirmer la signature d'une déclaration sans revoir le contenu du fichier modifié. L'index AST peut le faire lorsqu'il dépense la lecture nécessaire. Le mécanisme permet donc une **continuité de portée plus fine**, pas une preuve sémantique nouvelle.

## 3. Changements réellement observés

- **31 événements de fichiers Python du portefeuille modifiés** pendant TEST ; les deux politiques indexées en effectuent exactement 31 analyses.
- Dans les 40 transitions : **79 changements d'état de faits syntaxiques figés** (module ou déclaration) et **21 changements d'état de faits de déclaration** (modification, disparition ou réapparition) ; dans les 20 transitions TEST, **5 changements d'état de faits de déclaration**. Le corpus est donc discriminant, bien que la fréquence des modifications de signatures soit faible.
- **1 événement** a modifié les octets d'un fichier Python du portefeuille sans modifier son AST complet (par exemple un changement purement lexical/formatage : ce rapport ne prétend pas identifier sa cause sans une annotation dédiée).
- Le registre final contient **3 093 versions d'attestations syntaxiques historiquement rattachées à un commit et à l'identifiant Git du blob**. La seconde voie constate **2 106 réémissions dont l'empreinte de signature reste identique alors que l'identifiant Git du blob source change**. Ce sont des occurrences de certificats versionnés, pas 2 106 déclarations distinctes.
- Les 20 premières transitions de calibration avaient déjà `18 330` occurrences exactes, `110` indisponibles, `0` faux positifs, et `28` analyses pour l'index AST et Omega.

Les attributs AST ne constituent **pas une équivalence comportementale Python** : un décorateur nouveau, un import modifié, une dépendance externe ou une modification du corps de fonction peut changer le comportement sans changer la signature suivie. Pour ces propriétés, le statut est **NON VÉRIFIÉ**, et non « vrai ».

## 4. Deux voies d'audit, tests négatifs et limites de leur indépendance

### Validation externe réellement réussie

- [GitHub Actions `43088629074`](https://github.com/Abrasax63/Omega-pub/actions/runs/43088629074) — première épreuve externe, 9 tests de régression et rejeu complet des 40 transitions.
- [GitHub Actions `43089045306`](https://github.com/Abrasax63/Omega-pub/actions/runs/43089045306) — **SUCCESS**, même corpus figé et **vérification indépendante des faits et archives**.
- [GitHub Actions RCE `43089001555`](https://github.com/Abrasax63/Omega-pub/actions/runs/43089001555) — **SUCCESS, 227 tests du Prisme**, six tests MCP, tests RCE/index réussis.
- [Artefact JSON intégral du registre AST](https://github.com/Abrasax63/Omega-pub/actions/runs/43089045306/artifacts/13886584548).

### Deuxième voie de vérification

`prism/ast_claim_independent_crosscheck.py` ne réutilise ni les fonctions d'extraction ni le code de sélection des politiques du module principal. Il reconstruit les faits par un **parcours différent de l'AST**, relit lui-même les arbres/objets Git, recalcule les états sur les **40 transitions**, contrôle **36 880 décisions de statut fait×révision** (`922 × 40`), reconstitue l'ordre des **59 parsings ciblés** et revérifie **chacun des 3 093 certificats** contre le blob source de leur commit historique. Il confirme aussi **1 004 occurrences incorrectes** du témoin sans actualisation, réparties `305 + 699` entre calibration et test.

**Limite d'indépendance :** les deux implémentations utilisent le parseur standard Python `ast` et les **mêmes fichiers Git**. Elles évitent la réutilisation du code de calcul principal mais ne sont pas deux formalismes sémantiques indépendants, ni une analyse dynamique de Flask, ni une preuve de sécurité de l'environnement Python.

### Contre-tests négatifs

Les neuf tests Python vérifient :
- changement de commentaire et de formatage sans modification des faits AST ;
- changement du corps de fonction modifiant l'AST du module mais **pas** la signature ;
- changement réel d'arguments, avec conservation de l'ancienne attestation au commit antérieur ;
- suppression d'une déclaration et ajout d'une nouvelle (non ajoutée opportunément au corpus fixe) ;
- suppression du fichier ;
- dépassement du budget de huit analyses, conduisant à une attente et non une vérité inventée ;
- manifeste Git inventé ou incomplet bloqué contre les arbres Git ;
- échec du parseur donnant **abstention** ;
- modification de décorateur montrant que **même signature ne certifie pas même comportement**.

## 5. Implication pour le projet et arrêt

**DÉMONTRÉ DANS LE MODÈLE D'OBSERVATION AST** : on peut conserver une attestation de déclaration syntaxique au travers de versions successives d'un fichier, en revalidant le contenu réellement pertinent et en maintenant un historique de sources précis. Le danger d'une réponse périmée peut être évité par une abstention ciblée.

**NON DÉMONTRÉ** : qu'Omega apporte plus que l'index AST conventionnel, qu'il vérifie des affirmations mathématiques ou scientifiques, qu'il authentifie les auteurs de dépôts, qu'il découvre des stratégies ou qu'il améliore la résolution de nouveaux problèmes.

**Décision :** ne pas ajouter de profondeur de planification pour exploiter des données où un index suffit. Passer à des **preuves structurées, des dépendances de théorèmes, des hypothèses contradictoires et des témoins de réfutation** vérifiables par un moteur indépendant du fournisseur, avec une baseline forte ayant la même bibliothèque, les mêmes contrôles et les mêmes coûts. Les prochains progrès doivent viser la *qualité du raisonnement et de la vérification*, pas seulement les économies de relecture.

**Statut de branche :** PR brouillon empilée sur #41 ; pas de merge de `main`, aucune écriture SQLite, CORE ou mémoire scientifique certifiée.
