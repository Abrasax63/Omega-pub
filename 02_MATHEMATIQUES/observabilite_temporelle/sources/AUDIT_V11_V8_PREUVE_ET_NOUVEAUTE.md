# V11 — Audit profond de V8 : preuve alternative et antériorité

## Verdict

La factorisation V8 résiste à une seconde preuve indépendante.

Mais l'audit bibliographique impose trois corrections :

1. Le critère qualitatif d'observabilité à horizon infini est essentiellement connu dans la littérature sur les graphes observables / réseaux booléens.
2. Le cas accessible « queue + cycle » et son comptage par mots primitifs sont connus dans la littérature des automates unaires, y compris pour un alphabet de sortie arbitraire.
3. Ce qui n'a pas été retrouvé est la factorisation complète pour une endofonction arbitraire fixée avec ramifications, plusieurs composantes et plusieurs cycles de même longueur.

Statuts :
- preuve mathématique V8 : DÉMONTRÉ INTERNE ;
- critère existence : CONNU / REFORMULATION ;
- cas queue + cycle : CONNU DANS LA LITTÉRATURE ;
- factorisation générale : NOUVEAUTÉ INDÉTERMINÉE.

## 1. Factorisation V8

Pour d_y=|T^{-1}(y)|, c_r(T) le nombre de cycles de période minimale r, et

Q_r(z)=sum_{e|r} mu(e) z^(r/e),

on a

chi_obs(T,∞;z)
=
prod_{y non périodique} (z)_{d_y}
*
prod_{y périodique} (z-1)_{d_y-1}
*
prod_{r>=1} prod_{j=0}^{c_r(T)-1} (Q_r(z)-jr).

## 2. Seconde preuve indépendante

On colore d'abord les cycles.

Sur un cycle de longueur r, les futurs symboliques des r phases sont les rotations du mot cyclique. Ils sont tous distincts exactement lorsque le mot est primitif. Il existe Q_r(m) mots primitifs.

Deux cycles distincts de même longueur doivent recevoir deux classes de rotation différentes. Chaque classe primitive contient r rotations, d'où

Q_r(m)(Q_r(m)-r)...(Q_r(m)-(c_r-1)r).

Deux cycles primitifs de longueurs minimales différentes ne peuvent produire la même suite infinie, car une suite périodique possède une période minimale unique.

On propage ensuite vers les arbres de préimages.

Supposons déjà distincts les futurs symboliques des états plus proches de la partie périodique. Pour deux nouveaux états u,v :

- si Tu != Tv, leurs queues symboliques sont déjà différentes ;
- si Tu = Tv, leurs queues sont identiques, donc ils sont distingués exactement lorsque c(u) != c(v).

Ainsi seuls les frères d'une même fibre doivent recevoir des couleurs distinctes.

Pour un sommet non périodique y, cela donne (m)_{d_y}.
Pour un sommet périodique y, un prédécesseur est déjà le prédécesseur cyclique ; les d_y-1 prédécesseurs transitoires doivent être distincts et éviter sa couleur, donnant (m-1)_{d_y-1}.

Les fibres partitionnent X, donc les choix se multiplient.

Cette preuve reconstruit V8 sans utiliser l'argument historique du premier instant de fusion.

## 3. Traduction en machine de Moore unaire

Une paire (T,c) est une machine de Moore à un seul symbole d'entrée :
- état : X ;
- transition : T ;
- sortie : c.

Deux états sont équivalents au sens de Moore lorsque leurs suites futures de sorties coïncident.

Donc une coloration génératrice à horizon infini est exactement une fonction de sortie qui rend la machine de Moore réduite.

Cette traduction doit désormais être notre vocabulaire bibliographique principal.

## 4. Critère qualitatif déjà connu

Pour le graphe fonctionnel, colorons l'arête x -> T(x) par c(x).

La littérature sur l'observabilité initiale des graphes colorés caractérise l'observabilité par l'absence de :
- deux arêtes entrantes de même couleur vers un même sommet ;
- deux cycles séparés générant la même sortie.

Le premier point est exactement :
Tu=Tv et c(u)=c(v).

Le second est exactement la collision entre futurs périodiques ; la littérature inclut explicitement le cas d'un cycle et de son décalage cyclique.

Notre critère « injectivité sur les fibres + distinction des futurs périodiques » est donc une reformulation spécialisée, pas un nouveau théorème qualitatif.

## 5. Le cas queue + cycle est connu

Considérons une endofonction accessible constituée d'une queue de longueur i suivie d'un cycle de longueur r=n-i.

Si i=0 :
V8 donne Q_n(k).

Si i>=1 :
- les fibres non périodiques donnent k^(i-1) ;
- la jonction queue-cycle donne k-1 ;
- le cycle donne Q_(n-i)(k).

Donc V8 donne pour cette structure fixée :

(k-1) k^(i-1) Q_(n-i)(k).

En sommant sur toutes les longueurs de queue :

Q_n(k) + sum_{i=1}^{n-1} (k-1) k^(i-1) Q_(n-i)(k).

C'est exactement la formule connue pour les motifs/automates unaires minimaux, reprise explicitement par Vieira et Budroni pour un alphabet de k symboles et dérivée d'un argument de Nicaud.

## 6. Ce qui reste non retrouvé

L'audit ciblé n'a pas trouvé de source donnant explicitement la formule complète V8 pour une endofonction arbitraire fixée.

Ce que la formule générale ajoute au cas queue + cycle :
- ramifications arbitraires via (z)_{d_y} et (z-1)_{d_y-1} ;
- plusieurs composantes ;
- plusieurs cycles de même longueur via prod_j(Q_r(z)-jr).

Absence trouvée dans les recherches != preuve de nouveauté.

Statut : INDÉTERMINÉ.

## 7. Appréciation scientifique corrigée

La factorisation reste très importante pour notre programme, car elle ferme complètement l'horizon infini.

Mais ses ingrédients sont largement classiques :
- observabilité des graphes / machines de Moore ;
- graphes fonctionnels = cycles avec arbres de préimages ;
- mots et colliers primitifs.

Même si la formule générale s'avère absente de la littérature, elle ressemble désormais davantage à une extension combinatoire propre et utile qu'à une nouvelle théorie autonome.

La partie la plus susceptible d'être originale reste l'horizon fini et les incompatibilités transitoires.

## 8. Frontière de recherche recommandée

Revenir au défaut fini

chi_obs(T,∞;z) - chi_obs(T,L;z)

et chercher une caractérisation structurelle des obstructions qui :
- ne sont pas des collisions de fibres ;
- ne sont pas des collisions périodiques ;
- disparaissent lorsque L augmente.

La classification exacte (m,L)=(2,3) et ses 162 incompatibilités transitoires redeviennent alors le laboratoire naturel.

## Références clés

- R. M. Jungers, V. D. Blondel, Observable Graphs, Discrete Applied Mathematics 159 (2011), 981–989.
- D. Laschov, M. Margaliot, G. Even, Observability of Boolean Networks: A Graph-Theoretic Approach, Automatica 49 (2013).
- C. Nicaud, Average State Complexity of Operations on Unary Automata, MFCS 1999.
- M. Domaratzki, D. Kisman, J. Shallit, On the Number of Distinct Languages Accepted by Finite Automata with n States, JALC 7 (2002), 469–486.
- L. B. Vieira, C. Budroni, Temporal correlations in the simplest measurement sequences, Quantum 6, 623 (2022).