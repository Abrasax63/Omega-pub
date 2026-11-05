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
- `V19ForcedEdge` et `v19_forced_edge_symm` : adjacency non orientée des arêtes M/I et preuve de sa symétrie.
- `V19AlternatingChain4` et `v19_no_forced_alternating_chain4` : regroupement et exclusion des deux motifs alternés de quatre arêtes.

Ces résultats formalisent les deux propriétés de matching et l'obstruction locale qui borne les chaînes alternées. Ils constituent le noyau combinatoire du raisonnement P1–P4.

## Vérification automatisée

Le workflow [V19 Lean core](https://github.com/Abrasax63/Omega-pub/actions/workflows/v19-lean-core.yml) installe Lean 4.19.0 via Elan et compile directement `V19Core.lean`.

Première compilation réussie du noyau initial :
[GitHub Actions — run 42075241015](https://github.com/Abrasax63/Omega-pub/actions/runs/42075241015).

La compilation complète du noyau précédent a réussi : [GitHub Actions — run 42076029405](https://github.com/Abrasax63/Omega-pub/actions/runs/42076029405).

L'extension du graphe forcé compile également : [GitHub Actions — run 42078870162](https://github.com/Abrasax63/Omega-pub/actions/runs/42078870162).


- `v19_no_three_forced_neighbors` : sous cohérence, un sommet ne peut pas avoir trois voisins forcés deux à deux distincts. Le résultat découle des matchings M et I : parmi trois arêtes incidentes, deux auraient nécessairement le même type.
- `v19_merge_neighbors_eq` et `v19_invariant_neighbors_eq` exposent les deux lemmes de voisinage utilisés dans cette borne de degré.

## Ce qui reste à formaliser

- le théorème de classification de toutes les composantes du graphe forcé en chemins de taille au plus quatre sommets (P1–P4), à partir des lemmes locaux ;
- la définition formelle des ancrages et des préfixes ;
- la visibilité des chemins entre ancrages jusqu'à L+2 ;
- l'extension des branches pendantes sans ancrage ;
- l'égalité des projections de colorations sur B, donc l'égalité des ombres globale et locale.

**Statut :** matching M et I, périodicité des extrémités I et obstruction aux chaînes alternées de quatre arêtes compilés sous Lean 4.19. La classification globale P1–P4 et le théorème général L+2 restent non formalisés et non certifiés.

Aucune étape ultérieure ne doit être considérée comme acquise tant que son théorème Lean compilé n'est pas présent.


L'adjacence forcée est maintenant explicitée, mais les composantes connexes ne sont pas encore définies dans Lean : la classification P1–P4 n'est donc pas encore un théorème formalisé.


## Connexité et composantes — état vérifié au 5 novembre 2026

Le noyau définit désormais `V19Reachable` comme la relation de marche finie du graphe forcé, puis `V19Component` comme le prédicat des sommets atteignables depuis une racine. Les lemmes de réflexivité, symétrie et transitivité sont compilés. Deux racines sont dans la même composante exactement lorsque leurs prédicats de composante sont égaux (`v19_component_eq_iff_reachable`). La fermeture d'une composante par les arêtes forcées est aussi établie.

La séparation des types d'arêtes est explicite : `v19_merge_invariant_disjoint` prouve qu'une même paire distincte ne peut être à la fois M et I.

Compilation Lean 4.19.0 confirmée :
- [run #42087598469](https://github.com/Abrasax63/Omega-pub/actions/runs/42087598469) — noyau Lean, SUCCESS ;
- [run #42087598738](https://github.com/Abrasax63/Omega-pub/actions/runs/42087598738) — chemins et cycles, SUCCESS ;
- [run #42087804728](https://github.com/Abrasax63/Omega-pub/actions/runs/42087804728) — noyau Lean après disjonction M/I et fermeture des composantes, SUCCESS.

**Frontière de preuve :** les composantes sont maintenant définies et leurs lois élémentaires sont prouvées. Le théorème Lean « chaque composante est P1, P2, P3 ou P4 » n'est toujours pas formalisé. La note primaire V19(2) contient déjà ce théorème mathématique, mais le noyau Lean doit encore reconstruire le passage de la connexité, de la borne de degré et de l'exclusion des cycles à la classification explicite. Le théorème de petit modèle L+2 et la visibilité restent eux aussi hors de la formalisation.
