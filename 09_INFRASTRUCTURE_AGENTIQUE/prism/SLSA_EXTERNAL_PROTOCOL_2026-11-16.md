# Omega — vérification d'attestations étrangères, protocole pré-exécution (2026-11-16)

Objectif : contrôler **deux artefacts de deux dépôts extérieurs** et lire les dépendances *déclarées* dans leurs attestations SLSA, avant tout raccord au système de décision Omega. Aucun fichier binaire téléchargé ne sera exécuté.

## Échantillon et identité gelés

1. `cli/cli`, release `v2.62.0`, artefact `gh_2.62.0_linux_amd64.tar.gz`, taille annoncée 13 065 800 octets, commit source issu de la ref GitHub `cd3f2ad064fbeca17d330e321fef0591eaa0fea5`, repository ID `212613049`, signataire `cli/cli/.github/workflows/deployment.yml`. Documentation de la provenance : https://github.com/cli/cli#verification-of-binaries.
2. `sigstore/fulcio`, release `v1.10.0`, artefact `fulcio-linux-amd64`, taille annoncée 51 024 868 octets, commit source de l'étiquette annotée `172a6d44c839cbd152a6b9e3fc41b1b66c2710e4`, repository ID `341596960`, signataire `sigstore/fulcio/.github/workflows/release.yml`. Documentation de la provenance : https://docs.sigstore.dev/certificate_authority/verify-release/.

Les SHA de commits sont récupérés des références GitHub du dépôt source, pas des déclarations contenues dans les attestations. Les identifiants numériques des deux dépôts ont également été recherchés indépendamment des bundles.

## Méthode et comparateur

- Télécharger les binaires de release publiés sans les exécuter.
- Télécharger leurs attestations depuis l'API GitHub avec `gh attestation download -R REPO`.
- Installer la racine de confiance via `gh attestation trusted-root` et vérifier localement la signature et l'identité cryptographique avec la CLI officielle `gh attestation verify`.
- Comparer au pilote Omega `slsa_attestation_pilot.py`, qui exige en sus l'ID numérique du dépôt, l'identité du workflow, le commit et l'empreinte locale. Référence et Omega utilisent le même moteur cryptographique : leurs résultats **ne sont pas deux preuves indépendantes**. L'écart recherché est le refus d'une identité incorrecte, pas une augmentation arbitraire du nombre de signatures.
- Lire les `resolvedDependencies` (si présents) dans le statement validé et comparer les URI et empreintes *déclarées*. **Une dépendance déclarée dans un statement signé n'est pas nécessairement exhaustive ni indépendante du signataire**.
- Tests adversariaux : modifier un octet de l'artefact ; remplacer l'ID de dépôt. Le résultat doit être négatif. Un 403, 404, bundle absent ou format différent donne `INDETERMINATE`, jamais "absent de provenance".

## Décisions préfixées

- La vérification d'un artefact atteste **l'origine de build sous la politique imposée**, pas la conformité de son code à une spécification et encore moins la vérité de résultats scientifiques.
- Un résultat positif sur un seul artefact ne prouve pas un gain Omega ; deux artefacts de dépôts distincts ne constituent pas deux reproductions scientifiques indépendantes.
- Le cas d'échec reste visible. Aucun remplacement a posteriori par un artefact opportunément favorable ; toute correction d'intégration doit être versionnée.
- `main` et les PR #81/#83 restent inchangées ; PR #94 toujours DRAFT ; aucune API LLM payante.

## Sources

- https://cli.github.com/manual/gh_attestation_verify
- https://slsa.dev/spec/v1.2/build-provenance
- https://slsa.dev/spec/v1.2/verifying-artifacts
