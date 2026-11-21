# SCALE-01 — capacité Omega : états, données, paramètres et mémoire

**Prototype expérimental, en lecture seule, sans modification de `main` et sans API payante.**

Ce banc réunit de façon **non destructive** deux techniques déjà testées isolément :
- réemploi *exact* de préfixes de trajectoires microscopiques selon [GLUE-CACHE-01 / PR #222](https://github.com/Abrasax63/Omega-pub/pull/222) ;
- réemploi de préfixes d'inférence locale `llama.cpp` selon [KV-READER18 / PR #220](https://github.com/Abrasax63/Omega-pub/pull/220), sous garde de qualité et avec cache OFF comme référence.

Le calcul exact et la classification LLM sont **séparés**. Le cache LLM n'est *pas* activé par défaut : [KV-EXT01 / PR #221](https://github.com/Abrasax63/Omega-pub/pull/221) a confirmé une divergence de classification malgré les économies de calcul. Aucune décision de classification non contrôlable ne peut être promue par ce prototype.

## Réglage concret

| Domaine | Options | Choix conservateur |
|---|---|---|
| Recollement exact | `ExactGluingRouter("off"\|"on"\|"adaptive")` | `off` tant que le profil réel n'a pas été mesuré ; `adaptive` pour systèmes récurrents après qualification |
| Cache KV LLM | `cache_prompt=false/true` pendant un test A/B | `false` en opération ordinaire ; `true` uniquement en environnement d'essai qualifié |
| Taille de modèle | Qwen2.5-0.5B / 3B Q4_K_M | Choisir d'après mémoire réellement mesurée et F1, pas d'après le seul nombre de paramètres |
| RAM | `VmHWM` du serveur Linux + plafond expérimental de 6 GiB | Arrêter si plafond dépassé ; ne jamais confondre poids GGUF et RAM totale |
| Provenance | Git blobs figés, `paired.one_case()` et contrôle `gate` | Obligatoires, identiques OFF/ON |

### Calcul exact à témoins
`witness_cache.py` est recopié **sans modification de logique** de la PR #222 (commit source `de3bec0329e2a9a82b3ec7625a0b20c5b9b9b5e2`). `exact_router.py` ajoute trois modes, dont un mode **adaptatif** ne construisant des entrées de cache qu'après une deuxième demande sur le même `(T,π)`. Les compteurs rendent visibles les calculs et la mémoire supplémentaires.

Test : n=8,32,128,512 états, 24 requêtes par taille et profil, mots de longueur 12. Profils `repeated` (même système) et `unique_systems` (système renouvelé à chaque appel). Comparer 3 sorties **objet par objet**, témoins et premiers préfixes impossibles compris. Les garde-fous exhaustifs de #222 (jusqu'à n=4, 232 748 cas) sont rejoués.

### Modèle et données
`model_scale.py` appelle les **mêmes six documents Reader18** en flux de tailles 6,12,24. Un flux plus long représente *davantage d'appels* et pas **davantage de documents uniques ni de tokens dans la fenêtre de contexte**. Deux modèles quantifiés et épinglés, serveur redémarré à chaque bloc OFF/ON/ON/OFF. Les paires doivent être identiques en entrée ; toute différence de sortie ou de sélection est publiée, pas corrigée.

Mesurer `model_weight_file_bytes`, `server_peak_rss_kib` (`VmHWM`), `prompt_n`, `cache_n`, `prompt_ms`, tokens générés, durée d'inférence et temps complet y compris démarrage, F1, faux positifs et abstentions. Les 84 comparaisons appariées par modèle donnent la détection de régression *locale*, pas la validité générale.

## Pourquoi cela ne suffit pas à « faire tenir davantage de paramètres »

Le cache KV accélère le **calcul du contexte**, mais ne supprime pas les matrices de poids du modèle. Passer de 0,5B à 3B modifie les poids et la RAM ; aucune des expériences actuelles ne montre que le cache KV permet de charger un 7B ou 14B impossible à charger sans cache. Les hypothèses de quantification, buffers, activations, KV cache, implémentation et environnement doivent être vérifiées.

**Aucun 7B/14B téléchargé.** Les limites seront étudiées de façon incrémentale seulement si les ressources vérifiées le permettent. Le stockage de données par compression réversible de témoins est une autre piste distincte : non livré par ce test.

## Comment reproduire

```bash
python -m unittest discover -s 09_INFRASTRUCTURE_AGENTIQUE/scale01 -p 'test*.py' -v
python 09_INFRASTRUCTURE_AGENTIQUE/scale01/bench_finite.py --output /tmp/omega-scale01/exact/report.json
# Pour inférence réelle, lancer le workflow GitHub avec les deux GGUF au SHA256 épinglé.
```

[Workflow GitHub](https://github.com/Abrasax63/Omega-pub/actions/workflows/omega-scale01.yml) : 1 job de contrôle exact + 2 jobs d'inférence CPU (0,5B / 3B). Les sorties brutes et statistiques sont conservées pendant 14 jours. **Aucun merge automatique.**

## Critères avant incorporation

Ne considérer `adaptive` pour le recollement que si le témoin exact est préservé sur toutes les charges, et qu'un gain subsiste malgré les allocations de cache à une charge réelle représentative. Ne considérer le cache LLM que sur tâches dont la sortie peut être validée indépendamment, après tests sur documents externes nouveaux, mesure des divergences, et interrupteur de retour arrière.

Enfin, comparer **l'empreinte mémoire maximale**, pas seulement la baisse de tokens préremplis ; intégrer une politique de capacité et de mise en quarantaine des caches.
