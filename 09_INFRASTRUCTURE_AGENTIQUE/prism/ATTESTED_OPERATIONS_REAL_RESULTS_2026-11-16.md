# Omega #94 — Expérience prospective signée, copies/recalculs, 16 novembre 2026

## Verdict scientifique et décision

**EXÉCUTÉ (CI réelle), TESTS VÉRIFIÉS, GAIN D'EXACTITUDE NON OBSERVÉ** sur **4 interventions contrôlées**. Comparaison signée vs sélecteur existant sur **exactement la même question** : « copie ou recalcul ? ».

- Référence `provenance_selection.select_verdict` : **3/4** classifications correspondant au plan pré-enregistré ; **1 abstention**.
- Candidat `attested_evidence_bridge.select_with_attested_artifact` : **3/4** ; **1 abstention** ; **4/4 signatures de build validées** ; **4 vérifications cryptographiques supplémentaires**.
- Lecture du journal d'exécution : **4 lectures par bras** (une observation par cas ; techniquement la même trace préchargée est réutilisée, donc ce compteur n'est PAS le nombre de téléchargements réseau).
- Discordances SHA-256 fichier/journal : **0**.
- Certifications scientifiques émises : **0**, **par construction du raccord**, donc ne pas interpréter ce zéro comme mesure indépendante d'un taux de fausses certifications.
- **Différence de précision pour la tâche copie/recalcul : 0/4**. Aucun gain d'adaptation ou de raisonnement démontré. Les quatre contrôles de signature ajoutent un coût ; durée CPU et coût en octets non mesurés séparément.

## Sources vérifiables

- **Protocole de vérité terrain figé avant exécution** : [commit e38119a5](https://github.com/Abrasax63/Omega-pub/commit/e38119a5ef16d1116ee2fd753da89f3576facc07), fichier [ATTESTED_OPERATIONS_PREREG_V1.json](fixtures/ATTESTED_OPERATIONS_PREREG_V1.json).
- **Runner réel** : [GitHub Actions #43821249350](https://github.com/Abrasax63/Omega-pub/actions/runs/43821249350), job `produce-attest-compare` **SUCCESS**.
- **Attestation SLSA réelle pour les quatre fichiers** : [#68002159](https://github.com/Abrasax63/Omega-pub/attestations/68002159). Les octets ont été comparés localement à leurs SHA-256, et `gh attestation verify` a retourné un succès dans les quatre appels.
- **Archive reproductible de 9 pièces** : [artefact GitHub Actions ID 14204731225](https://github.com/Abrasax63/Omega-pub/actions/runs/43821249350/artifacts/14204731225) (expire selon l'API GitHub le **30 novembre 2026 à 07:05 UTC**) : quatre fichiers, journal `producer-xtrace.log`, `compare-report.json`, corrigé figé, bundle signé et racine de confiance.
- **Tests de non-régression** : [RCE prototype tests #43821256242](https://github.com/Abrasax63/Omega-pub/actions/runs/43821256242), **143 tests Prism réussis** ; 7 jobs verts.

## Observations par cas

| Cas | Opération réellement demandée dans le script de production | Corrigé pré-enregistré | Sélecteur #81 | Sélecteur + SLSA | Attestation |
| --- | --- | --- | --- | --- | --- |
| A | `cp seed-a` → `case-a-copy.json` | copie | copie | copie | valide |
| B | `python3 -c` → `case-b-recalc.json` | recalcul | recalcul | recalcul | valide |
| C | `install -m 0644 seed-c` → `case-c-install.json` | copie | copie | copie | valide |
| D | `cp seed-d` → `case-d-hidden.json`, commande volontairement hors de la trace fournie | copie | **indéterminé** | **indéterminé** | valide |

La commande de D apparaît dans la définition publique du workflow (ce n'est pas un secret), mais **n'est pas comprise dans le journal `producer-xtrace.log` donné aux deux méthodes**. La validation pré-enregistrée vient d'une intervention contrôlée, **pas d'un audit extérieur**. On ne peut donc pas estimer une précision générale de 75 % ou déclarer qu'un oracle scientifique indépendant a été acquis.

### Identité des octets vérifiés

- A : `101\n` ; SHA-256 `39b8dc3fc8b44765c8e6f1adee04c5b465e555ab791cc42d0d9e810d5b64297c`.
- B : `506\n` ; SHA-256 `b390d063dd02f23ec6bfa1ccb02f64cdae46f1af2b2c33596b9929a91b8e1747`.
- C : `303\n` ; SHA-256 `38c62c0e8256ed8bcb1b23a308d84d8271d6d77121b6e739a993139ee42fa950`.
- D : `404\n` ; SHA-256 `f8bf41177a5f5e808a7ccb648b51080b031f15ca8018d91a576263d6cc626eb6`.

Tous les hachages calculés directement à partir du ZIP de preuve concordent avec les lignes d'empreintes enregistrées, mais ce contrôle ne démontre pas la réalité de chaque processus au-delà des observations disponibles.

## Analyse du verrou

Une signature SLSA de build relie les **octets** à un **environnement de production déclaré**, suivant les garanties effectives du signataire. Elle ne certifie pas intrinsèquement l'instruction `cp` ou `python` ni ne reconstitue les opérations que le collecteur a omises.

L'expérience est donc une **contre-vérification** de l'idée « ajoutons la signature pour mieux retrouver les copies » : **cela n'a rien amélioré dans le seul cas où la trace manquait**.

Ce que le raccord #94 apporte de réel est une dimension d'intégrité de l'artefact, pas un gain prouvé de classification ou une certification scientifique. La technique reste un sous-module éventuel, sans raison de supplanter le sélecteur #81.

## Préservation et prochain choix

- Conserver la PR #94 en **DRAFT**, séparée de `main`, sans promotion.
- Ne pas proposer un *nouveau* routeur ou un second laboratoire. Pour acquérir un oracle d'origine indépendant, il faudra instrumenter une autre source vérifiable (ex. attestation détaillée du workflow de production ou trace d'appel système indépendante des xtraces) et faire examiner le protocole par un autre vérificateur, sur une cohorte **nouvelle**, préenregistrée, non utilisée pour le développement.
- Critère de décision : réduction des fausses confirmations **sans perte de bonnes décisions**, en comptant les abstentions et **tous** les coûts (lectures, signatures, CPU, réseau), face à la référence #81 et à une méthode classique forte. Arrêter si gain nul ou absence de labels crédibles.

Sources : [SLSA Build Provenance](https://slsa.dev/spec/v1.2/build-provenance) ; [GitHub actions/attest](https://github.com/actions/attest).

**Statuts :** code implémenté ; expérience GitHub exécutée ; quatre provenances cryptographiques vérifiées ; classification 3/4 vs 3/4 sur cas construits ; bénéfice scientifique **INDÉTERMINÉ / NON DÉMONTRÉ**.
