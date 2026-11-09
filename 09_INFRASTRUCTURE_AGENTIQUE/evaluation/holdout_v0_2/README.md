# P5 — holdout v0.2 (énoncés publics, corrigé privé)

**Identifiant :** `P5-HOLDOUT-2026-11-09-v0.2`  
**Statut :** jeu construit et empreintes calculées ; campagne A/B/C non lancée.  
**Branche :** `architecture/memoire-agentique-native-2026-11-05`

## Règle de confidentialité

Ce dossier ne contient que les énoncés destinés aux systèmes évalués. Le corrigé détaillé et ses critères de référence sont conservés hors du dépôt public. Le corrigé v0.1 reste compromis et ne doit pas servir à une évaluation aveugle.

## Composition

Cinq cas nouveaux, un par strate :
- raisonnement formel ;
- calcul fini exact ;
- recherche documentaire sur une source primaire ;
- observabilité et agrégation macro ;
- réfutation adversariale.

Les cas v0.2 ne réutilisent pas les énoncés de v0.1. Le cas d'observabilité porte sur la déterminisation d'un quotient par observation, et non sur la seule extrapolation d'une trajectoire.

## Engagements SHA-256

Les empreintes sont calculées sur les octets UTF-8 exacts des fichiers, avec un saut de ligne final.

- `cases.jsonl` : `7826c9cb3262d09e2cc47c8547353be95786bcd87e4b92c4be453bb0f4a85a66`
- corrigé privé `answer_key.private.json` : `6e22868dc702d951fec0fa9a27629c57be50711e1afacf349bb5261716dc81c3`

Le manifeste `commitment.json` enregistre ces deux empreintes. La seconde est un engagement cryptographique ; elle ne révèle pas le corrigé. Toute modification du jeu ou du corrigé impose une nouvelle version et de nouvelles empreintes.

## Conditions d'utilisation

- Ne pas communiquer le corrigé aux systèmes évalués ni aux évaluateurs avant la clôture de la notation.
- Pré-enregistrer les modèles, versions, prompts, outils, budgets, ordre randomisé, évaluateurs et barème.
- Générer les bras en sessions séparées, sans partage de sorties.
- Utiliser le protocole comparatif P5 : A = réponse directe ; B = perspectives à rôles fixes ; C = routage adaptatif.
- Au moins deux évaluateurs indépendants doivent noter les trois sorties de chaque cas à l'aveugle.
- Le validateur contrôle la structure des notes, pas leur vérité ni l'indépendance réelle des évaluateurs.

**Aucune génération, notation, conclusion comparative ou supériorité du bras C n'est revendiquée par la création de ce holdout.**
