# Δ_h — accès, interventions et obstructions persistantes

Itération v1.1 du 29 septembre 2026. Point de départ certifié : `DELTA_H_RECOLLEMENT_INTERNE_2026-09-29.md` établit, pour une dynamique autonome déterministe finie, la base de mots interdits minimaux et `r_cl≤L*≤K−q+1`. Cette note teste exactement la frontière de cette conclusion lorsque l'ensemble initial est restreint ou que plusieurs actions sont possibles. Aucun résultat du socle n'est rétrogradé.

## 1. Prédictions figées avant calcul

- H₀ : plusieurs interventions totales préservent une borne uniforme du type `K−q+1` sur l'ordre local. **Prédiction : faux**, car une phase invisible peut tourner arbitrairement longtemps avant une sonde.
- H₁ : une machine à trois états, deux observations et deux actions totales suffit à produire des interdictions minimales de longueurs non bornées. **Prédiction : vrai**.
- H₂ : une restriction des états initiaux ne change que la base des mots interdits. **Prédiction : faux**, car le langage enraciné n'est généralement plus factoriel.

Le calcul a été exécuté après ces prédictions; les preuves ci-dessous ne dépendent pas de l'absence de contre-exemple dans l'énumération.

## 2. Deux cadres qu'il faut séparer

Soit `A` un ensemble fini d'actions, et pour chaque `a∈A`, `T_a:X→X` une application totale. L'observation `π:X→Y` reste fixe. Une lettre est le couple `(π(x_i),a_i)` : elle enregistre l'observation avant l'application de l'action. Ainsi le langage `L_E⊆(Y×A)*` regroupe les mots produits depuis un état initial de `E⊆X`. La dernière action enregistrée est toujours applicable, même si son observation ultérieure n'est pas inscrite dans le mot.

Définir la **clôture accessible** `H=⋃_{u∈A*}T_u(E)`. Elle est stable par chaque action. Les deux langages ont des rôles distincts :

- `L_E` est un langage *enraciné*, fermé par préfixes ;
- `L_H` est un langage *factoriel*, fermé par tout facteur contigu.

**[DÉMONTRÉ, CERT-V]** `Fact(L_E)=L_H`. Un facteur d'un mot issu de `E` commence nécessairement dans `H`. Inversement, si `z∈H`, une suite d'actions mène d'un état de `E` à `z` ; tout mot produit depuis `z` apparaît alors comme suffixe d'un mot issu de `E`. Le résultat ne dépend que du langage observable et résiste donc à un changement de présentation comportemental.

Cela fournit un objet utile dans notre cadre : le **défaut de frontière d'accès**

`A_E = Fact(L_E) \ L_E`.

Le nom est proposé ici pour cette analyse, sans revendication de nouveauté terminologique. Il compte les mots réalisables plus tard dans une expérience, mais indisponibles au départ. Le mot « frontière » désigne la condition initiale, pas une frontière topologique ou un faisceau.

Pour une clôture locale `M_H` calculée dans `H`, la décomposition est exacte et disjointe :

`M_H \ L_E = (M_H \ L_H) ⊔ (L_H \ L_E)`.

Le premier terme est le défaut de recollement; le second est le défaut d'accès. Le premier peut ensuite être séparé par les projections d'extrémités `Δ_u` et les fantômes internes pour chaque suite d'actions `u`. Construire la relation locale à partir de `E` sans prendre sa clôture `H` mélangerait les deux mécanismes, car une trajectoire issue de `E` peut quitter `E`.

**[DÉMONTRÉ, contre-exemple minimal]** Deux états `a→b→b`, observations `π(a)=0`, `π(b)=1`, un seul contrôle, `E={a}`. Le mot `01` vient de `E`, mais son facteur `1` ne peut pas commencer dans `E`. Pourtant `1` commence dans `H={a,b}` et tous les mots localement permis dans `H` sont réellement réalisables. Ainsi le défaut d'accès est infini (`1,11,111,…`) avec aucun défaut de recollement. H₂ est **RÉFUTÉ**.

## 3. Intervention totale créant une mémoire locale infinie

**[DÉMONTRÉ, CERT-V]** Trois états suffisent. Numéroter `c=0`, `u=1`, `v=2`. Leurs observations sont `π(c)=1`, `π(u)=π(v)=0`. Deux actions totales :

| État | action `a` | action `b` |
| --- | --- | --- |
| `c` | `u` | `c` |
| `u` | `v` | `c` |
| `v` | `u` | `v` |

Pour tout entier impair `n≥1`, le mot sur l'alphabet `(observation,action)`

`f_n=(1,a)(0,a)^n(0,b)(1,a)`

est interdit minimal. Le premier symbole impose l'état `c`, puis l'action `a` entre en `u`. Les `n` répétitions de `a` conduisent en `v` lorsque `n` est impair; l'action `b` laisse alors le système en `v`, ce qui rend le dernier symbole `1` impossible. Le préfixe sans le dernier symbole est possible. Le suffixe sans le premier symbole est possible en choisissant la phase initiale `u` ou `v` qui conduit en `u` avant `b`. Tous les autres facteurs propres sont des facteurs de l'un de ces deux mots réels. La longueur des `f_n` vaut `n+3` et n'est pas bornée. Donc `r_cl(A)=∞`.

L'exemple est minimal en trois sens : si `|X|≤2` avec deux observations, l'état est connu et la compatibilité locale avec l'action suffit; avec une seule observation, toutes les suites d'actions sont possibles; avec une seule action, la borne autonome finie du socle s'applique. Les trois états sont distinguables comportementalement : `c` se distingue immédiatement, et `u,v` après l'action `b`.

Chaque mode considéré seul reste de profondeur finie. L'audit du quotient autonome donne `r_cl({a})=1` et `r_cl({b})=2`; la réunion des protocoles permet `r_cl({a,b})=∞`. H₀ est **RÉFUTÉ**. Il s'agit d'une mémoire de *phase cachée entre deux sondes*, et non d'une croissance du nombre d'états. La proximité avec les shifts sofics stricts est une traduction mathématique, pas une équivalence particulière revendiquée avec un exemple classique.

## 4. Certificat cyclique exact, au-delà de l'exemple

**[DÉMONTRÉ, CERT-V]** Pour un ensemble de départ fermé `H`, définir le filtre des croyances

`δ(B,(y,a))={T_a(x):x∈B,π(x)=y}`.

Un mot `w` est possible si et seulement si `δ(H,w)≠∅`. Sa base interdite minimale est régulière :

`F = (L_H Σ) ∩ (Σ L_H) \ L_H`, où `Σ=Y×A`.

En effet, `L_H` est factoriel : vérifier le préfixe et le suffixe propres les plus longs suffit à vérifier tous les facteurs propres. `L_H` est reconnu par l'automate fini des ensembles de croyance; les opérations indiquées préservent la régularité.

Une construction explicite suit trois registres de croyance : `B_w` pour le mot entier, `B_p` pour le mot privé de sa dernière lettre, `B_s` pour le mot privé de sa première lettre. Après une nouvelle lettre `z`,

`(B_w,B_p,B_s) → (δ(B_w,z),B_w,δ(B_s,z))`.

Les états acceptants satisfont `B_w=∅`, `B_p≠∅`, `B_s≠∅`. L'ensemble `F` est infini **si et seulement si** un cycle accessible de cet automate peut encore atteindre un état acceptant. C'est un certificat fini de profondeur de recollement non bornée. S'il n'existe pas de tel cycle, la longueur maximale des interdictions est bornée par le nombre d'états accessibles de l'automate, au plus `8^K`. Cette borne est grossière mais entièrement effective.

Cette construction est une **REFORMULATION** opérationnelle des critères élémentaires de régularité et de cycles des automates. Elle est utile ici parce qu'elle fournit un témoin structurel vérifiable plutôt qu'une suite de tests d'horizons croissants. Les mots interdits minimaux et les langages factoriels réguliers sont déjà étudiés, notamment par Béal, Crochemore, Mignosi, Restivo et Sciortino, *Computing forbidden words of regular languages* (2003), https://doi.org/10.3233/FUN-2003-561-208. La distinction entre shifts de type fini et sofics est également classique; Good et Meddaugh (2020) expliquent le rôle des motifs de pseudo-orbites locales : https://doi.org/10.1007/s00222-019-00936-8.

## 5. Falsification, reconstruction et limites

`delta_interventions_audit.py` réalise l'automate de trois croyances et énumère exactement les présentations surjectives avec deux actions totales. Résultats bruts :

| `|X|,q` | Présentations | Base infinie |
| --- | ---: | ---: |
| 2,2 | 32 | 0 |
| 3,2 | 4 374 | 864 |
| 3,3 | 4 374 | 0 |

Ce sont des présentations étiquetées, non quotientées par isomorphisme; la preuve de minimalité du §3 ne repose pas sur ces nombres. Pour l'exemple fixé, l'automate comporte 41 états accessibles, dont 10 acceptants, et possède un cycle utile. `delta_interventions_crosscheck.py`, écrit avec une simulation directe des trajectoires, vérifie seize mots interdits de la famille, leurs facteurs propres, les voisins pairs réalisables, puis l'invariance de mots courts sous les 24 changements de codage des états, observations et actions. Il vérifie séparément le contre-exemple d'accès à deux états. La formule générale et le critère cyclique disposent des preuves ci-dessus; la seconde implémentation ne constitue pas une vérification exhaustive indépendante des 864 présentations.

**Barrière de généralisation.** Les actions sont ici totales, l'ensemble des contrôles fini, le système déterministe, l'observation fixe, et toutes les suites d'actions sont autorisées. Une contrainte de protocole à mémoire finie peut s'ajouter à l'état; une contrainte de politique sans mémoire finie ne relève pas automatiquement du certificat. L'ordre `r_cl=∞` porte sur les mots de couples action–observation, pas sur l'ordre de la seule trace des observations et pas sur une profondeur d'autonomie relative `ℓ_{Γ,E}`. Il ne doit être identifié ni à `L_A`, ni à `L_P`, ni à `L*`.

## 6. État épistémique et prochain test

- **DÉMONTRÉ / CERT-V** : `Fact(L_E)=L_H`, séparation accès/recollement, famille à base interdite infinie, critère cyclique exact.
- **CALCUL EXACT** : nombres bruts `0/32`, `864/4374`, `0/4374`; calcul reproductible, sans extrapolation.
- **RÉFUTÉ** : la borne autonome `K−q+1` sous plusieurs interventions; la factorisation directe du langage enraciné `L_E`.
- **CONNU DANS LA LITTÉRATURE / REFORMULATION** : mots interdits minimaux, shifts sofics, automates de croyance et détection de cycles. La priorité bibliographique d'une réalisation contrôlée précise et du triplet accès/recollement/extrémités demeure **INDÉTERMINÉE** : je ne peux pas confirmer leur nouveauté scientifique.
- **Rollback** : aucun résultat autonome antérieur n'est invalidé; son hypothèse « une unique loi `T` » est maintenant explicitement indispensable à la borne finie.

**Un seul prochain verrou :** caractériser directement, sur le graphe des paires d'états cachés et les sondes accessibles, les cycles qui donnent `r_cl=∞`, afin de remplacer l'automate à trois croyances de taille potentiellement `8^K` par un certificat plus petit ou un contre-exemple à cette compression.