# Prototype RCE — lecture seule

**Version :** 0.1.0  
**Statut :** prototype local expérimental, non intégré à un orchestrateur multi-agent.

## Ce que fait cette version

Le prototype lit un checkout local d'Omega-pub et produit un paquet de contexte JSON adapté à un rôle d'agent. Il utilise uniquement la bibliothèque standard Python.

- Lit l'index global et le registre transversal.
- Préserve séparément statut scientifique source et statut de publication.
- Classe prudemment les fiches référencées comme `experimental_internal` tant qu'une certification explicite n'est pas interprétée par un validateur dédié.
- Sépare les dossiers en attente de migration des fiches présentes.
- Recherche lexicalement dans les documents locaux (`.md`, `.py`, `.lean`, `.json`, `.yaml`, `.yml`, `.toml`, `.csv`).
- Produit des extraits avec numéros de ligne, chemins, termes correspondants et avertissement sur les confirmations circulaires.
- Adapte les priorités et consignes au rôle : chercheur, réfutateur, formaliste, computationnel ou bibliographe.
- Émet un manifeste avec horodatage, couverture et empreinte SHA-256 du paquet.

## Ce que cette version ne fait pas

- Aucun accès réseau ni recherche bibliographique externe.
- Aucune recherche vectorielle ou sémantique.
- Aucun appel de modèle ou orchestration d'agents.
- Aucune écriture dans les index ou fiches scientifiques.
- Aucune certification ou modification de statut.
- Aucune lecture des fichiers absents du checkout local.
- Aucun accès automatique aux données privées d'autres espaces.

La recherche lexicale fournit des **candidats documentaires**, pas des dépendances scientifiques. Les liens de dépendance ne sont pas inférés à partir de la proximité textuelle.

## Utilisation

Depuis la racine d'un checkout Omega-pub avec Python 3.10+ :

```bash
python 09_INFRASTRUCTURE_AGENTIQUE/prototype/rce.py \
  --repo . \
  --question "Quelles hypothèses et contre-exemples concernent les graphes forcés P1 P4 ?" \
  --role refuter \
  --output /tmp/omega-context.json
```

Pour afficher le JSON dans le terminal, omettre `--output`.

Rôles disponibles : `researcher`, `refuter`, `formalist`, `computational`, `bibliographer`.

## Tests

Depuis le dossier du prototype :

```bash
python -m unittest -v
```

Les tests couvrent le parsing des tables, la conservation des statuts, la séparation des dossiers en attente et l'absence de modification des fichiers sources.

## Exemple d'intégration multi-agent

L'orchestrateur appelle le RCE une fois par mission et par rôle, puis transmet le JSON à l'agent concerné. Tous les agents doivent conserver les mêmes identifiants et versions de sources. Leurs paquets peuvent différer par le classement et les extraits, mais les références sous-jacentes restent traçables.

Un agent doit citer `path` et `line_start/line_end` des extraits ou l'identifiant/version d'une fiche. Il ne doit jamais citer un autre agent comme preuve primaire si la source racine est disponible.

## Prochaine étape après validation du prototype

1. Tester sur un clone complet et comparer les résultats aux recherches manuelles.
2. Ajouter une résolution explicite des dépendances déclarées dans les fiches.
3. Ajouter un index persistant dérivé, reconstructible et versionné.
4. Brancher des connecteurs bibliographiques externes avec leurs propres provenance et dates de consultation.
5. Exposer une API stable à l'orchestrateur multi-agent.

Aucune de ces étapes futures n'est prétendue réalisée dans la version 0.1.0.
