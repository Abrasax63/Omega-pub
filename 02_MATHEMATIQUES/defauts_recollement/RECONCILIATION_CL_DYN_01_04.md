# Réconciliation documentaire — CL-DYN-01 à CL-DYN-04

**Nature :** RECONSTRUCTION DE TRAÇABILITÉ — NON ORIGINALE  
**Date :** 4 novembre 2026  
**Portée :** retrouver les énoncés historiques et leurs pièces de preuve sans fabriquer de cartes originales ni les assimiler à OBS-V8.

## 1. Verdict documentaire

Les quatre identifiants CL-DYN-01 à CL-DYN-04 n'ont pas été retrouvés comme fichiers autonomes dans l'inventaire complet de la bibliothèque (1 450 fichiers), ni comme noms de fichiers dans les deux arbres GitHub consultés. La vérification documentaire RAVI-2 du 4 novembre indique également qu'ils ne figurent pas parmi les résultats structurés de SQLite v33 / historiques examinés.

En revanche, des **sources mathématiques de contenu concordant** ont été retrouvées : rapport de spectres de défauts, notes de recollement Δ_h, scripts d'énumération et audits reproductibles. Elles permettent de retrouver une partie substantielle du travail, mais **ne prouvent pas à elles seules la correspondance historique exacte entre chaque identifiant CL-DYN et chaque fichier**.

Les contenus ci-dessous sont reconstitués à partir de l'historique de recherche du 25 septembre 2026 et confrontés aux sources retrouvées. Ce document n'est pas une carte CL-DYN originale et ne promeut aucun statut.

## 2. Énoncés historiques récupérés

### CL-DYN-01 — définition du défaut

Cadre : endofonction finie observée par une partition π.

- Matrice booléenne de transition microscopique : A.
- Matrice d'observation : C.
- Relation macro à un pas : B = CᵀAC.
- Relation macro réellement réalisable à h pas : E_h = CᵀA^hC = R̄_h.
- Défaut : Δ_h = supp(B^h) \ supp(E_h).

La multiplication est booléenne. Le point essentiel est la distinction entre les chemins permis par la composition macro B^h et ceux effectivement relevés par une trajectoire microscopique.

**Source candidate par contenu :** [rapport_spectre_defauts_iteration_1.md](sources/rapport_spectre_defauts_iteration_1.md), définitions et réduction à l'état (B^h,A^hC).  
**Reproductibilité candidate :** [quotient_spectrum_search.py](sources/quotient_spectrum_search.py) et [verify_quotient_spectrum.py](sources/verify_quotient_spectrum.py).

### CL-DYN-02 — périodicité ultime de Δ_h

L'état fini (B^h,A^hC) évolue par une récurrence déterministe sur un espace fini. Le prédicat « Δ_h non vide » est donc ultimement périodique.

Le rapport retrouvé donne une borne de prépériode et une borne de période via :
- le seuil et la cyclicité des puissances booléennes de B ;
- la profondeur des arbres du graphe fonctionnel ;
- les périodes minimales des mots d'observation sur les cycles.

**Source candidate par contenu :** [rapport_spectre_defauts_iteration_1.md](sources/rapport_spectre_defauts_iteration_1.md), sections 1 à 4.  
**Contrôle exécuté :** les scripts de spectre ont été rejoués le 4 novembre 2026 ; détails en section 5.

### CL-DYN-03 — correction du critère de finitude de τ

Formulation historique corrigée : **τ est fini si et seulement si aucun état défectueux n'appartient au cycle unique finalement atteint par l'automate déterministe pertinent.**

L'ancienne formulation « aucun cycle terminal quelconque ne porte de défaut » était trop imprécise : il faut parler du cycle effectivement atteint par l'orbite issue de l'état initial considéré, ou du cycle terminal unique de l'automate minimal lorsqu'on raisonne sur celui-ci.

Le rapport retrouvé énonce que P3 équivaut à l'absence d'état acceptant sur l'unique cycle terminal de l'automate minimal. C'est un appui de contenu à la correction, **pas la fiche CL-DYN-03 originale**.

**Source candidate par contenu :** [rapport_spectre_defauts_iteration_1.md](sources/rapport_spectre_defauts_iteration_1.md), conséquences immédiates du théorème de l'automate canonique et section 4.3.

### CL-DYN-04 — chaîne P1 ⇒ P2 ⇒ P3 et contre-exemples

Définitions récupérées dans l'historique :

- **P1 :** tout chemin macro dans Q possède un relèvement microscopique cohérent.
- **P2 :** Q^h = R̄_h pour tout h ≥ 1, autrement dit Δ_h = ∅ à tout horizon.
- **P3 :** il existe H tel que Q^h = R̄_h pour tout h ≥ H, autrement dit Δ_h = ∅ à partir d'un certain horizon.

Implications démontrées : P1 ⇒ P2 ⇒ P3. Les réciproques sont fausses.

**CE-01 — P2 n'implique pas P1.**

- T = (0,0,2), π = (0,1,1).
- Q = {(0,0),(1,0),(1,1)}.
- W₃ = {000,100,111}.
- Le mot 110 est localement permis par Q mais n'est pas réalisable : Γ₃ = {110}.
- Δ_h = ∅ pour tout h ≥ 1.

Donc P2 est vraie tandis que P1 est fausse. La minimalité |X|=3 est rapportée dans les sources retrouvées.

**Source candidate :** [DELTA_H_STRATEGIE_COUVERTURE_2026-09-29.md](sources/DELTA_H_STRATEGIE_COUVERTURE_2026-09-29.md), famille à aveuglement total des extrémités et cas K=3,q=2. Le script [delta_gluing_audit.py](sources/delta_gluing_audit.py) retrouve précisément ce témoin dans le balayage.

**CE-02 — P3 n'implique pas P2.**

- T = (0,0,0,1,2), π = (0,1,2,2,3).
- Δ₂ = {(3,1)}.
- Δ_h = ∅ pour tout h ≥ 3.

Donc P3 est vraie tandis que P2 est fausse. La minimalité |X|=5 est rapportée dans l'historique. Le script de spectre retrouvé produit le spectre D={2} pour ce témoin.

**Source candidate :** [rapport_spectre_defauts_iteration_1.md](sources/rapport_spectre_defauts_iteration_1.md), témoin du seul spectre fini non vide à cinq états et audit exhaustif.

Les noms historiques CE-01 et CE-02 sont conservés ici comme étiquettes de régression rapportées ; le fichier de test original portant ces noms n'a pas été retrouvé. Les instances elles-mêmes ont été recalculées séparément le 4 novembre.

## 3. Sources retrouvées — correspondance non certifiée

| Identifiant | Source(s) candidates | Ce qui est effectivement étayé | Ce qui manque |
|---|---|---|---|
| CL-DYN-01 | rapport de spectres ; scripts de spectre | définitions B, E_h, Δ_h et calcul exact | carte originale et liaison d'évidence |
| CL-DYN-02 | rapport de spectres ; scripts de spectre | automate fini (B^h,A^hC), périodicité ultime | carte originale et certificat historique associé |
| CL-DYN-03 | rapport de spectres | critère P3 sur l'unique cycle terminal | texte original corrigé et preuve/certificat initial |
| CL-DYN-04 | rapport de spectres ; notes stratégie et recollement ; audits | chaîne de propriétés et témoins de non-réciproque | fiche originale, paquet CE-01/CE-02 initial et décompte historique non ambigu |

Les notes de recollement du 29 septembre développent aussi des obstructions internes qui peuvent subsister alors que tous les Δ_h sont vides. Elles approfondissent la séparation entre défaut d'extrémités et défaut de recollement interne ; elles ne doivent pas être confondues avec les cartes originales CL-DYN.

## 4. Vérifications exécutées le 4 novembre 2026

### Spectres de défauts — énumération canonique à N=5

Commande exécutée sur le script source retrouvé : `quotient_spectrum_search.py 5 --show 25`.

- 162 500 couples (T,π) parcourus : toutes les endofonctions à 5 états et toutes les partitions canoniques de [5].
- 19 spectres distincts.
- 54 380 spectres vides.
- 240 spectres finis non vides.
- 107 880 spectres infinis.
- Le seul spectre fini non vide observé est D={2}, avec 240 présentations.

### Contrôle indépendant

`verify_quotient_spectrum.py` s'est terminé avec :

- 13 984 comparaisons directes ;
- 13 983 contrôles de renommage ;
- 4 001 réalisations universelles ;
- horizons de contrôle 80 et 150 selon le test.

### Recollement interne — énumération binaire/ternaire

`delta_gluing_audit.py` s'est terminé sans erreur. Il retrouve notamment :

- N=3,q=2 : 162 présentations, 12 cas avec Δ_h tous vides mais Γ₃ non vide ;
- N=5,q=2 : 93 750 présentations, 12 160 cas avec Δ_h tous vides mais Γ₃ non vide.

Ces nombres portent sur le défaut interne P2 sans P1, et non sur le défaut temporel P3 sans P2.

Le contrôle indépendant `delta_gluing_crosscheck.py` a réussi les domaines (2,2), (3,2), (4,2) et (3,3), puis a dépassé le temps disponible sur (4,3). Il est donc **partiel**, pas intégralement validé.

## 5. Écart de comptage à ne pas masquer

Un résumé historique de conversation mentionne **360** cas P3 sans P2 à N=5. Le rapport et le script d'énumération canonique retrouvés donnent **240** spectres finis non vides à N=5, et le rejeu du script confirme 240.

Ces nombres ne sont pas conciliés à ce stade. Ils peuvent dépendre d'une version de code, d'un univers d'énumération ou d'une définition antérieure des propriétés ; aucune explication n'est démontrée. **Le nombre 360 est donc mis en quarantaine ; le nombre 240 est le seul confirmé par le script actuellement retrouvé et rejoué.**

## 6. Séparation stricte avec OBS-V8

OBS-V8-FACT-INF compte les colorations génératrices à horizon infini par une factorisation en facteurs de fibres et de cycles primitifs. Les CL-DYN portent sur les défauts de composition des relations macro à horizon fini, les chemins fantômes et leur périodicité.

Une proximité de domaine ne constitue pas une identité d'énoncé, une dépendance causale ou une équivalence de cartes.

**Correspondance CL-DYN ↔ OBS-V8 : INDÉTERMINÉE.** Aucune fusion, aucun renommage et aucune dépendance n'est créée.

## 7. Décision RAVI-2

- Les cartes CL-DYN originales ne sont pas déclarées retrouvées.
- Les sources candidates et les scripts sont restaurés dans un dossier séparé pour faciliter l'audit.
- Les anciens statuts CORE/CERTIFIED rapportés dans l'historique ne sont pas réactivés par cette reconstruction.
- Aucune promotion scientifique, aucune relation DEPEND_DE et aucune écriture dans SQLite ne sont effectuées.
- Prochaine étape avant toute publication : retrouver les fiches primaires ou leurs certificats de commit, puis auditer la différence 360/240 et rejouer le contrôle indépendant complet.
