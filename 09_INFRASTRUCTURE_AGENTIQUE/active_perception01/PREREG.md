# APERCEPT01 — préenregistrement (19 novembre 2026)

## Question et limites
L'ajustement de plusieurs représentations mathématiques candidates, couplé au choix actif des observations, améliore-t-il l'identification d'une fonction finie inconnue à budget de mesures égal ? Il s'agit **d'un proxy de perception active par une interface d'observation symbolique**, et non de vision, de langage enfantin, de découverte spontanée de concepts, d'apprentissage de poids, d'AGI ou d'un prolongement prouvé des théorèmes d'observabilité d'Omega.

## Expérience figée avant écriture du moteur
- Univers : fonctions totales f:{0,...,15}->{0,1,2,3}. Un agent ne voit initialement pas la table vraie; il peut demander exactement 5 valeurs f(x) différentes par problème. Les prédictions et les requêtes sont calculées depuis les seules observations autorisées. L'oracle complet n'est utilisé qu'à la fin pour le score.
- 96 problèmes tirés par PRNG Python, graine fixe **20261119** : 12 chacun de 6 familles (constante, affine modulo 4, paire/impaire, seuil, fonction de parité XOR de bits, périodique de période 2/3/4), et 24 fonctions pseudo-aléatoires hors bibliothèque (OOD). Le générateur d'OOD évite par construction de reproduire exactement une fonction candidate; ce filtre est utilisé **uniquement lors de la constitution du jeu**, jamais par un agent.
- Bibliothèque commune B/D/E : toutes les fonctions de ces six familles, définies par énumération exhaustive des paramètres et dédoublonnées **au sein de chaque famille**. Les classes de représentations et l'algorithme de déduction sont fixés, et non appris. Une même table peut appartenir à plusieurs classes et reste présente dans ces classes.
- Politique A : mémoire table observée, prédiction sur points non vus par plus proche voisin (égalité : indice minimal), requêtes fixes 0,3,6,9,12.
- Politique B : ensemble de candidats typés filtrés par cohérence exacte, même plan fixe 0,3,6,9,12.
- Politique C : même prédicteur table/proche voisin que A, mais action de couverture : choisir le point maximisant la distance minimale aux points déjà vus (égalité : indice minimal).
- Politique D : même ensemble de candidats que B; action de **désaccord pondéré par classe** : prior égal pour chaque famille encore admissible, uniforme au sein de chaque classe. Choisir l'indice maximisant l'entropie des sorties prédites, égalités par indice minimal.
- Contrôle classique fort E : même ensemble de candidats que B/D; action par **entropie classique du version space**, candidats pondérés également (pas de pondération par famille), égalités par indice minimal.
- Les cinq politiques disposent du même budget de 5 observations par monde. Les observations sont sans bruit et exactes dans cette version; aucune représentation n'est inventée spontanément.
- Prédictions des politiques B/D/E : majorité des candidats encore compatibles (égalité : plus petite valeur). Si ensemble vide, repli sur le même plus proche voisin que A/C, statut **OUT_OF_MODEL**. Une prédiction n'est « sûre » que si tous les candidats survivants concordent; sans candidats, elle est explicitement non sûre. Pour A/C, les prédictions hors observation sont non sûres.
- Le nombre de candidats, la classe sélectionnée et les observations sont enregistrés pour la traçabilité. Les chaînes et signes de causalité ne sont pas déduits de seules associations.

## Mesures et décision
- Primaire : exactitude des 11 valeurs *non observées* après 5 requêtes, par politique, rapportée séparément in-family et OOD, et comparaisons appariées sur les mêmes 96 mondes. Les sets de 11 positions diffèrent entre politiques : c'est une **mesure transductive conditionnelle au plan d'observation**, pas une comparaison sur les mêmes positions.
- Secondaires : exactitude sur les 16 entrées après observation (inclut 5 triviales, ne pas présenter comme résultat primaire), couverture des prédictions unanimement certifiées par l'ensemble de candidats, erreurs malgré unanimité, taux de rejet hors modèle, dispersion des gains entre familles, volume des opérations (pas comparables à coûts CPU), traces par problème et empreinte SHA256.
- Vérification indépendante : comparer chaque prédiction au vrai f(x) après l'épisode, sans fournir f au choix des requêtes; tests de budget, d'absence de fuite, de reproductibilité, d'abstention OOD, et de non-régression des observations.
- Interprétation : un avantage éventuel de D vs B/C *et surtout E* n'est qu'un résultat local pour cet univers synthétique avec bibliothèque fournie. Si D = E ou D < E, l'« intelligence de représentation » supplémentaire n'apporte pas de gain démontré. Aucune généralisation à perception infantile, compréhension mathématique en langage naturel ou modèle frontière.

## Sécurité / intégration
Branche autonome issue de main; aucun appel API, aucune modification de main, aucune promotion ou certification mathématique. Les outils existants Reader12, SEM22 et Creative Prism restent intacts. Python standard library seulement. Les résultats locaux sont distincts d'une éventuelle exécution CI GitHub.
