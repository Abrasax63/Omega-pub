# V19 — distinguer les fibres forcées des composantes événementielles

19 novembre 2026, vers 10 h 24 (Paris). **EXÉCUTÉ — calcul fini exact ; preuve élémentaire proposée ci-dessous.** Branche `work/omega-math-brick-pilot-2026-11-14`, départ [fd940554fabbc026b63fa5e8649fe9ab0f1fcde7](https://github.com/Abrasax63/Omega-pub/commit/fd940554fabbc026b63fa5e8649fe9ab0f1fcde7). Dernier [cycle mathématique](OBS-V19-CACHED-QUOTIENT-COST_2026-11-19.md), dernière [provenance](https://github.com/Abrasax63/Omega-pub/commit/7373a96bee006ee06be75d05c0a52ab062dfe644).

Définition relue avant test : ombre = projection des colorations globalement extensibles. Sources épinglées : [fiche audit](OBS-V19-LPLUS1-AUDIT_2026-11-14.md), [index #2](https://github.com/Abrasax63/Omega-pub/blob/2f71a6b8ed03914c0b5d308520d30e0133d9e9ad/research/bricks/INDEX_BRIQUES.md), [projecteur #5](https://github.com/Abrasax63/Omega-pub/blob/639dc01ca3ea58c61b075adb9a6d860bf41db7bc/research/code/audit_v19_c5_independent_2026-11-04.py), [convention et définitionF #18](https://github.com/Abrasax63/Omega-pub/blob/763d77f0aa735d90bb558b2c7fac056298d5313c/02_MATHEMATIQUES/v19_c5/TEST_OPTIMALITE_LOCALITE_L_PLUS_1_2026-11-10.md).

Question [préenregistrée](../code/v19-forced-fibres-prereg-2026-11-19.md) : une composante des contraintes forcées F peut-elle rencontrer plusieurs sommets d'un même cycle de longueur au moins3 ? Le prochain essai proposé au cycle précédent confondait ce cas avec une connexion créée après ajout des égalités événementielles. Les deux graphes doivent être distingués.

Hypothèse réfutable : toute composante de F rencontre le cycle en au plus un sommet. Développement : cycleC3+2états libres, toutes25applications ; réserve distincte : cycleC4+3états libres, toutes343applications. Les états libres peuvent viser tout l'espace, contrairement à la famille disjointe précédente. Contrôle négatif artificiel : une arête entre deux sommets du cycle est bien détectée. Contrôle événementiel réel : C4pur, paire(0,1),horizon2 ; les égalités relient trois sommets du cycle. Budget inférieur à60s, aucun appel externe.

| Famille | Systèmes | Maximum de sommets du cycle dans une composanteF | Erreurs de l'identité par fibre | Projections globales | Divergences garde/cache/exhaustif |
| --- | ---: | ---: | ---: | ---: | ---: |
| C3+2 développement | 25 | 1 | 0 | 500 | 0 |
| C4+3 réserve | 343 | 1 | 0 | 14 406 | 0 |

Toutes les paires et horizons2et3 sont projetés. Ombres vides :176en développement,5154en réserve. Le cache historique est inchangé et reste expérimental. Temps d'un lot référence/cache :0,003183/0,003572s puis0,219009/0,218360s. Une seule mesure, aucun gain d'efficacité revendiqué, aucune nouvelle correction retenue.

## Preuve proposée de l'identité de la composante

Hypothèses : T est une application d'un ensemble fini dans lui-même ; C est un cycle de longueur q≥3. Les arêtes forcées entre sommets distincts u,v sont définies par T(u)=T(v) ou {T(u),T(v)}={u,v}. Pour b dans C, posons p=T(b) et A=T⁻¹({p}).

1. A est une clique d'arêtes de fusion, donc appartient à la composante de b. Une arête de fusion ne peut sortir de A, puisque tous ses sommets ont la même image p.
2. Aucun sommet w de A n'est égal à p : p appartient à un cycle de longueur≥3 et n'est donc pas fixe.
3. Si une arête d'invariance joignait w dans A à z, alors {p,T(z)}={w,z}. Puisque p≠w, il faudrait z=p et T(p)=w. Avec T(w)=p, cela placerait p dans un cycle de longueur2, contradiction.
4. Aucune arête forcée ne sort donc de A. La composante de b est exactement A. La restriction de T au cycle est injective : seul b, parmi les sommets de C, a pour image p. Cette composante rencontre C en exactement un sommet.

Cette déduction n'exige pas la cohérence binaire de F : une fibre de taille3 peut former un triangle incohérent tout en ne rencontrant C qu'une fois. Pour q=2, l'énoncé échoue : T=(1,0) crée une arête d'invariance entre les deux sommets. Ce contrôle a aussi été exécuté. Les égalités événementielles peuvent ensuite joindre plusieurs de ces fibres ; le lemme ne porte pas sur F+E.

Statuts : égalités et projections de la campagne = **CALCUL FINI EXACT** ; argument général ci-dessus = **PREUVE PROPOSÉE, vérifiable, sans revue externe** ; originalité bibliographique **NON ÉVALUÉE**. Aucune promotion canonique, aucune conclusion universelle sur L+1. La correction concerne la formulation du prochain test.

Non-régressions :2projections du témoin cinq états et4536projections de la famille C5 distincte, zéro erreur du garde contre le projecteur exhaustif. Les erreurs historiques du projecteur non gardé ne sont pas un gain du jour.

Depuis `research/code` :
```sh
python audit_v19_forced_fibres.py
python audit_v19_shadow_guard.py
python -c 'from test_v19_locality_l_plus_1 import forced_edges; assert forced_edges((1,0)) == ((0,1,1),)'
```
[Harnais](../code/audit_v19_forced_fibres.py) SHA-256 `a3696349dd8e93e8e57002fb98382dddf7104a8d538de0b380b4e61eeb3c97f0`. [Résultats](../code/v19-forced-fibres-results-2026-11-19.jsonl), SHA-256 `7f32a482549cbe902cac5d7e9e8285676f88d332cd11c6b70fb3aa59a07ab4f7`.

Prochain test décisif : faire varier uniquement les égalités événementielles sur le quotient des fibres et chercher une obstruction de parité reliant trois fibres, avec témoin contradictoire minimal et projecteur exhaustif. Ne pas chercher deux sommets du cycle dans une seule composante de F sous q≥3. Prochain cycle alterné : provenance.
