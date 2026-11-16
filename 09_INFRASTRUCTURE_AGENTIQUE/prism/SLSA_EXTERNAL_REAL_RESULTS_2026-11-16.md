# Omega — attestations externes GitHub CLI & Fulcio (16 novembre 2026)

## Verdict

**VÉRIFIÉ :** deux artefacts publics provenant de deux dépôts externes ont été validés cryptographiquement avec racine Sigstore, certificat OIDC de GitHub Actions, workflow signataire épinglé, SHA-256 local et commit source pré-enregistré. Sur chacun, un artefact altéré et un identifiant numérique de dépôt falsifié ont été **refusés**.

**NON DÉMONTRÉ :** indépendance scientifique, exhaustivité des dépendances, exactitude mathématique du code, gain de fiabilité du routage adaptatif Omega, supériorité sur GitHub CLI. Les deux bras partagent **le même vérificateur cryptographique GitHub CLI**, la valeur ajoutée du pilote est la politique supplémentaire et la reconstruction explicite des liens déclarés.

## Sources et historique de l'exécution

- [Protocole fixé avant exécution](SLSA_EXTERNAL_PROTOCOL_2026-11-16.md), commit [5e03c20b](https://github.com/Abrasax63/Omega-pub/commit/5e03c20b818b24cdcdd4810c46a8f3bdc5ae8a2e).
- [Premier run externe #43812730487 — 3 jobs réussis](https://github.com/Abrasax63/Omega-pub/actions/runs/43812730487) : deux attestations externes acceptées, quatre refus attendus. Le premier export ne retenait pas le champ `gitCommit` des dépendances et a été **corrigé explicitement**.
- [Run de non-régression et de traçabilité #43813153282 — 3 jobs réussis](https://github.com/Abrasax63/Omega-pub/actions/runs/43813153282), version au commit [3c6bf612](https://github.com/Abrasax63/Omega-pub/commit/3c6bf612ddd8c869f58c4c420f839a1049437ea1). Les vérifications cryptographiques et les quatre refus adversariaux sont encore réussis.
- [CI module Prism #43813128054](https://github.com/Abrasax63/Omega-pub/actions/runs/43813128054) : **128/128 tests réussis**, dont assertions sur les champs `gitCommit` et l'abstention scientifique.

Les données brutes des sorties `gh attestation verify`, des verdicts Omega et des deux refus par projet se trouvent dans les artefacts de run de la seconde campagne. Les données de la première campagne sont conservées dans [run #43812730487](https://github.com/Abrasax63/Omega-pub/actions/runs/43812730487) ; la nouvelle campagne n'est pas un holdout inédit, mais une correction traçable.

## Résultats pour les deux logiciels externes

| Mesure | GitHub CLI | Fulcio |
| --- | --- | --- |
| Dépôt certifié par GitHub | `cli/cli`, ID `212613049` | `sigstore/fulcio`, ID `341596960` |
| Version / artefact | `v2.62.0` / `gh_2.62.0_linux_amd64.tar.gz` | `v1.10.0` / `fulcio-linux-amd64` |
| SHA-256 artefact vérifié | `41c8b0698ad3003cb5c44bde672a1ffd5f818595abd80162fbf8cc999418446a` | `92092b98fbb78ec24585982f970367a734ac8ab035fde42df05ef9b0c48cb07d` |
| Workflow revendiqué par le statement signé | `.github/workflows/deployment.yml@refs/heads/trunk` | `.github/workflows/release.yml@refs/tags/v1.10.0` |
| Lien d'exécution revendiqué | [Actions #11840704330](https://github.com/cli/cli/actions/runs/11840704330) | [Actions #42711651597](https://github.com/sigstore/fulcio/actions/runs/42711651597) |
| Commit source de la référence GitHub, également **déclaré** dans SLSA | `cd3f2ad064fbeca17d330e321fef0591eaa0fea5` | `172a6d44c839cbd152a6b9e3fc41b1b66c2710e4` |
| Dépendances déclarées par l'attestation | 1 | 1 |
| Attestation officielle `gh` | Acceptée | Acceptée |
| Politique Omega | `VERIFIED_BUILD_PROVENANCE_ONLY` | `VERIFIED_BUILD_PROVENANCE_ONLY` |
| Contrefaçon d'artefact / ID de dépôt | Refus / refus | Refus / refus |

### Graphe de dépendances reconstruit à partir des déclarations signées

```
Artefact CLI (SHA256 41c8...)
  → workflow déclaré cli/cli/.github/workflows/deployment.yml
  → source déclarée git+https://github.com/cli/cli@refs/heads/trunk
    gitCommit = cd3f2ad064fbeca17d330e321fef0591eaa0fea5

Artefact Fulcio (SHA256 9209...)
  → workflow déclaré sigstore/fulcio/.github/workflows/release.yml
  → source déclarée git+https://github.com/sigstore/fulcio@refs/tags/v1.10.0
    gitCommit = 172a6d44c839cbd152a6b9e3fc41b1b66c2710e4
```

Chaque attestation comporte **un** `resolvedDependencies` dans le statement ; aucune dépendance *déclarée* n'est commune. Cela ne démontre **pas** l'absence de dépendances réelles communes : ces listes ne sont ni exhaustives ni indépendamment attestées. Le champ `gitCommit` conserve la bonne famille de hachage de commit Git, et ne doit pas être converti artificiellement en `sha256`.

### Comparaison de politiques

- Référence `gh attestation verify` : valide la signature, le sujet local et la politique de dépôt/workflow/source.
- Pilote Omega : délègue la même cryptographie à `gh`, puis vérifie notamment l'identifiant numérique du dépôt et analyse `buildDefinition.resolvedDependencies` sous une **frontière de confiance explicite**.
- Gain mesuré de certification scientifique : **non évaluable**.
- Gain démontré d'identification de dépendances au-delà du statement : **aucun** ; Omega fait pour l'instant une lecture structurée des déclarations déjà disponibles.

## Décision de non-promotion

La PR #94 reste `DRAFT`, empilée sur la PR #81 ; **aucune modification de `main`**. La prochaine comparaison scientifique doit établir si une collecte de provenance attestée réduit de véritables fausses confirmations sur un corpus externe pré-enregistré, à coût comparable face à un baseline fort. Les mêmes artefacts ne peuvent pas être réutilisés comme nouvel ensemble réservé.

## Sources normatives

- https://cli.github.com/manual/gh_attestation_verify
- https://slsa.dev/spec/v1.2/build-provenance
- https://slsa.dev/spec/v1.2/verifying-artifacts
