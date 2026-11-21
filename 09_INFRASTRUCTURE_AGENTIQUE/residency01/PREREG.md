# RESIDENCY-01 — préengagement du gestionnaire local de modèles (2026-11-21)

**But** : réserver la RAM à un seul modèle quantifié à la fois, sans conserver ses caches KV lorsqu'on passe à un autre modèle. Empêcher un chargement non vérifié ou une substitution de poids. Les décisions scientifiques sont laissées au lecteur/vérificateur original, non à ce gestionnaire.

## Contraintes
- Modèles admissibles : **seulement** Qwen2.5-0.5B-Instruct Q4_K_M et Qwen2.5-3B-Instruct Q4_K_M avec SHA256 et moteur llama.cpp épinglés dans Reader18/SCALE01.
- Aucune option qui télécharge un modèle 7B ou 14B, aucun entraînement, aucune API payante.
- Un seul modèle **résident** à la fois : changement = arrêter l'ancien processus local et attendre son arrêt avant démarrer le nouveau. L'état KV et les requêtes précédentes ne sont pas partagés entre deux modèles.
- Avant chaque nouveau chargement : vérifier fichier et SHA256 des poids, identifiant de modèle, révision du moteur, taille de fichier, **mesure réelle** du pic RSS du modèle tirée d'un rapport SCALE01 terminé ; budget RAM de l'ordinateur moins réserve de sécurité.
- Si le rapport est absent/non mesuré, si l'empreinte est fausse, si la RAM ne suffit pas ou si l'ancien serveur ne s'arrête pas : **refuser**, sans substituer silencieusement un modèle plus petit.
- Le gestionnaire ne doit pas promettre la réussite de l'inférence à partir de la seule RAM : réserver une marge et observer l'état sain du serveur lancé.
- Les appels réseau à un serveur restent en boucle locale `127.0.0.1`. `cache_prompt=false` demeure la politique par défaut pour toute classification scientifique, puisque KV-EXT01 #221 a constaté des divergences.
- Protéger les transitions et les erreurs de démarrage par tests à backend factice (échecs d'arrêt/chargement, poids altérés, budget insuffisant, même modèle réutilisé, aucune dégradation automatique).

## Portée des tests
- Tests logiciels et de simulation de démarrage **sans poids modèle** pour le gestionnaire, avec fichiers éphémères réellement hachés.
- Le bon fonctionnement physique du basculement 0,5B↔3B dans une seule machine reste **NON MESURÉ** tant qu'un vrai test de passage sur le même runner n'est pas exécuté.
- La RAM maximale mesurée par SCALE01 est une **observation** sur un runner, pas une limite universelle ni une garantie de disponibilité sur une autre machine.
- Aucune modification de `main`, pas de déploiement de serveur public, pas d'intégration automatique à la production Omega.

Préenregistrement et code sur une branche expérimentale séparée, empilée sur SCALE-01 #223. Toute limite rencontrée doit être déclarée, pas contournée par un changement de modèle non autorisé.
