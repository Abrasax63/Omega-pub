# OMEGA-STRAT-004 — protocole pré-enregistré : valeur stratégique d'une observation non conclusive

**Date 2026-11-11. Données scellées au commit `dff3ceeb90d2523dba0c3146f1bbf32ec5e1de01`, avant tout nouveau solveur ou résultat. Statut : CALIBRATION SYNTHÉTIQUE PUBLIQUE, NON AVEUGLE.**

## Question falsifiable
Omega et le critère « certificat » savent-ils valoriser une observation qui ne réduit PAS directement l'incertitude sur la vérité finale, mais modifie l'utilité des vérifications suivantes ? Est-ce meilleur qu'un ordre fixe ? Existe-t-il un avantage distinct contre une baseline conditionnelle forte et indépendante ?

## Corpus gelé, quatre domaines
Fichier `prism/intermediate_evidence_cases_v01.json` : 64 *enveloppes opaques* construites, 32 TRAIN et 32 TEST, huit instances par mode et par partition. Aucun identifiant ne réapparaît d'une partition à l'autre ; les **gabarits** sont néanmoins les mêmes, la collecte et les réponses sont déterministes et le corpus est conçu par l'expérience.

L'enveloppe n'est accessible qu'aux implémentations des outils de vérification et au correcteur. Les sélecteurs reçoivent **seulement les réponses aux vérifications qu'ils ont réellement payées**. Tout avantage conditionnel dépend de cette hypothèse d'observation scellée, non démontrée dans le monde réel. Les ID sont inutilisables comme caractéristique de sélection ; aucune politique ne doit lire directement la charge utile avant l'action.

Quatre familles : 
1. `algebra`, énoncé universel « pour tout k entier, m divise a*k+b » ; preuve formelle exacte et négation par k=0 ou k=1.
2. `graph`, graphe non orienté fini avec arêtes connues du solveur ; existence d'un circuit eulérien ; vérification indépendante par DFS de parcours et critère degrés/connexité.
3. `rates`, comparaison exacte de deux rationnels ; calcul `Fraction` et produits croisés indépendants.
4. `http`, permission de changer POST en GET sur redirections RFC 9110 301,302 vs 307,308 ; catalogue normatif local cité, aucune requête web pendant le rejeu.

Chaque famille comporte autant de vrais que de faux **dans TRAIN et dans TEST**. Une étiquette de route ne change donc pas la fréquence de vérité de la proposition dans le corpus ; en particulier la valeur informationnelle immédiate de `probe` pour la classification est nulle. Les huit pannes simulées sont enregistrées dans le corpus (une par famille dans TRAIN et TEST) et ne sont visibles aux stratégies qu'après l'appel correspondant.

## Vérifications tarifées
Actions disponibles (une unité et `cost_milli=20` par appel, maximum **2 actions par cas**) :
- `probe` : lecture du schéma de l'enveloppe ; renvoie `route:algebra`, `route:graph`, `route:rates` ou `route:http`, **jamais la décision finale**.
- `formal` : preuve exacte uniquement dans l'enveloppe algebra.
- `graph` : calcul constructif ou obstruction exacte du graphe.
- `fraction` : comparaison de rapports exacts.
- `source` : règle normative référencée (RFC 9110).

Les vérifications hors périmètre retournent `unknown:unsupported`, une panne de l'outil pertinent retourne `unknown:outage` ; elles sont facturées. Les vérifications conclusive fournissent `yes/no` et un certificat vérifiable ; elles terminent la politique. Les signaux `route:*` et `unknown:*` ne constituent jamais des certificats.

## Bras pré-déclarés
- **A fixe** : meilleur ordre fixe de deux actions parmi `probe,formal,graph,fraction,source`, choisi exhaustivement sur les 32 TRAIN ; ne peut pas changer selon le résultat de la première action.
- **B portefeuilles spécialistes** : meilleur ordre fixe de deux vérifications terminales parmi `formal,graph,fraction,source`, choisi uniquement sur TRAIN.
- **C Omega historique** : véritable `action_planning_two_step.optimize_policy`, `max_depth=2`, `max_cost_milli=40`, modèle fini déduit exclusivement des 32 TRAIN, `cost_milli=20`, décisions `yes/no`. Toute sortie de son calcul de risque qui n'est pas accompagnée d'un certificat réellement obtenu donne **ABSTENTION**, pas une réponse garantie.
- **D Omega orienté certificats** : extension expérimentale de la fonction objectif à un programme dynamique fini de 2 étapes maximisant `réponse certifiée – 0,02 par action`, calculée sur observations TRAIN. Les observations intermédiaires avec gain de classification nul peuvent avoir valeur stratégique positive.
- **E baseline conditionnelle forte** : énumération **indépendante**, par action initiale, puis par résultat intermédiaire, de la meilleure seconde action avec les mêmes 32 TRAIN et le même coût, sans utiliser la récurrence DP de D. Le verdict ne pourra attribuer un gain spécifiquement Omega que si D dépasse E.
- **F glouton une étape** : méthode maximisant la probabilité immédiate d'obtenir un certificat sur TRAIN, suivie d'un second contrôle fixe pré-entraîné si le premier n'a pas conclu.

Tous utilisent les mêmes preuves exactes, coûts, budgets, informations initiales et chemins de lecture. Le test de valeur stratégique porte sur le gain D/E contre A/B/F et sur l'accord D vs E ; la différence C vs D teste l'effet du changement d'objectif mais peut être nulle.

## Critères, tests négatifs et arrêt
Pour chaque bras : nombre de conclusions vérifiées, erreurs, abstentions, **coûts exacts en actions**, résultat par famille et traces intégrales. Score conventionnel :
`correct - 5*wrong - calls/50` sur les 32 tests (gain 1 pour certifié, 0 pour abstention et coût 0,02/contrôle). Jamais transformer ce score fictif en argent, temps ou capacité LLM. Calculer le nombre de cas pour lesquels **aucun** spécialiste n'a de certificat disponible (panne).

Tests nécessaires :
1. Compter 16 oui/16 non dans chaque partition, et 4 oui/4 non par famille.
2. `probe` émet les quatre routes, jamais `yes` ou `no`, et ne diminue pas l'entropie de la décision dans le train.
3. Contre-tests des quatre vérificateurs selon un second algorithme (parité/congruence, DFS/critère Euler, Fraction/produits croisés, URL RFC).
4. Une réponse finale exige le certificat du vérificateur effectivement appelé, jamais l'inférence a posteriori d'un modèle.
5. Aucune politique ne réutilise une action, ne dépasse deux appels ou ne consulte la valeur cible d'une vérification non choisie.
6. Invariance au renversement de l'ordre des tâches d'apprentissage.
7. En cas de panne, abstention ou tentative encore disponible seulement si le budget le permet.
8. L'absence de gain sur E constitue un verdict négatif **sur la spécificité d'Omega**, même en cas d'avantage substantiel sur les ordres fixes.

Arrêt après les 32 TEST ; aucune révision des baselines, objectifs, poids ou tâches suite aux résultats. Toute correction de bug de code doit être versionnée et clairement distinguée de l'adaptation de protocole. PR DRAFT empilée sur #35, sans fusion dans `main` ni mutation des mémoires/CORE.

## Sources de droit HTTP, limites
RFC 9110 : https://www.rfc-editor.org/rfc/rfc9110#section-15.4.2 ; https://www.rfc-editor.org/rfc/rfc9110#section-15.4.3 ; https://www.rfc-editor.org/rfc/rfc9110#section-15.4.8 ; https://www.rfc-editor.org/rfc/rfc9110#section-15.4.9.

Les contenus du corpus sont publics pour permettre la reproduction. Il ne s'agit pas d'un holdout secret ni d'une preuve d'intelligence générale, d'apprentissage de nouvelles méthodes, de fournisseurs de provenance indépendants ou de capacité à découvrir des stratégies en langage naturel.
