# Reconstruction indépendante — graphe forcé P1–P4 et localité L+2

**Date :** 10 novembre 2026  
**Statut initial :** preuve reconstruite ci-dessous ; contre-tests finis indépendants en attente de CI.  
**Source de comparaison :** note primaire V19(2), §2–4. Cette reconstruction ne reprend aucun code des scripts V19.

## 0. Cadre et conventions

Soit (T:X\to X) une application sur un ensemble fini. Pour une paire non diagonale (\{u,v\}), les contraintes forcées sont les arêtes de deux types :

- (M(u,v)) (« fusion ») si (T(u)=T(v)) ;
- (I(u,v)) (« invariance ») si (\{T(u),T(v)\}=\{u,v\}).

Chaque arête impose la relation binaire (c_u\oplus c_v=1). Le graphe forcé est dit cohérent si toutes ces relations admettent simultanément une coloration binaire. C'est exactement l'absence de cycle de parité impaire.

Pour une paire (p=\{x,y\}) et un horizon (L\ge2), on ajoute les égalités de mauvais événement
\[
c_{T^t x}\oplus c_{T^t y}=0,\qquad 0\le t<L.
\]
L'ombre sur un cycle (B) est l'ensemble des colorations binaires de (B) extensibles à toutes les contraintes forcées et aux égalités de l'événement.

## 1. Critère singleton des contraintes forcées

Posons (H_L(\{u,v\})\) égal à l'ensemble des paires non diagonales rencontrées par les itérations synchrones de (\{u,v\}), aux temps (0,\ldots,L-1).

Pour (L\ge2), (|H_L(\{u,v\})|=1) si et seulement si (T(u)=T(v)) ou (\{T(u),T(v)\}=\{u,v\}).

**Preuve.** Si (T(u)=T(v)), la paire devient diagonale au temps 1 et ne réapparaît pas. Si les images sont exactement (u,v), la paire reste inchangée. Réciproquement, si les images sont distinctes et que la seule paire non diagonale rencontrée est la paire initiale, l'image au temps 1 doit être cette même paire. Il n'y a pas d'autre possibilité. \(\square\)

## 2. Théorème P1–P4 : reconstruction structurelle

**Théorème.** Si le graphe forcé est cohérent, chacune de ses composantes connexes est un chemin (P_1,P_2,P_3\) ou (P_4). Dans toute composante de taille au moins 3, il existe exactement une arête (I), centrale, et les autres arêtes sont de type (M).

**Preuve.**

**Étape A — les arêtes (M) forment un matching.** Si trois sommets distincts (a,b,c) avaient la même image, les trois arêtes (M(a,b),M(a,c),M(b,c)) formeraient un triangle. Trois inégalités binaires sur un triangle sont incompatibles. Donc chaque fibre (T^{-1}(z)) contient au plus deux éléments ; chaque sommet est incident à au plus une arête (M).

**Étape B — caractérisation des arêtes (I).** Pour deux sommets distincts (u,v), (I(u,v)) signifie soit (T(u)=v,T(v)=u), soit (T(u)=u,T(v)=v). Autrement dit, ses extrémités sont soit un 2-cycle, soit deux points fixes. Aucun sommet non périodique n'est donc incident à une arête (I).

**Étape C — les arêtes (I) forment un matching sous cohérence.** Un 2-cycle ne peut être incident à une autre arête (I) : ses deux sommets sont déjà déterminés comme prédécesseurs périodiques l'un de l'autre. Pour les points fixes, trois points fixes distincts produiraient le triangle formé par leurs trois arêtes (I), impossible sous cohérence. Il y a donc au plus deux points fixes, et au plus une arête (I) entre eux. Ainsi chaque sommet est incident à au plus une arête (I).

**Étape D — exclusion des cycles et borne de taille.** Le graphe est l'union de deux matchings disjoints (M\sqcup I), donc chaque degré est au plus 2 et les arêtes alternent de type. Une composante cyclique serait un cycle alterné. Elle devrait contenir une arête (I), dont les extrémités sont périodiques (2-cycle ou points fixes). Or aucun sommet périodique de ce noyau ne peut être relié par une arête (M) à un autre sommet périodique : dans une fibre de point fixe, le second élément est transitoire ; dans une fibre d'un sommet d'un 2-cycle, le second élément est transitoire, le prédécesseur périodique étant déjà l'autre sommet du 2-cycle. Le cycle alterné est donc impossible.

Enfin, une arête (I) ne peut être entourée que d'au plus une arête (M) à chacune de ses extrémités, car (M) est un matching. Une composante contient donc au plus quatre sommets. Sans arête (I), elle est une arête (M) isolée ou un sommet isolé. Les seules formes sont (P_1,P_2,P_3,P_4). \(\square\)

### Vérification des formes P3/P4

- Deux points fixes (a,b) : (I(a,b)), et au plus un frère (u\to a), (v\to b), donnant (u-a-b-v).
- Un 2-cycle (a\leftrightarrow b) : (I(a,b)), et au plus un frère (u\to a), (v\to b), donnant (u-b-a-v).

Les frères peuvent manquer, ce qui donne (P_2) ou (P_3).

## 3. Lemme de diamètre orbital

Dans une composante (P_1\)–(P_4), si deux sommets (r,s) sont reliés, chaque sommet intérieur du chemin entre eux appartient à
\[
\{r,s,Tr,T^2r,T^3r,Ts,T^2s,T^3s\}.
\]
C'est une vérification des deux formes possibles ci-dessus : dans le cas fixe, les frères ont pour images les deux extrémités de l'arête (I) ; dans le cas du 2-cycle, leurs images sont les extrémités opposées, et deux itérations supplémentaires atteignent les deux sommets du 2-cycle. Pour (P_2/P_3), la propriété est immédiate.

Ce lemme ne dit pas que tout sommet de la composante est sur l'orbite d'un sommet donné : il ne concerne que le chemin entre deux sommets pertinents. C'est précisément la distinction qui permet d'écarter les feuilles non observées sans perdre de contrainte entre sommets pertinents.

## 4. Théorème de petit modèle L+2

**Théorème.** Soit (B) un cycle de longueur (q\ge3), et supposons le graphe forcé cohérent. Pour (L\ge2), l'ombre sur (B) de la paire (\{x,y\}) à horizon (L) est déterminée par (B) et les deux préfixes
\[
x,Tx,\ldots,T^{L+2}x,\qquad y,Ty,\ldots,T^{L+2}y.
\]

**Preuve.**

Posons (R=B\cup\{T^t x,T^t y:0\le t<L\}\), l'ensemble des sommets sur lesquels portent les égalités de l'événement ou dont la couleur est demandée.

Les contraintes supplémentaires de l'événement sont entièrement dans (R). Pour les contraintes forcées, leur graphe est une union de chemins (P_1\)–(P_4). Dans une composante, les relations induites entre les sommets de (R) sont exactement les parités des chemins forcés qui les relient. Toute paire (r,s\in R) reliée par un tel chemin a, d'après le lemme orbital, ses sommets intermédiaires dans les orbites de (r,s) jusqu'à trois itérations. Si (r\) ou (s\) est dans (B), son orbite reste dans (B). Sinon, un sommet de (R\setminus B) est (T^t x) ou (T^t y) avec (t<L), et ses trois itérés supplémentaires sont au plus au temps (L+2). Tous les sommets du chemin sont donc présents dans le sous-ensemble local (V\) constitué de (B) et des deux préfixes jusqu'à (L+2).

Ainsi, pour chaque composante forcée, la relation de parité entre toute paire de sommets pertinents (R) est identique dans le graphe global et dans le graphe forcé induit par (V). Les sommets hors de (R) qui restent attachés à une seule partie de composante sont des feuilles sans autre contrainte ; ils peuvent toujours recevoir la couleur opposée à leur voisin et n'imposent aucune restriction supplémentaire sur (R).

En ajoutant les mêmes égalités d'événement, toutes portées par (R\subseteq V), les colorations de (B) extensibles globalement sont donc exactement celles extensibles dans le modèle local. \(\square\)

## 5. Contre-tests exacts indépendants

Un programme neuf, sans import des scripts V19 existants, énumère toutes les endofonctions étiquetées (T:[n]\to[n]), pour (1\le n\le6).

- Pour P1–P4 : il reconstruit les arêtes directement à partir de la définition, teste la cohérence par propagation XOR, puis vérifie chaque composante sans utiliser de reconnaissance de motifs du script source.
- Pour L+2 : pour tous les systèmes cohérents avec un cycle de longueur au moins 3, toutes les paires non ordonnées et (L=2,3), il compare les projections globales et celles du sous-graphe induit par les préfixes (L+2), avec un solveur de propagation explicite sur les colorations du cycle.

Les résultats exacts attendus sont :

| n | Endofonctions cohérentes | Systèmes cohérents avec cycle q≥3 | Comparaisons global/local |
|---:|---:|---:|---:|
| 1 | 1 | — | — |
| 2 | 4 | — | — |
| 3 | 23 | 2 | 12 |
| 4 | 191 | 38 | 456 |
| 5 | 2 069 | 614 | 12 280 |
| 6 | 27 454 | 10 384 | 312 720 |
| **Total** | **29 742** | — | **325 468** |

Aucun contre-exemple n'est trouvé. Ces nombres sont des contrôles finis ; ils ne remplacent pas la preuve ci-dessus.

## 6. Points de vigilance / limites

1. La cohérence est une hypothèse indispensable : si le graphe forcé contient une contradiction de parité, l'ombre est vide pour des raisons globales et la réduction doit être reformulée.
2. La preuve utilise exactement la définition des arêtes (M/I) et les égalités événementielles ci-dessus. Une variation de convention (par exemple inclure (t=L)) change le préfixe requis et doit être auditée séparément.
3. La borne (L+2) est une borne suffisante ; cette reconstruction ne prétend pas qu'elle soit optimale.
4. La preuve concerne les cycles (q\ge3), comme dans l'énoncé source.
5. La validation bibliographique de l'originalité du lemme reste distincte et indéterminée.

## 7. Statut

- Critère singleton : **DÉMONTRÉ** par argument direct.
- Structure P1–P4 : **DÉMONTRÉ** sous cohérence, preuve reconstruite ci-dessus.
- Localité L+2 : **DÉMONTRÉ** sous cohérence et les conventions fixées, preuve reconstruite ci-dessus.
- Contre-tests indépendants (n\le6), (L=2,3) : **CALCUL EXACT** si le workflow CI passe.
- Généralisation à d'autres définitions/conventions : **INDÉTERMINÉ**.
- Originalité bibliographique : **INDÉTERMINÉ**.

Aucun résultat n'est ajouté à la bibliothèque certifiée et aucune branche n'est fusionnée.
