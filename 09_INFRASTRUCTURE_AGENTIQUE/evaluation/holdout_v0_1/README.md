# Jeu pilote P5 — version 0.1

**Statut :** jeu pilote construit ; gel documentaire à ce commit ; pas encore exécuté.  
**Taille :** 5 cas, un par strate.  
**Usage :** test exploratoire initial, pas benchmark statistiquement puissant.

## Fichiers
- `cases.jsonl` : énoncés, livrables attendus et axes de notation.
- `answer_key.jsonl` : éléments de correction et erreurs critiques. À conserver hors du contexte des systèmes évalués.
- `SHA256SUMS.txt` : empreintes des deux fichiers.

## Avertissement de confidentialité
Le dépôt est public. La séparation en fichiers ne rend donc PAS le corrigé secret : toute personne ayant accès à la branche peut le consulter. Pour une véritable évaluation aveugle, copier `answer_key.jsonl` dans un espace privé avant de soumettre les cas aux systèmes, puis retirer le corrigé du contexte des évaluateurs. Cette version est un pilote reproductible, pas un jeu de test secret.

## Limites
- 5 cas seulement : insuffisant pour conclure statistiquement à une supériorité générale.
- Un cas par strate ne permet pas d'estimer correctement les effets de domaine.
- Le cas documentaire est fondé sur RFC 9110, source primaire.
- Les cas formels et calculatoires ont des corrigés déterministes ; le cas exploratoire est évalué sur la calibration et la qualité des contre-modèles, pas sur une réponse unique.
- Aucun résultat A/B/C n'est inclus. Aucune campagne n'a été lancée.
- Ce jeu doit rester inchangé après le premier lancement. Toute modification ultérieure crée une nouvelle version et doit être testée sur un autre jeu tenu à l'écart.

## Procédure de gel
1. Vérifier les empreintes.
2. Copier le corrigé dans un espace privé.
3. Geler les prompts et le barème avant toute génération.
4. Générer A/B/C en sessions séparées.
5. Randomiser et masquer les bras avant notation.
6. Ne déverrouiller les bras qu'après gel des notes.
