# V19 — Grammaire orbitale locale et théorème de petit modèle

Date : 2026-09-25

## 1. Correction méthodologique

L'hypothèse intermédiaire « les contraintes forcées forment toujours un matching » est fausse.

Contre-exemple minimal abstrait : un sommet d'un 2-cycle peut aussi avoir un frère de préimage ; il appartient alors à deux contraintes forcées cohérentes.

La structure correcte est plus générale et reste très rigide.

---

## 2. Critère exact d'une contrainte forcée

Pour une paire p={u,v}, soit H_L(p) l'ensemble des paires non diagonales visitées pendant les L premiers temps.
Pour tout L>=2 :

    |H_L(p)|=1

si et seulement si

    Tu=Tv

ou

    {Tu,Tv}={u,v}.

### DÉMONTRÉ

Si la première image est diagonale, la paire disparaît après son premier état.
Si elle reste non diagonale et H_L ne contient qu'une paire, cette image doit être la paire initiale.
La réciproque est immédiate.

En binaire, une telle paire impose c_u+c_v=1.

---

## 3. Théorème de structure du graphe forcé

Séparer deux types d'arêtes forcées :

M — fusion : Tu=Tv ;
I — invariance : {Tu,Tv}={u,v}.

Si le système de contraintes binaires forcées est cohérent :

1. chaque fibre de T contient au plus deux états ; donc les arêtes M forment un matching ;
2. les arêtes I relient soit les deux états d'un 2-cycle, soit deux points fixes ;
3. il ne peut exister plus de deux points fixes dans une composante de contraintes cohérente globale ;
4. les arêtes I forment donc elles aussi un matching ;
5. un sommet non périodique ne peut appartenir à une arête I.

### THÉORÈME — DÉMONTRÉ

Chaque composante connexe du graphe forcé est un chemin de taille au plus 4 :

    P1, P2, P3 ou P4.

Un P3/P4 est constitué d'une arête invariant centrale avec éventuellement un frère de préimage attaché à chacune de ses extrémités.

### Audit indépendant

Toutes les endofonctions étiquetées de taille n<=6 ont été testées.
Parmi 29 742 endofonctions dont les contraintes forcées sont cohérentes :

    0 contre-exemple.

Les seules formes de composantes observées sont P1,P2,P3,P4.

STATUT : DÉMONTRÉ + CALCUL EXACT indépendant.

---

## 4. Théorème de localité temporelle

Soit B un cycle périodique de longueur q>=3 et considérons une paire p={x,y} à horizon L>=2.
Les égalités du mauvais événement concernent les états

    T^t x, T^t y, 0<=t<L.

Une composante forcée qui relie deux de ces états ou l'un d'eux à B a diamètre au plus 3.

Si un état pertinent est un frère transitoire attaché à un 2-cycle, son noyau invariant complet est révélé par au plus trois itérés supplémentaires :

    z -> b -> a -> b.

Le cas d'un point fixe est plus court.

### THÉORÈME DE PETIT MODÈLE — DÉMONTRÉ

Sous cohérence des contraintes forcées, l'ombre sur B d'une paire à horizon L est entièrement déterminée par :

- le cycle B ;
- les deux préfixes de trajectoire

      x,Tx,...,T^(L+2)x
      y,Ty,...,T^(L+2)y.

Elle ne dépend d'aucune autre partie de l'endofonction.

Pour L=3, il suffit donc des temps 0,...,5.

Conséquence : pour q et L fixés, il existe un langage fini d'ombres réalisables, indépendant de |X|.

---

## 5. Grammaire orbitale

Fixer B=C5.
On énumère les deux trajectoires jusqu'au temps 5 en introduisant les nouveaux états par ordre de première apparition.

La seule règle syntaxique fondamentale est la fonctionnalité :

> si deux occurrences représentent le même état, leurs occurrences suivantes doivent aussi représenter le même état.

La transition du C5 est fixée.
Les états anonymes peuvent pointer vers un état déjà apparu ou vers un nouvel état.

Cette construction énumère toutes les formes locales possibles, à renommage des états anonymes près.

Pour C5,L=3 :

    3 341 diagrammes locaux de profondeur 5

sont examinés.

### CALCUL EXACT

Ils produisent exactement :

    13 classes D5 d'ombres propres non vides.

En ajoutant l'ombre pleine et l'ombre vide, c'est tout l'alphabet local.

Abstraitement, les partitions signées de C5 à codimension <=3 donnent 39 classes D5, dont 38 sont propres.

La dynamique élimine donc exactement :

    38 - 13 = 25

classes propres abstraitement possibles.

---

## 6. Les 13 lettres

La classification complète est jointe dans classification_13_ombres_C5_L3.csv.

Répartition :

- codimension 1 : 4/4 types abstraits sont réalisables ;
- codimension 2 : 5/16 ;
- codimension 3 : 4/18.

Au niveau des sous-espaces individuels de AG(4,2), les 13 orbites représentent :

- 20 3-flats sur 20 possibles ;
- 35 plans sur 100 ;
- 30 lignes sur 120.

Soit 85 ombres propres dynamiques sur 240 ombres propres abstraites.

---

## 7. Deux mécanismes générateurs simples

Douze des treize types possèdent un témoin particulièrement simple obtenu uniquement par les temps d'entrée dans C5.

Une trajectoire qui rejoint C5 a une trace d'ancrage de la forme :

    ... , non ancrée,
    (phase i, parité 1),
    (phase i+1, parité 0),
    (phase i+2, parité 0), ...

Le bit 1 juste avant l'entrée vient du fait que tout prédécesseur supplémentaire de c_(i+1) est forcé opposé au prédécesseur cyclique c_i.

Les paires de telles traces engendrent 12 types.

Le treizième type est obtenu par une mémoire périodique externe de période 2 :

    a -> b -> a,
    c_a != c_b.

Égaler successivement trois phases consécutives du C5 à a,b,a induit le motif de parité

    0,1,0.

C'est le type P5.

Cette décomposition 12+1 est une explication mécanistique ; la complétude repose sur le théorème de petit modèle et l'énumération finie.

---

## 8. Audit computationnel indépendant

### A — endofonctions complètes avec C5 fixé

Toutes les applications des états supplémentaires ont été énumérées, sans quotient par isomorphisme :

N=5   : 1 mapping,       2 types propres
N=6   : 6 mappings,       5 types
N=7   : 49 mappings,      8 types
N=8   : 512 mappings,    10 types
N=9   : 6 561 mappings,  12 types
N=10  : 100 000 mappings,12 types
N=11  : 1 771 561 mappings, 13 types

Aucun quatorzième type.

### B — tests aléatoires à taille supérieure

300 000 mappings aléatoires ont été testés séparément pour :

    N=12,13,15,20.

Chaque échantillon retrouve exactement les mêmes 13 types et aucun nouveau.

### C — audit du théorème de localité

Sur 99 545 paires tirées dans des systèmes aléatoires dont le graphe forcé est cohérent, pour N jusqu'à 30 :

- calcul de l'ombre avec tout T ;
- calcul en ne conservant que C5 et les deux trajectoires jusqu'au temps 5.

Résultat :

    0 divergence.

Ces audits ne remplacent pas la preuve de localité, mais en testent indépendamment l'implémentation.

---

## 9. Correction de V18 : 10 n'était pas l'alphabet dynamique

Les 39 systèmes en rupture exhaustive N=11,12 utilisent seulement 10 des 13 lettres.

Les trois lettres dynamiquement réalisables mais absentes de ces gaps sont :

1. égalité d'une paire adjacente du C5 ;
2. égalité d'une paire à distance 2 ;
3. motif alterné 0-1-0 sur trois phases consécutives.

Les deux premières sont de codimension 1 ; la troisième est le plan P5 produit naturellement par un 2-cycle externe.

Donc :

    alphabet dynamique = 13,
    alphabet observé dans les gaps N<=12 = 10.

---

## 10. Les trois lettres absentes ne sont pas simplement « inertes »

On peut former les 85 copies géométriques des 13 lettres sous D5 et étudier leurs colonnes centrées.

Un test de programmation linéaire montre que chacune des trois familles absentes des gaps peut recevoir un poids strictement positif dans une dépendance positive abstraite.

### RÉFUTÉ

Leur absence des gaps ne s'explique pas par un simple hyperplan séparateur ou par l'impossibilité de participer à un circuit positif dans la géométrie abstraite.

La contrainte restante est donc plus forte :

    COEXISTENCE DYNAMIQUE.

Des ombres individuellement réalisables ne sont pas nécessairement réalisables simultanément par un même opérateur T.

---

## 11. Nouvelle structure proposée : langage local / langage global

Cela suggère deux niveaux distincts.

### Langage local

    G_(q,L)

= ensemble fini des ombres qu'une seule paire peut produire sur un cycle C_q.

Pour q=5,L=3 :

    |G_(5,3)^proper / D5| = 13.

### Langage global de coexistence

    C_(q,L)

= ensembles ou multisets de lettres de G_(q,L) pouvant être produits simultanément par toutes les paires d'une même endofonction T.

Les gaps d'intégralité dépendent du second langage, pas seulement du premier.

C'est une séparation conceptuelle nouvelle dans notre programme :

    réalisabilité individuelle  !=  compatibilité collective.

---

## 12. Audit bibliographique

CONNU :

- les weighted pair graphs / observability graphs et leur transformation en automates finis pour les réseaux booléens ;
- les graphes signés / gain graphs ;
- les partitions étiquetées par un groupe et les lattices de Dowling.

Les travaux de Zhang et collaborateurs utilisent explicitement des pair graphs et des automates finis pour décider l'observabilité des Boolean control networks.
Dowling et Zaslavsky fournissent le langage classique pour les partitions signées et les gain graphs.

NON RETROUVÉ TEL QUEL dans l'audit ciblé :

- le théorème de localité à horizon L donnant le préfixe L+2 ;
- l'alphabet de frontière indépendant de |X| ;
- la classification exacte 13/38 pour C5,L=3 ;
- la séparation « langage local des ombres / langage global de coexistence » dans ce problème d'observabilité.

STATUT DE NOUVEAUTÉ : INDÉTERMINÉ.

---

## 13. Portes d'audit

### Porte A — preuve indépendante
PASSÉ pour :
- critère singleton ;
- structure P1-P4 du graphe forcé ;
- localité L+2.

### Porte B — calcul indépendant
PASSÉ :
- 29 742 systèmes cohérents N<=6 pour le théorème P1-P4 ;
- exhaustive C5 fixé jusqu'à N=11 ;
- tests aléatoires tailles 12,13,15,20 ;
- 99 545 comparaisons global/local sans divergence.

### Porte C — redondance
PARTIELLEMENT PASSÉ :
- gain graphs, pair graphs et partitions signées sont connus ;
- la réduction locale précise ne s'est pas révélée une conséquence immédiate des sources consultées.

### Porte D — littérature
INDÉTERMINÉ :
aucune source équivalente à la classification 13/38 n'a été retrouvée dans l'audit ciblé.

---

## 14. Prochaine cible

Ne plus chercher de nouvelles lettres.

Le problème est désormais :

> caractériser quels multisets des 13 lettres peuvent coexister pour un même T.

C'est cette grammaire globale qui doit expliquer pourquoi les gaps connus n'utilisent que 10 lettres et pourquoi certains circuits positifs abstraits ne peuvent jamais être assemblés dynamiquement.

Une piste nouvelle est de construire un graphe (ou hypergraphe) de compatibilité entre lettres à partir du partage obligatoire des mêmes fibres, des mêmes temps d'entrée et du même opérateur T.