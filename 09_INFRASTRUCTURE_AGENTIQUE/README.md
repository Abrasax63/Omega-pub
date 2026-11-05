# Infrastructure agentique native

**Statut :** PROPOSITION D'ARCHITECTURE — non implémentée  
**Version :** 0.1  
**Date :** 2026-11-05

## Objet

Ce module définit comment les agents de recherche deviennent des composants natifs d'Omega-pub. Ils ne constituent pas un laboratoire parallèle et ne possèdent pas une mémoire scientifique concurrente : ils consultent le référentiel commun, produisent des travaux traçables et soumettent leurs propositions aux procédures de validation déjà définies par RAVI-2.

L'objectif central est l'**auto-référence scientifique contrôlée** : un agent doit pouvoir retrouver les résultats, les sources, les preuves, les contre-exemples, les expériences et les interventions d'agents antérieurs, puis citer précisément les éléments réutilisés.

Ce document décrit une architecture cible. Il ne prétend pas qu'un moteur de contexte, une base de données ou une orchestration multi-agent sont déjà déployés.

## Principes non négociables

1. **Mémoire unique, vues multiples.** Les agents consultent le même référentiel ; leurs contextes sont adaptés à leur mission, mais les identifiants et versions des connaissances restent communs.
2. **Trois espaces épistémiques distincts.** Connaissances internes certifiées, travaux internes expérimentaux et connaissances externes restent séparés, même lorsqu'ils sont reliés.
3. **Provenance de bout en bout.** Toute affirmation réutilisée doit pointer vers sa source, sa version et, si possible, un extrait ou un emplacement précis.
4. **Pas de certification par répétition.** La reprise d'une affirmation par plusieurs agents ne constitue pas une confirmation indépendante.
5. **Écriture par proposition.** Un agent peut déposer un résultat candidat, un rapport ou un contre-exemple ; il ne peut pas promouvoir seul un contenu au statut certifié.
6. **RAVI-2 reste l'autorité méthodologique.** Cette infrastructure outille RAVI-2 ; elle ne duplique ni ne remplace ses protocoles.
7. **Pas de mélange des domaines.** Une relation entre deux axes de recherche doit être déclarée et justifiée ; une analogie ne devient pas une dépendance formelle.
8. **Confidentialité par défaut.** Les contenus privés, secrets, données personnelles et sources non autorisées ne sont jamais injectés dans un contexte destiné à un agent externe.

## Composants proposés

| Composant | Responsabilité |
|---|---|
| Research Context Engine | Constituer un paquet de contexte versionné pour chaque mission |
| Knowledge Resolver | Résoudre les IDs, versions, dépendances et références |
| Provenance Ledger | Enregistrer les sources, activités, agents et dérivations |
| Agent Registry | Décrire les rôles, versions, capacités et droits des agents |
| Research Index | Recherche exacte et sémantique dans les contenus autorisés |
| Literature Connectors | Interroger des sources bibliographiques externes |
| Proposal Inbox | Recevoir les résultats candidats sans toucher au référentiel certifié |
| Validation Bridge | Transmettre les propositions aux contrôles RAVI-2 applicables |

## Cycle général

1. La mission est définie avec un objectif, un périmètre, des critères de sortie et des limites.
2. Le Context Engine recherche dans les trois espaces et construit un paquet de contexte avec références exactes.
3. L'agent consulte ce paquet et peut demander des compléments ; chaque accès significatif est journalisé.
4. L'agent produit un artefact et un manifeste de provenance.
5. Les autres agents peuvent examiner ou contester cet artefact, en déclarant leurs dépendances au travail antérieur.
6. Les propositions sont soumises au processus de validation RAVI-2.
7. Après décision documentée, le référentiel est mis à jour ; les versions antérieures restent traçables.

## Documents du module

- [Contrat du moteur de contexte](CONTRAT_CONTEXT_ENGINE.md)
- [Contrat de mémoire et d'auto-référence](CONTRAT_MEMOIRE.md)
- [Modèle de provenance](MODELE_PROVENANCE.md)
- [Feuille de route et critères d'acceptation](ROADMAP.md)
- [Schéma JSON d'un événement de recherche](schemas/research-event.schema.json)

## Limites de cette version

Cette proposition ne choisit pas encore une base de données, un moteur vectoriel, un orchestrateur, un fournisseur de modèles ou une infrastructure cloud. Ces choix doivent découler d'un audit des outils déjà disponibles, de la charge réelle, des contraintes de coût et de la sécurité. Aucun calcul, preuve ou résultat scientifique n'est modifié par la création de ce module.
