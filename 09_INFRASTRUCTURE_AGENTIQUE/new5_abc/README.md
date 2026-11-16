# Omega NEW5-ABC-01 — pilote exploratoire prospectif sur cinq vrais bogues

**Statut initial : code expérimental, aucun taux de réparation présumé.**

### Hypothèse

Tester la valeur propre du diagnostic par traces et d'une sélection par LLM sur le **même ensemble de patches AST**, pas comparer un modèle à une baseline artificiellement affaiblie. En cas de 0/5, de non-reproduction des régressions ou d'infrastructures historiques incompatibles, publier le résultat négatif et **ne pas remplacer les problèmes** après observation.

### Cohorte et sources exactes

- **tqdm-3 et tqdm-4** (deux versions historiques distinctes, `test_bool`, `test_nototal`).
- **cookiecutter-3 et cookiecutter-4** (`test_click_invocation`, `test_run_failing_hook`).
- **httpie-1** (`test_unique_filename`).

Le manifeste [COHORT_FREEZE.json](COHORT_FREEZE.json) contient chaque SHA Git buggy/fixed, chaque chemin de test et les URLs BugsInPy correspondantes. Un verrou de préenregistrement [PREREG_2026-11-16.md](PREREG_2026-11-16.md) a été commité avant le moteur de réparation et avant l'inférence.

Les fichiers de tests remontent aux commits fixes **mais seuls ces fichiers** sont récupérés pendant la sélection ; les sources de production corrigées et les diff sont interdits à cette étape. Cela constitue une séparation procédurale, pas une évaluation aveugle indépendante sur des dépôts privés.

### Bras A/B/C

A. *A_lexical_symbolic* — sélection lexicale de quatre candidats maximum.
B. *B_trace_symbolic* — la même grammaire et le même ensemble de candidats, réordonnés par fichiers/fonctions réellement appelés dans la trace du **test défectueux** ; quatre tests de patch maximum. La trace guide le classement, mais le système ne réapprend pas encore une stratégie générale.
C. *C_trace_symbolic_plus_qwen* — un véritable appel Qwen2.5-Coder-3B Q4_K_M (au plus 128 tokens sortants) pour choisir un **ID parmi les douze meilleurs de B** ; maximum quatre tests de patch. Si la réponse n'est pas un ID exact de la liste, abstention explicite. Le modèle ne génère pas de code arbitraire.

Le **coût des appels du modèle** n'est pas égalisé avec les bras A/B. Il est documenté séparément ; seule la limite de quatre essais de correctif par bug est commune. Un ID invalide n'ouvre pas un budget supplémentaire.

### Chaîne et périmètre

- `abc_fetch.py` : récupère les cinq snapshots exacts, teste les SHA, et interdit le téléchargement des sources fixes dans le premier job.
- `abc_core.py` : grammaire AST générique de PR #106, empreintes des codes avant/après, même pool limité à 90, ordre A/B/C contrôlé.
- `abc_runner.py` : builds des dépendances historiques, tests upstream réellement lancés dans Docker sans réseau, profilage de fonctions, au plus quatre correctifs par bras, sélection Qwen locale et sérialisation des résultats. Aucun correctif lu.
- `abc_oracle.py` : ne fonctionne qu'après la validation de l'empreinte du manifeste gelé. Contrôle `buggy FAIL` et `fixed PASS`, puis rejoue la version modifiée choisie. **Ne teste que la régression cible**, pas toute la suite amont.
- `test_abc_core.py` et `test_pipeline.py` : contrôles unitaires et tentatives de falsification.
- Workflow GitHub `.github/workflows/omega-new5-abc-real.yml` : deux jobs, lecteur seul ; chaque étape et chaque échec restent dans les journaux et artefacts. Aucune API payante.

### Limites causales de la comparaison à garder visibles

Le pool commun de 90 patches au maximum est construit comme l'union de candidats lexicaux et de candidats qui correspondent aux fichiers observés dans la trace. **Le bras A ne voit pas les scores de trace**, mais bénéficie indirectement d'un pool qui a été partiellement guidé par les traces pour garantir l'égalité des candidates. **B−A mesure donc surtout l'effet du classement guidé**, pas l'effet total de l'existence d'une instrumentation par rapport à une vraie recherche sans trace. C−B teste seulement l'effet d'une sélection d'ID via Qwen, pas une génération libre de nouveau programme.

Les mêmes tests upstream authentiques peuvent servir au diagnostic et à la sélection, puis à la reproduction par l'oracle : **aucun test extérieur inconnu n'est évalué**. Un éventuel patch PASS peut surapprendre le test ciblé. Seule une nouvelle cohorte de tests jamais vus permettra d'avancer vers une revendication de réparation générale.

### Interprétation correcte

Les cas dont les dépendances ne s'installent pas, dont le test échoue pour une raison infrastructure, ou dont le buggy ne FAIL pas sont **bloqués** et ne sont pas considérés comme réparés. Seuls les cas `buggy FAIL / fixed PASS / patched PASS` permettent de constater la correction **du seul test cible**.

Ce pilote ne garantit ni absence de régression sur la totalité du logiciel, ni bénéfice d'un LLM à coût complet égal, ni transfert statistique sur des bugs inconnus. Une CI verte **ne signifie pas** qu'une réparation a réussi.

**Pas de modification de main ni de la bibliothèque CORE, pas de fusion automatique, aucune promotion scientifique.**
