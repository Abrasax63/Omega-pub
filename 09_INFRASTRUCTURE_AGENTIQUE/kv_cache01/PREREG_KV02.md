# KV-02 — contrôle post-hoc distinct, préenregistré avant nouvelles inférences

Date 2026-11-21. Après observation de KV-01, le modèle dense 0,5B a
continué les exemples bruts et produit 0/14 réponses conformes au format strict.
On ne modifie pas KV-01, ses prompts ou ses chiffres ; on teste ici un **nouveau
protocole avec format de conversation Qwen** et de nouvelles petites additions.
Ce protocole est **post-hoc par rapport à KV-01**, mais les nouvelles questions,
métriques et paramètres sont figés avant ses propres générations.

## Constance et changement
- Même poids Qwen2.5-0.5B-Instruct Q4_K_M SHA256
  `74a4da8c9fdbcd15bd1f6d01d621410d31c6fc00986f5eb687824e7b93d7a9db`.
- Même binaire llama-server commit `5a4afd80779ba51166b59986e61a0bfbb9e1a4c6`,
  même CPU, -t 4, -c 4096, --parallel 1, serveur redémarré pour chacun des blocs.
- La requête exploite le format de chat Qwen2.5 de base :
  `<|im_start|>system`, `<|im_end|>`, `<|im_start|>user`,
  `<|im_start|>assistant`. Un préfixe système identique inclut
  trois exemples de petites additions ; la question utilisateur varie.
- Six nouvelles additions simples à un chiffre (tous résultats de 0 à 100) :
  2+3, 3+4, 5+2, 6+3, 4+5, 2+6, puis répétition exacte de 2+3.
  Ce corpus **ne constitue pas** un holdout externe, un test de mathématiques complexes,
  ni une validation de compréhension.
- Température 0, `n_predict=16`, seed 42, id_slot 0, stream false.
- Seul facteur ON/OFF : `cache_prompt`. Ordre ABBA : OFF/ON/ON/OFF.
- Contrôles attendus : >0 réponses numériquement exactes dans les deux groupes,
  aucune divergence entre réponses appariées pour témoigner de non-régression
  sur cette petite cohorte ; réduction du nombre de tokens `timings.prompt_n`
  après premier appel et `cache_n > 0` en condition ON.
- Critère quantitatif inchangé : mesure tokens de préfixe, durée `prompt_ms`,
  temps HTTP ; ne conclure ni aux joules économisés ni au coût API.
- Enregistrer toute sortie brute non conforme et toute divergence.
- Protéger le run original KV01 : ne changer aucun de ses fichiers.

## Interprétation
Si le modèle se trompe ou si la sortie diverge, conservation de la trace et
statut prudent. Le format de chat est étudié pour obtenir une qualité non nulle,
mais **la comparaison ON/OFF à prompt identique reste le seul test causal**.
