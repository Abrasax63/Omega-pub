# OMEGA-SELF-TEACH Reader V2 — correctif candidat, distinct du benchmark

Date : 23 novembre 2026. Branche successeur de la PR #242, sans aucune fusion dans main.

## Observation à corriger
Le run original [#45118652661](https://github.com/Abrasax63/Omega-pub/actions/runs/45118652661) donne A=0/15, B=0/15, avec 0 leçon admise et 9 générations. Un audit post-hoc strictement rétrospectif [#45119315453](https://github.com/Abrasax63/Omega-pub/actions/runs/45119315453) retrouve A=5/15 et B=5/15 en corrigeant certains changements de ligne littéraux \n sans modifier la logique. Il ne s'agit pas d'un gain d'apprentissage.

## Ce qui est implémenté ici
- `reader_v2.py` : une fonction `inspect_candidate(raw, safe)` qui exige un JSON avec un seul champ de code, accepte le Python déjà correct et ne tente une normalisation que si une fonction complète contient des délimiteurs littéraux `\\n` hors chaîne.
- Tous les programmes passent ensuite le vérificateur AST existant de la PR #232 ; les appels interdits, imports et structures malformées restent refusés.
- Le statut `SAFE_PYTHON_FORMAT_NORMALIZED_NOT_LEARNING` sépare le rétablissement du format de toute réussite sémantique.
- `test_reader_v2.py` contient des témoins positifs et négatifs. Le workflow CI est purement hors ligne.

## Frontière scientifique
Le benchmark original et les rapports de la PR #242 sont inchangés. Cette PR ne réexécute **aucun** des 15 cas cachés déjà consommés, n'entraîne aucun poids, ne crée aucune leçon, ne touche pas le routeur horaire, et n'active pas automatiquement ce lecteur dans les anciens pipelines.

## Prochaine expérience décisive
Avant d'activer le lecteur V2 :
1. préenregistrer de nouvelles familles de tâches et des tests réellement inconnus de la génération ;
2. faire deux bras A (sans mémoire) et B (avec leçon vérifiée), avec mêmes plafonds de génération, coûts totaux tracés et une cohorte de rétention ;
3. n'utiliser le LoRA C qu'avec un ensemble diversifié de corrections admises et un troisième jeu d'évaluation indépendant ;
4. consigner séparément format, sécurité syntaxique, comportement exact, transfert et régressions.
Un échec reste un résultat valable. Aucune compétence générale ou autonomie démontrée ici.
