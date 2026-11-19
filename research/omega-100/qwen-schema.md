# Qwen local et Omega 031 — prémisses numérotées et JSON contraint

19 novembre 2026, 13 h 42 (Paris). **EXÉCUTÉ / hypothèse de gain vérifié RÉFUTÉE dans le pilote.** Branche `experiment/omega-100-2026-11-18`, départ `614cc450119bcff93aca52d2326af0e48e53a299`. Suite du [premier pilote](qwen-pilot.md), hors numérotation du programme horaire.

Le [préenregistrement](qwen-schema-protocole.md) exigeait huit formats valides, au moins deux verdicts exacts de plus après vérification, aucune perte de verdict vérifié correct et aucun verdict vérifié erroné. Le témoin négatif au bon format, avec conclusion falsifiée, est rejeté. Huit nouvelles obligations synthétiques appariées, sur les entiers de −16 à 16 inclus, sont annotées séparément par prédicats Python. L'oracle sur les contrats manuels retrouve les huit verdicts et premiers témoins. Aucun corrigé n'est inclus dans l'invite.

| Mesure | Référence historique | Prémisses identifiées et schéma |
| --- | ---: | ---: |
| Formats conformes au contrat de réponse de chaque bras | 0/8 | 8/8 |
| Traductions complètes acceptées par Omega 031 | 0/8 | 0/8 |
| Verdicts directs corrects / erronés / abstentions | 2 / 5 / 1 | 3 / 5 / 0 |
| Verdicts vérifiés corrects / erronés / abstentions | 0 / 0 / 8 | 0 / 0 / 8 |
| Jetons entrée / sortie | 1 431 / 860 | 1 581 / 370 |
| Temps d'inférence cumulé | 92,98 s | 37,11 s |

Même Qwen2.5-Coder-3B-Instruct Q4_K_M, 8 appels locaux par bras, température 0, graine 71 et 384 jetons de sortie maximum. Référence exécutée d'abord. Les invites diffèrent et le candidat reçoit 150 jetons d'entrée de plus. Temps mesurés sur une exécution avec cache du serveur, sans estimation de variance. Le traitement après génération a pris 0,38 ms et 1,99 ms respectivement, hors préparation humaine. Voir les [mesures](qwen-schema-summary.json).

La référence échoue sur le nombre de prémisses dans sept cas et sur le JSON ou le verdict dans le dernier. Le candidat produit les champs attendus puis échoue à la liaison AST sur les huit cas. Le schéma limite les clés, la longueur extérieure des listes et le verdict. Il autorise encore un contenu incorrect dans ces listes. Après le test, [un diagnostic](qwen-schema-diagnostic.py) a vérifié séparément les 18 champs candidats sur le domaine fini : 4 identiques au contrat, 12 non interprétables et 2 interprétables dont l'ensemble des valeurs de vérité diffère. L'audit des champs réutilise l'oracle et ne modifie aucun verdict. Voir le [relevé](qwen-schema-diagnostic.json).

Décision : retenir l'observation de format, écarter le candidat comme amélioration de la chaîne complète. Les deux interventions ont été appliquées ensemble, leur contribution respective est indéterminée. Le rejeu 031 garde ses 6/6 (référence 4/6) et les 16 tests métier passent. Le rejeu des 16 réponses enregistrées reproduit tous les scores sans nouvelle inférence. Cas, corrigés et sorties individuelles conservés hors commit.

Reproduction : reprendre les poids et les trois fichiers Omega aux noms locaux indiqués dans le [premier pilote](qwen-pilot.md) et lancer le même serveur sur le port 18723. Copier `qwen-pilot.py` comme `baseline.py` et remplacer son port 18722 par 18723. Dans ce dossier, lancer `python qwen-schema.py CAS_LOCAUX.py > results.jsonl` avec huit cas et leurs prédicats locaux, puis `python qwen-schema-aggregate.py results.jsonl`. Le diagnostic importe le harnais sous le nom `pilot.py` et lit les réponses locales archivées. Poids SHA-256 `724fb256bec1ff062b2f65e4569e871ad2e95ab2a3989723d1769c54294730b7`. Préenregistrement `2a0a8479bb7961fe2f11f4d8e8df84833ca5c47632dbe86548a2b6b296bf629e`. Corpus local `87be27dd1151aa72737f8d19b0ac879babe4000ba20ab5b1c18665e5b5d0dfa4`. Relevé détaillé local `57d376d00bbd1d2d3a99dafdfe242edb78ca7aac57dc8aa05d6cadf01e7b93a5`.

Prochain test décisif : garder les clés numérotées communes aux deux bras et changer uniquement la grammaire interne des AST, en imposant les opérateurs et types supportés. Mesurer sur de nouveaux cas le passage de la syntaxe valide à la fidélité, avec un témoin négatif qui respecte la grammaire mais inverse une inégalité.
