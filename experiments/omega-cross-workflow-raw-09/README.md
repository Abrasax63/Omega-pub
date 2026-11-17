# OMEGA-CROSS-WORKFLOW-RAW-09 — liaisons entre vraies archives ZIP et journaux GitHub

**Une progression du laboratoire de données de la [PR #171](https://github.com/Abrasax63/Omega-pub/pull/171).** Le pilote précédent générait 4 sous-processus dans un seul job. Ici nous utilisons **7 ZIP de vrais artefacts GitHub Actions** et **les logs réels des jobs de 5 runs existants** de quatre familles de workflows (#159, #169, #170, #171).

Les identifiants des runs et artefacts sont *préenregistrés* avant l'implémentation au commit `4a665830b38f133ab903882748029123c6b33389` ([protocole](PREREG_2026-11-17.md)). Ce ne sont pas des runs scientifiques cachés ou inconnus lors du choix du jeu de données ; seuls leurs octets bruts n'ont pas été examinés avant la programmation.

## Les trois étapes indépendantes

1. `collect` : le runner GitHub utilise uniquement `actions:read` pour télécharger des ZIP et des logs depuis les API publiques réelles ; il conserve leurs bytes, leurs SHA256, les URLs de provenance et la vérité GitHub **dans un artefact de gold séparé**. L'entrée brute donne à l'agent des ZIP sous noms opaques, leur **artifact ID de transport sans run ID**, et des logs sous des noms opaques. Il n'est pas possible de deviner le run d'un ZIP à partir du seul hash sans une assertion du fournisseur.
2. `infer` : un autre job, sans gold, cherche uniquement les URLs explicites de téléchargement d'artefact présentes **dans les lignes des logs GitHub authentiques**. Une URL `.../actions/runs/NNN/artifacts/MMM` associe un run à un artefact ; jamais le SHA de commit, le nom ou les bytes identiques. Un ZIP sans lien explicite provoque une **abstention**. L'agent n'affirme pas que les résultats scientifiques sont indépendants.
3. `score` : troisième job, disposant du corrigé, recalcule le nombre de vrais liens, leur justesse, les abstentions et les erreurs d'un comparateur `NAME_ONLY`. Il rejette toute fausse origine ou prétention à une preuve scientifique.

Le générateur ajoute **deux contrôles de transport synthétiques**, distincts des archives réellement téléchargées : une copie binaire d'un ZIP avec le même artifact ID, puis une copie binaire d'un autre ZIP dont l'ID est omis. Ils doivent donner respectivement **miroir** et **abstention**. Les 7 ZIP d'origine restent intacts.

## Commandes de test

```bash
python -m unittest discover \
  -s experiments/omega-cross-workflow-raw-09 \
  -p 'test_cross_raw.py' -v
```

La commande de collecte demande un `GITHUB_TOKEN` de workflow disposant de `actions:read`, mais **aucune API LLM payante**. Elle est exécutée **dans GitHub Actions uniquement**, sur le chemin `pull_request`. Le chemin `push` exécute les 14 tests adversariaux **sur des ZIP et journaux synthétiques**, sans télécharger les données réservées.

**Périmètre :** il s'agit de réconciliation de métadonnées **trouvées dans les journaux** avec les octets de vrais ZIP. L'ID d'artefact est donné comme numéro de transport, pas comme label de run. Il n'y a **aucune extraction magique d'une origine depuis un résultat mathématique**. Deux workflows distincts peuvent partager un même SHA ou les mêmes paramètres ; cela ne constitue **pas** une réplication scientifique indépendante.

**Sécurité :** la vérité est seulement cachée au job `infer`, non aux personnes qui peuvent consulter les artefacts GitHub du dépôt public. Les liens de logs sont une donnée du fournisseur, non une attestation cryptographique complète. Aucun accès aux secrets ni déploiements protégés, aucune fusion ni modification de `main` ou CORE.

**Suite utile :** vérifier la qualité des calculs eux-mêmes (code, inputs, seed, résultats, bibliothèques) à partir de ces ZIP, puis construire un vrai benchmark hors-échantillon dont la vérité n'était pas connue lors du développement.
