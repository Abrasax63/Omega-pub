# Réconciliation des revues et audits historiques — lot 05 (5 fichiers, 9 novembre 2026)

**Dépôt :** `Abrasax63/Omega-pub`  
**Branche source :** `migration/ravi2-ccs-public-2026-11-04`  
**Branche de publication :** `maintenance/reconciliation-bibliotheque-2026-11-05`  
**Périmètre :** quatre rapports V19 de mauvais objets/capacité/coexistence et vérification technique SQLite v33.  
**Nature :** réconciliation documentaire. Aucun script, calcul, requête SQLite ou test n'a été exécuté dans ce lot.

## 1. Fichiers examinés et empreintes Git source

| Fichier | SHA Git source |
|---|---|
| `V19_BADOBJECT_FIBER2_2026-10-15.md` | `d23dca3e6cd6ca5082580e17e1654d1149461f01` |
| `V19_BADOBJECT_N11_2026-10-15.md` | `f142853ff96e2f9138d6eca377887f918b5e0f04` |
| `V19_MULTIPLICITE_CAPACITE_2026-10-15.md` | `10fd9011265018f4b96cd50771f608daba4542a8` |
| `V19_REGION_COEXISTENCE_2026-10-15.md` | `ecf92218c1e700e0abd9be6e604fb839b3bc61dd` |
| `VERIFICATION_SQLITE_V33_2026-11-04.md` | `a486342220dd979b71104453d578397cb4e94f30` |

## 2. V19 — de la paire au mauvais objet

### V19_BADOBJECT_N11

Ce rapport reconstruit les mauvais objets de cinq mappings historiques N=11 à partir des contraintes affines augmentées. Il rapporte les comptes exacts par mapping : 48, 48, 48, 47 et 50 paires propres ; 42, 36, 36, 37 et 38 mauvais objets distincts ; fibres de taille 1 ou 2.

Il rapporte également, dans ces cinq systèmes :
- impossibilité d'un 1-cover ;
- packing disjoint maximal de valeur 7 ;
- 2-cover exact par 16 mauvais objets ;
- circuit positif primitif à coefficients unitaires, rang 15 et nullité 1.

Mais le rapport de ce 15 octobre conclut explicitement que la borne universelle fibre≤2 est encore INDÉTERMINÉE : les cinq systèmes N=11 et les tests finis soutiennent la conjecture sans la prouver.

### V19_BADOBJECT_FIBER2

Le rapport ultérieur propose une preuve générale, dans le domaine C5, binaire, L=3, contraintes forcées cohérentes, pour les mauvais objets propres non vides :
`#{p : B_p=B} ≤ 2`.

La preuve combine :
- un lemme de récupération du générateur de Krylov ;
- le quotient forcé invariant ;
- l'égalité des signatures affines augmentées ;
- la classification des composantes forcées P1–P4 ;
- l'analyse des quatre coins de la fibre paire-image.

Le rapport rapporte un contrôle exhaustif sur 4 820 systèmes cohérents de N=5 à 9, 148 120 paires propres et 132 990 mauvais objets, sans fibre supérieure à 2, plus des contrôles supplémentaires. Il conclut DÉMONTRÉ dans le domaine restreint déclaré.

**Réserve de statut à résoudre :** la preuve utilise explicitement `OBS-V19-FORCED-P4`. Un audit du 4 novembre (traité au lot 02) affirme que la classification P1–P4 et le lemme L+2 sont démontrés, tandis que l'état de recherche ultérieur conserve P4 comme verrou à contrôler. Le présent rapport ne peut pas décider si le point P4 est réellement clos. La borne fibre≤2 doit donc rester attachée à ses hypothèses et à cette dépendance, sans promouvoir le statut courant sur la seule base du texte historique.

Le théorème exclut expressément les mauvais objets vides, les ombres pleines, les horizons autres que L=3 et les cycles autres que C5 sans preuve correspondante. La capacité exacte en mauvais objets `μ_T(ω)` reste distincte de la capacité en paires `ν_T(ω)`.

## 3. V19 — capacité des classes orientées

### V19_MULTIPLICITE_CAPACITE

Le rapport corrige une faiblesse des certificats antérieurs : certaines lignes de paires et de triples réutilisaient exactement la même paire d'états, alors que la multiplicité exige des paires distinctes comme objets combinatoires.

Il rapporte les corrections :
- 105/105 paires orientées avec deux paires distinctes ;
- 455/455 triples D5 avec trois paires distinctes.

Il présente ensuite six capacités ancrées et leurs bornes (10, 10, 20, 40, 80, 160), atteintes simultanément, puis un témoin U42 de 42 états dont le vecteur de capacités assure au moins dix paires distinctes pour chacune des 14 classes orientées. Il en déduit le premier ordre d'obstruction au niveau des labels de classes : k*=11.

La portée est C5 orienté, observation binaire, L=3 et contraintes forcées cohérentes. Le résultat ne classe pas toutes les capacités possibles et l'originalité bibliographique reste INDÉTERMINÉE.

### V19_REGION_COEXISTENCE

Ce rapport réfute le modèle de packing exclusif des états comme modèle exact des occurrences de paires : un même état peut appartenir à plusieurs paires distinctes. Pour un T fixé, les paires sont partitionnées par ombre et toute sélection de multiplicité dans chaque fibre est réalisable ; la matrice d'incidence possède un seul 1 par colonne et est totalement unimodulaire.

Il rapporte ensuite une région exacte de coexistence géométrique, sous les capacités individuelles et une famille cofinale construite, et distingue :
- premier ordre d'obstruction géométrique k_geo*=3, pour les ombres géométriques exactes ;
- premier ordre d'obstruction au niveau des labels orientés k_classe*=11.

La différence est essentielle : le quotient par 14 labels agrège des ombres géométriques et peut cacher une obstruction plus précoce. Le rapport identifie ensuite le niveau à examiner : paire → mauvais objet → ombre, car plusieurs paires peuvent produire le même mauvais objet.

## 4. Cohérence entre les niveaux V19

Les quatre rapports ne doivent pas être amalgamés en une unique affirmation :
1. N11 : calcul exact sur cinq mappings et circuits/2-covers reconstruits ; borne universelle fibre≤2 encore ouverte à cette date.
2. Fibre≤2 : preuve générale ultérieure revendiquée sous C5/L=3 et contraintes forcées cohérentes, dépendant de P4 et du lemme de Krylov.
3. Capacités orientées : bornes sur les paires distinctes et ordre 11 au niveau des classes.
4. Région géométrique : distinction entre capacité des ombres exactes et capacité agrégée des classes ; premier ordre 3 au niveau géométrique contre 11 au niveau des labels.

Ces résultats utilisent des objets de comptage différents. En particulier, une capacité de paires ne donne pas automatiquement une capacité de mauvais objets ni une caractérisation des circuits positifs.

## 5. Vérification technique de SQLite v33

`VERIFICATION_SQLITE_V33` rapporte un contrôle en lecture seule du binaire de 819 200 octets, SHA-256 `ef3e9a0de51a44b30599f73f027829751a2eb144e4468175c0f290b5e0159bf4`.

Contrôles consignés :
- `PRAGMA integrity_check = ok` ;
- zéro violation de clé étrangère ;
- zéro référence `result_sources` vers un résultat ou une source absente ;
- zéro relation avec extrémité de résultat absente.

Comptages consignés :
- 89 résultats, 85 admissibles ;
- 105 sources, 177 relations `result_sources` ;
- 217 evidence, 83 relations dont 49 `DEPEND_DE` ;
- 78 audits, 62 tests enregistrés PASS ;
- 7 nœuds mémoire, 8 liens et 7 éléments de snapshot.

Les 62 tests sont enregistrés PASS, mais n'ont pas été rejoués lors de ce contrôle. La base binaire n'était pas présente dans le dépôt GitHub au snapshot du rapport ; son empreinte n'est pas une sauvegarde. Le contrôle technique ne certifie pas les 85 résultats mathématiques, ni l'exhaustivité de leurs preuves.

## 6. Décisions de réconciliation

- Conserver la distinction paires / mauvais objets / ombres géométriques / labels de classes.
- Conserver les versions corrigées des témoins distinctes des versions historiques ; pas d'écrasement silencieux.
- Maintenir la dépendance P4/L+2 explicitement ouverte à l'audit adversarial tant que la divergence de statut n'est pas résolue.
- Ne pas étendre fibre≤2 hors de C5, L=3, mauvais objets propres non vides et hypothèses de cohérence.
- Ne pas confondre k_geo*=3 avec k_classe*=11.
- Traiter SQLite v33 comme un snapshot technique historiquement contrôlé ; aucun accès ni changement de base dans cette opération.
- Ne modifier ni `main`, ni les statuts, ni les relations SQLite.

## 7. Limites de ce lot

Les preuves et contrôles numériques sont ceux rapportés par les fichiers historiques. Aucun script, calcul exact, vérification SQLite, test de régression ou preuve Lean n'a été exécuté dans ce lot. Aucune certification scientifique n'est renouvelée.

**Verdict :** cinq derniers fichiers réconciliés documentairement. Les niveaux combinatoires V19 et leurs dépendances sont séparés ; la divergence P4 reste visible et non arbitrée.
