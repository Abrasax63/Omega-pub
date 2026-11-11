# OMEGA-CERT-001 — pré-enregistrement de l'objectif « certificat vérifiable »

**11 novembre 2026. Corpus et pannes GELÉS au commit `c395e0e065f345a0d083e383c13e6fac8077ad60`, avant l'implémentation et les premiers résultats de la nouvelle expérience.**

## Question
Remplacer l'optimisation du seul risque de décision hypothétique par une optimisation de l'obtention **effective d'une réponse justifiée** améliore-t-il la couverture à budget identique ? Comparer Omega original, le nouveau critère certificat, et une référence simple robuste, optimisée sur le même apprentissage.

**Statut CALIBRATION PUBLIQUE CONSTRUITE.** Les tâches sont nouvelles par leurs paramètres et toutes disjointes de STRAT-002, mais réutilisent les familles de procédures. Ce ne sont pas des questions indépendantes conçues en aveugle ni des sorties de modèles. Leurs méthodes sont des programmes déterministes.

## Données figées
`prism/certification_cases_v01.json` contient **48 cas explicitement fixés** : 24 train et 24 test (6 par domaine pour chaque partition). Sept sous-types (mod, euler, map, zip, ratio, simpson, header), avec 3+3 cas par sous-type sauf `header` 6+6. Quatorze échecs de méthode sont simulés et déclarés dans l'instantané ; **le planificateur et les règles concurrentes ne peuvent pas voir la panne du cas cible avant d'appeler la méthode**. La fonction de lecture peut la connaître pour simuler un outil, pas la politique.

Les paramètres sont différents de STRAT-002, sauf la *structure* générale des types. Aucun cas précédent ni sa réponse ne doivent être consultés pour apprendre les nouveaux réglages.

Sous-type documentaire inédit `header` : selon RFC 9110 §13.1.3, une condition `If-Modified-Since` n'est éligible à son évaluation standard que pour GET/HEAD, si elle est présente, et en l'absence d'un `If-None-Match`. Les assertions sont une table locale de règle normative, pas des requêtes réseau et pas des attestations cryptographiques. Source officielle : https://www.rfc-editor.org/rfc/rfc9110#section-13.1.3.

## Quatre procédures réellement exécutées
`formal` (règles et preuves symboliques), `compute` (exécution exacte, recherche bornée lorsque approprié), `refute` (contre-exemple correct, absence de contre-exemple ne prouve jamais le vrai), `source` (règle documentaire identifiée). Réutiliser autant que possible `strategic_methods_executable.py` et créer un adaptateur de nouveau corpus ; ne pas dupliquer le planificateur général ni sa mémoire. Toute méthode retourne `yes/no/unknown` avec un certificat ou motif textuel. Une réponse conclusive doit être vérifiée par un second calcul lorsque mathématiquement possible. Le résultat `unknown` peut être typé `outage / no_witness / not_applicable`, **d'après le message réellement produit**, sans accéder au corrigé.

## Objectif gelé
- Gain terminal : **+1 pour une réponse munie d'un certificat vérifié**, 0 pour abstention ; une affirmation sans certificat ne reçoit jamais le gain.
- Garde-fou : **-5 pour erreur de certificat détectée par l'oracle indépendant**, uniquement lors de la notation, jamais en utilisant les réponses de test à l'entraînement.
- Coût : **0,05** par méthode essayée, y compris en panne. Les stratégies peuvent s'arrêter sans dépense, ne peuvent jamais dépasser **deux** essais par tâche. Le score affiché est **`certified_correct - 5*wrong - 0.05*calls`** ; publier aussi les trois composantes séparées, car cette pondération est une convention expérimentale et non un coût réel.
- Le nouveau sélecteur C utilise un programme dynamique fini sur les **seuls retours de méthodes des cas d'entraînement** (observations yes/no/unknown:reason) pour maximiser le gain empirique attendu moins le coût ; aucune lecture du corrigé n'est permise pour définir la politique.
- Une réponse `yes/no` termine l'essai avec un certificat. `unknown` ouvre éventuellement une autre méthode, si son gain estimé est positif. Toute branche absente de la table d'apprentissage est traitée par **repli sur le meilleur second contrôle selon le seul apprentissage**, sans accès aux résultats de test. Départager par lexicographie.
- L'ancienne version de `optimize_policy` est rejouée avec les mêmes 24 cas d'apprentissage, avec deux hypothèses sentinelles `unknown`. Une réponse sans certificat issue de son risque postérieur reste une abstention.

## Baselines fortes et égalité d'informations
- **A** : méthode globale et repli fixés en fonction des seuls cas d'entraînement.
- **B** : meilleur ordre fixe de 2 méthodes par sous-type, sélection exhaustive sur les seules tâches d'entraînement, objectif du même score `certification - 0.05*calls`.
- **D** : stratégie conditionnelle « repli intelligent » par sous-type : meilleure première méthode selon l'entraînement, et seconde méthode ayant la meilleure fréquence de certification **conditionnellement au type d'échec réellement observé**, avec repli global quand ce type d'échec est inédit. Elle reçoit les mêmes informations de sous-type et de motif d'échec que C ; son code et son réglage sont figés avant lecture des résultats.
- **E** : Omega actuel `optimize_policy` entraîné sur le même nouveau jeu par sous-type, et exécuté avec la même exigence de certificat.
- **F** : oracle rétrospectif de la meilleure paire fixe sur les 24 cas test, **non admissible comme concurrent**.

Si D et C se rejoignent, les classer à égalité : ne pas revendiquer une émergence stratégique. Si B/D bat C, publier ce contre-exemple et ne pas régler C sur les cas de test. Les politiques n'ont accès ni aux pannes cibles, ni au fichier de référence par leur chemin pour choisir une action ; seuls sous-type, historiques et derniers retours de méthode sont autorisés.

## Contre-tests
1. Un calcul borné `compute` ou `refute` sans contre-exemple donne `unknown`, jamais un universel vrai.
2. Un document `header` indisponible ne peut donner une réponse certifiée.
3. Aucune stratégie ne peut effectuer trois essais, relancer une méthode, ni utiliser un résultat non observé.
4. Le choix est invariant à l'ordre des lignes d'apprentissage et ne dépend pas des réponses de la partition test.
5. Corriger la classification du type d'échec ne doit pas créer de certificat ; les raisons d'échec peuvent orienter la méthode suivante seulement.
6. Comparer le regret aux baselines sur le score conventionnel et les taux de réussite ; signaler toute supériorité due à plus d'essais.
7. Vérifier séparément l'invariant de vérité des méthodes sur les 48 cas et des contrôles documentaires RFC officiels. Les sorties des méthodes ne constituent pas une validation humaine indépendante.

## Arrêt et livrables
Exécuter une seule fois les 24 cas test avec tous les bras, puis figer traces et verdict. Pas de sélection de meilleurs cas a posteriori ni de modification des poids pour embellir l'épreuve. Les corrections de bugs nécessaires doivent être publiées avec nouvelle CI et statut expérimental. Mettre protocole, code, tests, diagnostics et rapport final dans une PR brouillon empilée sur #34 ; ni merge de main, ni écritures de bibliothèque certifiée ou SQLite.

**Critère scientifique** : une fonction objectif « certificat » n'est intéressante que si elle dépasse une politique simple de sélection conditionnelle disposant de la même information, et si le gain subsiste sur un nouveau lot réellement indépendant. La présente expérience teste une première calibration, pas cette preuve finale.
