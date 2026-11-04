# Audit RAVI-2 — complexité prédictive du compteur réversible et pont vers détecteurs finis

Date : 19 octobre 2026  
Commit proposé : `COMMIT-RAVI2-2026-10-19-TIME-PREDICTIVE-21`

## Question

Tester la piste Discovery `BR-TIME-01 <-> DET-FIN-01` sans forcer une analogie. Le verrou est : peut-on obtenir une relation exacte entre horizon de distinction, mémoire prédictive et persistance de détection ?

## Résultat A — profil exact mémoire–horizon

Pour le mot binaire cyclique de `BR-TIME-01`, période `T=m^2`, `m>=5` impair, le nombre `p_m(L)` de facteurs cycliques distincts de longueur `L` vaut exactement

```
L+1                      1 <= L <= 2m
2L-2m+1                  2m < L < 3m
L+m                      3m <= L <= T-m
T                        T-m < L <= T.
```

La preuve repose sur les écarts `2m,...,2m,3m`, puis sur la réduction, pour `L>=3m`, au mot de parités de blocs `0101...0` ayant un unique défaut cyclique `00`.

Corollaire : `p_m(3m)=4m=4sqrt(T)`.

**Verdict : DÉMONTRÉ interne.**

## Résultat B — pont vers la détection à mémoire finie

Sous la loi nulle à phase initiale uniforme, toute probabilité conditionnelle positive du prochain symbole est au moins `1/T`. L'interface satisfait donc `DET-FIN-01`. Pour tout détecteur fini à alerte absorbante et risque total `<1`, les changements de phase arbitrairement tardifs deviennent conditionnellement indétectables au sens de `DET-FIN-01`, alors même que les phases non congruentes modulo `m` sont distinguables en au plus `3m` observations et que la complexité de ces blocs est exactement `4m`.

**Verdict : DÉMONTRÉ interne.**

## Expériences décisives

Budget RAVI-2 respecté : deux familles de contrôles, sans réaudit des briques certifiées.

1. **Profil exact** : 5 446 couples `(m,L)` exhaustifs pour `m` impair `5..31`, puis 489 tests adversariaux/bornes pour `m` impair `5..61`. Zéro échec.
2. **Interface DET-FIN** : 280 941 probabilités conditionnelles positives contrôlées (`m=5..21` impair), toutes `>=1/T`, et 70 440 préfixes de changements de phase vérifiés identiques avant le changement.

## Redondance interne

Aucune carte active ne donne le profil `p_m(L)`. `BR-TIME-01` donne la résolution `rho_q=Theta(sqrt(T))`, mais ne compte pas les classes de blocs futurs. `DET-FIN-01` donne la perte de sensibilité tardive pour un détecteur fini mais n'instancie pas le processus périodique à phase aléatoire. Les deux nouveaux énoncés ajoutent donc des informations autonomes et des interfaces nouvelles.

## Audit bibliographique ciblé

Le concept de **factor/subword complexity** est classique ; Morse–Hedlund et les synthèses modernes établissent les liens généraux entre périodicité et complexité. Allouche–Shallit traitent systématiquement la complexité des facteurs, et la littérature étudie aussi des mots binaires via leurs fonctions d'écarts (par ex. Gheorghiciuc, *Advances in Applied Mathematics* 39 (2007), 237–259, DOI 10.1016/j.aam.2006.04.001). Une recherche ciblée sur notre mot à écarts cycliques `2m,...,2m,3m` et la formule en quatre régimes n'a pas localisé l'énoncé exact. Cela ne prouve pas la nouveauté : **originalité exacte INDÉTERMINÉE**.

Pour la détection, la littérature classique distingue souvent probabilité de fausse alarme et ARL ; des travaux existent sur processus périodiques et changements Markoviens, mais l'audit ciblé n'a pas localisé l'énoncé exact « processus périodique à phase uniforme + détecteur déterministe fini + risque total <1 + perte uniforme des changements de phase tardifs ». **Originalité exacte INDÉTERMINÉE**.

## Portée / limites

- famille particulière de `BR-TIME-01`, `m` impair >=5 ;
- complexité prédictive finie-horizon, pas complexité algorithmique ;
- le pont de détection utilise le critère de risque total de `DET-FIN-01`, pas l'ARL ;
- aucune interprétation en flèche du temps n'est ajoutée.

## Décision RAVI-2

- `BR-TIME-FACTOR-COMPLEX-01` : **DÉMONTRÉ**, non redondant en interne, originalité externe INDÉTERMINÉE ; promotion recommandée.
- `BR-TIME-FINDET-BRIDGE-01` : **DÉMONTRÉ**, raccordement non redondant en interne, originalité externe INDÉTERMINÉE ; promotion recommandée.

Dépendances causales minimales :

- `BR-TIME-FACTOR-COMPLEX-01 DEPEND_DE BR-TIME-01` ;
- `BR-TIME-FINDET-BRIDGE-01 DEPEND_DE BR-TIME-FACTOR-COMPLEX-01` ;
- `BR-TIME-FINDET-BRIDGE-01 DEPEND_DE DET-FIN-01`.

Artefacts :

- `/Recherche/01_BRIQUES_REUTILISABLES/BR-TIME-FACTOR-COMPLEX-01_BRIQUE.md` ;
- `/Recherche/01_BRIQUES_REUTILISABLES/BR-TIME-FINDET-BRIDGE-01_BRIQUE.md` ;
- `/Recherche/04_CODE_DONNEES/RAVI2_RESEARCH/time_predictive_checks_2026-10-19.py` ;
- `/Recherche/04_CODE_DONNEES/RAVI2_RESEARCH/TIME_PREDICTIVE_CHECKS_2026-10-19.json`.