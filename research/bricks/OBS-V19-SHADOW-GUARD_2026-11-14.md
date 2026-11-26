# V19 — garde de cohérence du projecteur d’ombre

Cycle mathématique du 14 novembre 2026. Base `fce31065bb1a06ad1cbf483128542019fb7611da`. Sources épinglées : [fiche précédente](https://github.com/Abrasax63/Omega-pub/blob/fce31065bb1a06ad1cbf483128542019fb7611da/research/bricks/OBS-V19-LPLUS1-AUDIT_2026-11-14.md), [index historique #2](https://github.com/Abrasax63/Omega-pub/blob/2f71a6b8ed03914c0b5d308520d30e0133d9e9ad/research/bricks/INDEX_BRIQUES.md), [audit source #5](https://github.com/Abrasax63/Omega-pub/blob/639dc01ca3ea58c61b075adb9a6d860bf41db7bc/02_MATHEMATIQUES/defauts_recollement/AUDIT_INDEPENDANT_LOCALITE_V19_L_PLUS_2_2026-11-05.md), [test #18](https://github.com/Abrasax63/Omega-pub/blob/763d77f0aa735d90bb558b2c7fac056298d5313c/research/code/test_v19_locality_l_plus_1.py). L’index sert à repérer les briques, avec l’écart historique 83/85 toujours signalé. La note primaire V19(2), §4, donne le cadre de localité. L’audit #5 définit explicitement l’ombre comme les colorations de B qui s’étendent à X en satisfaisant toutes les contraintes forcées et événementielles.

## Raccord démontré

Pour un graphe fini de contraintes binaires c(u) XOR c(v) = p, avec p dans {0,1}, le projecteur ancré contrôle les composantes touchant B. Un échec du garde global rend l’ombre vide. Si le garde réussit, toute coloration acceptée par le projecteur satisfait toutes les arêtes des composantes touchant B après propagation. Sur chaque autre composante, prendre la restriction d’une solution du graphe entier, dont l’existence est garantie par le garde. Les composantes sont disjointes, donc assembler ces colorations donne une extension globale. Réciproquement une extension globale fournit un masque accepté. Le garde est appliqué séparément à l’ensemble complet et à l’ensemble restreint.

## Calcul exact et coût

Témoin fixé à cinq états : les contraintes sur la paire (0,1) exigent les parités 1 et 0. Les deux projections, complète et locale, doivent être vides. L’ancien projecteur retourne les huit masques du C3. Le garde retrouve l’ensemble vide dans les deux cas.

Famille réservée distincte : C5 et C2 disjoints, deux feuilles fixées vers deux sommets périodiques différents, 21 applications, toutes les 36 paires et L=2,3,4. Les 2 268 cas donnent chacun deux projections. Famille générée indépendamment du témoin, sans réglage du garde. La référence énumère les 512 colorations des neuf états à chaque projection.

| Lot | Projections | Écarts avant | Écarts avec garde | Écarts global/local exacts |
| --- | ---: | ---: | ---: | ---: |
| Témoin | 2 | 2 | 0 | 0 |
| Famille réservée | 4 536 | 276 | 0 | 0 |

Sur la famille réservée, 456 projections exactes sont vides. Temps cumulés observés des projecteurs, en un passage : 0,134 s ancien, 0,128 s avec garde, 0,963 s exhaustif. Mesure indicative, sans revendication de gain de vitesse. Le garde coûte O(n+m) pour n sommets et m arêtes.

Commandes depuis `research/code` :

```sh
python3 test_v19_locality_l_plus_1.py
python3 audit_v19_full_coloring_projection.py
python3 audit_v19_shadow_guard.py
```

Les deux scripts existants ont terminé : 325 468 comparaisons chacun. L’audit exhaustif confirme 9 520 divergences avec le projecteur historique dans chaque vue et zéro divergence exacte entre les vues. SHA-256 du candidat : `20285dde0486fbdd23404de18c276cec728a32020558d8de9536757dd4cb70fa`.

Le garde est retenu dans le pilote. La preuve porte sur la correction du projecteur pour le contrat d’extension, et le calcul borné ne tranche pas la localité universelle de L+1. L’originalité bibliographique n’a pas été évaluée. Prochain test mathématique : chercher une contradiction de parité qui disparaît dans le préfixe L+1, sur des familles hors de la campagne précédente et avec le projecteur exact comme oracle.
