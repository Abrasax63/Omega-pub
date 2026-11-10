# Prisme adaptatif Omega — contrat de conception 0.1

**Statut :** spécification initiale, non implémentée et non évaluée  
**Branche :** `architecture/memoire-agentique-native-2026-11-05`  
**Principe :** ChatGPT reste l'agent principal ; Omega organise l'accès aux capacités et conserve les traces.

## 1. Objectif

Le Prisme adaptatif ne remplace ni ChatGPT, ni RAVI-2, ni le Research Context Engine (RCE). Il aide l'agent principal à décomposer une mission en angles de travail utiles, préparer des contextes adaptés, confronter les résultats et recombiner les éléments soutenus par des preuves.

Le prisme est adaptatif : il ne lance pas systématiquement tous les rôles. Il sélectionne les angles selon la nature de la question, les incertitudes, les dépendances et le verrou susceptible de changer le verdict.

## 2. Rôle, exécution et agent indépendant

Trois niveaux doivent rester distincts :

1. **Perspective de rôle :** consigne spécialisée appliquée par l'agent principal.
2. **Exécution séparée :** tâche, contexte, sortie et trace distincts. Deux exécutions peuvent partager modèle, données et biais.
3. **Agent indépendant :** processus ou modèle distinct, avec provenance et configuration identifiables. Son indépendance doit être évaluée par dimensions ; elle ne découle pas de son nom ou de son rôle.

Dans la première version, ChatGPT effectue les perspectives qu'il peut réellement prendre en charge. Il ne présente jamais ces perspectives comme des sous-agents autonomes ou des vérifications indépendantes. Les modèles externes et agents distants sont une capacité ultérieure, soumise à disponibilité, autorisation, coût et traçabilité.

## 3. Rôles réutilisés du RCE

- `researcher` : état des connaissances, lacunes, hypothèses concurrentes et pistes.
- `refuter` : réfutation prioritaire, contre-exemples, cas limites, contradictions et résultats négatifs.
- `formalist` : définitions, quantificateurs, hypothèses, portée exacte et chaîne logique.
- `computational` : calculs discriminants, données, scripts, reproductibilité et limites d'exécution.
- `bibliographer` : sources primaires, littérature contradictoire, antériorité et limites de la recherche documentaire.

L'agent principal assure coordination et synthèse. Cette fonction n'est pas comptée comme un agent indépendant.

## 4. Routage adaptatif initial

Le routeur produit un plan explicable, pas un score opaque :

- Toute affirmation susceptible d'être fausse reçoit une passe de réfutation avant toute conclusion positive.
- Si la mission dépend de définitions, d'hypothèses ou d'une preuve, activer `formalist`.
- Si un cas fini, un contre-exemple ou une distinction calculable peut changer le verdict, activer `computational`.
- Si l'originalité, l'état de l'art ou une affirmation historique est en jeu, activer `bibliographer`.
- Si le problème est exploratoire ou mal cartographié, activer `researcher`.
- Ne pas activer un rôle sans question précise.
- Éviter les perspectives redondantes qui ne peuvent produire de résultat discriminant.
- Commencer par le verrou au gain d'information attendu le plus élevé.

Chaque activation précise : question assignée, raison du routage, contexte nécessaire, résultat attendu, test d'échec et condition d'arrêt.

## 5. Cycle de mission

1. **Cadrage :** question, périmètre, exclusions et verdict à éclairer.
2. **État initial :** interroger le RCE ; récupérer IDs, versions, statuts, dépendances et objections.
3. **Choix du prisme :** sélectionner les rôles et justifier chaque activation.
4. **Travaux séparés :** une sortie par rôle, avec sources consultées et actions réellement exécutées.
5. **Confrontation :** contradictions, dépendances communes, désaccords et éléments manquants.
6. **Test discriminant :** au plus deux nouvelles expériences décisives pour le verrou actif, conformément à RAVI-2.
7. **Recombinaison :** synthèse conservant les désaccords et distinguant faits, calculs, simulations et hypothèses.
8. **Traçabilité :** enregistrer plan, contextes, sorties, erreurs, coûts et limites comme activités candidates.
9. **Décision :** aucune promotion automatique ; RAVI-2 reste responsable de la validation scientifique.

## 6. Contrat de sortie

Chaque mission produit un objet structuré comprenant :

- `mission_id`, version et question exacte ;
- état de départ et verrou choisi ;
- rôles activés et non activés, avec justification ;
- pour chaque tâche : question, contexte, agent/modèle réellement utilisé, version disponible, statut d'exécution ;
- sources et artefacts avec identifiants, versions et localisateurs ;
- résultats séparés, objections et désaccords ;
- dépendances partagées et dimensions d'indépendance connues/inconnues ;
- tests exécutés, commandes, données, sorties et empreintes lorsqu'elles existent ;
- actions non exécutées, erreurs et limites ;
- synthèse et statut épistémique ;
- proposition éventuelle à soumettre à RAVI-2.

Statuts d'exécution : `completed`, `partial`, `failed`, `not_executed`. Une tâche prévue mais non exécutée ne doit jamais être décrite comme un résultat.

## 7. Évaluation de l'utilité

Le prisme ne sera considéré comme une amélioration que si une comparaison contrôlée montre un gain. Comparer sur un jeu de problèmes tenu à l'écart du réglage :

- **A — référence :** ChatGPT sans décomposition explicite ;
- **B — prisme fixe :** rôles prédéfinis ;
- **C — prisme adaptatif :** sélection justifiée selon la mission.

Mesures minimales : exactitude du verdict selon corrigé ou revue indépendante ; taux de contre-exemples pertinents détectés ; erreurs et affirmations non sourcées ; qualité de traçabilité ; temps, appels et coût ; conservation des désaccords ; reproduction par un évaluateur ignorant la configuration utilisée.

Les jeux de test ne doivent pas servir au réglage puis être présentés comme preuve d'amélioration. Rapporter les gains avec incertitude et échecs.

## 8. Garde-fous

- RAVI-2 n'est pas réimplémenté.
- Le nombre de rôles, de votes ou d'appels ne vaut pas preuve.
- Les perspectives exécutées par le même modèle ne sont pas indépendantes par défaut.
- Une source commune est signalée comme dépendance commune.
- Aucune auto-certification ni écriture directe dans la mémoire certifiée.
- Aucun accès aux secrets, données privées ou espaces non autorisés.
- Aucun appel externe sans outil réellement disponible et autorisé.
- Aucun calcul, recherche ou test prétendument exécuté s'il ne l'a pas été.
- Les sorties restent expérimentales jusqu'à décision RAVI-2.

## 9. Incréments d'implémentation

- **P0 — Contrat et état des lieux :** présent document ; réutilisation des rôles RCE et de la passerelle MCP existante.
- **P1 — Planificateur explicable :** fonction pure qui reçoit une mission structurée et retourne les rôles, questions, critères d'échec et raisons du routage. Aucun appel de modèle ni écriture.
- **P2 — Préparation des contextes :** appeler `memory_search` et `memory_get` pour chaque tâche, sans aplatir les statuts ni confondre candidats documentaires et dépendances.
- **P3 — Exécution supervisée :** ChatGPT exécute les perspectives disponibles et renvoie des sorties structurées. Les modèles distincts restent optionnels et identifiés.
- **P4 — Enregistrement :** journaliser plans et exécutions selon le schéma d'événement existant, sans secrets.
- **P5 — Évaluation comparative :** protocole A/B/C, tests tenus à l'écart et revue indépendante avant adaptation automatique.

La publication de ce contrat ne signifie pas que les phases suivantes sont réalisées.

## 10. Premier critère d'acceptation

Le prototype sera acceptable seulement s'il explique pourquoi chaque rôle est activé ou écarté, produit des tâches non redondantes et falsifiables, conserve sources et statuts RCE, marque les perspectives non exécutées, ne confond pas rôles et agents indépendants, et ne modifie aucun résultat scientifique ni fichier de mémoire certifiée.
