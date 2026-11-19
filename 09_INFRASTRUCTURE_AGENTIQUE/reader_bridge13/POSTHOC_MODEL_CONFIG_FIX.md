# READER13 — correction d'infrastructure post-hoc (19 novembre 2026)

## Incident reproductible, sans conclusion scientifique
- Run original [44208982479](https://github.com/Abrasax63/Omega-pub/actions/runs/44208982479) : job `source-and-baseline` SUCCESS ; job `qwen-cpu-real-inference` FAILURE.
- Artefact brut `14384718241`, `real-model-report.json` : `ValueError: Unrecognized model in Qwen/Qwen2.5-0.5B-Instruct` pendant `AutoModelForCausalLM.from_pretrained`, avant toute inférence.
- SHA résolue pendant le run : `367ae90eaf97b8d64787d6ee9101a04460b55392`. L'arbre de cette révision ne liste pas `config.json` ; cela explique l'exception (modèle Qwen2 non identifié).
- Arbre public d'une révision antérieure `c89bee90d9f811437d9735454613c35b4a3c4dc8` : `config.json`, tokenizer et `model.safetensors` sont présents ; `config.json` contient `model_type: qwen2` et `architectures: [Qwen2ForCausalLM]`.

## Modification minimale isolée
- Pin immuable sur `c89bee90...` plutôt que `main` mouvant.
- Vérification explicite SHA résolue == SHA pin et présence/contenu du `config.json`, **avant** chargement des poids.
- Refus `MODEL_CONFIG_INCOMPLETE` / `MODEL_REVISION_DRIFT` ; exception conservée dans l'artefact, aucun fallback silencieux.
- Tests unitaires de configurations manquantes ou incohérentes ; même modèle, même prompt, même échantillon BR-R90, même gate et mêmes budgets qu'avant.
- Branche de correction isolée et workflow sur cette branche seulement ; `main` et PR #180 inchangées.

## Statut et critères de validation
Ce correctif est **post-hoc infrastructure**. Il ne crée pas un nouveau holdout ; aucun gain scientifique n'est revendiqué.
La validation exige (1) unit tests PASS, (2) modèle réel chargé, (3) inférences réellement achevées, (4) rapports et citations comparés au témoin mécanique, et (5) zéro certification automatique.

Attention : la cohorte ne comporte que deux sources et les étiquettes de référence ne sont pas indépendantes. Même après succès technique, elle ne démontre ni compétence frontière ni compréhension mathématique autonome.

Sources :
- [Run de l'incident](https://github.com/Abrasax63/Omega-pub/actions/runs/44208982479).
- [Révision défectueuse HF](https://huggingface.co/Qwen/Qwen2.5-0.5B-Instruct/tree/367ae90eaf97b8d64787d6ee9101a04460b55392).
- [Révision complète HF](https://huggingface.co/Qwen/Qwen2.5-0.5B-Instruct/tree/c89bee90d9f811437d9735454613c35b4a3c4dc8).
