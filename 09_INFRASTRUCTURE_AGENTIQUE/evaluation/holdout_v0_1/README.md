# Jeu pilote P5 — v0.1 (développement public, non aveugle)

**Statut :** cinq cas publics de développement ; aucune campagne A/B/C exécutée.  
**Usage autorisé :** tests fonctionnels, essais de prompts et démonstrations non aveugles.  
**Usage interdit comme preuve :** benchmark aveugle ou démonstration de supériorité.

## Fichiers
- `cases.jsonl` : cinq énoncés publics, un par strate.
- `answer_key.jsonl` : corrigé historiquement commité dans le dépôt public.

## Alerte de contamination

Le corrigé est accessible dans l'historique et les copies du dépôt public. Il est donc **compromis comme secret**. Le déplacer, le supprimer ou réécrire la branche ne garantit pas l'effacement des clones, caches ou historiques. Ne pas utiliser v0.1 pour une évaluation prétendument aveugle.

Pour un essai aveugle, créer un holdout v0.2 avec de nouveaux cas et garder son corrigé dans un espace privé, hors de portée des systèmes et évaluateurs pendant la génération. Le dépôt public ne doit contenir que les cas destinés aux systèmes et une empreinte du corrigé privé, pas son contenu.

## Limites
- Cinq cas ne permettent aucune conclusion statistique générale.
- Un cas par strate ne permet pas d'estimer les effets de domaine.
- Le cas documentaire s'appuie sur la RFC 9110, sections 9.2.1 et 9.2.2 : https://www.rfc-editor.org/rfc/rfc9110.html
- Aucun résultat A/B/C, aucune notation indépendante et aucune analyse statistique ne sont présents.

## Gel avant une future campagne v0.2
1. Préparer les cas et le corrigé privé indépendamment.
2. Faire relire les critères par une personne non impliquée dans la génération.
3. Calculer et enregistrer les empreintes SHA-256 avant les essais.
4. Pré-enregistrer modèles, versions, prompts, outils, budgets, randomisation et barème.
5. Générer A/B/C en sessions séparées, sans corrigé.
6. Faire noter chaque sortie par au moins deux évaluateurs indépendants, à l'aveugle.
7. Figer les notes avant arbitrage et dévoilement des bras.
