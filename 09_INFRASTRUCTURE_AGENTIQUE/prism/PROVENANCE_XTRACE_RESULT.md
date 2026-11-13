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

## Dossier externe SageMath

Le [job doc-pdf](https://github.com/sagemath/sage/actions/runs/41538531683/job/125596440060)
s'est terminé avec succès. Le journal Meson indique une copie de
`src/sage/libs/gap/sage.gaprc`. Le [script Meson au commit testé](https://github.com/sagemath/sage/blob/6244e7214a1cb9afe7275954aa9aab779c5494e6/src/sage/libs/gap/meson.build#L24)
corrobore l'opération avec `fs.copyfile('sage.gaprc')`.

Le rejeu des lignes horodatées commençant par `+ ` et des lignes relatives
à cette sortie faisait lever `ValueError: No closing quotation`. La première
ligne fautive était un commentaire dans un diff affiché par le job.
L'extracteur ignore désormais les commentaires et s'abstient si une ligne
de commande est illisible, car elle pourrait masquer un autre écrivain.
Après correction, le vérificateur fixe et le candidat `install -m` rendent
tous deux `indéterminé`. Le format de progression Meson reste à prendre en
charge. Ce cas mesure une erreur de couverture, sans gain de classification.


## Transfert externe BuildKit — 13 novembre 2026

Deux jobs réussis de k3s-io/k3s : [construction](https://github.com/k3s-io/k3s/actions/runs/43477410364/job/132064733608), [réservé](https://github.com/k3s-io/k3s/actions/runs/43477306465/job/132064373779). Journaux GitHub obtenus en lecture seule. Évaluation sur les lignes horodatées portant le préfixe #22, pour les archives `pkg/data/embed/4873afb1a4cbd30b68e17aa817c29eb1d267db562293def3d821141a86355aed.tar.zst` et `pkg/data/embed/f4649b3a5ee76edb0dd43baff97d735cb5de4931190fc214b004eb40d32f77c3.tar.zst` respectivement.

Sur les mêmes lignes, `fixed_verdict(extract(log, output))` s'abstient, car la trace porte le préfixe BuildKit. `extract_buildkit_copy` exige la commande tracée, le retour verbeux avec les deux chemins et la fin réussie de la même étape. `fixed_verdict` et `classify` donnent copie dans les deux cas. La règle synthétisée sur le premier cas est `[{"argv_prefix":["cp","-av"],"verdict":"copie"}]`. Sur chacun des deux journaux, supprimer le retour verbeux conduit à l'abstention. Les contrôles locaux couvrent aussi une confirmation dans une autre étape, une fin absente et une commande répétée. Les 15 tests locaux passent.

Les jobs utilisent la même famille de workflow. Les traces établissent la copie dans l'étape BuildKit ; aucune vérification indépendante du contenu de l'archive finale n'a été effectuée. La règle fixe égale le candidat appris sur ce lot. Le nouvel extracteur est appelé explicitement et n'est pas encore raccordé à la sélection automatique.


## Cycle Meson — 13 novembre 2026

Le [job SageMath doc-pdf](https://github.com/sagemath/sage/actions/runs/41538531683/job/125596440060) déjà recensé a fourni un essai rétrospectif de couverture. Les déclarations `fs.copyfile` au commit `6244e7214a1cb9afe7275954aa9aab779c5494e6` ont servi de contrôle distinct pour le fichier GAP et trois fichiers de documentation. Un adaptateur expérimental normalise uniquement les lignes de progression Meson horodatées de type `[n/m] Copying file PATH` du job réussi vers une observation `meson fs.copyfile PATH`. Le verdict concerne l'opération rapportée, sans vérification des octets finaux.

La référence déclarative contenait `cp -av → copie` et `install -m → copie`. `provenance_cycle.py propose` a reçu un seul exemple annoté (GAP) et a choisi le préfixe `meson` avant création des observations réservées destinées à `check`. Le comparateur fixe classe directement les mêmes événements normalisés. Sur trois chemins réservés distincts du même job et un contrôle sans trace, la référence s'abstient quatre fois. Le candidat et le comparateur fixe donnent chacun trois confirmations correctes et une abstention, sans fausse confirmation. Le drapeau de revue compare à la référence déclarative. La parité avec le comparateur fixe et la réutilisation du même job excluent un gain externe selon le protocole. L'adaptateur et la règle n'ont pas été intégrés. Les 20 tests locaux du répertoire prism passent.

```json
{
  "proposal": {
    "target": [
      "meson"
    ],
    "failure_counts": [
      {
        "prefix": [
          "meson"
        ],
        "false_confirmations": 0,
        "missed_confirmations": 1
      }
    ],
    "rules": [
      {
        "argv_prefix": [
          "meson"
        ],
        "verdict": "copie"
      }
    ],
    "training_fingerprints": [
      "e4da871195eab649153a471dc4fbaedb4f4ed27549133b5808ec1c266c1e9e7b"
    ],
    "baseline_fingerprint": "550b41020fb22671f47706a51e5045a8e6cc3d4cce276c67030af9f8ba6c9f33"
  },
  "check": {
    "cases": 4,
    "baseline": {
      "false_confirmations": 0,
      "correct_confirmations": 0,
      "abstentions": 4
    },
    "candidate": {
      "false_confirmations": 0,
      "correct_confirmations": 3,
      "abstentions": 1
    },
    "recommend_for_review": true,
    "direct": {
      "false_confirmations": 0,
      "correct_confirmations": 3,
      "abstentions": 1
    }
  },
  "sha256": {
    "check": "3a5b01590633e9236b287c179a3a39b106b49d052f0805155455857ad6d5d7be",
    "reserved.json": "6be4188e40cffb72fff4d9c109fcb528d78b9b790d71246a08905920e66f4837",
    "fixed.json": "d0a58a968fc956388553bcd59c0ff9ced85e2e65d0d6ce64ea0236a74e1f6f6f",
    "proposal.json": "7c82d0fb52f2eddd7e8bd87e1acf015f199a831e9ab92b59dc359f9585bc2074",
    "train.json": "c33daba8b660d7996cbbcd6d2ac1e9211cf25ab12f7ea95ff0d6eed6ddbcc1ae",
    "baseline.json": "5013a0ab9c7d2b5f7dd00db1c0f92fdacf28ba34d6388f11ef1542790948cf51",
    "reserved.log": "df95d9352191197cd81f631a7d37e603e22724632f269d990558e02f940553b2",
    "train.log": "b74ff43430092f5618c095ee8b6a98a04fda480edf28a6cdcae9681a59c363fa"
  }
}
```
