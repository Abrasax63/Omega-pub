# V19 — formalisation Lean

## Résultats formalisés

Le fichier `V19Core.lean` est autonome (Lean 4, sans Mathlib) et contient :

- `V19Merge` et `V19Invariant`, les deux relations d'arêtes forcées ;
- `V19Coherent`, la cohérence exprimée par une coloration binaire séparant les extrémités de toute arête forcée ;
- `v19_merge_matching` et `v19_no_three_preimages` : les arêtes de fusion forment un matching, et trois états distincts ne peuvent avoir la même image ;
- `v19_invariant_matching` : les arêtes d'invariance forment également un matching ;
- `V19CorePeriodic` et `v19_invariant_endpoints_core_periodic` : chaque extrémité d'une arête I est un point fixe ou appartient à un 2-cycle ;
- `v19_merge_not_both_core_periodic` : une arête M ne peut relier deux états fixes/2-périodiques distincts ;
- `v19_no_alternating_MIMI` et `v19_no_alternating_IMIM` : les deux orientations d'une chaîne forcée alternée de quatre arêtes sont impossibles.

Ces résultats formalisent les deux propriétés de matching et l'obstruction locale qui borne les chaînes alternées. Ils constituent le noyau combinatoire du raisonnement P1–P4.

## Vérification automatisée

Le workflow [V19 Lean core](https://github.com/Abrasax63/Omega-pub/actions/workflows/v19-lean-core.yml) installe Lean 4.19.0 via Elan et compile directement `V19Core.lean`.

Première compilation réussie du noyau initial :
[GitHub Actions — run 42075241015](https://github.com/Abrasax63/Omega-pub/actions/runs/42075241015).

Les ajouts ultérieurs sur les extrémités périodiques et les chaînes alternées doivent encore passer cette compilation avant d'être considérés comme vérifiés.

## Ce qui reste à formaliser

- le théorème de classification de toutes les composantes du graphe forcé en chemins de taille au plus quatre sommets (P1–P4), à partir des lemmes locaux ;
- la définition formelle des ancrages et des préfixes ;
- la visibilité des chemins entre ancrages jusqu'à L+2 ;
- l'extension des branches pendantes sans ancrage ;
- l'égalité des projections de colorations sur B, donc l'égalité des ombres globale et locale.

**Statut :** noyau initial compilé ; extension matching I / périodicité / chaînes de quatre arêtes écrite mais compilation à confirmer ; théorème général L+2 non formalisé et non certifié.

Aucune étape ultérieure ne doit être considérée comme acquise tant que son théorème Lean compilé n'est pas présent.
