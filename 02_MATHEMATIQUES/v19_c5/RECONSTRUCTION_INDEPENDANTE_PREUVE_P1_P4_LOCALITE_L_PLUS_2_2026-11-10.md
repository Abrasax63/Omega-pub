# Reconstruction indépendante — graphe forcé P1–P4 et localité L+2

**Date :** 10 novembre 2026  
**Statut :** preuve reconstruite ; contre-tests finis indépendants soumis à CI.  
**Source de comparaison :** note primaire V19(2), §2–4. Aucun code V19 antérieur n'est importé par le nouveau vérificateur.

## 0. Cadre et conventions

Soit T : X → X une application sur un ensemble fini. Pour une paire non diagonale {u,v}, le graphe forcé contient deux types d'arêtes :

- M(u,v), dite fusion, si T(u)=T(v) ;
- I(u,v), dite invariance, si {T(u),T(v)}={u,v}.

Chaque arête impose c(u) XOR c(v)=1. Le graphe forcé est cohérent si toutes ces relations admettent simultanément une coloration binaire. C'est équivalent à l'absence de cycle de parité impaire.

Pour une paire p={x,y} et un horizon L≥2, les égalités du mauvais événement sont :
c(T^t x) XOR c(T^t y)=0, pour 0≤t<L.

L'ombre sur un cycle B est l'ensemble des colorations binaires de B extensibles à toutes les contraintes forcées et aux égalités de l'événement.

## 1. Critère singleton des contraintes forcées

Soit H_L({u,v}) l'ensemble des paires non diagonales rencontrées par les itérations synchrones de {u,v}, aux temps 0,...,L−1.

Pour L≥2, |H_L({u,v})|=1 si et seulement si T(u)=T(v) ou {T(u),T(v)}={u,v}.

**Preuve.** Si T(u)=T(v), la paire devient diagonale au temps 1 et ne réapparaît pas. Si les images sont distinctes mais constituent exactement la paire initiale, celle-ci reste inchangée. Réciproquement, si l'image au temps 1 est non diagonale et distincte de la paire initiale, H_L contient déjà deux paires distinctes. Il n'y a pas d'autre possibilité. QED.

## 2. Théorème P1–P4 : reconstruction structurelle

**Théorème.** Si le graphe forcé est cohérent, chacune de ses composantes connexes est un chemin P1, P2, P3 ou P4. Dans toute composante de taille au moins 3, il existe exactement une arête I, centrale, et les autres arêtes sont de type M.

**Preuve.**

**Étape A — les arêtes M forment un matching.** Si trois sommets distincts a,b,c avaient la même image, les trois arêtes M(a,b), M(a,c), M(b,c) formeraient un triangle. Trois inégalités binaires sur un triangle sont incompatibles. Donc chaque fibre T⁻¹(z) contient au plus deux éléments ; chaque sommet est incident à au plus une arête M.

**Étape B — caractérisation des arêtes I.** Pour deux sommets distincts u,v, I(u,v) signifie soit T(u)=v et T(v)=u, soit T(u)=u et T(v)=v. Ses extrémités sont donc soit un 2-cycle, soit deux points fixes. Aucun sommet non périodique n'est incident à une arête I.

**Étape C — les arêtes I forment un matching sous cohérence.** Un sommet d'un 2-cycle ne peut être incident à une autre arête I : son seul prédécesseur périodique est l'autre sommet du 2-cycle. Pour les points fixes, trois points fixes distincts produiraient le triangle formé par leurs trois arêtes I, impossible sous cohérence. Il y a donc au plus deux points fixes, et au plus une arête I entre eux. Ainsi chaque sommet est incident à au plus une arête I.

**Étape D — exclusion des cycles et borne de taille.** Le graphe est l'union disjointe de deux matchings M et I : chaque degré est au plus 2 et les arêtes alternent de type. Une composante cyclique devrait donc alterner M et I. Or chaque extrémité d'une arête I est périodique (point fixe ou sommet d'un 2-cycle), tandis que toute arête M incidente à un tel sommet relie celui-ci à un sommet transitoire. Un sommet transitoire ne peut être incident à I. Un cycle alterné est donc impossible.

Une composante contenant une arête I ne peut avoir qu'une arête M supplémentaire à chacune de ses extrémités, car M est un matching. Elle contient au plus quatre sommets. Une composante sans arête I est un sommet isolé ou une unique arête M. Les seules formes sont P1, P2, P3, P4. QED.

### Formes explicites des composantes de taille 3 ou 4

- **Noyau de points fixes :** T(a)=a, T(b)=b. L'arête I relie a à b. Au plus un frère u avec T(u)=a et un frère v avec T(v)=b peuvent s'y attacher, donnant le chemin u—a—b—v.
- **Noyau 2-cycle :** T(a)=b, T(b)=a. L'arête I relie a à b. Au plus un frère u avec T(u)=a et un frère v avec T(v)=b peuvent s'y attacher, donnant le chemin u—b—a—v.

Un ou deux frères peuvent manquer, ce qui donne P2 ou P3. Dans les deux cas, les sommets transitoires sont les feuilles.

## 3. Lemme orbital précis

Dans une composante P1–P4, considérons deux sommets r,s reliés par le chemin de la composante.

- Pour le noyau de points fixes, les sommets intérieurs du chemin sont parmi T(r) et T(s).
- Pour le noyau 2-cycle, ils sont parmi T(r), T²(r), T(s), T²(s).
- P2 et P3 sont des sous-chemins de ces formes.

De plus, pour identifier chaque arête du chemin, il suffit de connaître les images des sommets intérieurs. Dans le cas 2-cycle, ces images sont connues en suivant au plus trois itérations depuis r ou s : la chaîne d'un frère est z → a → b → a. Dans le cas fixe, deux itérations suffisent.

Cette formulation est plus précise que l'affirmation vague « le diamètre vaut au plus 3 » : les sommets intérieurs et les transitions nécessaires pour identifier les arêtes sont effectivement présents dans les préfixes orbitaux jusqu'à trois itérations.

## 4. Théorème de petit modèle L+2

**Théorème.** Soit B un cycle de longueur q≥3, et supposons le graphe forcé cohérent. Pour L≥2, l'ombre sur B de la paire {x,y} à horizon L est déterminée par B et les deux préfixes :

x, T(x), ..., T^(L+2)(x)  
y, T(y), ..., T^(L+2)(y).

**Preuve.**

Posons R = B ∪ {T^t(x), T^t(y) : 0≤t<L}. Ce sont les sommets dont la couleur intervient dans les égalités de l'événement ou qui appartiennent au cycle dont on demande l'ombre.

Les égalités de l'événement sont entièrement portées par R. Dans le graphe forcé, chaque composante est un chemin P1–P4. Les restrictions imposées aux couleurs de deux sommets r,s de R proviennent exactement du chemin forcé qui les relie, s'il existe.

Par le lemme orbital, les sommets intérieurs de ce chemin sont dans les orbites de r et s jusqu'à deux itérations. Pour identifier toutes les arêtes de ce chemin, les transitions nécessaires sont connues jusqu'à trois itérations. Si r ou s appartient à B, son orbite reste dans B. Sinon, r ou s est T^t(x) ou T^t(y), avec t<L ; trois itérations supplémentaires atteignent au plus le temps L+2. Le chemin forcé entre deux sommets pertinents, ainsi que chacune de ses arêtes, est donc entièrement déterminé par B et les deux préfixes jusqu'à L+2.

Les feuilles d'une composante qui ne sont pas pertinentes et ne se trouvent sur aucun chemin entre deux sommets de R n'imposent aucune restriction supplémentaire : elles ne portent qu'une contrainte d'inégalité avec leur unique voisin et peuvent toujours être colorées en conséquence.

Ainsi, les relations de parité induites sur R sont les mêmes dans le système global et dans le modèle local. En ajoutant les mêmes égalités d'événement, les colorations de B extensibles globalement sont exactement celles extensibles dans le modèle local. QED.

## 5. Contre-tests exacts indépendants

Un programme neuf, sans import des scripts V19 existants, énumère toutes les endofonctions étiquetées T:[n]→[n], pour 1≤n≤6.

- Pour P1–P4 : il reconstruit les arêtes directement à partir de la définition, teste la cohérence par propagation XOR, puis vérifie chaque composante comme chemin de taille au plus 4.
- Pour L+2 : pour tous les systèmes cohérents avec un cycle de longueur au moins 3, toutes les paires non ordonnées et L=2,3, il compare les projections globales et celles du sous-graphe induit par les préfixes L+2, avec un solveur explicite par propagation sur les colorations du cycle.

Les comptes de reproduction attendus sont :

| n | Endofonctions cohérentes | Systèmes cohérents avec cycle q≥3 | Comparaisons global/local |
|---:|---:|---:|---:|
| 1 | 1 | — | — |
| 2 | 4 | — | — |
| 3 | 23 | 2 | 12 |
| 4 | 191 | 38 | 456 |
| 5 | 2 069 | 614 | 12 280 |
| 6 | 27 454 | 10 384 | 312 720 |
| **Total** | **29 742** | — | **325 468** |

Aucun contre-exemple n'est présumé : les comptes et l'absence de divergence ne seront dits reproduits qu'après succès de la CI.

## 6. Points de vigilance et limites

1. La cohérence est une hypothèse indispensable. Si le graphe forcé est incohérent, il faut traiter séparément l'ombre vide résultante.
2. La preuve utilise exactement les arêtes M/I et les égalités événementielles aux temps 0,...,L−1. Inclure le temps L changerait l'énoncé et doit être audité séparément.
3. L+2 est une borne suffisante ; cette reconstruction ne prétend pas qu'elle soit optimale.
4. La preuve concerne les cycles q≥3.
5. La validation bibliographique de l'originalité du lemme reste distincte et indéterminée.

## 7. Statut

- Critère singleton : **DÉMONTRÉ** par argument direct.
- Structure P1–P4 : **DÉMONTRÉ** sous cohérence, preuve reconstruite ci-dessus.
- Localité L+2 : **DÉMONTRÉ** sous cohérence et les conventions fixées, preuve reconstruite ci-dessus.
- Contre-tests indépendants n≤6, L=2,3 : **EN ATTENTE DE CI**.
- Généralisation à d'autres définitions/conventions : **INDÉTERMINÉ**.
- Originalité bibliographique : **INDÉTERMINÉ**.

Aucun résultat n'est ajouté à la bibliothèque certifiée et aucune branche n'est fusionnée.
