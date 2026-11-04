# V19 — Multiplicité réelle, capacités et premier ordre d'obstruction

Date : 15 octobre 2026

## 1. Correction adversariale

Le cycle précédent employait le mot « multiset » alors que certains CSV autorisaient, pour une classe répétée, de réutiliser exactement la même paire d'états. Cela certifiait une famille indexée avec répétition, mais pas une multiplicité portée par des **paires d'états distinctes**.

La notion correcte utilisée ici est donc : une occurrence = une paire non ordonnée `{x,y}` distincte comme objet combinatoire. Deux occurrences peuvent partager un état, mais elles ne peuvent pas être la même paire.

Audit des anciens certificats :
- 105 lignes de compatibilité orientée par paires : 2 lignes réutilisaient la même paire ; dans les mêmes endofonctions, des secondes paires distinctes de la même classe existent. Correction : **105/105 avec deux paires distinctes**.
- 455 lignes ternaires D5 : 26 lignes contenaient au moins une paire répétée ; dans les mêmes endofonctions, une affectation de **trois paires distinctes** existe pour les trois classes demandées. Correction : **455/455 avec trois paires distinctes**.

Aucun résultat n'est réfuté, mais les certificats sont renforcés et les cartes doivent passer en v2 pour expliciter cette condition.

## 2. Six classes orientées ancrées

On travaille avec le cycle orienté `C5`, horizon `L=3`, contraintes forcées binaires cohérentes et les 14 classes `C5O-00..13` de `OBS-V19-C5-ORIENTED14`.

La réinspection exacte des 3 341 diagrammes locaux montre que six classes ne possèdent que des témoins entrant dans le bassin de `C5`, avec les formes profondeur–phase suivantes :

- `C5O-02` : profondeurs `0/1`, décalage de phase `±2` ;
- `C5O-03` : profondeurs `0/1`, décalage `±1` ;
- `C5O-05` : profondeurs `2/2`, décalage `±2` ;
- `C5O-07` : profondeur `2` contre profondeur `0` ou `1`, décalage `±2` ;
- `C5O-11` : profondeurs `3/3`, décalage `±2` ;
- `C5O-13` : profondeur `3` contre profondeur `0`, `1` ou `2`, décalage `±2`.

Cette classification des formes est un **CALCUL EXACT** sur l'alphabet local déjà certifié ; elle sert de lemme fini à la preuve de capacité ci-dessous.

## 3. Théorème de capacité

### Énoncé

Dans toute endofonction finie cohérente possédant le cycle orienté `C5`, le nombre `ν_a(T)` de paires d'états distinctes produisant une classe orientée ancrée vérifie :

- `ν_02 <= 10` ;
- `ν_03 <= 10` ;
- `ν_05 <= 20` ;
- `ν_07 <= 40` ;
- `ν_11 <= 80` ;
- `ν_13 <= 160`.

Les six bornes sont atteintes simultanément.

### Preuve

La cohérence binaire impose `|T^{-1}(y)|<=2`. Sur `C5`, chaque sommet cyclique possède déjà son prédécesseur cyclique ; il reste donc au plus un prédécesseur extérieur de profondeur 1 par phase.

En notant `n_h(j)` le nombre d'états de profondeur `h` dans l'isochrone `theta=j`, on obtient pour chaque phase :

`n_0(j)=1`, `n_1(j)<=1`, `n_2(j)<=2`, `n_3(j)<=4`.

Les formes profondeur–phase exactes donnent alors :

- classe 02 ou 03 : chaque état de profondeur 1 a exactement deux phases cycliques candidates de la classe considérée, donc `<=5*2=10` ;
- classe 05 : couples de profondeur 2 sur deux phases à distance `±2`, soit cinq paires de phases, chacune de capacité `2*2`, donc `<=20` ;
- classe 07 : chaque état de profondeur 2 a au plus quatre partenaires admissibles aux profondeurs 0/1 sur les deux phases `±2`, donc `<=10*4=40` ;
- classe 11 : cinq paires de phases à distance `±2`, chacune de capacité `4*4`, donc `<=80` ;
- classe 13 : chaque état de profondeur 3 a, sur chacune des deux phases `±2`, au plus `1+1+2=4` partenaires aux profondeurs 0/1/2, donc `<=20*8=160`.

Le bassin binaire maximal de profondeur 3 contient exactement 5 états cycliques, 5 états de profondeur 1, 10 de profondeur 2 et 20 de profondeur 3. Le calcul exact des paires dans ce bassin donne précisément :

`ν_02=10, ν_03=10, ν_05=20, ν_07=40, ν_11=80, ν_13=160`.

Les bornes sont donc optimales.

**STATUT : DÉMONTRÉ**, avec dépendance à la classification locale exacte orientée et à la structure forcée cohérente.

## 4. Témoin universel U42

Ajouter au bassin maximal précédent un 2-cycle disjoint. On obtient une endofonction cohérente à 42 états `U42`.

Le comptage exact des paires distinctes de chacune des 14 classes orientées est :

`[10,10,10,10,20,20,10,40,10,40,100,80,160,160]`.

Donc chaque classe possède au moins 10 paires distinctes dans **un même** opérateur.

Conséquence immédiate : tout multiset de classes orientées de cardinal `k<=10` est réalisable simultanément avec `k` paires d'états distinctes : pour chaque multiplicité demandée, choisir le nombre correspondant de paires de cette classe dans `U42`.

**STATUT : CALCUL EXACT** pour le vecteur de multiplicité et certificat constructif explicite.

## 5. Premier ordre d'obstruction

Définir `k_*` comme le plus petit entier `k` pour lequel il existe un multiset de `k` classes orientées qui ne peut pas être réalisé par `k` paires d'états distinctes dans une même endofonction cohérente contenant le même `C5` orienté.

- Par `U42`, tous les multisets de taille `k<=10` sont réalisables.
- Par le théorème de capacité, `11` copies de `C5O-02` sont impossibles, puisque `ν_02<=10` dans tout système.

Donc :

`k_* = 11`.

C'est la première obstruction de coexistence trouvée dans V19 qui ne provient ni d'une incompatibilité pairwise, ni d'un quotient de symétrie, mais d'une **capacité dynamique finie de multiplicité**.

**STATUT : DÉMONTRÉ.**

## 6. Ce que cela change

La piste « chercher une petite hyperarête interdite entre classes » n'est pas le mécanisme principal aux faibles ordres :
- ordre 2 : complet ;
- ordre 3 : complet ;
- ordre 4 : complet ;
- en fait tous les ordres `<=10` : complets au niveau des labels de classes orientées.

La première obstruction est quantitative et apparaît à l'ordre 11 par saturation d'un bassin ancré.

Cela rapproche directement le problème des circuits positifs avec coefficients : les coefficients/multiplicités ne sont plus un détail, ils sont une variable structurelle essentielle.

## 7. Limites

- Le théorème porte sur `C5`, observation binaire, `L=3`, cohérence des contraintes forcées.
- Une occurrence signifie une paire d'états distincte comme objet ; différentes paires peuvent partager un état.
- `k_*=11` concerne les **labels de classes orientées**. Le complexe des copies géométriques exactes peut avoir des obstructions plus précoces.
- Les bornes ci-dessus ne prétendent pas classifier toutes les capacités des 14 classes ; elles suffisent à établir l'ordre critique.
- Originalité bibliographique : **INDÉTERMINÉE**. Aucun audit externe nouveau n'est effectué dans ce commit.

## 8. Artefacts

- Code : `/Recherche/04_CODE_DONNEES/v19_multiplicity_capacity.py`
- Paires distinctes : `/Recherche/04_CODE_DONNEES/V19_PAIR_WITNESSES_C5O14_DISTINCT_V2_2026-10-15.csv`
- Triples D5 distincts : `/Recherche/04_CODE_DONNEES/V19_TRIPLE_WITNESSES_D5_13_DISTINCT_V2_2026-10-15.csv`
- Témoin universel : `/Recherche/04_CODE_DONNEES/V19_UNIVERSAL10_U42_2026-10-15.json`
- Capacités : `/Recherche/04_CODE_DONNEES/V19_CAPACITY_BOUNDS_C5O14_2026-10-15.csv`