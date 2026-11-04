# OBS-V19-C5-CAPACITY — Spectre exact des capacités géométriques orientées

**Type :** brique d’application / capacité dynamique  
**ID scientifique :** `OBS-V19-C5-CAPACITY` v2  
**Statut :** DÉMONTRÉ (certification interne RAVI-2)  
**Originalité :** INDÉTERMINÉE  
**Dépendances :** `BR-OBS-CAP-01`, `OBS-V19-C5-ORIENTED14`, `OBS-V19-FORCED-P4`.

## Domaine

Cycle orienté `C5` avec `T(c_i)=c_{i+1}`, observation binaire, horizon `L=3`, contraintes forcées cohérentes. Une occurrence est une paire non ordonnée d’états distincte.

## Correction géométrique

La fermeture diédrique des 13 formes `D5` contient 85 copies géométriques. Mais, pour une orientation commune fixée par l’opérateur, seules **70** sont réellement produites par les 3 341 diagrammes locaux :

- codimension 1 : 20 ;
- codimension 2 : 30 ;
- codimension 3 : 20.

Les 15 restantes sont des copies obtenues uniquement par réflexion et exigent l’orientation opposée du cycle.

## Capacité dynamique exacte

Pour une ombre géométrique exacte `ω`,

`Cap(ω)=sup_T #{paires distinctes produisant ω}`.

Les cinq rotations d’une même classe orientée ont la même capacité.

| Classe | Capacité d’une copie exacte |
|---|---:|
| `C5O-00` | 2 |
| `C5O-01` | 2 |
| `C5O-02` | 2 |
| `C5O-03` | 2 |
| `C5O-04` | 8 |
| `C5O-05` | 4 |
| `C5O-06` | ∞ |
| `C5O-07` | 8 |
| `C5O-08` | ∞ |
| `C5O-09` | 12 |
| `C5O-10` | ∞ |
| `C5O-11` | 16 |
| `C5O-12` | ∞ |
| `C5O-13` | 32 |

Donc, sur les 70 ombres orientées exactes :

- 50 ont capacité finie ;
- 20 ont capacité infinie ;
- spectre fini : `{2,4,8,12,16,32}`.

Effectifs :

- 20 ombres de capacité 2 ;
- 5 de capacité 4 ;
- 10 de capacité 8 ;
- 5 de capacité 12 ;
- 5 de capacité 16 ;
- 5 de capacité 32.

## Mécanisme des bornes finies

Pour chaque phase `j`, si `R_h(j)` désigne les états du bassin à profondeur `h`, la cohérence binaire donne

`|R_0(j)|=1`,

`|R_h(j)|≤2^(h-1)` pour `h≥1`.

Les gabarits profondeur–phase de chaque ombre transforment ces ressources en bornes de comptage. Les classes `C5O-04` et `C5O-09` utilisent en plus les noyaux fixes : il existe au plus deux points fixes cohérents, chacun avec au plus un prédécesseur externe direct pertinent.

Un même système constitué du bassin maximal de profondeur 3 et de deux composantes fixes maximales atteint simultanément toutes les capacités finies ci-dessus.

## Mécanisme des capacités infinies

Les classes `C5O-06`, `08`, `10`, `12` possèdent un témoin utilisant un noyau extérieur de période 2. Des copies disjointes de ce gadget peuvent être ajoutées arbitrairement sans interaction forcée entre elles.

Par `BR-OBS-CAP-01`, leur capacité est donc infinie.

## Relation avec la v1

La v1 certifiait seulement les capacités totales de six classes ancrées :

`10,10,20,40,80,160` pour `C5O-02,03,05,07,11,13`.

Ces bornes restent exactes. Elles correspondent à cinq fois les capacités d’une copie géométrique, car chaque classe comporte cinq rotations.

## Limites

- Résultat exact pour `C5`, binaire, `L=3`.
- Une capacité individuelle ne donne pas les contraintes de ressources **partagées** entre plusieurs ombres différentes.
- La capacité borne des occurrences/témoins distincts, pas automatiquement les coefficients entiers d’un circuit positif ; utiliser `BR-OBS-CAP-02` pour cette interface.

## Provenance

Rapport : `/Recherche/03_AUDITS_CERTIFICATS/V19_THEORIE_CAPACITES_DYNAMIQUES_2026-10-15.md`  
Code : `/Recherche/04_CODE_DONNEES/v19_dynamic_capacity_theory.py`  
Catalogue : `/Recherche/04_CODE_DONNEES/V19_GEOMETRIC_CAPACITY_85_AUDIT_2026-10-15.csv`