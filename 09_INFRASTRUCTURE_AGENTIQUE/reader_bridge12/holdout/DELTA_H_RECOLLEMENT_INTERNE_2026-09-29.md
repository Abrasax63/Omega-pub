# Δ_h : première obstruction de recollement interne

Itération de recherche du 29 septembre 2026. Cadre : application totale déterministe finie `T:X→X`, observation surjective `π:X→Y`, `q=|Y|`. Les statuts ci-dessous portent sur les énoncés de cette itération, pas sur une revendication de priorité historique.

## 1. Ce qui manque exactement à Q

**[DÉMONTRÉ]** Écrire `X_a=π⁻¹(a)`. Pour un triple `abc` localement admissible, les deux transitions `ab` et `bc` peuvent être réalisées par des témoins différents. Le triple est réalisable exactement quand

`T(X_a) ∩ X_b ∩ T⁻¹(X_c) ≠ ∅`.

Le graphe `Q` garde les deux assertions séparées `T(X_a)∩X_b≠∅` et `X_b∩T⁻¹(X_c)≠∅`, mais perd l'identité de l'état dans leur intersection. Une incidence binaire entre *types* de transitions (autrement dit la seule liste des triples réalisables) répare les triples sans garantir les mots plus longs.

Pour un mot `w=y₀…yₙ₋₁`, poser `B₀=X_{y₀}` puis `Bᵢ=T(Bᵢ₋₁)∩X_{yᵢ}`. Alors `w∈Wₙ` si et seulement si `Bₙ₋₁≠∅`. Le premier `i` tel que `Bᵢ=∅` fournit un certificat d'échec : toutes les réalisations du préfixe encore présentes à `i−1` refusent la lettre suivante. L'algorithme utilise `O(n|X|)` opérations élémentaires et `O(|X|)` mémoire sur la table fonctionnelle de `T`, sans énumérer les chemins possibles séparément.

## 2. Plus petit système où Δ ne voit rien

**[DÉMONTRÉ : minimalité, calcul corroborant]** Trois états suffisent et moins de trois sont impossibles avec deux observations. Soient `X={a,b,c}`, `π(a)=π(b)=0`, `π(c)=1`, et

`T(a)=a`, `T(b)=c`, `T(c)=c`.

Les trois traces infinies sont `0∞`, `01∞` et `1∞`. `Q={00,01,11}`. Pour tout `h≥1`, `Q^h={00,01,11}` et les trajectoires issues de `a,b,c` réalisent respectivement ces trois paires à l'horizon `h` : `Δ_h=∅` pour tout `h`.

Pourtant `001∈M₃\W₃` : le témoin de `00` arrive en `a` et celui de `01` doit partir de `b`; ils appartiennent à la même fibre `0` sans être raccordables. La paire d'extrémités `01` est réellement réalisable par `011`, d'où un fantôme purement interne. Ici `W₃={000,011,111}`, `Γ₃={001}`, `L*=2` et `r_cl=2`. Si `|X|≤2` et `q=2`, l'observation est injective; si `q=1`, il n'existe aucun mot fantôme. Cela prouve la minimalité en nombre d'états et d'observations non triviaux.

## 3. Candidats et réfutations immédiates

| Donnée additionnelle | Test | Statut |
| --- | --- | --- |
| `μ₂` ou les nombres de témoins de chaque arête | Deux systèmes minimaux à quatre états ont même `Q`, même `μ₂` et `Δ_h=∅` à tous les horizons, mais des `W₃` différents; voir §4. | **RÉFUTÉ** comme donnée suffisante |
| Compatibilité existentielle entre deux transitions observables (`W₃`) | La famille du §5 donne `000,001∈W₃`, mais `0001∉W₄`. | **RÉFUTÉ** comme donnée suffisante à tous les horizons |
| Filtre des ensembles de survivants `Bᵢ` / matrices booléennes étiquetées | Récurrence exacte ci-dessus. | **DÉMONTRÉ** suffisant; présentation non minimale en général |
| Ensemble des mots interdits minimaux `F` | Un mot est possible si et seulement s'il ne contient aucun mot de `F`. | **DÉMONTRÉ** suffisant et unique comme base de facteurs interdits |
| Automate minimal des continuations `F(w)={u:wu∈W_*}` | Quotients résiduels de Myhill–Nerode. | **CONNU DANS LA LITTÉRATURE**; minimal parmi les reconnaisseurs déterministes en ligne |

La « plus petite information » dépend donc de la catégorie autorisée. La base interdite est minimale sous inclusion parmi les descriptions par facteurs interdits; l'automate résiduel est minimal en nombre d'états parmi les automates déterministes complets reconnaissant `W_*`. Il n'y a ici aucune preuve d'un minimum universel en bits.

## 4. Même Q, mêmes extrémités et mêmes multiplicités à deux pas

**[CALCUL EXACT, avec vérification manuelle des trajectoires]** Numéroter les états `0,1,2,3`.

- A : `T=(0,0,2,2)`, `π=(0,1,1,0)`. Les traces de longueur 3 sont `W₃(A)={000,011,100,111}`.
- B : `T=(1,0,0,1)`, `π=(0,1,0,1)`. Les traces de longueur 3 sont `W₃(B)={001,010,101,110}`.

Les deux systèmes ont quatre futurs distincts, `Q=Y²` et `μ₂(00)=μ₂(01)=μ₂(10)=μ₂(11)=1`. Dans A, les boucles `0` et `1` et les deux transitions transitoires donnent toutes les paires d'extrémités à chaque horizon. Dans B, les deux états d'un cycle alterné et les deux états transitoires les donnent également à chaque horizon. Ainsi `Δ_h(A)=Δ_h(B)=∅` pour tout `h`, mais `001` est fantôme pour A et réalisable pour B. Leurs bases interdites minimales sont respectivement `{001,010,101,110}` et `{000,011,100,111}`. Ce test ne repose ni sur des duplications d'états ni sur un changement de code : les langages diffèrent réellement.

## 5. Obstructions internes de profondeur arbitraire

**[DÉMONTRÉ]** Pour `m≥1`, prendre un état `a` fixé de couleur `0`, un état `c` fixé de couleur `1`, et une chaîne `b_m→b_{m−1}→…→b₁→c`, tous les `b_j` de couleur `0`. Le quotient comportemental a `K=m+2`, `q=2` et `L*=m+1`. Les futurs sont `0∞`, `01∞`, `001∞`, …, `0^m1∞`, `1∞`.

Tous les `Δ_h` sont vides : les paires possibles sont toujours `00`, `01`, `11`, réalisées par `a`, `b₁`, `c`. La base des mots interdits minimaux est exactement `{10, 0^{m+1}1}`. La transition `10` est déjà exclue par `Q`; le seul renseignement additionnel par rapport à `Q` est `0^{m+1}1`. Donc `r_cl=m+1=K−q+1`. Lorsque `m=2`, les triples `000` et `001` sont chacun réalisables, mais leur raccordement `0001` est fantôme. Le seuil `K−q+1` est atteint pour tout `K≥3` dans cette famille.

## 6. Théorème fini et coût

**[DÉMONTRÉ]** Sur le quotient comportemental `Z` des futurs observables, de taille `K`, définir `L*` comme la plus petite longueur séparant tous ses états. Toute *interdiction minimale* (mot impossible dont tout facteur propre est possible) a longueur au plus `L*+1`.

Preuve : si `u` est minimal interdit de longueur `n≥L*+2`, son préfixe de longueur `n−1` est produit par un état `x` et son suffixe de longueur `n−1` par un état `z`. Les états `T(x)` et `z` produisent le même bloc de longueur `n−2≥L*`, donc ils ont le même futur. Le dernier symbole du suffixe complète alors aussi le chemin issu de `x`, contradiction.

La partition des états par leurs préfixes s'affine strictement tant qu'elle n'est pas stable. Elle commence avec `q` classes et finit avec `K`, d'où `L*≤K−q+1`. Ainsi `r_cl≤L*≤K−q+1`, borne optimale par la famille du §5. La base `F` est l'ensemble unique des mots impossibles dont tous les facteurs propres sont possibles : tout mot impossible contient un tel facteur, et toute base de facteurs interdits doit contenir chacun d'eux.

À chaque longueur `j`, il existe au plus `K` mots réellement produits, donc au plus `qK` extensions candidates minimales interdites. Le nombre de mots de la base est au plus `qK L*`. Sa taille textuelle peut coûter `O(qK(L*)²)` symboles. `Q` requiert jusqu'à `q²` bits, alors que la description fonctionnelle du quotient utilise `K` successeurs et `K` étiquettes. L'automate des ensembles survivants construit depuis l'ensemble des `K` états comporte au plus `K L*+2` états accessibles, y compris l'état initial et le puits : il existe au plus `K` préfixes à chaque longueur `1,…,L*−1`, puis uniquement des ensembles singletons. Après minimisation par continuations, c'est l'automate canonique du langage. Leurs ensembles survivants distincts sont déjà distinguables par des futurs de longueur `L*` sur le quotient comportemental.

**Attention.** Cette borne finie utilise le déterminisme *sans entrée*, l'ensemble fini de `K` futurs et l'observation de tous les états. Elle ne doit pas être transposée telle quelle à une chaîne de Markov cachée, à un graphe étiqueté ramifié ou à des interventions : ces cadres peuvent posséder infiniment de futurs possibles.

## 7. Position exacte de Δ dans le défaut

**[DÉMONTRÉ]** Pour `h=L−1`, soit `e(w)=(w₀,w_h)`. Le défaut se scinde sans recouvrement :

`Γ_L = {w∈M_L : e(w)∈Δ_h} ⊔ {w∈M_L\W_L : e(w)∈R̄_h}`.

Le premier ensemble représente les extrémités fantômes; le second, les mots fantômes dont les extrémités sont possibles. `Δ_h` est l'image par `e` du premier ensemble. La base interdite `F₂,F₃,…,F_{L*+1}` forme une gradation canonique des obstructions selon la longueur du contexte requis. Il serait trompeur de prétendre que la projection sur les extrémités et cette gradation sont une seule chaîne totale d'invariants : ce sont deux axes d'information distincts.

## 8. Audit exact et limites

Les programmes `delta_gluing_audit.py` et `delta_gluing_crosscheck.py` sont reproductibles sans dépendance tierce. Le premier énumère les présentations brutes `T,π` surjectives, calcule les horizons par récurrence exacte de l'état produit `(Q^h,T^h)`, les bases minimales et le quotient comportemental. Le second vérifie par un parcours de matrices booléennes, indépendant de la construction directe des mots, les bases sur tous les systèmes à deux couleurs de taille `2,3,4` et à trois couleurs de taille `3,4`, pour des mots jusqu'à `|X|+2`; il vérifie séparément la borne sur les interdictions minimales. Les cinq premiers membres de la famille sont testés à davantage d'horizons et le sixième pour la taille de l'automate d'ensembles.

| `|X|,q` | Présentations surjectives brutes | `Δ_h=∅` pour tout `h` | `Δ≡∅` et `Γ₃≠∅` | `r_cl` maximum |
| --- | ---: | ---: | ---: | ---: |
| 2,2 | 8 | 8 | 0 | 1 |
| 3,2 | 162 | 102 | 12 | 2 |
| 4,2 | 3 584 | 1 736 | 408 | 3 |
| 5,2 | 93 750 | 36 630 | 12 160 | 4 |
| 3,3 | 162 | 162 | 0 | 1 |
| 4,3 | 9 216 | 4 032 | 288 | 2 |

Ces dénombrements portent sur des présentations étiquetées brutes, **pas** sur des classes d'isomorphisme. Les preuves ci-dessus établissent les résultats généraux indépendamment des dénombrements. Une énumération exhaustive à six états et trois couleurs n'a pas été effectuée.

## 9. Comparaison bibliographique et prochain verrou

**[CONNU DANS LA LITTÉRATURE]** Les mots interdits minimaux et leur calcul pour les langages factoriels réguliers sont étudiés par Béal et al. (2003), [Computing forbidden words of regular languages](https://doi.org/10.3233/FUN-2003-561-208). Les *follower sets* sont une construction standard en dynamique symbolique, par exemple French (2019), [Follower, predecessor, and extender set sequences](https://doi.org/10.3934/dcds.2019175). Les shifts de type fini sont définis par une liste finie de mots interdits : Good et Meddaugh (2020), [Shifts of finite type as fundamental objects in the theory of shadowing](https://doi.org/10.1007/s00222-019-00936-8), opposent les pseudo-orbites locales aux véritables orbites. La minimisation par continuations relève du théorème de Myhill–Nerode. Ces notions ne sont donc pas nouvelles.

**[REFORMULATION]** Leur articulation explicite avec `Δ_h`, la scission extrémités/interne et le certificat par survivants traduit le problème présent dans le langage standard des automates et des shifts. **[INDÉTERMINÉ]** Une priorité bibliographique pour la borne `r_cl≤K−q+1` et sa saturation par la famille ci-dessus n'est pas établie par cette recherche ciblée. Ne pas annoncer de théorème inédit dans une soumission avant revue bibliographique approfondie et audit externe.

**Prochain verrou à fort gain d'information :** déterminer comment une restriction d'états accessibles ou des interventions typées change la base interdite et l'automate des survivants. La mise à jour `B↦T_i(B)∩X_a` reste exacte pour chaque action `i`, mais la preuve de la borne `K−q+1` n'est plus applicable sans une hypothèse remplaçant le futur unique de chaque état.