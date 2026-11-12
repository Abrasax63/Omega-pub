# Pré-enregistrement : première contribution mesurable d'Omega (P5-VALUE-01)

**12 novembre 2026 — avant le code et toute nouvelle génération modèle.**

## Question scientifique

Distinguer **(H1)** le gain réel apporté par une vérification mathématique exécutable d'une réponse de modèle, de **(H2)** le gain propre à la politique de sélection adaptative d'Omega. Ne pas confondre les deux.

Hypothèse nulle H1 : un correcteur/calculateur externe n'améliore pas l'exactitude appariée sur de nouvelles tâches exécutables. H2 : à capacité de vérification identique, la stratégie Omega ne surpasse pas un simple routage basé sur le type de tâche.

## Jeux et gel avant appels

Jeu **public de calibration uniquement**, non indépendant et non secret. 18 tâches nouvelles distinctes du premier pilote : 6 congruences CRT, 6 comparaisons exactes de taux agrégés, 6 affirmations documentaires explicitement **non authentifiées**. Les paramètres numériques et les six énoncés fictifs doivent être gelés dans une constante de programme avant le premier appel au modèle ; aucune modification ultérieure du jeu en réponse aux résultats. Les références exactes seront calculées par une **autre implémentation** que l'outil de vérification.

Pour chaque tâche : même contenu documentaire et question pour A/B/C, mêmes paramètres et même modèle, zéro historique de réponse réutilisé. Aucun corpus privé P5 v0.5 ni corrigé provenant de la Bibliothèque ne doit être lu. Tout reste public.

## Traitements et témoins

- **A** : modèle, réponse directe.
- **B** : même modèle, cinq perspectives fixes.
- **C** : même modèle, rôles sélectionnés par le vrai `planner.plan_mission` (il n'exécute pas des sous-agents).
- **A+V** et **C+V** : mêmes réponses modèles A/C, puis vérification/calcul exact **disponible à tous les bras** ; sur tâche documentaire non authentifiée, abstention. Ces conditions n'effectuent pas d'appel modèle supplémentaire et visent à mesurer le gain du vérificateur, non à le présenter comme un gain propre à C.
- **V-all** : vérificateur systématiquement appelé sur les 18 tâches ; abstention si verdict non disponible.
- **Omega-route** : planificateur actuel sélectionne le calculateur pour les tâches où le rôle `computational` est activé, sinon abstention ; ne remplace pas un raisonnement général.
- **Type-route** : routeur trivial `mission_type == computational`, témoin négatif destiné à détecter l'absence de valeur spécifique du planificateur.
- Une « réussite » d'Omega-route égale à Type-route n'est **pas** un avantage scientifique d'Omega.

## Métriques primaires et limites

1. Score d'**exactitude explicite** de A/B/C, avec un parseur robuste mais **figé avant génération**. Refuser les réponses absentes/ambiguës ; conserver la sortie brute. Les bonnes conclusions non conformes sont comptées séparément comme refus de parsing, pas transformées arbitrairement en échec sémantique.
2. Exactitude A+V, C+V, V-all, Omega-route et Type-route sur un oracle de référence indépendant du code de vérification. C'est une vérification logicielle sur une famille restreinte, **pas** une preuve d'intelligence générale.
3. Nombre de générations modèle, tokens de prompts/sortie et appels au vérificateur par condition ; aucune estimation de gains de facturation si le matériel n'est pas facturé au token.
4. Contrastes clés : C–A et C–B sans outil ; A+V–A (valeur de la vérification), C+V–A+V (valeur marginale Omega **à même outil**), Omega-route–Type-route (valeur marginale du routage au-delà d'une règle triviale).
5. Résultats **exploratoires uniquement** ; les 18 tâches sont conçues par l'auteur, les tests ne sont pas indépendants/aveugles, six cas par catégorie, modèle open-weight modeste.

## Cadre d'exécution et critère d'arrêt

GitHub Actions **standard sur dépôt public** et modèle open-weight `Qwen/Qwen2.5-0.5B-Instruct` en CPU ; **54 générations maximum** = 18 tâches × A/B/C × 1. Aucun client OpenAI API, aucune clé et aucun achat. `max_new_tokens=96`, échantillonnage déterministe `do_sample=False`, ordre des requêtes mélangé sous graine prédéfinie `20261112`. Une erreur d'installation/modèle, l'absence d'une sortie ou l'échec d'un test oracle produit le statut `INCOMPLETE` ; aucun score proclamé sans archive complète.

**Important** : la bibliothèque historique, le holdout privé, PR #47/#48 et `main` ne sont pas modifiés.
