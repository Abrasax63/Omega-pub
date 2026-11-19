# V19 — obstruction minimale à quatre égalités orbitales

19 novembre 2026, 13 h 49 (Paris). **EXÉCUTÉ / VÉRIFIÉ**, calcul fini et preuve du témoin. Branche `work/omega-math-brick-pilot-2026-11-14`, départ `588a8762ef0a12d26cf47636b379a5c862c2bdd3`. Suite du [noyau à trois égalités](OBS-V19-THREE-EVENT-CORE_2026-11-19.md), après le cycle de provenance `6c4111b7f985ec0ffb47a6d2ac7058f21feb97ab`.

L'ombre est la projection des colorations qui s'étendent à toutes les contraintes du système. Audit [L+1](OBS-V19-LPLUS1-AUDIT_2026-11-14.md) relu, [index #2](https://github.com/Abrasax63/Omega-pub/blob/2f71a6b8ed03914c0b5d308520d30e0133d9e9ad/research/bricks/INDEX_BRIQUES.md), [définition #5](https://github.com/Abrasax63/Omega-pub/blob/639dc01ca3ea58c61b075adb9a6d860bf41db7bc/02_MATHEMATIQUES/defauts_recollement/sources/V19/NOTE_RECHERCHE_V19_GRAMMAIRE_ORBITALE_2.md), [projecteur #5](https://github.com/Abrasax63/Omega-pub/blob/639dc01ca3ea58c61b075adb9a6d860bf41db7bc/research/code/audit_v19_c5_independent_2026-11-04.py) et [convention #18](https://github.com/Abrasax63/Omega-pub/blob/763d77f0aa735d90bb558b2c7fac056298d5313c/02_MATHEMATIQUES/v19_c5/TEST_OPTIMALITE_LOCALITE_L_PLUS_1_2026-11-10.md) épinglés. La comparaison du garde et du projecteur exhaustif porte sur cette extension globale.

Question [préenregistrée](../code/v19-four-event-protocol.md) : en horizon 4 sur un C4 avec trois états supplémentaires, des contraintes forcées cohérentes peuvent-elles devenir incohérentes avec quatre égalités d'événement, mais rester cohérentes après suppression de chacune ? Témoin négatif passé : C4 pur, paire (0,1), ombre non vide.

**Certificat exact.** Pour T=(1,2,3,0,0,1,2) et la paire (0,4), les quatre égalités sont c0=c4, c1=c0, c2=c1, c3=c2. Elles imposent c3=c4, alors que F exige c3 XOR c4=1, c0 XOR c5=1 et c1 XOR c6=1. Les égalités forment le chemin 4–0–1–2–3. En retirer une sépare 4 et 3. On peut colorer les deux composantes avec des valeurs opposées, puis fixer c5 et c6. Le projecteur exhaustif donne 0 coloration du cycle pour le système entier et 2 après chacune des quatre suppressions. Par monotonie, tout sous-ensemble propre est cohérent. Ceci prouve la minimalité par inclusion pour ce T et cette paire.

343 transformations dans le balayage réservé, dont 80 écartées pour incohérence de F. Sur 5 523 requêtes, 4 869 comportent quatre arêtes. Le projecteur et le garde donnent exactement les mêmes ombres pour les 24 999 comparaisons, dont toutes les suppressions. 792 requêtes forment un noyau à quatre arêtes par le critère fixé. Temps cumulés par méthode : 1,537 s exhaustif et 0,380 s garde. Cette mesure concerne le garde existant. Le rejeu séparé du témoin à cinq états (2 projections) et de la famille C5 (4 536) donne zéro désaccord entre garde et exhaustif. [Mesures](../code/v19-four-event-results.json) et [rejeu](../code/v19-four-event-guard.txt).

```sh
cd research/code
timeout 30 python audit_v19_four_event_core.py
timeout 30 python audit_v19_shadow_guard.py
```

Harnais SHA-256 `e2e70f2fba59b2b68698bca64de91659406238c9747c6287e61ee6deb270bbdd`. Résultats `ef8fecb5e4103cb6f7126f7b65cf8b0014a26075792e70f7ff0c2628261fa13a`. Référence et vérificateur conservés. Cette preuve du témoin ne règle ni la minimalité du nombre d'états ni la suffisance générale de L+1. Originalité bibliographique non examinée.

Prochain essai mathématique : déterminer le nombre d'états minimal du témoin à quatre égalités avec cycle distingué de longueur au moins trois, par balayage des tailles 4 à 6 puis preuve si la structure le permet. Prochain cycle alterné : provenance.
