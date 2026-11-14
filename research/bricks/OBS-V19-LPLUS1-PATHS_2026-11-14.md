# V19 — visibilité des chemins forcés au temps L+1

Cycle mathématique du 14 novembre 2026. Base `462643d3ef446680ae15a566839ca931111735e4`. Sources épinglées : [fiche d’audit](https://github.com/Abrasax63/Omega-pub/blob/462643d3ef446680ae15a566839ca931111735e4/research/bricks/OBS-V19-LPLUS1-AUDIT_2026-11-14.md), [index historique #2](https://github.com/Abrasax63/Omega-pub/blob/2f71a6b8ed03914c0b5d308520d30e0133d9e9ad/research/bricks/INDEX_BRIQUES.md), [définition et structure #5](https://github.com/Abrasax63/Omega-pub/blob/639dc01ca3ea58c61b075adb9a6d860bf41db7bc/02_MATHEMATIQUES/defauts_recollement/AUDIT_INDEPENDANT_LOCALITE_V19_L_PLUS_2_2026-11-05.md), [campagne #18](https://github.com/Abrasax63/Omega-pub/blob/763d77f0aa735d90bb558b2c7fac056298d5313c/research/code/test_v19_locality_l_plus_1.py). L’ombre est la projection des solutions globales de F et E sur B.

## Argument de preuve soumis à revue

Hypothèses : endofonction finie, couleurs binaires, L ≥ 2, cycle B de longueur ≥ 3, cohérence du graphe forcé F. Les arêtes de F représentent la fusion ou l’invariance d’une paire. On utilise la structure de #5 : chaque composante est un chemin, avec au plus une arête centrale d’invariance et au plus une feuille de fusion de chaque côté. Sans arête d’invariance, la composante est un singleton ou une arête de fusion.

Appelons ancrages les sommets de B et les états aux temps 0 à L−1 des deux trajectoires. Pour chaque paire d’ancrages d’une même composante de F, le chemin forcé minimal entre eux est visible au temps L+1 :

- Une arête de fusion seule a ses deux extrémités déjà ancrées si elle relie deux ancrages.
- Une feuille de fusion d’une composante à noyau invariant est transitoire et n’est donc jamais un sommet de B. Si elle est un ancrage, son partenaire dans le noyau est visible en au plus deux pas : pour un noyau fixe elle atteint directement son partenaire fixe, et pour un 2-cycle elle atteint d’abord l’autre sommet puis son partenaire. Une extrémité du noyau qui est elle-même un ancrage est déjà visible.
- Le chemin minimal ne contient comme sommets internes que des sommets du noyau. Un sommet du noyau interne sur le chemin est soit lui-même ancré, soit du côté d’une feuille ancrée, donc couvert par les cas précédents.

Ainsi toutes les relations de parité de F entre ancrages sont conservées. Réciproquement, la restriction de F ne peut en ajouter. De manière constructive, une coloration des ancrages compatible avec ces relations s’étend à chaque composante de F : choisir une racine ancrée lorsqu’il en existe une et propager, en choisissant librement la couleur de la racine ailleurs. Les égalités E ne touchent que les ancrages et sont présentes dans les deux graphes. Les deux ensembles de colorations des ancrages, et donc leurs projections sur B, coïncident, y compris si E rend le système incohérent. Ce raisonnement déduit la suffisance de L+1 des hypothèses ci-dessus. Il ne tranche pas sa minimalité. Originalité bibliographique non évaluée.

## Calcul exact indépendant sur la famille choisie

Vingt systèmes à neuf états : C3 distingué, noyau distinct C2 ou deux points fixes, deux queues de longueur deux à destinations périodiques distinctes. Toutes les paires et L=2,3,4,5 : 2 880 comparaisons exactes global/local, 1 264 ombres vides, zéro écart. Le garde coïncide avec l’oracle sur les 5 760 projections. Coût total local du harnais avec oracle : 1,856 s en un passage. Aucun changement du vérificateur. Famille distincte des pilotes précédents et choisie pour solliciter les chemins du noyau.

Depuis `research/code` :

```sh
python3 audit_v19_lplus1_paths.py
python3 audit_v19_shadow_guard.py
python3 test_v19_locality_l_plus_1.py
```

Les deux contrôles historiques passent : garde sans erreur sur le témoin et les 4 536 projections réservées, et campagne historique #18 terminée sur 325 468 comparaisons. SHA-256 du harnais : `992d6a2b47398b08493a9a95e402fc7b5d32b0a709fefb4d616e23c886245a5b`.

Prochain test mathématique : rechercher une paire dont l’ombre varie quand on tronque au temps L, et distinguer alors optimalité et simple suffisance. Prochain cycle de l’alternance : provenance.
