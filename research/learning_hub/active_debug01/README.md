# OMEGA ACTIVE-DEBUG01 — programmer, exécuter, corriger, vérifier

**Expérience du 23 novembre 2026. Branche et PR indépendantes ; main inchangée.**

## Objectif falsifiable

Le gain du LoRA SFT01 sur des erreurs de *syntaxe* n'avait pas été transféré aux erreurs de *logique* (0/12 sur SEMANTIC04). Une correction symbolique locale avait réussi 11/12, et un audit rétrospectif après changement du générateur 12/12 sur l'ancienne cohorte. Il manque une comparaison indépendante entre un **vrai modèle spécialisé en programmation**, une seconde génération sans outils et une seconde génération munie de l'**exécution réelle**.

Ce pilote compare sur six fonctions synthétiques inédites et une seule faute sémantique par fonction :
- Qwen2.5-Coder-3B-Instruct Q4_K_M, première génération ;
- même modèle, deux appels et **seconde révision sans exécution** ;
- même modèle, deux appels et **feedback d'exécution du code précédent sur deux exemples publics** ;
- correcteur symbolique \`execution_guided.resolve\` réutilisé depuis PR #237 ;
- hybride protégé \`execution_guided.resolve_guarded\`, qui ne doit pas dégrader une solution symbolique admissible uniquement parce que le modèle propose une autre correction.

La **première génération est partagée**, ce qui élimine la variabilité initiale et limite réellement les requêtes à **18 au total**. La comparaison des deux révisions est à deux appels chacune, 400 tokens de génération maximum/appel, même seed/température ; seul le bras avec outils reçoit les sorties d'exécution. Les tokens de prompt et la durée sont mesurés et peuvent différer — le feedback coûte aussi des tokens et des tests.

## Données et provenance

- [Préenregistrement PREREG.md](PREREG.md), committé **avant** la cohorte et l'inférence.
- [Six familles gelées](FROZEN_BENCHMARK.json), **blob git 73ba10b629206dd3d771cb03048031157645ab38** : chacune comporte une source défectueuse qui compile, un objectif, deux observations visibles et cinq tests finaux séparés (30 au total).
- [contract.py](contract.py) conserve le hash exact et ne donne au runner d'inférence que \`id,family,broken,public,prompt\`. Le corrigé source et les tests cachés ne sont récupérés **qu'après les 18 appels** par \`grade.py\`. Les données sont publiques dans le dépôt mais ne sont pas passées au modèle.
- [inference.py](inference.py) : API llama.cpp **locale**, aucune clé. Les programmes générés sont contrôlés par l'AST puis exécutés avec les limites mémoire/CPU du laboratoire existant \`prog_reconstruction_pilot.py\`. Les sorties publiques constituent le feedback.
- [grade.py](grade.py) : évaluation **ultérieure** du nombre de fonctions passant tous les cinq tests, des erreurs d'exécution, des erreurs silencieuses, des abstentions, des coûts en tokens/appels/durée, et des écarts appariés.
- [test_active_debug01.py](test_active_debug01.py) : tests contradictoires de contrôle de fuite, exactitude de l'oracle, échec des programmes initialement défectueux, conformité à l'AST et limite des appels.

## Limites & état

C'est un **pilote de six programmes jouets** et non un benchmark industriel, un entraînement de modèle, une AGI ou une preuve de transfert général. Les exercices ont été construits à la main, donc ne sont pas des « nouvelles compétences découvertes par Omega ». Les évaluations précédentes SFT01 et SEMANTIC04 ne sont pas recyclées. Une fois la cohorte notée, elle devient consommée.

Qwen2.5-Coder-3B-Instruct est un modèle préentraîné pour la programmation, pas un modèle entraîné par Omega. Le GGUF évalué est celui de [bartowski sur Hugging Face](https://huggingface.co/bartowski/Qwen2.5-Coder-3B-Instruct-GGUF/blob/main/Qwen2.5-Coder-3B-Instruct-Q4_K_M.gguf), SHA256 3da3afe6cf5c674ac195803ea0dd6fee7e1c228c2105c1ce8c66890d1d4ab460. La page indique une licence **qwen-research** : usage expérimental et réexaminer la licence avant toute commercialisation. Le moteur llama.cpp \`b12633\` et le sandbox ont été utilisés dans les PR #232–234.

Le workflow sur CPU GitHub Actions est borné en requêtes, durée et tokens ; **aucun appel à une API payante**. Les fichiers bruts, les métriques et le SHA du modèle sont archivés. Une CI verte prouve le pipeline, pas un apprentissage de poids ni une compréhension générale.

**Statut avant run** : code du pilote proposé et contrôles logiciels à exécuter ; aucune réussite modelée ne peut être annoncée tant que le premier run n'a pas terminé.

### Après le pilote

Quel que soit le verdict, conserver le principe : quand l'outil symbolique suffit, ne pas gaspiller un appel neuronal ; lorsqu'il échoue, demander au modèle une correction vérifiable à partir des erreurs d'exécution. Construire ensuite un autre holdout de défauts et de fonctions indépendants, pour vérifier un éventuel gain sans avoir réglé les scripts sur les mêmes six problèmes.
