# V19 — une composante disjointe interdit un certificat limité au cycle

19 novembre 2026, 03 h 49 (Paris). **EXÉCUTÉ / RÉFUTÉ** pour le certificat restreint testé ; calcul fini exact, aucune promotion de théorème. Branche `work/omega-math-brick-pilot-2026-11-14`, SHA initial [396ba4d8836a173d1197ff2019a3577150443e3b](https://github.com/Abrasax63/Omega-pub/commit/396ba4d8836a173d1197ff2019a3577150443e3b). Dernier cycle : [cohérence présupposée](OBS-V19-COHERENCE-ASSUMPTION_2026-11-19.md). Dernière provenance : [8fdb144](https://github.com/Abrasax63/Omega-pub/commit/8fdb14445942c9637cb3528797833191f96473b8).

Définition source relue : ombre = projection des colorations extensibles à toutes les contraintes. Le projecteur #5 propage aussi les composantes non encore colorées, contrairement à une propagation uniquement ancrée au cycle. Sources épinglées : [audit](OBS-V19-LPLUS1-AUDIT_2026-11-14.md), [index #2](https://github.com/Abrasax63/Omega-pub/blob/2f71a6b8ed03914c0b5d308520d30e0133d9e9ad/research/bricks/INDEX_BRIQUES.md), [source #5](https://github.com/Abrasax63/Omega-pub/blob/639dc01ca3ea58c61b075adb9a6d860bf41db7bc/research/code/audit_v19_c5_independent_2026-11-04.py), [convention #18](https://github.com/Abrasax63/Omega-pub/blob/763d77f0aa735d90bb558b2c7fac056298d5313c/02_MATHEMATIQUES/v19_c5/TEST_OPTIMALITE_LOCALITE_L_PLUS_1_2026-11-10.md).

Question fixée avant test : sans cohérence globale présupposée, peut-on limiter le certificat de cohérence aux contraintes du cycle ? Entrées : C4 et 3 états disjoints (27 applications), puis réserve C5 et 4 états disjoints (256 applications). Événement : paire (0,1), horizon 2. Toutes les applications sur les états disjoints sont énumérées. Témoin négatif en premier : trois états envoyés sur un même état, imposant un triangle de différences XOR. Référence fixe : projecteur exhaustif de toutes les colorations. Comparateurs : garde limité aux contraintes du cycle, garde global existant. Succès requis : zéro faux résultat non vide et zéro divergence ; budget 283 cas, moins de 30 s, aucun appel. Le [préenregistrement](../code/v19-disjoint-prereg-2026-11-19.md) est conservé ; son heure a été corrigée à partir de l'horodatage local du fichier, sans changer les critères.

| Famille | Cas | Faux non-vides du contrôle restreint | Erreurs du garde global | Temps exhaustive / restreint / global (s) |
| --- | ---: | ---: | ---: | --- |
| Développement C4 + 3 | 27 | 4 | 0 | 0,002957 / 0,000390 / 0,000315 |
| Réserve C5 + 4 | 256 | 65 | 0 | 0,066245 / 0,007880 / 0,005570 |

Contre-exemple : T=(1,2,3,0,4,4,4). Le contrôle restreint renvoie {0,7,8,15}, le projecteur exhaustif renvoie l'ensemble vide. Les états 4,5,6 imposent trois différences mutuelles impossibles à satisfaire avec deux couleurs. Remplacer leur dynamique par un cycle de longueur trois supprime cette obstruction sans changer les transitions du cycle observé. Les composantes réellement disjointes sont nouvelles par rapport à la précédente famille à états libres reliables au préfixe.

Décision : candidat restreint rejeté, référence globale inchangée. Aucune abstention : les 283 résultats sont calculés exactement. Aucun nouveau gain de coût revendiqué ; le garde global était déjà disponible. Ce résultat ne réfute pas un énoncé qui suppose explicitement la cohérence globale. Originalité bibliographique non évaluée.

Non-régressions exécutées : témoin historique à cinq états, 2 projections, zéro erreur du garde ; famille C5 distincte, 4 536 projections, zéro erreur du garde ; contrôle de lecture simple passé. Les erreurs du projecteur ancien non gardé (2 et 276) sont historiques et ne sont pas un gain du jour.

Reproduction depuis `research/code` :
```sh
python audit_v19_disjoint_coherence.py
python audit_v19_shadow_guard.py
python audit_v19_single_read.py
```
SHA-256 du nouveau harnais : `d268a50ed70ab98038e860c4b4a63c0b9aee7f1b86db337a1608b5b0fa3f7a3c`.

Prochain test décisif : exiger un certificat explicite des composantes non observées, puis tester sa validation à coût linéaire face à une nouvelle composante distante contradictoire. Distinguer coût de construction et coût de validation. Prochain cycle alterné : provenance.
