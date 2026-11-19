# LAB23 — ERRATUM falsificateur au préenregistrement, 19/11/2026

**Ne remplace pas `PREREG.md`.** Dans ce préenregistrement, nous avons conjecturé qu'il existe un exemple binaire à `n=4` où la relation d'indistinguabilité ne se stabilise qu'à `h=n`. Cette hypothèse de *borne atteinte* est **RÉFUTÉE**.

## Observation avant correction
[Premier run #44495078554](https://github.com/Abrasax63/Omega-pub/actions/runs/44495078554) : 4 328 systèmes/colorations exhaustifs à `n=2..4`, puis 128 instances à 5/6 états. Les deux représentations de type paire et partition concordaient avec le calcul direct. Les invariants de monotonie et d'arrêt à `h=n` tenaient. Mais **aucun** cas avec `E_{n-1} != E_n` n'a été observé, et le run a été explicitement marqué `FAIL_OR_INDETERMINATE` à cause de la condition de témoin préenregistrée.

Histogramme de la première stabilisation en calibration : h=1 pour 1 952 cas, h=2 pour 1 800 cas, h=3 pour 576 cas. Aucun h=4. Cela met en évidence la distinction entre « `E_n = E_{n+1}` est une borne vraie » et « `n` est une borne optimale ».

## Preuve élémentaire corrigée — une borne classique plus forte
Soit `P_h` la partition des états selon les mots d'observation de longueur `h`. Dans un système déterministe fini, `P_{h+1}` raffine `P_h`, et une étape sans raffinement (`P_{h+1}=P_h`) signifie que la partition est stable pour toujours. Si toutes les couleurs initiales sont identiques, `P_1=P_2` et la stabilité arrive dès `h=1`. Sinon, `P_1` contient **au moins deux classes**. À chaque raffinement strict, le nombre de classes augmente d'au moins un, sans dépasser `n`. Il peut donc y avoir au plus `n-2` étapes strictes **après** `h=1` avant une étape stable, ce qui donne `P_{n-1}=P_n`.

La borne `n-1` est atteinte par la chaîne `T(i)=i+1` pour `i<n-1`, `T(n-1)=n-1`, avec `pi(i)=0` si `i<n-1` et `pi(n-1)=1` : à chaque horizon, une nouvelle classe se sépare, et la première partition stable est `P_{n-1}`. Pour `n=4`, `T=[1,2,3,3]`, `pi=[0,0,0,1]`, la première stabilisation est h=3.

La preuve se fonde sur les mêmes principes classiques que la minimisation de Moore ; **aucune originalité revendiquée**. Le laboratoire doit désormais distinguer :
- `E_n=E_{n+1}` — **vrai mais non optimal**.
- « la borne n est atteinte » — **RÉFUTÉ**.
- `E_{n-1}=E_n` et la borne `n-1` atteignable — **démontré par raisonnement combinatoire**, exemples exacts dans les tests.

## Décision de réparation causale
Sans toucher au dataset, au générateur, à la définition d'`E_h`, aux trois algorithmes ni aux seuils de concordance :
1. Conserver l'échec du premier run dans le journal et la PR.
2. Ajouter une assertion positive de témoin `n-1` et une assertion négative pour « n optimale », sans effacer l'hypothèse initiale.
3. Relancer l'intégralité de la calibration et du réservé : toute divergence ou nouveau contre-exemple doit être archivé.

La correction n'est pas une découverte scientifique nouvelle ; elle démontre seulement que la procédure de réfutation peut signaler et corriger sa propre hypothèse.
