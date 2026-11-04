# V7 — Polynôme chromatique temporel et factorisation à horizon infini

## ÉTAT ACTUEL

### DÉMONTRÉ — Arrangement temporel

Soit \(X\) fini, \(|X|=N\), \(T:X\to X\), et \(L\ge1\).

Pour chaque paire non ordonnée \(p=\{x,y\}\), \(x\ne y\), définissons le graphe

\[
\Gamma_{p,L}=(X,E_{p,L}),
\]

avec

\[
E_{p,L}
=
\left\{
\{T^t x,T^t y\}:
0\le t<L,\ T^t x\ne T^t y
\right\}.
\]

Pour un corps \(K\), définissons le sous-espace

\[
D_{p,L}(K)
=
\left\{
c\in K^X:
c_u=c_v\quad\forall\{u,v\}\in E_{p,L}
\right\}.
\]

La famille

\[
\mathcal A_{T,L}(K)
=
\{D_{p,L}(K):p\in \tbinom X2\}
\]

est un arrangement de sous-espaces contenus dans le treillis de la braid arrangement.

Une coloration \(c:X\to K\) distingue tous les états en \(L\) observations si et seulement si

\[
c\notin \bigcup_{D\in\mathcal A_{T,L}}D.
\]

La preuve est directe : \(c\in D_{p,L}\) signifie exactement que les deux états de la paire \(p\) produisent la même histoire pendant les \(L\) premiers temps.

---

## DÉMONTRÉ — Codimension intrinsèque

Le sous-espace \(D_{p,L}\) impose seulement des égalités de coordonnées le long des arêtes de \(\Gamma_{p,L}\).

Donc

\[
\dim D_{p,L}
=
\kappa(\Gamma_{p,L}),
\]

où \(\kappa\) est le nombre de composantes connexes du graphe incluant les sommets isolés.

Ainsi

\[
\boxed{
\operatorname{codim}D_{p,L}
=
N-\kappa(\Gamma_{p,L})
=
\operatorname{rank} B(\Gamma_{p,L}),
}
\]

où \(B(\Gamma_{p,L})\) est une matrice d’incidence.

En particulier,

\[
\operatorname{codim}D_{p,L}
\le \min(L,N-1).
\]

Cette formule est indépendante du corps.

---

## DÉMONTRÉ — Polynôme chromatique temporel

Définissons

\[
\chi_{T,L}(q)
\]

comme le nombre d’observations

\[
\pi:X\to[q]
\]

pour lesquelles

\[
x\mapsto
(\pi(x),\pi(Tx),\ldots,\pi(T^{L-1}x))
\]

est injectif.

Alors \(\chi_{T,L}(q)\) est un polynôme en \(q\).

Une formule directe par inclusion-exclusion est

\[
\boxed{
\chi_{T,L}(q)
=
\sum_{J\subseteq \binom X2}
(-1)^{|J|}
q^{\kappa\left(
\bigcup_{p\in J}E_{p,L}
\right)}.
}
\]

Les duplications de sous-espaces peuvent ensuite être quotientées via le treillis d’intersections et sa fonction de Möbius.

Équivalent :

\[
\chi_{T,L}(q)
=
\chi(\mathcal A_{T,L},q),
\]

le polynôme caractéristique de l’arrangement temporel.

Cette existence est un cas particulier de la théorie connue des subspace arrangements embedded in the braid arrangement.

---

## DÉMONTRÉ — Développement en factorielles décroissantes

Soit \(g_{T,L}(k)\) le nombre de partitions de \(X\) en exactement \(k\) blocs qui sont \(L\)-génératrices.

Alors

\[
\boxed{
\chi_{T,L}(q)
=
\sum_{k=1}^N
g_{T,L}(k)\,(q)_k,
}
\]

où

\[
(q)_k=q(q-1)\cdots(q-k+1).
\]

Preuve : toute coloration induit une partition en classes de couleurs. Pour une partition génératrice à \(k\) blocs, il existe exactement \((q)_k\) injections des blocs dans un alphabet de \(q\) couleurs.

Conséquences :

\[
\boxed{
\mathcal M_T(L)
=
\min\{k:g_{T,L}(k)>0\}
=
\min\{q\ge1:\chi_{T,L}(q)>0\}.
}
\]

Et

\[
g_{T,L}(k)\le g_{T,L+1}(k).
\]

Le profil temporel est donc monotone coefficient par coefficient dans la base des factorielles décroissantes.

---

## RÉFUTÉ — Le cas \(q=2\) n’est pas le seul cas linéaire

La conjecture précédente selon laquelle \(q>2\) nécessiterait fondamentalement une union de morceaux affines est trop faible.

Les ensembles de mauvaises colorations sont définis par

\[
c_u=c_v,
\]

donc ils sont des sous-espaces linéaires sur \(\mathbb F_q\) pour tout corps fini.

Le caractère spécial de \(q=2\) apparaît seulement lorsqu’on transforme une contrainte forcée

\[
c_u\ne c_v
\]

en une équation unique :

\[
c_u+c_v=1.
\]

Pour \(q>2\), le complément de l’hyperplan \(c_u=c_v\) n’est plus un unique hyperplan affine.

Mais l’arrangement des mauvaises colorations reste linéaire pour tout \(q\).

---

## DÉMONTRÉ — Quotient canonique

Tous les \(D_{p,L}\) contiennent la droite des colorations constantes

\[
K\mathbf 1.
\]

On peut donc quotienter canoniquement :

\[
\overline V=K^X/K\mathbf1.
\]

L’arrangement descend dans \(\overline V\), sans changement des codimensions.

La construction est invariante par toute conjugaison

\[
T'=hTh^{-1},
\]

car \(h\) ne fait que permuter les coordonnées et les orbites de paires.

---

# FACTORISATION À HORIZON INFINI

Notons

\[
d_y=|T^{-1}(y)|.
\]

Soit \(\operatorname{Per}(T)\) l’ensemble des sommets périodiques.

Soit \(c_d(T)\) le nombre de cycles de longueur exactement \(d\).

Enfin,

\[
P_d(q)
=
\frac1d
\sum_{e\mid d}\mu(e)q^{d/e}
\]

est le nombre de colliers primitifs de longueur \(d\) sur \(q\) couleurs.

Pour \(a\in\mathbb Z\), posons

\[
(a)_r=a(a-1)\cdots(a-r+1).
\]

### THÉORÈME

Le nombre \(\chi_{T,\infty}(q)\) d’observations à \(q\) couleurs qui distinguent tous les états à horizon infini vaut

\[
\boxed{
\chi_{T,\infty}(q)
=
\left[
\prod_{d\ge1}
d^{c_d(T)}
\bigl(P_d(q)\bigr)_{c_d(T)}
\right]
\left[
\prod_{y\in\operatorname{Per}(T)}
(q-1)_{d_y-1}
\right]
\left[
\prod_{y\notin\operatorname{Per}(T)}
(q)_{d_y}
\right].
}
\]

## Preuve

Une coloration est génératrice à horizon infini si et seulement si les trois conditions suivantes sont satisfaites.

### 1. Fibres

Pour tout \(y\),

\[
c|_{T^{-1}(y)}
\]

doit être injective.

Sinon deux états ayant la même image possèdent exactement le même futur après un pas.

Réciproquement, si deux trajectoires fusionnent pour la première fois au temps \(j\), les deux états au temps \(j-1\) sont deux antécédents distincts du même sommet et sont donc séparés par cette condition.

### 2. Cycles primitifs

Sur chaque cycle de longueur \(d\), le mot cyclique des couleurs doit avoir période primitive exactement \(d\).

Sinon deux phases du même cycle produisent la même histoire infinie.

### 3. Cycles de même longueur

Deux cycles distincts de longueur \(d\) doivent recevoir deux colliers primitifs différents.

Des cycles de longueurs différentes ne peuvent produire la même suite périodique si leurs mots sont primitifs, car leur période minimale serait différente.

Ces trois conditions sont aussi suffisantes.

Si deux trajectoires ne fusionnent jamais, elles atteignent des cycles. Les conditions 2 et 3 séparent alors leurs queues périodiques.

## Comptage

Pour les cycles de longueur \(d\), il existe \(P_d(q)\) colliers primitifs.

Pour les \(c_d\) cycles distincts :

\[
(P_d(q))_{c_d}
\]

choix injectifs de colliers, et

\[
d^{c_d}
\]

choix de phases.

Une fois les couleurs périodiques fixées :

- si \(y\) est périodique, un antécédent périodique possède déjà une couleur fixée, donc ses \(d_y-1\) autres antécédents ont
  \[
  (q-1)_{d_y-1}
  \]
  choix ;

- si \(y\) n’est pas périodique, ses \(d_y\) antécédents ont
  \[
  (q)_{d_y}
  \]
  choix.

Les fibres \(T^{-1}(y)\) étant disjointes, les facteurs se multiplient.

---

## COROLLAIRE — formule de \(m_\infty\)

La factorisation donne immédiatement

\[
\chi_{T,\infty}(q)>0
\]

si et seulement si

\[
q\ge \max_y d_y=\Delta(T)
\]

et

\[
P_d(q)\ge c_d(T)
\quad\forall d.
\]

Donc

\[
\boxed{
m_\infty(T)
=
\min\left\{
q:
q\ge\Delta(T),
\quad
c_d(T)\le P_d(q)\ \forall d
\right\}.
}
\]

La formule antérieure de \(m_\infty\) devient donc un corollaire d’un théorème de comptage plus fort.

---

## DÉMONTRÉ — Stabilisation du polynôme

Pour \(N>1\), toute partition génératrice possède au moins deux blocs.

Le raffinement des partitions doit être strict à chaque étape tant que la partition discrète n’est pas atteinte.

Ainsi toute partition génératrice infinie distingue déjà tous les états en au plus

\[
N-1
\]

observations.

Donc

\[
\boxed{
\chi_{T,L}(q)=\chi_{T,\infty}(q)
\qquad
\forall L\ge N-1.
}
\]

Pour le seuil minimal seul, la borne plus précise reste

\[
\mathcal M_T(L)=m_\infty(T)
\]

dès

\[
L\ge N-m_\infty(T)+1.
\]

---

# EXEMPLE — première obstruction transitoire à 6 états

Considérons

\[
T=(1,0,0,2,3,3).
\]

Son profil commence par

\[
\mathcal M_T=(6,3,3,2,\ldots).
\]

Les premiers polynômes sont :

\[
\chi_{T,1}(q)
=
(q)_6,
\]

\[
\chi_{T,2}(q)
=
q(q-1)(q-2)^2(q^2+2q-5),
\]

\[
\chi_{T,3}(q)
=
q(q-1)^2(q-2)(q^2+q+2),
\]

puis

\[
\boxed{
\chi_{T,4}(q)
=
\chi_{T,\infty}(q)
=
q^3(q-1)^3.
}
\]

Ainsi

\[
\chi_{T,3}(2)=0,
\]

mais

\[
\chi_{T,3}(3)=168,
\]

et

\[
\chi_{T,3}(4)=1584.
\]

La première obstruction globale est donc spécifiquement une obstruction de faible alphabet et de faible horizon ; elle disparaît à \(L=4\).

Les deux premières obstructions globales non isomorphes à six états ont exactement le même polynôme

\[
q(q-1)^2(q-2)(q^2+q+2)
\]

à horizon 3.

C’est plus fort que leur équivalence affine binaire déjà observée.

---

# CALCUL EXACT

La factorisation infinie a été comparée à l’énumération directe :

- exhaustivement pour toutes les endofonctions jusqu’à \(N=5\) ;
- pour \(q=1,2,3\).

À \(N=5\), cela représente les 3125 applications \(T:[5]\to[5]\).

Aucun contre-exemple n’a été trouvé.

Le calcul n’est pas utilisé comme preuve du théorème, mais comme audit indépendant.

---

# COMPLEXITÉ — résultat simple

Pour décider

\[
\mathcal M_T(L)\le m,
\]

on a nécessairement

\[
N\le m^L.
\]

Si cette condition échoue, on répond immédiatement NON.

Sinon on peut tester toutes les \(m^N\) observations.

Ainsi le problème est FPT pour le paramètre combiné \((m,L)\), avec une borne brute

\[
m^{m^L}\operatorname{poly}(N).
\]

Aucune NP-complétude n’est revendiquée ici.

---

# LIEN AVEC LA LITTÉRATURE

CONNU DANS LA LITTÉRATURE :

- les arrangements de sous-espaces ;
- les arrangements inclus dans la braid arrangement ;
- leur polynôme caractéristique ;
- l’interprétation de ces polynômes par des colorations généralisées ;
- les graphes de paires en observabilité.

Sources importantes :

1. Andreas Blass, Bruce E. Sagan, "Characteristic and Ehrhart Polynomials", Journal of Algebraic Combinatorics 7 (1998), 115–126.
2. Matthew Miller, Max Wakefield, "Edge Colored Hypergraphic Arrangements", Pure and Applied Mathematics Quarterly 8(3), 2012; arXiv:0903.4221.
3. Christos Athanasiadis, "Characteristic Polynomials of Subspace Arrangements and Finite Fields", Advances in Mathematics 122 (1996), 193–233.
4. R. M. Jungers, V. D. Blondel, "Observable Graphs", Discrete Applied Mathematics 159 (2011), 981–989.
5. Kuize Zhang, "A survey on observability of Boolean control networks", Control Theory and Technology 21 (2023), 115–147.

INDÉTERMINÉ :

Je n’ai pas retrouvé dans cette recherche ciblée la spécialisation exacte

\[
(T,L)\mapsto \mathcal A_{T,L}
\]

construite à partir des orbites synchrones de paires, ni la factorisation fermée de

\[
\chi_{T,\infty}(q)
\]

ci-dessus pour une endofonction finie arbitraire.

Cela ne constitue pas une preuve de nouveauté.

---

# CE QUI A RÉELLEMENT CHANGÉ

Le problème n’est plus naturellement "binaire puis q-aire".

Il possède directement un objet universel :

\[
\boxed{
\mathcal A_{T,L}
}
\]

l’arrangement temporel de sous-espaces.

Le profil

\[
\mathcal M_T(L)
\]

est seulement le premier entier où son polynôme de colorations devient positif.

Ainsi la quantité plus riche est

\[
\boxed{
\chi_{T,L}(q).
}
\]

Elle encode simultanément :

- le nombre de colorations génératrices ;
- le minimum d’alphabet ;
- les partitions génératrices par nombre de blocs ;
- la disparition progressive des obstructions transitoires ;
- la stabilisation vers l’horizon infini.

La factorisation de \(\chi_{T,\infty}\) redonne \(m_\infty\) comme simple seuil de positivité.

---

# PROCHAINE QUESTION

Étudier la famille de polynômes

\[
L\longmapsto\chi_{T,L}(q)
\]

comme invariant dynamique.

Questions prioritaires :

1. quelles suites de polynômes peuvent apparaître ?
2. quelle information sur \(T\) est déterminée par la suite complète ?
3. quand deux dynamiques non conjuguées ont-elles le même profil polynomial ?
4. quelles propriétés de l’arrangement temporel permettent une factorisation ?
5. peut-on caractériser les classes de dynamiques pour lesquelles \(\chi_{T,L}\) est complètement factorisé pour tout \(L\) ?