# Essai sur des journaux GitHub Actions

Run 43480869950, jobs build 132076679364 et reserved 132076679324. Les cinq fichiers ont la même empreinte SHA-256. Le premier run a détecté des octets différents dus à un échappement de fin de ligne ; le run retenu a été produit après correction.

Lancer provenance_xtrace.py avec les deux journaux bruts dans l’ordre build, reserved. Le candidat est construit sur deux traces annotées puis évalué sur trois sorties distinctes du même workflow. Sur ces trois sorties, la règle fixe qui lit la même trace et le candidat donnent chacun une copie, un recalcul et une abstention attendue. Aucun gain sur la règle fixe. La règle à marqueurs explicites de la PR #79 s’abstient sur ce format.

Les deux comparateurs partagent un extracteur écrit pour ce corpus. Le comparateur fixe connaît l’expression exacte du fixture. L’essai est contrôlé, avec une collecte des journaux opérée dans la session, et ne valide ni un nouveau format externe ni une amélioration autonome inter-cycle. Le candidat basé sur les préfixes peut confondre deux programmes ayant le même préfixe.

## Cycle du 13 novembre 2026 — copie avec install

Workflow contrôlé distinct, [run 43489499229](https://github.com/Abrasax63/Omega-pub/actions/runs/43489499229), jobs build 132106598355 et reserved 132106598328. L'extracteur de référence et le candidat ont lu les mêmes journaux récupérés via GitHub. Le candidat apprend sur `train.json` en mode 0644 et est testé notamment sur une copie en mode 0600. Les quatre sorties ont la même empreinte. Le cas à deux écritures est volontairement ambigu pour ce protocole à écrivain unique.

Avant, la copie install était manquée et le dossier à deux écritures était traité comme une écriture unique. Après, la copie est reconnue et les cas à écritures multiples ou sans trace donnent indéterminé. La règle fixe étendue donne les mêmes résultats que le candidat. Les traces proviennent d'un workflow contrôlé ; la collecte a été effectuée dans la session. Aucun transfert externe ni avantage de l'apprentissage n'est établi.

```json
{
  "digest": "b390d063dd02f23ec6bfa1ccb02f64cdae46f1af2b2c33596b9929a91b8e1747",
  "rules": [
    {
      "argv_prefix": [
        "install",
        "-m"
      ],
      "verdict": "copie"
    }
  ],
  "rows": [
    {
      "case": "copy",
      "expected": "copie",
      "before": "indéterminé",
      "after": "copie",
      "fixed": "copie"
    },
    {
      "case": "conflict",
      "expected": "indéterminé",
      "before": "copie",
      "after": "indéterminé",
      "fixed": "indéterminé"
    },
    {
      "case": "hidden",
      "expected": "indéterminé",
      "before": "indéterminé",
      "after": "indéterminé",
      "fixed": "indéterminé"
    }
  ],
  "logs_sha256": {
    "build": "216b2c83b22326862243174e83bad0e1e5f1a464edb0918350988a442aaf330b",
    "reserved": "5fccddd8aa04da1db3bacc994e12ae06e44f1f13e0df4e155e30638847d62545"
  }
}
```

## Transfert externe — 13 novembre 2026

Journal brut du [job Static gate](https://github.com/nexu-io/open-design/actions/runs/38714250159/job/116353498714) du dépôt nexu-io/open-design, obtenu via l'accès GitHub autorisé. SHA-256 de la réponse texte UTF-8 : d332b40fd16fdc424d4d82a6d45be7a34442a2016e6cee150346278d3c372c19. Le premier run externe envisagé, 29481239283, renvoyait HTTP 410 à la demande du journal.

Comparaison à journal identique, sans réentraînement. Pour `/usr/local/bin/actionlint` et `/usr/local/bin/shellcheck`, appeler `extract(log, output)`, puis `fixed_verdict(trace)` et `classify(trace, {("install", "-m"): "copie"})`. Zéro écrivain reconnu et verdict indéterminé pour les deux sorties, avec les deux méthodes.

Le journal contient le script de l'étape affiché par GitHub Actions, mais aucune trace xtrace reconnue pour les deux appels install. La régression vérifie que l'affichage seul laisse le résultat indéterminé. Ce transfert ne mesure donc aucune confirmation hors du corpus contrôlé. La prochaine évaluation exige un workflow externe montrant les commandes effectivement exécutées, avec des cas à verdict vérifiable.

Candidat évalué puis écarté : supprimer les séquences de couleur et transformer les lignes horodatées commençant par `sudo install -m` en lignes `+ install -m`. Sur la ligne externe isolée (source affichée, exécution non observable dans cet extrait), la référence s'abstient, le candidat conclut copie. La trace positive de contrôle `+ install -m 0755 actionlint /usr/local/bin/actionlint` est reconnue par l'extracteur existant. Le candidat élargit donc les confirmations sans établir l'exécution et n'est pas intégré. Les 12 tests locaux du répertoire prism passent.
