# V19 — noyau contradictoire de trois égalités événementielles

19 novembre 2026, vers 11 h 31 (Paris). **EXÉCUTÉ — calcul exact et certificat fini vérifiable.** Branche `work/omega-math-brick-pilot-2026-11-14`, départ [c804fde07ddcc6d659d140054ad981279fea1abc](https://github.com/Abrasax63/Omega-pub/commit/c804fde07ddcc6d659d140054ad981279fea1abc). Dernier [cycle mathématique](OBS-V19-FORCED-FIBRES_2026-11-19.md), dernière [provenance](https://github.com/Abrasax63/Omega-pub/commit/ec6edc92bf8b6f062f852601894c27f48d261b8a).

Définition source relue avant test : ombre = projection des colorations extensibles à toutes les contraintes. Sources épinglées : [audit](OBS-V19-LPLUS1-AUDIT_2026-11-14.md), [index #2](https://github.com/Abrasax63/Omega-pub/blob/2f71a6b8ed03914c0b5d308520d30e0133d9e9ad/research/bricks/INDEX_BRIQUES.md), [projecteur #5](https://github.com/Abrasax63/Omega-pub/blob/639dc01ca3ea58c61b075adb9a6d860bf41db7bc/research/code/audit_v19_c5_independent_2026-11-04.py), [convention #18](https://github.com/Abrasax63/Omega-pub/blob/763d77f0aa735d90bb558b2c7fac056298d5313c/02_MATHEMATIQUES/v19_c5/TEST_OPTIMALITE_LOCALITE_L_PLUS_1_2026-11-10.md). L'index comporte déjà des travaux sur les obstructions collectives ; aucune nouveauté bibliographique n'est revendiquée ici.

Question [préenregistrée](../code/v19-three-event-prereg-2026-11-19.md) : trois égalités orbitales peuvent-elles être collectivement incohérentes, alors que chaque paire reste cohérente avec F ? Référence fixe : garde global ; oracle : toutes les colorations binaires. Budget inférieur à30s. Contrôle négatif exécuté d'abord : C4pur,paire(0,1),L3, ombre non vide.

Témoin T=(1,2,0,1), cycle(0,1,2), paire(3,1), horizon3. F contient uniquement c0 XOR c3=1. Les trois égalités événementielles sont c3=c1, c1=c2, c2=c0. Après quotient par F, elles imposent :

- c0 XOR c1=1 ;
- c1 XOR c2=0 ;
- c2 XOR c0=0.

Le XOR des trois relations donne0=1. Toutes ensemble, l'ombre est vide. Retirer n'importe laquelle donne une ombre de taille2, confirmé par le projecteur exhaustif. C'est un noyau minimal par inclusion relativement aux trois égalités, F restant fixé. Le témoin a quatre états ; avec trois états et un cycle distingué de longueur≥3, l'application est un C3pur, F est vide et les égalités seules sont satisfiables par la coloration constante. Quatre états sont donc minimaux sous ces hypothèses précises. Cela ne classe pas tous les noyaux ni tous les horizons.

Campagne réservée : cycleC3fixé et trois états libres,216applications, toutes destinations dans l'espace, toutes15paires,horizon3. Les52applications dont F est incohérent sont écartées conformément au protocole. Sur les164restantes :

| Mesure | Résultat |
| --- | ---: |
| Projections comparées | 2 460 |
| Noyaux à3égalités minimaux par suppression | 414 |
| Désaccords garde/exhaustif | 0 |
| Temps garde/exhaustif(s) | 0,017283 / 0,076692 |

Le premier certificat réservé est conservé dans les résultats. La campagne cherche une propriété nouvelle pour ce protocole (les suppressions d'égalités), sans présenter les applications déjà énumérables dans les audits antérieurs comme un nouveau corpus indépendant. Les414cas ne sont pas414découvertes distinctes.

Décision : référence inchangée, aucun changement de vérificateur ni gain de coût nouveau. Le certificat fini et sa démonstration XOR sont vérifiables ; aucune validation bibliographique ou revue externe, aucune promotion canonique. Ce résultat n'établit pas la suffisance universelle de L+1.

Non-régressions :2projections du témoin cinq états et4536projections de la famille C5distincte, zéro erreur du garde face au projecteur exhaustif.

Depuis `research/code` :
```sh
python audit_v19_three_event_core.py
python audit_v19_shadow_guard.py
```
Harnais SHA-256 `b4255c664b2a4d31e13cf9b90e711898c2c3e1439a06bf2e82980d088c7388de`. [Résultats](../code/v19-three-event-results-2026-11-19.jsonl), SHA-256 `86ddc82ebefd231678dd590bea52bdb173e7e945b0670477958ded996d1fbea3`.

Prochain test décisif : rechercher un noyau minimal à quatre égalités qui ne contienne aucun noyau contradictoire à trois, sur une famille C4et feuilles déclarée avant le balayage. Comparer toutes les suppressions au projecteur exhaustif. Prochain cycle alterné : provenance.
