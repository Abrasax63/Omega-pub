# V8 — Factorisation exacte du polynôme d’observabilité à horizon infini

## 1. Cadre

Soit \(X\) un ensemble fini non vide et

\[
T:X\to X.
\]

Pour un alphabet de \(m\) symboles, une observation

\[
c:X\to[m]
\]

est dite génératrice à horizon infini lorsque

\[
x\longmapsto
(c(x),c(Tx),c(T^2x),\ldots)
\]

est injective.

On note

\[
\chi^{\mathrm{obs}}_{T,\infty}(m)
\]

le nombre de telles observations.

Le résultat principal de cette note est une factorisation fermée de ce polynôme.

---

## 2. Notations

Pour \(y\in X\), poser

\[
d_y=|T^{-1}(y)|.
\]

Soit \(\operatorname{Per}(T)\) l’ensemble des points périodiques.

Pour \(r\ge1\), soit

\[
c_r(T)
\]

le nombre de cycles de période minimale exactement \(r\).

Définissons le polynôme des mots primitifs

\[
Q_r(z)
=
\sum_{e\mid r}
\mu(e)\,z^{r/e}.
\]

Pour un entier \(m\ge1\),

\[
Q_r(m)
\]

est le nombre de mots de longueur \(r\) sur \(m\) symboles ayant période minimale exactement \(r\).

Le nombre de colliers primitifs est

\[
P_r(m)=\frac{Q_r(m)}r.
\]

Enfin, on écrit

\[
(z)_k=z(z-1)\cdots(z-k+1)
\]

et

\[
(z-1)_k=(z-1)(z-2)\cdots(z-k).
\]

---

## 3. Théorème de factorisation

### THÉORÈME — DÉMONTRÉ

Pour toute endofonction finie \(T:X\to X\),

\[
\boxed{
\chi^{\mathrm{obs}}_{T,\infty}(z)
=
\left[
\prod_{y\notin\operatorname{Per}(T)}
(z)_{d_y}
\right]
\left[
\prod_{y\in\operatorname{Per}(T)}
(z-1)_{d_y-1}
\right]
\left[
\prod_{r\ge1}
\prod_{j=0}^{c_r(T)-1}
\bigl(Q_r(z)-jr\bigr)
\right].
}
\]

Chaque facteur possède une interprétation dynamique indépendante :

1. les fibres au-dessus des points non périodiques ;
2. les prédécesseurs transitoires des points périodiques ;
3. les mots primitifs portés par les cycles.

---

## 4. Lemme de caractérisation

### LEMME — DÉMONTRÉ

Une observation \(c:X\to[m]\) est génératrice à horizon infini si et seulement si les deux conditions suivantes sont satisfaites.

### Condition F — fibres

Pour tout \(y\in X\),

\[
c|_{T^{-1}(y)}
\]

est injective.

### Condition P — périodicité

Les itinéraires symboliques infinis des points périodiques sont deux à deux distincts.

La condition P équivaut à :

- sur chaque cycle de longueur \(r\), le mot cyclique porté par les couleurs est primitif ;
- deux cycles distincts de même longueur ne portent pas deux rotations du même mot primitif.

### Preuve de la nécessité

Si \(u\neq v\) vérifient

\[
Tu=Tv
\]

et

\[
c(u)=c(v),
\]

alors leurs histoires symboliques sont identiques pour toujours. Donc F est nécessaire.

La condition P est immédiatement nécessaire puisque les points périodiques doivent être distingués.

### Preuve de la suffisance

Supposons F et P.

Si deux états distincts \(x,z\) avaient la même histoire symbolique infinie, leurs orbites finiraient sur des cycles.

À temps assez grand, les deux états sont périodiques. L’égalité des suites symboliques et P imposent alors qu’ils soient sur le même cycle et à la même phase. Il existe donc un temps \(k\ge1\) tel que

\[
T^k x=T^k z.
\]

Choisissons le plus petit tel \(k\).

Alors

\[
T^{k-1}x\neq T^{k-1}z
\]

mais

\[
T(T^{k-1}x)=T(T^{k-1}z).
\]

Comme les histoires symboliques initiales sont égales,

\[
c(T^{k-1}x)=c(T^{k-1}z),
\]

ce qui contredit l’injectivité de \(c\) sur cette fibre.

Donc l’observation est génératrice.

---

## 5. Comptage des parties transitoires

Les fibres

\[
T^{-1}(y),
\qquad y\in X,
\]

forment une partition de \(X\).

### Si \(y\) n’est pas périodique

Aucun élément périodique n’appartient à \(T^{-1}(y)\).

Les \(d_y\) couleurs doivent être distinctes :

\[
(z)_{d_y}.
\]

### Si \(y\) est périodique

La fibre contient exactement un prédécesseur périodique : le sommet précédent sur son cycle.

Sa couleur est déjà fixée par le coloriage du cycle.

Les \(d_y-1\) prédécesseurs transitoires doivent :

- avoir des couleurs deux à deux différentes ;
- éviter la couleur du prédécesseur périodique.

Nombre de choix :

\[
(z-1)_{d_y-1}.
\]

Ces choix sont indépendants entre fibres.

---

## 6. Comptage des cycles

Considérons les \(c_r\) cycles de longueur \(r\).

Un cycle doit recevoir un mot primitif de longueur \(r\).

Il existe

\[
Q_r(z)
\]

mots primitifs.

Pour le premier cycle :

\[
Q_r(z)
\]

choix.

Une fois un mot choisi, ses \(r\) rotations sont interdites aux autres cycles de même longueur.

Pour le second :

\[
Q_r(z)-r.
\]

Pour le troisième :

\[
Q_r(z)-2r.
\]

Ainsi le facteur exact est

\[
\boxed{
\prod_{j=0}^{c_r-1}
(Q_r(z)-jr).
}
\]

Équivalent :

\[
r^{c_r}\,(P_r(z))_{c_r}.
\]

La première écriture montre immédiatement que le facteur possède des coefficients entiers.

---

## 7. Corollaire : formule de \(m_\infty(T)\)

### COROLLAIRE — DÉMONTRÉ

Le premier entier \(m\) pour lequel

\[
\chi^{\mathrm{obs}}_{T,\infty}(m)>0
\]

est

\[
\boxed{
m_\infty(T)
=
\min\left\{
m:
m\ge\Delta(T),
\quad
c_r(T)\le P_r(m)
\ \forall r
\right\}.
}
\]

En effet :

- les facteurs de fibres sont positifs exactement lorsque
  \[
  m\ge d_y
  \quad\forall y,
  \]
  soit
  \[
  m\ge\Delta(T);
  \]

- le facteur associé aux cycles de longueur \(r\) est positif exactement lorsque
  \[
  Q_r(m)\ge r\,c_r,
  \]
  soit
  \[
  P_r(m)\ge c_r.
  \]

L’ancienne formule de \(m_\infty\) devient donc un corollaire immédiat d’une identité de comptage plus forte.

---

## 8. Exemples

### Identité sur \(N\) états

Tous les sommets sont des points fixes :

\[
c_1=N.
\]

Donc

\[
\boxed{
\chi^{\mathrm{obs}}_{\mathrm{id},\infty}(z)
=
(z)_N.
}
\]

### Application constante sur \(N\) états

Le point fixe a indégrée \(N\).

Le facteur périodique donne \(z\) et la fibre du point fixe donne

\[
(z-1)_{N-1}.
\]

Donc

\[
\boxed{
\chi^{\mathrm{obs}}_{T,\infty}(z)
=
(z)_N.
}
\]

L’identité et la dynamique constante ont donc le même polynôme infini, bien que leurs graphes fonctionnels soient opposés.

### Cycle unique de longueur \(N\)

Il n’y a aucun prédécesseur transitoire.

Donc

\[
\boxed{
\chi^{\mathrm{obs}}_{C_N,\infty}(z)
=
Q_N(z)
=
\sum_{e\mid N}\mu(e)z^{N/e}.
}
\]

### Système \(T=(0,0,3,2)\)

Un point fixe avec une feuille et un 2-cycle.

La formule donne

\[
\boxed{
\chi^{\mathrm{obs}}_{T,\infty}(z)
=
z^2(z-1)^2.
}
\]

À horizon \(L=2\), on avait au contraire

\[
\chi^{\mathrm{obs}}_{T,2}(z)
=
z(z-1)(z-2)(z+1).
\]

Ainsi les obstructions transitoires disparaissent réellement lorsque l’horizon devient infini.

### Les deux obstructions globales F6-A et F6-B

À horizon \(L=3\), les deux avaient le même polynôme :

\[
z(z-2)(z-1)^2(z^2+z+2).
\]

À horizon infini, la factorisation donne pour les deux :

\[
\boxed{
z^3(z-1)^3.
}
\]

---

## 9. Séparation exacte du transitoire et du périodique

Le théorème établit une décomposition conceptuelle nette :

\[
\boxed{
\chi^{\mathrm{obs}}_{T,\infty}
=
\text{facteurs de fibres}
\times
\text{facteurs de cycles primitifs}.
}
\]

Les arbres attachés aux cycles n’interviennent à horizon infini que par les tailles des fibres

\[
d_y.
\]

Leur géométrie globale — profondeur, forme des branches, intersections transitoires — disparaît du comptage.

À horizon fini, au contraire, ces détails géométriques déterminent les obstructions transitoires.

Ceci donne une formulation rigoureuse de la transition :

\[
\text{géométrie transitoire détaillée}
\quad\longrightarrow\quad
\text{ramification locale + périodicité}
\]

quand

\[
L\to\infty.
\]

---

## 10. Nouvel invariant de stabilisation des paires

Pour une paire non diagonale \(p=\{x,y\}\), suivre son orbite sous

\[
F(p)=\{Tx,Ty\},
\]

avec absorption sur la diagonale.

Définissons \(s(p)\) comme le nombre de paires non diagonales distinctes visitées avant :

- fusion sur la diagonale, ou
- première répétition d’une paire.

Posons

\[
\sigma(T)=\max_{p}s(p).
\]

### THÉORÈME — DÉMONTRÉ

Le système d’arrangements diagonaux et donc le polynôme d’observabilité sont stabilisés pour

\[
\boxed{
L\ge\sigma(T).
}
\]

En particulier,

\[
\sigma(T)\le\binom{|X|}{2}.
\]

Donc

\[
\boxed{
\chi^{\mathrm{obs}}_{T,L}
=
\chi^{\mathrm{obs}}_{T,\infty}
\qquad
L\ge\sigma(T).
}
\]

Cette borne concerne le polynôme entier, et non seulement le premier alphabet admissible \(m_\infty\).

---

## 11. Premier coefficient dynamique

Écrivons

\[
N=|X|.
\]

Pour \(L\ge2\), le coefficient de \(z^{N-1}\) dans

\[
\chi^{\mathrm{obs}}_{T,L}(z)
\]

est

\[
\boxed{
-
\left[
\sum_{y\in X}\binom{d_y}{2}
+
\binom{c_1}{2}
+
c_2
\right].
}
\]

### Interprétation

Les sous-espaces interdits de codimension 1 correspondent exactement aux paires \(\{u,v\}\) telles que leur orbite de paire ne quitte jamais cette paire avant fusion :

1. \(Tu=Tv\) : deux frères dans une même fibre ;
2. \(u,v\) sont deux points fixes ;
3. \(u,v\) forment un 2-cycle.

Le nombre de telles paires est donc :

\[
\sum_y\binom{d_y}{2}
+
\binom{c_1}{2}
+
c_2.
\]

Pour \(L=1\), toutes les paires sont de codimension 1 et le coefficient vaut

\[
-\binom N2.
\]

---

## 12. Audit bibliographique

### CONNU DANS LA LITTÉRATURE

La décomposition d’un graphe fonctionnel fini en cycles munis d’arbres enracinés est classique.

Les mots primitifs, colliers et formules de Möbius sont classiques.

Les arrangements diagonaux et leurs polynômes caractéristiques/chromatiques généralisés sont également connus.

### RECHERCHE CIBLÉE

Des recherches ont été effectuées autour de :

- functional digraph coloring primitive necklaces;
- finite dynamical system generating partitions;
- endofunction observability primitive words;
- functional graph chromatic polynomial primitive necklace.

Aucune source consultée n’a présenté la factorisation exacte ci-dessus du nombre d’observations génératrices d’une endofonction arbitraire.

### STATUT

\[
\boxed{\text{INDÉTERMINÉ}}
\]

pour la nouveauté.

L’absence de résultat trouvé par recherche ciblée n’est pas une preuve d’absence dans la littérature.

---

## 13. Ce qui a réellement changé

Avant V8, on connaissait uniquement le seuil

\[
m_\infty(T).
\]

Après V8, on possède le comptage exact

\[
\chi^{\mathrm{obs}}_{T,\infty}(m)
\]

pour chaque alphabet \(m\).

La formule du seuil devient un corollaire.

Le rôle respectif des arbres et des cycles est désormais explicite et factorisé.

---

## 14. Prochaine question

Le problème fini peut maintenant être reformulé comme un défaut multiplicatif :

\[
R_{T,L}(z)
=
\frac{
\chi^{\mathrm{obs}}_{T,L}(z)
}{
\chi^{\mathrm{obs}}_{T,\infty}(z)
},
\]

lorsque cette écriture a un sens algébrique approprié.

Il faut déterminer si une normalisation polynomialement naturelle mesure exactement la contribution des incompatibilités transitoires.

Une autre voie consiste à étudier

\[
\chi^{\mathrm{obs}}_{T,\infty}(z)
-
\chi^{\mathrm{obs}}_{T,L}(z),
\]

qui compte, aux entiers positifs, les observations qui deviennent génératrices seulement après l’horizon \(L\).

Cette différence pourrait fournir la mesure quantitative du « coût du transitoire » recherchée depuis V5.