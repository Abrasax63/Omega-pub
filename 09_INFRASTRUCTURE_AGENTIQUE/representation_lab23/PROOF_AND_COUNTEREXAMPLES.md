# LAB23 — preuves élémentaires des deux changements de représentation

Ce document apporte les arguments mathématiques manuels associés au [run](https://github.com/Abrasax63/Omega-pub/actions/runs/44495656413). Ils sont classiques ; ce ne sont pas des preuves Lean ni de nouvelles découvertes.

## Définitions

Pour `T:X→X` finie et une observation `pi:X→{0,1}`, `E_h` est la relation sur les paires `(x,y)` dont les mots d'observation `(pi(x),...,pi(T^(h-1)x))` et `(pi(y),...,pi(T^(h-1)y))` sont égaux. Par convention, `E_0=X×X`.

## Relation par rappel (pullback)

Les mots de longueur `h+1` s'obtiennent en préfixant `pi(x)` au mot de longueur `h` lu depuis `T(x)`. Ainsi :

`(x,y) ∈ E_(h+1) iff (pi(x)=pi(y) and (T(x),T(y))∈ E_h)`.

Le cas `h=0` est universel. Une induction en `h` montre que la fonction `pair_pullback` calcule exactement les mêmes classes d'équivalence que le calcul direct pour tout `h`. Le code de la relation et le code de l'oracle sont séparés.

## Partition par signatures

Soit `P_0` la partition indiscrète. Définissons `P_(h+1)(x)` par la classe de la paire `(pi(x),P_h(T(x)))`. Comme deux signatures reçoivent le même code si et seulement si ces signatures sont égales, l'identité précédente donne par induction :

`P_h(x)=P_h(y) iff (x,y)∈E_h`.

L'algorithme `partition_refinement` est donc une représentation exacte de la relation observationnelle. C'est le principe classique de l'algorithme de Moore de raffinement des partitions des automates finis, cf. [MFCS 2019](https://drops.dagstuhl.de/storage/00lipics/lipics-vol138-mfcs2019/LIPIcs.MFCS.2019.77/LIPIcs.MFCS.2019.77.pdf).

## Monotonie et stabilisation (correction du préenregistrement)

En retirant le dernier symbole d'un mot, on obtient `E_(h+1) ⊆ E_h`. La récurrence de relations implique que si `E_(h+1)=E_h` pour un `h`, la même égalité se répète pour toutes les étapes suivantes.

- Si `pi` est constante, `E_1=E_2`, donc la stabilisation commence à `h=1`.
- Si `pi` n'est pas constante, `P_1` a au moins 2 classes. Chaque raffinement strict ajoute au moins une classe, sans dépasser `n` classes. Il peut donc y avoir au maximum `n-2` strictes étapes après `P_1`, d'où `P_(n-1)=P_n`.

En particulier, pour `n≥2`, la borne universelle sur la première stabilisation est `n-1`, pas `n`. La borne est atteinte par `T=(1,2,...,n-1,n-1)` et `pi=(0,...,0,1)` : une classe supplémentaire se sépare à chaque étape jusqu'à `h=n-1`. Pour `n=4`, `T=(1,2,3,3)` et `pi=(0,0,0,1)` produisent `E_2 != E_3=E_4`.

Le protocole original cherchait un témoin de la borne `n`, ce qui a **causé l'échec réel du premier run**. Voir [ERRATUM_FALSIFICATION.md](ERRATUM_FALSIFICATION.md), qui préserve la trace et ne réécrit pas le préenregistrement.

## Pourquoi trois autres représentations ne sont pas équivalentes

- Histogramme : `T=(1,0)`, `pi=(0,1)`, `h=2` ; les mots `(0,1)` et `(1,0)` ont le même histogramme mais diffèrent.
- Instant initial seul : `T=(0,0,1)`, `pi=(0,1,0)`, `h=2` ; la paire `(0,2)` a même couleur à `t=0`, mais mots `(0,0)` et `(0,1)` distincts.
- Futur seul : `T=(0,0)`, `pi=(0,1)`, `h=1` ; les deux états diffèrent immédiatement, mais coïncident après leur première transition.

**Statuts :** équivalence des deux premières représentations **démontrée par raisonnement** ; inadéquation des trois autres **réfutée par témoins exacts** ; efficacité numérique, originalité et créativité autonome **non démontrées**.
