# OMEGA-MATH-WEB-01 — apprentissage mathématique par recherche autonome

**22 novembre 2026. Premier essai exécuté sur CPU, source brute, sans API payante, sans aide sur les notions.** PR #230 expérimentale ; aucune modification de `main`, aucune nouvelle cadence, aucune suppression.

## Question scientifique

L'échec des lectures brutes de Riemann (RAW-01/02 : 0 citation valide sur 8 sorties) provient-il d'un **défaut de contexte mathématique disponible**, et un moteur capable de **choisir lui-même une notion à rechercher** peut-il reconstruire les structures nécessaires ?

L'hypothèse reste **INDÉTERMINÉE** : « manquer de connaissances » et « manquer de capacités à manipuler ces connaissances » sont deux causes distinctes.

Les travaux publics de référence comprennent [LeanDojo](https://arxiv.org/abs/2306.15626), [CRAMF](https://arxiv.org/abs/2508.06931) et [Re²Math](https://arxiv.org/abs/2605.09012). Leurs tâches et modèles ne sont pas identiques à Omega : ils motivent un contrôle séparé de la récupération, de l'applicabilité et de la preuve, pas une amélioration supposée par analogie.

## Premier test réel, sans notion préparée

[Run GitHub 45056407124](https://github.com/Abrasax63/Omega-pub/actions/runs/45056407124). Les étapes de téléchargement du PDF, lancement d'inférence et recherche externe ont fonctionné. **Le job CI a terminé rouge** à cause d'un `KeyError: theorem_certified` dans une assertion finale après l'exécution, sur une réponse JSON invalide ; les traces et réponses ont été archivées.

- Source : guide mathématique original de Rubinstein, **page physique 6**, non utilisée dans les RAW-01/02 ; même empreinte PDF `667d88b3c375adf0466678094f452ca966aef0f4d368f6340d2bd5328b7fb706`.
- Modèle : **Qwen2.5-0.5B-Instruct Q4_K_M** sur CPU, poids épinglés au même SHA-256 `6eb923e7d26e9cea28811e1a8e852009b21242fb157b26149d3b188f3a8c8653`.
- Consigne de recherche **générique** : choisir lui-même un concept mathématique dont une explication pourrait être utile. **Aucun nom de concept dans la consigne, aucune hypothèse M/B/C, aucun graphe préparé, aucun corrigé.**
- Le modèle a choisi **« Legendre's formula »**, phrase de recherche acceptée sans modification humaine. La recherche MediaWiki a réellement renvoyé deux documents : [Legendre's formula](https://en.wikipedia.org/wiki/Legendre%27s_formula) (révision identifiée `1386811594`) et [Factorial](https://en.wikipedia.org/wiki/Factorial) (révision `1384624747`). Leurs fragments, URLs, IDs et SHA sont conservés dans le rapport.
- Deux réponses du **même modèle et sur la même page** : une directe, une avec ces extraits. Les budgets maximaux de sortie sont identiques (500 tokens), mais **le coût total des tokens d'entrée n'est pas égal**. Il s'agit d'un essai d'intégration et d'un signal exploratoire, non d'un benchmark causal validé.

## Observation du résultat

1. **Recherche autonome de la bonne famille de concepts : positive localement.** La formule de Legendre est réellement utile dans la partie élémentaire de la théorie des nombres abordée sur la page, et la source identifiée lui correspond.
2. **Reconstruction mathématique : non concluante / incorrecte sur l'exemple visible.** La sortie directe évoque à tort une dépendance « lisse » à des facteurs qui interviennent dans des parties entières. La réponse enrichie cite correctement le sujet (« Legendre's formula »), mais produit ensuite une longue répétition de `log n! = floor(n / ph)`, qui **n'est pas l'identité mathématique de Legendre**. La vraie formule est `v_p(n!) = sum_{k>=1} floor(n/p^k)` ; la notation proposée par le modèle confond la valuation, le logarithme et les puissances de p.
3. **Sorties JSON intégrales valides : 0/2**. **Citations primaires littérales validées : 0/2.** Aucun résultat vérifié comme compréhension, aucune nouvelle structure mathématique admise dans la mémoire scientifique.
4. **Défaut du workflow :** la vérification CI attendait le champ `theorem_certified` même quand le JSON était invalide. Cette erreur est **une erreur de contrôle**, distincte du comportement du modèle. Le code du workflow a été corrigé pour traiter l'absence de champ comme « non certifié ». Les tests de non-régression ont été relancés **sans rejouer les mêmes données exposées** : [run #45056587700](https://github.com/Abrasax63/Omega-pub/actions/runs/45056587700), succès technique ; le travail de modèle est volontairement désactivé sur les commits postérieurs.

Les réponses brutes, requêtes réellement choisies, sources, empreintes et durées sont dans l'artefact `omega-math-web-learning-45056407124`. Ce résultat **ne confirme pas** l'hypothèse d'une amélioration mathématique grâce à la seule recherche internet.

## Ce que doit être une véritable éducation d'Omega

**Étape 1 — Recherche ouverte par Omega :** à partir de la question brute, il identifie lui-même des lacunes conceptuelles, formule des requêtes, cherche des documents sourcés, et garde titres, versions, citations et preuves de provenance. Pas de recherche inventée en amont par l'expérimentateur.

**Étape 2 — Formation de cartes de concepts provisoires :** terme, définition dans la source, domaines et hypothèses, reformulations candidates, relations aux autres concepts, contre-exemples. **Toute extraction reste en quarantaine** tant que sa fidélité n'est pas évaluée. La citation exacte n'est ni une garantie de compréhension, ni un théorème.

**Étape 3 — Représentations contrôlées :** l'agent doit convertir les définitions en systèmes manipulables (symboles, graphes, contraintes, exemples), prédire les effets d'une modification d'hypothèse, trouver des témoins négatifs, et vérifier les invariants avec les calculs exacts ou un vérificateur formel quand disponible.

**Étape 4 — Consolidation de mémoire :** fusionner seulement des entrées réellement équivalentes, en conservant les sources historiques, les versions et les désaccords. Rechercher une définition n'est pas modifier les poids du modèle ; l'apprentissage permanent des paramètres est un autre chantier, qui nécessite des données filtrées et une évaluation séparée.

**Étape 5 — Falsification indépendante :** mêmes sources et budget comparables, réponse directe versus avec recherche versus avec mémoire structurée. Corrigé humain ou formel gelé hors du contexte du modèle, documents encore jamais vus, gains et régressions explicitement comptés.

## Décision après le pilote

**Recherche web autonome : démontrée sur une requête et deux sources.**
**Reconstruction de représentation scientifique fiable : NON DÉMONTRÉE dans ce test.**
**Compréhension de la preuve RH / nouvelle découverte : NON DÉMONTRÉE.**

Le prochain test discriminant doit conserver la recherche autonome, mais ajouter un **vérificateur local élémentaire** pour reconnaître les fausses reformulations (par exemple des identités sur entiers), puis un modèle plus capable à budget comparable. Il ne faut ni précharger les solutions ni transformer les nouvelles sources en vérités acquises.
