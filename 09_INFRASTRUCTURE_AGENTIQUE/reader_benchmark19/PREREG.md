# BENCH19 — évaluation mathématique sur structures finies, comparaisons appariées

**Préenregistré avant la constitution des données, du code et des appels modèles.** 19 novembre 2026.

## Question
Quand les propositions à sélectionner ont toutes la même forme et les mêmes mots, Qwen2.5-3B-Instruct Q4_K_M identifie-t-il plus de **propositions vraies** concernant une fonction finie que Qwen2.5-0.5B-Instruct Q4_K_M et que le choix mécanique des trois premières propositions ?

## Population/holdout
- **20 fiches synthétiques nouvelles** de fonctions f de Z/mZ dans Z/mZ, 10 fonctions affines et 10 quadratiques, paramètres et ordres verrouillés dans CASES_SPEC.json **avant toute génération** ; algorithme de création déterministe, identités et énoncés sans annotation visible.
- Sources rendues en Markdown à partir des paramètres figés ; chaque proposition dans une section « Énoncé » est numérotée exactement par le lecteur et **tous les candidats ont une formulation neutre « Proposition : ... »**. Aucun token « résultat », « hypothèse » ou « vrai/faux » dans la liste de propositions.
- Cinq propositions standardisées par cas, ordre contrebalancé et déterministe à partir du manifeste : f est injective ; f possède au moins un point fixe ; f(f(0))=c ; f(1)=d ; f est involutive (pour tout x f(f(x))=x). Le c,d sont figés comme valeurs numériques dans CASES_SPEC.json ; aucune vérité n'est calculée par le modèle et les valeurs ne sont pas adaptées après résultats.
- Oracle hors-modèle : calcul exhaustif des n valeurs de f, injectivité, point fixe, involution et vérification directe des deux évaluations f(f(0)), f(1). **Le vrai/faux est contrôlable indépendamment des textes produits par un modèle.** Vérifications de cohérence de génération, de provenance et tests de perturbation d'équation.
- **Attention** : ce ne sont pas des extraits de documents réels. Il n'y a **aucune annotation externe/humaine indépendante**, malgré la vérification algorithmique de la vérité. Ce protocole teste la sélection de propositions vraies en mathématiques finies, pas la compréhension de publications réelles ni l'aptitude AGI.

## Interfaces verrouillées
- Une liste de cinq lignes proposées, chaque ligne provenant d'un blob Git gelé et contrôlé par Reader12 `gate`, jamais d'affirmation mathématique écrite par le modèle.
- Prompt strict commun, figé avant inférence, **nouveau par rapport à Reader18** : choisir au maximum trois numéros de propositions **mathématiquement vraies**, sinon `NONE`, sans justification, sans texte additionnel. La consigne complète est enregistrée dans `PROMPT.txt` avant inférence.
- Un appel glouton (température 0), plafond de 64 tokens de sortie, par fiche et modèle : **40 appels CPU sans retry**, enchaînés successivement sur le même runner, un modèle chargé à la fois, 4 threads, contexte 4096, même version de llama.cpp (commit 5a4afd80779ba51166b59986e61a0bfbb9e1a4c6), même format Q4_K_M.
- Poids officiels SHA256 : 0,5B `74a4da8c9fdbcd15bd1f6d01d621410d31c6fc00986f5eb687824e7b93d7a9db`; 3B `626b4a6678b86442240e33df819e00132d3ba7dddfe1cdc4fbb18e0a9615c62d`. Mêmes hashes testés dans Reader18 #202.
- Trois témoins sans modèle : `first3` (règle lexicale/positionnelle), `NONE`, `all` (référence de couverture ; ne respecte pas le maximum 3). Ne pas utiliser le gold dans la sélection du témoin.
- Le parseur strict, la quarantaine et le principe de refus des IDs fictifs (`999`) sont réutilisés sans relâcher la sûreté.

## Evaluation et critère gelé
- Archiver par fiche : ID/blobs Git, famille fonctionnelle, paramètres, candidats, masque de vérité de l'oracle, messages envoyés, réponse brute, tokens, latence, positions retenues, rejets, abstentions, TP FP FN, précision/rappel/F1, nombre de promotions/certifications (doit rester à 0).
- Si plus de 3 propositions sont vraies, le maximum 3 reste appliqué : publier ce plafond dans le résultat et ne jamais masquer les FN. Scores micro et scores séparés par famille, 20/20 fiches requises.
- **Succès local préenregistré** : F1 micro 3B strictement supérieur au F1 du 0,5B ET au F1 du témoin `first3`. En parallèle, rapporter les faux positifs et les échecs de parsing ; ne pas transformer un échec scientifique en « succès CI ».
- Un cas non exécuté, hash manquant, erreur infrastructure ou refus de provenance invalide le bilan primaire : statut `INCOMPLETE` ou `INFRA_FAILURE`.
- No paid API. Séparer le temps d'inférence du temps d'installation/téléchargement. `main` inchangée, pas de fusion, pas de promotion, aucune règle Horn.

## Interprétation limitée
Les 20 cas ne suffisent pas à attribuer causalement une différence à la **taille seule**, car modèles et poids sont distincts ; pas de calibration multiple, pas d'estimation de généralisation à toutes mathématiques. Les textes/masques ne doivent jamais être retouchés après inférence. Une étude ultérieure sur documents réels annotés humainement et indépendamment sera nécessaire ; ne pas la présenter comme déjà faite.
