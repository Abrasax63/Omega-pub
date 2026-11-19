# OMEGA-READER15 — ablation modèle Qwen 0,5B contre Qwen Coder 3B

**Préenregistrement avant implémentation, 19 novembre 2026.**

## Hypothèse
Sur les deux documents BR-R90 déjà exploités, Reader14/Qwen2.5-0.5B a répondu deux fois `NONE` et conservé zéro conclusion. Le petit modèle peut manquer de capacité pour ce choix, ou le protocole lui-même peut pousser à l'abstention. On teste un modèle plus grand et **différent (Coder)** sans changer les textes, candidats, critères de scoring ni le prompt et le gate de Reader14.

## Cohorte, référence et statuts
- Base exacte : [PR #183](https://github.com/Abrasax63/Omega-pub/pull/183), dernier état avant cette branche `f4bb0dd0480d64355deeb22c8ecb829e2caa8d39`. Ne pas changer `selector.py`, `test_selector.py`, `GOLD_PROVISIONAL.json`.
- Corpus identique et **vu** : BR-R90-01 `478ca7c518ed1368a0bf35deb5f9be160bba581d`, BR-R90-02 `0a9f6bab0b91a93f8fcc831c39a988171c169eb5`.
- Modèle test : `Qwen/Qwen2.5-Coder-3B-Instruct-GGUF` quantifié `q4_k_m`, binaire llama.cpp source SHA `5a4afd80779ba51166b59986e61a0bfbb9e1a4c6`, fichier `qwen2.5-coder-3b-instruct-q4_k_m.gguf` SHA256 `724fb256bec1ff062b2f65e4569e871ad2e95ab2a3989723d1769c54294730b7`. Empreintes reprises d'un pilote Omega antérieur #174.
- 1 requête par document ; température 0, au plus 64 jetons générés ; même chaîne system/user que Reader14. Pas d'API payante ; llama-server en localhost uniquement.
- Le seul output accepté reste une liste stricte d'au plus 3 numéros présents dans les candidats Reader14 ou `NONE` ; programme reconstruit les citations via Git blob puis gate de Reader12.
- Contrôles Reader14 : sélection de tous les candidats et premiers trois candidats. Les deux réponses brutes du 0,5B sont archivées dans l'artefact [14506395106](https://github.com/Abrasax63/Omega-pub/actions/runs/44474710529/artifacts/14506395106).
- Mesures : authentification modèle/code par SHA, durée inférence, tokens, réponse exacte, erreurs parse, lignes sélectionnées, conclusions exactes selon annotation auteur, précision/rappel, contrôle de non-promotion, échec infra séparé.

## Précautions et critère falsifiable
- Ce test est **post-hoc et non indépendant** : il mesure une capacité locale de classification de lignes, et non la qualité du raisonnement mathématique. Le jeu et le prompt ne sont pas de nouveaux holdouts.
- 3B et 0,5B diffèrent **en taille, entraînement (Coder), quantification, moteur et tokenisation** ; aucune attribution causale à la taille seule ne sera défendable. Les plafonds de génération sont identiques mais **pas les coûts totaux**.
- Résultat positif local : au moins 1 ligne gold correctement retenue, zéro ligne invalide acceptée, et pas de promotion. Verdict de progrès scientifique reste **indéterminé**. Résultat nul, `NONE`, ou incohérence sont conservés comme échec de l'hypothèse d'utilité du test.
- Aucun ajustement après résultat présenté comme prospectif ; aucune modification `main`, aucune fusion ni exécution de code des propositions LLM.

## Préalables techniques
Le contrôle du hash du GGUF et celui du commit llama.cpp sont obligatoires. Si téléchargement/build échoue, rapporter INFRA_FAILURE sans conclusion scientifique. Les rapport bruts sont archivés quelle que soit l'issue.