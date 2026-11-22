# OMEGA-PY-SFT-01 — premier entraînement supervisé Python de SmolLM2

**Statut initial : corpus et protocole figés, pas encore de résultat neuronal.**

Le hub réutilise le savoir-faire de [TRAIN26 / PR #198](https://github.com/Abrasax63/Omega-pub/pull/198), qui a démontré la faisabilité d'un LoRA CPU sur SmolLM2-135M, mais son entraîneur attend des **formules mathématiques**. Cette expérience utilise donc le même modèle/révision, la même pile épinglée et le même mécanisme PEFT, avec un petit **adaptateur de domaine Python** indépendant. Ce n'est pas une copie silencieuse des entraînements mathématiques ni un entraînement du Qwen 3B.

## Données gelées AVANT le premier appel du modèle

- [Préenregistrement](PREREG.md) : hypothèse, hyperparamètres et règles de falsification.
- \`TRAIN_FROZEN.json\` : **62 réparations supervisées**, 22 familles ; **60 exemples synthétiques conçus et étiquetés par le développeur**, deux programmes proposés par Omega dans le vrai run V3 et vérifiés. Aucun des 62 n'est une découverte scientifique.
- \`HOLDOUT_EVAL_ONLY.json\` : **12 réparations de six fonctions différentes**, cinq entrées cachées chacune. Le module d'entraînement ne charge pas ce fichier ; seul le job d'évaluation l'ouvre après sauvegarde des poids.
- \`data_guard.py\` : git-blob SHA1 exacts du train et du holdout pour détecter toute modification. Les fonctions sources évaluées sont une vérité d'ingénierie sur un domaine borné, pas une démonstration de compétence générale.

## Entraînement réel

\`train_lora.py\` effectue deux époques sur 62 exemples avec PEFT LoRA (\`q_proj\` et \`v_proj\`, rank=8, alpha=16, seed=20261122, AdamW LR=0,0005). Il doit :

- modifier effectivement un adaptateur (norme L2 des mises à jour strictement positive) ;
- parcourir les **124 mises à jour** ;
- enregistrer les pertes, la révision exacte du modèle et le SHA256 du fichier \`.safetensors\` ;
- sauvegarder l'adaptateur AVANT le moindre score de test.

L'adaptateur est un petit composant auxiliaire ; il n'a pas d'accès GitHub en écriture, au réseau ni aux poids du modèle de dialogue Qwen.

## Évaluation rigoureuse, mais limitée

\`evaluate.py\` recharge l'adaptateur enregistré et compare le modèle initial et le modèle adapté sur les **mêmes 12 questions** ; génération déterministe 220 tokens maximum, aucun feedback ni essai supplémentaire. Chaque proposition Python est vérifiée par la syntaxe/politique AST existante puis exécutée dans le sous-processus restreint du laboratoire. Sont comptées séparément :

- fonctions syntaxiquement valides et sûres ;
- fonctions correctes sur les **cinq** cas cachés ;
- régressions sur les douze tâches ;
- tokens et durée.

Un score de 0/12 après entraînement est un résultat techniquement valide. Un score supérieur signale une amélioration **exploratoire de réparation Python dans ce corpus**, pas la généralisation durable, ni la construction de son propre modèle, ni une AGI.

## Sécurité, durée, intégration

GitHub Actions CPU, versions exactes issues de TRAIN26 : Torch CPU 2.5.1, Transformers 4.49.0, PEFT 0.15.2, Accelerate 1.5.2, safetensors 0.5.3, huggingface_hub 0.30.2. Aucune API payante. Aucun nouvel agent horaire, aucune fusion automatique dans \`main\`.

Les **deux** candidats déjà admissibles dans le Learning Hub restent en quarantaine ; leur inclusion dans un jeu d'entraînement **exploratoire** ne les promeut pas en compétences permanentes. Les cibles synthétiques sont séparées des deux vraies corrections du modèle par un champ de provenance. L'ancien modèle mathématique TRAIN26 et son adaptateur ne sont pas écrasés.

Toute reprise de ce pilote après inspection des résultats devra employer **un autre holdout**. Un simple redémarrage CI sur les douze mêmes exercices n'est pas une vérification indépendante.

**Après les scores :** constituer progressivement de nouvelles corrections réellement produites par Omega, valider chaque famille, comparer apprentissage paramétrique / mémoire seule / référence directe, puis organiser une seconde expérience avec un holdout externe inédit.
