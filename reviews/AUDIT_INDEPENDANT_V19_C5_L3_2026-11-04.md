# Audit indépendant V19–C5, L=3 — 4 novembre 2026

## Verdict exécutif

Les résultats de classification locale sont reproduits indépendamment par propagation directe des 32 colorations possibles du cycle, sans structure DSU/parité-union :

- 3 341 diagrammes locaux canoniques ;
- 510 diagrammes à ombre propre ;
- 13 classes modulo D5, réparties 4/5/4 par codimension 1/2/3 ;
- 14 classes modulo les seules rotations C5, réparties 4/6/4 ;
- une seule classe D5 se scinde : D5-06 donne C5O-06 et C5O-09, deux classes chirales distinctes sous rotations.

Les 105 témoins de paires archivés et les 455 témoins de triples D5 ont leurs classes vérifiées, mais leurs fichiers bruts contiennent respectivement 2 et 26 lignes qui réutilisent la même paire d'états. Ces lignes ne satisfont donc pas, telles quelles, la condition de copies distinctes. Elles ont été réparées en conservant le même T et les mêmes classes, par remplacement des paires répétées par d'autres paires exactes du même système.

Un point plus important apparaît : les 455 témoins D5 ne couvrent que 455 des 560 multisets de triples orientés C5. Les 105 triples orientés manquants contiennent tous C5O-09. Le quotient D5 masque donc effectivement une partie de l'information chirale.

Ce manque est néanmoins levé par le témoin universel U42 déjà présent dans les archives. Une réénumération directe de ses 861 paires d'états confirme exactement les 680 ombres propres et les comptes des 14 classes. Chaque classe orientée apparaît au moins 10 fois avec des paires distinctes. Il en résulte qu'un même T à 42 états réalise tous les multisets de taille au plus 10 des 14 classes orientées, et en particulier les 560 triples orientés.

**Statut retenu : CALCUL EXACT reproduit pour la classification 13 D5 / 14 C5 et pour la coexistence de tous les multisets orientés de taille ≤10 dans U42.** L'optimalité des capacités par classe et l'originalité bibliographique ne sont pas auditées ici ; elles restent INDÉTERMINÉES dans le présent audit.

## 1. Définition contrôlée

La source primaire V19 (note du 25 septembre 2026, version 2) fixe :

- cycle distingué C5 orienté par T(c_i)=c_(i+1 mod 5) ;
- observation binaire ;
- horizon L=3 ;
- contraintes forcées d'opposition pour u≠v lorsque T(u)=T(v) ou {T(u),T(v)}={u,v} ;
- égalités du mauvais événement aux temps t=0,1,2.

L'ombre est la projection sur les 32 colorations binaires du cycle qui s'étendent à une coloration de tous les états et satisfont simultanément les contraintes forcées et les trois égalités de trajectoire.

Le quotient D5 est pertinent pour classifier une ombre isolée à symétrie près. Pour une coexistence dans un même opérateur T, seule la rotation C5 conserve l'orientation du cycle sans remplacer T par son inverse.

## 2. Reproduction indépendante du catalogue

Le programme indépendant construit les deux trajectoires jusqu'au temps 5 par première apparition canonique des états anonymes. Pour chaque diagramme, il construit le graphe des contraintes XOR puis essaie les 32 colorations du cycle. La propagation directe vérifie si chacune admet une extension ; aucune structure union-find/parité n'est utilisée.

Résultats reproduits :

| Quantité | Résultat |
|---|---:|
| Diagrammes canoniques | 3 341 |
| Diagrammes à ombre propre | 510 |
| Classes D5 | 13 |
| Classes C5 | 14 |
| Tailles des classes D5 (ombres) | 4 classes de taille 4 ; 5 de taille 8 ; 4 de taille 16 |
| Tailles des classes C5 (ombres) | 4 classes de taille 4 ; 6 de taille 8 ; 4 de taille 16 |

Les 14 classes orientées de la table CSV sont retrouvées exactement à partir de leurs équations affines. Le regroupement par D5 donne 12 classes de taille 1 et une classe de taille 2. La classe scindée est D5-06 ; ses deux membres sont C5O-06 et C5O-09.

**Réserve de portée :** cette reproduction certifie le catalogue fini de diagrammes locaux. Le passage de toute endofonction admissible à ces préfixes locaux dépend du lemme général de localité L+2 de la note primaire V19. Ce lemme n'est pas re-prouvé ligne par ligne dans le présent audit C5 ; la portée universelle de la classification 13/14 est donc retenue **sous cette hypothèse/ce lemme**, et non comme une nouvelle preuve indépendante de la réduction générale.

## 3. Audit des témoins de paires

Le fichier historique contient 105 multisets non ordonnés de deux classes parmi les 14 classes C5, avec répétition. Les 105 combinaisons sont présentes. Pour chaque ligne, le recalcul sur le T complet confirme les deux classes annoncées et la cohérence des contraintes forcées.

Deux lignes répètent exactement la même paire d'états :
- ligne 0 : C5O-00 / C5O-00, paire historique (0,1) répétée ; réparation (0,1) et (0,4) ;
- ligne 14 : C5O-01 / C5O-01, paire historique (0,2) répétée ; réparation (0,2) et (0,3).

Les deux réparations sont vérifiées par projection exacte sur le même T à 5 états. Le fichier réparé contient donc 105 témoins avec deux paires non ordonnées distinctes, taille maximale 17 états.

## 4. Audit des témoins de triples D5

Le fichier historique contient les 455 multisets de trois classes parmi les 13 classes D5. Les trois classes annoncées sont confirmées par recalcul direct sur le T complet ; les systèmes sont cohérents.

26 lignes réutilisent toutefois au moins une paire d'états. Chaque ligne a été réparée en recherchant, dans le même T, des paires distinctes qui réalisent exactement les mêmes classes D5. Les 26 réparations passent la vérification directe. Le fichier réparé conserve donc les 455 multisets D5 et des paires d'états distinctes, avec une taille maximale de 21 états.

### Limite du quotient D5 pour les triples orientés

Pour chacune des 455 lignes historiques, les ombres des trois paires ont aussi été reclassées modulo rotations C5, sans réflexion. On obtient 455 multisets orientés distincts sur les 560 possibles. Les 105 multisets absents contiennent tous C5O-09.

Ce n'est pas une réfutation de la coexistence D5. C'est une limite précise de ce que les certificats D5 démontrent lorsqu'on conserve l'orientation du cycle.

## 5. Vérification indépendante du témoin universel U42

Le fichier U42 archivé donne un endofonction totale de 42 états. Le contrôle indépendant a :

1. vérifié que le cycle initial est 0→1→2→3→4→0 ;
2. vérifié la cohérence du graphe de toutes les contraintes forcées par propagation bipartite directe ;
3. calculé l'ombre de chacune des 861 paires non ordonnées ;
4. classé les ombres propres par les 14 classes C5 orientées.

Décompte des 861 paires :

- 680 ombres propres ;
- 141 ombres vides ;
- 40 ombres pleines.

Les 680 ombres propres se répartissent exactement comme suit :

| Classe | Paires distinctes dans U42 |
|---|---:|
| C5O-00 | 10 |
| C5O-01 | 10 |
| C5O-02 | 10 |
| C5O-03 | 10 |
| C5O-04 | 20 |
| C5O-05 | 20 |
| C5O-06 | 10 |
| C5O-07 | 40 |
| C5O-08 | 10 |
| C5O-09 | 40 |
| C5O-10 | 100 |
| C5O-11 | 80 |
| C5O-12 | 160 |
| C5O-13 | 160 |

Ces comptes sont identiques au JSON U42 historique. Les deux classes chirales C5O-06 et C5O-09 sont toutes deux présentes (10 et 40 témoins respectivement).

Comme chaque classe possède au moins 10 paires distinctes, on peut choisir dans U42 n'importe quel multiset de 10 classes orientées ou moins, en affectant à chaque occurrence une paire distincte. En particulier, les 560 multisets de trois classes C5 orientées ont été générés et vérifiés explicitement dans le CSV U42.

## 6. Fichiers produits

- audit_v19_c5_independent_2026-11-04.py : audit autonome, sans DSU/parité-union ;
- AUDIT_V19_C5_INDEPENDENT_2026-11-04.json : compte rendu machine ;
- V19_PAIR_WITNESSES_C5O14_REPAIRED_2026-11-04.csv : 105 témoins de paires réparés ;
- V19_TRIPLE_WITNESSES_D5_13_REPAIRED_2026-11-04.csv : 455 témoins D5 réparés ;
- V19_TRIPLE_WITNESSES_C5O14_U42_2026-11-04.csv : 560 témoins de triples orientés sur U42.

Les fichiers historiques du 15 octobre ne sont pas écrasés. Les nouveaux fichiers sont des versions d'audit/reconstitution.

## 7. Portée et réserves

- **DÉMONTRÉ par argument direct dans le modèle fini** : si un même système possède au moins 10 paires distinctes de chacune des 14 classes, alors tous les multisets de taille ≤10 coexistent dans ce système.
- **CALCUL EXACT reproduit** : U42 possède effectivement ces nombres de paires ; les 560 triples orientés ont été générés et revérifiés.
- **CALCUL EXACT reproduit sous le lemme L+2** : catalogue local 3 341 → 13 classes D5 / 14 classes C5 ; la preuve générale de L+2 n'est pas re-auditée ici.
- **RÉPARATION DOCUMENTAIRE** : 2 lignes de paires et 26 lignes de triples D5 réutilisaient une paire ; les fichiers réparés conservent T et les classes annoncées.
- **À RÉEXAMINER** : les arguments d'optimalité globale des capacités propres à chaque classe ne sont pas réaudités ici.
- **INDÉTERMINÉ** : originalité bibliographique ; aucune revue humaine tierce ni formalisation Lean n'a été effectuée dans cet audit.

Aucune base SQLite n'a été modifiée et aucun statut de résultat dans la base RAVI-2 n'a été promu.


## Addendum de reproductibilité GitHub — 4 novembre 2026

Le script a été ajusté pour lire ses quatre entrées et écrire ses quatre sorties dans `research/data/v19_c5/`, séparément du code. La commande prévue depuis la racine du dépôt est :

```bash
python research/code/audit_v19_c5_independent_2026-11-04.py
```

**État exact au moment de cet addendum :** le script modifié est commité sur la branche de migration, mais les huit fichiers de données (quatre entrées historiques et quatre sorties d'audit) ne sont pas encore présents dans le dépôt. L'exécution depuis les seuls fichiers GitHub n'a donc pas été validée et échouerait tant que les quatre entrées ne sont pas ajoutées. L'exécution locale du 4 novembre sur les fichiers de l'archive C5 s'est terminée avec : 3 341 diagrammes locaux, 510 ombres propres, 13 classes D5, 14 classes C5, 105 témoins de paires, 455 témoins de triples D5, et 560 triples C5 orientés dans U42.

Le script ne modifie aucune base SQLite et n'écrit que les sorties dans le dossier de données. Aucun statut scientifique n'est promu. La réserve relative au lemme général de localité L+2 demeure inchangée.
