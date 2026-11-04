# Audit scientifique du programme « temps observé »

**Date :** 22 août 2026  
**Périmètre :** règle 90 sur les cycles, fermeture observationnelle, périodes, mots observés, Fourier–Walsh, entropie de Rényi-2, résolution \(\rho\) et Régime B.  
**Convention :** \(W_h(x)=(\pi(x),\pi(Ax),\ldots,\pi(A^h x))\), soit \(h+1\) observations.

## 1. Verdict général

Le programme contient désormais un noyau mathématique solide, mais toutes les affirmations antérieures n'ont pas le même statut.

- **Démontré :** structure algébrique de la règle 90, dimensions des noyaux et rangs, critère de fermeture par stabilité des fibres, formule d'observabilité pour les observations linéaires, uniformité de Majority dans le domaine \(N\ge 2h+3\), interprétation collisionnelle exacte de \(H_2\), et construction abstraite d'un Régime B en \(\Theta(\sqrt T)\).
- **Reproduit numériquement seulement :** liste des 24 règles locales fermées pour \(5\le N\le13\), tables particulières de périodes, certaines distributions hors régime sans repliement.
- **Faux ou à corriger :** formule de rang de \(\Pi_2\) avec un plafond, identification automatique des collisions orbitales avec \(2^{-H_2}\), correction diagonale approximative présentée comme identité, et toute déduction d'une croissance observationnelle depuis la seule entropie topologique.
- **Ouvert :** classification générale des 24 facteurs locaux, existence d'un Régime B pour une famille locale naturelle de règle 90, lois générales pour les périodes \(L_m\), originalité précise de la typologie \(\rho_q\), et théorie reliant autocollisions orbitales et entropies de mots.

## 2. Matrice d'audit

| Affirmation | Statut après audit | Justification |
|---|---|---|
| \(A_N=z+z^{-1}=z^{-1}(z+1)^2\) dans \(R_N=\mathbb F_2[z]/(z^N-1)\) | **Théorème classique confirmé** | Identité directe; cadre standard des automates cellulaires additifs. |
| Si \(N=2^a m\), \(m\) impair, alors \(\dim\ker A_N^t=\min(2t,2^a)\) | **Démontré** | \(z^N-1=(z^m-1)^{2^a}\) et calcul du PGCD avec \((z+1)^{2t}\). |
| Dimension récurrente \(N-2^a\) | **Démontré** | Complément de la composante primaire \((z+1)\), de dimension \(2^a\). |
| Pour \(N=2^a\), \(A_N^{2^{a-1}}=0\) | **Démontré** | Conséquence directe de la formule précédente. |
| \(L_N=2^aL_m\) pour \(m>1\) impair | **Démontré sous la définition de période maximale de la composante récurrente** | Relèvement des multiplicités par Frobenius; convention \(L_{2^a}=1\) si la composante récurrente est nulle. |
| Une dynamique observée \(G\) existe si et seulement si les fibres de \(\Pi\) sont stables | **Démontré** | \(\Pi(x)=\Pi(y)\Rightarrow\Pi(Ax)=\Pi(Ay)\); pour \(\Pi\) linéaire, équivaut à \(A\ker\Pi\subseteq\ker\Pi\). |
| Toute fermeture à \(N\) fixé est automatiquement une règle locale uniforme | **Faux** | Une congruence globale à taille fixée ne prouve ni localité de \(G\), ni uniformité en \(N\). |
| \(H(W_h^{\Pi_1})=H_2(W_h^{\Pi_1})=\min(h+1,\lceil N/2\rceil)\) | **Démontré et reproduit** | Rang de la matrice d'observabilité sur \(\mathbb F_2\). |
| Même formule pour \(\Pi_2(x)=x_0\oplus x_1\) avec \(\lceil N/2\rceil\) | **Faux** | La bonne formule est \(\min(h+1,\lfloor N/2\rfloor)\); contre-exemples pour \(N\) impair. |
| Majority donne \(H=H_2=h+1\) pour \(N\ge2h+3\) | **Démontré et reproduit** | Preuve Fourier–Walsh contrainte ci-dessous; exhaustif jusqu'à \(h=7\), notamment aux frontières \(N=2h+3,2h+4\). |
| Majority est uniforme pour tous \(N,h\) | **Faux** | Exemple : \(N=5,h=2\), collision \(17/128\), \(H_2\approx2.912537<3\). |
| Il existe exactement 24 observations locales de rayon 1 fermées | **Résultat numérique limité** | Même liste pour chaque \(5\le N\le13\); aucune preuve générale en \(N\). Majority n'en fait pas partie. |
| \(2^{-H_2(W_h)}\) est la probabilité de collision | **Exact pour deux tirages indépendants avec remise** | Définition de l'entropie de Rényi-2. |
| Cette quantité est aussi la fréquence de collision entre décalages d'une orbite | **Non démontré et généralement faux** | Les mots orbitaux décalés ne sont pas deux copies indépendantes; il faut une fonction d'autocollision. |
| Fraction de paires distinctes \(=2^{-H_2}-2^{-N}\) | **Faux comme identité normalisée** | La formule exacte est donnée en section 6. |
| \(h_{\rm top}>0\Rightarrow H_2(W_h)\) croît linéairement pour toute observation | **Faux** | L'entropie topologique ne contraint pas une observation arbitraire sous une mesure arbitraire. Chaque système fini isolé a en outre une entropie topologique nulle. |
| La construction impulsionnelle à deux compteurs réalise un Régime B | **Confirmé sous une définition précise** | Pour \(T=m^2\), la résolution par pire phase donne \(\rho_{50}=m-1=\Theta(\sqrt T)\). |
| La règle 90 locale réalise elle-même le Régime B | **Ouvert** | Aucun résultat actuel ne l'établit. |

## 3. Preuve auditée du théorème Majority–Walsh

Pour trois bits,

\[
(-1)^{\operatorname{Maj}(a,b,c)}=
\frac12\bigl(\chi(a)+\chi(b)+\chi(c)-\chi(a+b+c)\bigr),
\qquad \chi(u)=(-1)^u.
\]

Posons \(q=z+z^{-1}\) et \(r=z^{-1}+1+z=q+1\). Dans l'expansion d'un coefficient de Walsh joint non trivial de \(W_h\), chaque temps \(t\) fournit exactement un choix

\[
u_t\in\{0,z^{-1},1,z,r\}
=\{0,q+z,1,z,q+1\},
\]

et la forme linéaire résultante a pour polynôme

\[
P(z)=\sum_{t=0}^{h}q^t u_t.
\]

Dans \(\mathbb F_2(z)=\mathbb F_2(q)\oplus z\mathbb F_2(q)\), écrivons \(P=A(q)+zB(q)\). Alors

\[
B(q)=\sum_{u_t\in\{q+z,z\}}q^t.
\]

Les monômes \(q^t\) étant linéairement indépendants, \(B=0\) exclut tous les choix \(q+z\) et \(z\). Il reste \(u_t\in\{0,1,q+1\}\). Si \(t_0\) est le plus petit indice non nul, le coefficient de \(q^{t_0}\) dans \(A\) vaut 1, que \(u_{t_0}=1\) ou \(q+1\); aucun temps antérieur ne peut l'annuler. Donc \(P\ne0\).

Chaque coefficient de Walsh non trivial est ainsi nul sous la mesure uniforme. Le mot de \(h+1\) sorties est donc uniforme, à condition que le passage au cycle ne puisse annuler un polynôme de Laurent non nul. Son support est contenu dans \([-h-1,h+1]\); la réduction modulo \(z^N-1\) y est injective lorsque

\[
\boxed{N\ge2h+3.}
\]

Par conséquent,

\[
\boxed{H(W_h)=H_2(W_h)=h+1\quad\text{pour }N\ge2h+3.}
\]

Remarque d'audit : l'ancienne justification par la seule « indépendance de \(1\) et \(z\) » était incomplète. La preuve exige le langage contraint — un seul choix Walsh par temps — et l'argument du plus petit degré.

## 4. Structure linéaire et périodes

Écrivons \(N=2^a m\), \(m\) impair. En caractéristique 2,

\[
z^N-1=(z^m-1)^{2^a}.
\]

Comme \(z+1\) est simple dans \(z^m-1\),

\[
\gcd(q^t,z^N-1)=(z+1)^{\min(2t,2^a)},
\]

d'où

\[
\boxed{\dim\ker A_N^t=\min(2t,2^a),\qquad
\operatorname{rang}A_N^t=N-\min(2t,2^a).}
\]

La composante récurrente a dimension \(N-2^a\). Pour \(m>1\), si \(L_m\) désigne l'ordre de \(q\) sur la composante récurrente impaire, l'audit donne

\[
\boxed{L_N=2^aL_m.}
\]

Les valeurs reproduites jusqu'à \(N=16\) sont :

\[
(L_1,\ldots,L_{16})=(1,1,1,1,3,2,7,1,7,6,31,4,63,14,15,1).
\]

Les tables plus longues antérieurement annoncées et la piste de « résidu cubique » ne sont pas certifiées par cet audit.

## 5. Fermeture et facteurs locaux

Pour une observation quelconque \(\Pi:X\to Y\), une application \(G:\Pi(X)\to\Pi(X)\) satisfaisant \(\Pi A=G\Pi\) existe exactement lorsque

\[
\Pi(x)=\Pi(y)\Longrightarrow\Pi(Ax)=\Pi(Ay).
\]

Pour \(\Pi\) linéaire, cela devient \(A\ker\Pi\subseteq\ker\Pi\). La parité globale fournit un facteur de rang 1, puisque \(\Pi A=0\). Cela réfute toute équivalence entre « fermeture exacte » et « faible compression ».

Le calcul exhaustif des 256 tables booléennes de rayon 1 trouve les mêmes 24 tables pour chacun des cycles \(C_N\), \(5\le N\le13\) :

`00, 0f, 2d, 33, 3c, 4b, 55, 59, 5a, 65, 66, 69, 96, 99, 9a, a5, a6, aa, b4, c3, cc, d2, f0, ff`.

Ce résultat ne doit pas être appelé « classification pour tout \(N\) » avant une preuve symbolique. Il faut également distinguer :

1. fermeture globale sur un cycle fixé;
2. facteur local uniforme d'automates cellulaires;
3. lumpability d'une chaîne de Markov munie d'un noyau et d'une mesure.

## 6. Entropie de collision : formule correcte

Si les fibres de \(W_h\) ont des tailles \(c_w\) dans un espace de \(2^N\) états, alors

\[
p_w=\frac{c_w}{2^N},\qquad
2^{-H_2(W_h)}=\sum_w p_w^2
=\frac{\sum_w c_w^2}{2^{2N}}.
\]

C'est exactement la probabilité que deux états indépendants, tirés avec remise, donnent le même mot. Pour deux états distincts tirés uniformément sans remise, la probabilité exacte vaut

\[
\boxed{
\frac{\sum_w c_w^2-2^N}{2^N(2^N-1)}.
}
\]

Pour deux positions séparées par un décalage sur une même orbite, il faut définir et calculer

\[
C_h(s)=\frac1T\#\{t:W_h(x_t)=W_h(x_{t+s})\},
\]

et non substituer automatiquement \(2^{-H_2}\).

## 7. Résolution \(\rho\) et Régime B

La notion doit être définie avec cinq choix explicites : ensemble de paires ou de décalages, mesure, agrégation sur la phase initiale, traitement de \(\rho=\infty\), et quotient par les indiscernables permanents.

Pour le compteur hiérarchique

\[
F(a,b)=\left(a+1,\ b+\mathbf1_{\{a=m-1\}}\right)\pmod m,
\qquad T=m^2,
\]

et l'observation impulsionnelle \(\pi(a,b)=b\) si \(a=m-1\), \(0\) sinon, le calcul exact donne, sous la convention « pire phase »,

\[
\boxed{\rho_{50}=m-1=\Theta(\sqrt T).}
\]

Il s'agit donc d'un exemple abstrait valide d'échelle intermédiaire. Il ne démontre pas que la règle 90, une règle locale à rayon borné ou une famille naturelle réalise ce régime.

## 8. Position par rapport à la littérature

Les briques suivantes sont classiques : automates cellulaires additifs et représentation polynomiale, facteurs/sliding-block codes, congruences dynamiques, observabilité linéaire, analyse Fourier–Walsh et entropie de Rényi.

La combinaison proposée — distribution quantile des temps de séparation, quotient des indiscernables permanents, autocollisions de mots et comparaison entre facteurs locaux — peut constituer un programme original. **Je ne peux pas confirmer son originalité au sens bibliographique fort** sans recherche d'antériorité terminologique plus exhaustive, notamment du côté des distinguishing/homing sequences et des partitions génératrices.

## 9. Sources vérifiables

- O. Martin, A. Odlyzko, S. Wolfram, « Algebraic Properties of Cellular Automata », *Communications in Mathematical Physics* 93 (1984), [texte intégral](https://projecteuclid.org/journals/communications-in-mathematical-physics/volume-93/issue-2/Algebraic-properties-of-cellular-automata/cmp/1103941055.pdf).
- A. Canteaut, M. Videau, « Symmetric Boolean Functions », *IEEE Transactions on Information Theory* 51(8), 2005, [DOI](https://doi.org/10.1109/TIT.2005.851743), [manuscrit](https://inria.hal.science/inria-00001148/document).
- A. Rényi, « On Measures of Entropy and Information », 1961, [Project Euclid](https://projecteuclid.org/ebooks/berkeley-symposium-on-mathematical-statistics-and-probability/On-Measures-of-Entropy-and-Information/chapter/On-Measures-of-Entropy-and-Information/bsmsp/1200512181).
- R. Rivest, R. Schapire, « Inference of Finite Automata Using Homing Sequences », 1989, [manuscrit MIT](https://people.csail.mit.edu/rivest/pubs/RS89.pdf).
- D. Boley, « Krylov Space Methods on State-Space Control Models », 1994, [manuscrit](https://www-users.cse.umn.edu/~boley/publications/papers/Krylov94.pdf).

## 10. Priorités scientifiques

1. Prouver symboliquement la classification des 24 facteurs locaux, ou trouver un premier \(N\) exceptionnel.
2. Définir une version canonique de \(\rho_q\) et de l'autocollision orbitale \(C_h(s)\).
3. Recalculer les tables \(L_m\) avec code, tests croisés et certificats d'ordre.
4. Chercher ou réfuter un Régime B dans une famille locale à rayon borné.
5. Comparer formellement \(\rho_q\), homing sequences, partitions génératrices et observabilité.

## 11. Reproductibilité

Le script `independent_audit.py` reproduit les rangs linéaires, les distributions Majority, les périodes pour petits \(N\), le crible des 256 règles locales et la construction impulsionnelle. Un calcul exhaustif reste une preuve seulement sur le domaine effectivement énuméré.

## 12. Branches anciennes non certifiées par cette phase

Le contexte antérieur mentionne aussi des dénombrements de résolutions acycliques sur \(C_5,\ldots,C_8\), des signatures \((D,L)\), ainsi qu'un programme de colorations distinguant les renversements temporels. Les définitions complètes, programmes et sorties brutes correspondants n'ont pas été retrouvés dans le corpus de travail disponible. **Je ne peux donc pas confirmer ces nombres dans le présent audit.** Ils doivent former un lot de réplication séparé; ils ne sont ni utilisés ni supposés vrais dans les théorèmes ci-dessus.

## 13. Campagne adversariale de contre-exemples

Une seconde campagne a tenté de réfuter les résultats conservés.

- **Noyaux et observations linéaires :** 10 656 comparaisons exactes sur \(1\le N\le64\), sans contre-exemple aux formules de \(\ker A_N^t\), \(\Pi_1\) ou \(\Pi_2\).
- **Majority :** aucun contre-exemple dans le domaine théorique \(N\ge2h+3\) pour \(N\le18\), \(h\le8\). Hors domaine, l'uniformité échoue, par exemple dès \((N,h)=(3,1),(5,2),(7,3)\). La borne est suffisante mais non nécessaire dans tous les cas : \((8,3)\) reste uniforme.
- **Périodes :** aucun contre-exemple à \(L_N=2^aL_m\) par énumération complète pour \(N\le20\). Les nouvelles valeurs \(L_{17}=15\), \(L_{18}=14\), \(L_{19}=511\), \(L_{20}=12\) satisfont la loi.
- **Facteurs locaux :** les mêmes 24 règles persistent pour tout \(5\le N\le16\). Les petites tailles constituent des exceptions massives : 256 règles ferment pour \(N=1,2\), 142 pour \(N=3\), 98 pour \(N=4\).
- **Régime B abstrait :** aucun contre-exemple à \(\rho_{50}=m-1\) pour l'observation à valeurs dans \(\mathbb Z_m\), pour \(3\le m\le30\). Cette observation possède toutefois un alphabet croissant. Une variante à alphabet binaire fixe, observant la parité de \(b\) lors des retenues, conserve pour tout \(m\) impair testé une période effective \(T=m^2\) et \(\rho_{50}=2m-1=\Theta(\sqrt T)\). Les \(m\) pairs se quotientent à une période \(2m\), ce qui montre que la restriction impaire est essentielle pour cette variante.
- **Collision orbitale :** contre-exemple explicite sur \(C_5\). L'orbite de période 3 contenant l'état 18 produit le mot ponctuel `000`; ses autocollisions aux deux décalages non nuls valent 1, alors que la collision globale uniforme de \(\Pi_1\) vaut \(1/2\).

Le script `counterexample_audit.py` reproduit cette campagne. L'absence de contre-exemple sur un domaine fini ne remplace pas les preuves algébriques, mais elle teste les conventions, les cas limites et les généralisations abusives.

## 14. Théorème du Régime B binaire à compteur impair

La variante binaire observée dans la campagne précédente admet une preuve générale.

### Énoncé

Soit \(m\ge3\) impair et

\[
X_m=\mathbb Z_m^2,
\qquad
F(a,b)=\left(a+1,\ b+\mathbf 1_{\{a=m-1\}}\right)\pmod m.
\]

En identifiant chaque classe de \(\mathbb Z_m\) à son représentant canonique dans \(\{0,\ldots,m-1\}\), définissons l'observation à alphabet fixe

\[
\pi_m(a,b)=
\begin{cases}
b\bmod2,&a=m-1,\\
0,&a\ne m-1.
\end{cases}
\]

Sur l'orbite issue de \((0,0)\), de longueur ambiante \(T=m^2\), posons

\[
\rho(d)=\max_{n\in\mathbb Z_T}
\min\{t\ge0:s_{n+t}\ne s_{n+d+t}\},
\qquad 1\le d<T,
\]

où \(s_t=\pi_m(F^t(0,0))\). Pour tout quantile fixe \(q\in(0,1)\), lorsque \(m\) est assez grand relativement à \(q\),

\[
\boxed{
\left\lceil\frac{m^2}{m-1}\right\rceil-1
\le \rho_q
\le 3m-1.
}
\]

En particulier,

\[
\boxed{\rho_q=\Theta(m)=\Theta(\sqrt T).}
\]

De plus, le mot observé possède lui-même la période minimale \(T=m^2\) : le phénomène ne résulte pas d'un quotient périodique plus petit.

### Preuve

Écrivons \(t=bm+a\), avec \(0\le a,b<m\). Les positions où \(s_t=1\) forment l'ensemble

\[
M=\{bm+m-1:b\text{ impair}\}.
\]

Il contient \((m-1)/2\) points. Les écarts cycliques successifs entre les points de \(M\) valent \(2m\), sauf l'écart traversant la frontière du cycle, qui vaut \(3m\).

Si \(d\not\equiv0\pmod m\), les ensembles \(M\) et \(M-d\) occupent deux classes résiduelles distinctes modulo \(m\); ils sont donc disjoints. Les instants de désaccord entre \(s_t\) et \(s_{t+d}\) sont exactement

\[
D_d=M\mathbin\triangle(M-d)=M\cup(M-d),
\]

et \(|D_d|=m-1\). La résolution \(\rho(d)\) est le plus grand écart cyclique entre deux points consécutifs de \(D_d\), moins 1.

La moyenne des \(m-1\) écarts étant \(m^2/(m-1)\), le plus grand est au moins son plafond. D'autre part, puisque \(D_d\supseteq M\), ajouter les points de \(M-d\) ne peut augmenter le plus grand écart de \(M\), qui vaut \(3m\). Ainsi

\[
\left\lceil\frac{m^2}{m-1}\right\rceil-1
\le\rho(d)\le3m-1
\qquad(d\not\equiv0\pmod m).
\]

Il existe \(m^2-m\) tels décalages parmi les \(m^2-1\) décalages non nuls, soit une proportion

\[
\frac{m^2-m}{m^2-1}=\frac{m}{m+1}\longrightarrow1.
\]

Les décalages multiples de \(m\), non couverts par cet encadrement, ont une proportion \(1/(m+1)\). Pour que le quantile croissant d'ordre \(q\) soit encadré, il suffit donc que

\[
\frac1{m+1}<q<\frac m{m+1}.
\]

Ces deux inégalités sont satisfaites, pour tout \(q\in(0,1)\) fixé, dès que \(m\) est assez grand. Cela établit les bornes quantiles et l'échelle \(\Theta(\sqrt T)\).

Enfin, toute période \(d\) du mot doit préserver \(M\). Comme tous ses points sont congrus à \(m-1\) modulo \(m\), on doit avoir \(d=km\). Sur les indices de blocs, le motif est

\[
0,1,0,1,\ldots,0,
\]

avec une unique paire cyclique de zéros consécutifs. Une rotation qui préserve ce motif doit fixer cette paire, donc \(k=0\pmod m\). La période minimale est bien \(m^2\).

### Portée conceptuelle

Ce théorème établit une **échelle intermédiaire de résolution observationnelle** avec un alphabet de sortie fixe. Il ne suffit pas, à lui seul, à établir une flèche du temps : \(F\) est une permutation réversible et la définition de \(\rho\) ne distingue pas encore passé et futur. Le résultat sépare donc rigoureusement deux notions :

\[
\boxed{
\text{temps nécessaire pour distinguer}
\ \not\equiv\ 
\text{orientation irréversible du temps}.
}
\]

Pour obtenir une véritable flèche, il faut ajouter un invariant asymétrique sous \(F\leftrightarrow F^{-1}\), par exemple une différence entre résolutions prédictive et rétrodictive, ou une production d'information conditionnelle dépendant du sens temporel.

## 15. Théorème d'impossibilité pour la résolution directionnelle

La première proposition naturelle consistait à définir

\[
\Delta\rho_q=\rho_q^+-\rho_q^-,
\]

en comparant le premier désaccord lu vers le futur et vers le passé. Cette quantité est toujours nulle sur un mot cyclique uniformément échantillonné.

### Énoncé

Soit \(s=(s_t)_{t\in\mathbb Z_T}\) un mot cyclique quelconque. Pour un décalage \(d\), posons

\[
r_{n,d}^{+}=\min\{k\ge0:s_{n+k}\ne s_{n+d+k}\},
\]

\[
r_{n,d}^{-}=\min\{k\ge0:s_{n-k}\ne s_{n+d-k}\}.
\]

Alors, pour chaque \(d\), les deux familles indexées par les phases ont le même multiensemble :

\[
\boxed{
\{r_{n,d}^{+}:n\in\mathbb Z_T\}
=
\{r_{n,d}^{-}:n\in\mathbb Z_T\}.
}
\]

Tous leurs quantiles, moyennes et maxima sont donc égaux. En particulier,

\[
\boxed{\Delta\rho_q=0}
\]

pour toute agrégation uniforme sur les phases et les décalages.

### Preuve

Fixons \(d\) et considérons le mot binaire d'accord

\[
a_n=\mathbf1_{\{s_n=s_{n+d}\}}.
\]

Sur chaque segment maximal de \(\ell\) valeurs égales à 1, suivi et précédé d'un 0, les attentes vers l'avant sont

\[
\ell,\ell-1,\ldots,1,
\]

tandis que les attentes vers l'arrière sont

\[
1,2,\ldots,\ell.
\]

Les zéros contribuent 0 dans les deux sens. Les deux multiensembles sont donc identiques segment par segment. Si \(a_n=1\) partout, les deux résolutions sont infinies partout et l'égalité reste vraie.

Ainsi, une flèche temporelle ne peut pas être extraite de \(\rho\) en changeant seulement le sens de lecture.

## 16. Construction combinant Régime B et chiralité temporelle

On peut cependant conserver le Régime B et ajouter une orientation observable explicite.

### Construction

Prenons le même compteur \(F\), avec \(m\ge5\) et \(3\nmid m\), mais l'observation à alphabet fixe \(\{0,1,2,3\}\)

\[
\widetilde\pi_m(a,b)=
\begin{cases}
1+(b\bmod3),&a=m-1,\\
0,&a\ne m-1.
\end{cases}
\]

Chaque bloc de longueur \(m\) se termine ainsi par une impulsion colorée, selon

\[
1,2,3,1,2,3,\ldots
\]

### Période et résolution

Le support non nul contient exactement une position par bloc. Toute période doit donc être de la forme \(km\). Une telle période induirait une rotation du mot de couleurs

\[
c_b=1+(b\bmod3),\qquad 0\le b<m.
\]

Supposons qu'une rotation non nulle de \(k\) blocs, \(1\le k<m\), préserve les couleurs. En prenant \(b=0\), on obtient \(c_k=c_0\), donc \(k\equiv0\pmod3\). En prenant \(b=m-k\), dont l'image après rotation est le bloc 0, on obtient \(c_{m-k}=c_0\), donc \(m-k\equiv0\pmod3\). Il s'ensuivrait \(m\equiv0\pmod3\), contrairement à l'hypothèse. La période minimale est donc

\[
\boxed{T_{\rm eff}=m^2.}
\]

Si \(d\not\equiv0\pmod m\), les deux supports non nuls sont disjoints et forment deux classes résiduelles modulo \(m\). En posant \(r=d\bmod m\), les écarts entre désaccords alternent entre \(r\) et \(m-r\). Par conséquent,

\[
\boxed{
\rho(d)=\max(r,m-r)-1.
}
\]

Pour tous les quantiles fixes \(q\in(0,1)\),

\[
\boxed{\rho_q=\Theta(m)=\Theta(\sqrt T).}
\]

### Chiralité

Soit \(Q_m^+(i,j)\) la fréquence des transitions entre deux impulsions colorées successives dans le sens direct, et

\[
Q_m^-(i,j)=Q_m^+(j,i)
\]

la distribution renversée. Définissons

\[
\mathcal A_m=
\frac12\sum_{i,j}|Q_m^+(i,j)-Q_m^-(i,j)|.
\]

Un comptage exact donne

\[
\boxed{
\mathcal A_m=
\begin{cases}
\dfrac{m-1}{m},&m\equiv1\pmod3,\\[2mm]
\dfrac{m-2}{m},&m\equiv2\pmod3.
\end{cases}}
\]

Donc

\[
\boxed{\mathcal A_m\longrightarrow1.}
\]

Cette famille possède simultanément une période effective \(T=m^2\), une résolution quantile \(\Theta(\sqrt T)\) et une chiralité observable asymptotiquement maximale.

### Limite physique

La chiralité distingue les deux orientations lorsque les étiquettes \(1,2,3\) sont maintenues fixes. Elle n'est pas encore une production thermodynamique d'entropie : la dynamique microscopique reste inversible et son mouvement inverse existe. Il faut donc distinguer trois niveaux :

1. **résolution temporelle** : combien de temps faut-il pour distinguer deux phases ?
2. **chiralité temporelle** : les motifs orientés diffèrent-ils de leurs renversés ?
3. **irréversibilité** : existe-t-il une dissipation ou une production d'entropie positive relativement à une involution physique de renversement ?

Notre construction atteint rigoureusement les deux premiers niveaux, pas encore le troisième.

## 17. Niveau 3 : production d'entropie et irréversibilité

### Pourquoi le déterminisme fini ne suffit pas

Une production d'entropie trajectorielle doit être définie relativement à une opération physique de renversement \(\Theta\). Si une permutation déterministe \(F\) satisfait

\[
\Theta F\Theta=F^{-1}
\]

et si la mesure stationnaire est \(\Theta\)-invariante, la loi des trajectoires directes coïncide avec celle des trajectoires renversées. Leur divergence relative est donc nulle.

Si, au contraire, on compare une transition déterministe \(x\mapsto F(x)\) à une transition inverse qui a probabilité zéro sous la dynamique directe, les deux lois de chemins deviennent singulières et la divergence de Kullback–Leibler est infinie. Ce n'est pas un taux fini exploitable.

Ainsi, dans notre cadre fini, une production stationnaire finie et strictement positive requiert soit :

1. des transitions stochastiques dans les deux sens;
2. un environnement ou réservoir explicitement modélisé;
3. ou un régime transitoire non stationnaire, distinct de l'analyse des cycles récurrents.

Cette conclusion est conforme à la théorie des réseaux de chaînes maîtresses de Schnakenberg et à l'action de renversement de Lebowitz–Spohn.

## 18. Théorème du cycle stochastique biaisé

Soit \(T\ge3\) et une chaîne de Markov sur \(\mathbb Z_T\) définie par

\[
P(x,x+1)=p,
\qquad
P(x,x-1)=q=1-p,
\qquad
\frac12<p<1.
\]

La mesure uniforme

\[
\mu(x)=\frac1T
\]

est stationnaire. Le courant moyen par pas vaut

\[
J=p-q>0.
\]

La production d'entropie stationnaire par pas, en logarithmes naturels, est

\[
\begin{aligned}
\sigma
&=\sum_x\mu(x)\sum_yP(x,y)
\log\frac{\mu(x)P(x,y)}{\mu(y)P(y,x)}\\
&=p\log\frac pq+q\log\frac qp.
\end{aligned}
\]

Donc

\[
\boxed{
\sigma=(p-q)\log\frac pq>0.
}
\]

Pour une trajectoire stationnaire de \(n\) pas, notons \(\mathbb P_n\) sa loi et \(\mathbb P_n^R\) la loi du chemin renversé sous la même dynamique. L'indépendance des incréments donne

\[
\boxed{
D_{\mathrm{KL}}(\mathbb P_n\|\mathbb P_n^R)=n\sigma.
}
\]

L'irréversibilité est donc extensive dans le temps.

### Relation de fluctuation exacte

Si

\[
K_n=\#\{\text{pas }+1\}-\#\{\text{pas }-1\}
\]

est le courant net, les chemins de courant \(k\) et \(-k\) ont les mêmes coefficients combinatoires. Par conséquent,

\[
\boxed{
\frac{\Pr(K_n=k)}{\Pr(K_n=-k)}
=\left(\frac pq\right)^k
=e^{k\log(p/q)}.
}
\]

La variable d'entropie trajectorielle

\[
S_n=K_n\log\frac pq
\]

vérifie donc

\[
\boxed{
\frac{\Pr(S_n=s)}{\Pr(S_n=-s)}=e^s,
\qquad
\mathbb E[S_n]=n\sigma.
}
\]

Il s'agit d'une version élémentaire exacte de la symétrie de fluctuation pour notre cycle biaisé.

### Limites singulières

- Si \(p=q=1/2\), alors \(\sigma=0\) : équilibre et absence de courant.
- Si \(p\to1\), alors \(q\to0\) et \(\sigma\to+\infty\) : les chemins inverses deviennent impossibles. La limite déterministe orientée est singulière, non une irréversibilité finie.

## 19. Nouvelle architecture de la théorie du temps

L'audit conduit à trois invariants logiquement indépendants :

| Niveau | Quantité | Question mesurée |
|---|---|---|
| Résolution | \(\rho_q\) | Combien de temps faut-il pour distinguer deux phases ? |
| Chiralité | \(\mathcal A\) | Les motifs observés distinguent-ils une orientation ? |
| Irréversibilité | \(\sigma\) | Les trajectoires inverses sont-elles statistiquement moins probables ? |

Les implications générales

\[
\rho_q\text{ intermédiaire}\Rightarrow\mathcal A>0,
\qquad
\mathcal A>0\Rightarrow\sigma>0
\]

sont toutes deux fausses sans hypothèses supplémentaires.

Nous disposons maintenant de modèles témoins séparés :

- compteur binaire impair : \(\rho_q=\Theta(\sqrt T)\), mais \(\mathcal A=0\) et aucune production stationnaire;
- compteur coloré : \(\rho_q=\Theta(\sqrt T)\) et \(\mathcal A\to1\), mais dynamique microscopique réversible;
- cycle stochastique biaisé : \(\sigma>0\) et divergence de chemins extensive.

La prochaine question réellement ouverte est de construire une même famille locale, avec alphabet et rayon bornés, réalisant simultanément

\[
\boxed{
\rho_q=\Theta(T^\alpha),\quad0<\alpha<1,
\qquad
\mathcal A>0,
\qquad
0<\sigma<\infty.
}
\]

## 20. Références pour l'irréversibilité

- J. Schnakenberg, « Network theory of microscopic and macroscopic behavior of master equation systems », *Reviews of Modern Physics* 48, 571–585 (1976), [DOI](https://doi.org/10.1103/RevModPhys.48.571).
- J. L. Lebowitz, H. Spohn, « A Gallavotti–Cohen-Type Symmetry in the Large Deviation Functional for Stochastic Dynamics », *Journal of Statistical Physics* 95, 333–365 (1999), [DOI](https://doi.org/10.1023/A:1004589714161), [prépublication](https://arxiv.org/abs/cond-mat/9811220).

## 21. Théorème unifié : modèle local à particule marquée

La coexistence des trois niveaux peut être obtenue dans une seule famille locale, à alphabet et rayon bornés.

### Substrat

Prenons

\[
m\equiv3\pmod6,
\qquad
T=m^2,
\]

et un anneau de \(T\) sites. Chaque site \(j\in\mathbb Z_T\) porte deux étiquettes immobiles :

\[
u_j\in\{0,1\},
\qquad
c_j\in\mathbb Z_3.
\]

Le canal sparse est défini, en écrivant \(j=bm+a\), par

\[
u_j=
\begin{cases}
b\bmod2,&a=m-1,\\
0,&a\ne m-1,
\end{cases}
\]

et le canal coloré par

\[
c_j=j\bmod3.
\]

Comme \(m\) est impair, le mot sparse a la période minimale \(T=m^2\). Comme \(3\mid T\), le canal coloré est parfaitement périodique de période 3. La paire \((u_j,c_j)\) possède donc la période minimale \(T\).

### Dynamique locale

On ajoute une variable d'occupation

\[
\eta_j\in\{0,1\},
\qquad
\sum_j\eta_j=1.
\]

L'unique particule située au site \(j\) saute vers \(j+1\) avec probabilité \(p\), et vers \(j-1\) avec probabilité \(q=1-p\), où

\[
\frac12<p<1.
\]

La transition ne lit que le site occupé et ses deux voisins. Le rayon vaut donc 1. L'alphabet par site est

\[
\{0,1\}\times\mathbb Z_3\times\{0,1\},
\]

de cardinal

\[
\boxed{2\times3\times2=12,}
\]

indépendant de \(m\) et de \(T\). Aucun bruit global partagé n'est nécessaire : le choix aléatoire est effectué localement au site occupé.

L'observateur marqué, transporté par la particule, lit seulement les deux étiquettes \((u_j,c_j)\) du site courant.

### Résolution intermédiaire

Couplons deux particules initialement séparées d'un décalage \(d\), en leur appliquant les mêmes incréments aléatoires. Leur séparation reste égale à \(d\). Elles produisent des valeurs sparse différentes exactement lorsque la particule de référence atteint

\[
D_d=M\mathbin\triangle(M-d),
\]

où \(M=\{j:u_j=1\}\).

Pour \(d\not\equiv0\pmod m\), on a \(|D_d|=m-1\), et le plus grand intervalle sans désaccord est au plus \(3m\). Géométriquement,

\[
\left\lceil\frac{m^2}{m-1}\right\rceil-1
\le\rho(d)\le3m-1.
\]

Cette conclusion s'étend au temps stochastique de premier désaccord. Posons

\[
v=p-q>0.
\]

Depuis toute phase, un point de \(D_d\) se trouve à une distance orientée d'au plus \(3m\). Le temps moyen nécessaire à une marche biaisée pour progresser de \(\ell\) unités est \(\ell/v\); le quantile supérieur est donc \(O(m/v)\).

Inversement, les voisinages de rayon \(r\) des \(m-1\) points de \(D_d\) contiennent au plus

\[
(2r+1)(m-1)
\]

phases. En prenant \(r=c_qm\) avec une constante \(c_q>0\) assez petite, une proportion fixée des phases reste à distance au moins \(c_qm\) de tout désaccord. Une marche à pas voisins ne peut les résoudre en moins de \(c_qm\) pas.

Ainsi, pour chaque quantile fixe non extrême, pris sur les phases, les décalages non multiples de \(m\) et le bruit,

\[
\boxed{
\rho_q^{\rm stoch}=\Theta(m)=\Theta(\sqrt T).
}
\]

En particulier, pour la médiane, on peut choisir des constantes explicites de la forme

\[
\frac m8-O(1)
\le\rho_{50}^{\rm stoch}
\le\frac{6m}{p-q}.
\]

Ces constantes ne sont pas optimales; seule l'échelle est utilisée.

### Chiralité du canal coloré

Sous la mesure stationnaire uniforme de la position, le canal \(c_j=j\bmod3\) évolue selon

\[
c\longrightarrow c+1\pmod3
\quad\text{avec probabilité }p,
\]

\[
c\longrightarrow c-1\pmod3
\quad\text{avec probabilité }q.
\]

Les trois arêtes positives et les trois arêtes négatives sont disjointes. La distance totale de variation entre les transitions directes et renversées vaut donc

\[
\boxed{
\mathcal A=|p-q|=2p-1>0.
}
\]

### Production d'entropie

La position de la particule suit exactement le cycle stochastique biaisé. Sa production stationnaire est

\[
\boxed{
\sigma=(p-q)\log\frac pq,
\qquad
0<\sigma<\infty.
}
\]

Le canal coloré conserve entièrement cette irréversibilité : il permet de reconnaître si chaque saut s'est effectué dans le sens positif ou négatif. Sa divergence de chemins observés vaut donc également \(n\sigma\).

### Conclusion du théorème

Pour tout \(m\equiv3\pmod6\) et tout \(p\in(1/2,1)\), cette famille possède simultanément

\[
\boxed{
\begin{aligned}
T_{\rm phase}&=m^2,\\
\rho_q^{\rm stoch}&=\Theta(\sqrt T),\\
\mathcal A&=2p-1>0,\\
\sigma&=(2p-1)\log\frac p{1-p}\in(0,\infty).
\end{aligned}}
\]

Le rayon dynamique est 1 et l'alphabet local contient 12 états, uniformément en \(m\).

Ici \(T_{\rm phase}\) désigne le nombre de positions distinctes de la particule, équivalemment la période minimale du substrat observé. La chaîne stochastique n'a pas de « période orbitale » déterministe au sens utilisé auparavant pour la règle 90; employer le même symbole sans cette précision serait trompeur.

### Réserve exacte

La règle locale et l'alphabet sont uniformes, mais le substrat initial \((u_j,c_j)\) contient une structure organisée à l'échelle \(m\). Le théorème établit donc l'existence d'une famille locale bornée, pas encore l'émergence spontanée du Régime B depuis une mesure initiale translation-invariante simple.

La prochaine question est plus exigeante : produire les trois invariants dans une règle translation-invariante dont le substrat hiérarchique se forme dynamiquement, au lieu d'être encodé dans l'état initial.

## 14. Phénomènes révélés par l'exploration de la structure

Cette section sépare les identités exactes propres au substrat, les conséquences classiques de la marche biaisée et les interprétations qui restent à tester.

### 14.1 Deux populations de décalages

Les décalages ordinaires, \(d\not\equiv0\pmod m\), ont déjà été traités : leur résolution déterministe est comprise entre des constantes multipliées par \(m\). Ils forment une proportion

\[
1-\frac{m-1}{m^2-1}=1-O(m^{-1})
\]

de tous les décalages non nuls.

Pour les \(m-1\) décalages exceptionnels \(d=km\), \(1\le k<m\), le calcul exact donne au contraire

\[
\boxed{
\rho(km)=
\begin{cases}
(k+1)m-1,&k\text{ impair},\\
(m-k+1)m-1,&k\text{ pair}.
\end{cases}}
\]

Comme \(m\) est impair, les valeurs obtenues sont

\[
2m-1,\,4m-1,\,\ldots,\,(m-1)m-1,
\]

chacune avec multiplicité deux. Leur minimum est donc \(2m-1\), tandis que leur maximum vaut

\[
T-m-1=\Theta(T).
\]

Il existe ainsi une population rare, de masse exacte

\[
\frac{m-1}{m^2-1}=\frac1{m+1}=\Theta(T^{-1/2}),
\]

qui remplit presque uniformément toutes les échelles macroscopiques entre \(0\) et \(T\). Ce résultat a été vérifié exhaustivement par le script jusqu'à \(m=99\), soit 850 cas sans échec; la formule elle-même découle directement de la parité des blocs sparse et ne dépend pas de cette vérification numérique.

### 14.2 Couche limite des quantiles extrêmes

Cette population rare est invisible à tout quantile fixé \(q<1\) lorsque \(m\to\infty\) : on retrouve alors 

\[
\rho_q=\Theta(m)=\Theta(\sqrt T).
\]

Elle devient cependant visible si le quantile approche 1 à la même vitesse que sa masse. Pour

\[
q_m=1-\frac{\lambda}{m},
\qquad 0<\lambda<1,
\]

la distribution discrète précédente implique

\[
\boxed{
\frac{\rho_{q_m}}{T}\longrightarrow1-\lambda.
}
\]

La loi en \(\sqrt T\) est donc une loi de masse, et non une borne uniforme sur toutes les paires. Les limites « taille infinie » et « quantile tendant vers 1 » ne commutent pas. C'est le phénomène structurel le plus spécifique à notre construction.

### 14.3 Crossover dérive--diffusion sous faible biais

Posons

\[
v_m=2p_m-1\asymp m^{-\beta}.
\]

Le paramètre sans dimension qui commande le premier passage entre deux marqueurs séparés de \(O(m)\) est \(m v_m\). Il compare le temps balistique \(m/v_m\) au temps diffusif \(m^2\). On obtient

\[
\boxed{
\tau_m\asymp
\begin{cases}
m^{1+\beta}=T^{(1+\beta)/2},&\beta<1,\\
m^2=T,&\beta\ge1.
\end{cases}}
\]

Le seuil \(\beta=1\), équivalent à \(m v_m=O(1)\), est un crossover critique de taille finie, pas une transition de phase thermodynamique. Le calcul exact du temps moyen de sortie d'une marche biaisée sur \([-m,m]\) reproduit les exposants \(1+\beta\) puis 2 dans les tests numériques.

Cette partie est une manifestation de résultats classiques de premier passage pour les marches aléatoires biaisées et du régime de faible asymétrie; elle ne constitue pas à elle seule une nouveauté du modèle.

### 14.4 Seuil de détectabilité de la flèche du temps

Dans le même régime,

\[
\mathcal A_m=v_m\asymp T^{-\beta/2}
\]

et

\[
\sigma_m=v_m\log\frac{1+v_m}{1-v_m}
=2v_m^2+O(v_m^4)
\asymp T^{-\beta}.
\]

La production d'entropie accumulée pendant un temps de résolution vaut donc, à l'échelle,

\[
\boxed{
\sigma_m\tau_m\asymp
\begin{cases}
2m^{1-\beta}=2T^{(1-\beta)/2},&\beta<1,\\
O(1),&\beta=1,\\
2m^{2-2\beta}=2T^{1-\beta},&\beta>1.
\end{cases}}
\]

Il en résulte trois régimes opérationnels : une flèche cumulée de plus en plus nette pour \(\beta<1\), une quantité finie d'information temporelle au seuil, et une flèche indétectable sur le seul temps de résolution pour \(\beta>1\). Dans ce dernier cas, l'orientation microscopique existe encore pour chaque taille finie, mais il faut observer beaucoup plus longtemps que \(\rho\) pour l'estimer avec une fiabilité constante.

### 14.5 Portée et statut

Les phénomènes établis dans cette construction sont donc :

1. une séparation exacte entre une masse bulk à l'échelle \(\sqrt T\) et une queue rare à l'échelle \(T\);
2. une couche limite de quantiles de largeur \(T^{-1/2}\);
3. un crossover dérive--diffusion gouverné par \(m(2p-1)\);
4. un seuil simultané de détectabilité entropique au même exposant \(\beta=1\).

Les points 3 et 4 reposent sur la théorie standard des marches biaisées, bien que leur couplage aux invariants \(\rho,\mathcal A,\sigma\) soit utile ici. Les points 1 et 2 sont des conséquences exactes du substrat sparse particulier. Une recherche bibliographique plus large serait nécessaire avant toute revendication d'originalité générale.

## 15. Théorème de distribution complète et banc de réfutation

### 15.1 Convention de quantile

Dans cette section, \(\rho(d)\) est la résolution déterministe en pire phase du canal sparse pour le décalage \(d\in\{1,\ldots,T-1\}\). Le quantile empirique à gauche est

\[
\rho_q=\inf\left\{r:
\frac1{T-1}\#\{d:\rho(d)\le r\}\ge q
\right\}.
\]

Cette convention est indispensable : changer la mesure sur les décalages ou mélanger ce quantile avec le temps de premier passage stochastique produit un autre objet.

### 15.2 Théorème

Soit \(m\) impair, \(T=m^2\), et soit \(M\) le support formé par la dernière position de chaque bloc impair de longueur \(m\). Alors :

1. le mot sparse a pour période minimale \(T\);
2. pour \(d\not\equiv0\pmod m\),

\[
\left\lceil\frac{m^2}{m-1}\right\rceil-1
\le \rho(d)\le3m-1;
\]

3. pour \(d=km\), \(1\le k<m\),

\[
\rho(km)=
\begin{cases}
(k+1)m-1,&k\text{ impair},\\
(m-k+1)m-1,&k\text{ pair};
\end{cases}
\]

4. pour chaque \(q\in(0,1)\) fixé,

\[
\rho_q=\Theta(m)=\Theta(\sqrt T);
\]

5. pour \(q_m=1-\lambda/m\), avec \(0<\lambda<1\),

\[
\frac{\rho_{q_m}}{T}\longrightarrow1-\lambda.
\]

### 15.3 Preuve de la partie extrême

Les points 1 à 3 ont été établis par le calcul des supports et des intervalles sans désaccord. Pour les décalages multiples de \(m\), les valeurs sont exactement

\[
2jm-1,\qquad
1\le j\le\frac{m-1}{2},
\]

chacune deux fois. Tous les autres décalages sont au plus \(3m-1\). Le nombre total de décalages est

\[
T-1=(m-1)(m+1),
\]

et la population exceptionnelle en contient \(m-1\), soit la proportion exacte \(1/(m+1)\).

Un quantile fixé finit donc dans la population ordinaire, ce qui donne le point 4. Pour \(q_m=1-\lambda/m\), le nombre de valeurs situées au-dessus du quantile est asymptotiquement

\[
(1-q_m)(T-1)\sim\lambda m.
\]

Dans la liste exceptionnelle, dont chaque niveau apparaît deux fois, retirer les \(\lambda m+o(m)\) plus grandes valeurs place le seuil au niveau

\[
(1-\lambda)m^2+o(m^2).
\]

Après division par \(T=m^2\), on obtient le point 5. Les erreurs d'arrondi du rang et la correction \(-1\) disparaissent après normalisation par \(T\).

Le calcul direct de tous les \(T-1\) décalages confirme cette convergence pour
\(m=33,63,123,243\) et \(\lambda=0.25,0.5,0.75\). À \(m=243\), les trois valeurs
de \(\rho_{q_m}/T\) sont respectivement \(0.74895\), \(0.50204\) et \(0.24690\),
à comparer aux limites \(0.75\), \(0.50\) et \(0.25\). Cette vérification
reproduit le théorème; elle ne remplace pas la preuve précédente.

### 15.4 Résultats du banc de réfutation

#### Parité de \(m\)

Le test exhaustif pour \(3\le m\le99\) donne 2 450 vérifications de la formule exceptionnelle pour \(m\) impair, sans échec.

Pour \(m\) pair, le résultat est réfuté de manière structurelle :

\[
\boxed{\operatorname{per}(u)=2m\ne m^2.}
\]

De plus, tous les décalages \(d=2\ell m\), \(1\le\ell<m/2\), préservent le mot sparse et ont donc \(\rho(d)=\infty\). L'imparité de \(m\) est une hypothèse nécessaire à la période sparse \(m^2\).

#### Rôle de \(m\equiv3\pmod6\)

La formule de résolution sparse exige seulement que \(m\) soit impair. La condition plus forte

\[
m\equiv3\pmod6
\]

combine deux exigences indépendantes :

- \(m\) impair pour la période sparse \(m^2\);
- \(3\mid m^2\) pour que la coloration \(c_j=j\bmod3\) se referme sans couture sur l'anneau.

Elle est donc nécessaire à cette réalisation précise à trois couleurs, mais pas au théorème sparse pris isolément.

#### Bruit commun contre bruits indépendants

Sous bruit commun, les deux particules reçoivent le même incrément et leur séparation reste exactement \(d\). C'est ce qui réduit le problème à l'ensemble fixe \(M\triangle(M-d)\).

Sous deux incréments indépendants \(\xi_1,\xi_2\in\{-1,+1\}\), la séparation devient

\[
d' = d+\xi_2-\xi_1\in\{d-2,d,d+2\}.
\]

La réduction à un ensemble de désaccord fixe est donc fausse dans ce modèle. Cela réfute la preuve par couplage constant, mais ne suffit pas à déterminer la nouvelle loi de résolution; celle-ci reste à analyser comme problème distinct à deux particules.

#### Ajout d'une probabilité d'immobilisation

Si les probabilités sont \(p\) vers la droite, \(q\) vers la gauche et \(r=1-p-q\) de rester sur place, alors les boucles d'immobilisation sont invariantes par renversement. Pour le canal coloré,

\[
\mathcal A=|p-q|,
\qquad
\sigma=(p-q)\log\frac pq.
\]

Le mécanisme survit donc à l'immobilisation tant que \(p\ne q\). Le paramètre de crossover devient toujours \(m|p-q|\); seules les constantes temporelles changent.

#### Perturbation des marqueurs

Un test reproductible déplace chaque marqueur de \(0,\pm1,\pm2\) positions selon un hachage déterministe. Pour \(m=33,63,123,243\), le maximum exceptionnel normalisé passe respectivement de

\[
0.969,\ 0.984,\ 0.992,\ 0.996
\]

à

\[
0.181,\ 0.126,\ 0.065,\ 0.049.
\]

Ces données montrent que la hiérarchie exacte à l'échelle \(T\) est sensible à l'alignement des marqueurs. Elles ne constituent pas une preuve asymptotique : je ne peux pas confirmer, sur ce seul test, que toute perturbation bornée détruit nécessairement la queue macroscopique.

### 15.5 Bilan logique

Après réfutation :

- **démontré :** distribution exceptionnelle exacte, couche limite des quantiles, nécessité de l'imparité pour la période sparse;
- **robuste :** chiralité et production d'entropie sous ajout d'immobilisation;
- **propre à la réalisation choisie :** congruence \(m\equiv3\pmod6\) pour fermer le canal à trois couleurs;
- **non transféré :** preuve de résolution par séparation constante sous bruits indépendants;
- **indication numérique seulement :** fragilité de la queue macroscopique sous désalignement borné des marqueurs.

## 16. Robustesse et émergence sans alignement préparé

### 16.1 Critère géométrique exact

Soit \(u\) un mot binaire cyclique de longueur \(T\). Pour un décalage \(d\), posons

\[
D_d=\{j:u_j\ne u_{j+d}\}.
\]

La résolution \(\rho(d)\) est exactement la longueur du plus long intervalle
cyclique ne rencontrant pas \(D_d\). Par conséquent,

\[
\boxed{
\rho(d)\ge cT
\iff
\exists I,\ |I|\ge cT,\ 
u_j=u_{j+d}\quad\forall j\in I.
}
\]

Cette équivalence a été vérifiée par deux algorithmes indépendants sur 1 100
cas, sans échec; elle résulte surtout directement de la définition des
intervalles entre désaccords.

Une queue \(\Theta(T)\) n'est donc pas simplement produite par la faible densité
des marqueurs. Elle exige une symétrie translationnelle exacte sur une région
macroscopique.

### 16.2 Perturbations corrélées par domaines

Pour tester le rôle de la longueur de corrélation, chaque marqueur est déplacé
de \(0,\pm1,\pm2\), mais le déplacement est partagé par des domaines de \(B\)
blocs consécutifs. La longueur physique de corrélation est alors \(Bm\), et sa
fraction de l'anneau vaut

\[
\frac{Bm}{T}=\frac{B}{m}.
\]

Les résultats reproductibles sont :

| \(m\) | \(B\) | \(B/m\) | \(\max_d\rho(d)/T\) |
|---:|---:|---:|---:|
| 63 | 1 | 0,0159 | 0,1267 |
| 123 | 1 | 0,0081 | 0,0810 |
| 243 | 1 | 0,0041 | 0,0412 |
| 483 | 1 | 0,0021 | 0,0331 |
| 63 | 16 | 0,2540 | 0,5067 |
| 123 | 31 | 0,2520 | 0,5037 |
| 243 | 61 | 0,2510 | 0,5020 |
| 483 | 121 | 0,2505 | 0,5010 |
| 63 | 63 | 1 | 0,9839 |
| 123 | 123 | 1 | 0,9918 |
| 243 | 243 | 1 | 0,9959 |
| 483 | 483 | 1 | 0,9979 |

Le déplacement indépendant bloc par bloc fait décroître la queue normalisée
dans cette expérience. Une corrélation sur environ un quart des blocs produit
au contraire une résolution maximale proche de \(T/2\), et une perturbation
entièrement cohérente conserve presque \(T\).

Ces valeurs ne prouvent pas une loi universelle en \(B\). Elles confirment le
critère exact : la queue macroscopique survit lorsque la perturbation conserve
des domaines de symétrie eux-mêmes macroscopiques.

### 16.3 Comparaison avec les mots aléatoires

Pour des suites de lettres indépendantes de probabilités fixes, la longueur du
plus long accord consécutif est logarithmique. Avec optimisation sur les
décalages, Arratia et Waterman démontrent également une loi logarithmique pour
la plus longue correspondance de deux suites indépendantes :

R. Arratia et M. S. Waterman, *An Erdős–Rényi Law with Shifts*, Advances in
Mathematics 55 (1985), 13–23,
https://dornsife.usc.edu/msw/wp-content/uploads/sites/236/2023/09/msw-058.pdf

Ce résultat ne s'applique pas directement à notre ensemble sparse, dont la
densité tend vers zéro et dont les comparaisons utilisent le même mot décalé.
Il fournit néanmoins un contre-modèle rigoureux : le désordre indépendant à
densité fixe ne produit pas spontanément des accords de longueur
\(\Theta(T)\).

### 16.4 Ce qui peut émerger localement

Une dynamique locale de coarsening constitue un mécanisme crédible pour former
une longueur intermédiaire sans placer les marqueurs à l'avance. Dans la
dynamique unidimensionnelle de Glauber, les changements de spins sont locaux et
dépendent des voisins; le modèle est exactement analysable :

R. J. Glauber, *Time-Dependent Statistics of the Ising Model*, Journal of
Mathematical Physics 4 (1963), 294–307,
https://pubs.aip.org/aip/jmp/article/4/2/294/230204/Time-Dependent-Statistics-of-the-Ising-Model

Des parois de domaines qui diffusent et s'annihilent peuvent ainsi produire une
échelle de corrélation croissante. Cela suggère une construction où :

1. un champ local forme des domaines et des parois;
2. les parois jouent le rôle de marqueurs sparse;
3. une particule biaisée lit ces marqueurs et un canal orienté.

Mais cette proposition ne résout pas encore quatre difficultés :

- arrêter ou stabiliser le coarsening à l'échelle \(\sqrt T\) sans horloge globale;
- conserver une période effective \(T\);
- obtenir une mesure stationnaire compatible avec \(\rho,\mathcal A,\sigma\);
- produire des domaines de symétrie de taille \(\Theta(T)\) si la queue extrême
  est exigée.

Je ne peux donc pas confirmer qu'une règle locale translation-invariante simple
engendre déjà les quatre propriétés. Le coarsening fournit un candidat sérieux
pour le régime bulk \(\rho=\Theta(\sqrt T)\), pas encore pour la queue
macroscopique.

### 16.5 Conclusion de robustesse

L'exploration conduit à une séparation :

\[
\boxed{
\begin{aligned}
\text{échelle bulk }\sqrt T
&:\ \text{compatible avec une densité locale de défauts }T^{-1/2},\\
\text{queue extrême }T
&:\ \text{requiert une symétrie corrélée sur une fraction de }T.
\end{aligned}}
\]

La prochaine construction ne doit donc pas chercher à reproduire
accidentellement l'alignement initial. Elle doit choisir entre deux objectifs :

- abandonner la queue extrême et viser un Régime B bulk robuste;
- ou introduire un véritable mécanisme local d'ordre de longue portée capable
  de créer des domaines translationnellement cohérents macroscopiques.

## 17. Prototype auto-organisé par coarsening

### 17.1 Dynamique utilisée

Sur un anneau de \(T=m^2\) sites, on initialise des spins binaires indépendants.
Les parois entre spins différents sont ensuite représentées par des particules
qui :

1. effectuent des marches aléatoires continues à pas voisins;
2. s'annihilent deux à deux lorsqu'elles se rencontrent.

Cette dynamique \(A+A\to\varnothing\) est locale, translation-invariante et ne
contient aucune grille de marqueurs préalignée. Elle représente le secteur des
parois de domaines du coarsening unidimensionnel de type Glauber.

Le système est observé à l'âge

\[
t_{\mathrm{age}}=T.
\]

Comme une paroi diffuse sur une distance d'ordre \(\sqrt t\), l'échelle attendue
des domaines à cet âge est \(\sqrt T=m\). Cette motivation est issue du
coarsening diffusif; les exposants ci-dessous sont mesurés indépendamment dans
notre simulation.

### 17.2 Protocole

Pour

\[
m\in\{21,27,33,45,63,81\},
\]

on effectue 32 répétitions indépendantes. Pour chaque substrat final :

- 256 décalages non nuls sont échantillonnés;
- toutes les phases de départ sont comptées exactement pour ces décalages;
- on mesure \(\rho_{50}\), \(\rho_{90}\) et le maximum sur l'échantillon;
- on calcule la période minimale du mot de parois.

Il s'agit donc de 192 substrats et de 49 152 comparaisons de décalages. Le
maximum rapporté n'est pas le maximum exhaustif sur les \(T-1\) décalages.

### 17.3 Résultats

| \(m\) | \(T\) | parois moyennes | fraction de période \(T\) | \(\rho_{50}/m\) | \(\rho_{90}/m\) | maximum échantillonné/\(m\log m\) |
|---:|---:|---:|---:|---:|---:|---:|
| 21 | 441 | 6,250 | 1,000 | 1,083 | 3,287 | 2,832 |
| 27 | 729 | 7,438 | 1,000 | 1,174 | 3,428 | 2,688 |
| 33 | 1 089 | 9,688 | 1,000 | 1,083 | 3,320 | 2,679 |
| 45 | 2 025 | 12,500 | 1,000 | 1,140 | 3,401 | 2,649 |
| 63 | 3 969 | 17,562 | 1,000 | 1,126 | 3,517 | 2,741 |
| 81 | 6 561 | 22,500 | 1,000 | 1,150 | 3,415 | 2,557 |

Les régressions log--log en fonction de \(T\) donnent :

\[
\begin{array}{c|c}
\text{quantité}&\text{exposant ajusté}\\ \hline
\#\text{parois}&0,481\\
\rho_{50}&0,512\\
\rho_{90}&0,516\\
\rho_{\max}^{\mathrm{échantillon}}&0,612
\end{array}
\]

Les rapports \(\rho_{50}/m\) et \(\rho_{90}/m\) restent approximativement
constants, tandis que le maximum croît plus vite et se normalise beaucoup mieux
par \(m\log m\). Les données soutiennent donc :

\[
\boxed{
\rho_q=\Theta(\sqrt T)
\quad\text{pour les quantiles de phase fixes,}
}
\]

et sont compatibles avec

\[
\rho_{\mathrm{extrême}}
=\Theta(\sqrt T\log T).
\]

La première relation est une conclusion numérique robuste sur le domaine
testé, pas encore un théorème pour ce protocole. La seconde est seulement une
hypothèse d'échelle soutenue par les données et par la théorie des valeurs
extrêmes des longueurs de domaines.

### 17.4 Ce que le prototype accomplit

Le prototype obtient sans alignement préparé :

- une densité de marqueurs décroissante proche de \(T^{-1/2}\);
- une résolution quantile proche de \(T^{1/2}\);
- une période minimale \(T\) dans les 192 réalisations testées;
- une séparation nette entre quantiles typiques et phases extrêmes.

Il montre aussi que l'ancien choix « pire phase » n'est pas neutre : dans un
substrat auto-organisé aléatoire, les plus grands domaines introduisent une
correction logarithmique absente de la grille régulièrement espacée.

### 17.5 Limites non résolues

Ce n'est pas encore la mécanique finale :

1. le substrat est lu après un arrêt externe à l'âge \(T\);
2. cet arrêt dépend de la taille globale et n'est pas produit par une règle
   autonome;
3. la particule biaisée et le canal coloré ne sont pas encore couplés à ce
   substrat évolutif dans une mesure stationnaire commune;
4. la loi \(\rho_q=\Theta(\sqrt T)\) reste à démontrer;
5. la période \(T\) est observée empiriquement, pas garantie pour chaque
   réalisation.

Je ne peux donc pas confirmer que le problème d'émergence autonome est résolu.
En revanche, le principal obstacle a changé : il ne faut plus inventer les
marqueurs sparse, mais remplacer l'arrêt externe par un mécanisme local de
stabilisation ou une définition réellement non stationnaire de l'observateur.

## 18. Stabilisation autonome par signal circulant

### 18.1 Mécanisme local à trois tours

On ajoute une balise unique \(B\) et un signal \(H\) se déplaçant
déterministement d'un site vers la droite à chaque unité de temps. La règle
reste identique sur tous les sites; seule la condition initiale contient une
balise distinguée.

Le protocole comporte trois tours :

1. **tour d'armement**, de \(0\) à \(T\) : le signal parcourt l'anneau pendant
   que les parois coarsissent;
2. **tour d'enregistrement**, de \(T\) à \(2T\) : au passage sur le site \(j\),
   le signal copie la présence locale d'une paroi dans une mémoire immuable;
3. **tour de nettoyage**, de \(2T\) à \(3T\) : le signal place le champ de
   coarsening dans un état quiescent, sans modifier la mémoire enregistrée.

Le retour du signal à la balise sépare localement les tours. Aucune cellule ne
connaît \(T\), et aucune horloge globale ne déclenche l'arrêt. La propagation de
signaux et la synchronisation par une cellule initialement distinguée
appartiennent au cadre classique du *firing squad synchronization problem*;
voir par exemple la synthèse :

H. Umeo, *An Overview of Recent Solutions to and Lower Bounds for the
Firing Squad Synchronization Problem*,
https://arxiv.org/abs/1701.01045

Notre protocole est plus simple qu'un firing squad complet : il ne cherche pas
à faire changer tous les sites simultanément, mais utilise un balayage local.

### 18.2 Couche colorée et observateur

Pendant le tour d'enregistrement, le signal transporte un état
\(c\in\mathbb Z_3\) et effectue

\[
c\longmapsto c+1\pmod3
\]

à chaque déplacement. Il écrit simultanément le bit de paroi \(u_j\) et la
couleur \(c_j\). Pour les tailles \(3\mid T\), la coloration se referme sur
l'anneau.

Après le nettoyage, une particule observatrice saute à droite avec probabilité
\(p\) et à gauche avec probabilité \(q=1-p\). Elle lit la mémoire
\((u_j,c_j)\). On retrouve alors exactement

\[
\mathcal A=|p-q|,
\qquad
\sigma=(p-q)\log\frac pq.
\]

Une réalisation finie utilise un alphabet borné. Par exemple, sans
optimisation, on peut prendre les couches :

\[
\begin{aligned}
s&\in\{0,1\} &&\text{champ de coarsening},\\
M&\in\{\varnothing\}\cup(\{0,1\}\times\mathbb Z_3)
&&\text{mémoire : 7 états},\\
B&\in\{\text{absente, armée, enregistrement, complète}\},\\
H&\in\{\text{absent, armement, nettoyage}\}
\cup\{\text{enregistrement-}0,1,2\},\\
\eta&\in\{0,1\} &&\text{occupation de l'observateur}.
\end{aligned}
\]

Le produit brut donne au plus

\[
2\times7\times4\times6\times2=672
\]

états par site, indépendamment de \(T\). Beaucoup sont inaccessibles et ce
nombre n'est pas minimal. Les transitions du signal, de la paroi et de
l'observateur sont à rayon 1.

### 18.3 Simulation de l'enregistrement roulant

Le site \(j\) enregistre la présence d'une paroi à l'instant

\[
t_j=T+j,\qquad0\le j<T.
\]

Le test utilise à nouveau 32 répétitions pour chacune des six tailles
\(m=21,27,33,45,63,81\), et 256 décalages par réalisation.

| \(m\) | marqueurs moyens | fraction de période \(T\) | \(\rho_{50}/m\) | \(\rho_{90}/m\) | maximum échantillonné/\(m\log m\) |
|---:|---:|---:|---:|---:|---:|
| 21 | 5,250 | 1,000 | 2,216 | 6,557 | 4,003 |
| 27 | 6,344 | 1,000 | 2,140 | 5,818 | 3,897 |
| 33 | 8,500 | 1,000 | 2,204 | 6,781 | 4,193 |
| 45 | 9,688 | 1,000 | 2,525 | 7,976 | 4,514 |
| 63 | 15,000 | 1,000 | 1,884 | 5,870 | 3,723 |
| 81 | 19,219 | 1,000 | 1,922 | 6,026 | 3,967 |

Les exposants de régression en \(T\) sont :

\[
\begin{array}{c|c}
\#\text{marqueurs}&0,479\\
\rho_{50}&0,446\\
\rho_{90}&0,483\\
\rho_{\max}^{\mathrm{échantillon}}&0,626
\end{array}
\]

Sur ce domaine fini, les ratios \(\rho_{50}/m\) et \(\rho_{90}/m\) restent
bornés sans tendance monotone nette, tandis que la densité de marqueurs suit
bien l'exposant \(1/2\). Les données sont compatibles avec une résolution
quantile \(\Theta(\sqrt T)\), mais l'exposant médian \(0,446\) ne permet pas de
la déclarer démontrée.

Le balayage roulant augmente les constantes par rapport à un instantané
simultané, car les différents sites enregistrent des âges compris entre \(T\)
et \(2T\). La correction extrême proche de \(\sqrt T\log T\) persiste.

### 18.4 Statut exact

Ce mécanisme résout effectivement l'usage d'un ordre externe d'arrêt :

- la règle est locale et uniforme;
- le temps de formation est découvert par le retour d'un signal;
- la mémoire finale est stable;
- après nettoyage, le canal de lecture biaisé admet une mesure stationnaire et
  une production d'entropie finie.

Il conserve néanmoins deux hypothèses préparées :

1. une balise unique existe dans l'état initial;
2. les tailles considérées satisfont \(3\mid T\) pour le canal coloré.

La première n'est pas une grille hiérarchique à l'échelle \(\sqrt T\), mais elle
brise la symétrie translationnelle. Élire spontanément une unique balise sur un
anneau anonyme constitue un problème supplémentaire. Je ne peux pas confirmer
que cette élection puisse être obtenue avec les mêmes garanties, dans un temps
\(O(T)\), depuis une mesure initiale i.i.d. simple.

Le résultat actuel est donc :

\[
\boxed{
\text{mécanique locale autonome conditionnée par une balise unique,}
}
\]

et non encore une émergence entièrement spontanée depuis un état
translation-invariant sans marque.

## 19. La balise comme trace de l'observateur

### 19.1 Suppression de la balise extérieure

Le modèle unifié contient déjà exactement une particule observatrice. Il n'est
donc pas nécessaire d'ajouter une seconde singularité. Au temps initial,
l'observateur :

1. dépose un bit de balise \(b_J=1\) sur son site \(J\);
2. lance le signal d'armement;
3. reste dans un état de contrôle pendant les trois tours;
4. devient ensuite la particule biaisée qui lit la mémoire.

On choisit

\[
J\sim\operatorname{Unif}(\mathbb Z_T)
\]

indépendamment des spins initiaux i.i.d. La mesure initiale est alors
translation-invariante : une translation simultanée du champ et de \(J\) ne
change pas sa loi. Chaque réalisation choisit un repère, mais aucun site n'est
privilégié dans l'ensemble statistique.

Il faut distinguer :

\[
\boxed{
\text{symétrie de la loi}
\ne
\text{symétrie de chaque réalisation}.
}
\]

La règle locale commute avec les translations et la mesure initiale aussi;
l'origine individuelle est fournie par l'observateur marqué.

### 19.2 Période effective garantie

L'observation finale devient

\[
\pi_j=(u_j,c_j,b_j),
\]

où

\[
b_j=\mathbf1_{\{j=J\}}.
\]

Le mot \(b\) contient exactement un symbole 1. Si un décalage \(d\) préserve le
mot observé, il doit préserver la position de ce symbole unique :

\[
J+d\equiv J\pmod T.
\]

Donc

\[
d\equiv0\pmod T
\]

et

\[
\boxed{\operatorname{per}(\pi)=T}
\]

pour chaque réalisation, sans hypothèse probabiliste sur la mémoire de
coarsening.

### 19.3 Effet de la balise sur la résolution

Pour comparer deux phases séparées par \(d\), le canal de balise ajoute au plus
deux points de désaccord :

\[
D_d^{\mathrm{total}}
=D_d^{\mathrm{mémoire}}\cup\{J,J-d\}.
\]

Il ne peut donc qu'accélérer la résolution. Si \(g_{\max}(d)\) est le plus grand
intervalle de la mémoire sans désaccord, l'ajout d'un point ne modifie les temps
d'attente que pour les phases appartenant à l'intervalle qu'il coupe. Avec
\(r\) points ajoutés, la proportion de phases affectées est au plus

\[
\frac{r\,g_{\max}(d)}{T}.
\]

Ainsi, lorsque \(g_{\max}=o(T)\), un nombre fixe de canaux singuliers devient
négligeable pour les quantiles de phase fixes. Ce lemme explique pourquoi une
balise garantit la période sans imposer l'échelle de résolution bulk.

### 19.4 Nouveau test numérique avec canal de balise

Le programme calcule désormais la résolution de la paire
\((u,b)\), et non celle du seul bit de paroi. Le protocole comporte 16
répétitions pour chacune des six tailles et 256 décalages par réalisation.

| \(m\) | marqueurs moyens | période observée \(T\) | \(\rho_{50}/m\) | \(\rho_{90}/m\) | maximum échantillonné/\(m\log m\) |
|---:|---:|---:|---:|---:|---:|
| 21 | 5,875 | 1,000 | 1,336 | 4,494 | 3,136 |
| 27 | 6,500 | 1,000 | 1,688 | 4,782 | 3,340 |
| 33 | 8,250 | 1,000 | 1,761 | 6,070 | 3,797 |
| 45 | 11,500 | 1,000 | 1,719 | 5,665 | 3,774 |
| 63 | 15,812 | 1,000 | 1,725 | 5,568 | 3,454 |
| 81 | 18,750 | 1,000 | 1,770 | 5,500 | 3,648 |

Les exposants ajustés sont :

\[
\begin{array}{c|c}
\#\text{marqueurs}&0,459\\
\rho_{50}&0,571\\
\rho_{90}&0,567\\
\rho_{\max}^{\mathrm{échantillon}}&0,675
\end{array}
\]

Les exposants sont sensibles aux petites tailles, mais les rapports
\(\rho_{50}/m\) et \(\rho_{90}/m\) se stabilisent respectivement autour de
\(1,7\) et \(5,5\) pour les quatre plus grandes tailles testées. Les données
restent donc compatibles avec

\[
\rho_q=\Theta(\sqrt T)
\]

et un extrême amplifié par un logarithme. Je ne peux pas confirmer les
exposants asymptotiques à partir de ces 96 réalisations.

### 19.5 Mesure stationnaire finale

Après le troisième tour :

- le champ de coarsening est quiescent;
- la mémoire \((u,c,b)\) est fixe;
- le signal circulant a disparu;
- l'observateur suit seul la marche biaisée sur l'anneau.

Conditionnellement à toute mémoire réalisée, la position uniforme de
l'observateur est stationnaire. En mélangeant sur la loi translation-invariante
des mémoires produites, on obtient une mesure stationnaire annealed. Les
invariants restent

\[
\boxed{
\begin{aligned}
T_{\mathrm{phase}}&=T\quad\text{exactement},\\
\mathcal A&=2p-1,\\
\sigma&=(2p-1)\log\frac p{1-p}.
\end{aligned}}
\]

La résolution \(\rho_q=\Theta(\sqrt T)\) est soutenue numériquement mais reste
le seul élément asymptotique non démontré de cette version.

### 19.6 Frontière restante

La construction part d'une mesure translation-invariante contenant exactement
une particule marquée. Elle ne part pas d'un produit i.i.d. sur toutes les
couches, car la contrainte

\[
\sum_j\eta_j=1
\]

est globale. Cette contrainte existait déjà dans le modèle de l'observateur.

Par conséquent :

- **résolu :** aucune position spatiale prédéterminée, aucune grille sparse,
  aucune horloge globale, période \(T\) garantie;
- **non résolu :** création spontanée d'un observateur unique depuis une mesure
  entièrement i.i.d. avec alphabet fini.

Ce dernier problème relève de l'élection de leader stochastique sur un anneau
anonyme. Il est logiquement distinct de la formation du temps observé une fois
un observateur marqué admis.

## 20. Photographie simultanée synchronisée

### 20.1 Mécanisme proposé et portée réelle du test

On remplace le balayage d'enregistrement par un changement simultané de toutes
les cellules à un âge

\[
\tau_T=cT,\qquad c>0\text{ constant}.
\]

Une cellule initialement distinguée joue le rôle de général et de balise. Un
synchroniseur local à alphabet fini propage l'information, toutes les cellules
copient alors simultanément leur bit de paroi dans une mémoire immuable, puis
les couches transitoires sont nettoyées. L'existence de mécanismes locaux de
synchronisation relève du *firing squad synchronization problem* [Umeo,
synthèse](https://arxiv.org/abs/1701.01045).

Le programme `synchronized_snapshot_model.py` ne simule toutefois pas la table
d'états interne d'un tel synchroniseur : il simule exactement la couche
physique de coarsening au temps de tir supposé. Les valeurs (c=1,2,3) sont des
tests de sensibilité, et non les temps annoncés d'une construction particulière
de firing squad. **Je ne peux donc pas confirmer, avec ce seul programme, que
l'automate complet synchroniseur–coarsening a été implémenté.**

La mémoire observée est

\[
O_j=(\mathbf 1_{\{j\in M_{\tau_T}\}},\mathbf 1_{\{j=J\}}),
\]

où (J) est la balise unique, uniforme sur l'anneau dans la loi initiale. Son
second canal garantit exactement une période spatiale (T), réalisation par
réalisation, sans supposer que le motif aléatoire de parois ait pleine période.

### 20.2 Borne inférieure démontrée

Fixons un décalage non nul (d), et posons

\[
D_d=O\mathbin\triangle(O-d).
\]

Si (X) est une phase uniforme et si

\[
\mathbb E|M_{cT}|/T\le C_cT^{-1/2},
\]

alors

\[
\Pr(X\in D_d)\le 2C_cT^{-1/2}+2T^{-1}.
\]

Pour la distance orientée \(\rho(X,d)\) jusqu'au prochain désaccord, une borne
de l'union, sans aucune hypothèse d'indépendance, donne

\[
\Pr\{\rho(X,d)\le h\}
\le(h+1)\left(2C_cT^{-1/2}+2T^{-1}\right).
\]

Pour tout quantile fixe (q\in(0,1)), choisir une constante (a_{q,c}>0)
assez petite et (h=\lfloor a_{q,c}\sqrt T\rfloor) rend le membre droit
strictement inférieur à (q), pour (T) assez grand. Ainsi

\[
\boxed{\rho_q=\Omega(\sqrt T).}
\]

Cette implication est une preuve conditionnelle uniquement à la borne de
densité affichée, borne classique du coarsening diffusif unidimensionnel. Elle
n'utilise ni une approximation de Poisson, ni l'indépendance des parois.

### 20.3 Résultats numériques

Huit réalisations par couple ((m,c)), avec (T=m^2) et 256 décalages
échantillonnés par réalisation, donnent les exposants de régression suivants :

| (c) | exposant marqueurs | exposant \(\rho_{50}\) | exposant \(\rho_{90}\) | exposant maximum échantillonné |
|---:|---:|---:|---:|---:|
| 1 | 0,486 | 0,522 | 0,496 | 0,601 |
| 2 | 0,456 | 0,574 | 0,571 | 0,650 |
| 3 | 0,404 | 0,634 | 0,638 | 0,696 |

Pour (c=1), l'accord avec l'exposant (1/2) est particulièrement bon. Sur
les trois âges, 

\[
\rho_{50}/(m\sqrt c)\in[0{,}715,1{,}200],
\]

et, sauf la petite taille (m=21,c=3),

\[
\rho_{90}/(m\sqrt c)\in[2{,}530,4{,}036].
\]

Ces données sont compatibles avec \(\rho_q=\Theta(\sqrt{cT})\) pour (c)
fixé. Elles ne prouvent pas l'exposant; la dérive à (c=2,3) montre justement
que les tailles testées restent préasymptotiques.

### 20.4 Lemme manquant pour la borne supérieure

La densité seule ne suffit pas à borner les grands trous. Une conclusion
\(\rho_q=O(\sqrt T)\) suivrait, par exemple, d'une estimation uniforme du type

\[
\Pr\{D_d\cap I=\varnothing\}
\le A\exp\!\left(-a|I|/\sqrt T\right)
\]

pour les intervalles (I), les décalages pertinents et des constantes
indépendantes de (T). Mais une estimation d'intervalle vide pour
\(M_{cT}\) seule ne l'implique pas automatiquement : un motif peut localement
coïncider avec son translaté, précisément parce que
\(D_d=M_{cT}\triangle(M_{cT}-d)\).

Le statut exact est donc :

- période (T) : **démontrée** grâce à la balise;
- \(\rho_q=\Omega(\sqrt T)\) : **démontrée sous la borne classique de densité**;
- \(\rho_q=O(\sqrt T)\) : **ouverte**, réduite à une borne de vide pour la
  différence symétrique;
- comportement \(\Theta(\sqrt T)\) : **fortement compatible avec les
  simulations, non démontré**;
- automate synchroniseur complet : **mécanisme standard disponible en
  principe, mais table locale non encore intégrée au programme**.

## 21. Attaque du second moment

### 21.1 Variable testée

Pour une photographie (M=M_{cT}), un décalage (d\ne0), une phase uniforme
(X) et une fenêtre orientée (I_h(X)) de (h+1) sites, on définit

\[
N_h(d,X)=\left|I_h(X)\cap\bigl(O\triangle(O-d)\bigr)\right|.
\]

On a exactement

\[
\rho(X,d)>h\quad\Longleftrightarrow\quad N_h(d,X)=0.
\]

Le programme `second_moment_attack.py` teste (c\in\{1,2,3\}),
(m\in\{33,45,63,81\}), 12 réalisations par couple, 128 phases par
décalage et trois décalages dans chacune des classes suivantes :

- petits : (d=1,2,3);
- mésoscopiques : (d\simeq m/2,m,2m);
- macroscopiques : (d\simeq T/4,T/3,T/2).

Les fenêtres ont la longueur

\[
h+1=\lfloor K\sqrt{cT}\rfloor+1,
\qquad K\in\{0{,}5,1,2,4,8\}.
\]

Chaque cas est calculé avec et sans la balise. Les 144 réalisations contenaient
encore au moins une paroi à l'âge mesuré; le test ne rencontre donc pas ici de
réalisation complètement éteinte.

### 21.2 Résultat du test adversarial

Sur l'ensemble des tailles, âges et classes de décalages :

| (K) | intervalle de \(\Pr(N_h>0)\), sans balise | borne Paley–Zygmund minimale | maximum de \(\mathbb E[N_h^2]/(\mathbb E[N_h]+\mathbb E[N_h]^2)\) |
|---:|---:|---:|---:|
| 1 | 0,224–0,492 | 0,217 | 1,442 |
| 2 | 0,438–0,765 | 0,395 | 1,254 |
| 4 | 0,693–0,965 | 0,580 | 1,140 |
| 8 | 0,896–1,000 | 0,718 | 1,143 |

Avec la balise, les intervalles de probabilité de détection deviennent
respectivement 0,242–0,536, 0,463–0,815, 0,716–0,982 et 0,910–1,000.
Le cas le plus défavorable sans balise à (K=8) est observé pour
((c,m,d\text{ petit})=(2,81,\text{petit})), avec une probabilité de détection
de 0,896.

Ces observations soutiennent, sur le domaine fini testé, la conjecture

\[
\mathbb E[N_h^2]
\le C\left(\mathbb E[N_h]+\mathbb E[N_h]^2\right)
\]

avec une constante uniforme. **Je ne peux pas confirmer cette inégalité
asymptotiquement : le maximum numérique 1,442 n'est pas une preuve.** Les
échantillons de phases issus d'une même photographie sont en outre dépendants;
ils ne doivent pas être interprétés comme autant de réalisations indépendantes.

### 21.3 Ce que Paley–Zygmund donne réellement

L'inégalité de Paley–Zygmund appliquée à la variable non négative (N_h) donne

\[
\Pr(N_h>0)\ge
\frac{\mathbb E[N_h]^2}{\mathbb E[N_h^2]}.
\]

Si la borne de second moment précédente est démontrée et si
(\mathbb E[N_h]\asymp K), elle fournit une probabilité de détection strictement
positive dans une fenêtre de longueur (K\sqrt T). Elle ne permet toutefois
pas, à elle seule, d'itérer cette probabilité sur des fenêtres successives :
les événements de vide peuvent être corrélés.

La proposition antérieure doit donc être corrigée. Pour conclure

\[
\Pr\{\rho>K_q\sqrt T\}\le1-q,
\]

il faut encore l'un des ingrédients suivants :

1. une borne directe de probabilité de vide pour
   (M\triangle(M-d));
2. une propriété de mélange ou une domination conditionnelle permettant
   d'itérer les blocs;
3. un calcul exact des fonctions de corrélation ou d'un déterminant/Pfaffien
   contrôlant la différence symétrique.

Les systèmes unidimensionnels coalescents et annihilants possèdent une structure
pfaffienne dans certains cadres exactement résolus; voir R. Tribe et
O. Zaboronski, *Pfaffian formulae for one dimensional coalescing and
annihilating systems*, [Electronic Journal of Probability 16 (2011),
DOI et texte](https://doi.org/10.1214/EJP.v16-901). Cette littérature justifie
l'exploration de la troisième voie, mais **je ne peux pas confirmer que ses
formules impliquent directement la borne requise pour
(M\triangle(M-d)) sur notre anneau fini**.

### 21.4 Verdict actualisé

- La conjecture de second moment résiste aux petits décalages et aux tests sans
  balise.
- À \(K=8\), la détection empirique dépasse 0,9 dans toutes les strates avec
  balise; sans balise, une strate atteint seulement 0,896.
- Aucun contre-exemple numérique n'invalide l'échelle \(\sqrt T\).
- Le théorème \(\rho_q=O(\sqrt T)\) reste non démontré : le verrou est désormais
  la dépendance des événements de vide, ou un contrôle pfaffien équivalent.

## 22. Réduction exacte aux collisions de blocs

### 22.1 Identité combinatoire

La difficulté d'itérer des fenêtres peut être évitée lorsque le quantile porte,
comme dans notre définition, sur une phase (X) et un décalage non nul (d)
uniformes.

Pour une photographie cyclique fixée (O=(O_0,\ldots,O_{T-1})), notons

\[
B_x^{(\ell)}=(O_x,O_{x+1},\ldots,O_{x+\ell-1})
\]

le bloc cyclique de longueur \(\ell=h+1\), et

\[
n_w=\#\{x:B_x^{(\ell)}=w\},
\qquad p_w=n_w/T.
\]

L'absence de désaccord pendant \(\ell\) observations équivaut exactement à

\[
B_X^{(\ell)}=B_{X+d}^{(\ell)}.
\]

Le nombre de couples ordonnés de blocs égaux, diagonale comprise, vaut
\(\sum_w n_w^2\). En retirant les (T) couples diagonaux et en divisant par
\(T(T-1)\), on obtient l'identité exacte

\[
\boxed{
\Pr_{X,d\ne0}\{\rho(X,d)>h\}
=\frac{\sum_w n_w(n_w-1)}{T(T-1)}
=\frac{T\sum_w p_w^2-1}{T-1}.
}
\]

En définissant l'entropie de collision du bloc par

\[
H_2(B^{(\ell)})=-\log_2\sum_w p_w^2,
\]

cela devient

\[
\boxed{
\Pr\{\rho>h\}
=\frac{T,2^{-H_2(B^{(h+1)})}-1}{T-1}.
}
\]

Cette formule est démontrée par comptage fini; elle ne suppose ni indépendance,
ni mélange, ni limite thermodynamique. Elle est une application directe de
l'interprétation collisionnelle de l'entropie de Rényi d'ordre 2; voir
A. Rényi, *On Measures of Entropy and Information* (1961),
[texte original](https://projecteuclid.org/ebooks/berkeley-symposium-on-mathematical-statistics-and-probability/On-Measures-of-Entropy-and-Information/chapter/On-Measures-of-Entropy-and-Information/bsmsp/1200512181).

### 22.2 Nouvelle forme exacte du théorème recherché

Pour inclure l'aléa de la photographie (M), posons précisément

\[
C_{T,\ell}^{\rm ann}
=\mathbb E_M\!\left[\sum_w p_{w,M}^2\right],
\qquad
H_{2,T}^{\rm ann}(\ell)=-\log_2 C_{T,\ell}^{\rm ann}.
\]

La moyenne de l'identité précédente donne alors

\[
\Pr_{M,X,d\ne0}\{\rho>h\}
=\frac{T\,2^{-H_{2,T}^{\rm ann}(h+1)}-1}{T-1}.
\]

Pour démontrer \(\rho_q=O(\sqrt T)\), il suffit donc d'établir que, pour tout
(q<1), il existe (K_q<\infty) tel que

\[
\limsup_{T\to\infty}
2^{-H_{2,T}^{\rm ann}(\lfloor K_q\sqrt T\rfloor)}
\le1-q.
\]

Une propriété plus forte et naturelle serait l'existence d'une fonction
\(g(K)\to\infty\) telle que, uniformément pour les grandes tailles,

\[
H_{2,T}^{\rm ann}(\lfloor K\sqrt T\rfloor)\ge g(K).
\]

Ainsi, le verrou n'est plus une indépendance hypothétique entre fenêtres : il
est exactement une minoration de l'entropie de collision des blocs à l'échelle
du coarsening.

### 22.3 Calcul exhaustif des collisions spatiales

Le programme `block_collision_attack.py` reprend les 144 paramètres-réalisations
de la campagne précédente et compte tous les (T) blocs cycliques. Il en déduit
exactement les (T(T-1)) comparaisons phase–décalage; aucun décalage n'est
échantillonné. Les blocs sont encodés par des entiers de précision arbitraire de
façon injective, et non par un hachage probabiliste.

| (K) | détection moyenne globale sans balise | intervalle selon \((c,m)\), sans balise | intervalle selon \((c,m)\), avec balise |
|---:|---:|---:|---:|
| 0,5 | 0,251 | 0,222–0,277 | 0,232–0,309 |
| 1 | 0,452 | 0,407–0,490 | 0,422–0,536 |
| 2 | 0,715 | 0,661–0,756 | 0,676–0,804 |
| 4 | 0,918 | 0,884–0,941 | 0,894–0,967 |
| 8 | 0,989 | 0,979–0,995 | 0,984–0,998 |
| 12 | 0,998 | 0,995–1,000 | 0,997–1,000 |

L'entropie de collision *annealed* mesurée sans balise varie, selon (c,m),
de 0,754–0,970 bit à (K=1), 3,103–4,070 bits à (K=4), et
5,583–7,588 bits à (K=8). Cette croissance est compatible avec une fonction
\(g(K)\) croissante, approximativement linéaire sur la fenêtre testée.
**Je ne peux pas confirmer une loi linéaire asymptotique à partir de six valeurs
de (K) et quatre tailles.**

### 22.4 Limites et statut

Les probabilités du tableau sont moyennées sur la loi des photographies. Elles
établissent des quantiles *annealed*, pas une garantie uniforme pour chaque
réalisation. À titre de contre-test, certaines réalisations individuelles ont
une détection sensiblement plus faible : le minimum sans balise observé vaut
0,871 à (K=8), puis 0,970 à (K=12).

La balise améliore les petites tailles parce que les blocs qui la rencontrent
sont plus faciles à distinguer. Comme une fenêtre de longueur (O(\sqrt T))
rencontre un site fixé avec probabilité (O(T^{-1/2})), cet avantage ne doit pas
être utilisé comme preuve de la limite asymptotique.

Le bilan est désormais :

- identité entre queue de résolution et collision de blocs : **démontrée**;
- calcul de toutes les phases et de tous les décalages pour le domaine testé :
  **exact conditionnellement aux photographies simulées**;
- croissance de l'entropie de bloc à l'échelle \(\sqrt T\) : **fortement
  soutenue numériquement**;
- borne uniforme (H_2\ge g(K)\to\infty) : **ouverte**;
- théorème complet \(\rho_q=\Theta(\sqrt T)\) : **toujours non démontré**, mais
  réduit à une seule proposition entropique explicite.

## 23. Transfert exact vers la marche biaisée

### 23.1 Définition avec bruit commun

Deux phases candidates (x) et (x+d) doivent être comparées sous la même
suite d'actions de l'observateur. On introduit donc des incréments communs

\[
Z_k\in\{-1,+1\},
\qquad
\Pr(Z_k=+1)=p,
\qquad
\Pr(Z_k=-1)=q=1-p,
\]

et

\[
S_0=0,
\qquad
S_n=\sum_{k=1}^n Z_k.
\]

Les observations comparées au temps (k) sont

\[
O_{x+S_k}
\quad\text{et}\quad
O_{x+d+S_k}.
\]

Ce couplage par bruit commun est essentiel : il représente le même protocole
d'exploration appliqué aux deux hypothèses de phase. Avec deux marches
indépendantes, le théorème ci-dessous ne s'applique pas.

### 23.2 Identité trajectorielle

Posons

\[
m_n=\min_{0\le k\le n}S_k,
\qquad
M_n=\max_{0\le k\le n}S_k,
\qquad
R_n=M_n-m_n.
\]

Une marche à pas voisins visite nécessairement chaque entier entre son minimum
et son maximum. Son ensemble de sites visités jusqu'au temps (n) est donc
exactement

\[
\{m_n,m_n+1,\ldots,M_n\}.
\]

Si

\[
\tau(x,d)=\inf\{k\ge0:O_{x+S_k}\ne O_{x+d+S_k}\},
\]

alors

\[
\tau(x,d)>n
\quad\Longleftrightarrow\quad
(O_{x+m_n},\ldots,O_{x+M_n})
=(O_{x+d+m_n},\ldots,O_{x+d+M_n}).
\]

Conditionnellement à la trajectoire, il s'agit donc exactement d'une collision
de blocs de longueur (R_n+1). Tant que (R_n<T), l'identité de la section 22
donne

\[
\boxed{
\Pr_{M,x,d\ne0}\{\tau>n\mid(S_k)_{k\le n}\}
=\frac{T,2^{-H_{2,T}^{\rm ann}(R_n+1)}-1}{T-1}.
}
\]

Il ne s'agit plus d'une analogie entre distance et durée : c'est une égalité
finie, trajectoire par trajectoire, après moyenne sur la photographie et les
phases.

### 23.3 Théorème de transfert d'échelle

Supposons (p>q>0) fixé et posons

\[
v=p-q=2p-1>0.
\]

La loi des grands nombres et les inégalités de concentration pour les sommes de
variables bornées impliquent

\[
\frac{R_n}{n}\longrightarrow v
\quad\text{en probabilité, et même presque sûrement}.
\]

En effet, (S_n/n\to v), le maximum avance à la même vitesse (v), tandis que
le minimum passé est sous-linéaire. Pour les bornes quantitatives, on peut
utiliser W. Hoeffding, *Probability Inequalities for Sums of Bounded Random
Variables*, JASA 58 (1963), 13–30,
[DOI](https://doi.org/10.1080/01621459.1963.10500830).

Comme la probabilité de collision de blocs est décroissante avec leur longueur,
pour tout \(\varepsilon\in(0,v)\), l'identité précédente peut être encadrée par
les collisions aux longueurs

\[
(v-\varepsilon)n
\quad\text{et}\quad
(v+\varepsilon)n,
\]

à une erreur (o(1)) près. Par conséquent, sous les bornes de quantile spatiales
non dégénérées utilisées dans notre définition,

\[
\boxed{
\rho_q^{\rm sp}(T)=\Theta(\sqrt T)
\quad\Longrightarrow\quad
\tau_q^{(p,q)}(T)=\Theta(\sqrt T),
\qquad p>q.
}
\]

Les constantes temporelles sont renormalisées au premier ordre par (1/v) :

\[
\tau_q^{(p,q)}\simeq\frac{\rho_q^{\rm sp}}{p-q}.
\]

Cette dernière équivalence avec constante précise requiert une convergence de
la loi spatiale de résolution; le résultat en \(\Theta\) ne requiert que des
encadrements de quantiles stables.

### 23.4 Contre-exemple sans dérive

Lorsque (p=q=1/2), l'étendue d'une marche symétrique après (n) pas est de
l'ordre de \(\sqrt n\), et non de (n). Explorer une distance spatiale
\(\Theta(\sqrt T)\) demande alors un temps

\[
\sqrt n\asymp\sqrt T
\quad\Longrightarrow\quad
n\asymp T.
\]

Une formule explicite pour la distribution de l'étendue de la marche simple
symétrique est donnée par B. A. Moser, *The Range of a Simple Random Walk on
\(\mathbb Z\): An Elementary Combinatorial Approach*, Electronic Journal of
Combinatorics 21(4), 2014,
[DOI et article](https://doi.org/10.37236/4106).

Ainsi la marche non biaisée ne préserve pas le Régime B temporel : elle le
transforme en une résolution linéaire. Cela montre que le biais n'était pas un
ornement thermodynamique; il est aussi nécessaire pour convertir une distance
\(\sqrt T\) en une durée \(\sqrt T\).

### 23.5 Vérification numérique adversariale

Le programme `biased_walk_transfer.py` teste six tailles, six photographies par
taille et 128 couples phase–décalage par photographie, avec la balise incluse.
Les exposants de régression en (T) sont :

| (p) | dérive (v=2p-1) | exposant de \(\tau_{50}\) | exposant de \(\tau_{90}\) |
|---:|---:|---:|---:|
| 0,50 | 0 | 1,101 | 0,988 |
| 0,55 | 0,10 | 0,695 | 0,522 |
| 0,65 | 0,30 | 0,576 | 0,527 |
| 0,75 | 0,50 | 0,568 | 0,531 |
| 0,90 | 0,80 | 0,544 | 0,535 |

Pour les trois biais les plus nets, les exposants sont proches de (1/2). Le
biais faible (p=0,55) présente une correction de taille plus forte pour la
médiane, tandis que son quantile 90 % reste proche de (1/2). Après
renormalisation par la dérive, les grandes tailles donnent typiquement

\[
v\tau_{50}/\sqrt T\approx0,9\text{--}1,2,
\qquad
v\tau_{90}/\sqrt T\approx3,0\text{--}3,9.
\]

Pour (p=1/2), les exposants sont proches de 1. Quelques trajectoires sont
censurées à (20T); elles représentent moins de 10 % de chaque strate et ne
font pas franchir ce seuil au quantile 90 %, mais elles interdisent une lecture
fine de la queue extrême.

### 23.6 Statut corrigé

- identité entre résolution temporelle et collision d'un bloc de longueur
  aléatoire : **démontrée sous bruit commun**;
- transfert \(\Theta(\sqrt T)\) spatial vers temporel pour dérive fixe non
  nulle : **démontré conditionnellement aux bornes spatiales**;
- changement vers l'échelle (T) sans dérive : **prédit théoriquement et
  reproduit numériquement**;
- production entropique
  \(\sigma=(p-q)\log(p/q)\) : **compatible avec le même observateur**;
- seul verrou asymptotique principal restant : **la minoration uniforme de
  l'entropie de collision spatiale à l'échelle \(\sqrt T\)**.

## 24. Réduction du verrou spatial à l'anti-concentration

### 24.1 Une statistique plus simple que le bloc complet

Pour une photographie (M), une origine (x) et une longueur
\(\ell=\lfloor K\sqrt T\rfloor+1\), notons

\[
N_{M,K}(x)=|M\cap\{x,x+1,\ldots,x+\ell-1\}|
\]

le nombre de parois dans le bloc. Si deux blocs binaires sont égaux, leurs
nombres de parois sont nécessairement égaux. En écrivant

\[
p_{M,K}(r)=\frac1T\#\{x:N_{M,K}(x)=r\},
\]

on obtient, réalisation par réalisation,

\[
\boxed{
C_{\rm bloc}(M,K)
\le C_{\rm compte}(M,K)
=\sum_r p_{M,K}(r)^2
\le\max_r p_{M,K}(r).
}
\]

Après moyenne sur (M), une condition suffisante pour fermer le théorème est
donc

\[
\boxed{
\sup_{T\ge T_0(K)}
\mathbb E_M\!\left[\max_r p_{M,K}(r)\right]
\le a(K),
\qquad a(K)\longrightarrow0.
}
\]

Cette propriété d'anti-concentration locale implique immédiatement

\[
C_{T,K\sqrt T}^{\rm ann}\longrightarrow0
\quad(K\to\infty),
\]

puis \(H_{2,T}^{\rm ann}\to\infty\), \(\rho_q^{\rm sp}=O(\sqrt T)\) et, par la
section 23, \(\tau_q^{(p,q)}=O(\sqrt T)\) pour toute dérive fixe non nulle.

### 24.2 Correction : la variance ne suffit pas

Une croissance

\[
\operatorname{Var}N_{M,K}=\Theta(K)
\]

n'est pas suffisante à elle seule. Une distribution peut conserver un atome de
masse fixe et placer une petite masse très loin, produisant ainsi une variance
divergente sans anti-concentration. Il faut donc soit :

1. un théorème central **local** pour le nombre de parois;
2. une borne directe sur son plus grand atome;
3. une fonction génératrice pfaffienne donnant cette borne.

Un simple théorème central en distribution ne ferme pas cette étape.

### 24.3 Littérature applicable et limite de l'application

Sous la loi d'entrée maximale, les systèmes browniens annihilants et
coalescents unidimensionnels sont des processus pfaffiens; voir R. Tribe,
S. K. Yip et O. Zaboronski, *One dimensional annihilating and coalescing
particle systems as extended Pfaffian point processes*, Electronic
Communications in Probability 17 (2012),
[DOI et texte](https://doi.org/10.1214/ECP.v17-2133).

Un théorème central récent pour une classe générale de processus pfaffiens a été
proposé par K. Wang et M. Xu, *Gaussian limit for Pfaffian point processes*,
[arXiv:2504.14487](https://arxiv.org/abs/2504.14487). Il s'agit d'un préprint et
d'un résultat central global, non automatiquement d'un théorème central local.

Le théorème central local de P. J. Forrester et J. L. Lebowitz concerne les
processus **déterminantaux** et certaines extensions spécifiques, pas tous les
processus pfaffiens : *Local Central Limit Theorem for Determinantal Point
Processes*, [arXiv:1311.7126](https://arxiv.org/abs/1311.7126).

**Je ne peux pas confirmer qu'un théorème publié couvre directement notre
anti-concentration quenched sur anneau fini.** La voie pfaffienne reste
plausible, mais les hypothèses et le passage réseau discret–limite brownienne
doivent encore être établis.

### 24.4 Test exact de la statistique de compte

Le programme `count_entropy_attack.py` utilise (m=45,63,81), huit
photographies par taille et compte toutes les fenêtres cycliques. Les moyennes
sur les trois tailles sont :

| (K) | moyenne du compte | variance spatiale | collision des comptes | plus grand atome moyen | collision du bloc complet |
|---:|---:|---:|---:|---:|---:|
| 1 | 0,308 | 0,239 | 0,582 | 0,706 | 0,503 |
| 2 | 0,611 | 0,426 | 0,433 | 0,514 | 0,242 |
| 4 | 1,218 | 0,783 | 0,326 | 0,431 | 0,0593 |
| 8 | 2,430 | 1,422 | 0,257 | 0,357 | 0,0043 |
| 12 | 3,643 | 1,913 | 0,235 | 0,337 | 0,0005 |
| 16 | 4,855 | 2,267 | 0,217 | 0,304 | 0,0003 |

Pour (K\le12), la moyenne du compte croît numériquement comme (K^{0,99}).
Selon la taille, la variance croît comme (K^{0,80}) à (K^{0,93}), et la
collision des comptes décroît comme (K^{-0,33}) à (K^{-0,43}). Ces exposants
sont compatibles avec une convergence lente vers le scénario local-gaussien
\(K^{-1/2}\), mais ils ne l'établissent pas.

Les valeurs (K\ge16) commencent à subir des effets d'anneau, particulièrement
pour (m=45), car la fenêtre n'est plus petite devant la circonférence. Elles
ne doivent pas être utilisées pour extrapoler un exposant asymptotique.

La collision du bloc complet décroît beaucoup plus vite que la borne par le
compte. Cela confirme que le nombre de parois est une statistique volontairement
grossière : sa faiblesse facilite une preuve éventuelle, mais elle perd une
grande partie de l'information positionnelle.

### 24.5 Statut

- réduction de la collision complète à l'anti-concentration du compte :
  **démontrée**;
- décroissance du plus grand atome et de la collision du compte : **observée
  exactement sur les photographies simulées**;
- loi locale gaussienne ou borne uniforme \(a(K)\to0\) : **ouverte**;
- variance seule comme preuve : **réfutée logiquement**;
- verrou final : **établir l'anti-concentration quenched du nombre de parois
  dans une fenêtre (K\sqrt T)**.

## 25. Audit de la fonction génératrice du nombre de parois

### 25.1 Question testée et ordre des limites

Pour éviter de confondre limite thermodynamique et grandes fenêtres, le test
respecte la structure pertinente : d'abord augmenter

\[
T=m^2\quad\text{à }K\text{ fixé},
\]

puis seulement étudier la dépendance en (K). Les tailles utilisées sont
(m=81,123,171), avec respectivement 8, 5 et 3 photographies, et
(K=1,2,4,8,12,16). Toutes les origines cycliques sont comptées exactement.

Deux polynômes doivent être distingués :

\[
G_{M,K}(z)=\sum_r p_{M,K}(r)z^r
\]

pour une photographie donnée (polynôme **quenched**), et

\[
G^{\rm ann}_{T,K}(z)=\mathbb E_M G_{M,K}(z)
\]

pour la loi moyennée. Notre borne cible contient
\(\mathbb E_M[\max_r p_{M,K}(r)]\). Une belle propriété du seul polynôme
moyenné ne suffirait donc pas sans un argument supplémentaire.

### 25.2 Contre-exemple exact à la voie des racines réelles

Une photographie simulée avec (m=81), (T=6561), (K=2), graine
18630002676 et longueur de fenêtre 163 donne les fréquences exactes

\[
(n_0,n_1,n_2)=(4024,2140,397).
\]

Le facteur constant (1/T) ne changeant pas les zéros, le polynôme à tester est

\[
P(z)=4024+2140z+397z^2.
\]

Son discriminant, calculé en arithmétique entière, vaut

\[
\boxed{2140^2-4\times397\times4024=-1\,810\,512<0.}
\]

Il possède donc deux racines non réelles. Ce résultat est une **certification
exacte du polynôme fini obtenu**, et non une décision fondée sur les erreurs
d'un solveur numérique. Il réfute l'assertion selon laquelle tous les
polynômes empiriques quenched de notre modèle auraient des zéros réels
négatifs.

Ce contre-exemple ne prouve pas qu'une fonction génératrice pfaffienne dans
une limite annealed ne pourrait jamais avoir une autre structure. Il détruit
plus précisément le raccourci qui aurait déduit notre anti-concentration
quenched d'une factorisation exacte, photographie par photographie, en somme
de variables de Bernoulli indépendantes. Pour les processus déterminantaux,
ce type d'indépendance du nombre de points est un phénomène spécial; voir
Hough, Krishnapur, Peres et Virág, *Determinantal Processes and Independence*,
[arXiv:math/0503110](https://arxiv.org/abs/math/0503110). On ne peut pas le
transférer sans preuve à notre loi pfaffienne annihilante.

### 25.3 Résultat numérique global

En regroupant les 16 photographies de chaque (K), on obtient :

| (K) | fraction quenched à racines toutes réelles | fraction log-concave | plus grand atome moyen | variance moyenne |
|---:|---:|---:|---:|---:|
| 1 | 0,938 | 1,000 | 0,733 | 0,220 |
| 2 | 0,562 | 0,875 | 0,536 | 0,386 |
| 4 | 0,250 | 0,938 | 0,450 | 0,681 |
| 8 | 0,062 | 0,500 | 0,338 | 1,274 |
| 12 | 0,000 | 0,312 | 0,300 | 1,914 |
| 16 | 0,000 | 0,062 | 0,283 | 2,555 |

Les polynômes annealed empiriques ne réparent pas le problème : ils ont des
racines complexes pour 12 des 18 couples ((m,K)) testés. La log-concavité
annealed tient pour 14 de ces 18 couples, mais échoue aux plus grandes fenêtres
pour chacune des trois tailles. Surtout, même lorsqu'elle tient numériquement,
elle n'est ici ni démontrée uniformément ni suffisante, telle quelle, pour
l'ordre de limites requis.

Les racines de degré supérieur sont un **diagnostic numérique** sensible aux
coefficients; seules les conclusions appuyées par le discriminant entier
ci-dessus sont qualifiées de preuve exacte. La décroissance du plus grand atome
et la croissance de la variance restent visibles et compatibles avec une loi
locale gaussienne, mais ne la prouvent pas.

### 25.4 Conséquence pour la construction du temps

La construction temporelle n'est pas réfutée. Les identités de collision et
le transfert par marche biaisée restent exacts. Ce qui est réfuté est une
méthode de fermeture particulièrement courte :

\[
\text{« zéros réels négatifs »}
\Rightarrow\text{Poisson-binomial}
\Rightarrow\text{anti-concentration}.
\]

La voie rationnelle restante est maintenant plus étroite : établir une borne
locale directement, soit par un théorème central local adapté au processus
pfaffien annihilant, soit par une estimation de mélange/cumulants suffisamment
uniforme pour contrôler
\(\mathbb E_M[\max_r p_{M,K}(r)]\). **Je ne peux pas confirmer à ce stade
qu'un théorème publié fournisse directement cette borne quenched sur anneau
fini.**

### 25.5 Statut après ce test

- contre-exemple quenched à la propriété « toutes les racines sont réelles
  négatives » : **démontré exactement pour un polynôme fini**;
- généralité d'une factorisation Poisson-binomial quenched : **réfutée**;
- anti-concentration observée quand (K) croît : **renforcée numériquement**;
- anti-concentration asymptotique uniforme : **toujours ouverte**;
- prochaine attaque justifiée : **mélange/cumulants puis théorème central
  local**, et non recherche de racines réelles.

## 26. Attaque par mélange, cumulants et obstruction de réseau

### 26.1 Protocole

Le programme `mixing_cumulant_attack.py` reprend les tailles
(m=81,123,171), avec 8, 5 et 3 photographies indépendantes. Il énumère toutes
les origines cycliques et mesure :

1. la corrélation entre les nombres de parois de deux blocs de longueur (m),
   séparés de (j) blocs;
2. les quatre premiers cumulants du nombre de parois dans une fenêtre
   (Km+1);
3. le plus grand atome, le biais de parité
   \(|\mathbb E[(-1)^{N_K}]|\), et le maximum de la fonction caractéristique
   sur (\theta\in[\pi/4,\pi]).

Les moyennes spatiales sont exactes **conditionnellement à chaque photographie
simulée**. Leur extrapolation en (T) ou (K) demeure une inférence numérique.

### 26.2 Corrélations entre blocs macroscopiques

La corrélation moyenne entre deux blocs adjacents de taille (\sqrt T=m) vaut :

| (m) | corrélation au décalage 1 | décalage 2 | décalage 3 |
|---:|---:|---:|---:|
| 81 | -0,154 | -0,031 | -0,002 |
| 123 | -0,151 | -0,010 | 0,008 |
| 171 | -0,127 | -0,030 | 0,061 |

L'anticorrélation du voisin immédiat est cohérente avec l'exclusion créée par
l'annihilation : une concentration locale de parois rend moins probable une
seconde concentration juste à côté. Au-delà de deux ou trois blocs, la
corrélation moyenne est généralement proche de zéro, mais elle n'est ni
monotone ni uniformément petite réalisation par réalisation. Par exemple, les
extrêmes observés restent parfois de l'ordre de (0,1).

Cela constitue un **indice de mélange à portée courte**, pas une preuve d'une
inégalité de mélange (\alpha(j)\le Ce^{-cj}) ni même d'une borne sommable
uniforme. Une covariance faible ne contrôle pas à elle seule tous les
événements nécessaires à un coefficient de mélange fort.

### 26.3 Cumulants et anti-concentration

Sur (K\le16), les régressions logarithmiques donnent :

| (m) | exposant de (\kappa_2) | exposant du plus grand atome |
|---:|---:|---:|
| 81 | 0,745 | -0,274 |
| 123 | 0,904 | -0,363 |
| 171 | 0,808 | -0,325 |

La variance augmente donc nettement et son exposant se rapproche parfois de la
croissance linéaire (\kappa_2\asymp K) attendue. Le plus grand atome diminue,
mais plus lentement que la cible gaussienne (K^{-1/2}) sur ces tailles.

L'asymétrie standardisée diminue globalement avec (K) et devient petite aux
grandes fenêtres. En revanche, l'excès de kurtosis ne converge pas proprement
vers zéro : il fluctue et devient souvent négatif aux grandes valeurs de (K).
Ce comportement peut provenir des contraintes de l'anneau et du chevauchement
des fenêtres, mais **je ne peux pas confirmer cette explication à partir de ces
seules données**. Il interdit de déclarer une convergence gaussienne uniforme.

### 26.4 Test spectral de l'arithmétique entière

Un théorème central local demande davantage que des cumulants normalisés : la
fonction caractéristique doit aussi être contrôlée loin de zéro. Le biais de
parité moyen tombe, selon les tailles, d'environ (0,43--0,49) à (K=1) vers
(0,08--0,13) à (K=16). Il n'apparaît donc pas de conservation stricte de la
parité du nombre de parois dans une fenêtre.

Sur l'arc fixe (\theta\in[\pi/4,\pi]), le maximum moyen de
\(|\mathbb E e^{i\theta N_K}|\) décroît :

| (m) | (K=1) | (K=8) | (K=16) |
|---:|---:|---:|---:|
| 81 | 0,931 | 0,696 | 0,591 |
| 123 | 0,935 | 0,670 | 0,413 |
| 171 | 0,933 | 0,665 | 0,518 |

Cette décroissance est nécessaire et favorable, mais reste lente. Le calcul ne
démontre pas que ce supremum tend vers zéro dans le double ordre de limites
requis. Il ne ferme donc pas encore la condition spectrale d'un théorème
central local.

### 26.5 Ce que l'attaque établit réellement

- dépendance négative entre blocs voisins : **observée robustement**;
- corrélations moyennes faibles après quelques blocs : **observées**, mais sans
  enveloppe uniforme démontrée;
- variance croissante et atome maximal décroissant : **confirmés sur une plage
  plus large de (K)**;
- obstruction stricte de parité : **non observée**, mais absence asymptotique
  non démontrée;
- cumulants normalisés gaussiens et contrôle spectral uniforme : **non
  établis**;
- théorème central local quenched : **toujours ouvert**.

La prochaine étape ne doit donc pas être une régression supplémentaire. Il faut
exploiter le noyau pfaffien connu du processus annihilant pour calculer ou
borner analytiquement les corrélations tronquées intégrées. La cible est de
montrer, dans la limite brownienne puis avec contrôle de l'approximation de
l'anneau discret,

\[
\kappa_2(N_K)\asymp K,
\qquad
|\kappa_j(N_K)|\le C_jK,
\]

et une décroissance uniforme de la fonction caractéristique loin de zéro.
Sans ce dernier contrôle, les cumulants peuvent soutenir un théorème central
ordinaire mais pas la borne locale nécessaire à notre construction du temps.

## 27. Calcul pfaffien exact de la variance dans la limite brownienne

### 27.1 Noyau utilisé

Pour les mouvements browniens annihilants issus de la loi d'entrée maximale,
la littérature donne un processus ponctuel pfaffien; voir Tribe, Yip et
Zaboronski, *One dimensional annihilating and coalescing particle systems as
extended Pfaffian point processes*,
[ECP 17 (2012)](https://doi.org/10.1214/ECP.v17-2133).

Dans la convention où un mouvement brownien a variance (2Dt), posons pour
(s>0)

\[
F(s)=\operatorname{erfc}\!\left(\frac{s}{\sqrt{8Dt}}\right),
\qquad
g(s)=-F'(s)=\frac{e^{-s^2/(8Dt)}}{\sqrt{2\pi Dt}}.
\]

Pour l'annihilation pure, le facteur pfaffien est (a=1/2). Le noyau à deux
points conduit à

\[
\rho=a g(0)=\frac1{\sqrt{8\pi Dt}}
\]

et à la covariance tronquée

\[
\boxed{
c(s)=\rho_2(0,s)-\rho^2
=a^2\left[
\frac{s}{4Dt}F(s)g(s)-g(s)^2
\right].
}
\]

Cette formule est obtenue en développant le pfaffien (4\times4). Elle est
négative à courte distance, conformément à l'anticorrélation observée dans les
simulations.

### 27.2 Intégration exacte

Pour le nombre (N_L) de particules dans un intervalle de longueur (L),

\[
\operatorname{Var}N_L
=\rho L+2\int_0^L(L-s)c(s)\,ds.
\]

Les deux intégrales nécessaires sont

\[
\int_0^\infty g(s)^2ds=\frac1{2\sqrt{\pi Dt}},
\]

et, après le changement de variable
\(u=s/\sqrt{8Dt}\),

\[
\int_0^\infty\frac{s}{4Dt}F(s)g(s)ds
=\frac{\sqrt2-1}{2\sqrt{\pi Dt}}.
\]

La covariance est intégrable. Par conséquent,

\[
\boxed{
\operatorname{Var}N_L
\sim
\frac{\sqrt2-1}{2\sqrt{\pi Dt}}L
\qquad(L\to\infty).
}
\]

Comme

\[
\mathbb EN_L\sim\frac{L}{\sqrt{8\pi Dt}},
\]

le facteur de Fano asymptotique est exactement

\[
\boxed{
\frac{\operatorname{Var}N_L}{\mathbb EN_L}
\longrightarrow2-\sqrt2\simeq0,585786.
}
\]

Le caractère sous-poissonien est donc une conséquence analytique de
l'annihilation, et non un artefact numérique.

### 27.3 Constantes correspondant au simulateur

Dans `coarsening_time_model.py`, chaque paroi saute au taux total 1 et chaque
saut vaut (\pm1). Sa variance par unité de temps vaut donc 1, ce qui correspond
à (D=1/2). Avec (t=T) et (L=K\sqrt T), la limite brownienne prédit

\[
\boxed{
\mathbb EN_K\sim\frac{K}{\sqrt{4\pi}}
=0,28209479K,
}
\]

et

\[
\boxed{
\operatorname{Var}N_K\sim
\frac{2-\sqrt2}{\sqrt{4\pi}}K
=0,16524730K.
}
\]

Le programme `pfaffian_variance_audit.py` recalcule ces constantes et les
compare aux simulations. Pour (m=123), la variance **annealed** par unité de
(K) vaut respectivement 0,1713, 0,1743 et 0,1780 pour (K=8,12,16), contre
0,16525 prédit. Pour (m=171,K=8), elle vaut 0,16265. Les écarts sont donc de
l'ordre de quelques pourcents dans ces strates, mais augmentent lorsque la
fenêtre devient une fraction importante de l'anneau ou lorsque le nombre de
répétitions est trop faible.

### 27.4 Correction quenched–annealed

Le calcul pfaffien porte sur la variance annealed. Notre variance spatiale à
photographie fixée est différente. La relation exacte est

\[
\boxed{
\operatorname{Var}_{M,x}N
=\mathbb E_M[\operatorname{Var}_x(N\mid M)]
+\operatorname{Var}_M(\mathbb E_x[N\mid M]).
}
\]

Le second terme contient les fluctuations du nombre total de parois entre
photographies. Confondre la variance quenched moyenne avec la variance
pfaffienne annealed aurait été incorrect. Le fichier de comparaison utilise
désormais la formule de variance totale.

Avec seulement trois photographies pour (m=171), les trois réalisations ont
fortuitement le même nombre total de parois; le terme inter-photographies y est
donc nul dans l'échantillon. Cela ne prouve évidemment pas qu'il est nul dans
la loi réelle.

### 27.5 Portée exacte du résultat

- densité brownienne et covariance à deux points : **issues du noyau pfaffien
  publié**;
- intégration et coefficient (2-\sqrt2) : **dérivés exactement**;
- croissance linéaire de la variance annealed dans la limite brownienne :
  **démontrée à partir de ce noyau**;
- accord des constantes avec le modèle discret : **observé sur certaines
  strates**, avec effets finis clairement visibles;
- convergence rigoureuse de l'anneau discret vers ce résultat, uniformément en
  (K) : **non démontrée ici**;
- passage de la loi annealed à
  \(\mathbb E_M[\max_r p_{M,K}(r)]\) : **non démontré**;
- anti-concentration locale (O(K^{-1/2})) : **toujours ouverte**.

Ce calcul ferme donc exactement la partie « variance linéaire » du programme
continuum. Il ne ferme pas le théorème temporel, puisque la variance seule ne
contrôle pas le plus grand atome. Le verrou restant est désormais plus précis :
obtenir un théorème central **local** pour le compte pfaffien, puis justifier le
passage ergodique et uniforme de cette loi annealed à la statistique spatiale
quenched de l'anneau discret.