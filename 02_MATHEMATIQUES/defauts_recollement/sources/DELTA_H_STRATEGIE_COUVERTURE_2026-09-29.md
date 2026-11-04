# Stratégie de résolution : fermeture finie autonome et couverture sous interventions

Itération du 29 septembre 2026, suite de `DELTA_H_FRONTIERE_COALITIONS_2026-09-29.md`. L'audit a imposé une séparation décisive. Pour le problème autonome initial, avec **une seule** application `T` et tous les états comme départs, l'ordre de fermeture est fini et admet une borne linéaire optimale. Pour l'extension contrôlée à deux actions, le rang de coalition d'un cycle de frontière peut varier arbitrairement entre deux présentations comportementalement minimales du **même** langage, y compris à nombre d'états égal. On ne transfère pas ce second énoncé au premier cadre.

## 1. Protocole de recherche désormais opérationnel

On travaille sur le langage `L` des chemins finis étiquetés par `(observation avant action, action)`, avec tous les états comme départs. Les actions sont totales et déterministes. L'ordre de décision est le suivant.

1. **Fixer la sémantique.** Conserver séparément langage des chemins finis, état initial accessible, multiplicités, et dynamique sous interventions. Une égalité de langages ne dit rien des multiplicités.
2. **Normaliser le langage.** Déterminiser les ensembles d'états compatibles avec un mot, minimiser le DFA obtenu et identifier chaque préfixe par son résiduel `R_u={z:uz∈L}`. Pour comparer deux présentations, parcourir le produit de leurs déterminisations : un désaccord produit un mot témoin; l'absence de désaccord après épuisement du produit prouve l'égalité pour toutes les longueurs.
3. **Falsifier une quantité proposée.** Chercher des présentations égales en langage par des modifications contrôlées, puis comparer la quantité. Les états « épissés » sans prédécesseur préservent le langage mais ne modifient pas les cycles utiles; quand cette chirurgie ne discrimine pas, reconstruire les entrées dans les composantes récurrentes.
4. **Analyser l'obstruction.** Construire la base minimale interdite `F`, le certificat de frontière `(B,v)` et les cycles utiles. Archiver un mot fantôme pompable et un certificat de non-existence des cycles plus petits.
5. **Changer de représentation.** Lorsque `|B|` dépend de la présentation, mesurer la couverture de **l'ensemble de futurs observable** `R_u`, puis calculer une borne intrinsèque sur les cycles interdits.
6. **Auditer.** Utiliser une seconde comparaison directe de mots courts, une perturbation négative qui doit produire un témoin, une preuve paramétrique indépendante du code et une comparaison bibliographique. Séparer chaque statut épistémique.

Le code joint implémente les points 2 à 6. Le produit de déterminisations est décisif : comparer seulement les mots de longueur bornée n'aurait pas validé l'identité de langage recherchée. Dans le cas autonome, la stratégie plus directe est le raffinement des partitions de traces exposé ci-dessous.

## 2. Théorème pour le problème initial à une seule dynamique

Supposons `T:X→X`, `π:X→Y`, avec tous les états comme départs. Quotienter d'abord par l'égalité des **traces infinies** `π(x)π(Tx)…`; noter `K` le nombre d'états du quotient et `q=|Y|` le nombre d'observations effectivement utilisées. Soit `d` le plus petit entier tel que la trace `S_d` distingue tous les états du quotient. Définir `r_cl` par les blocs autorisés de longueur `r+1`, en exigeant aussi les mots corrects de longueurs plus petites.

**DÉMONTRÉ :** `r_cl ≤ d ≤ K−q+1`. Tout mot interdit minimal a donc longueur au plus `K−q+2`, et la base interdite `F` est **toujours finie** dans ce cadre. Il n'existe aucun cycle utile de la frontière `(B,v)` après quotient comportemental.

Preuve. Les partitions selon `S_1,S_2,…` commencent avec `q` classes. Si deux partitions successives coïncident, la partition est stable sous `T` et ne se raffinera plus. Avant d'atteindre les `K` classes distinctes, chaque étape ajoute donc au moins une classe; d'où `d≤K−q+1`. Supposons qu'un mot possède tous ses blocs de longueur `d+1` dans `W_{d+1}`. Chacun de ces blocs impose un **unique** état initial par ses `d` premières observations. Deux blocs consécutifs imposent alors des états `x_i,x_{i+1}` avec `Tx_i=x_{i+1}`, puisque les `d` dernières observations du premier bloc sont les `d` premières du second. Ces états se recollent en une trajectoire unique réalisant le mot, d'où `r_cl≤d`. Un interdit minimal plus long que `d+1` contredirait cette propriété. La finitude de `F` implique l'absence de cycle utile par le critère de frontière déjà démontré.

**Borne optimale, DÉMONTRÉE.** Poser `n=K−q+1`. Prendre un état absorbant observé `0`, `q−2` états d'observations toutes distinctes `1,…,q−2` envoyés vers l'absorbant, et une chaîne de `n` états observés `b=q−1` qui descend vers l'absorbant. Toutes les traces infinies sont distinctes. Le mot `b^(n+1)` est interdit minimal, donc `r_cl≥n`; la borne précédente donne `r_cl=n`. Pour `q=2,K=5`, la réalisation explicite est `π=(0,1,1,1,1)` et `T=(0,0,1,2,3)` : `11111` est interdit minimal et `r_cl=4`.

**Borne optimale même sous aveuglement total des extrémités, DÉMONTRÉE.** Pour tout `K>q≥2`, poser `n=K−q+1≥2`. Garder l'état absorbant `s₀` observé `0`, les `q−2` états d'observations intermédiaires distinctes envoyés vers `s₀`, et parmi les `n` états observés `b=q−1`, prendre **une chaîne de `n−1` états** descendant vers `s₀` et **un état absorbant** observé `b`. Toutes les traces infinies sont distinctes. La relation observable `Q` a les seules arêtes `0→0`, `b→0`, `b→b` et `c→0` pour chaque autre observation `c`. Elle vérifie `Q²=Q`; de plus chacun de ces couples est effectivement réalisé entre les temps `0` et `h` pour **tout** `h≥1` (utiliser la première extrémité de la chaîne pour `b→0`, et l'absorbant `b` pour `b→b`). Par conséquent `Δ_h=∅` pour tout `h≥1`. Cependant `b^n0` est interdit minimal : son préfixe `b^n` est porté par l'absorbant `b`, son suffixe `b^(n−1)0` par la chaîne, et aucune trajectoire ne recolle les deux. Donc `r_cl=n=K−q+1`, aussi grand que la borne universelle. Pour `K=3,q=2`, `π=(0,1,1)`, `T=(0,0,2)`, `Γ₃={110}` et tous les `Δ_h` sont vides. C'est le plus petit cas non trivial : avec deux états et deux observations, l'observation est injective, donc aucun fantôme.

**Canonicité, DÉMONTRÉE.** Le langage de tous les mots finis détermine l'ensemble des traces infinies : une suite appartient à cet ensemble si tous ses préfixes sont réalisables. Les ensembles de départs compatibles avec ces préfixes sont finis, non vides et emboîtés; un état commun réalise donc toute la suite. Le quotient comportemental est canoniquement l'ensemble de ces traces, avec le décalage comme dynamique et la première lettre comme observation. Ainsi deux modèles autonomes minimaux de **même langage entier** sont isomorphes. Dans ce cadre, le coût de couverture `c_L(u)` défini à la section 4 égale exactement la taille de la croyance quotientée `|B(u)|` : un seul choix d'action laisse autant d'arbres distincts que de futurs infinis distincts. Le rang de coalition est par conséquent intrinsèque au langage autonome, mais il n'a **pas de cycle utile** et ne définit pas ici une profondeur infinie. La borne `h(L)` de la section 5 est alors sans objet (`F` est fini).

**CALCUL EXACT.** Pour les observations binaires et ternaires, 6 962 présentations autonomes comportementalement minimales de taille `K≤4` ont été auditées : `c_L(u)=|B(u)|` sur chaque résiduel accessible et aucun cycle utile. Un second balayage couvrant tous les `T` et chaque composition positive des tailles de fibres, à relabelage d'états près, a vérifié la borne et ses cas d'égalité jusqu'à `K=5`. Un troisième audit a comparé `Q^h` aux vrais couples à **tous** les horizons en itérant `(T^h,Q^h)` jusqu'à répétition : le premier cas avec `Δ_h=∅` partout et des fantômes apparaît à `K=3,q=2`. Ces calculs ne constituent pas la preuve des énoncés généraux.

Cette étape réoriente la question initiale sur `Δ_h` : son aveuglement peut être **maximal à tous les horizons**, alors que l'obstruction locale nécessaire atteint la profondeur maximale permise par `K,q`. Les fantômes peuvent subsister pour des longueurs arbitraires en contenant un facteur interdit court; cela ne rend pas `F` infini.

**Structure à ajouter à `Q`.** Comme `Q=W₂` et `W₁=Y`, la base canonique des facteurs interdits `F` de longueurs `3,…,d+1` contient exactement les interdictions supplémentaires nécessaires à la reconstruction de tous les `W_L`. Un mot dont les paires sont dans `Q` est fantôme **si et seulement s'il contient un facteur de cette base**. `F` est l'unique antichaîne minimale pour l'ordre « être facteur »; ceci n'est pas une prétention de compression optimale en nombre de bits. Le filtrage de `F` par longueur donne une hiérarchie de contextes qui s'arrête à `d≤K−q+1`. On calcule `d` par raffinement des partitions, puis les `W_{d+1}` depuis `K` trajectoires de longueur `d+1`, puis les facteurs minimaux interdits. Après prétraitement, un test direct d'un mot de longueur `L` vérifie ses fenêtres en temps `O(Ld)`; un automate de motifs peut éviter de rescanner chaque fenêtre. Les paires d'extrémités `Δ_h` demeurent une projection distincte de cette hiérarchie : les extrémités seules ne peuvent identifier quel mot intermédiaire a échoué.

Le paramètre `d` est une longueur **uniforme de distinction des états du quotient**, sans ensemble d'accès ni classe d'interventions. La coïncidence numérique éventuelle avec une profondeur `ℓ_{Γ,E}`, une longueur d'observabilité microscopique `L*` ou un horizon de stabilisation ne constitue pas une identification de ces objets.

## 3. Extension à deux actions : un rang arbitraire pour un langage fixe

Soit `m≥2`. La présentation brute `P_m` a `K=2m+4` états :

- `u_i`, `i∈Z/mZ`, puis `v,d`, d'observation 0 ;
- `h_i`, `i∈Z/mZ`, puis `e₁,e₂`, d'observation 1.

Deux actions `a,b` suffisent. Les transitions sont :

| État | Sous `a` | Sous `b` |
|---|---|---|
| `u_i` | `u_{i+1}` | `e₁` si `i=0`, sinon `d` |
| `v` | `v` | `e₂` |
| `d` | `e₂` | `e₂` |
| `h_i` | `u_i` | `u_i` |
| `e₁` | `d` | `e₂` |
| `e₂` | `e₂` | `e₂` |

**DÉMONTRÉ.** Tous les états sont comportementalement distincts. Les états `u_i` se distinguent par un nombre approprié de `a` suivi de `b`; `v` se distingue des `u_i` par la sortie après `b` puis `a` si nécessaire, `d` par sa sortie après `a`, et les marqueurs `h_i` par le comportement des `u_i` qui les suivent. Les états `e₁,e₂` ont des futurs distincts.

Pour tout `n≥1`, le mot

`f_n = (1,a)(0,a)^n(0,b)(1,a)(1,a)`

est minimal interdit. Son préfixe est réalisé depuis un marqueur dont la phase atteint `u₀` lors du `b`, puis `e₁→d`; son suffixe est réalisé depuis `v`, puis `e₂`. Le mot complet est irréalisable. Ainsi `F` est infini. Après une entrée par les marqueurs et deux lettres `(0,a)`, la croyance est exactement `U={u₀,…,u_{m−1}}`; `v` reste exclu et indistinguable sous la répétition de `(0,a)`. Les croyances accessibles, intersectées avec `U∪{v}`, ne valent que `∅`, `U` ou `U∪{v}`. Dans une boucle utile de frontière, les états transitoires `d,e₁` ne peuvent subsister, et la boucle sur `e₂` n'admet aucun témoin extérieur coaccessible; la seule boucle utile garde donc `U` face à `v`. **Le rang de coalition de `P_m` est exactement `m`.**

Considérons maintenant quatre états de base `v,d,g,t` observés 0 et quatre états `h_g,h_t,e₁,e₂` observés 1. Ils forment une présentation `C` de **huit états**, avec :

| État | Sous `a` | Sous `b` |
|---|---|---|
| `v` | `v` | `e₂` |
| `d` | `e₂` | `e₂` |
| `g` | `g` | `e₁` |
| `t` | `t` | `d` |
| `h_g` | `g` | `g` |
| `h_t` | `t` | `t` |
| `e₁` | `d` | `e₂` |
| `e₂` | `e₂` | `e₂` |

**DÉMONTRÉ.** `L(P_m)=L(C)` pour **tout** `m≥2`. Fixons une suite d'actions et examinons sa première occurrence de `b`, précédée de `k` actions `a`. Si `b` n'arrive pas, tous les `u_i`, `g` et `t` restent observés 0. Sinon, parmi les `u_i`, exactement un aboutit à `e₁` et les autres à `d`. L'état `g` donne toujours le premier comportement, `t` le second; après la sortie, leurs trajectoires coïncident avec celles des états correspondants. Par conséquent, l'union des langages individuels des `u_i` est exactement `L_g∪L_t`. La même égalité après la première lettre remplace l'ensemble des marqueurs `h_i` par `h_g,h_t`. Les états `v,d,e₁,e₂` sont identiques dans les deux constructions. Cette preuve porte sur **toutes** les suites d'actions, pas seulement sur la famille `f_n`.

Le rang de `C` vaut 2 : après `(1,a)(0,a)^2`, sa croyance est `{g,t}`, avec le témoin exclu `v`. Les deux états `g,t` restent ensemble sous `a` jusqu'à la sortie. Aucun singleton récurrent utile n'est accessible. La famille `f_n` est commune aux deux présentations.

**DÉMONTRÉ.** On peut imposer le **même nombre d'états** aux deux descriptions. Pour `m≥4`, conserver les `u_i` de `P_m` comme états initiaux supplémentaires dans la présentation compressée (leurs mots sont déjà couverts par `g,t`), puis ajouter `m−4` états sources observés 0, `z_j` pour `1≤j≤m−4`, avec `a(z_j)=u_{j+1}` et `b(z_j)=e₁`. Pour chaque première action, le langage de `z_j` est couvert par un `u_i` existant. Ces sources n'ont aucun prédécesseur et ne créent aucun cycle utile. Elles sont comportementalement distinctes entre elles et des autres états grâce à leurs réponses après `a`, puis une phase convenable et `b`.

La nouvelle présentation `Q_m` a donc elle aussi `K=2m+4`, elle est comportementalement minimale, `L(Q_m)=L(P_m)`, mais son rang vaut **2**. L'écart `m−2` est sans borne. Pour `m=4`, les deux présentations ont chacune 12 états et une même signature canonique de DFA à 12 états, mais des rangs 4 et 2.

**RÉFUTÉ.** Le rang de coalition d'une présentation, même après quotient comportemental et à `K`, `q`, alphabet d'actions et langage fixés, n'est pas un invariant du langage. La multiplicité diffère également : le mot `(1,a)(0,a)^2` a quatre états de départ dans `P₄` et deux dans `Q₄`, bien que son support et tous ses prolongements observables soient les mêmes.

## 4. Remplacement intrinsèque sous actions : coût de couverture des réponses

Pour chaque mot réalisable `u`, son résiduel observable est `R_u={z:uz∈L}`. Un **arbre de réponse déterministe** choisit une observation à chaque histoire d'actions, indépendamment des actions qui seront choisies plus tard; toutes ses branches finies doivent appartenir à `R_u`. Définir `c_L(u)` comme le plus petit nombre de tels arbres dont l'union couvre `R_u`. Les arbres autorisés sont des sélections **synthétiques** du langage; ils ne sont pas tenus d'être les trajectoires d'états d'une présentation finie particulière.

Pour calculer exactement cette quantité, poser `c₀(R)=1` si `R` est non vide et `0` sinon. Pour les horizons suivants :

`c_{n+1}(R) = somme sur y de [ maximum sur a de c_n(R_{(y,a)}) ]`.

**DÉMONTRÉ.** À observation initiale `y` fixée, un arbre doit couvrir séparément chaque choix d'action `a`. Il lui faut au moins autant de copies que la branche `a` la plus exigeante; les couvertures des différentes actions peuvent ensuite être appariées arbitrairement, car elles occupent des branches différentes du même arbre. Les observations initiales distinctes requièrent des arbres distincts, d'où la somme. Cette récurrence donne le minimum exact à chaque horizon. Les valeurs sont croissantes et bornées par `K` dans n'importe quelle présentation microscopique de `L`; sur le DFA canonique fini des résiduels, elles stabilisent. La compacité des arbres sur des alphabets finis permet de choisir des couvertures finies compatibles à tous les horizons : leur limite est bien `c_L(u)`, **calculable et intrinsèque au langage**, et satisfait `c_L(u)≤|B(u)|` pour toute présentation.

Le cas `c_L(u)=1` caractérise un résiduel dont toutes les sorties sont fonctionnelles pour chaque suite d'actions. Après quotient comportemental, cela équivaut exactement à `|B(u)|=1`. Pour `c_L(u)>1`, l'égalité avec `|B(u)|` peut échouer fortement : sur le préfixe `(1,a)(0,a)^2`, nous avons `c_L=2`, `|B_{P_m}|=m` et `|B_{Q_m}|=2`. La quantité `|B|-c_L` mesure ici une **redondance de présentation**, pas un défaut du langage.

Une première candidate plus simple, `ω_L(u)=max_{suite d'actions} nombre de réponses observables distinctes sous cette même suite`, satisfait `ω_L(u)≤c_L(u)` mais ne suffit pas. **RÉFUTÉ par quatre états :** avec `π=(0,0,1,1)`, `T_a=(0,2,0,0)` et `T_b=(0,0,0,2)`, toute suite commune d'actions distingue au plus trois réponses, donc `ω_L(ε)=3`. Les deux états d'observation 0 demandent deux arbres à cause de `a`; les deux états d'observation 1 en demandent deux à cause de `b`. Ces demandes ne se superposent pas : `c_L(ε)=4`.

## 5. Une borne intrinsèque sur les cycles fantômes contrôlés

La base interdite `F` est reconnue par un automate de trois résiduels **canoniques** : celui du mot lu, celui du mot privé de sa dernière lettre et celui du mot privé de sa première lettre. Un état est final lorsque le mot entier est impossible et les deux facteurs propres restent possibles. Cela n'utilise plus les états de la présentation.

Pour `F` infini, définir `h(L)` comme le plus petit seuil `k` pour lequel le sous-graphe des états accessibles et utiles de cet automate, restreint aux préfixes dont le coût `c_L` est au plus `k`, contient un cycle.

**DÉMONTRÉ.** Pour toute présentation comportementalement minimale `P` du même langage et de rang de coalition `κ(P)`, on a `h(L)≤κ(P)`. Un cycle utile de frontière avec `|B|=r` produit des mots interdits minimaux arbitrairement longs; chaque préfixe rencontré sur la boucle possède `c_L≤r`. Après pompage et passage dans l'automate canonique fini de `F`, ces chemins donnent un cycle utile situé sous le seuil `r`.

**CALCUL EXACT.** Pour le langage commun aux `P_m`, `Q_m` et `C`, le DFA canonique de `L` possède 12 états, celui de `F` construit ci-dessus 56 états accessibles, dont 34 utiles. L'examen exhaustif donne `h(L)=2`. La présentation `C` atteint cette borne : le plus petit rang **parmi toutes les présentations** de ce langage est donc exactement 2. L'égalité générale `h(L)=min_P κ(P)` demeure **INDÉTERMINÉE**.

## 6. Audit et limites

**CALCUL EXACT.** Les égalités de langages ont été vérifiées par deux méthodes : signatures de DFA minimisés et parcours produit exhaustif sans témoin de différence. Pour `m=4`, une seconde routine de trajectoires microscopiques directes a comparé tous les mots jusqu'à longueur 6. Une mutation négative d'une seule transition a bien produit un mot qui distingue les langues. Les formules de rang et de mots minimaux ont été contrôlées pour `m=2,…,10` et `n` jusqu'à 100 selon les familles. Le calcul soutient les preuves paramétriques; il ne les remplace pas. La borne `h≤κ` a également été confrontée à 177 petites présentations minimales tirées avec une graine fixe, sans contre-exemple; cette dernière vérification est une **SIMULATION**.

**Invariance de représentation.** Le DFA minimal de `L`, ses résiduels, `c_L` et `h(L)` ne dépendent que du langage des chemins finis et de l'alphabet action-observation fixé. Ils changent légitimement si l'on change les actions admissibles ou l'ensemble de départ. Sous **plusieurs actions**, `κ(P)` et les multiplicités peuvent dépendre de la présentation; avec **une seule action**, le quotient comportemental est canonique et `κ` est intrinsèque, sans cycle utile. La preuve ne transfère pas automatiquement ces conclusions aux sous-décalages bilatères qui écartent les chemins transitoires.

**Journal des réfutations et du changement de méthode.** Le graphe des paires détectait une obstruction possible sans décider sa persistance; le singleton de frontière manquait les obstructions collectives; l'échantillonnage aléatoire avait manqué la première coalition de rang 2. La famille tournante a ensuite montré tous les rangs, mais sa compression en comportements « toujours succès / toujours échec » a réfuté l'invariance supposée du rang. Une nouvelle tentative fondée sur le maximum de sorties d'une seule suite d'actions a échoué sur quatre états. Chacun de ces échecs a déplacé le calcul vers le langage canonique et la récurrence de couverture, au lieu de seulement agrandir les énumérations.

**CONNU DANS LA LITTÉRATURE / REFORMULATION.** Le raffinement des états par expériences observables remonte aux machines de [Moore, 1956](https://www.cs.cmu.edu/~cdm/resources/Moore1956-gedanken-experiments.pdf); les langages factoriels, leurs facteurs interdits et les automates de résiduels sont classiques : [Béal et al., 2003](https://doi.org/10.3233/FUN-2003-561-208), [Rogers et Lambert, 2017](https://aclanthology.org/W17-3404/). Les présentations déterministes de systèmes sofiques sont étudiées par [Cai et Frongillo, 2022](https://doi.org/10.1016/j.tcs.2022.09.017), avec des conventions qu'il faut distinguer des chemins finis à départ arbitraire ici. La sélection déterministe dans une relation est voisine de l'[uniformisation de transducteurs](https://doi.org/10.4230/LIPIcs.ICALP.2016.125); les couvertures par fonctions sont également proches de [Weber, 1993](https://doi.org/10.1137/0222014) et [Daviaud et al., 2017](https://arxiv.org/abs/1701.04632). Ici `c_L` autorise des arbres de réponse qui ne sont pas nécessairement à état fini; il faut préserver cette distinction. La preuve du majorant linéaire optimal pour l'unique dynamique est donnée ici, mais **je ne peux pas confirmer une priorité littéraire** pour cette borne exacte, la récurrence de couverture ou la famille à deux actions sans recherche bibliographique spécialisée supplémentaire.

## 7. Résultats et prochain verrou

| Énoncé | Statut |
|---|---|
| Système autonome : `r_cl≤K−q+1`, borne atteinte, quotient canonique, `F` fini | DÉMONTRÉ |
| Pour tout `K>q≥2` : `Δ_h=∅` pour tous les horizons et `r_cl=K−q+1` | DÉMONTRÉ |
| Balayage autonome `K≤5` pour la borne et `K≤4` pour la couverture | CALCUL EXACT |
| Famille à deux actions, langage fixe, rang brut arbitraire; paires de même `K` et rangs `m` contre 2 | DÉMONTRÉ |
| Invariance du rang après quotient avec plusieurs actions et langage fixé | RÉFUTÉ |
| Récurrence du coût intrinsèque `c_L` et borne `h(L)≤κ(P)` | DÉMONTRÉ |
| `ω_L=c_L` en général | RÉFUTÉ |
| `h(L)=2` pour le langage témoin | CALCUL EXACT |
| `h(L)=min_P κ(P)` pour tout langage admissible | INDÉTERMINÉ |
| Bases interdites, résiduels, décomposition générale de transducteurs | CONNU DANS LA LITTÉRATURE |
| Vocabulaire « coût de couverture des réponses » dans ce cadre déterministe | REFORMULATION |

**Prochain verrou au plus fort gain d'information :** dans le cadre autonome, caractériser le **plus petit ordre** `r_cl` directement par la géométrie des fibres et les cycles/transitoires du quotient, puis classifier les petits cas où `Δ_h=∅` mais `r_cl>1`. La borne optimale fournit désormais un horizon fini de recherche. Pour l'extension sous interventions, chercher un langage contrôlé pour lequel `h(L)<min_P κ(P)`; il faudrait montrer qu'un cycle autorisé par le DFA intrinsèque ne peut être réalisé par une famille finie cohérente d'états sous toutes les actions. Si aucun contre-exemple n'apparaît, tenter une construction effective d'une présentation atteignant `h(L)`. Pour un accès restreint `E` et des interventions `I`, recalculer `L_{H_I}` tout en gardant séparé le défaut initial `L_{H_I}\setminus L_E`.

Fichiers reproductibles : `delta_uncontrolled_canonical.py`, `delta_uncontrolled_closure_bound.py`, `delta_uncontrolled_delta_gap.py`, `delta_coalition_family.py`, `delta_language_equivalence.py`, `delta_response_width.py`, `delta_cover_rank.py`, `delta_intrinsic_cycles.py` et leurs données JSON. Ils importent les trois scripts du cycle précédent inclus dans l'archive.

**Reproduction.** Extraire l'archive dans un même dossier, puis exécuter chaque script ci-dessus avec `python3` depuis ce dossier; seule la bibliothèque standard de Python est requise. Les scripts réécrivent leurs JSON d'audit. Le balayage autonome regroupe les observations par compositions ordonnées des tailles de fibres : tout étiquetage de `π` est obtenu par permutation des états d'un de ces cas; les `T` sont ensuite tous énumérés. Pour la famille paramétrique, les assertions couvrent `2≤q≤4`, `q<K≤8`; sa preuve générale ne dépend pas de cette plage.