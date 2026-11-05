# Module — Extraction et réutilisation des méthodes

**Statut du module : PILOTE EXPÉRIMENTAL**  
**Date : 2026-11-04**

## Objet

Extraire de travaux mathématiques existants des instruments réutilisables — lemmes, constructions, invariants, réductions, schémas de preuve et procédures de vérification — sans confondre cette extraction avec une validation du résultat source.

Le module est testé sur le dossier C4, L=2. Il ne modifie aucun statut scientifique existant.

## Chaîne de traitement

1. **Identifier la source** : dépôt, version, document, code, date et provenance.
2. **Normaliser l'énoncé** : objet, définitions, hypothèses, conclusion et périmètre.
3. **Extraire l'instrument** : isoler le mécanisme mathématique réutilisable et ses préconditions.
4. **Reproduire** : exécuter le code source disponible sans le modifier, enregistrer la commande et l'environnement.
5. **Vérifier séparément** : seconde implémentation ou preuve reconstruite, avec comparaison des sorties.
6. **Attaquer** : variante de définition, cas limite, hypothèses omises, canonisation, dépendances.
7. **Décider** : attribuer un statut scientifique et un statut de publication distincts.

## Fiche minimale d'un instrument

- Identifiant et version.
- Source primaire et provenance.
- Énoncé exact / opération exacte.
- Hypothèses et préconditions.
- Domaine de validité et limites.
- Preuve ou justification.
- Implémentation de référence et empreinte.
- Vérification indépendante et empreinte.
- Contre-tests et variantes réfutées.
- Dépendances.
- Niveau de nouveauté bibliographique : NON ÉVALUÉ tant qu'une revue de littérature n'a pas été menée.
- Statut scientifique et statut de publication.

## Règles de non-promotion

- Une exécution réussie ne prouve que les sorties du programme dans son périmètre.
- Deux programmes concordants ne valident pas automatiquement la définition mathématique qu'ils encodent.
- Un témoin sous une spécification opérationnelle ne valide pas l'équivalence de cette spécification avec une définition primaire non retrouvée.
- Un résultat expérimental ne devient pas certifié par son simple transfert dans ce module.
- Les fichiers historiques sont conservés ; aucune source n'est remplacée silencieusement.

## Pilote

Voir [PILOTE-EXT-C4-L2-2026-11-04](../../02_MATHEMATIQUES/defauts_recollement/PILOTE_EXTRACTION_C4_L2_2026-11-04.md).

Le pilote est une démonstration de la chaîne documentaire et de vérification, pas une nouvelle certification du résultat C4.
