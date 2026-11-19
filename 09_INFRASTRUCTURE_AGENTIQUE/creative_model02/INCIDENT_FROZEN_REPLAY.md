# CREATIVE02 — correction de chemin pour rejouer exactement les propositions déjà figées

19 novembre 2026. **Pas de nouvelle inférence. Pas de nouveau prompt. Pas de réglage du juge.**

Le [run original #44498942756](https://github.com/Abrasax63/Omega-pub/actions/runs/44498942756) a exécuté les tests offline (SUCCESS) et trois appels réels Qwen3B (SUCCESS), puis déposé les réponses **avant correction** sous l'artefact GitHub #14515959746, `omega-creative02-raw-qwen-proposals-before-gold`.

Le job de correction a échoué pour **erreur de chemin**, et non pour résultat mathématique : après téléchargement, le ZIP contient `creative02-model/frozen-proposals.json` ; le script cherchait `frozen-proposals.json` directement. Le bon chemin est donc `/tmp/creative02-inference/creative02-model/frozen-proposals.json`.

Ce correctif ne touche **ni le modèle, ni ses trois messages bruts, ni le protocole ni le parseur, ni les cas, ni les seuils**. Il ajoute un workflow **séparé, sur une branche distincte**, qui télécharge **explicitement l'artefact du run historique #44498942756** via `actions/download-artifact@v4` (`run-id=44498942756`, `name=omega-creative02-raw-qwen-proposals-before-gold`). Puis il appelle le `grade.py` original hérité, sans lancer `propose.py`.

Les sorties brutes de trois appels contiennent des blocs Markdown `\`\`json` plutôt que du JSON nu, interdits explicitement par le protocole. Les objets internes peuvent aussi être sémantiquement faux ; il ne faut pas nettoyer, réparer ou parser les blocs post-hoc pour sauver le score. Le juge doit retourner trois `ABSTAIN_INVALID_PROPOSAL` et conserver l'erreur `RESPONSE_NOT_EXACT_JSON`, pas trois réussites.

Ce document est une **chronologie causale d'un incident technique**, et non un nouveau préenregistrement ni une permission de réajuster le modèle. La validation peut être rapportée comme négative même si le workflow réparé est vert.

**Implication** : le verrou immédiat est la fiabilité de la génération structurée et du contenu mathématique. Une future expérience séparée pourra éventuellement mesurer, prospectivement, un mode de génération JSON contraint ; les mêmes sorties ne doivent pas être réparées rétroactivement et comptées comme succès. `main` inchangée.
