# OBS-COL-10 — Pré-engagement avant le code de sélection
Date : 16 novembre 2026. Branche distincte sur la PR #96 ; `main` et les branches sources restent inchangées.

## Éviter les doublons
Déjà fait : PR #47 (16 cas privés candidats, ni notation externe ni campagne réelle), #55 (96 générations réelles mais 0 gain adaptatif spécifique), #92 (PR23/P1 identique à optimiseur exact), #96 (L# et L#+P1 requêtes identiques), #105 et #108 (cohortes prospectives pour réparation de bogues, donc **autre domaine**). Cette expérience **n'ouvre pas un autre holdout opaque** ; elle mesure la condition préalable manquante dans le domaine des automates : *le mécanisme Omega choisit-il réellement une sonde différente ?*

## Hypothèse réfutable
Sur les trois automates Moore tiers déjà épinglés dans #96 (4,3,9 états), construire un choix `Omega-candidat` pour l'ordre d'interrogation des **512 mêmes mots EQ** à chaque hypothèse L#. Ce choix peut dépendre du graphe de l'**hypothèse courante** et des préfixes **effectivement interrogés antérieurement**, mais pas du générateur vrai ni des 256 réponses réservées.

La politique est fixe avant mesure et constituée de règles déjà classiques, non d'une « intelligence autonome » :
- score d'une sonde = `4 * nombre de transitions (état hypothétique, action) distinctes traversées` + `2 * nombre de changements de sortie prédite` + `nombre de préfixes non encore vus / (len(mot)+1)` ;
- tri décroissant par score, puis longueur croissante, puis ordre d'apparition dans le manifeste.
- Pour isoler l'effet de la mémoire, bras `coverage_only` : **même score sans terme de préfixes non vus**.
- Bras `fixed` : ordre du manifeste de #96 inchangé.
- Toutes les politiques examinent le **même ensemble exact de 512 candidats** et retournent le premier contre-exemple sur préfixe ; elles peuvent consommer des budgets différents.

## Modèles, coûts, réserve et critères de succès
Vrai `run_Lsharp` AALpy 2.0.0 et véritable P1 en routage d'interventions pour `omega_candidate`, pas d'agent LLM ou API payante. Algorithme L# inchangé. Cache externe désactivé dans tous les bras. Trois automates publics tiers déjà utilisés dans la conception : cette cohorte est **calibration et NON holdout aveugle**.

Plafonds 10 000 resets / 50 000 symboles par modèle et politique ; 40 tours. Les mêmes 256 séquences réservées (longueur 12..18) que PR #96 restent indisponibles lors de la sélection. Contrôle de surapprentissage par soustraction des séquences physiquement observées. Enregistrer compteur d'essais, symboles, resets, CPU, prédictions et empreinte de chaque ordre proposé ; erreurs et blocages jamais convertis en succès.

**Succès technique** = divergence effective des premiers mots proposés (ou verdict `NO_POLICY_DIVERGENCE`), 3 bras effectivement exécutés, tests de non-fuite et budget, cohérence des résultats. **Gains scientifiques** : non revendiqués sur ces trois cas ; ne parler de gain spécifique que si une véritable politique propre à Omega dépasse une baseline classique forte sur jeu externe scellé et nouveau. `coverage_only` montre si la mémoire ajoute quelque chose au-delà d'une heuristique classique.

**Règle d'arrêt** : si la nouvelle politique ne propose aucune consultation différente, ne pas consommer un nouveau holdout. Si elle diffère, elle est seulement admissible à un futur test indépendant ; elle n'y gagne aucun certificat automatiquement.

Ne pas comparer les CPU aux expériences historiques ; ne pas fusionner ni promouvoir CORE.
