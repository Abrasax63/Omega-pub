# Omega — SLSA signé, vérifications positives et adversariales (16 novembre 2026)

## Statut

**EXÉCUTÉ / VÉRIFIÉ (provenance d'artefact de démonstration uniquement)**. La validation scientifique et l'indépendance d'exécution demeurent **INDÉTERMINÉES**. Exécution sur branche isolée de la PR #94, sans fusion de `main` ni accès LLM payant.

## Sources directement vérifiables

- [GitHub Actions #43811359196](https://github.com/Abrasax63/Omega-pub/actions/runs/43811359196), job `attest-and-verify` (ID **133113515602**) : **SUCCESS**.
- [Attestation #67981883](https://github.com/Abrasax63/Omega-pub/attestations/67981883), signée via Sigstore public et enregistrée dans le journal de transparence Rekor, selon les journaux du workflow.
- [Commit testé 41bf400b](https://github.com/Abrasax63/Omega-pub/commit/41bf400b12122e83fcb72351c0668bf268f27d74).
- [Tests CI #43811364813](https://github.com/Abrasax63/Omega-pub/actions/runs/43811364813) : sept jobs réussis, notamment **120/120 tests du module Prism**, dont 16 nouveaux tests de politique SLSA avec exécuteur `gh` simulé.
- Première attestation réelle préliminaire : [run #43811134327](https://github.com/Abrasax63/Omega-pub/actions/runs/43811134327), [attestation #67981488](https://github.com/Abrasax63/Omega-pub/attestations/67981488).

## Preuve expérimentale

Artefact sans valeur sensible `omega-slsa-smoke.txt`, contenu attendu `omega-slsa-provenance-smoke-v1\n` ; SHA-256 affiché dans les logs :

`ff011cebc7f00a34546cc55a3707c7a4819cac6171b939bea37b1020959a3442`.

Le workflow a généré un bundle SLSA via `actions/attest@v4`, récupéré une racine de confiance avec `gh attestation trusted-root` puis exécuté `slsa_attestation_pilot.py`. Celui-ci a délégué la vérification cryptographique à `gh attestation verify` en exigeant `--bundle`, `--custom-trusted-root`, `--repo`, `--signer-workflow`, `--source-digest`, `--cert-oidc-issuer` et `--format json`. Le pilote a vérifié en sus le SHA-256 local et l'identifiant numérique du dépôt dans le certificat.

Les journaux du job démontrent :

| Essai réel | Verdict attendu | Observation |
| --- | --- | --- |
| Artefact original signé, paramètres de dépôt/workflow/commit fixés | Autoriser uniquement la provenance de build | `Signed build provenance verified; scientific proof NOT established` (exit 0) |
| Artefact modifié APRÈS la signature | Refuser | `Expected refusal: GH_VERIFICATION_FAILED` (exit contrôlé non nul) |
| Artefact intact mais ID numérique de dépôt falsifié (`9999999`) | Refuser | `Expected refusal: SIGNED_STATEMENT_POLICY_MISMATCH` (exit contrôlé non nul) |

La création de l'attestation et la contre-vérification sont effectuées au sein du **même workflow** : ce n'est **pas** une vérification scientifique indépendante et ce n'est **pas** un holdout externe.

## Limites et décision

- Ne pas confondre signature valide et certitude sur `runDetails` ou `buildDefinition`, contenus pouvant être influencés par le workflow signataire. Ne pas attribuer de niveau SLSA à partir de la simple existence de l'attestation.
- Ne pas utiliser le champ `invocationId` du statement pour conclure à des exécutions scientifiquement indépendantes.
- Aucun gain du routage adaptatif de la PR #94 n'est démontré ; le [contrôle extérieur précédent](BENCHMARK_EXTERNAL_REPORT_2026-11-16.md) reste **BENCHMARK_INSUFFISANT**.
- La preuve est pour le **module de collecte et vérification cryptographique**, pas pour un agent qui découvre des preuves ni qui auto-améliore sa programmation.
- Suite recommandée : comparer des attestations **réellement externes** et auditer leurs dépendances, en conservant une règle d'abstention face aux liens manquants. Ne modifier ni la référence existante ni `main` tant que cette évaluation n'est pas terminée.

**Conclusion certifiée par les logs visibles :** un contrôle cryptographique réel a fonctionné pour un artefact créé par Omega et a refusé deux altérations contrôlées, mais la plus-value scientifique d'Omega reste indéterminée.
