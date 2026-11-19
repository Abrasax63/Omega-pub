# OMEGA-READER20 — préenregistrement : sélection automatique d'un vérificateur exact

Date : 2026-11-19. Branchée sur Reader19 (#188), `main` inchangée. Ce protocole est établi **avant de coder le routeur et avant de générer les nouveaux cas**. Aucune API, aucun ajustement neuronal.

## Question décisive
Un routeur sans LLM, sans identifiant manuel de vérificateur et sans connaissance du verdict peut-il lire **un énoncé source contrôlé**, en extraire les hypothèses et limites requises, choisir parmi trois vérificateurs exacts et produire une décision correcte ou s'abstenir ? Le raccord échoue s'il se trompe de vérificateur, accepte un cas hors scope, ou certifie une phrase dont il n'a pas parsé les hypothèses.

Ce test a une **grammaire explicitement restreinte**, pas du français scientifique libre. Il démontrerait au plus un routage formel sur domaines finis, pas l'intelligence scientifique autonome.

## Sources, protocole et données séparées
Les cas seront construits **après ce commit** de manière reproductible avec `random.Random(seed=20261119)`. Trois familles (aucun nom de solver dans les contrats) :
- Arithmétique : `Hypothèses: a=<entier>; b=<entier>; domaine=N[0,999]` ; `Énoncé: a * b = c` ; `Limites: entier naturel borné`.
- Congruences de dynamiques finies : `Hypothèses: T=[t0,...,tn-1]; domaine={0,...,n-1}` ; `Énoncé: nombre_congruences(T) = c` ; `Limites: 2<=n<=6; partitions finies`.
- Graphes de contraintes binaires : `Hypothèses: n=<entier>; differences=[(u,v),...]` ; `Énoncé: deux_colorable = oui|non` ; `Limites: 2<=n<=12; valeurs binaires`.

Chaque bloc contient *exactement* les trois champs, dans l'ordre, avec une source Markdown épinglée par blob Git exact. Un moteur doit refuser les titres, citations, hypothèses ou limites manquants ou incohérents, toute instruction qui simule une consigne, tout champ supplémentaire, ainsi que toute famille non reconnue. Aucune auto-promotion vers des théorèmes généraux.

## Échantillon figé par règle avant génération
- 8 nouvelles instances par famille, soit **24 cas** (4 assertions vraies et 4 fausses par famille) ; paramètres choisis par PRNG avant calcul du score, pas par sélection selon les résultats du routeur.
- 8 cas négatifs hors grammaire ou limites (2 sans hypothèses, 2 sans limites, 2 hors bornes, 1 expression de conjecture hors famille, 1 texte injectant une fausse instruction).
- Limites de temps/ressources : n <=6 pour congruences, n <=12 pour graphes, entiers <=999, max 32 lignes de contrat, max 4000 octets/contrat, 32 contrats maximum ; abandon sûr si dépassé.
- Le modèle de décision doit être unique par famille **par correspondance syntaxique exacte** des énoncés. Aucune valeur gold ni l'identifiant de famille n'est passée au routeur. Les trois fonctions de preuve restent séparées du parseur.
- Le corpus synthétique Markdown entier est créé et épinglé à un SHA de Git **avant** l'exécution de l'évaluateur ; son corrigé est calculé à part après prédictions figées et comparé sans optimisation post-hoc.

## Comparaisons et falsification
Le routeur doit produire 24/24 sélections de la famille attendue ; 24/24 verdicts exacts sur les propositions ; 8/8 abstentions sur négatifs ; zéro erreur silencieuse ; références exactes aux lignes du Markdown et au Git blob ; **zéro promotion** de provenance seule. Le score secondaire s'obtient par deux implémentations mathématiques différentes :
1. Congruences : `Reader19.partitions_of_mask + congruent` sans recoder la logique de référence. Le contrôle indépendant utilise une énumération par **mots de croissance restreinte** et tests directs d'image.
2. Graphes : BFS de coloration vs **force brute** de 2^n affectations.
3. Produit : multiplication native Python vs produit par additions répétées (intérêts strictement limités aux valeurs bornées).

Les comparaisons doivent inclure un témoin qui affecte un solver fixe à tous les problèmes (attendu 8/24 routes exactes au plus). Le score de route est indépendant de la preuve; l'absence de règle applicable est une abstention, et non un résultat négatif.

## Déclenchement et portée
Exécution entièrement sur GitHub Actions CPU, 0 clé/0 inférence de LLM. Test de bout-en-bout : fichier Markdown → audit de provenance → parsing d'hypothèses/limites → routage → calcul exact → contrôle de référence indépendant → registre de verdicts. En sortie, rapport JSON avec ID, indices de lignes, hypothèses, limites, noms des familles de contrôleurs *sélectionnés automatiquement*, statut scientifique conditionnel, temps/décisions et échecs.

**Ce que ce protocole ne valide pas :** compréhension de textes mathématiques libres, généralité des théorèmes, nouveau résultat scientifique, modèle frontière, certitude formelle Lean, annotation indépendante humaine ou autonomie auto-améliorante. Même 32/32 résultats réussis ne démontreront qu'une capacité technique étroite. Ne pas modifier les poids ni `main`, ne pas fusionner.
