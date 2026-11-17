# Spectres de défauts des quotients déterministes finis — Itération 1

Date : 17 septembre 2026

Notations : (n=|X|), (m=|Y|), (A_{xy}=1iff T(x)=y),
(C_{xa}=1iff pi(x)=a), (B=C^{\mathsf T}AC),
(E_h=C^{\mathsf T}A^hC=\bar R_h), et
(D(T,\pi)=\{h\geq1:B^h\setminus E_h\neq\varnothing\}).
Tous les produits matriciels sont booléens.

## 1. ÉTAT ACTUEL

### Démontré

- **Statut — DÉMONTRÉ.** Le langage unaire
  (L_D=\{u^h:h\in D(T,\pi)\}) est reconnu exactement par l'automate
  déterministe dont l'état après (h) lettres est
  
  \[
  Z_h=(B^h,A^hC).
  \]

- **Statut — DÉMONTRÉ.** L'automate minimal est le quotient de l'orbite
  accessible de (Z_0=(I_m,C)) par l'équivalence de Myhill–Nerode. Si
  (d_h=\mathbf 1_{\{\Delta_h\neq\varnothing\}}) a prépériode minimale
  (mu_D) et période minimale (p_D), cet automate est exactement une
  chaîne de (mu_D) états suivie d'un cycle de (p_D) états.

- **Statut — DÉMONTRÉ.** Si (K_Q,c_Q) sont un seuil et la cyclicité de la
  suite (B^h), si (d_T) est la profondeur maximale des arbres du graphe
  fonctionnel de (T), et si (p_\pi) est le PPCM des périodes minimales des
  mots de couleurs portés par les cycles de (T), alors
  
  \[
  \mu_D\leq H:=\max(K_Q,d_T),\qquad
  p_D\mid L:=\operatorname{lcm}(c_Q,p_\pi).
  \]

  En particulier, le nombre d'états minimaux est au plus (H+L).

- **Statut — DÉMONTRÉ.** Avec (g) la fonction de Landau,
  
  \[
  H\leq\max(2m^2-3m+2,n-1),\qquad L\leq g(n+m).
  \]

  Si P3 est vraie, alors aucun défaut ne peut subsister après (H-1), donc
  
  \[
  \tau\leq H-1.
  \]

- **Statut — DÉMONTRÉ.** Classification complète des spectres réalisables :
  
  \[
  \boxed{
  D\text{ est réalisable par un }(T,\pi)\text{ fini}
  \iff D\subseteq\mathbb N_{\geq1}\text{ est ultimement périodique et }1\notin D.
  }
  \]

  La suffisance utilise toujours seulement trois macro-états.

- **Statut — DÉMONTRÉ.** Pour le seul spectre (D), la donnée de (pi)
  intervient uniquement par son noyau (la partition de (X)), à renommage des
  classes près. En revanche, (B=Q) seul ne détermine pas (D).

### Connu

- **Statut — CONNU DANS LA LITTÉRATURE.** Un langage unaire régulier est
  représenté par une chaîne suivie d'un cycle ; sa suite caractéristique est
  ultimement périodique. La théorie moderne des automates unaires remonte
  notamment à Chrobak (1986).

- **Statut — CONNU DANS LA LITTÉRATURE.** Les puissances d'une matrice
  booléenne sont ultimement périodiques ; leur période se lit par les
  cyclicité des composantes fortement connexes, et le seuil général
  (2m^2-3m+2) est établi par De Schutter et De Moor.

- **Statut — CONNU DANS LA LITTÉRATURE.** La forte préservation et
  l'élimination des chemins abstraits fallacieux sont étudiées en interprétation
  abstraite. Cela fournit un cadre voisin, mais pas la classification du spectre
  (D) obtenue ici.

### Conjecturé

- **Statut — INDÉTERMINÉ.** Deux macro-états pourraient peut-être suffire à
  réaliser tous les spectres admissibles. La construction démontrée en utilise
  trois ; aucune conjecture ferme n'est retenue sans recherche supplémentaire.

### Réfuté

- **Statut — RÉFUTÉ.** « Tous les ensembles ultimement périodiques sont
  réalisables » sans restriction est faux, car (Delta_1=Q\setminus E_1)
  est toujours vide.

- **Statut — RÉFUTÉ.** (Q) seul ne détermine pas le spectre.

- **Statut — RÉFUTÉ.** Les anciens décomptes de cas P3 mémorisés pour les
  petites tailles doivent être remplacés par les décomptes exacts de la
  section 5 ; certains anciens totaux étaient incompatibles avec la définition
  (D=\{h:\Delta_h\neq\varnothing\}).

Score de l'itération : **+2** (classification nécessaire et suffisante et objet
fini canonique).

## 2. CHANGEMENT RÉEL DE CETTE ITÉRATION

La périodicité connue a été renforcée en une classification exacte : hormis
l'impossibilité universelle d'un défaut à un pas, la dynamique déterministe
quotientée n'impose aucune autre restriction aux ensembles ultimement
périodiques réalisables.

## 3. RÉSULTAT PRINCIPAL

### Théorème de l'automate canonique et de réalisation universelle

**Statut — DÉMONTRÉ.** Pour tout système fini déterministe observé
((X,T,\pi)) :

1. l'automate
   
   \[
   \mathcal A_0:quad
   (S,V)\xmapsto{u}(SB,AV),qquad (S_0,V_0)=(I_m,C),
   \]
   
   avec acceptation lorsque
   (\operatorname{supp}(S)\setminus
   \operatorname{supp}(C^{\mathsf T}V)\neq\varnothing), reconnaît exactement
   (L_D) ;

2. son quotient de Nerode est l'unique automate déterministe minimal de
   (L_D) ;

3. (D) est ultimement périodique, avec les bornes (H,L) ci-dessus ;

4. réciproquement, chaque ensemble ultimement périodique
   (D\subseteq\mathbb N_{\geq1}) tel que (1\notin D) est le spectre d'un
   système ayant exactement trois macro-états.

Conséquences immédiates :

- **Statut — DÉMONTRÉ.** P2 équivaut à l'absence totale d'états acceptants
  dans l'automate minimal.
- **Statut — DÉMONTRÉ.** P3 équivaut à l'absence d'état acceptant sur son
  unique cycle terminal.
- **Statut — DÉMONTRÉ.** Les spectres des systèmes P3 sont exactement les
  sous-ensembles finis de ({2,3,4,\ldots\}).

## 4. PREUVE / CALCUL / CONTRE-EXEMPLE

### 4.1 Réduction minimale avant minimisation

**Statut — DÉMONTRÉ.** Posons (V_h=A^hC). Chaque ligne de (V_h) est
unitaire et code la coloration

\[
c_h(x)=\pi(T^h x).
\]

On a par induction

\[
(S_h,V_h)=(B^h,A^hC),qquad
C^{\mathsf T}V_h=C^{\mathsf T}A^hC=E_h.
\]

L'état ((B^h,A^hC)) suffit donc ; mémoriser (A^h), (T^h), ou tous les
témoins de chemins est inutile. L'acceptation est exactement
(B^h\setminus E_h\neq\varnothing), ce qui prouve le point 1 du théorème.

**Statut — DÉMONTRÉ.** La représentation est compatible avec tout renommage
des états et des classes : (A,C,B,E_h) sont seulement conjugués par des
matrices de permutation. Le booléen « (Delta_h\neq\varnothing) » est donc
inchangé.

**Statut — CALCUL EXACT.** (B) seul est insuffisant. Sur
(X=\{0,1,2\}), avec la même partition (pi=(0,1,1)), les deux applications

\[
T_1=(0,0,1),\qquad T_2=(0,0,2)
\]

donnent le même quotient

\[
Q(0)=\{0\},\qquad Q(1)=\{0,1\},
\]

mais

\[
D(T_1,\pi)=\{h\geq2\},\qquad D(T_2,\pi)=\varnothing.
\]

### 4.2 Minimisation exacte

**Statut — DÉMONTRÉ.** Deux longueurs (i,j) sont équivalentes si et seulement
si

\[
\forall k\geq0,quad d_{i+k}=d_{j+k}.
\]

C'est exactement la congruence droite de Myhill–Nerode. Si (mu_D) est le
plus petit début de périodicité et (p_D) la plus petite période à partir de ce
début, les suffixes infinis associés aux positions
(0,\ldots,\mu_D+p_D-1) sont deux à deux distincts. Ils donnent donc les
(mu_D+p_D) états minimaux ; la dernière transition revient à l'état
(mu_D).

### 4.3 Bornes

**Statut — DÉMONTRÉ.** La suite (A^hC), ou (c_h=\pi\circ T^h), devient
périodique au plus tard après (d_T\leq n-1). Sa période est

\[
p_\pi=\operatorname{lcm}_{\gamma}
\bigl(\text{période minimale du mot }\pi|_\gamma\bigr),
\]

où (gamma) parcourt les cycles de (T).

**Statut — CONNU DANS LA LITTÉRATURE.** Pour le graphe de (Q), la suite
(B^h) vérifie (B^{h+c_Q}=B^h) à partir d'un seuil (K_Q), où (c_Q) est
le PPCM des cyclicité non nulles des composantes fortement connexes. Le seuil
général (K_Q\leq2m^2-3m+2) vient du théorème 3.20 de De Schutter–De Moor.

**Statut — DÉMONTRÉ.** Le couple (Z_h) se répète donc avec période
(L=\operatorname{lcm}(c_Q,p_\pi)) dès
(H=\max(K_Q,d_T)). Comme les entiers entrant dans ce PPCM ont une somme au
plus (m+n), (L\leq g(m+n)) par définition de la fonction de Landau.

**Statut — DÉMONTRÉ.** Si P3 est vraie et si un défaut apparaissait à un
rang (h\geq H), il réapparaîtrait à tous les rangs (h+kL). Ce serait une
contradiction. Ainsi (	au\leq H-1).

### 4.4 Classification de tous les spectres

**Statut — DÉMONTRÉ.** Nécessité : (D) est ultimement périodique par
l'automate fini précédent, et (E_1=B), donc (1\notin D).

**Statut — DÉMONTRÉ.** Suffisance : soit (D) ultimement périodique avec
(1\notin D). Prenons (Y=\{s,f,n\}) et le mot ultimement périodique

\[
w_h=\begin{cases}
f,&h\in D,\\
n,&h\notin D,
\end{cases}qquad h\geq1.
\]

Il existe un lasso fini (r_1\to r_2\to\cdots) dont la couleur au rang (h)
est (w_h). Ajoutons les états suivants :

| État | Classe | Image |
|---|---:|---|
| (s_f) | (s) | (f_\infty) |
| (s_w) | (s) | (r_1) |
| (f_\infty) | (f) | (f_\infty) |
| (f_n) | (f) | (n_\infty) |
| (n_\infty) | (n) | (n_\infty) |
| (n_f) | (n) | (f_\infty) |
| (r_h) | (w_h) | (r_{h+1}), avec retour sur le cycle du lasso |

Comme (1\notin D), (w_1=n). Le quotient satisfait alors

\[
Q(s)=Q(f)=Q(n)=\{f,n\};
\]

aucune arête n'arrive en (s). Pour tout (h\geq1), les états de support
(f_\infty,f_n,n_\infty,n_f) réalisent exactement les deux extrémités
({f,n\}) depuis les fibres (f) et (n). Depuis la fibre (s), on obtient

\[
E_h(s,\cdot)=\{f,w_h\}
=\begin{cases}
\{f\},&h\in D,\\
\{f,n\},&h\notin D.
\end{cases}
\]

Ainsi (Q^h\setminus E_h\neq\varnothing) exactement lorsque (h\in D).
Cela achève la classification.

## 5. AUDIT ADVERSARIAL

**Statut — CALCUL EXACT.** Tous les (T:X\to X) et toutes les partitions non
étiquetées de (X) ont été énumérés jusqu'à (n=5).

| (n) | Couples ((T,\pi)) | Spectres distincts | (D=\varnothing) | (D) fini non vide | (D) infini | Taille maximale du DFA minimal |
|---:|---:|---:|---:|---:|---:|---:|
| 2 | 8 | 1 | 8 | 0 | 0 | 1 |
| 3 | 135 | 2 | 105 | 0 | 30 | 3 |
| 4 | 3 840 | 7 | 2 052 | 0 | 1 788 | 5 |
| 5 | 162 500 | 19 | 54 380 | 240 | 107 880 | 8 |

**Statut — CALCUL EXACT.** Le seul spectre fini non vide à (n=5) est
(D=\{2\}). Un témoin est

\[
T=(0,0,0,1,2),\qquad \pi=(0,1,2,2,3).
\]

Cela reconfirme que (n=5) est la première taille possible pour P3 sans P2.

**Statut — CALCUL EXACT.** Une implémentation indépendante a comparé les
sorties de l'automate avec l'itération directe de (T^h) et (Q^h) sur
13 984 systèmes (exhaustif jusqu'à (n=4), puis 5 000 tirages pour chacun de
(n=5,6)), jusqu'à l'horizon 80. Elle a aussi vérifié 13 983 renommages
aléatoires d'états et de classes.

**Statut — CALCUL EXACT.** La construction universelle a été testée sur 4 001
couples prépériode/période binaires, jusqu'à l'horizon 150, sans échec.

Attaques imposées :

- **Statut — CALCUL EXACT.** Petit espace : exhaustif pour (n\leq5).
- **Statut — CALCUL EXACT.** Non-injectivité extrême : les tests incluent les
  applications constantes, les longs arbres et la construction universelle à
  puits.
- **Statut — CALCUL EXACT.** Permutations pures : toutes sont incluses dans
  l'exhaustif ; elles produisent plusieurs périodes non triviales.
- **Statut — CALCUL EXACT.** Partitions asymétriques : toutes les partitions
  sont incluses, sans hypothèse sur les tailles des fibres.
- **Statut — DÉMONTRÉ.** SAT/SMT n'est pas nécessaire pour la classification,
  car la nécessité et la réalisation explicite couvrent les deux directions.

Fichiers de vérification : `quotient_spectrum_search.py` et
`verify_quotient_spectrum.py`.

## 6. LITTÉRATURE

| Comparaison | Notre énoncé | Énoncé de la littérature | Différence réelle |
|---|---|---|---|
| Automates unaires | (D) est reconnu par l'orbite de ((B^h,A^hC)), puis minimisé par Nerode. | Les automates sur alphabet unaire, leurs formes normales et leurs complexités sont classiques ; voir Chrobak (1986) et Czerwiński et al. (2023). | **Statut — REFORMULATION.** L'ultime périodicité et la forme chaîne-cycle ne sont pas nouvelles. L'apport propre est l'identification du générateur exact associé à ((T,\pi)). |
| Puissances booléennes | Le facteur macro est (B^h), avec seuil (K_Q) et cyclicité (c_Q). | De Schutter–De Moor caractérisent la cyclicité par les SCC et donnent (K_Q\leq2m^2-3m+2). | **Statut — REFORMULATION.** La borne sur (B^h) est connue ; sa combinaison avec la coloration (A^hC) donne la borne du spectre. |
| Préservation abstraite | P2/P3 mesurent l'absence totale/asymptotique d'extrémités fallacieuses. | Ranzato–Tapparo relient forte préservation, complétude et raffinement des abstractions. | **Statut — INDÉTERMINÉ.** Le vocabulaire est proche, mais je n'ai pas trouvé leur équivalent du spectre de longueurs ni le théorème de réalisation. |
| Classification des spectres | Tous et seulement les ensembles ultimement périodiques évitant (1), réalisables avec trois classes. | Aucune source exacte trouvée sous les vocabulaires « quotient transition system spurious paths », « unary defect lengths », « Boolean matrix quotient powers », « endpoint exactness » et variantes. | **Statut — INDÉTERMINÉ.** Absence de résultat trouvé n'est pas preuve de nouveauté. |

Sources vérifiables :

1. B. De Schutter et B. De Moor, *On the Sequence of Consecutive Powers of a
   Matrix in a Boolean Algebra*, SIAM J. Matrix Anal. Appl. 21(1), 1999,
   DOI 10.1137/S0895479897326079 :
   https://www.bartdeschutter.org/publications/97-67-sequence-consecutive-powers-matrix/97-67-sequence-consecutive-powers-matrix.pdf
2. M. Chrobak, *Finite Automata and Unary Languages*, Theoretical Computer
   Science 47, 1986, pp. 149–158 :
   https://www.sciencedirect.com/science/article/pii/0304397586901428
3. W. Czerwiński et al., *Languages Given by Finite Automata over the Unary
   Alphabet*, FSTTCS 2023, DOI 10.4230/LIPIcs.FSTTCS.2023.22 :
   https://drops.dagstuhl.de/entities/document/10.4230/LIPIcs.FSTTCS.2023.22
4. F. Ranzato et F. Tapparo, *Strong Preservation as Completeness in Abstract
   Interpretation*, ESOP 2004 :
   https://www.math.unipd.it/~ranzato/papers/esop04.pdf
5. P. Boldi et S. Vigna, *Fibrations of Graphs*, Discrete Mathematics 243,
   2002 : https://doi.org/10.1016/S0012-365X(00)00455-6

## 7. NOUVEAUTÉ RÉSIDUELLE

**Statut — REFORMULATION.** La périodicité, la forme chaîne-cycle du DFA
minimal et la cyclicité des puissances booléennes sont des résultats standards.

**Statut — DÉMONTRÉ.** La classification constructive à trois macro-états et
la réduction exacte à ((B^h,A^hC)) restent mathématiquement valides après
retrait de ces éléments connus.

**Statut — INDÉTERMINÉ.** Je ne peux pas confirmer que la classification à
trois macro-états est nouvelle dans la littérature mondiale. La recherche
ciblée n'a trouvé aucun énoncé équivalent, mais une vérification de nouveauté
exigerait une recherche bibliographique plus large et, idéalement, une revue
par un spécialiste des automates/abstractions.

VALIDITÉ :

- **Statut — DÉMONTRÉ.** Systèmes finis, déterministes, temps discret,
  observation surjective vers un ensemble fini.

ROBUSTESSE :

- **Statut — DÉMONTRÉ.** Invariance sous renommage des états, renommage des
  classes et isomorphisme du graphe fonctionnel coloré.
- **Statut — INDÉTERMINÉ.** La classification n'est pas encore transférée aux
  relations non déterministes ou aux chaînes de Markov.

GÉNÉRALITÉ :

- **Statut — DÉMONTRÉ.** Tous les spectres ultimement périodiques admissibles
  apparaissent déjà avec trois macro-états ; aucune hypothèse d'injectivité,
  d'équitabilité ou de tailles égales des fibres n'est requise.

## 8. PROCHAINE QUESTION

**Statut — INDÉTERMINÉ.** Peut-on caractériser P3 directement par les SCC de
(Q), les cycles colorés de (T) et leurs classes de résidus — et décider P3
sans énumérer les (L=\operatorname{lcm}(c_Q,p_\pi)) phases — ou cette décision
est-elle intrinsèquement difficile (par exemple coNP-difficile via les automates
unaires) ?