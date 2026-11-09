# P5 — protocole d’évaluation comparative du prisme Omega

**Version :** 0.1  
**Statut :** protocole et validateur implémentés ; aucune campagne A/B/C exécutée  
**Branche :** `architecture/memoire-agentique-native-2026-11-05`  
**Périmètre :** évaluer l’utilité du routage adaptatif, pas valider des résultats scientifiques.

## 1. Question évaluée

Sur un ensemble de missions fixé avant l’essai, la configuration C (prisme adaptatif) améliore-t-elle la qualité des réponses par rapport à A (ChatGPT sans décomposition explicite) et B (prisme fixe), à budget comparable ?

Aucun gain n’est présumé. Une absence de gain, une régression ou un résultat indéterminé sont des issues recevables.

## 2. Bras comparés

- **A — référence :** réponse directe de l’agent principal, sans plan de perspectives explicite.
- **B — prisme fixe :** même agent principal, rôles préétablis identiques pour toutes les missions pertinentes.
- **C — prisme adaptatif :** plan produit par `planner.py`, rôles sélectionnés et justifiés selon la mission.

Les trois bras utilisent le même modèle disponible, la même version/configuration autant que possible, les mêmes outils autorisés, le même contexte de départ et le même budget maximal. Toute différence inévitable est consignée. Les perspectives de B et C sont des rôles du même agent principal, pas des agents indépendants.

## 3. Jeu d’évaluation tenu à l’écart

Le jeu doit être gelé avant les essais et ne doit pas avoir servi à modifier le planificateur, les prompts ou les règles de notation.

Strates minimales :
1. problèmes formels avec hypothèses et quantificateurs ;
2. cas finis/calculables avec résultat de référence reproductible ;
3. questions documentaires nécessitant des sources primaires ;
4. missions exploratoires avec plusieurs hypothèses concurrentes ;
5. cas adversariaux contenant ambiguïtés, données manquantes ou prémisses fausses.

Pour chaque cas, un responsable prépare avant l’essai : identifiant, énoncé exact, périmètre, corrigé ou critères de décision, sources de référence, pièges connus, tests discriminants et limites du corrigé. Les cas et corrigés sont conservés séparément des sorties évaluées. Le jeu final n’est pas encore constitué par ce commit.

## 4. Procédure

1. Geler le jeu, les critères, les budgets et les versions ; calculer les empreintes des fichiers.
2. Générer A, B et C pour chaque cas dans des sessions séparées, avec ordre aléatoire. Ne pas exposer les sorties d’un bras aux autres.
3. Capturer les prompts, contextes, outils réellement utilisés, versions, temps, appels, coûts disponibles, erreurs et sorties brutes.
4. Remplacer les étiquettes A/B/C par des identifiants opaques avant notation. L’évaluateur ne doit pas connaître le bras.
5. Faire noter chaque sortie par au moins deux évaluateurs indépendants, sans accès à l’identité du bras ni aux notes de l’autre évaluateur.
6. Résoudre les désaccords selon une règle préenregistrée ; conserver les notes initiales et l’arbitrage.
7. Déverrouiller les étiquettes seulement après gel des notes.
8. Rapporter les résultats par strate, les différences appariées, les intervalles d’incertitude, les échecs et les cas où les évaluateurs ne peuvent pas trancher.

Si deux évaluateurs réellement indépendants ne sont pas disponibles, le rapport doit le dire et ne pas qualifier la notation d’indépendante.

## 5. Grille de notation humaine

Chaque dimension est notée de 0 à 4 selon un guide défini avant l’essai :

- exactitude et respect du corrigé ;
- validité des justifications et adéquation des sources ;
- qualité des tentatives de réfutation et détection des contre-exemples ;
- calibration : incertitudes, limites et refus de conclure quand il le faut ;
- traçabilité : possibilité de reconstruire les opérations et provenances ;
- conservation des désaccords et des hypothèses concurrentes.

Les évaluateurs comptent séparément les affirmations factuelles non étayées, les erreurs matérielles et les contre-exemples pertinents manqués. Une réponse plus longue ou comportant plus de rôles ne reçoit aucun crédit par elle-même.

Le score global ne doit pas masquer les dimensions : publier chaque dimension et les comptages séparément. Le protocole ne fixe pas de pondération composite avant validation du guide.

## 6. Mesures opérationnelles

Pour chaque bras et chaque cas, enregistrer :
- durée murale ;
- nombre d’appels et d’outils ;
- coût observé, ou « non disponible » ;
- taux d’échec technique ;
- nombre de perspectives planifiées, réellement exécutées et non exécutées ;
- erreurs matérielles, affirmations non étayées et contre-exemples pertinents manqués.

Comparer les bras à budget comparable. Si les budgets diffèrent, présenter le compromis qualité/coût plutôt que d’attribuer tout écart à l’adaptativité.

## 7. Analyse et décision

- Analyse principale appariée par cas ; publier les résultats par strate et globalement.
- Rapporter les effectifs, données manquantes, désaccords inter-évaluateurs et intervalles d’incertitude.
- Ne pas traiter les cas d’un même domaine comme des observations nécessairement indépendantes.
- Ne pas modifier le planificateur à partir du jeu tenu à l’écart. Toute adaptation crée une nouvelle version et exige un nouveau jeu de test.
- Conclure séparément sur qualité, traçabilité, coût/latence et robustesse.
- « Amélioration démontrée » exige un protocole préenregistré, un échantillon adéquat, une évaluation réellement aveugle et indépendante, et des résultats robustes. Sinon : « indéterminé » ou « signal exploratoire ».

## 8. Limites et état actuel

Ce dépôt contient le protocole et un validateur structurel de notes. Il ne contient pas encore de jeu d’évaluation gelé, de sorties A/B/C, de notation indépendante ni de calcul de significativité. Le validateur vérifie la forme et la cohérence des enregistrements ; il ne juge pas la vérité d’une réponse et ne produit aucune certification RAVI-2.

Le module P1–P4 reste un prototype supervisé. Il n’exécute pas lui-même les bras A/B/C et ne lance pas de modèles.
