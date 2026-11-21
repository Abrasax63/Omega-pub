# V19 — classes d'information d'une observation partielle (18 novembre 2026)

**Statut : CALCUL EXACT FINI, pas un théorème universel.** Expérience autonome en lecture seule, construite à partir du témoin et de la définition d'ombre de la PR #82. Aucun changement de solveur actif, aucun appel à une API, aucune modification de `main`.

## Question / proposition falsifiable

Soit `O` une observation partielle (cycle distingué et préfixes étiquetés) et `C(O)` l'ensemble **complet** de ses endofonctions sur un ensemble d'états fixé, dont les contraintes forcées sont cohérentes. Notons `S(T)` l'ensemble des colorations binaires du cycle extensibles à une coloration globale respectant les contraintes forcées et événementielles.

Une observation supplémentaire `O'` **détermine** l'ombre exactement lorsque

`{ S(T) : T dans C(O') } est un singleton non vide.`

Une **ambiguïté vérifiée** consiste en deux endofonctions `T,U` compatibles avec la même observation `O'` mais telles que `S(T) != S(U)`.

Le présent audit calcule toutes ces classes d'observations pour trois familles finies. Il fait varier **simultanément** toutes les transitions initialement inconnues. Aucun accès caché à l'endofonction de référence n'intervient dans la décision ; l'accès aux fonctions complètes ne sert qu'à construire les classes et les témoins du certificat hors ligne.

## Sémantique et portée

Sur un ensemble fini étiqueté `X`, la fonction `T:X->X` est totale. Pour deux états distincts `u,v`, on impose `c(u) XOR c(v)=1` si `T(u)=T(v)` (fusion) ou si `{T(u),T(v)}={u,v}` (invariance). Les contraintes forcées doivent admettre une coloration globale. Aux temps `t=0,...,L-1`, les deux trajectoires observées imposent `c(T^t(x)) XOR c(T^t(y))=0`.

L'ombre est la projection **globale** : les masques sur le cycle qui s'étendent à une coloration de **tous** les états satisfaisant contraintes forcées + égalités d'événement. Le projecteur ancré ancien, dont la sémantique était différente, n'est pas utilisé.

Sources : [définition et correction du projecteur](OBS-V19-LPLUS1-AUDIT_2026-11-14.md), [ambiguïté d'une lecture](OBS-V19-ONE-READ-COMPLETIONS_2026-11-18.md), [recherche hors terminaux du 18 novembre](OBS-V19-OUTSIDE-TERMINAL_2026-11-18.md).

## Résultats exacts du nouveau balayage

| Famille | Transitions inconnues | Complétions brutes | Cohérentes retenues | Ombres comparées par deux solveurs |
| --- | --- | ---: | ---: | ---: |
| C3, 10 états, préfixes (7,5,3) / (8,6,4), sommet 9 non lu | 3,4,9 | 1 000 | 800 | 800 |
| C3, 9 états, mêmes préfixes | 3,4 | 81 | 74 | 74 |
| C4, 10 états, préfixes (8,6,4) / (9,7,5) | 4,5 | 100 | 92 | 92 |
| **Total** | | **1 181** | **966** | **966** |

**Zéro désaccord** entre un solveur union-find à parité et une énumération indépendante des `2^n` colorations binaires pour chaque complétion cohérente. Les deux solveurs partagent toutefois la **même définition** des contraintes forcées et événementielles ; ce n'est pas une validation indépendante des axiomes.

Dans le cas principal (C3, 10 états), sur les 800 complétions cohérentes : **785** ombres pleines (8 masques) et **15** ombres vides.

### Information nécessaire et suffisante dans le cas principal

| Transitions nouvellement observées | Classes d'observations admissibles | Classes déterminantes | Classes ambiguës | Complétions cohérentes déjà décidables |
| --- | ---: | ---: | ---: | ---: |
| Aucune | 1 | 0 | 1 | 0 / 800 |
| `T(3)` | 10 | 8 | 2 | 651 / 800 |
| `T(4)` | 10 | 8 | 2 | 651 / 800 |
| `T(9)` | 10 | 2 | 8 | 150 / 800 |
| `T(3),T(4)` | 93 | 93 | 0 | 800 / 800 |

Les valeurs `T(3)=3` et `T(3)=4` restent ambiguës, avec respectivement 74 et 75 complétions cohérentes. Les huit autres valeurs déterminent toutes l'ombre pleine malgré les deux autres transitions inconnues. Les résultats sont symétriques pour `T(4)`.

**Témoin négatif constructif.** Les deux complétions ci-dessous partagent le cycle C3, les préfixes et l'observation supplémentaire `T(3)=3`, mais pas l'ombre :

- `T=(1,2,0,3,0,3,4,5,6,1)` : ombre pleine, 8 masques.
- `U=(1,2,0,3,4,3,4,5,6,0)` : ombre vide, 0 masque.

Toutes les arêtes forcées de chacun des deux systèmes sont cohérentes ; c'est l'ajout des égalités événementielles qui vide l'ombre de `U`. Les deux transitions inconnues `T(4)` et `T(9)` varient simultanément. Une lecture n'est donc **pas** toujours suffisante.

**Observation forte mais bornée.** Pour cette famille précise, l'observation conjointe des deux terminaux `T(3),T(4)` détermine toujours l'ombre : les 93 classes d'observations cohérentes sont univoques malgré `T(9)` inconnu. Cela n'autorise **aucun** énoncé universel pour les autres cycles, préfixes, horizons et tailles.

## Information et coût : bornes, pas promesse de gain en production

Une politique diagnostique hors ligne lit d'abord `T(3)`, puis `T(4)` uniquement si `T(3)` vaut 3 ou 4. Sur les **800 complétions cohérentes considérées à poids égal**, cela représente 651 cas à une lecture et 149 cas à deux lectures : `949` acquisitions au total contre `1 600` avec deux lectures systématiques, soit `40,6875 %` de lectures en moins **dans cette hypothèse de pondération**. Ce n'est ni une mesure de temps réel, ni un gain généralisable ; les calculs hors ligne pour certifier la politique ne sont pas inclus dans le coût d'acquisition.

Le calcul sur une sous-famille peut donner une décision sûre **uniquement** si cette sous-famille contient réellement toutes les complétions admissibles du système étudié. Si la taille de l'univers, les contraintes ou le domaine des transitions possibles sont inconnus, une telle garantie n'est pas acquise.

## Lemme général élémentaire (aucune revendication de nouveauté)

Si une observation `O1` contient toute l'information de `O0`, alors `C(O1) ⊆ C(O0)`. Ainsi, si l'ombre est constante sur `C(O0)`, elle l'est aussi sur tout sous-ensemble non vide `C(O1)`. En revanche, l'absence de contre-exemple dans **un échantillon** ne démontre jamais cette constance. C'est le principe de monotonie de la détermination, valable pour n'importe quelle propriété, pas seulement V19.

## Exécution / certificat rejouable

```sh
cd research/code
python3 audit_v19_information_classes.py
python3 audit_v19_information_classes.py /tmp/v19_information_certificate.json
python3 -m py_compile audit_v19_information_classes.py
```

Le programme effectue une énumération exhaustive de chaque complétion cohérente et vérifie pour chacune l'égalité des deux projecteurs. Il construit ensuite toutes les partitions par ensemble de transitions observées et émet un JSON comprenant les comptes par classe, les observations déterminantes et des paires de témoins pour les classes ambiguës. Les assertions intégrées bloquent tout changement des valeurs cardinales attendues. Il n'y a pas de dépendance externe.

**Exécuté et vérifié localement :** 966 comparaisons indépendantes sans écart, trois familles, assertions et compilation Python réussies. **CI GitHub non encore vérifiée ; aucune exécution CI revendiquée.**

SHA-256 du fichier Python exécuté localement : `5b2a7a420ddf9766a7ec0bb0c48941663b5fea5806df9f1acc5fbf11111a1ad8`.

## Limites et prochain test décisif

- Pas de preuve générale qu'une image « hors terminaux » suffit ; le cas principal est une observation unique, fixée avant l'énumération.
- Résolution exacte par deux algorithmes, mais formalisation commune : ni revue indépendante des définitions, ni preuve Lean.
- Le sous-ensemble des endofonctions cohérentes est connu à l'oracle hors ligne ; impossible de conclure en production sans hypothèses contrôlées.
- **Prochain test proposé :** geler une famille d'observations aux préfixes distincts, faire varier *toutes* les transitions inconnues sans modèle de référence complet consulté par le décideur, rechercher d'abord un contre-exemple à la règle « sortie hors terminaux », puis évaluer une politique de lectures adaptatives et ses coûts sur un holdout. Garder tout résultat en quarantaine jusqu'à vérification.

**Statut scientifique : CALCUL EXACT FINI pour ces trois familles ; UNIVERSALITÉ INDÉTERMINÉE ; GAIN OPÉRATIONNEL NON MESURÉ.**
