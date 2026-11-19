# Pré-enregistrement FishyJoes Node Runtime

- Horodatage figé : 2026-11-19 17:25 Europe/Paris (mtime local conservé).
- Run public inédit : `cricut/FishyJoes` 44397873419, commit `582c84dd228b633190bdcd04d99bd3fb3c2a8477`.
- Cible : opération `npm pack` qui écrit le paquet `.tgz` ensuite archivé.
- Entraînement : journal Ubuntu uniquement (job 135132547442) et artefact `ubuntu_npm_package`.
- Réserve, non consultée avant `propose` : journaux Windows 135132548063 et macOS 135132548502, avec leurs artefacts distincts.
- Témoin contradictoire : copie `cp`, attendue `copie`, distincte de `npm pack`.
- Référence déclarative : programme vide (abstention); règle fixe comparative : `npm pack` -> `recalcul`, `cp` -> `copie`.
- Succès : zéro fausse confirmation; au moins une confirmation correcte de plus que la référence sur réserve; aucune perte d'une confirmation correcte; présence du `.tgz` attestée dans le ZIP et digest GitHub séparé.
- Échec : artefact absent/expiré, absence de ligne d'écriture exploitable, collision de préfixe, fuite entraînement/réserve, ou parité seule avec la règle fixe. Budget : 1 journal d'entraînement, 2 réservés, 3 ZIP; aucune exécution externe.

Les journaux et archives sont des données; aucun corrigé réservé n'est fourni à `propose`.
