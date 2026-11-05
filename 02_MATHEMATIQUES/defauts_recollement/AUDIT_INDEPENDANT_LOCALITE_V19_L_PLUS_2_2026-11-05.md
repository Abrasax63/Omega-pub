# Audit indépendant du lemme de localité V19 — reconstruction de la preuve

**Date :** 2026-11-05  
**Périmètre :** endofonctions totales finies, contraintes forcées cohérentes, cycle distingué (B=C_q), (q\geq 3), horizon (L\geq 2).  
**Statut :** RECONSTRUCTION MATHÉMATIQUE INDÉPENDANTE — à soumettre à contre-audit ; test exhaustif fini séparé.  
**Source primaire comparée :** `02_MATHEMATIQUES/defauts_recollement/sources/V19/NOTE_RECHERCHE_V19_GRAMMAIRE_ORBITALE_2.md`.

## 1. Objet précis

Soit (T:X\to X) une endofonction totale finie. Pour chaque paire distincte (\{u,v\}\), on impose une inégalité binaire forcée lorsque

\[
T(u)=T(v)\quad\text{ou}\quad \{T(u),T(v)\}=\{u,v\}.
\]

On suppose que ce système d'inégalités est cohérent, c'est-à-dire que son graphe est biparti.

Pour une paire initiale (p=\{x,y\}), l'horizon (L) ajoute les égalités

\[
c(T^t x)=c(T^t y),\qquad 0\leq t<L,
\]

en omettant les égalités diagonales lorsque les deux états sont identiques.

L'ombre sur (B) est l'ensemble des colorations binaires de (B) qui se prolongent en une coloration de (X) satisfaisant toutes ces contraintes.

**Énoncé à établir.** Cette ombre est entièrement déterminée par la restriction de (T) à (B) et par les deux préfixes
(x,Tx,\ldots,T^{L+2}x) et (y,Ty,\ldots,T^{L+2}y).

## 2. Graphe des contraintes forcées

On sépare les arêtes en deux types :

- (M) : (T(u)=T(v)) (fusion) ;
- (I) : (\{T(u),T(v)\}=\{u,v\}) (invariance).

### Lemme 1 — les arêtes de fusion forment un matching

Pour un état (w\), les éléments de la fibre (T^{-1}(w)) sont deux à deux reliés par des arêtes (M). Si cette fibre contenait trois états distincts, ces trois sommets formeraient un triangle dans le graphe des contraintes, incompatible avec la bipartition.

Donc chaque fibre a cardinal au plus deux et chaque sommet est incident à au plus une arête (M).

### Lemme 2 — les arêtes invariantes forment un matching

Si (\{T(u),T(v)\}=\{u,v\}), les deux images sont distinctes et il existe exactement deux cas :

1. (T(u)=v) et (T(v)=u) : (u,v) forment un 2-cycle ;
2. (T(u)=u) et (T(v)=v) : (u,v) sont deux points fixes.

Les points fixes sont donc deux à deux reliés par des arêtes (I). Trois points fixes produiraient un triangle ; il y a par conséquent au plus deux points fixes dans tout système cohérent. Chacun ne peut donc avoir qu'un partenaire invariant. Les états d'un 2-cycle ont eux aussi un unique partenaire invariant, leur autre état.

Aucun état non périodique n'est incident à une arête (I). Les arêtes (I) forment donc un matching.

### Lemme 3 — les composantes sont des chemins de taille au plus quatre

Une arête (M) ne peut relier deux états périodiques distincts : la restriction de (T) à l'ensemble des états périodiques est injective, puisque deux orbites périodiques qui ont une image commune appartiennent au même cycle, sur lequel (T) est une permutation.

Ainsi :

- une arête (M) entre deux états non périodiques forme une composante isolée (P_2) ;
- une arête (M) entre un état périodique et un état transitoire peut être prolongée par au plus une arête (I) à son extrémité périodique ;
- si cette arête (I) existe, son autre extrémité peut porter au plus une arête (M).

Les deux types d'arêtes sont chacun des matchings ; le cas précédent exclut les cycles et limite les composantes à trois arêtes. Les composantes sont donc exactement de type (P_1,P_2,P_3,P_4) (certaines formes peuvent ne pas apparaître dans un système donné).

**Conclusion du lemme :** toute composante de contraintes forcées est un chemin de diamètre au plus trois.

## 3. Lemme de visibilité des composantes pertinentes

Appelons *points d'ancrage* les états du cycle (B) et les états qui apparaissent dans les égalités du mauvais événement :
\[
R=B\cup\{T^t x,T^t y:0\leq t<L\}.
\]

Les arêtes ajoutées par le mauvais événement ne touchent que les états de (R\setminus B). Les états de (B) sont périodiques de période (q\geq3) : ils ne peuvent donc être extrémités d'une arête (I). Dans le graphe forcé, une composante qui rencontre (B) est ainsi soit un singleton, soit une arête (M) reliant un état du cycle à un éventuel frère transitoire.

Considérons maintenant une composante forcée qui rencontre un état de trajectoire (z=T^t x) ou (T^t y), avec (t<L).

- Si (z) est non périodique et que sa composante est une simple arête (M), son autre extrémité est soit un autre état de trajectoire (auquel cas son propre préfixe le révèle), soit un état sans égalité ajoutée, dont la couleur peut être choisie librement.
- Si (z) est une extrémité transitoire d'une composante (P_3) ou (P_4) attachée à un 2-cycle (a\leftrightarrow b), la trajectoire révèle le noyau invariant :
  \[
  z\to b\to a\to b.
  \]
  Les états (a,b) apparaissent donc au plus aux temps (t+2,t+1,t+3), respectivement. Comme (t\leq L-1), ils sont visibles au plus au temps (L+2).
- Pour un noyau constitué de deux points fixes, chaque point fixe pertinent est révélé comme image immédiate d'un état transitoire qui lui est attaché ; si le second point fixe n'est pas lui-même un point d'ancrage, il n'est incident à aucune égalité ajoutée et sa couleur se prolonge librement.
- Si un état d'ancrage est déjà dans le noyau invariant, son partenaire est soit lui-même, soit son image suivante dans le cas du 2-cycle, soit un autre point fixe qui doit être un autre point d'ancrage pour influencer l'ombre.

Il en résulte la propriété suivante : **dans toute composante forcée, tout chemin reliant deux points d'ancrage est entièrement contenu dans le cycle et les deux préfixes jusqu'au temps (L+2)**. Les sommets omis ne peuvent être que des extrémités sans égalité ajoutée ; ils ne font que recevoir la couleur opposée à leur voisin lorsqu'une arête les relie au sous-graphe visible.

## 4. Preuve du petit modèle (L+2)

Posons
\[
P=B\cup\{T^t x,T^t y:0\leq t\leq L+2\}.
\]

Notons (G) le graphe forcé complet, (G[P]) son sous-graphe induit sur (P), et (E_L) les arêtes d'égalité du mauvais événement.

Une coloration de (B) appartient à l'ombre globale si et seulement si elle se prolonge en une coloration de (G\cup E_L).

Par le lemme de visibilité :

1. tout chemin de contraintes qui peut relier deux sommets portant une contrainte du mauvais événement, ou relier un tel sommet au cycle (B), est entièrement visible dans (P) ;
2. les sommets de (X\setminus P) qui restent adjacents au sous-graphe visible ne sont que des extrémités de composantes forcées, sans arête du mauvais événement ;
3. chaque telle extrémité peut être colorée avec la couleur opposée à son unique voisin. Les composantes entièrement extérieures à (P) sont biparties par hypothèse et peuvent être colorées indépendamment.

Supprimer ces extrémités ne change donc ni les contradictions entre contraintes, ni les relations de parité induites sur (B). Réciproquement, toute coloration admissible du sous-graphe visible s'étend aux extrémités omises et aux composantes extérieures.

L'ombre globale est ainsi égale à l'ombre calculée sur (P). Cette dernière ne dépend que de (B), des deux préfixes jusqu'à (L+2), et des égalités aux temps (0,\ldots,L-1).

\[
\boxed{\text{L'ombre sur }B\text{ est déterminée par les préfixes jusqu'à }L+2.}
\]

La preuve ne dépend ni de (q) au-delà de (q\geq3), ni de la cardinalité de (X).

## 5. Contre-audit : points à attaquer

La reconstruction ci-dessus repose sur les implications détaillées aux sections 2 et 3. Les contre-tests prioritaires sont :

1. vérifier qu'une composante (P_4) peut être rattachée à un 2-cycle ou à deux points fixes, mais qu'aucun chemin forcé plus long n'est possible ;
2. vérifier le cas où les deux extrémités transitoires d'un (P_4) apparaissent dans les deux préfixes ;
3. vérifier le cas où un seul point fixe du noyau est visible et l'autre est extérieur ;
4. vérifier qu'une extrémité omise ne peut jamais porter une égalité du mauvais événement sans être déjà dans un préfixe ;
5. chercher un contre-exemple avec plusieurs composantes forcées reliées entre elles uniquement par les égalités du mauvais événement.

Une erreur dans l'un de ces cas invaliderait la preuve telle qu'écrite. Aucun statut de certification formelle ou Lean n'est revendiqué.

## 6. Vérification exhaustive finie complémentaire

Un test distinct énumère toutes les extensions d'un cycle distingué (C_3), pour (3\leq N\leq7). Il élimine les systèmes dont le graphe forcé n'est pas biparti, vérifie la forme des composantes, puis compare l'ombre calculée sur tout le système à celle calculée sur le cycle et les deux préfixes jusqu'à (L+2), pour (L=2,3) et toutes les paires initiales.

Résultat de l'exécution exploratoire indépendante :

| N | Extensions | Systèmes cohérents | Comparaisons global/local |
|---:|---:|---:|---:|
| 3 | 1 | 1 | 6 |
| 4 | 4 | 4 | 48 |
| 5 | 25 | 22 | 440 |
| 6 | 216 | 164 | 4 920 |
| 7 | 2 401 | 1 571 | 65 982 |
| **Total** | **2 647** | **1 762** | **71 396** |

Aucune divergence n'a été observée. Le script reproductible associé est `research/code/verify_v19_locality_exhaustive_small.py`. Le transfert du script dans la branche est effectué ; son exécution CI dédiée reste à enregistrer.

**Portée :** ce calcul est un test de falsification fini pour (q=3), (N\leq7), (L\in\{2,3\}). Il ne prouve pas le théorème pour tout (q,L,N), et ne remplace pas la preuve des sections 2 à 4.

## 7. Verdict provisoire

- Structure (P_1\)–(P_4) : **preuve reconstruite**, sous réserve du contre-audit des cas explicités.
- Petit modèle (L+2) : **preuve reconstruite**, avec une étape de visibilité maintenant explicitée ; contre-audit indépendant encore requis.
- Test exhaustif (C_3), (N\leq7), (L=2,3) : **CALCUL EXACT exploratoire**, aucune divergence.
- Vérification par Lean : **NON RÉALISÉE**.
- Généralisation au-delà des hypothèses énoncées : **NON REVENDIQUÉE**.
- Statut de certification final : **À RÉEXAMINER** jusqu'au contre-audit indépendant.



## 8. Contre-vérification finie indépendante par union-find à parité — 5 novembre

Un second vérificateur, `research/code/verify_v19_locality_parity_dsu.py`, a été ajouté. Il n'utilise pas la propagation de couleurs du premier script : les contraintes sont agrégées par une structure union-find avec parité, puis les colorations du cycle sont énumérées.

Périmètre exact :
- cycles distingués C_q, pour q=3,4,5,6 ;
- extensions fonctionnelles de taille N=q,q+1,q+2,q+3 ;
- tous les systèmes dont le graphe forcé est cohérent ;
- toutes les paires initiales ;
- horizons L=2,3,4,5.

Résultats exécutés localement et reproduits par GitHub Actions :
- 2 000 extensions de fonctions examinées ;
- 1 582 systèmes cohérents retenus ;
- 173 680 comparaisons entre ombre globale et ombre restreinte aux préfixes jusqu'à L+2 ;
- aucune divergence ;
- aucune composante forcée hors des formes P1,P2,P3,P4.

CI : [run 42019391876](https://github.com/Abrasax63/Omega-pub/actions/runs/42019391876), job `parity-dsu-stress`, conclusion `success`.

Ce test est indépendant du premier au niveau de l'algorithme de résolution des contraintes (union-find à parité contre propagation de couleurs). Il partage néanmoins la même formalisation des arêtes forcées et du calcul de l'ombre ; il ne constitue donc pas une vérification indépendante des définitions elles-mêmes.

Portée : calcul exact fini sur le domaine indiqué. Il ne démontre pas la localité pour tous q,L,N, ne remplace pas le contre-audit mathématique de l'étape de visibilité, et ne constitue pas une preuve formelle Lean.


## 9. Contre-audit mathématique indépendant — 5 novembre, seconde passe

Cette passe repart des définitions de la note primaire, sans utiliser les résultats des scripts comme prémisses. Elle vérifie séparément la structure des contraintes, puis la réduction de l'ombre à la partie visible.

### 9.1 Structure P1–P4 : reconstruction

Notons F le graphe des arêtes forcées, M les arêtes de fusion et I les arêtes d'invariance.

- Pour chaque sommet w, les préimages distinctes de w forment une clique M. La cohérence bipartie impose donc |T^{-1}(w)|<=2 : M est un matching.
- Une arête I ne peut relier que les deux sommets d'un 2-cycle ou deux points fixes. Tous les points fixes sont deux à deux reliés par I ; trois points fixes donneraient un triangle. Il y a donc au plus deux points fixes dans tout le système cohérent, et I est un matching.
- Un sommet périodique ne peut avoir deux préimages périodiques distinctes : sur les cycles, T est une permutation. Une arête M ne relie donc jamais deux sommets périodiques distincts.
- Tout sommet non périodique est incident à M au plus une fois et jamais à I. Tout sommet périodique est incident à I au plus une fois et à M au plus une fois. Le degré dans F est donc au plus deux.
- Un cycle dans F devrait alterner M et I. Une arête I de type 2-cycle a pour extrémités les deux sommets du 2-cycle ; une arête M qui s'y attache relie un prédécesseur transitoire à l'un de ces sommets. Une arête I de type points fixes a pour extrémités les deux seuls points fixes possibles ; toute arête M qui s'y attache vient d'un prédécesseur transitoire. Dans les deux cas, les sommets transitoires ne peuvent pas prolonger le chemin par I, et aucun autre sommet périodique ne peut le fermer par M. Aucun cycle n'est donc possible.

Ainsi chaque composante de F est un chemin P1, P2, P3 ou P4. Cette déduction est valable pour toute taille finie, pas seulement dans les domaines testés.

### 9.2 Visibilité des chemins entre ancrages

Posons A = B union les états T^t(x),T^t(y) pour 0<=t<L. Ce sont les seuls sommets qui portent une contrainte d'égalité du mauvais événement ou une couleur observée sur B.

La propriété utile n'est pas que toute la composante forcée d'un ancrage soit nécessairement visible. Elle est que **tout chemin forcé reliant deux sommets de A est visible dans B et les préfixes jusqu'à L+2**.

Vérification par types :

1. **Ancrage transitoire z.** Il n'est incident qu'à une éventuelle arête M. Si son voisin est un autre ancrage, les deux extrémités sont déjà visibles. Si son voisin est périodique s, alors T(z)=T(s). Si s appartient à un cycle de longueur au moins trois, la composante forcée se limite à l'arête M (il n'existe pas d'arête I sur ce cycle) et l'image commune est révélée au pas suivant. Si s appartient à un 2-cycle, trois pas au plus donnent z→b→a→b et révèlent les deux sommets du noyau. Si s est fixe, un pas révèle le point fixe ; son éventuel partenaire fixe est révélé dès qu'il est lui-même ancrage ou qu'un frère transitoire de ce partenaire est ancrage. Le chemin forcé reliant deux ancrages est donc visible avant ou au temps L+2. Un frère de préimage supplémentaire qui n'est pas ancrage ne peut pas prolonger le chemin vers un autre ancrage.
2. **Ancrage dans un 2-cycle.** Son partenaire I est son image suivante, donc visible. Un frère de préimage attaché à l'un des deux sommets ne peut compter comme second ancrage que s'il appartient à l'un des deux préfixes ; dans ce cas sa propre trajectoire révèle le même noyau.
3. **Ancrage point fixe.** Son partenaire I est l'autre point fixe éventuel. Si ce partenaire ou son frère de préimage est un ancrage, la trajectoire de cet ancrage le révèle (le frère transitoire atteint le point fixe en un pas). Sinon, le chemin supplémentaire ne relie aucun autre ancrage et n'ajoute aucune contrainte à l'ombre sur B.

Comme F a diamètre au plus trois, les cas ci-dessus épuisent les chemins possibles. La marge L+2 couvre le cas le plus long, celui d'un frère transitoire attaché à un 2-cycle.

### 9.3 Extension des sommets omis : précision à apporter

La formulation précédente de la section 4 disait que les sommets omis adjacents au sous-graphe visible sont toujours des « extrémités ». C'est trop fort au sens littéral : si un seul point fixe d'une paire I est un ancrage, l'autre point fixe peut être omis avec son propre frère transitoire ; le morceau omis est alors un chemin pendant de longueur deux, pas un sommet isolé.

Cela ne crée pas de contre-exemple. Un chemin pendant d'une composante bipartie, qui ne contient ni sommet de B ni extrémité d'une égalité du mauvais événement, peut toujours être colorié en prolongeant la couleur de son unique point d'attache. Il n'impose aucune nouvelle relation entre sommets de B. La preuve doit donc parler de **branches pendantes sans ancrage**, et non seulement de feuilles isolées.

Cette correction est une précision de la preuve, pas une réfutation du lemme L+2.

### 9.4 Réduction de l'ombre — argument de projection

Dans un graphe de contraintes binaires, une coloration de B est prolongeable si et seulement si :
- aucune composante du graphe augmenté F union E_L ne contient un cycle de parité contradictoire ;
- les parités des chemins reliant des sommets de B sont respectées.

Les arêtes de E_L ont leurs deux extrémités dans A. Les seules parties de F pouvant créer une relation entre deux ancrages, ou entre un ancrage et B, sont les chemins forcés examinés en 9.2 ; ils sont visibles dans les préfixes jusqu'à L+2. Toutes les branches de F non visibles qui restent attachées à cette partie visible ne contiennent aucun autre ancrage : elles se prolongent toujours et ne changent ni la cohérence ni les parités induites sur B. Les composantes entièrement extérieures se colorient indépendamment, puisque F est cohérent et qu'aucune arête de E_L ne les touche.

La projection sur B est donc déterminée par le sous-graphe visible et les égalités E_L. Cela fournit l'argument manquant entre la visibilité des chemins et l'égalité des ombres.

### 9.5 Verdict de cette passe

- Structure P1–P4 : **DÉMONTRÉ** par l'argument combinatoire ci-dessus, sous les définitions exactes de M, I et cohérence bipartie.
- Localité L+2 : **preuve reconstruite et cohérente après précision** sur les branches pendantes sans ancrage. La marge L+2 est suffisante dans les cas de 2-cycle ; le cas fixe est plus court.
- Aucun contre-exemple mathématique n'a été trouvé dans cette passe.
- Le passage précédent « les sommets omis sont toujours des extrémités » est corrigé conceptuellement par 9.3 ; il ne faut pas le citer dans sa formulation littérale.
- Les deux scripts de calcul et leurs résultats restent des vérifications finies complémentaires, pas la base de la preuve universelle.
- Lean : **NON RÉALISÉ**.
- Statut global de certification : **À RÉEXAMINER** jusqu'à une formalisation des définitions et de l'argument de projection, ou une revue humaine indépendante supplémentaire.

