# Omega — atelier des changements de représentation 01

**Date :** 19 novembre 2026. **État :** protocole fixé AVANT toute implémentation. Branche isolée créée depuis `main`, sans dépendre des PR empilées ou de la boucle horaire Omega.

## Question, pas de rhétorique
Une stratégie qui *modifie explicitement la représentation* d'un problème fini peut-elle résoudre davantage de tâches qu'une recherche directe et une simple diversification, **sans** produire de faux verdict ? La comparaison cruciale est contre une **méthode algorithmique classique optimisée**, pour ne pas appeler « créativité » ce qui relève seulement d'une algorithmique connue.

Ce pilote ne teste **pas** un LLM inventant spontanément des concepts ; le générateur de candidats sera une bibliothèque fermée à deux transformations classiques, choisies selon les opérateurs du problème, avec des transformations délibérément mauvaises mises en quarantaine.

## Deux domaines et transformation autorisée
1. **Contraintes binaires XOR** : entrée `n` sommets et liste `(u,v,bit)`, signifiant `color[u] XOR color[v] = bit`. Question : existe-t-il une affectation binaire ? Transformation candidate : **graphe de parité / union-find avec parité**. Inverse : lorsqu'il existe une solution, la reconstruire en bits et vérifier chaque contrainte d'origine. Pour une réponse « impossible », contrôle indépendant par parcours BFS/parité avant conclusion.
2. **Observabilité d'une dynamique finie** : `T` total sur `n` états, `pi` couleurs binaires, horizon `h`. Question : les suites de sorties de longueur `h` distinguent-elles les états ? Transformation : **suite de partitions d'équivalence**, raffinement par `(pi[x],classe_{h-1}(T[x]))`. Retour à la source : chaque classe du dernier horizon doit correspondre exactement aux mots temporels explicitement calculés. La monotonie du nombre de classes est un invariant **connu**, pas une découverte.

## Corpus construit par recette fixée, non aveugle
- `random.Random(20261119)`, sans recherche ni ajustement d'instances après observation des résultats.
- **24** graphes : `n` uniforme dans `[10,15]`, contraintes générées par arbre aléatoire puis 0 à 4 cordes non redondantes. Pour les 12 indices pairs, toutes les contraintes sont compatibles avec une affectation binaire aléatoire ; pour les 12 indices impairs, une corde (ou si nécessaire une contrainte additionnelle nouvelle) est inversée et crée une contradiction par rapport au chemin de l'arbre. Si impossibilité de générer une corde, la recette est un échec explicite.
- **24** dynamiques : `n` uniforme dans `[9,15]`, `T` une permutation circulaire canonique des états mais réétiquetée par un mélange PRNG, `pi` binaire tirée par PRNG, `h=n`. Les 12 indices pairs reçoivent des couleurs pseudo-aléatoires ; les indices impairs une séquence périodique constante (toutes les sorties égales). Ne pas ajuster a posteriori l'étiquette de vérité : la référence calcule les collisions et les deux bras peuvent s'abstenir.
- **4 cas négatifs hors hypothèses** : couleurs ternaires pour XOR, valeur de parité autre que 0/1, fonction `T` partielle, horizon négatif. Aucun bras ne doit produire de « vrai/faux » sur ces cas.
- Aucun cas n'est présenté comme un holdout indépendant : corpus synthétique issu du protocole, généré par le même programme et publiquement relisible.

## Stratégies et équité
- **A — direct** : recherche par énumération des 2^n affectations XOR, ou comparaison paire-à-paire des mots d'observation ; budget 500 opérations comptées.
- **B — diversification superficielle** : deux réordonnancements de la même recherche (états renversés/complémentés), partageant **le même total de 500 opérations**. Ne jamais compter un second parcours comme indépendance scientifique.
- **C — changement structuré** : union-find à parité pour XOR, et raffinement d'équivalences pour observabilité, chacune ≤500 unités instrumentées ; chaque verdict est contrôlé par une reconstruction ou une seconde méthode directe.
- **D — baseline algorithmique forte** : parcours BFS de contraintes XOR et mots d'observation construits par hash, ≤500 opérations instrumentées. Ce bras est indispensable : si D = C, **aucun avantage spécifique au pas de côté** n'est démontré.
- Les unités d'opération représentent des primitives **différentes** selon la représentation. Les scores d'opérations sont descriptifs, **pas une mesure précise d'un budget matériel égal**. Enregistrer aussi les durées CPU au niveau de chaque bras (indicatives sur GitHub runner). Ne jamais déclarer « gain à budget égal matériel » sur cette base.
- `ABSTAIN_BUDGET`, `ABSTAIN_UNSUPPORTED`, `VERIFIED_TRUE`, `VERIFIED_FALSE` sont distincts. Mesurer erreurs silencieuses, cas résolus, abstentions, coût instrumenté, délai et diversité des candidats.

## Contrôles adversariaux des représentations
- XOR : `n=3` et contraintes `(0,1,1),(1,2,1),(0,2,1)` sont incompatibles ; « supprimer les valeurs de parité » donnerait un faux résultat.
- Observabilité : `T=[1,0]`, `pi=[0,1]`, `h=2` a deux mots temporels distincts ; « trier les symboles des trajectoires » détruit la distinction.
- Ne jamais sélectionner les deux transformations fautives. Conserver trace de la réfutation et leurs contre-exemples exacts.

## Critères
1. **Sécurité :** 0 verdict faux sur les 48 cas, 4/4 refus de scope, 2/2 transformations fautives rejetées ; sinon FAIL.
2. **Utilité :** comparer `solved_C - solved_A`, `solved_C - solved_B` ET `solved_C - solved_D`, avec détail par domaine. D peut égaler C ; ne pas dissimuler.
3. **Épistémologie :** `TRANSFORM_CONSTRUCTED_FROM_FIXED_LIBRARY` (pas `NEW_IDEA_DISCOVERED`), `KNOWN_INVARIANT`, `PROOF_NOT_FORMAL_LEAN`; aucun résultat promu dans la bibliothèque certifiée.
4. **Généralisation :** non testée. Aucune nouvelle théorie, indépendance scientifique, créativité autonome ou amélioration des poids n'est déduite de ce banc.

## Sorties
`experiment.py` construit les cas via le seed ; `test_experiment.py` vérifie les formules et les garde-fous ; GitHub Actions archive JSON avec tous les choix et contre-exemples, résultats A/B/C/D, stats et statut. Ne modifier ni `main` ni les PR existantes. Finir avec une **seule** prochaine expérience falsifiable sur une transformation non fournie dans la bibliothèque, proposée par un modèle distinct et évaluée sur des cas nouveaux.

Il serait trompeur de déclarer la créativité d'Omega démontrée si C n'est qu'une nouvelle façon de lancer deux algorithmes connus. C'est précisément ce que la comparaison à D doit révéler.
