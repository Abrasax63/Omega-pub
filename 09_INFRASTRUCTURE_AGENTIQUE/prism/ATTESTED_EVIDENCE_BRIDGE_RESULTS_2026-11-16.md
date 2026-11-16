# Omega #94 — Raccord attestations signées → sélection de preuves (16 novembre 2026)

## Ce qui existait déjà : aucun nouveau solveur nécessaire

- [PR #76](https://github.com/Abrasax63/Omega-pub/pull/76) a déjà démontré, sur un modèle fini de provenance, qu'un artefact miroir compté comme une confirmation distincte peut changer un verdict ; il ne s'agissait pas d'un oracle externe universel.
- [PR #81](https://github.com/Abrasax63/Omega-pub/pull/81) fournit déjà le sélecteur `provenance_selection.select_verdict` pour les traces `copie/recalcul`.
- [PR #83](https://github.com/Abrasax63/Omega-pub/pull/83) fournit un verrou d'évaluation pour une promotion éventuelle. Il n'est pas fusionné.
- [PR #94](https://github.com/Abrasax63/Omega-pub/pull/94) vérifiait déjà les attestations SLSA de fichiers logiciels et extrayait des dépendances de build déclarées.

Le seul nouveau raccord est `attested_evidence_bridge.py` (et ses tests). Le sélectionneur original n'est **pas modifié**.

## Interface, budget et interdits

L'entrée est la paire **(ensemble de pièces / fonction de lecture du sélecteur existant)** plus **(octets exacts d'un artefact, bundle SLSA, racine de confiance, dépôt et ID numérique, workflow signataire et commit cible)**.

1. `select_verdict` fournit `operation_from_untrusted_log = copie/recalcul/indéterminé`, sans changer sa politique historique. Les journaux restent non authentifiés par SLSA.
2. `verify_artifact` relit **les octets réels** du fichier et fait vérifier cryptographiquement les attestations par GitHub CLI ; un simple JSON `signature_verified:true` n'est jamais accepté en remplacement.
3. Le raccord refuse de relier un fichier si le nom de sortie et le nom du fichier sont incompatibles. Même si un journal déclare le SHA-256 exact et que la signature est valide, cela établit au mieux **une concordance déclarée par le journal**, pas une preuve cryptographique que la commande a produit ce résultat.
4. Il calcule `routing`, une *suggestion* pour la prochaine vérification (chercher la trace, refaire une signature, contrôler l'indépendance). Il ne lance aucune action.
5. `scientific_verdict = INDETERMINATE` et `scientific_independence = NOT_ESTABLISHED` pour **toutes** les entrées. Aucune promotion, aucun changement de statut d'un théorème.
6. Coût conservé dans la sortie : `log_read_count` et `signature_verification_attempts` séparés ; on ne prétend pas que le coût de la cryptographie est nul ni interchangeable avec une lecture de journal.

## Tests reproductibles

- [CI Python #43814947667](https://github.com/Abrasax63/Omega-pub/actions/runs/43814947667) : **138/138 tests Prism**, dont 10 tests spécifiquement consacrés au raccord. Cas contradictoires : signature absente, empreinte incohérente, observation contradictoire, sortie non reliée au fichier, budget insuffisant, fichier manquant, absence de journal.
- [Workflow externe #43815102001](https://github.com/Abrasax63/Omega-pub/actions/runs/43815102001) : 2 artefacts déjà étudiés (`cli/cli` et `sigstore/fulcio`) donnent `VERIFIED_BUILD_ONLY`, **0** classification positive de `copie/recalcul` (journaux de production absents), **0** certification scientifique.
- [Nouveau protocole pré-enregistré pour Rekor](ATTESTED_SELECTOR_FRESH_REKOR_PROTOCOL_2026-11-16.md), commit [e4de58f6](https://github.com/Abrasax63/Omega-pub/commit/e4de58f61a10e88f3e4efe5ada04a26d815aa83b).
- [Workflow externe #43815365926](https://github.com/Abrasax63/Omega-pub/actions/runs/43815365926) : **trois** artefacts de release vérifiés, dont **un nouveau dépôt jamais utilisé pour ce raccord** : `sigstore/rekor v1.6.1`, binaire `rekor-cli-linux-amd64`, commit source annoncé `30ae802eec547479bc3334ca92b9e9c4df27d9a5`. Le commit correspond à la référence GitHub résolue avant la lecture SLSA.
- Ce même run refuse les trois modifications de contenu post-signature et trois IDs numériques de dépôts falsifiés : **6 refus attendus**, journalisés. Les comparaisons de dépendances signées passent ; aucune origine scientifique indépendante n'a été déduite.

**Important :** le run #43815365926 comporte **deux contrôles déjà vus** et **un seul nouveau dépôt**. Ce n'est **pas** une cohorte de 15–20 dossiers scientifiquement validés. Les succès de signature et les refus négatifs ne mesurent **aucune amélioration du raisonnement d'Omega**.

## Tableau de décision

| Question | Comparateur existant #81 | Nouveau raccord #94 | Conclusion |
| --- | --- | --- | --- |
| Une trace prouve-t-elle une opération copie/recalcul ? | Peut classer si trace exploitable | **Même classification** sur les mêmes pièces ; aucune promotion | 0 gain démontré de classification |
| Les octets d'un artefact ont-ils une provenance de build signée ? | Non couvert par #81 | Oui, si GitHub CLI valide la signature et les identités épinglées | Nouvelle *dimension de confiance*, déjà vérifiée sur des artefacts réels |
| Deux calculs scientifiques sont-ils indépendants ? | Non établi | Non établi | **Indéterminé** |
| Le système prend-il moins de mauvaises décisions ? | Référence non mesurée sur ce nouveau critère | Aucune vérité terrain scientifique disponible | **Non mesurable à ce stade** |

## Blocage encore présent et prochaine expérience vraiment discriminante

Le problème restant est de lier **l'observation des commandes** (journaux) à **l'artefact signé** (SLSA), à partir de sources authentifiées et avec un oracle d'origine *indépendant*. Sur ces trois releases, les attestations vérifiées prouvent une origine de construction, **mais pas quelle commande brute a produit le binaire**. Les comparateurs ne répondent pas encore à la même question scientifique.

La prochaine expérience devrait être une cohorte **préenregistrée de dossiers comportant les deux types de preuves**, le même budget total de lectures/vérification et un oracle indépendant sur copie/recalcul, miroirs et reproductions distinctes. Rejeter l'hypothèse d'avantage si le raccord ne réduit pas les fausses confirmations face au sélecteur existant et à une politique classique forte. Si le corpus reste impossible à construire, arrêter l'intégration plutôt que multiplier des simulations favorables.

**Décision :** conserver le raccord en PR #94 DRAFT, sans fusionner `main`, sans changer le sélecteur ni le cycle autonome.
