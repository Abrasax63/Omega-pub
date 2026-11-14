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


## Cycle CMake — 13 novembre 2026

Collecte GitHub autorisée du nouveau [job curl CM awslc](https://github.com/curl/curl/actions/runs/43485734962/job/132093549032). Le [CMakeLists au checkout](https://github.com/curl/curl/blob/82240c5970411ac8d7916adbd00004fe30d778c5/docs/libcurl/CMakeLists.txt) déclare deux opérations distinctes : génération des pages dans le répertoire de build, puis installation des fichiers générés. Le journal affiche les destinations mais l'événement Installing pris isolément ne suffit pas à classifier la provenance de bout en bout.

Essai contradictoire : l'adaptateur local convertit un événement d'installation en pseudo-commande et fournit un exemple étiqueté copie au sens de l'étape locale. Après `provenance_cycle.py propose`, le préfixe choisi est `cmake --install` avec verdict copie. `check` reçoit ensuite deux événements distincts dont la provenance est indéterminée à partir de la seule observation normalisée et un contrôle sans trace. Le comparateur fixe s'abstient pour ce type de signal. Le candidat émet deux confirmations non étayées et une abstention. La référence et le fixe s'abstiennent trois fois. La cible et l'évaluation portent sur le danger de mélanger la sémantique locale et la provenance de bout en bout. Elles ne démontrent pas que l'installation elle-même n'a pas copié un fichier. Candidat écarté. Jeu réservé et corrigé non publiés. Vingt tests locaux passent.

| Entrée | SHA-256 |
|---|---|
| Construction | d637eade351fe25ea0847317b16d7a0a1d46312df4b1a2c4a56b9e04d520e791 |
| Référence | 5013a0ab9c7d2b5f7dd00db1c0f92fdacf28ba34d6388f11ef1542790948cf51 |
| Proposition | 887abb3e17b4f44d82d8b76556201966125f9c30147a1d4ba1562f86aa90b031 |
| Réservé | 9be239b884f7bff4b13439ca4dcde91b2023c1e4625f88ade96fb0ce3faca7cd |
| Fixe | 8fa86bd6ee1b47d872c2d4663d7c517c7f8514ed30864f902b4b720c0193fa3b |


## Routage des extracteurs — 13 novembre 2026

Sur un [nouveau job K3s](https://github.com/k3s-io/k3s/actions/runs/43476757307/job/132062459438) de la même famille BuildKit, l'extrait des lignes horodatées `#22` jointes par LF a pour SHA-256 `bac44f4af39f6fd468e76ec1e3dfac3a33e13a8906b8c7e0e2aa9112472d0801`. [Le script épinglé](https://github.com/k3s-io/k3s/blob/91b9cf50c12eed08f5e4f175b12eaa81e1dc5d8d/scripts/package-cli#L74) prescrit la copie, et le journal montre la confirmation et la fin de l'étape.

Candidat de routage déterministe évalué localement : appliquer les deux extracteurs existants au même texte. Si les deux signalent un écrivain pour la sortie, s'abstenir. Sinon retenir BuildKit s'il confirme, ou rendre la trace Bash. Sur le journal réel, Bash seul s'abstient, le candidat et BuildKit seul répondent copie. Sur un contrôle synthétique ajoutant une deuxième écriture Bash à la même sortie, Bash et BuildKit seuls répondent copie et le candidat s'abstient. Les 20 tests existants et le contrôle du candidat passent localement. Aucune synthèse de règle annotée dans ce cycle.

La [nouvelle PR K3s et son workflow Install Script](https://github.com/k3s-io/k3s/actions/runs/43502342269) étaient en statut action_required à la collecte. Le test positif porte sur un autre job de la famille déjà étudiée et donne une égalité avec le fixe. Candidat de routage non intégré. Attendre un workflow distinct avec trace et contrôle séparé de l'opération pour mesurer un gain externe.


## Cycle Libtool / Autotools — 13 novembre 2026

Nouvelle famille de workflow. Le [job curl AM awslc](https://github.com/curl/curl/actions/runs/43485734962/job/132093549401) rapporte les commandes Libtool avec chemin source et destination. Le [Makefile.am épinglé au checkout](https://github.com/curl/curl/blob/82240c5970411ac8d7916adbd00004fe30d778c5/lib/Makefile.am) corrobore la construction de libcurl avant l'installation. Pas de contrôle distinct des octets installés. Le verdict porte uniquement sur l'opération rapportée par Libtool, sans inférence sur l'origine du contenu.

Adaptateur temporaire : reconnaître les lignes horodatées dont le message entier est `libtool: install: /usr/bin/install -c SOURCE DESTINATION` avec deux chemins sans espaces et une destination absolue. Le comparateur fixe classe directement ces opérations de copie et s'abstient sinon. Une trace de construction, puis deux sorties réservées distinctes et un contrôle synthétique dont le préfixe Libtool a été remplacé par `checking:`. La référence déclarative `cp -av / install -m` a été fournie à `provenance_cycle.py propose` avant préparation du réservé pour `check`. Le programme a choisi `/usr/bin/install -c → copie`.

Référence : trois abstentions. Candidat et fixe : deux confirmations, une abstention, zéro fausse confirmation dans ce lot. Égalité au fixe, donc aucun gain externe. Candidat et adaptateur non intégrés. Les observations viennent du même job et le code épinglé ne certifie pas chaque sortie. Les 21 tests locaux passent.

```text
log 64fa966e0d73ee02c7c2710b08ca620c559b38b75f518ba0fa88d5d6221374fc
baseline 5013a0ab9c7d2b5f7dd00db1c0f92fdacf28ba34d6388f11ef1542790948cf51
train c604f9cdfda33c117d01e241b41bf34f61816598c9043ffe10bf8a2c3544d745
proposal 8515949c3041d81f71aae0b88673f9c49052a188e36d0799eeec82c79eade81e
reserved 1863733601db42158c6987a220ed1414696b22ecced62504b4b4a5c63db88104
fixed c23fad2c89e43a69c835586b6ef330254286d2310d0c69d15ab1fbadfef988f6
```


## Raccord job–artefact — 14 novembre 2026

Collecte en lecture autorisée des journaux et de la liste des artefacts des runs [K3s](https://github.com/k3s-io/k3s/actions/runs/43476757307) et [SageMath](https://github.com/sagemath/sage/actions/runs/41538531683). Les trois journaux ont été relus pour une question distincte des classifications d'écriture précédentes : associer au job un ID d'artefact publié. Un candidat déterministe croise l'ID et le nom de l'événement horodaté de finalisation avec la liste API du run et exige une correspondance unique. Ce prototype a été testé sur les lignes sélectionnées, avec des données d'un job à la fois. Le comparateur fixe vérifie le suffixe exact de la ligne avec le nom et l'ID attendus dans l'inventaire.

Les deux méthodes relient trois artefacts, pour deux jobs K3s et un job SageMath, alors que la référence actuelle ne produit pas de lien job–artefact. Dans un contrôle synthétique par journal, remplacer l'ID final par 1 force le candidat à s'abstenir. SHA-256 du JSON de session (liste ordonnée K3s Linux, SageMath, K3s Windows, métadonnées API et lignes de finalisation) : `31b1036870fee985afb24a921dd7d9b1311627ba938d64de39462c3468259aad`. Les 21 tests existants passent localement. Aucune règle sur des traces annotées n'a été générée dans ce cycle.

La liste API et le journal sont deux pièces du même fournisseur, et l'archive publiée ne prouve pas par sa seule présence la provenance des octets en amont. Parité avec le fixe sur ce raccord et aucun nouveau workflow admissible pour le verdict copie/recalcul. Candidat non intégré. La décision sur un extracteur reste soumise à une trace d'exécution et à une vérification distincte de l'opération.


## Vérification de la création d'archives — 14 novembre 2026

Nouveau workflow externe [Ninja Linux](https://github.com/ninja-build/ninja/actions/runs/42888784476), jobs 130093749128 et 130093749464, artefacts 13798927618 et 13798982552. Téléchargés via GitHub en lecture autorisée. Les ZIP publiés contiennent chacun le ZIP annoncé par 7-Zip, de même taille que dans le journal. Les deux ZIP internes contiennent une entrée ninja et passent le contrôle CRC. Vérification des octets des archives, sans exécution ni extraction sur disque des binaires. Cette observation porte sur l'emballage, sans verdict sur la compilation ou le recalcul du binaire.

Candidat déterministe local : rechercher dans les messages d'exécution le triplet création, taille, succès, puis joindre le nom et la taille de l'entrée du ZIP publié. Le comparateur fixe vérifie directement les trois lignes avec les mêmes informations d'archive. La référence xtrace s'abstient sur les deux journaux. Le candidat et le fixe rendent deux confirmations chacun et s'abstiennent sur les quatre contrôles dérivés (taille incompatible et marqueur de succès absent dans chaque cas). Les deux architectures constituent des jobs distincts du même workflow. Les 21 tests locaux passent. Aucune annotation d'entraînement ni synthèse de règle dans ce cycle. Égalité au fixe et candidat non intégré.

Empreintes SHA-256, dans l'ordre ZIP publié puis extrait UTF-8 des trois lignes jointes par LF :

```text
635f87c064556b02f3046cd6bd6f7eb17fa6de51aabc51f60e7d73e6b7dd2c86 5f05e7014b9f6b7592ae926b0ddf1ed659ce1af92a62fc9bc291dae43ff0ab21 b'ninja-linux.zip' 145259 ['ninja']
0f749468951e9a10b61abb1a5b91cb67d2959c8455fc25a89b0a4cbb58f889b1 a3610fda54b8b3402fdfe5405596c950814dc7737c96f0f0df47aff22b7cf72f b'ninja-linux-aarch64.zip' 138008 ['ninja']
```
