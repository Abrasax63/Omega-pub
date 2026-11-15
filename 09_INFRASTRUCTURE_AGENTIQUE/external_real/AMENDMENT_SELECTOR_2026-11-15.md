# OMEGA-EXTERNAL-REAL-01 — amendement avant toute inférence de Qwen

Date : 15 novembre 2026, **après** run de reproduction #43766939606 et **avant** le premier appel du modèle pour ce pilote.

Le [run #43766939606](https://github.com/Abrasax63/Omega-pub/actions/runs/43766939606) a vérifié les 6 blobs Git historiques et reproduit les trois défauts avec leurs fonctions originelles. Résultats publics connus au moment de cet amendement :

- E1 `cool-RR/PySnooper` : 8 patchs AST, **P00 et P01** admis sur le test public ; différence de mode fichier (append vs overwrite).
- E2 `tqdm/tqdm` : 3 patchs AST, **P00** seul admis.
- E3 `cookiecutter/cookiecutter` : 4 patchs AST, **P01** seul admis.

**Nouvelle expérience de sélection préengagée** : appeler Qwen2.5-Coder-3B **une seule fois pour E1**, parce que c'est le seul cas avec véritable ambiguïté. Ne pas lui demander de « sélectionner » E2 et E3 où il ne reste qu'une hypothèse ; le modèle n'aurait alors aucune décision substantielle. Témoin déterministe : premier candidat public admis par ID, soit E1/P00, E2/P00, E3/P01.

Qwen ne reçoit **que le nom de la fonction, le problème public, les deux lignes candidates et les IDs**, jamais les différences historiques du commit fixed, le code fixed, les entrées réservées ni leurs réponses. Température zéro, Qwen2.5-Coder-3B GGUF déjà utilisé dans les PR antérieures (SHA-256 `724fb256bec1ff062b2f65e4569e871ad2e95ab2a3989723d1769c54294730b7`), llama.cpp fixé au commit `5a4afd80779ba51166b59986e61a0bfbb9e1a4c6`, 96 tokens max, 2048 contexte. Sortie attendue : un seul ID exact `P00` ou `P01`. Sinon **abstention**.

Après écriture du fichier des choix, en calculer SHA-256 avant d'ouvrir la réserve candidate. L'évaluateur Docker recharge les versions buggy originales, régénère les candidates depuis la **même grammaire gelée**, vérifie leurs SHA contre le manifeste, puis teste la source choisie sur les entrées réservées déjà définies dans `external_real.py`. Le bras déterministe et Qwen sont évalués sur **les mêmes entrées** ; si la même source est sélectionnée, ne pas compter deux reproductions indépendantes. Également évaluer **une seule fois après gel** tous les candidats qui passaient le développement, à des fins d'audit, sans changer les choix.

**Limite particulièrement importante** : le banc et les entrées réservées sont connus du développeur et les patches historiques ont été inspectés avant la sélection de ces cas. Il ne s'agit pas d'une nouvelle cohorte aveugle indépendante. L'expérience mesure la fonctionnalité de l'assemblage et une première comparaison locale, **pas** l'intelligence générale ni une découverte d'algorithmes.

Le premier run en échec (permissions du volume Docker) reste conservé ; le correctif de transfert par stdout a été appliqué avant le second run. Les suites intégrales upstream n'ont pas été exécutées. Aucun changement `main`, CORE ni merge.
