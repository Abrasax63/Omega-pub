# Omega #94 — échantillon extérieur nouveau, figé avant vérification (16 novembre 2026)

## Cible nouvelle
- Dépôt : `sigstore/rekor` ; identifiant numérique du dépôt GitHub : `272963353`.
- Publication : [v1.6.1](https://github.com/sigstore/rekor/releases/tag/v1.6.1), version publiée le 11 novembre 2026.
- Binaire : `rekor-cli-linux-amd64`. Ce binaire sera téléchargé, jamais exécuté.
- Commit Git cible résolu **avant lecture de la provenance** : `30ae802eec547479bc3334ca92b9e9c4df27d9a5`, depuis l'étiquette annotée `v1.6.1`.
- Workflow de signature présumé à vérifier : `sigstore/rekor/.github/workflows/release.yml` ; le fichier à cette version contient une action d'attestation. Ne pas supposer que l'attestation GitHub est disponible avant l'avoir récupérée et vérifiée.

## Contrat

Geler les identités et reprendre **le même code** `slsa_attestation_pilot.verify_artifact` et `attested_evidence_bridge.select_with_attested_artifact` que pour les tests antérieurs. Budget : 0 lecture de journal d'exécution non disponible, 1 invocation cryptographique supplémentaire dans le raccord. Les branches précédentes `cli/cli` et `sigstore/fulcio` sont des contrôles déjà vus, **pas** un nouveau holdout.

Résultat positif attendu **si** une attestation GitHub SLSA est disponible : `VERIFIED_BUILD_ONLY` pour la provenance du binaire **et** `indéterminé` pour copie/recalcul et vérité scientifique. Un échec de téléchargement, de signature, de politique ou d'absence d'attestation doit rester rapporté comme **indéterminé** ; ne pas remplacer Rekor par une autre publication après lecture.

L'expérience **ne dispose pas d'oracle indépendant sur la correction mathématique ou scientifique** : ne pas rapporter un gain Omega. L'objectif est de tester le transfert du raccord sur une origine réellement nouvelle, pas de confondre disponibilité d'une attestation avec qualité du raisonnement.
