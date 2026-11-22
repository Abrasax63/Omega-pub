# Omega Learning Hub 01 — regroupement sans fusion aveugle

**22 novembre 2026. PR expérimentale, aucune modification de \`main\`.**

## Objectif

Unifier ce qui était dispersé, sans réécrire les mécanismes existants ni considérer les PR en brouillon comme des capacités déjà actives sur \`main\`.

### Composants effectivement raccordés

- \`../learning_lab/prog_reconstruction_pilot.py\` (PR #232) : client Qwen local et exécution Python restreinte.
- \`../learning_lab/python_curriculum_v2.py\` (PR #233) : messages exacts du compilateur.
- \`../learning_lab/python_mastery_v3.py\` (PR #234) : tests aveugles et conservation de la meilleure proposition.
- \`../learning_lab/verified_python_training_export.py\` (PR #234) : extraction de corrections de programme **déjà** contrôlées.

Le point d'entrée \`hub.py\` vérifie le rapport du run V3 par SHA-256 gelé, réutilise l'exporteur **sans le recopier**, établit un registre chaîné et évalue la préparation à l'entraînement. Il n'exécute ni nouveau LLM ni programme d'entraînement.

### Composants inventoriés mais **non fusionnés et non exécutés**

- AutoResearch / PR #83 : contrôle de budget et de régression ; code sur une autre branche.
- Mémoire scientifique / PR #228 : faits et origine scientifiques, volontairement distincts de la compétence Python.
- TRAIN26 / PR #198 : véritable entraînement LoRA CPU sur SmolLM2-135M, mais **avec contrat mathématique**, pas un jeu de code Python.
- TRANSFER27 / PR #199 : évaluateur de familles nouvelles et corrections vérifiées, également spécifique aux formules mathématiques.

Leur version et leur preuve d'exécution sont renseignées dans \`REGISTRY.json\`. Un pointeur de dépendance **n'est pas une fusion** : avant une vraie composition des modules non fusionnés, il faudrait examiner les importations, licences, sources de données, jobs et contrats d'entrée-sortie, puis adapter seulement la jointure nécessaire.

## Pourquoi l'entraînement Python reste bloqué

Le run réel [#45064696523](https://github.com/Abrasax63/Omega-pub/actions/runs/45064696523) a fourni un rapport V3 vérifié. Le [premier export réel contrôlé](https://github.com/Abrasax63/Omega-pub/actions/runs/45065884789) avait identifié **2 corrections Python admissibles**, sur **2 familles**. Leur validation est faite sur les anciens exemples publics et un ancien mini-examen déjà consommé, pas sur un nouveau benchmark indépendant.

Le hub exige provisoirement **12 familles distinctes et 24 solutions vérifiées**, un benchmark externe neuf et un contrat de données d'entraînement Python séparé. Ces nombres sont des **seuils opérationnels prudents**, pas une garantie qu'un LoRA sera efficace. Le volet entraînement est **désactivé indépendamment de ces seuils** jusqu'à décision et protocole préenregistré séparés.

### Pourquoi ne pas recycler TRAIN26 sans adaptation ?

La fonction \`load_training()\` de TRAIN26 attend des exemples \`TASK=FORMALIZE / REPAIR / CRITIQUE / ABSTAIN\`, avec des cibles \`EXPR:\` / \`ACCEPT\` / \`REJECT\`. L'export Python produit \`TASK=PYTHON_REPAIR\` et du code source complet. Brancher directement l'un sur l'autre ferait échouer l'intégrité des données ou, pire, produirait un entraînement dénué de sens. Le hub bloque explicitement cette connexion.

## Vérifications réelles et frontières de confiance

L'outil accepte **un seul** rapport V3 du run GitHub déjà audité, avec ID, commit et empreinte brute figés. Pour lui fournir des données :

\`\`\`sh
python research/learning_hub/hub.py inspect

python research/learning_hub/hub.py consolidate \
  --report path/to/real-v3/report.json \
  --output path/to/hub-state.json

python research/learning_hub/hub.py verify \
  --state path/to/hub-state.json
\`\`\`

\`consolidate\` vérifie le hash, le format, les versions de code choisies et les tests du programme. Il émet des enregistrements chaînés par SHA256 :

1. provenance du rapport audité ;
2. admission des candidats Python **en quarantaine**, jamais des cas cachés E/F ;
3. décision de blocage de préparation à l'entraînement.

Le chaînage permet de **détecter des modifications accidentelles** après émission. Il ne constitue pas une signature externe ou une preuve qu'un acteur malveillant ne puisse pas régénérer tout le fichier et les hashes. La provenance GitHub/artefact est par ailleurs liée à l'ID et au digest préenregistrés.

Le hub se limite à **un instantané de données** ; il ne devient pas automatiquement un service continu, une mémoire distribuée ni un mécanisme d'entraînement. Les sources dans les autres PR restent disponibles séparément.

## Protocole d'intégration, à confirmer avant diffusion

- 13 nouveaux tests de hub (pinning, tampering, rollback, anti-fuite, blocage), plus tous les tests existants des PR #232–234.
- Travail CI sans modèles, sans clés API payantes et sans droits d'écriture.
- Le CI télécharge le rapport V3 depuis GitHub Actions, vérifie son SHA, produit le snapshot, le valide une seconde fois et l'archive ; ne relance **jamais** l'inférence V3.
- Les travaux d'entraînement et de transfert mathématiques antérieurs sont **cités et audités**, pas recommencés.
- \`main\` n'est pas modifiée, PR en DRAFT, aucune fusion ni promotion scientifique automatique.

## Suite à démontrer

Créer de nouvelles familles pédagogiques de programmation avec sources et licences vérifiées, constituer plusieurs groupes indépendants de corrections réellement produites puis testées, préenregistrer un holdout neuf et choisir un modèle ainsi qu'un contrat de LoRA Python approprié. La comparaison doit inclure modèle original, fine-tuning, mémoire seule, tests de rétention et coût global. **Aucune de ces performances n'est actuellement démontrée.**

### Pointeurs audités

[PR #83](https://github.com/Abrasax63/Omega-pub/pull/83) ·
[PR #198](https://github.com/Abrasax63/Omega-pub/pull/198) ·
[PR #199](https://github.com/Abrasax63/Omega-pub/pull/199) ·
[PR #228](https://github.com/Abrasax63/Omega-pub/pull/228) ·
[PR #232](https://github.com/Abrasax63/Omega-pub/pull/232) ·
[PR #233](https://github.com/Abrasax63/Omega-pub/pull/233) ·
[PR #234](https://github.com/Abrasax63/Omega-pub/pull/234) ·
[AUDIT_REUTILISATION_ETAT_2026-11-22.md](../learning_lab/AUDIT_REUTILISATION_ETAT_2026-11-22.md)
