# V19 — formalisation Lean

## Portée du premier noyau

Le fichier `V19Core.lean` formalise, dans Lean 4 sans dépendance externe :

- les arêtes de fusion (M(u,v) : u\ne v \land T(u)=T(v)) ;
- les arêtes d'invariance (I(u,v)) ;
- la cohérence comme existence d'une coloration binaire qui sépare les extrémités de toute arête forcée ;
- le lemme `v19_merge_matching` : dans un système cohérent, un sommet ne peut pas avoir deux voisins distincts par fusion ;
- le corollaire `v19_no_three_preimages) : trois états distincts ne peuvent pas avoir la même image.

Le fichier est volontairement autonome et n'utilise pas Mathlib.

## Vérification automatisée

Le workflow `.github/workflows/v19-lean-core.yml` compile le fichier avec l'image Lean 4.19.0. Le statut de compilation doit être lu dans GitHub Actions ; l'ajout du fichier source ne vaut pas à lui seul confirmation de compilation.

## Ce qui n'est pas encore formalisé

- le matching des arêtes d'invariance ;
- l'injectivité de (T) sur les états périodiques ;
- la classification des composantes forcées en (P_1,P_2,P_3,P_4) ;
- le lemme de visibilité des chemins entre ancrages ;
- le lemme d'extension des branches pendantes ;
- l'égalité des ombres globale et locale jusqu'à (L+2).

**Statut :** premier noyau Lean écrit ; compilation CI à confirmer ; théorème général de localité (L+2) non formalisé et non certifié.

## Ordre de formalisation prévu

1. établir séparément que (M) et (I) sont des matchings ;
2. dériver degré au plus deux et absence de cycle dans le graphe forcé ;
3. formaliser la classification des composantes ;
4. définir les ancrages, les préfixes et la visibilité ;
5. prouver que les composantes extérieures sont des branches sans ancrage prolongeables ;
6. formaliser l'équivalence des projections de colorations sur (B).

Aucune étape ultérieure ne doit être considérée comme acquise tant que son théorème Lean compilé n'est pas présent.
