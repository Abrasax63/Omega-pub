# V19 — réutiliser le quotient forcé sur plusieurs événements

19 novembre 2026, vers 08 h 07 (Paris). **IMPLÉMENTÉ / EXÉCUTÉ — calcul fini exact ; gain de coût non établi.** Branche `work/omega-math-brick-pilot-2026-11-14`, départ [bceeb0c7d94f8b8956f067a9158e3101e8a0014d](https://github.com/Abrasax63/Omega-pub/commit/bceeb0c7d94f8b8956f067a9158e3101e8a0014d). Dernier [cycle mathématique](OBS-V19-COLOR-CERTIFICATE-COST_2026-11-19.md), dernière [provenance](https://github.com/Abrasax63/Omega-pub/commit/483f550413b6a64c90d344886d2bacfe01513040).

Définition revérifiée avant test : projection des colorations globalement extensibles. Les composantes non observées doivent rester cohérentes. Sources relues et épinglées : [fiche audit](OBS-V19-LPLUS1-AUDIT_2026-11-14.md), [index #2](https://github.com/Abrasax63/Omega-pub/blob/2f71a6b8ed03914c0b5d308520d30e0133d9e9ad/research/bricks/INDEX_BRIQUES.md), [projecteur #5](https://github.com/Abrasax63/Omega-pub/blob/639dc01ca3ea58c61b075adb9a6d860bf41db7bc/research/code/audit_v19_c5_independent_2026-11-04.py), [convention #18](https://github.com/Abrasax63/Omega-pub/blob/763d77f0aa735d90bb558b2c7fac056298d5313c/02_MATHEMATIQUES/v19_c5/TEST_OPTIMALITE_LOCALITE_L_PLUS_1_2026-11-10.md).

Question unique : amortir un quotient signé de toutes les contraintes forcées sur plusieurs événements réduit-il le coût complet sans perdre l'exactitude ? [Critères fixés avant test](../code/v19-cached-quotient-prereg-2026-11-19.md). Référence fixe `guarded_shadow` ; oracle indépendant `exhaustive_shadow`. Développement : C4 et3états distants,27applications ; réserve nouvelle pour ce protocole de requêtes multiples : C5 et4états distants,256applications. Toutes les paires de l'espace, horizons2et3. Les états distants restent dans leur sous-espace ; cette campagne ne couvre pas les composantes forcées reliant des états du cycle entre eux.

Prototype : clé = tuple immuable de toutes les transitions T, quotient signé construit sur toutes les composantes forcées, puis contrôle de cohérence globale du quotient des égalités événementielles et projection du cycle. La construction, la comparaison de la clé et toutes les requêtes sont incluses dans les mesures candidat. Les contraintes forcées données à la référence sont préparées une fois par système ; le candidat inclut sa propre reconstruction lors du remplissage du cache. Ce choix ne favorise pas son coût.

Négatifs exécutés avant balayage : fibre triple distante incohérente ; mutation en place de T rendant la dynamique cohérente (reconstruction du cache,2constructions observées) ; contraintes événementielles contradictoires. Tous passent. Le cache n'est pas réutilisé après modification de T.

| Jeu | Systèmes | Projections | Ombres vides | Divergences candidat/référence/exhaustif | Constructions du cache par reprise |
| --- | ---: | ---: | ---: | ---: | ---: |
| Développement | 27 | 1 134 | 294 | 0 | 27 |
| Réserve | 256 | 18 432 | 6 396 | 0 | 256 |

Critère de conservation : zéro divergence, invalidation correcte et coût inférieur dans les trois reprises réservées. Budget inférieur à60s par campagne, mêmes cas et nombre de requêtes, référence exécutée avant candidat à chaque reprise.

Temps réservés référence/candidat(s) :0,456872/0,479848 ;0,474319/0,485460 ;0,462781/0,490350. Le candidat est plus lent sur les trois reprises, malgré l'amortissement. Développement :0,013815/0,015680 ;0,016316/0,019306 ;0,014942/0,015557. Aucun gain d'efficacité revendiqué.

Décision : candidat non retenu comme correction active ; référence inchangée. Source évaluée conservée pour réutilisation. Résultat négatif nouveau sur le coût du cache, non une régression de la référence. Validité constatée seulement sur cette campagne finie ; pas de preuve universelle de suffisance L+1. Originalité bibliographique non évaluée.

Non-régressions : garde historique contre projecteur exhaustif,2projections du témoin cinq états et4536projections de la famille C5 distincte, zéro erreur du garde. Les erreurs du projecteur ancien non gardé sont historiques, pas un gain du jour.

Depuis `research/code` :
```sh
python audit_v19_cached_quotient.py
python audit_v19_shadow_guard.py
```
Harnais SHA-256 `bf06df64e577cd7a7ba35e83271f00cd2688a55283d9cc08770893dded49cd77`. [Résultats](v19-cached-quotient-results-2026-11-19.jsonl), SHA-256 `70b261aa26d49c350cd91226c6ec19628de5a3d51433f631ca7b40343b524035`.

Prochain test décisif : changer de famille et éprouver les relations de parité lorsqu'une composante forcée touche plusieurs états du cycle, avec un événement contradictoire et le projecteur exhaustif. Priorité à la couverture logique avant toute nouvelle optimisation de coût. Prochain cycle alterné : provenance.
