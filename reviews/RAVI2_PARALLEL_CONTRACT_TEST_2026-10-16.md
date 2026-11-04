# RAVI-2 — test parallèle des contrats machine-lisibles

Date : 16 octobre 2026.

## Protocole

Deux copies indépendantes du miroir v1.3 officiel ont été créées. Les **30 tables préexistantes** du miroir sont restées identiques dans les deux copies ; seules deux tables de test ont été ajoutées à chaque branche. `PRAGMA integrity_check=ok` et aucune erreur de clé étrangère n'est détectée.

Aucune modification n'a été faite à la base principale ni au miroir v1.3 officiel.

## Branche A — formalisation stricte

Pilote sur **11 contrats** couvrant V19, Mealy et les briques affines.

Le moteur teste l'inclusion des préconditions typées, les implications numériques (`L=3 => L>=2`, `q=5 => q>=3`), des adaptateurs explicites (`C5 => CYCLE`, représentation affine exacte => groupes d'équations) et des gardes conditionnelles.

Résultat :
- **8/8 dépendances réelles** du pilote sont vérifiées ;
- **5/5 contrôles négatifs** restent non vérifiés ;
- **2 dépendances** nécessitent une garde explicite : `INCOMPATIBLE_INPUT_ONLY` et `JOINT_EMPTY`.

Cela révèle une lacune réelle du schéma v1.3 actuel : une composition peut être valide seulement sur une branche logique. Le contrat doit donc pouvoir porter une **garde**, une **substitution/interface map** et une **base de vérification**.

## Branche B — découverte exploratoire aveugle

Les identifiants de toutes les briques ont été retirés des textes avant le classement. Les **40 `DEPEND_DE`** existants servent uniquement à l'évaluation après calcul.

Population : 75 cartes, soit 5 550 couples dirigés.

### Baseline lexicale
- rappel@30 : **0.125**
- rappel@100 : **0.425**
- rappel@300 : **0.825**
- rappel@1000 : **0.925**
- rang médian : **148.0**
- rang moyen : **356.45**

### Heuristique structurée générique
- rappel@30 : **0.100**
- rappel@100 : **0.400**
- rappel@300 : **0.650**
- rappel@1000 : **0.875**
- rang médian : **158.0**
- rang moyen : **417.88**

L'heuristique structurée générique fait **moins bien** que la baseline lexicale. Elle est donc rejetée comme moteur de certification.

## Conclusion

Le test soutient une architecture **hybride** :

1. **Certification / composition** : contrats stricts, typés, audités, avec gardes et substitutions explicites.
2. **Découverte** : moteur séparé de ranking qui ne produit que des candidats.
3. **Promotion scientifique** : jamais issue du score de découverte ; elle exige preuve/calcul et contre-tests indépendants.

Le prochain développement rationnel est d'étendre progressivement la formalisation stricte, domaine par domaine, plutôt que de tenter de formaliser automatiquement les 71 cartes d'un seul coup.