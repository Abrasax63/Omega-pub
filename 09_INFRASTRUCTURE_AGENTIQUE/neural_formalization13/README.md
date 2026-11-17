# Omega 13 — libre proposition de formalisations, puis calcul exact

Le pilote antérieur #172 n'a pu traduire aucune des 60 prémisses FOLIO examinées. Il reste utile comme référence stricte. Cette nouvelle voie accepte des **interprétations proposées par Qwen**, y compris celles qui n'entrent pas dans les règles textuelles du parseur.

## Fonctionnement

Qwen 2.5 Coder 3B (exécuté localement via `llama-server`, sans API payante) reçoit la question originale et les prémisses originales en anglais, **sans labels ni formules FOL de référence**. Il suggère des clauses dans un petit langage typé : faits individuels, implications, existences et exclusions de classes. Le prompt lui demande de laisser de côté toute phrase qu'il ne sait pas représenter, sans compléter artificiellement les hypothèses.

`runner.py` contrôle ensuite **indépendamment** le format, les indices de prémisses, les extraits textuels exacts et les types logiques. Si **toutes** les prémisses et le but sont représentés, le moteur déterministe de #172 cherche un **contre-modèle fini** et vérifie chacune de ses prémisses sur le témoin calculé. Aucun calcul de témoin n'est annoncé lorsqu'une prémisse manque.

Cette chaîne améliore potentiellement la **couverture des propositions de formalisation**, mais elle ne valide pas automatiquement leur fidélité sémantique. Même lorsqu'un contre-modèle est trouvé, il reste **conditionnel aux clauses proposées par Qwen** : `FINITE_COUNTERMODEL_CONDITIONAL_TO_LLM_AST`. Sans contrôle sémantique séparé, ne pas l'interpréter comme un contre-exemple au théorème en langue naturelle.

## Nouveau jeu indépendant de développement

Les **six nouvelles questions FOLIO 79–84** ont été gelées avant le prompt et le code de cette expérience. Deux ensembles de prémisses distincts. Source : [Yale-LILY/FOLIO](https://github.com/Yale-LILY/FOLIO), validation v0.0, commit `5d7bb84c7edab3fb358e057d2807f19cf5cf5e2d`, licence CC BY-SA 4.0. Tranche SHA Git `687571407a6d65dac98d57955d7dc5692139005a`. Aucun tri par réponse ou difficulté.

Le contrôle de référence est le moteur strict #172, **inchangé** ; les deux passent les mêmes six sources. Le protocole comprend un seul appel local Qwen par question, limite de 512 tokens, température 0,2, sans retry pour éviter d'optimiser sur les exemples après observation.

## Mémoire réellement reprise

Avant de traiter ces questions, la CI décompresse le checkpoint versionné de la PR #167 (12 événements réels), en vérifie le hash SHA256, puis ajoute un événement par nouvelle question à une nouvelle copie du journal chaîné. La mémoire étendue est conservée dans l'**artefact** du run, pas automatiquement commitée. Chaque événement reste `PROPOSED` ou `REJECTED_PROVENANCE` ; jamais `VERIFIED`.

Le contenu du journal en sortie peut être restauré pour une exécution ultérieure en réutilisant explicitement son chemin. **Ce n'est pas encore un apprentissage autonome ni une intégration au cycle horaire.**

## Reproduction

```bash
python3 -m unittest discover -s 09_INFRASTRUCTURE_AGENTIQUE/neural_formalization13 -p test_runner.py -v
```

Pour l'exécution neuronale, lancer un `llama-server` à `127.0.0.1:8091` avec le modèle et la version épinglés, préparer un `/tmp/omega13-memory.jsonl` à partir du checkpoint et exécuter :

```bash
python3 09_INFRASTRUCTURE_AGENTIQUE/neural_formalization13/runner.py \
  --ledger /tmp/omega13-memory.jsonl --output /tmp/omega13-raw-report.json
```

Le workflow `omega-neural-formalization13.yml` reproduit ces étapes automatiquement sur GitHub Actions et archive la génération et le journal.

**Interdictions :** aucune fusion, `main` inchangée, aucune altération des PR parentes, aucune promotion scientifique sur simple plausibilité, aucun API payante. Tout correctif après résultat devra être explicitement marqué `POSTHOC` et la cohorte 79–84 considérée comme exposée.
