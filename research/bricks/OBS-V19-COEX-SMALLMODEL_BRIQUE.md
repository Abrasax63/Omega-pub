# OBS-V19-COEX-SMALLMODEL — Petit modèle de coexistence de k ombres

**Type :** brique réutilisable / interface canonique  
**ID scientifique :** `OBS-V19-COEX-SMALLMODEL` v2  
**Statut :** DÉMONTRÉ (certification interne RAVI-2)  
**Originalité :** INDÉTERMINÉE  
**Projet source :** Observabilité — V19

## Domaine

Endofonction finie `T:X→X`, observation binaire, cycle distingué `C_q` avec `q≥3`, horizon `L≥2`, contraintes forcées cohérentes. On fixe `k≥1` **paires non ordonnées distinctes** et leurs `k` ombres sur `C_q`. Les paires peuvent partager des états.

## Énoncé

Si ces `k` ombres coexistent dans un système fini quelconque, alors les **mêmes k paires distinctes** coexistent déjà dans un système fini de taille

`N ≤ q + 2k(L+3) + max(3,2k)`.

Pour `q`, `L` et `k` fixés, la coexistence est donc décidable par recherche finie indépendamment de `|X|`.

## Preuve condensée

1. `OBS-V19-LOCAL-L2` : chaque ombre dépend seulement de `C_q` et des deux préfixes jusqu’au temps `L+2`.
2. L’union des préfixes des `k` paires contient au plus `q+2k(L+3)` états.
3. Il reste au plus `2k` images terminales indéfinies.
4. Ajouter un cycle externe de longueur `max(3,2k)` et y envoyer injectivement les terminaux.
5. Aucun état du sous-système initial n’est quotienté ni identifié : les paires distinctes restent distinctes.
6. Les préfixes jusqu’à `L+2` restent inchangés, donc les ombres aussi.
7. Le cycle ajouté ne crée ni point fixe ni 2-cycle ; les nouvelles fusions terminales sont disjointes.

## Dépendances

- `OBS-V19-COEX-SMALLMODEL DEPEND_DE OBS-V19-LOCAL-L2`
- `OBS-V19-LOCAL-L2 DEPEND_DE OBS-V19-FORCED-P4`

## Réutilisation

Utiliser cette brique pour :

- convertir une coexistence globale en recherche finie à `q,L,k` fixés ;
- rechercher une hyperarête interdite ou une capacité de multiplicité ;
- produire un certificat fini de coexistence/non-coexistence ;
- borner une recherche exhaustive indépendamment de la taille ambiante.

## Briques compagnons

- `OBS-V19-C5-ORIENTED14` : conserver l’orientation commune lors de l’assemblage ;
- `OBS-V19-FIRST-OBSTRUCTION11` : première obstruction de multiplicité au niveau des 14 labels orientés ;
- `OBS-V19-C5-CAPACITY` : capacités exactes de six classes ancrées.

## Contre-tests et limites

La compression/complétion a été testée sur 1 347 familles de 2 ou 3 paires : 0 divergence. Les tests soutiennent l’implémentation mais la certification repose sur la preuve.

La brique ne caractérise pas quelles familles coexistent. Elle donne une borne de témoin lorsqu’elles coexistent. Elle ne généralise pas automatiquement hors observation binaire ou hors cohérence forcée.

## Provenance

Preuve initiale : `/Recherche/03_AUDITS_CERTIFICATS/V19_ASSEMBLAGE_ORIENTE_2026-10-15.md`  
Correction multiplicité distincte : `/Recherche/03_AUDITS_CERTIFICATS/V19_MULTIPLICITE_CAPACITE_2026-10-15.md`  
Code : `/Recherche/04_CODE_DONNEES/v19_multiplicity_capacity.py`

Version active : commit `COMMIT-RAVI2-2026-10-15-V19-CAPACITY-05`.