# Audit mathématique et bibliographique du profil d’observabilité temporelle des dynamiques finies

## Résultat exécutif

Le programme mathématique étudié est centré sur le profil

\[
\mathcal M_T(L)
=
\min_{\pi:X\to[m]}
m
\quad\text{sous la contrainte que}\quad
S_L^\pi(x)=\bigl(\pi(x),\pi(Tx),\ldots,\pi(T^{L-1}x)\bigr)
\]

soit injectif sur un ensemble fini \(X\).

Deux résultats sont désormais suffisamment propres pour être isolés.

**Résultat A — horizon infini.** Pour toute application déterministe finie \(T:X\to X\),

\[
m_\infty(T)
=
\min\left\{
m:
m\ge \Delta(T),
\quad
c_d(T)\le P_d(m)\ \text{pour tout }d\ge1
\right\},
\]

où

\[
\Delta(T)=\max_{y\in X}|T^{-1}(y)|,
\]

\(c_d(T)\) est le nombre de cycles de période minimale \(d\) du graphe fonctionnel de \(T\), et

\[
P_d(m)=\frac1d\sum_{e\mid d}\mu(e)m^{d/e}
\]

est le nombre de colliers primitifs de longueur \(d\) sur un alphabet de \(m\) symboles.

**Résultat B — horizon fini.** Le profil \(\mathcal M_T(L)\) est exactement le plus petit \(m\) tel que le graphe fonctionnel de \(T\) s’immerge injectivement comme sous-graphe orienté dans le graphe de de Bruijn \(B(m,L)\).

Ces deux résultats ont été audités mathématiquement. Le résultat A a en plus été vérifié exhaustivement sur toutes les applications \(T:[N]\to[N]\) pour \(N\le6\), soit **50 069 dynamiques** au total, sans contre-exemple.

La recherche bibliographique montre cependant que plusieurs briques conceptuelles sont anciennes : partitions génératrices, générateurs unilatéraux, observabilité par suites de sorties, graphes observables, optimisation du nombre de couleurs/senseurs, contraintes de cycles périodiques et graphes de de Bruijn. La nouveauté éventuelle ne peut donc pas être revendiquée au niveau de l’idée générale « observer plus longtemps permet d’utiliser moins de symboles ».

En revanche, je n’ai pas retrouvé, dans les sources examinées, la **caractérisation fermée exacte du nombre minimal de symboles pour une endofonction finie arbitraire par la seule combinaison \(\Delta(T)\) + nombre de colliers primitifs**, ni la présentation explicite du profil \(\mathcal M_T(L)\) comme coût minimal d’alphabet égal au coût d’immersion du graphe fonctionnel dans \(B(m,L)\). Cela reste un **candidat à nouveauté**, pas une revendication de nouveauté établie.

---

## 1. Définitions

Soit \(X\) un ensemble fini et \(T:X\to X\) une application déterministe.

Une observation à \(m\) symboles est une application

\[
\pi:X\to[m]=\{0,\ldots,m-1\}.
\]

Pour une profondeur temporelle \(L\ge1\), on définit la signature

\[
S_L^\pi(x)=
\left(
\pi(x),\pi(Tx),\ldots,\pi(T^{L-1}x)
\right).
\]

Le **profil d’observabilité temporelle** est

\[
\boxed{
\mathcal M_T(L)
=
\min\left\{
m:\exists \pi:X\to[m]\text{ telle que }S_L^\pi
\text{ soit injective}
\right\}.
}
\]

Le nombre minimal à horizon infini est

\[
\boxed{
m_\infty(T)
=
\min\left\{
m:\exists \pi:X\to[m]\text{ telle que }
x\mapsto(\pi(T^n x))_{n\ge0}
\text{ soit injective}
\right\}.
}
\]

Dans le vocabulaire classique de la dynamique symbolique, une telle partition est un **générateur unilatéral** (one-sided generator) dans le cadre fini.

---

## 2. Théorème à horizon infini

### Théorème

Soit \(T:X\to X\) une application sur un ensemble fini.

Notons

\[
\Delta(T)=\max_{y\in X}|T^{-1}(y)|
\]

et \(c_d(T)\) le nombre de cycles de période minimale exactement \(d\).

Notons enfin

\[
P_d(m)=
\frac1d
\sum_{e\mid d}\mu(e)m^{d/e},
\]

le nombre de colliers primitifs de longueur \(d\) sur \(m\) symboles.

Alors

\[
\boxed{
m_\infty(T)=
\min\left\{
m:
m\ge\Delta(T)
\text{ et }
c_d(T)\le P_d(m)\ \forall d\ge1
\right\}.
}
\]

### Nécessité : ramification

Supposons que deux états distincts \(x,z\) satisfassent

\[
T(x)=T(z).
\]

À partir de l’instant 1, leurs trajectoires microscopiques coïncident exactement :

\[
T^n(x)=T^n(z),\qquad n\ge1.
\]

Si leurs histoires observées doivent être différentes, il est donc nécessaire que

\[
\pi(x)\neq \pi(z).
\]

Ainsi \(\pi\) doit être injective sur chaque fibre \(T^{-1}(y)\), ce qui impose

\[
m\ge\Delta(T).
\]

### Nécessité : cycles périodiques

Sur un cycle de période minimale \(d\), les \(d\) phases doivent produire \(d\) suites périodiques distinctes.

Le mot cyclique de longueur \(d\) associé à ce cycle doit donc avoir période primitive exactement \(d\). Sinon, deux phases du même cycle auraient la même histoire infinie.

Deux cycles distincts de période \(d\) doivent également recevoir deux colliers primitifs différents : s’ils recevaient le même collier à rotation près, il existerait deux phases, une sur chaque cycle, donnant exactement la même suite observée.

Il faut donc

\[
c_d(T)\le P_d(m).
\]

### Suffisance

Supposons maintenant

\[
m\ge\Delta(T)
\]

et

\[
c_d(T)\le P_d(m)\quad\forall d.
\]

Pour chaque cycle de période \(d\), choisissons un collier primitif distinct de longueur \(d\) et affectons ses symboles aux sommets du cycle.

Ensuite, traitons les sommets transitoires. Pour chaque \(y\in X\), attribuons des symboles distincts aux éléments de la fibre \(T^{-1}(y)\). C’est toujours possible parce que

\[
|T^{-1}(y)|\le \Delta(T)\le m.
\]

Lorsque l’un des antécédents appartient déjà à un cycle et possède donc un symbole fixé, on réserve ce symbole à cet antécédent et on utilise des symboles différents pour les autres éléments de la fibre.

Supposons par contradiction que deux états distincts \(x,z\) aient la même histoire observée infinie.

Comme \(X\) est fini, leurs trajectoires atteignent chacune un cycle. Les codages primitifs et distincts des cycles impliquent qu’à temps suffisamment grand, les deux trajectoires doivent avoir atteint le même cycle, à la même phase. Elles finissent donc par fusionner.

Soit \(j\ge1\) le plus petit entier tel que

\[
T^j x=T^j z.
\]

Alors

\[
T^{j-1}x\neq T^{j-1}z
\]

sont deux éléments distincts de la même fibre de \(T\). Comme les histoires observées de \(x\) et \(z\) sont égales, ces deux états portent le même symbole, contradiction avec l’injectivité de \(\pi\) sur chaque fibre.

Le codage infini est donc injectif.

---

## 3. Vérification exhaustive

Le théorème a été testé sur **toutes** les applications \(T:[N]\to[N]\) pour \(N\le6\).

| \(N\) | Nombre d’applications \(N^N\) | Contre-exemples |
|---:|---:|---:|
| 1 | 1 | 0 |
| 2 | 4 | 0 |
| 3 | 27 | 0 |
| 4 | 256 | 0 |
| 5 | 3 125 | 0 |
| 6 | 46 656 | 0 |
| **Total** | **50 069** | **0** |

Le calcul ne remplace pas la preuve, mais constitue un audit indépendant utile.

Un script reproductible est joint au dossier.

---

## 4. Théorème de de Bruijn à horizon fini

Notons \(G_T\) le graphe fonctionnel orienté de \(T\) : chaque sommet \(x\) possède l’unique arête

\[
x\to T(x).
\]

Notons \(B(m,L)\) le graphe de de Bruijn orienté dont les sommets sont les mots

\[
a_0a_1\ldots a_{L-1}\in[m]^L,
\]

avec une arête

\[
a_0a_1\ldots a_{L-1}
\longrightarrow
a_1a_2\ldots a_{L-1}b
\]

pour chaque \(b\in[m]\).

### Théorème

\[
\boxed{
\mathcal M_T(L)
=
\min\left\{
m:
G_T\hookrightarrow B(m,L)
\right\},
}
\]

où \(\hookrightarrow\) désigne une immersion injective respectant les arêtes.

### Preuve : observation \(\Rightarrow\) immersion

Si \(S_L^\pi\) est injective, posons

\[
\Phi(x)=S_L^\pi(x).
\]

Alors

\[
\Phi(Tx)
=
\left(
\pi(Tx),\ldots,\pi(T^Lx)
\right),
\]

qui est obtenu à partir de \(\Phi(x)\) en supprimant le premier symbole et en ajoutant un nouveau symbole à droite.

Donc

\[
\Phi(x)\to\Phi(Tx)
\]

est une arête de \(B(m,L)\).

Comme \(S_L^\pi\) est injective, \(\Phi\) est une immersion injective du graphe fonctionnel dans le graphe de de Bruijn.

### Preuve : immersion \(\Rightarrow\) observation

Réciproquement, supposons

\[
\Phi:G_T\hookrightarrow B(m,L).
\]

Définissons \(\pi(x)\) comme le premier symbole du mot \(\Phi(x)\).

La contrainte d’adjacence dans le graphe de de Bruijn force alors successivement

\[
\Phi(x)
=
\left(
\pi(x),\pi(Tx),\ldots,\pi(T^{L-1}x)
\right).
\]

Ainsi \(S_L^\pi=\Phi\), qui est injective.

---

## 5. Bornes immédiates à horizon fini

### Borne de cardinalité

Comme \(B(m,L)\) possède \(m^L\) sommets,

\[
|X|\le m^L.
\]

Donc

\[
\boxed{
\mathcal M_T(L)\ge |X|^{1/L}.
}
\]

### Borne de ramification

Le graphe \(B(m,L)\) a degré entrant \(m\). Donc

\[
\boxed{
\mathcal M_T(L)\ge\Delta(T).
}
\]

### Borne multi-pas

Si plusieurs états fusionnent après exactement \(t\) pas, ils doivent pouvoir être distingués par leurs \(t\) premiers symboles.

Ainsi, pour tout \(1\le t\le L\),

\[
|T^{-t}(y)|\le m^t.
\]

Donc

\[
\boxed{
\mathcal M_T(L)
\ge
\max_{1\le t\le L}
\max_{y\in X}
|T^{-t}(y)|^{1/t}.
}
\]

Cette borne sépare clairement deux phénomènes :

- la quantité totale d’états à coder ;
- la vitesse à laquelle la dynamique détruit l’information par fusion.

---

## 6. Exemples discriminants

### Identité

Si

\[
T=\operatorname{id}_X,
\]

alors

\[
S_L^\pi(x)
=
(\pi(x),\ldots,\pi(x)).
\]

Aucune profondeur temporelle n’ajoute d’information.

Donc

\[
\boxed{\mathcal M_T(L)=|X|\quad\forall L.}
\]

### Étoile

Si tous les états vont en un pas vers le même état,

\[
T(x)=y_0,
\]

alors

\[
\Delta(T)=|X|.
\]

Donc

\[
\boxed{\mathcal M_T(L)=|X|\quad\forall L.}
\]

Ici l’information est détruite immédiatement.

### Chaîne vers un point fixe

Pour

\[
0\to1\to2\to\cdots\to N-1\to N-1,
\]

on a

\[
\Delta(T)=2
\]

et un seul point fixe.

À horizon infini,

\[
\boxed{m_\infty(T)=2.}
\]

Un bit par instant suffit donc asymptotiquement à identifier n’importe lequel des \(N\) états initiaux.

### Permutations

Pour une permutation,

\[
\Delta(T)=1.
\]

Le théorème devient

\[
\boxed{
m_\infty(T)
=
\min\{m:c_d(T)\le P_d(m)\ \forall d\}.
}
\]

L’obstruction ne vient alors plus que de la multiplicité des orbites périodiques.

---

## 7. Ce qui est déjà connu

### 7.1 Partitions génératrices et générateurs unilatéraux

La notion selon laquelle une suite symbolique future doit déterminer l’état initial est classique en dynamique symbolique.

Dans le langage des partitions génératrices, une partition \(\alpha\) est un générateur unilatéral lorsque les raffinements

\[
\bigvee_{n\ge0}T^{-n}\alpha
\]

séparent les points.

Notre \(m_\infty(T)\) est donc une version finie et optimisée de la cardinalité minimale d’un tel générateur.

Conséquence : **le concept général n’est pas nouveau**.

### 7.2 Observabilité des graphes et systèmes finis

La littérature sur les graphes colorés observables et les réseaux booléens étudie exactement la possibilité de reconstruire l’état caché à partir d’une suite de couleurs/sorties.

Des travaux définissent une longueur d’enregistrement nécessaire pour identifier l’état initial et étudient même des problèmes d’assignation de couleurs.

Conséquence : **le rôle de la profondeur temporelle dans l’observabilité n’est pas nouveau**.

### 7.3 Compression symbolique et taille minimale d’alphabet

La littérature sur les générateurs uniformes et les extensions symboliques étudie la cardinalité optimale de l’alphabet nécessaire à un codage sans perte.

Downarowicz a aussi formulé le problème de la « vertical data compression » comme celui du plus petit alphabet permettant un codage symbolique sans perte en temps réel.

Conséquence : **l’idée générale de réduire l’alphabet tout en conservant la dynamique possède des antécédents importants**.

### 7.4 Contraintes périodiques

Les travaux sur les générateurs uniformes montrent explicitement que la structure des orbites périodiques contraint la taille minimale de l’alphabet.

Conséquence : **l’apparition des orbites périodiques comme obstruction n’est pas nouvelle en soi**.

### 7.5 Graphes de de Bruijn

Les graphes de de Bruijn sont classiques en codage symbolique. Des travaux les utilisent pour construire des séquences d’identification et pour empaqueter des cycles de longueur fixée, notamment dans des problèmes d’identification de robots par suites de couleurs.

Conséquence : **le mécanisme de fenêtres symboliques et de cycles dans de Bruijn possède des antécédents directs**.

---

## 8. Ce que je n’ai pas retrouvé tel quel

Après des recherches ciblées autour de :

- finite endofunction one-sided generator minimum alphabet;
- observable functional digraph coloring;
- finite deterministic system minimal output alphabet;
- functional digraph embedding de Bruijn;
- primitive necklaces indegree observability;
- minimum alphabet finite-horizon observability;

je n’ai pas retrouvé une source énonçant exactement l’un des deux résultats suivants.

### Candidat 1

\[
\boxed{
m_\infty(T)
=
\min\{m:
m\ge\Delta(T),
\ c_d(T)\le P_d(m)\ \forall d\}
}
\]

pour **toute endofonction finie arbitraire**.

La formule est simple une fois obtenue, donc il est tout à fait possible qu’elle existe dans une littérature différente ou ancienne.

Statut :

\[
\boxed{\text{nouveauté : non confirmée}}
\]

mais

\[
\boxed{\text{aucun antécédent exact retrouvé dans l’audit actuel}}.
\]

### Candidat 2

\[
\boxed{
\mathcal M_T(L)
=
\min\{m:G_T\hookrightarrow B(m,L)\}
}
\]

comme définition/équivalence générale du coût minimal d’alphabet à horizon fini.

Cette équivalence est presque immédiate une fois les deux objets placés côte à côte. Sa valeur pourrait donc être principalement **structurante** plutôt qu’un théorème profond.

Statut :

\[
\boxed{\text{énoncé exact non retrouvé ; proximité forte avec la littérature d’observabilité et de Bruijn}}.
\]

---

## 9. Matrice de nouveauté

| Élément | Déjà connu ? | Évaluation |
|---|---|---|
| Suites de sorties identifiant l’état | oui | classique |
| Générateur unilatéral | oui | classique |
| Optimiser le nombre de symboles/senseurs | oui | littérature observabilité |
| Profondeur temporelle nécessaire | oui | littérature observabilité |
| Cycles périodiques contraignant l’alphabet | oui | connu dans générateurs uniformes |
| Utilisation de de Bruijn pour identifier par fenêtres | oui | connu |
| Profil complet \(L\mapsto\mathcal M_T(L)\) sous alphabet libre | voisinage connu | candidat à une formulation utile |
| Formule exacte \(\Delta+c_d/P_d\) pour endofonctions finies | non retrouvée | **candidat le plus sérieux** |
| Équivalence générale \(G_T\hookrightarrow B(m,L)\) | non retrouvée telle quelle | candidat secondaire |
| Lien avec fermeture \(C_\pi\) et flèche \(A_\pi\) | pas audité complètement | piste pour un second travail |

---

## 10. Lecture conceptuelle correcte

Le résultat ne dit pas que « le temps est de l’information ».

Il établit un principe plus précis :

\[
\boxed{
\text{une dynamique peut transporter dans le temps une information
qui permet de réduire la résolution instantanée nécessaire à l’identification de l’état.}
}
\]

Deux mécanismes empêchent ce transfert :

1. **fusion irréversible** des trajectoires, mesurée localement par la ramification des préimages ;
2. **ambiguïté périodique**, lorsque trop d’orbites périodiques doivent être codées par trop peu de mots primitifs.

Ainsi le temps d’observation ne récupère que l’information que la dynamique a conservée sous une forme décodable.

---

## 11. Programme de publication conseillé

### Article 1 — mathématiques finies

Titre de travail :

**Finite-Horizon Generator Profiles of Deterministic Finite Dynamical Systems**

Contenu :

1. définition de \(\mathcal M_T(L)\) ;
2. équivalence avec immersion dans \(B(m,L)\) ;
3. bornes de cardinalité et de ramification multi-pas ;
4. théorème exact pour \(m_\infty(T)\) ;
5. cas des permutations ;
6. algorithmes et complexité ;
7. classification de familles de graphes fonctionnels ;
8. calculs exhaustifs.

Aucune spéculation sur la physique du temps dans cet article.

### Article 2 — représentation et irréversibilité

Après validation du premier :

\[
(\mathcal M_T(L),C_\pi(h),A_\pi(h))
\]

pour étudier simultanément :

- reconstruction d’état ;
- défaut de fermeture ;
- irréversibilité observable.

Ce deuxième article serait le lieu naturel du lien avec la flèche du temps.

---

## 12. Tests adversariaux restant à faire

Même si le théorème à horizon infini est prouvé, plusieurs questions restent ouvertes.

1. **Complexité exacte de \(\mathcal M_T(L)\).**  
   L’immersion dans un graphe de de Bruijn peut devenir un problème combinatoire difficile.

2. **Borne multi-pas suffisante ou non.**  
   Les contraintes
   \[
   |X|\le m^L,\quad
   |T^{-t}(y)|\le m^t
   \]
   ne sont vraisemblablement pas suffisantes en général à horizon fini : les contraintes globales de cycles et d’intersection des arbres peuvent ajouter des obstructions.

3. **Classification des plateaux du profil.**  
   Déterminer quelles suites décroissantes peuvent apparaître comme
   \[
   L\mapsto\mathcal M_T(L).
   \]

4. **Robustesse au bruit.**  
   Remplacer l’injectivité exacte par une probabilité d’erreur \(\varepsilon\).

5. **Dynamique stochastique.**  
   Remplacer la distinction certaine par une divergence statistique entre lois de sorties.

---

## 13. Conclusion

L’audit ne soutient pas l’idée que nous avons découvert une nouvelle théorie entière de l’observabilité : une grande partie du terrain est classique.

En revanche, il a isolé un noyau beaucoup plus défendable :

\[
\boxed{
m_\infty(T)
=
\min\left\{
m:
m\ge\Delta(T),\
c_d(T)\le P_d(m)\ \forall d
\right\}
}
\]

et

\[
\boxed{
\mathcal M_T(L)
=
\min\left\{
m:
G_T\hookrightarrow B(m,L)
\right\}.
}
\]

Le premier est actuellement le meilleur candidat à un résultat fini exact potentiellement publiable ; le second fournit le langage combinatoire naturel pour tout le profil à horizon fini.

La prochaine étape rationnelle n’est donc pas d’étendre immédiatement vers la cosmologie ou les PDE, mais de faire relire cette caractérisation par un spécialiste de dynamique symbolique / automates / graphes observables et de pousser une recherche bibliographique spécialisée (MathSciNet, zbMATH, citations croisées des travaux sur générateurs unilatéraux et observable graphs).

---

## Sources principales consultées

1. Burguet, D.; Downarowicz, T. **Uniform generators, symbolic extensions with an embedding, and structure of periodic orbits.** arXiv:1705.08829 (2017). https://arxiv.org/abs/1705.08829
2. Downarowicz, T. **Entropy in Dynamical Systems** / travaux sur *vertical data compression* et extensions symboliques. Voir notamment les références autour de la compression symbolique minimale.
3. **Observability Properties of Colored Graphs.** arXiv:1802.03060 (2018). https://arxiv.org/abs/1802.03060
4. **Observable Graphs.** Discrete Applied Mathematics 159 (2011), littérature sur reconstruction d’état depuis une suite de couleurs.
5. **Observability of Boolean Networks: A Graph-Theoretic Approach.** Automatica (2013), reconstruction de l’état initial à partir d’une suite finie de sorties.
6. **Observability analysis and observer design for finite automata.** IET Control Theory & Applications (2013).
7. **Partitioning de Bruijn graphs into fixed-length cycles for robot identification and tracking.** (2016), utilisation directe de cycles de de Bruijn pour identification par fenêtres de couleurs.
8. Littérature classique sur les **one-sided generating partitions** en théorie ergodique et dynamique symbolique.