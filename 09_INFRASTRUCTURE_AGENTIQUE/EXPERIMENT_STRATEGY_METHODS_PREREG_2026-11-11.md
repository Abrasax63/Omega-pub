# OMEGA-STRAT-002 — pré-enregistrement du choix de méthode et de la révision après échec

**11 novembre 2026 — CALIBRATION PUBLIQUE CONSTRUITE, non-aveugle et sans appels LLM.**
Ce gel précède la création du programme de vérification et les premières mesures. Le modèle n'est pas un agent généraliste, ni une expérience sur des questions véritablement inédites au concepteur.

## Question scientifique
Un choix adaptatif entre quatre **procédures exécutables et distinctes** augmente-t-il la résolution sous un plafond identique de deux essais, au-delà d'un sélecteur simple entraîné par type de problème ? Les procédures ont des succès et des échecs d'applicabilité ; elles ne renvoient pas des verdicts empruntés à la clé.

## Domaines et méthodes
Quatre familles : arithmétique/graphes (math), fonctions finies et `zip(strict=True)` (programmation), comparaisons de taux et paradoxe de Simpson (données), autorisation POST→GET par statut HTTP (documentation RFC 9110). Chaque famille comprend **8 instances**, 4 de calibration (indices 0..3) et 4 de test (indices 4..7), soit 16+16. Aucune instance n'est commune. L'algorithme générateur et toutes les instances sont publics ; ce n'est pas un véritable holdout secret ou un échantillon de problèmes naturel.

Méthodes communes aux 4 familles :
- `formal` : preuve exacte par critères symboliques (divisibilité universelle ; Euler dans graphe ; calculs par produits croisés ; fonctions finies).
- `compute` : exécution réelle sur Python, calcul avec fractions exactes, énumération témoin de circuit, et contrôle exhaustif de fonctions finies.
- `refute` : recherche effective de contre-exemple borné ou témoin de collision, ne certifie jamais le vrai par simple absence de contre-exemple.
- `source` : consultation d'un **instantané local de règles identifiées** provenant de la RFC 9110 pour 301/302/307/308 et de la documentation Python de `zip(strict=True)`. **Pas d'accès externe pendant le rejeu**. Les assertions documentaires ont été lues dans des sources publiques avant l'épreuve ; la vérité n'est pas doublement certifiée par un correcteur humain indépendant.

Toutes les procédures retournent `yes`, `no` ou `unknown` ; une réponse `unknown` ne devient jamais une preuve. Les procédures sont des algorithmes, et non quatre modèles indépendants. Une réponse conclusive doit être justifiée par l'opération réellement exécutée, non par un poids d'hypothèse.

## Échecs de méthode (explicitement synthétiques)
Introduire une panne simulée de méthode, **visible uniquement lors de l'appel**, pour certains cas : math M1 et M5 : `formal` indisponible ; programmation P1 et P5 : `compute` indisponible ; données D0 et D5 : `compute` pour D0, `formal` pour D5 ; documentation S1 et S4 : `source` indisponible. Le score ne doit pas récompenser un bras qui voit ces pannes avant de choisir la méthode.

Les autres méthodes ne doivent pas être artificiellement rendues exactes en utilisant la clé de vérité. La politique ne peut pas consulter `blocked`, le corrigé, ni les sorties futures. Les tâches documentaires sans source restent indécidables et entraînent l'abstention.

## Bras et budget
- **A** : ordre unique fixe des quatre méthodes, déterminé sur les 16 cas de calibration.
- **B** : meilleur ordre fixe de **deux méthodes par domaine**, optimisé par recherche exhaustive sur les cas de calibration ; il peut arrêter après une réponse conclusive. C'est la baseline forte principale.
- **C** : véritable `optimize_policy` d'Omega à horizon 2, à partir des tableaux de résultats produits par les quatre méthodes sur les 16 cas de calibration, avec une hypothèse sentinelle `yes` et une `no` pour les cas inconnus. Si une sortie test est inconnue du plan, Omega doit s'abstenir, jamais inventer de branche ou de résultat.
- **D** : règle fixe par domaine avec repli conditionnel après `unknown` (mêmes deux méthodes et résultats que B) pour contrôler l'effet du branchement ; toutes les méthodes sont facturées.
- **E oracle** : meilleure paire sur les cas de test choisie *après observation*, uniquement comme borne explicative, pas comme politique de comparaison prédéclarée.

Tous les bras partagent les mêmes données, outils, sortie factuelle des méthodes et **2 essais maximum** par question, y compris les essais `unknown`, au coût unitaire 1. Les règles A/B/D utilisent la même connaissance des domaines que C. Le score primaire est **correcte=+1, erreur=-1, abstention=0** ; rapporter séparément exactitude, abstentions, erreurs confiantes et appels moyens. Secondaire : précision parmi réponses effectivement données et taux de couverture ; aucun temps externe, prix ou tokens. Les ordres de B et A sont choisis avant le test par ordre lexicographique en cas d'égalité.

## Invariants de méthode et tests adversariaux
1. Vérifier chaque réponse conclusive par un **oracle séparé** : modularité en k=0/k=1 ou divisibilité exacte ; graphe via recherche exhaustive d'un circuit sur les arêtes ; programme via exécution du runtime ; données via fractions/rations exactes ; RFC via sections officielles et statut exact.
2. Un test de réfutation ne peut jamais conclure `yes` parce qu'aucun contre-exemple n'a été trouvé.
3. Un certificat défaillant ou une méthode indisponible donne `unknown`, jamais une conclusion inversée.
4. Aucun bras ne peut dépenser 3 appels, réutiliser une méthode déjà tentée ou lire le corrigé avant une décision.
5. Contrôler l'invariance à l'ordre des cas d'entraînement et la robustesse de la sélection aux réponses `unknown`.
6. Ajouter un contrôle négatif sans panne où la meilleure méthode par domaine suffit ; tout choix inutilement sophistiqué perd du budget.

## Décision d'arrêt et interprétation
Après les 16 tests, ne pas remplacer les mauvais cas ni modifier les hyperparamètres ou les règles pour améliorer le résultat. Publier les erreurs, abstentions et cas où B bat C. Toute amélioration de C doit subsister contre B/D et à budget égal. Ne pas confondre maîtrise de méthodes préprogrammées avec intelligence générale ou raisonnement en langue naturelle.

## Sources
- RFC 9110 §§15.4.2, 15.4.3, 15.4.8, 15.4.9 : https://www.rfc-editor.org/rfc/rfc9110
- Python `zip(strict=True)` : https://docs.python.org/3/library/functions.html#zip

Faire le test dans une branche empilée sur la PR #33, conserver le code exact du planificateur, ouvrir une PR DRAFT, ne pas toucher main/SQLite/CORE.
