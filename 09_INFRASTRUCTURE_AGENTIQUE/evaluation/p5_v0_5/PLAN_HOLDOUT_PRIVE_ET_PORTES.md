# P5 — préparation v0.5 privé et portes de validation

**Statut :** PLAN DE CONCEPTION — aucun holdout privé créé — aucun pilote autorisé.  
**Point de départ vérifié :** P5 v0.4 public, candidat non gelé, cinq cas.  
**Branche de travail :** `work/p5-calibration-v0-5-plan-2026-11-10`.

## 1. Décisions de séparation

- v0.4 reste un corpus public de calibration. Ne pas le renommer « aveugle » et ne pas tenter d'en restaurer le secret.
- v0.5 doit être un nouveau corpus, avec nouveaux identifiants et énoncés rédigés indépendamment. Ne pas simplement paraphraser les cinq items v0.4.
- Aucun énoncé, corrigé, indice, barème détaillé ou hash permettant une attaque par dictionnaire ne doit être publié dans ce dépôt public avant la clôture du test.
- Ce dépôt peut contenir le protocole, les schémas, le code du validateur et des tests synthétiques ; le corpus v0.5 et son corrigé restent dans un espace privé contrôlé.
- Ne pas supprimer les anciens artefacts publics : l'historique Git demeure une source de fuite.

## 2. Composition cible du corpus privé

Cinq cas inédits, avec des domaines et modes de raisonnement différents :
1. Démonstration formelle avec quantificateurs et contre-modèle.
2. Calcul exact vérifiable indépendamment, sans reprendre le thème des congruences.
3. Lecture critique d'une source normative ou technique primaire.
4. Interprétation de données avec piège de causalité, de sélection ou d'agrégation distinct du cas v0.4.
5. Réfutation adversariale d'une affirmation universelle, avec minimalité ou caractérisation corrigée.

Ces familles sont des quotas de couverture, pas des énoncés. Le rédacteur du v0.5 ne doit pas recycler les structures numériques, objets, formulations ou solutions de v0.4/v0.1.

## 3. Séparation des rôles

- **Constructeur** : rédige les énoncés et une première solution ; n'accède pas aux sorties des modèles.
- **Réfutateur** : cherche ambiguïtés, contre-exemples, solutions alternatives et fuites ; peut demander une révision mais ne valide pas son propre correctif.
- **Référent de source/calcul** : vérifie les sources primaires et refait les calculs par une voie distincte.
- **Évaluateur humain indépendant** : n'a participé ni à la rédaction ni à la sélection des items ; examine énoncés, corrigés et barème.
- **Gestionnaire du secret** : contrôle les accès, les versions, les journaux et la distribution. Il ne transmet que les énoncés aux systèmes évalués.

Si les rôles sont tenus par une même personne ou un même agent, cette dépendance doit être déclarée ; elle ne vaut pas indépendance.

## 4. Gel et provenance

Avant toute passation :
- figer les énoncés, corrigés, barème, protocole d'annotation et manifeste dans un stockage privé ;
- calculer SHA-256 sur les octets exacts de chaque fichier après gel ;
- enregistrer versions, auteur, relecteur, date, accès et modifications ;
- conserver une copie scellée non modifiable et journaliser toute consultation ;
- définir précisément ce qui est communiqué à chaque bras et à chaque évaluateur ;
- vérifier l'absence de publication antérieure par recherche d'extraits distinctifs et revue de provenance ;
- ne publier les empreintes qu'après évaluation si leur divulgation ne compromet pas le secret résiduel.

Un hash n'établit ni l'indépendance, ni la qualité, ni l'absence de fuite ; il atteste seulement l'identité des octets comparés.

## 5. Pré-enregistrement expérimental

Le pré-enregistrement doit fixer avant génération :
- identifiants et versions exactes des modèles/agents, paramètres et dates ;
- prompts système et utilisateur, contexte mémoire fourni, outils autorisés et état des connexions ;
- budget de tokens, temps, appels, reprises et règles d'arrêt ;
- bras A/B/C et différence exacte entre eux ;
- randomisation de l'ordre des items et des bras ;
- nombre de répétitions et gestion des sorties manquantes ;
- anonymisation, notation aveugle, arbitrage et traitement des incidents ;
- métriques primaires, secondaires, seuils, analyses et règles d'exclusion.

Toute modification après pré-enregistrement est consignée comme déviation ; elle ne doit pas être silencieusement intégrée à l'analyse confirmatoire.

## 6. Portes de validation

| Porte | Condition de passage | État actuel |
|---|---|---|
| G1 — corpus distinct | cinq items inédits, provenance vérifiée | NON DÉMARRÉ |
| G2 — correction | corrigés reconstruits par une voie distincte | NON DÉMARRÉ |
| G3 — adversarial | ambiguïtés et contre-exemples traités | NON DÉMARRÉ |
| G4 — indépendance | revue humaine sans participation à la rédaction | BLOQUÉ |
| G5 — secret | stockage privé, accès contrôlé, journalisation | NON DÉMARRÉ |
| G6 — gel | versions et empreintes exactes gelées | NON DÉMARRÉ |
| G7 — barème | barème calibré et fidélité inter-évaluateurs mesurée | NON DÉMARRÉ |
| G8 — validateur | tests positifs/négatifs et CI réussis | NON DÉMARRÉ |
| G9 — pré-enregistrement | bras, prompts, budgets, randomisation et analyses figés | NON DÉMARRÉ |
| G10 — autorisation | décision explicite après audit complet | NON AUTORISÉ |

Aucune porte n'est réputée franchie sur la seule base de ce document.

## 7. Critères d'arrêt

Arrêter et classer le corpus ou l'expérience comme non confirmatoire si :
- un item ou son corrigé a été exposé à un bras évalué ;
- une fuite plausible ne peut pas être exclue ;
- les évaluateurs connaissent le bras ou l'identité du modèle ;
- le validateur accepte une soumission invalide ou rejette une soumission valide ;
- le barème change après observation des résultats sans renotation complète ;
- le nombre de répétitions, les budgets ou les règles d'exclusion diffèrent entre bras sans pré-enregistrement.

## 8. Ce qui n'est pas fait

Aucun v0.5 réel n'est inclus dans cette branche publique. Aucun corrigé privé n'a été créé. Aucun évaluateur humain indépendant n'a été sollicité. Aucun test A/B/C n'a été lancé. Aucun résultat de performance Omega n'est établi.
