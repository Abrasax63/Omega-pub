# OMEGA-PY-SFT-01 — préenregistrement AVANT corpus et inférence

Date : 22 novembre 2026. Projet expérimental isolé sur une branche de la PR #235. Ne pas fusionner main.

## Question falsifiable

Le petit modèle **SmolLM2-135M-Instruct**, précédemment entraîné dans TRAIN26 sur une tâche mathématique différente, peut-il améliorer sa capacité à **réparer des fonctions Python** après un entraînement supervisé LoRA sur un cursus de réparations vérifiées, et généraliser à de **nouvelles fonctions** qui n'ont pas été utilisées à l'entraînement ?

Ce pilote ne prétend pas entraîner le modèle Qwen3B des PR #232–234 ; il ne prétend ni découverte autonome de règles, ni construction d'un modèle depuis zéro.

## Branches et réutilisation

- TRAIN26 PR #198 prouve le fonctionnement réel de la pile CPU Torch 2.5.1, Transformers 4.49.0, PEFT 0.15.2, Accelerate 1.5.2 et de la méthode LoRA q_proj/v_proj. Réutiliser cette pile, son modèle, sa révision et le contrôle de changement de poids. TRAIN26 conserve ses labels de mathématiques et **ne doit pas être modifié/invoqué pour des étiquettes Python incompatibles**.
- Le laboratoire Python V1/V3 fournit un interpréteur Python AST/sous-processus contrôlé et une séparation syntaxe / comportement. Ne pas exécuter du code généré dans le processus du modèle.
- Les deux corrections Python générées par Omega dans V3 ont été vérifiées sur leurs anciens cas de pratique et conservées dans l'index de la PR #235. Elles peuvent être incluses à titre de **2 exemples d'entraînement V3 consommés**, et ne doivent jamais redevenir un holdout.

## Données nouvelles, à créer et figer avant toute vraie inférence

- Environ 40–60 paires de réparation **synthétiques et supervisées par le concepteur** : plusieurs fonctions Python simples, chacune affectée de quelques erreurs syntaxiques. Ne **pas** les décrire comme découvertes par Omega.
- Inclure exactement 2 anciens candidats V3 vérifiés, clairement identifiés comme tels. Le reste des labels vient de programmes de référence déterministes, non de la génération autonome d'un LLM.
- Garder un holdout nouveau de 12 exercices issus de fonctions et objectifs absents du train. Éviter chevauchement de fonctions, identifiants et couples exacts. Tester avant/après sur les **mêmes 12 prompts** et leurs cas cachés de comportement. Tout code candidat est évalué par syntaxe/politique + appels dans un sandbox restreint.
- Les données de référence des 12 cas cachés ne sont jamais importées par le module d'entraînement ; elles ne sont ouvertes qu'en évaluation, après sauvegarde de l'adaptateur.
- Les 2 exemples V3 ne doivent pas se retrouver dans les données de test. Les holdouts A–F déjà utilisés ne sont jamais requalifiés en « nouveaux ».

## Protocole d'entraînement

- HuggingFaceTB/SmolLM2-135M-Instruct à la révision \`ee72e5415c002e8fc0566a191a07c0b2b708875a\`.
- LoRA rank 8, alpha 16, dropout 0, \`q_proj\` et \`v_proj\`, CPU float32, AdamW, LR 0.0005, seed 20261122. 2 passages complets du corpus figé, batch 1, limite 384 tokens par exemple (erratum de capacité documentaire, corrigé avant toute inférence et avant tout accès aux résultats); **aucun changement des hyperparamètres après avoir vu les scores de test**.
- Enregistrer l'empreinte du jeu d'entraînement, le nombre exact de mises à jour, la perte, la norme L2 non nulle du changement de paramètres et l'empreinte \`.safetensors\`.
- Sauvegarder le modèle avant toute évaluation finale. Comparer poids de base vs adaptateur entraîné sur les mêmes questions de holdout (greedy, max 220 nouveaux tokens, sans deuxième tentative).
- Pas d'API payante ; seule une CI CPU GitHub Actions est autorisée ; pas de secrets et aucun fichier modifié par le modèle sur GitHub.

## Critères de réussite et échec

1. **Vérification de construction de la chaîne** : tests de structure des données, absence de recouvrement, sandbox, valeur de hash, train complet et poids effectivement modifiés.
2. **Résultats scientifiques** : nombres de programmes qui compilent, programmes sûrs, programmes exacts sur tous les cas comportementaux cachés, par bras, erreurs silencieuses, programmes régressés, et coût.
3. **Gain pédagogique de Python** : score sémantique après entraînement strictement supérieur à celui de base, sans hausse d'erreurs potentiellement dangereuses. Un gain syntaxique seul ne constitue pas une maîtrise de Python.
4. **Généralisation** : un gain sur 12 fonctions nouvelles serait seulement **un signal exploratoire**, pas une causalité établie ni une compétence durable. Aucun corpus public n'est garanti absent du préentraînement initial.
5. **Rétention** : contrôle ancien savoir à programmer dans une expérience distincte à protocole neuf avant revendication de progression durable. Le modèle mathématique TRAIN26 conserve sa propre PR et n'est pas écrasé.

**Il est possible que LoRA améliore la conformité du format mais dégrade la fidélité fonctionnelle. Le résultat négatif est acceptable.** Une exécution GitHub verte ne prouve rien à elle seule.

## Environnement et sûreté

Cette version utilise des fonctions Python jouets et la stratégie SmolLM2 LoRA éprouvée ; elle ne démarre ni service autonome ni boucle non bornée. L'accès réseau sert exclusivement à installer des dépendances/matériaux publics épinglés ; les programmes générés sont exécutés dans un subprocessus sans accès réseau, fichiers ou API. La validation syntaxique/politique doit refuser tout code qui sort de la liste limitée. Le projet demeure sur une branche DRAFT, \`main\` inchangée.

**Le cursus synthétique est un pré-entraînement pédagogique supervisé, pas une preuve d'auto-apprentissage d'Omega.**

### Erratum technique pré-inférence

L'ancien plafond annoncé à 256 tokens a été porté à 384 **avant toute exécution de modèle** pour accueillir les prompts complets et les exemples publics. Rien d'autre ne change : deux époques, 62 exemples figés, 124 mises à jour maximum, six familles réservées et aucune adaptation aux résultats.
