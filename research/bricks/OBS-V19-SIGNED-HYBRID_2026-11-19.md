# V19 — quotient signé après filtre non signé

19 novembre 2026, 18 h 08 (Paris). **EXÉCUTÉ / VÉRIFIÉ ; gain conditionnel, pas de remplacement général.** Branche `work/omega-math-brick-pilot-2026-11-14`, SHA initial `437ed7f260a5c64ba3d9f8fa976a0038eecf2dad`. Suite du [cycle signé](OBS-V19-SIGNED-CORE_2026-11-19.md), après le cycle de provenance `b1f5725df2d74b1cdaeb5ca1a6a4e555b5bc6046`.

La définition source relue de l'ombre exige toujours une extension à une coloration globalement cohérente. Sources épinglées : [audit L+1](OBS-V19-LPLUS1-AUDIT_2026-11-14.md), [index historique #2](https://github.com/Abrasax63/Omega-pub/blob/2f71a6b8ed03914c0b5d308520d30e0133d9e9ad/research/bricks/INDEX_BRIQUES.md), [projecteur PR #5](https://github.com/Abrasax63/Omega-pub/blob/639dc01ca3ea58c61b075adb9a6d860bf41db7bc/research/code/audit_v19_c5_independent_2026-11-04.py) et [projecteur PR #18](https://github.com/Abrasax63/Omega-pub/blob/763d77f0aa735d90bb558b2c7fac056298d5313c/research/code/test_v19_locality_l_plus_1.py). L'écart 83/85 de l'index reste historique et sans rapport avec ce calcul.

[Protocole](../code/v19-signed-hybrid-protocol.md) fixé avant test. Question réfutable : réutiliser le quotient non signé, puis calculer les potentiels signés seulement sur les survivants, conserve-t-il le verdict exact avec un coût strictement inférieur sur deux nouvelles familles ? Référence fixe : filtre `priority`, puis cinq projections sur chaque survivant. Oracle : cinq projections sur toutes les requêtes. Contrôles : C4 pur négatif, témoin à cinq états positif, garde global sur le témoin et la famille C5.

Le candidat construit le quotient non signé une fois. Si les quatre arêtes quotientées ne forment pas un C4 simple, il rejette. Sinon il calcule les potentiels XOR forcés et le signe total du cycle, sans projection. La preuve du cycle précédent s'applique : une contradiction minimale à quatre événements est exactement un cycle simple de signe impair sous l'hypothèse F cohérent. Il s'agit d'une réutilisation de cette preuve, pas d'une nouvelle preuve bibliographique.

| Réserve nouvelle | Requêtes | Positives | Erreurs référence / candidat | Projections référence / candidat | Temps référence / candidat |
| --- | ---: | ---: | ---: | ---: | ---: |
| C6 + deux états libres | 1 526 | 0 | 0 / 0 | 0 / 0 | 6,207 / 5,508 ms |
| C4 disjoint C3 + un état libre | 217 | 8 | 0 / 0 | 200 / 0 | 29,011 / 1,044 ms |

L'oracle a exécuté 8 715 projections. Sur C6, la référence filtrait déjà tout : le candidat n'apporte aucun gain de projections, seulement un petit écart temporel ponctuel. Sur C4–C3, il supprime les 200 projections et réduit le temps mesuré de 96,4 %, sans erreur. Le critère de gain uniforme sur les deux familles est donc **RÉFUTÉ** pour les projections; un gain conditionnel est **VÉRIFIÉ** sur la seconde famille. Les temps sont une mesure ponctuelle, pas un débit stabilisé.

Le garde global rejoué conserve zéro erreur nouvelle sur 2 projections du témoin et 4 536 projections C5. Les scripts `signed_core.py`, `signed_power.py` et `audit_v19_shadow_guard.py` passent. Empreintes : candidat `3879c289c534d3e7149592e143d8e34af74b615d63d9c6d7887ffd23f84c9d9b`, résultats `5bde7ae12bf1f481cdc385385a3c19743efec986fe6c9a0695a84120f427a7f0`, garde `f78efcbfcdcbc4fbcb58fcd924a6903d10108aebdb62b9e41661663c9572c96e`.

**Décision :** conserver le candidat et ses mesures pour réutilisation, sans remplacer la référence générale ni promouvoir une brique. Statuts : calcul fini exact sur les deux réserves; preuve du critère réutilisée sous F cohérent; originalité bibliographique non examinée.

**Prochain test décisif :** pré-enregistrer une famille où le filtre laisse un taux intermédiaire de survivants, puis répéter les chronométrages pour estimer le seuil de rentabilité entre quotient seul et potentiels signés.

```sh
PYTHONPATH=<dépendances-épinglées> timeout 30 python signed_hybrid.py
timeout 30 python signed_core.py
timeout 30 python signed_power.py
timeout 30 python audit_v19_shadow_guard.py
```
