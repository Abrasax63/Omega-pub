# OBS-COL-07 — Pré-enregistrement avant création du solveur
Date : 2026-11-15. Branche : `experiment/obs-col07-active-automaton-synthesis-2026-11-15`.
Base : PR #90. **Engagement figé avant code et avant calcul du pilote.**

## Question falsifiable
À partir de réponses binaires de trajectoires à un oracle avec remise à zéro,
construire une **nouvelle représentation sous forme d'automate minimal candidat**,
sans transmettre au constructeur ni liste de familles, ni nombre d'états cachés.
L'algorithme doit aussi signaler un cas où les observations de longueur limitée
ne suffisent pas à établir l'exactitude hors distribution.

Ce n'est pas la découverte d'une théorie nouvelle : notre **algorithme
classique de référence** est l'apprentissage actif de langages réguliers
(Angluin, 1987, L*). Nous adaptons une table d'observation fermée/cohérente
avec contre-exemples **bornés** de longueur <=7, **pas** un véritable oracle
universel d'équivalence. Référence : DOI 10.1016/0890-5401(87)90052-6.

## Mondes gelés (générateurs cachés au constructeur, publics à l'audit)
Alphabet d'actions = {p,r}; chaque requête réinitialise l'état latent à zéro.
La réponse est un bit observable **après le dernier symbole** ; réponse au
mot vide 0. La fonction de sortie est un attribut de l'état latent atteint.

1. TOGGLE2 : états q=0,1 ; p=(q+1) mod 2 ; r=q ; sortie = 1 ssi q=1.
2. CYCLE3 : q=0,1,2 ; p=(q+1) mod 3 ; r=q ; sortie = 1 ssi q∈{1,2}.
3. CYCLE4 : q=0,1,2,3 ; p=(q+1) mod 4 ; r=q ; sortie = 1 ssi q∈{1,2}.
4. SET2 : q=0,1 ; p=1 ; r=q ; sortie = 1 ssi q=1.
5. MIX3 : q=0,1,2 ; p=(q+1) mod 3 ; r=0 ; sortie = 1 ssi q∈{1,2}.
6. DELAY9_OOD : q=0,...,8 ; p=min(q+1,8) ; r=q ; sortie = 1 ssi q=8.
Les noms et règles ne sont **jamais transmis dans une mission P1** ;
les noms peuvent apparaître uniquement dans le rapport post-hoc.

## Mesures et interventions
- Entraînement : réponses de mots de longueur <=7 ; quota maximal de
  256 requêtes distinctes, cache inclus. L'algorithme est arrêté et doit
  échouer visiblement s'il tente une requête de longueur >7.
- Algorithme : table d'observation S (préfixes), E (suffixes), fermer,
  rendre cohérente, construire des états comme classes de lignes ;
  pour réfuter une conjecture, énumérer les mots <=7 en ordre
  longueur puis lexicographique, renvoyer le premier contre-exemple.
  À aucun moment le nombre d'états du monde n'est connu de l'apprenant.
  Chaque nouveau mot interroge réellement l'oracle du simulateur.
- Variante Omega : **le véritable planificateur P1** reçoit une question
  de vérification construite à partir du mot candidat ; il doit retourner
  `verify` avant la requête. P1 n'est pas crédité d'avoir choisi la sonde,
  ni d'avoir construit l'automate.
- Baseline classique forte : le **même moteur d'apprentissage de table,
  sans P1**, sur un nouvel oracle de même monde ; comparer le modèle, le
  nombre et l'ordre des requêtes. Si identiques, **gain Omega nul**.
- Contrôle structurel indépendant (post-hoc seulement) : minimisation par
  raffinement de partition sur le graphe des états du générateur ; le
  constructeur n'a jamais accès à ce contrôle.
- Évaluation : tous les mots de longueur **8, 9 et 10** (1792 mots par
  monde), fournis après que le modèle soit gelé. Ces mots et leurs réponses
  ne servent ni au choix des suffixes ni au choix des états.
  Un échec conduit à `OUT_OF_HORIZON_WARNING`, jamais à certification.
- Quota d'environnement : six mondes x au maximum 256 requêtes
  d'apprentissage ; coût rapporté en consultations et appels P1,
  sans tarif fictif inventé.
- Tests adversariaux : contrôle du cache, exclusion des requêtes
  réservées, absence du nom de monde dans P1, contradiction exacte,
  minimisation indépendante, DELAY9_OOD, décompte budgétaire,
  déterminisme de l'ordre des requêtes et non-régression des PR existantes.

## Critères de réussite / échec
Les cinq mondes dans l'horizon doivent reconstruire respectivement
2, 3, 4, 2, 3 états minimaux et prédire tous les 1792 tests réservés.
DELAY9_OOD peut n'apprendre qu'un état constant sur les mots <=7 et
**doit être signalé par les erreurs réservées**, pas déclaré prouvé.
Les politiques Omega et classique doivent être comparées à nombre de
requêtes égal, avec même vérité terrain, et leurs égalités de décisions
rapportées comme un résultat négatif.

Ce protocole préenregistre un **test créé par nous**, donc pas d'aveuglement
scientifique externe et aucun résultat nouveau ou général à certifier.
Pas d'API payante, pas d'agent autonome exécuté, aucune modification de
`main` ni CORE, aucune fusion.
