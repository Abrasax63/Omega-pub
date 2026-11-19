# Qwen et Omega 031 — grammaire interne des expressions

19 novembre 2026, 13 h 47 (Paris). **EXÉCUTÉ / hypothèse de gain en fidélité RÉFUTÉE sur le pilote.** Branche `experiment/omega-100-2026-11-18`, SHA initial `2af2f150f6ea9335711e34858794e2fda723e956`. Ce pilote poursuit [le précédent](qwen-schema.md) hors numérotation du programme horaire.

[Protocole figé avant lancement](qwen-grammar-protocole.md). Huit cas synthétiques nouveaux, organisés en quatre paires. Même texte, mêmes clés P1/P2/C, même Qwen2.5-Coder-3B-Instruct Q4_K_M, même contrôle 031 et même budget. La référence contraint l'enveloppe JSON. Le candidat ajoute des types, opérateurs et arités à chaque expression. Les prédicats le/eq portent sur n, des entiers et des termes square/mod d'au plus deux niveaux. Le schéma dépend du nombre de prémisses, sans consulter les expressions attendues. Les prédicats Python indépendants sur [-16,16] confirment les 8 verdicts et les témoins calculés à partir des contrats manuels.

| Mesure | Enveloppe seule | Grammaire des expressions |
| --- | ---: | ---: |
| Enveloppes valides | 8/8 | 8/8 |
| Expressions exécutables | 4/18 | 18/18 |
| Expressions équivalentes au contrat sur 33 entiers | 4/18 | 4/18 |
| Verdicts directs corrects / erronés / abstentions | 3 / 5 / 0 | 3 / 5 / 0 |
| Verdicts Omega corrects / erronés / abstentions | 0 / 0 / 8 | 0 / 0 / 8 |
| Jetons entrée / sortie | 1 568 / 368 | 1 568 / 374 |
| Temps d'inférence cumulé | 31,06 s | 30,28 s |

Les huit traductions complètes sont rejetées dans les deux bras. Le [diagnostic après test](qwen-grammar-audit.json) calcule les implications dans les deux sens pour chaque champ. Les 14 expressions candidates divergentes ont une valeur de vérité différente du contrat sur au moins un entier, ce qui exclut sur ce lot l'explication par le seul rejet d'une représentation équivalente. Ce diagnostic utilise l'oracle fini en plus de la validation indépendante des verdicts. Il ne modifie pas la sélection. Le témoin contradictoire inverse les opérandes d'une inégalité et reste exécutable, mais le contrôle 031 le rejette. Son jumeau fidèle est accepté.

Le seuil était d'obtenir au moins deux verdicts vérifiés corrects supplémentaires, sans perte ni erreur vérifiée. Aucun gain de fidélité. Candidat conservé comme preuve reproductible d'un gain syntaxique seulement, écarté comme amélioration du pipeline. Les 16 tests métier et le rejeu 031 (4/6 et 6/6) passent. Le diagnostic rejoue les 16 évaluations enregistrées. Aucun appel payant et aucune nouvelle génération pour le diagnostic.

Reproduction : reprendre les dépendances et les poids du [pilote Qwen](qwen-pilot.md). Lancer le même serveur local sur le port 18724. Copier `qwen-pilot.py` comme `baseline.py`, `qwen-schema.py` comme `pilot.py` et remplacer 18723 par 18724 dans ce dernier. Copier `qwen-schema-aggregate.py` comme `aggregate.py` et `qwen-grammar.py` comme `grammar_trial.py`. Exécuter `python grammar_trial.py private-cases.py > results.jsonl`, puis `python qwen-grammar-score.py results.jsonl` et `python qwen-grammar-audit.py .` avec ses cas locaux non publiés. Les deux bras ont huit appels, un plafond de 384 jetons par réponse, température 0 et graine 71. La référence est exécutée avant le candidat. Les temps sont indicatifs, sur une exécution unique avec cache local.

SHA-256 : préenregistrement `5ed9d5a52ca125bfa8403f37c87783bf54b654c4a12dda006a7408bc6a4aceeb`, harnais `db53e5fab53f394f18a48aa5f6beec84b21909d79ab0c99aefab73379e28fb39`, corpus local `940a58b69f47603537be05d69d23fcaa0d5a00ae67863186a36361f2fcee04b3`, relevé détaillé local `e33605ce45e32efe1f0ad5aee8ca589518b1b8854f0f88665104518d1046335a`, [agrégats](qwen-grammar-summary.json) `b45e056c4aef624cf2d7e499b73df24309f74356d23d661bed1c417dfa317fe5`.

Prochain test : distinguer choix de l'opérateur et extraction des arguments. Évaluer un traducteur déterministe à couverture bornée comme référence sur des formulations nouvelles et des paraphrases, avec inversions de sens comme témoins. Mesurer les abstentions hors couverture avant de connecter une sélection par modèle.
