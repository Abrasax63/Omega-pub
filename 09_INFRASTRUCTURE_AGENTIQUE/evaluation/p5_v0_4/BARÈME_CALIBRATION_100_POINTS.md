# P5 v0.4 — barème de calibration (proposition gelable après revue)

**Statut :** PROPOSITION DE BARÈME — NON VALIDÉE — NON UTILISABLE POUR UN PILOTE.  
**Corpus :** les cinq énoncés publics de `holdout_v0_4/cases.jsonl`.  
**Règle :** ce barème sert à calibrer des évaluateurs sur un corpus public. Il ne transforme pas v0.4 en holdout aveugle.

## 1. Échelle commune par cas (100 points)

| Dimension | Points | Règle |
|---|---:|---|
| Exactitude du résultat central | 30 | Résultat correct, sans contradiction avec les données ou définitions |
| Justification / démonstration | 25 | Raisonnement valide, étapes nécessaires explicitées |
| Vérifications indépendantes | 15 | Contrôle distinct adapté au cas (substitution, contre-modèle, sections normatives, recalcul) |
| Couverture de la consigne | 15 | Toutes les sous-questions et demandes explicites sont traitées |
| Calibration épistémique | 10 | Limites, hypothèses et portée correctement énoncées |
| Traçabilité / reproductibilité | 5 | Sources, conventions et calculs suffisamment explicités |
| **Total** | **100** | |

Les points sont attribués par dimension, pas au prorata du seul nombre de phrases. Une réponse concise peut obtenir tous les points si elle établit les éléments requis.

## 2. Ancres de notation

Pour chaque dimension :
- **100 % des points** : élément correct, complet et justifié.
- **75 %** : élément essentiellement correct ; omission mineure sans effet sur le verdict.
- **50 %** : progrès partiel réel, mais étape importante manquante ou justification incomplète.
- **25 %** : intuition pertinente sans démonstration suffisante, ou résultat seulement partiellement exact.
- **0 %** : absent, faux, contradictoire ou non pertinent.

Les demi-points sont autorisés. L'évaluateur doit conserver une justification courte pour toute dimension notée sous 75 %.

## 3. Erreurs critiques et plafonds

Les erreurs critiques sont des erreurs de validité, pas de style. Elles imposent le plafond indiqué même si le total brut est supérieur.

| Code | Erreur critique | Plafond du cas |
|---|---|---:|
| CE-01 | Résultat central faux ou conclusion incompatible avec les données | 39/100 |
| CE-02 | Preuve invalide présentée comme démonstration, sans reconnaître la lacune | 49/100 |
| CE-03 | Contre-modèle annoncé mais ne satisfaisant pas les prémisses ou ne réfutant pas la propriété | 39/100 |
| CE-04 | Erreur arithmétique qui inverse le verdict ou les comparaisons demandées | 39/100 |
| CE-05 | Inférence causale affirmée à partir des seules fréquences descriptives du cas EXPL | 49/100 |
| CE-06 | Règle RFC inventée ou confusion qui autorise le décodage générique d'un caractère réservé comme `/` | 49/100 |
| CE-07 | Réponse prétendant avoir consulté/exécuté une source, un outil ou un calcul non effectivement consulté/exécuté | 49/100 |
| CE-08 | Omission d'une sous-question explicite qui rend le verdict global indéterminé | 69/100 |

Plusieurs erreurs critiques : appliquer le plafond le plus bas, sans additionner les plafonds. Une simple erreur typographique ou un arrondi raisonnable n'est pas critique si le raisonnement et le verdict restent corrects.

## 4. Exigences minimales par cas

### FORMAL
- Prouver que la surjectivité de f∘g entraîne celle de f.
- Ne pas conclure que g est surjective ni que f est injective.
- Fournir pour chacune des deux propriétés non forcées un contre-modèle entièrement défini et compatible avec les prémisses.
- Le même contre-modèle peut réfuter les deux propriétés si toutes les valeurs pertinentes sont précisées.

### COMPUTE
- Trouver la classe x ≡ 157 (mod 990).
- Justifier la combinaison des trois congruences et l'unicité modulo 990.
- Vérifier séparément les trois congruences.
- Une réponse donnant seulement 157 sans classe générale ni vérification ne peut dépasser 59/100.

### DOC
- Distinguer la casse hexadécimale, le décodage des caractères non réservés et la sémantique des caractères réservés.
- Identifier que `/` est réservé et que `%2F` ne doit pas être décodé génériquement en `/` sans analyse contextuelle.
- Citer correctement les sections pertinentes, notamment RFC 3986 §§2.1, 2.2, 2.3, 6.2.2.1 et 6.2.2.2.
- Distinguer exigence normative et choix propre à une implémentation.

### EXPL
- Recalculer 90 % contre 80 % dans l'hôpital 1 ; 1 % contre 0 % dans l'hôpital 2.
- Recalculer les taux agrégés A = 10/110 = 1/11 et B = 80/110 = 8/11.
- Expliquer le changement de pondération et le renversement.
- Ne pas inférer un effet causal à partir de ces seules données.

### ADV
- Réfuter l'affirmation par une liste finie non vide minimale, par exemple (0, 2).
- Montrer que sa moyenne vaut 1 et qu'aucun terme ne vaut 1.
- Prouver qu'une liste d'un seul terme est égale à sa propre moyenne.
- Donner une propriété correcte, par exemple min(x_i) ≤ m ≤ max(x_i).

## 5. Agrégation et interprétation

- Score de cas : somme des six dimensions, puis application éventuelle du plafond critique.
- Score du jeu : moyenne arithmétique non pondérée des cinq scores de cas ; publier aussi les cinq scores individuels.
- Ne pas masquer un échec critique par une moyenne élevée.
- Publier les désaccords par dimension et par cas, pas seulement un coefficient global.
- Aucun seuil de réussite n'est fixé ici : il doit être préenregistré après calibration inter-évaluateurs, avant toute comparaison de modèles.

## 6. Procédure d'annotation

1. Chaque réponse est anonymisée et présentée dans un ordre randomisé.
2. Deux évaluateurs notent indépendamment chaque réponse sans voir les notes de l'autre.
3. Ils consignent points par dimension, codes d'erreur critique et justification.
4. Un troisième arbitre tranche les désaccords matériels après gel des deux premières grilles.
5. Les évaluateurs ne modifient pas le barème au milieu d'une série. Toute modification crée une nouvelle version et impose de renoter toutes les réponses concernées.
6. Conserver les réponses brutes, grilles individuelles, arbitrages, version du barème et empreintes des artefacts.

## 7. Statut et limites

Ce barème est une proposition de calibration interne. Il n'a pas été validé par un évaluateur humain indépendant, ni testé sur un lot de réponses, ni soumis à une mesure de fidélité inter-évaluateurs. Les plafonds et pondérations doivent donc être revus avant gel. v0.4 reste public et impropre à un test aveugle.
