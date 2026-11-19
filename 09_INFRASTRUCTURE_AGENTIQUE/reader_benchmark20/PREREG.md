# BENCH20 — isoler les erreurs de numérotation sans relâcher la provenance

**Préenregistrement gelé avant création du jeu de test, du code et toute inférence.** 19 novembre 2026.

## Diagnostic issu de BENCH19 (ne pas réévaluer ses réponses)
Le modèle 0,5B avait 20/20 sorties rejetées ; le 3B 11/20. Une partie importante des sorties mélangeait des numéros de lignes sources (9–13) et des nombres naturels 1–5. BENCH19 est conservé comme résultat historique, sans normalisation a posteriori.

## Question
Si le modèle doit sélectionner **des identifiants de choix 1–5**, et que le programme convertit ces identifiants vers des lignes Git exactes 9–13, le taux de sorties acceptées et le score mathématique augmentent-ils **à jeu et modèle identiques** par rapport à la formulation source 9–13 ?

## Cohorte prospective
- **20 nouvelles fiches** distinctes des BF01–BF20. Dix fonctions affines, dix quadratiques, nouveaux paramètres a,b,m,c,d, 5 propositions mathématiques par fiche et nouvel ordre déterministe, fiches et blobs Git gelés avant toute inférence.
- Même structure de proposition neutre dans les deux bras ; oracle de vérité par énumération exhaustive des éléments de Z/mZ. Les masques de vérité sont enregistrés et vérifiés avant le run, jamais transmis aux modèles.
- Tous les golds sont des résultats *synthétiques* vérifiables automatiquement ; cela **n'est pas un benchmark de documents scientifiques réels et ne fournit pas d'annotation humaine indépendante**.

## Étude appariée (2 modèles × 2 interfaces × 20 fiches = 80 générations CPU)
- **SOURCE** : affichage IDs 9, 10, 11, 12, 13 (identique à BENCH19), parsing strict de ces IDs, pas de récupération implicite.
- **ORDINAL** : affichage IDs 1, 2, 3, 4, 5 ; mapping **bijectif et figé** `1→9, 2→10, 3→11, 4→12, 5→13`. Le modèle ne reçoit **jamais les deux espaces de numérotation**. Le modèle ne cite aucun extrait libre ; la citation source est reconstruite uniquement à partir du blob Git et contrôlée par Reader12.
- Chaque modèle reçoit EXACTEMENT les mêmes faits, questions et ordre dans les deux bras. Seuls les identifiants des candidats et leur liste autorisée varient ; le prompt générique reste gelé avant inférence. Cette intervention mesure une **modification d'interface**, pas une amélioration du raisonnement mathématique intrinsèque.
- **Qwen2.5-0.5B-Instruct** et **Qwen2.5-3B-Instruct** officiels en GGUF Q4_K_M, SHAs de BENCH19, même llama.cpp épinglé, 4 threads, contexte 4096, température 0, max 64 jetons de sortie, un appel par couple modèle/interface/fiche, aucun retry, aucune réparation, aucun ajustement au vu des réponses.
- Témoin simple `first3` prenant les premières lignes candidates (indépendant de l'interface) ; témoin `NONE` ; `all5` uniquement couverture.
- Enregistrer toutes réponses brutes (y compris invalides), accusés du gate, tokens, durées, no-candidate, faux positifs, vrai positifs, FN, F1 micro, abstentions, rejets par catégorie, et score par famille.

## Critères gelés
- Primaire **interface** : pour chaque modèle rapporter la paire `SOURCE vs ORDINAL` en **taux de sorties au format valide** et **F1 micro sur les 20 fiches** ; amélioration confirmée localement seulement si ORDINAL réduit strictement les rejets ET améliore strictement le F1. Si un seul des deux critères passe : partiel, non démontré globalement.
- Secondaire : sous ORDINAL, le 3B bat-il simultanément 0,5B et `first3` en F1 ? Rapporter le coût CPU et refus ; aucune certification, aucun Horn, aucune promotion.
- Tous les échecs de gate, corruption du mapping, répétition des IDs, prose/Markdown, réconciliation ambiguë et ID hors ensemble doivent être **fail-closed**.
- Le plafond de trois sélections (contre jusqu'à cinq vérités) est conservé et reflété dans FN.
- Le test doit produire exactement 20 fiches × 4 bras valides techniquement ; sinon `INCOMPLETE`, aucune conclusion mathématique.
- Aucun résultat sur BENCH19 ne peut être rescorré sous les nouvelles règles ; la comparaison causale d'interface doit reposer uniquement sur les nouvelles fiches et deux bras appariés.

## Gardes et limites
Aucune API payante, aucune modification de `main` ni des PR #202/#203, aucune fusion. Les étiquettes sont fixées par algorithme mathématique exact, pas par une personne indépendante. Ne jamais conclure à une AGI, à une compétence scientifique générale ou à une causalité purement due au nombre de paramètres.
