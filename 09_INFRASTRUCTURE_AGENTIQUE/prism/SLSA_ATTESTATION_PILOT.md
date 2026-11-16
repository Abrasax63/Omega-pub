# Pilote SLSA/in-toto de la PR #94 — vérification, pas certification

## Périmètre scientifique

Ce module **n'attribue aucun statut de preuve mathématique** et ne déduit jamais qu'une exécution est indépendante d'une autre. Il cherche uniquement à vérifier cryptographiquement **d'où provient un artefact logiciel**. La présence d'une attestation ne suffit pas : une structure JSON, une empreinte SHA-256 ou un champ `attested: true` ne sont pas des attestations cryptographiques.

Sources normatives vérifiées le 16 novembre 2026 :
- [SLSA v1.2 Build Provenance](https://slsa.dev/spec/v1.2/build-provenance), avec `predicateType = https://slsa.dev/provenance/v1`.
- [Documentation GitHub sur la vérification hors ligne](https://docs.github.com/en/actions/how-tos/secure-your-work/use-artifact-attestations/verify-attestations-offline).
- [Manuel gh attestation verify](https://cli.github.com/manual/gh_attestation_verify) : `--repo`, `--signer-workflow`, `--source-digest`, `--bundle`, `--custom-trusted-root`, `--format json`.

## Composants

- `slsa_attestation_pilot.py` : vérificateur conservateur. Exécute l'outil maintenu `gh attestation verify` dans un sous-processus **sans shell**, et **refuse** tout verdict positif si la commande échoue, si le bundle est absent, si le certificat ne contient pas l'ID numérique attendu du dépôt, si la signature n'a pas été approuvée par GitHub CLI ou si le sujet SLSA ne correspond pas aux octets locaux.
- `test_slsa_attestation_pilot.py` : tests unitaires adversariaux avec sortie `gh` **simulée**. Ils testent le contrôle de politique et la gestion des erreurs, **pas la cryptographie réelle**.
- `.github/workflows/omega-slsa-smoke.yml` : expérience de signature d'un artefact de démonstration sur la branche expérimentale uniquement, sans publication de code, et vérification avec le vrai `gh`. Échec du workflow = vérification non démontrée.
- Aucun changement des mécanismes de classification, de l'autonomie, des PR #81/#83, ou de `main`.

## Vérifier un artefact externe réellement signé

Pré-requis : GitHub CLI récent, artefact local, bundle Sigstore obtenu auprès de la source officielle et racines de confiance récupérées indépendamment. Exemple, avec une provenance préalablement émise pour un artefact du dépôt `Abrasax63/Omega-pub` :

```bash
gh attestation download ./artifact.bin -R Abrasax63/Omega-pub
gh attestation trusted-root > trusted_root.jsonl
# Utiliser le chemin du bundle téléchargé ci-dessus.
python slsa_attestation_pilot.py ./artifact.bin ./bundle.jsonl \
  --trusted-root ./trusted_root.jsonl \
  --repo Abrasax63/Omega-pub \
  --repo-id 1309584710 \
  --signer-workflow Abrasax63/Omega-pub/.github/workflows/omega-slsa-smoke.yml \
  --source-commit LE_SHA_COMPLET_DE_40_CARACTERES
```

Ne jamais inventer un SHA, un nom de workflow ni une racine de confiance. Les racines, chemins et identités doivent être obtenus hors de l'entrée non fiable elle-même.

Pour un usage hors connexion, le bundle et les racines doivent être acquis depuis des sources fiables **avant** la vérification et maintenus à jour ; une origine de racine arbitraire invalide la garantie.

## Sortie et niveaux de confiance

- `VERIFIED_BUILD_PROVENANCE_ONLY` et `signature_verified = true` : le vrai processus `gh` a rendu un code zéro sous les contraintes fixées ; le module a ensuite validé la structure SLSA, l'empreinte des octets de l'artefact et l'identifiant numérique du dépôt dans le certificat certifié. Les champs `claimed_*` de la prédication restent des **déclarations**, pas des faits indépendamment prouvés. Ne pas assimiler une signature valide à un niveau SLSA spécifique.
- `INDETERMINATE`, `signature_verified = false` : outil manquant, échec de commande, racine/bundle indisponible, identité incompatible, résultat vide, incohérence de structure ou de SHA. Aucun résultat scientifique n'est promu dans ces cas.
- `scientific_status = INDETERMINATE` et `origin_independence = NOT_ESTABLISHED` **même si la signature est valide**.

### Frontière de confiance importante

La documentation de GitHub indique que les champs du **certificat** de signature et les horodatages témoins sont protégés ; les champs du **statement/predicate** peuvent être influencés par le workflow appelant. Pour une garantie supérieure, un workflow réutilisable de construction fiable est requis. Le module n'authentifie donc pas `buildDefinition`, `invocationId`, `resolvedDependencies` comme des observations indépendantes.

De plus, `gh --repo` hors ligne compare le **nom historique** du dépôt dans le certificat ; pour les renommages, le contrôle de l'**identifiant numérique** du dépôt est indispensable. Le module refuse une attestation sans identifiant attendu.

## Interprétation pour Omega

Ce pilote représente **une nouvelle source de données vérifiables** pour le laboratoire de provenance. Il n'injecte pas encore de verdict dans le graphe adaptatif de la PR #94 ; ce raccord ne doit être tenté qu'après un cas de signature valide **réel**, une revue de la frontière de confiance, puis un corpus réservé indépendant. Les faux positifs, les échecs de collecte et les contre-exemples doivent être conservés dans le journal.

**Aucune fusion automatique.** La PR reste DRAFT.
