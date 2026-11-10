# P5 — matrice de tests négatifs du validateur (spécification)

**Statut :** spécification de tests — pas une preuve d'implémentation ni d'exécution.  
**Dépendance :** le contrat exact du validateur doit être aligné sur le protocole P5 v0.2 avant codage.  
**Principe :** les tests doivent vérifier les invariants de la soumission, sans contenir ni révéler de corrigé v0.5.

## 1. Invariants attendus

Le validateur doit refuser une soumission si l'une des conditions suivantes est vraie :
- bras requis manquant ;
- sortie manquante pour un cas attendu ;
- doublon d'une même unité (cas, bras, répétition ou évaluateur selon le schéma) ;
- évaluateur requis absent ou couverture non équilibrée ;
- moins de deux évaluateurs communs à toutes les sorties, si cette règle est maintenue dans le protocole ;
- score non numérique, NaN, +Inf ou -Inf ;
- score hors bornes ;
- identifiant de cas ou de bras inconnu ;
- champ obligatoire manquant ou type incorrect ;
- nombre de répétitions différent du pré-enregistrement ;
- métadonnées de version/prompt/outils absentes lorsque le protocole les rend obligatoires.

Le validateur doit accepter une soumission valide, y compris lorsque l'ordre des lignes est permuté.

## 2. Matrice minimale

| ID | Mutation négative | Résultat attendu |
|---|---|---|
| V-NEG-01 | Supprimer toutes les sorties du bras B | REJET |
| V-NEG-02 | Supprimer une sortie pour un cas attendu | REJET |
| V-NEG-03 | Retirer un évaluateur de la couverture commune | REJET |
| V-NEG-04 | Un seul évaluateur sur l'ensemble | REJET |
| V-NEG-05 | Dupliquer une clé de soumission | REJET |
| V-NEG-06 | Ajouter un cas inconnu | REJET |
| V-NEG-07 | Ajouter un bras inconnu | REJET |
| V-NEG-08 | Score = NaN | REJET |
| V-NEG-09 | Score = +Inf ou -Inf | REJET |
| V-NEG-10 | Score inférieur au minimum ou supérieur au maximum | REJET |
| V-NEG-11 | Omettre un champ obligatoire | REJET |
| V-NEG-12 | Remplacer un nombre par une chaîne | REJET |
| V-NEG-13 | Modifier le nombre de répétitions | REJET |
| V-NEG-14 | Omettre les métadonnées pré-enregistrées obligatoires | REJET |
| V-POS-01 | Soumission complète conforme | ACCEPTATION |
| V-POS-02 | Même soumission, lignes permutées | ACCEPTATION |
| V-POS-03 | Valeur limite autorisée (min/max) | ACCEPTATION |

## 3. Tests de mutation

Pour chaque test négatif :
1. Construire un petit jeu synthétique entièrement fictif, sans réponse de modèle réelle.
2. Valider d'abord le jeu de base et vérifier qu'il est accepté.
3. Appliquer une seule mutation.
4. Vérifier le rejet et un code d'erreur stable.
5. Vérifier que le message d'erreur ne révèle aucune donnée secrète.
6. Restaurer le jeu de base avant la mutation suivante.

Un test qui échoue parce que le jeu de base est lui-même invalide n'est pas un test négatif valide.

## 4. Contrôles de robustesse supplémentaires

- JSON mal formé et lignes JSONL vides selon la convention retenue.
- Unicode, espaces et ordre de propriétés JSON.
- Identifiants dupliqués avec espaces/casse différents si la normalisation est autorisée.
- Fichier vide, fichier tronqué et très grand nombre de lignes.
- Entrée contenant des clés supplémentaires : rejet strict ou tolérance documentée, mais jamais interprétation silencieuse.
- Réexécution du validateur : résultat déterministe.
- Code de sortie non nul sur rejet ; zéro uniquement sur acceptation.
- CI exécutant les tests depuis un checkout propre.

## 5. Condition de certification

La porte G8 ne peut passer que si :
- le schéma canonique est versionné ;
- tous les tests positifs et négatifs sont implémentés ;
- les tests réussissent en CI sur un commit identifié ;
- les erreurs sont explicites et stables ;
- aucune sortie invalide n'est acceptée ;
- la revue vérifie aussi que le validateur n'altère pas les données brutes.

Ce document ne déclare aucun test exécuté ni validateur certifié.
