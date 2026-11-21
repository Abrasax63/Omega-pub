# KV-01 — préenregistrement A/B avant toute inférence

Date : 2026-11-21. Question : peut-on économiser des évaluations de tokens
de préfixe dans `llama-server`, sans changer le modèle ni les requêtes ?

## Source et configuration gelées

- Modèle : Qwen2.5-0.5B-Instruct officiel GGUF `Q4_K_M`, URL
  `https://huggingface.co/Qwen/Qwen2.5-0.5B-Instruct-GGUF/resolve/main/qwen2.5-0.5b-instruct-q4_k_m.gguf`.
- SHA256 du poids : `74a4da8c9fdbcd15bd1f6d01d621410d31c6fc00986f5eb687824e7b93d7a9db`.
- Moteur : `llama.cpp` commit `5a4afd80779ba51166b59986e61a0bfbb9e1a4c6`.
- Ces identifiants sont repris de la PR Omega #202, pas choisis après avoir observé les résultats de ce test.
- CPU sur runner GitHub ubuntu-latest, `-t 4`, `-c 4096`, `--parallel 1`, `--host 127.0.0.1`.
- API locale native `/completion`, JSON avec la chaîne de prompt construite à l'identique dans les deux conditions.
- `temperature=0`, `n_predict=16`, `seed=42`, `stream=false`, `id_slot=0`.
- Facteur expérimental unique : `cache_prompt=false` vs `cache_prompt=true`.
- Corpus déterministe de six questions mathématiques très simples avec long préfixe commun
  et fins distinctes. Une requête identique de contrôle est insérée après la série.
- Ordre des quatre blocs : OFF/ON/ON/OFF ; redémarrer le serveur entre les blocs pour
  retrouver un contexte initial vide. Les deux premières requêtes de chaque bloc
  servent à vérifier que les timings de prompt sont rapportés.
- Ne pas ajuster ces conditions à la lecture des résultats.

## Mesures
Pour chaque appel, enregistrer les champs `timings.cache_n`, `prompt_n`,
`prompt_ms`, `predicted_n`, `predicted_ms`, durée HTTP et sortie brute;
enregistrer la disponibilité du serveur, la version des poids/moteur et les erreurs.
Les statistiques OFF et ON excluent le premier appel, identique et nécessaire pour
réchauffer le contexte. Calculer séparément la somme des tokens `prompt_n`, la
somme `cache_n`, le total `prompt_ms`, les différences de sortie exacte et
l'accord sur l'étiquette stricte lorsque la sortie est analysable.

## Critères de succès et limites
- Succès de *réutilisation instrumentée* : ON rapporte `cache_n > 0` sur
  au moins une requête non initiale et moins de `prompt_n` total que OFF,
  au sein du même moteur et du même jeu.
- Conservation des sorties : aucune divergence octet-par-octet après normalisation
  du seul champ de contenu n'est une condition *distincte*, qui peut échouer.
- Si les sorties diffèrent, enregistrer les désaccords, les réponses et l'absence
  de certification. Ne pas déclarer une absence de perte de qualité sur six questions.
- Gain de temps : seulement si les `prompt_ms` rapportés sont plus faibles de
  façon cohérente entre les blocs; aucune conclusion énergétique sans instrument.
- Les tokens `prompt_n` évités ne sont pas équivalents à une estimation directe
  des FLOPs, joules ou coûts facturés par des API externes.
- Si échec de téléchargement, hash, démarrage, réponse ou extraction du timing,
  déclarer `INFRA_FAILURE` ou `MEASUREMENT_UNAVAILABLE`, pas un résultat négatif
  sur la méthode.
- Test sur un modèle dense 0,5B, ne prouve rien sur la qualité d'un MoE Colibrì,
  ni sur un fournisseur distant sans contrôle sur son cache.

## Sûreté
Aucun appel externe de modèle payant, aucune donnée secrète ou personnelle.
Aucune modification de `main` ni du code des lecteurs/vérificateurs scientifiques.
Artefacts bruts et logs même en cas d'échec, pas de fusion automatique.

Référence API du commit épinglé :
https://github.com/ggml-org/llama.cpp/blob/5a4afd80779ba51166b59986e61a0bfbb9e1a4c6/tools/server/README.md
