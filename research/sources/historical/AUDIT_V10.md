# V10 — Audit systématique des preuves et de la littérature

Date : 2026-09-18

## Verdict exécutif

### V7 — Polynôme d'observabilité temporelle
STATUT MATHÉMATIQUE : PASSÉ

La construction
\[
\chi^{\mathrm{obs}}_{T,L}(m)
\]
comme nombre de colorations dont les histoires de longueur \(L\) sont injectives
est correcte. La représentation comme complément d'une union de sous-espaces
diagonaux et l'existence d'un polynôme de comptage suivent par
inclusion-exclusion / treillis d'intersections.

STATUT DE NOUVEAUTÉ : REFORMULATION / INDÉTERMINÉ

La théorie générale des arrangements de sous-espaces issus de l'arrangement de
tresses et des polynômes chromatiques généralisés est connue. La spécialisation
dynamique particulière reste à distinguer de cette théorie générale.

---

### V8 — Caractérisation et factorisation à horizon infini
STATUT MATHÉMATIQUE : PASSÉ

Le théorème suivant résiste à une reconstruction indépendante.

Une coloration \(c:X\to[m]\) est génératrice à horizon infini si et seulement si :

1. pour tout \(y\), la restriction de \(c\) à \(T^{-1}(y)\) est injective ;
2. les itinéraires symboliques des points périodiques sont tous distincts.

La seconde condition équivaut à :
- chaque cycle de longueur \(r\) reçoit un mot primitif de longueur \(r\) ;
- deux cycles distincts de même longueur reçoivent des classes de rotation
  distinctes.

Il en résulte la factorisation
\[
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
(Q_r(z)-jr)
\right],
\]
avec
\[
Q_r(z)=\sum_{e\mid r}\mu(e)z^{r/e}.
\]

La formule antérieure pour \(m_\infty(T)\) est un corollaire strict de cette
identité de comptage.

STATUT DE NOUVEAUTÉ : INDÉTERMINÉ

Aucune source trouvée dans l'audit ciblé ne contient cette factorisation exacte
pour une endofonction arbitraire. Cela ne constitue pas une preuve de nouveauté.

---

### V9 — Théorème de rang des orbites de paires
STATUT MATHÉMATIQUE : PASSÉ

Pour une paire \(p=\{x,y\}\), soit \(e_t=\{T^t x,T^t y\}\).
Si une arête \(e_t\) est dépendante des précédentes dans le graphe non orienté,
alors toutes les arêtes ultérieures le sont.

En effet, un chemin reliant les extrémités de \(e_t\), une fois appliqué par
\(T\), donne un chemin reliant les extrémités de \(e_{t+1}\).

Ainsi
\[
\operatorname{rank}G_{p,L}=\min(L,r_p).
\]

STATUT DE NOUVEAUTÉ : INDÉTERMINÉ pour le lemme lui-même.

---

### V9 — Stabilisation universelle en \(N-1\)
STATUT MATHÉMATIQUE : PASSÉ
STATUT DANS NOTRE PROGRAMME : REDONDANT

Le résultat
\[
\chi^{\mathrm{obs}}_{T,L}
=
\chi^{\mathrm{obs}}_{T,\infty}
\qquad (L\ge N-1)
\]
est correct.

Mais il était déjà contenu dans notre théorème antérieur de raffinement :
si une partition à \(k\ge2\) blocs est génératrice à horizon infini, chaque
raffinement strict augmente le nombre de blocs d'au moins un ; si un raffinement
cesse d'être strict avant la partition discrète, il reste stable pour toujours.
Il faut donc au plus
\[
N-k
\]
raffinements supplémentaires, soit
\[
L\le N-k+1\le N-1.
\]

Le lemme de rang donne une nouvelle preuve géométrique, mais la borne elle-même
ne doit plus être présentée comme une nouvelle découverte de V9.

---

### V9 — Spectre \(\Theta_T(z,u)\)
STATUT MATHÉMATIQUE : PASSÉ
STATUT CONCEPTUEL : REFORMULATION UTILE

Définir
\[
\Psi_{T,L}(z)=
\chi^{\mathrm{obs}}_{T,L}(z)
-
\chi^{\mathrm{obs}}_{T,L-1}(z)
\]
et
\[
\Theta_T(z,u)=\sum_L \Psi_{T,L}(z)u^L
\]
est correct.

Mais
\[
\{\chi^{\mathrm{obs}}_{T,L}\}_L
\longleftrightarrow
\Theta_T
\]
est une correspondance sans perte :
\[
\chi^{\mathrm{obs}}_{T,L}
=
\sum_{h\le L}[u^h]\Theta_T.
\]

Donc \(\Theta_T\) ne contient pas d'information mathématique nouvelle par rapport
à la famille complète des polynômes finis. Il reste une représentation très utile
du compromis résolution-temps.

---

## Porte A — Reconstruction indépendante des preuves

### A1. Suffisance de la caractérisation V8

Supposons l'injectivité sur toutes les fibres et la séparation de tous les points
périodiques.

Si deux états distincts \(x,z\) avaient la même histoire infinie, leurs orbites
finiraient par entrer dans la partie périodique. À un temps suffisamment grand,
les deux états itérés seraient périodiques et auraient la même histoire infinie.
La condition périodique force alors leur égalité.

Il existe donc un premier \(k\ge1\) tel que
\[
T^k x=T^k z.
\]
Alors
\[
T^{k-1}x\ne T^{k-1}z,
\qquad
T(T^{k-1}x)=T(T^{k-1}z),
\]
mais l'égalité des histoires donne
\[
c(T^{k-1}x)=c(T^{k-1}z),
\]
contradiction avec l'injectivité sur la fibre correspondante.

PASSÉ.

### A2. Comptage V8

Les fibres \(T^{-1}(y)\) partitionnent \(X\).

- Si \(y\) est non périodique, aucun antécédent périodique ne peut appartenir à
  \(T^{-1}(y)\). Les \(d_y\) couleurs doivent être distinctes :
  \[
  (m)_{d_y}.
  \]

- Si \(y\) est périodique, exactement un antécédent de \(y\) est périodique :
  son prédécesseur sur le cycle. Sa couleur est déjà déterminée par le mot du
  cycle. Les \(d_y-1\) autres antécédents doivent recevoir des couleurs
  distinctes évitant cette couleur :
  \[
  (m-1)_{d_y-1}.
  \]

- Sur un cycle de longueur \(r\), le mot doit être primitif :
  \[
  Q_r(m)
  \]
  choix. Un mot primitif possède exactement \(r\) rotations distinctes. Pour
  \(c_r\) cycles distingués de longueur \(r\), le nombre de choix est donc
  \[
  \prod_{j=0}^{c_r-1}(Q_r(m)-jr).
  \]

Les choix sont indépendants entre fibres et classes de longueurs de cycles.

PASSÉ.

### A3. Lemme de rang V9

Si \(e_t\) est déjà contenu dans la fermeture graphique des arêtes antérieures,
il existe un chemin composé de \(e_0,\ldots,e_{t-1}\) reliant ses extrémités.
L'image de ce chemin sous \(T\) est un chemin, après suppression des boucles,
composé de \(e_1,\ldots,e_t\), reliant les extrémités de \(e_{t+1}\).
Donc \(e_{t+1}\) est dépendante. Répéter donne la conclusion.

PASSÉ.

---

## Porte B — Vérification computationnelle indépendante

Les vérifications ont été refaites sans utiliser les scripts historiques.

### B1. Factorisation V8

Comparaison :
- formule fermée V8 ;
- comptage brut des colorations par signatures de longueur \(N-1\).

Résultats :
- toutes les endofonctions pour \(N\le5\),
  alphabets \(m=1,2,3\) :
  10 239 comparaisons, zéro contre-exemple ;
- toutes les 46 656 endofonctions pour \(N=6\), \(m=2\) :
  zéro contre-exemple ;
- 1 000 endofonctions aléatoires de taille 7, \(m=2\) :
  zéro contre-exemple ;
- 1 000 endofonctions aléatoires de taille 8, \(m=2\) :
  zéro contre-exemple ;
- 300 endofonctions aléatoires de taille 6, \(m=3\) :
  zéro contre-exemple.

Ces calculs ne remplacent pas la preuve, mais constituent un audit indépendant.

### B2. Théorème de rang

Toutes les endofonctions de tailles \(1\) à \(6\) ont été examinées :
\[
1+4+27+256+3125+46656=50069
\]
systèmes.

Pour chaque paire, aucun accroissement de rang n'a été observé après la première
stagnation.

Zéro contre-exemple.

### B3. Tableaux V9

Les partitions en blocs ont été réénumérées indépendamment pour :
- \(T=(0,0,3,2)\) ;
- F6-A ;
- F6-B.

Les valeurs \(b_T(k,L)\) publiées en V9 sont reproduites exactement.

---

## Porte C — Audit de redondance

### C1. Polynôme fini

Le fait que \(\chi^{\mathrm{obs}}_{T,L}\) soit polynomial est essentiellement une
application de la théorie générale des arrangements diagonaux / polynômes
chromatiques généralisés.

Verdict :
REFORMULATION dynamique, pas nouveau principe combinatoire à lui seul.

### C2. Formule \(m_\infty\)

Elle est maintenant absorbée par V8 :
\[
m_\infty(T)
=
\min\{m:\chi^{\mathrm{obs}}_{T,\infty}(m)>0\}.
\]

Verdict :
COROLLAIRE de V8.

### C3. Borne \(N-1\)

Déjà implicite dans le théorème antérieur de raffinement de partitions.

Verdict :
REDONDANT comme résultat global ; nouvelle preuve via les paires.

### C4. \(\Theta_T\)

Équivalent à la famille complète
\[
(\chi^{\mathrm{obs}}_{T,1},\ldots,\chi^{\mathrm{obs}}_{T,N-1}).
\]

Verdict :
ENCODAGE BIVARIÉ UTILE, mais pas invariant indépendant.

---

## Porte D — Audit bibliographique

### D1. Générateurs / partitions génératrices

La notion de partition génératrice et de codage symbolique injectif est classique
en dynamique symbolique et théorie ergodique. Les générateurs unilatéraux pour
endomorphismes sont bien établis.

Conséquence :
notre définition fondamentale n'est pas nouvelle comme concept général.

### D2. Observabilité et machines de Moore

L'observabilité par suites de sorties, la distinguabilité des états et les
raffinements de partitions sont classiques en automates et systèmes finis.

Les travaux sur les graphes observables de Jungers et Blondel caractérisent
l'observabilité de graphes colorés et calculent le nombre d'observations
nécessaires. Leur modèle autorise des trajectoires plus générales qu'une unique
endofonction, ce qui explique que leurs bornes générales puissent être
quadratiques sans contredire notre borne \(N-1\) dans le cas à successeur unique.

### D3. Coloration des états et traces

Des travaux récents emploient explicitement la notion de state coloring function
et les traces de couleurs le long des états d'automates.

Conséquence :
l'idée « colorer des états et lire la trace de couleurs » est clairement connue.

### D4. Arrangements diagonaux

Miller et Wakefield ont montré qu'une classe d'arrangements de sous-espaces
définis par intersections d'hyperplans de l'arrangement de tresses possède un
polynôme caractéristique donné par un polynôme chromatique généralisé d'un
hypergraphe coloré.

Conséquence :
V7 s'insère directement dans une théorie existante.

### D5. Contraintes périodiques / générateurs

La littérature sur les générateurs symboliques et les extensions avec plongement
fait intervenir explicitement les orbites périodiques comme obstruction à la
taille de l'alphabet.

Conséquence :
la présence de contraintes périodiques dans \(m_\infty\) n'est pas, en elle-même,
une signature de nouveauté.

### D6. Recherche ciblée de la factorisation V8

Recherches effectuées sous plusieurs vocabulaires :
- finite dynamical system observability;
- generating partition finite endomorphism;
- state coloring finite automata;
- output assignment / output labeling;
- functional digraph coloring;
- primitive necklaces functional graph;
- one-sided generator finite transformation;
- observable graphs;
- Moore machine distinguishability;
- diagonal subspace arrangements;
- chromatic polynomial generalized;
- finite transformation symbolic coding.

Aucune source consultée ne donne la factorisation exacte de V8 sous cette forme.

Verdict :
NOUVEAUTÉ INDÉTERMINÉE, pas « nouvelle ».

Attention :
la littérature sur les graphes fonctionnels contient des exemples documentés de
redécouverte de résultats anciens sous une terminologie moderne différente.
Cette situation justifie de ne pas conclure sur la seule base d'une recherche
lexicale.

---

## Nouvelle hiérarchie de confiance

### Niveau A — solide et connu/reformulé
- partitions génératrices ;
- observabilité par suites de sorties ;
- graphe des paires / raffinement ;
- arrangements diagonaux et polynômes chromatiques généralisés.

### Niveau B — démontré dans notre programme mais probablement proche de résultats classiques
- équivalence de Bruijn ;
- borne de stabilisation \(N-1\) ;
- lemme de rang des paires.

### Niveau C — candidat principal à contribution propre
- factorisation exacte de
  \[
  \chi^{\mathrm{obs}}_{T,\infty}(z)
  \]
  pour une endofonction arbitraire.

### Niveau D — outils de présentation / organisation
- \(\Theta_T(z,u)\) ;
- tableau \(b_T(k,L)\).

Ils peuvent devenir mathématiquement importants si de nouvelles contraintes
structurelles sont démontrées, mais leur définition seule ne constitue pas une
percée.

---

## Décision de recherche

Ne pas introduire de nouvel invariant maintenant.

Priorité suivante :

1. écrire V8 sous forme de théorème autonome minimal ;
2. chercher une preuve alternative par combinatoire des espèces / décomposition
   des graphes fonctionnels ;
3. effectuer un audit bibliographique par chaînage de citations à partir de :
   - générateurs unilatéraux ;
   - observable graphs ;
   - Moore machines ;
   - functional digraph enumeration ;
   - primitive necklaces ;
   - diagonal arrangements ;
4. tester si la factorisation V8 est une spécialisation immédiate d'un théorème
   d'énumération connu ;
5. seulement si elle survit, étudier les coefficients finis comme correction
   transitoire de cette factorisation.

## Verdict final V10

V8 : PASSÉ mathématiquement, NOUVEAUTÉ INDÉTERMINÉE.

V9 rang des paires : PASSÉ mathématiquement, NOUVEAUTÉ INDÉTERMINÉE.

V9 borne \(N-1\) : PASSÉ mais REDONDANT.

\(\Theta_T\) : PASSÉ comme définition, REFORMULATION UTILE.

La prochaine phase doit donc être un audit de nouveauté concentré sur V8, pas une
nouvelle expansion théorique.