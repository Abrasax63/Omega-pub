# Raccord horaire des capacités vérifiées d'Omega — 22 novembre 2026

## Objectif : « exploitable sans merge dans main »

Cette branche **n'est pas le runtime principal**. Le dépôt \`main\` ne contient pas le Learning Hub ni nos nouveaux workflows. Les PR #235–238 sont des travaux expérimentaux empilés. Une réussite CI ne rend pas un module disponible sur toutes les branches, et le simple fait de référencer une branche dans un catalogue ne l'exécute pas à chaque cycle.

L'objectif est de relier l'automatisation EXISTANTE « Amélioration continue d’Omega » à un **catalogue d'outils dont on connaît le statut et la preuve**, tout en conservant les cycles déjà autorisés sur les PR #81/#82 et Omega100. Pas de création d'un deuxième cron ni de fusion automatique.

## Fonctionnement

\`CAPABILITY_REGISTRY.json\` contient chaque capacité, sa PR, son **commit précis**, sa preuve de run, son domaine d'emploi, ses limites et son niveau épistémique.

\`route.py\` est un **sélecteur sans effets de bord** : on lui donne le type de tâche et il donne un plan de consultation. Il n'utilise ni réseau, ni clé, ni LLM, ni clonage, ni sous-processus de modèles. Il ne possède aucun pouvoir de lancement. Dans le cycle horaire, le pilote consulte le registre, vérifie par GitHub le commit et les preuves, puis peut réutiliser la logique d'une capacité **seulement quand elle correspond à la question, que son exécution est autorisée par la branche de travail, et que les tests locaux sont pertinents**.

\`\`\`sh
python research/learning_hub/hourly_router/route.py \
  --kind local_python_semantic_bug
python research/learning_hub/hourly_router/route.py \
  --kind mathematical_proof_or_counterexample
\`\`\`

Le pilote ne doit pas présenter le fait d'avoir *consulté* un outil comme une exécution de ce dernier.

## Nouveau résultat contrôlé après TRAIN SFT01

Le [run de sémantique #45074827572](https://github.com/Abrasax63/Omega-pub/actions/runs/45074827572) est **SUCCESS** et donne sur 12 erreurs Python logiques **0/12 pour SmolLM2 de base, 0/12 pour le LoRA SFT01, 11/12 pour le correcteur symbolique local**. Cette comparaison était préenregistrée avant l'inférence et ne prouve pas une supériorité générale de la programmation symbolique. Elle **réfute** l'hypothèse pratique que le gain syntaxique 11/12 du LoRA puisse être supposé transféré tel quel à ces erreurs sémantiques.

Conséquence de routage :
- en réparation locale d'un bug logique de même type, inspecter d'abord le petit correcteur symbolique comme **candidat soumis à de nouveaux tests**, et **ne pas faire tourner un entraînement LoRA** ;
- en réparation syntaxique, l'expérience SFT01 peut servir de référence expérimentale, pas de « compétence certifiée » ;
- en mathématiques/provenance, maintenir les méthodes et branches des PR #81/#82, le test d'une fonction Python ne remplaçant pas une preuve.

Le [run Fast Lane #45076652556](https://github.com/Abrasax63/Omega-pub/actions/runs/45076652556) montre un générateur de 77 exemples synthétiques validés sur 20 familles préexistantes. Ces données **ne sont pas nouvelles familles**, et ne sont pas un modèle entraîné.

## Protocole à intégrer à l'automatisation existante

1. Au début de **chaque déclenchement horaire**, lire le registre sur le SHA de cette branche contrôlé en CI, récupérer les PR/run de sources et vérifier qu'ils correspondent. Si les données/accès diffèrent, marquer \`CAPABILITY_UNAVAILABLE\`, sans substitution silencieuse.
2. Déterminer si un micro-cycle est de type \`mathematical_proof_or_counterexample\`, \`provenance_reconciliation\`, \`omega100_iteration\`, \`local_python_semantic_bug\`, \`python_syntax_repair_pilot\`, \`new_training_data_qa\` ou \`learning_state_integrity\`. Si aucun type ne correspond, se garder de forcer un outil.
3. Consulter le plan du routeur ; comparer les méthodes les plus pertinentes. Pour un code qui n'est pas sur la branche autorisée, travailler en **lecture seule ou copie temporaire**, sans faire de \`main\` la source de la capacité et sans écriture sur la branche tierce.
4. Exécuter seulement les contrôles **compatibles avec les budgets et interdictions du cycle actuel**. Vérifier les programmes et la provenance avant d'en tirer une nouvelle affirmation. Enregistrer : \`capability_considered\`, \`selected\`, \`actually_executed\`, \`reason\`, \`source_ref\`, \`tests\`, \`cost\`, \`new_evidence\`, \`fallback\`.
5. Garder la cadence existante (jusqu'à quatre micro-cycles dans **un** déclenchement, pas quatre nouveaux déclenchements) et la répartition #81/#82 et Omega100. Aucun lancement automatique LoRA, aucune dépense, aucune promotion d'hypothèse, aucune fusion.

## Ce que l'intégration ne prouve pas

Le registre + sélecteur peuvent passer leurs propres tests, mais **l'utilisation effective de ces capacités dans les prochaines exécutions de l'automatisation doit encore être observée dans les journaux**. Une fois le prompt sauvegardé, on peut vérifier que la tâche *doit* consulter le catalogue à l'heure suivante ; il faudra constater une trace effective pour dire qu'elle l'a fait.

Le routeur ne permet pas à un service GitHub \`main\` de « charger » une branche sans l'avoir checkout explicitement. Les PR restent DRAFT.

**Falsification** : si une exécution horaire ignore le catalogue alors qu'il est accessible, attribue un score sémantique positif au LoRA ou écrit hors branche, l'intégration est défaillante et l'ancien pilote reste le repli, sans nouvelle revendication de gain.
