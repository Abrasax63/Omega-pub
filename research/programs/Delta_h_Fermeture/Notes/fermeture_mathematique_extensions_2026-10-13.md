# Fermeture mathématique : parité, coordonnées et espaces lacunaires

Date : 13 octobre 2026. Version 1.

## Conclusion et statut

Cette note étend le critère de fermeture des espaces e^{-g} P_N. Elle contient des preuves directes et des contrôles rationnels exécutés. Elle ne revendique aucune nouveauté bibliographique, aucune classification de tous les espaces de fonctions, ni résolution générale de Schrödinger.

Résultat principal : pour un même opérateur différentiel d'ordre deux dans une même coordonnée et une même jauge, deux espaces polynomiaux complets distincts peuvent être préservés sans préservation de toute la suite. Trois espaces P_N distincts, avec N>=2, imposent la préservation de tous les P_n. Cette assertion ne concerne pas trois espaces utilisant des jauges ou coordonnées différentes.

Le cas à coefficient principal constant traité précédemment conserve son résultat plus fort : deux secteurs distincts suffisent alors. Il n'est pas réfuté dans ses hypothèses ; son extension sans ces hypothèses est réfutée.

## 1. Critère général dans une représentation commune

Soit J un intervalle ouvert réel et

L = -P(z) d²/dz² + A(z) d/dz + B(z),

avec coefficients fonctions sur J. Posons P_N=span{1,z,...,z^N}, N>=2.

**Théorème T1.** L P_N est inclus dans P_N si et seulement si P,A,B sont des polynômes, de degrés au plus 4,3,2 respectivement, et leurs coefficients vérifient

A_3 = 2(N-1) P_4,

B_2 = -N(N-1) P_4,

B_1 = N(N-1) P_3 - N A_2.

Les coefficients non spécifiés sont libres. Un coefficient absent vaut zéro. Il n'est pas nécessaire que P soit positif pour ce théorème algébrique.

### Preuve de nécessité

L1=B appartient à P_N ; Lz=A+Bz appartient à P_N ; Lz²=-2P+2Az+Bz² appartient à P_N. Par ces trois identités, B,A,P sont polynomiaux, avec degrés au plus N,N+1,N+2.

Pour un décalage de degré s, le coefficient de z^{n+s} dans Lz^n est

C_s(n) = -n(n-1)P_{s+2} + n A_{s+1} + B_s.

Pour s>=3, les degrés n=N,N-1,N-2 doivent tous annuler ce coefficient, car n+s>N. Le polynôme C_s, de degré au plus deux en n, a trois racines distinctes ; il est donc nul. Ainsi P_{s+2}=A_{s+1}=B_s=0. On obtient les bornes 4,3,2.

Pour s=2, C_2 s'annule en N et N-1. Son coefficient quadratique est -P_4 ; donc C_2(n)=-P_4(n-N)(n-N+1). L'identification donne les deux premières égalités.

Pour s=1, seul n=N dépasse le degré maximal. C_1(N)=0 donne la troisième égalité.

### Preuve de suffisance

Les seuls décalages susceptibles de dépasser N sont s=1 et s=2. Les identités précédentes les annulent exactement pour tous les n concernés. Les décalages nuls ou négatifs restent dans P_N. La différentiation de polynômes ne crée pas de puissance négative : les facteurs n et n(n-1) annulent les cas n=0,1. Cela prouve la réciproque.

## 2. Deux secteurs contre trois

Tous les secteurs de cette section utilisent le même L, la même variable z et les mêmes coefficients.

**Théorème T2.** Pour N,M>=2, N!=M, L préserve P_N et P_M si et seulement si

deg P<=3, deg A<=2, B=B_0+B_1 z,

A_2=(N+M-1)P_3,

B_1=-NM P_3.

**Preuve.** Appliquer T1 aux deux indices donne A_3=2(N-1)P_4=2(M-1)P_4, donc P_4=A_3=B_2=0. Soustraire les deux expressions de B_1 donne A_2=(N+M-1)P_3, puis B_1=-NM P_3. La réciproque découle de T1.

**Théorème T3.** Si trois indices distincts N,M,K>=2 sont préservés, alors deg P<=2, deg A<=1, B est constant ; tous les P_n sont préservés.

**Preuve.** T2 pour les paires (N,M) et (N,K) impose (M-K)P_3=0. Donc P_3=A_2=B_1=0. Ces bornes de degré assurent directement L P_n inclus dans P_n pour chaque n>=0.

### Contre-exemple explicite à la généralisation du seuil deux

Pour N=2 et M=4, prendre

L = -z³ D_z² + 5z² D_z - 8z.

Alors

Lz^k = -(k-2)(k-4)z^{k+1}.

P_2 et P_4 sont préservés ; P_3 ne l'est pas, car Lz³=z⁴. Parmi les espaces P_J, les seuls indices fermés sont J=2 et J=4. C'est un contre-exemple algébrique exact, non une simulation.

## 3. Rapport aux changements de coordonnée de Schrödinger

Si H=-D_x²+V(x), si z(x) est une coordonnée locale avec z'!=0, et si psi=e^{-g(x)}p(z(x)), alors

e^g H[e^{-g}p(z)] = -P(z)p''(z)+A(z)p'(z)+B(z)p(z),

P(z(x))=(z')²,

A(z(x))=2g'z'-z'',

B(z(x))=V+g''-(g')².

Donc un changement de coordonnée transforme le coefficient principal constant en un P variable. La distinction entre les seuils deux et trois vient précisément de ce coefficient variable. Pour construire localement un opérateur de Schrödinger réel depuis L, exiger P>0 sur l'intervalle choisi, résoudre z'=+/-sqrt(P(z)), puis g'=(A+z'')/(2z') et V=B-g''+(g')². Cela ne prouve rien sur les domaines auto-adjoints ou la normalisabilité globale.

### Réalisation locale du contre-exemple par un potentiel connu

Pour les indices N,M, poser x>0, z=4/x² et s=N+M+1/2. Prendre

g=-s log x,

H=-D_x² + ((N-M)²-1/4)/x².

La transformation précédente donne exactement P=z³, A=(N+M-1)z², B=-NMz.

Les espaces x^s P_N(4/x²) et x^s P_M(4/x²) sont donc fermés localement. Vérification indépendante de la règle de chaîne : pour alpha=s-2k,

H x^alpha = [((N-M)²-1/4)-alpha(alpha-1)]x^{alpha-2}

= -4(k-N)(k-M)x^{alpha-2}.

Cela confirme le contre-exemple dans une forme de Schrödinger, sur x>0. Le potentiel inverse-carré n'est pas nouveau et ces espaces ne sont pas revendiqués comme secteurs physiques dans L²(0,infinity). La normalisabilité et le domaine ne sont pas établis ici.

## 4. Polynômes en x² et parité

Fixons sigma=0 ou 1 et g(x)=a x⁴/4+b x²/2, avec a,b réels. Posons

M_{N,sigma}=x^sigma e^{-g(x)} P_N(x²), N>=2.

**Théorème T4.** Cet espace est préservé par H=-D_x²+V exactement lorsque

V=a²x⁶+2abx⁴+[b²-a(4N+2sigma+3)]x²+E-(2sigma+1)b,

où E est constant.

**Preuve.** Sur x>0, remplacer g par g-sigma log x et z par x². Comme sigma(sigma-1)=0, le terme inverse-carré disparaît. Le transformé est

L=-4z D_z² + [4az²+4bz-2(2sigma+1)]D_z -4Na z+E.

T1 donne immédiatement la nécessité et la suffisance. Les fonctions et le potentiel sont réguliers à x=0 dans cette famille, et l'identité se prolonge à toute la droite.

Si l'on cherche au contraire g sans fixer sa forme, cette nécessité reste valable sous l'hypothèse que g est paire et régulière au voisinage de zéro : A est au plus quadratique en z ; la régularité fixe A(0)=-2(2sigma+1), et impose g'=ax³+bx. Sur un intervalle qui évite zéro, une jauge logarithmique supplémentaire est possible ; elle n'est pas classée par T4 sous sa forme régulière.

À a!=0, le même potentiel et la même jauge ne peuvent préserver simultanément deux de ces secteurs aux indices (N,sigma) différents : l'égalité des coefficients impose 4N+2sigma=4M+2rho, donc N=M et sigma=rho. Si a=0, on retrouve une suite complète pour les deux parités. La famille sextique est un cas de référence connu, pas une découverte revendiquée.

## 5. Degrés manquants : une obstruction et son contournement singulier

Posons S=span{1,x²,x³}. Pour L=-D_x²+A(x)D_x+B(x), avec A et B polynomiaux, S ne peut être invariant.

**Preuve.** L1=B impose B dans S. Dans Lx³=-6x+3x²A+x³B, le coefficient de x est donc -6 : les autres termes ont degré au moins deux. Or x n'appartient pas à S. Contradiction.

Cette obstruction dépend de la polynomialité des coefficients. Sur x>0,

L=-D_x²+(2/x)D_x

préserve S : L1=0, Lx²=2, Lx³=0. Avec g=log x et V=2/x², ce L est le conjugué de H=-D_x²+2/x². Le secteur correspondant est span{x^{-1},x,x²}. La singularité de la jauge contourne l'obstruction ; aucun statut physique global n'est attribué à ce secteur.

La classification de tous les espaces lacunaires ne découle pas de cet exemple. Les espaces monomiaux ont déjà fait l'objet de classifications dans la littérature.

## 6. Contrôles exacts exécutés

Un programme utilisant uniquement fractions.Fraction et les opérations sur les coefficients polynomiaux a contrôlé :

- 792 images de monômes pour T1, N=2..12, dans neuf familles de paramètres rationnels ;
- 4 752 images de monômes pour T4, N=2..12, les deux parités, a,b,E dans {-2,0,3} ;
- 483 images dans les deux secteurs du contre-exemple généralisé, 2<=N<=8 et N<M<=10 ;
- 583 contrôles négatifs : perturbations interdites de B et vérification des degrés non fermés ;
- 336 identités rationnelles pour la réalisation inverse-carré ;
- les trois monômes du secteur lacunaire singulier.

Total : 6 946 contrôles comptabilisés, plus trois vérifications du secteur lacunaire. Tous passent. Ce programme contrôle les formules mais ne constitue pas une réplication par un autre chercheur. La preuve générale est donnée aux sections 1 et 2.

## 7. Audit bibliographique et interprétation minimale

Sources primaires consultées le 13 octobre 2026 :

1. Alexander Turbiner, Quasi-Exactly-Solvable Differential Equations, 1994. https://arxiv.org/abs/hep-th/9409068. L'auteur annonce une classification générale des opérateurs préservant des espaces polynomiaux et des opérateurs préservant une infinité de tels espaces.
2. Gerhard Post et Alexander Turbiner, Classification of linear differential operators with an invariant subspace of monomials, prépublication 1993, publication 1995. https://arxiv.org/abs/funct-an/9307001. Le résumé annonce une classification complète des sous-espaces à base monomiale.
3. Sergey Klishevich, Quasi-exact solvability and intertwining relations, 2004. https://arxiv.org/abs/hep-th/0410064. Le résumé mentionne l'entrelacement, deux sous-espaces monomiaux invariants et des exemples non réductibles aux monômes.
4. Alexander V. Turbiner, One-Dimensional Quasi-Exactly Solvable Schrödinger Equations, 2016. https://arxiv.org/abs/1603.02992. Revue du cadre quasi exactement soluble.

Ces notices vérifient l'existence et la portée générale des antécédents. Elles ne remplacent pas une comparaison ligne par ligne avec leurs preuves. Le seuil trois et les formules reconstruits ici ne sont donc pas revendiqués comme nouveaux : leur priorité exacte reste indéterminée dans cet audit.

Conclusion minimale : nous disposons de classifications prouvées pour des classes déclarées et d'un contre-exemple à une généralisation abusive. Nous n'avons pas obtenu de nouvelle famille ni une définition universelle de fermeture indépendante de la représentation. L'invariance d'un sous-espace est transportée par une conjugaison inversible, mais la propriété « ce sous-espace est le module polynomial complet de degré N » dépend du choix de coordonnée et de jauge.

## 8. Verrou suivant

Fixer une classe qui n'est pas déjà couverte par les classifications monomiales, avec une équivalence explicitement définie ; établir un invariant qui distingue ses secteurs de simples transformations de familles connues. Avant d'élargir aux espaces non polynomiaux, il faut lire intégralement les classifications citées. Aucune originalité, extrapolation physique ou résolution générale n'est acquise par les seuls résultats de cette note.