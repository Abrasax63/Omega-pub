# OMEGA ACTIVE-DEBUG-01 — préenregistré avant tout appel au modèle
Date de gel initial : 2026-11-23. Branche : experiment/omega-active-debugging-2026-11-23. main inchangée.

## Hypothèse falsifiable
Sur six **nouvelles familles de fonctions Python** de manipulation de chaînes (programme initial syntaxiquement valide mais logiquement faux), un Qwen2.5-Coder-3B-Instruct local quantifié Q4_K_M peut-il améliorer le nombre de fonctions totalement correctes en lisant les erreurs d'exécution de **deux exemples publics** plutôt qu'en effectuant une seconde révision sans feedback ?

**La question porte sur l'utilisation d'outils au moment de l'inférence, pas sur un changement des poids.** Le modèle n'est pas entraîné. L'amélioration mesurée n'est pas de l'apprentissage durable si les outils sont ensuite retirés.

## Cohorte, indépendante des anciens holdouts
Six fonctions distinctes non présentes dans les tâches et familles de TRAIN26, SFT01, SEMANTIC04 ou FastLane : (1) détection de mots palindromes non vides, (2) profondeurs de parenthèses ouvrantes, (3) conversion de paires hexadécimales en décimal, (4) majuscules/minuscules selon le rang d'un mot, (5) équilibre de parenthèses avec préfixes non négatifs, (6) somme alternée des chiffres en ignorant les autres caractères.

Une seule faute *sémantique compilable* par fonction, pas un bug syntaxique. **Deux observations publiques** par exercice et **cinq tests réservés à l'évaluation** (30 tests comportementaux). Les oracles et tests réservés sont committés dans un fichier figé, mais non envoyés au modèle ni utilisés pour choisir un candidat. Le code source de référence n'est pas envoyé aux modèles. Les prompts et budgets sont gelés avant la première inférence réelle. Les exercices synthétiques sont conçus par le développeur, pas auto-inventés par Omega, et ne garantissent pas l'absence dans le préentraînement de concepts voisins.

## Bras préenregistrés
- **DIRECT-1** : un seul appel à Qwen2.5-Coder-3B-Instruct, prompt avec code cassé et deux exemples. Un programme par réponse.
- **DIRECT-2** : même première génération (partagée) puis un second appel de révision, sans exécution ni exemples supplémentaires. Maximum 400 nouveaux tokens par appel.
- **EXEC-FEEDBACK-2** : même première génération (partagée), test du code proposé sur les deux exemples publics seulement (AST sécurisé + subprocessus limité), second appel avec sorties réelles vs attendues et erreurs éventuelles. **Même budget de deux appels de maximum 400 nouveaux tokens que DIRECT-2** ; seule l'information de feedback diffère.
- **SYM-LOCAL** : le correcteur déterministe borné existant `execution_guided.resolve` (sans modèle, ni nouvelle requête d'oracle), à partir du code cassé et des mêmes exemples.
- **HYBRIDE-PROTÉGÉ** : `execution_guided.resolve_guarded` sur le code cassé, exemples publics et la proposition EXEC-FEEDBACK ; il protège une solution symbolique unique et vérifiée, et n'autorise les propositions du modèle qu'en absence de solution symbolique. Les ambiguïtés restent des abstentions.

Pour ne pas créditer le modèle du résultat d'un vérificateur, les métriques « candidats trouvés » et « programmes effectivement sélectionnés » sont distinctes.

## Modèle, inférence et coûts
Qwen2.5-Coder-3B-Instruct Q4_K_M de bartowski, révision HF `21d6b71` (référence de page au moment du gel), SHA256 du GGUF `3da3afe6cf5c674ac195803ea0dd6fee7e1c228c2105c1ce8c66890d1d4ab460`, taille environ 1,93 Go, licence décrite comme qwen-research sur le dépôt Hugging Face — vérifier l'adéquation de cette licence avant tout usage commercial. llama.cpp release b12633 réutilisée depuis PR #233. Serveur uniquement sur 127.0.0.1, CPU GitHub Actions, pas de clé ni d'API payante. Température 0, seed 20261123, max 400 nouveaux tokens/appel, 2 appels au maximum dans les deux bras. Une première génération partagée limite le coût; les autres bras consomment zéro appel supplémentaire.

Préenregistrement d'une limite opérationnelle : au maximum six tâches complètes, budget total d'au plus **18 requêtes modèles** (six premières générations, six révisions DIRECT-2, six révisions EXEC-FEEDBACK-2) et 7 200 nouveaux tokens théoriques ; si les plafonds de temps CI sont dépassés, statut TECHNIQUE INDETERMINE sans en faire une observation scientifique.

## Critères
Pour chaque bras : fonctions validées par l'AST, fonctions correctes sur tous les cinq tests réservés, erreurs silencieuses sur les tests, abstentions, appels/tokens, temps d'inférence et de sandbox, coût symbolique (nombre de programmes essayés). Les tests cachés sont utilisés seulement **après** fixation des réponses de tous les bras.

- Si EXEC-FEEDBACK-2 > DIRECT-2 à égalité de requêtes et de plafond de génération, c'est un **signal exploratoire d'utilité du feedback**, pas apprentissage de poids ni généralisation générale.
- Si la méthode symbolique atteint plus ou autant que les bras modèle, un routage adaptatif peut être rentable, mais **ne pas forcer le modèle dans le chemin nominal**.
- Si DIRECT-2 et EXEC-FEEDBACK-2 restent à zéro, la boucle d'exécution n'est pas démontrée utile avec ce modèle et ces exercices.
- Toute solution non validée sur tests publics et test réservés n'est pas certifiée.

## Protocole de sécurité et d'honnêteté
Scripts existants pour AST et exécution CPU limitée. Aucun code généré ne touche le réseau, le dépôt GitHub, le système de fichiers en écriture ni l'environnement de la boucle LLM. Le fichier JSON contenant les tests réservés est **public dans GitHub** mais **non communiqué dans les prompts**. Ne jamais confondre cette séparation expérimentale avec une confidentialité cryptographique vis-à-vis d'un modèle ayant accès à internet. Ne jamais inspecter le score puis retoucher prompts, tâches, règles de sélection ou modèle en revendiquant la même expérience comme test indépendant. Après notation, cohorte consommée. PR DRAFT; aucun nouveau cron, aucune fusion, aucun entraînement automatique.

## Références existantes réutilisées
- [Tests Python du laboratoire PR #232](https://github.com/Abrasax63/Omega-pub/pull/232)
- [Réparateur symbolique corrigé PR #237](https://github.com/Abrasax63/Omega-pub/pull/237)
- [Modèle GGUF sur Hugging Face](https://huggingface.co/bartowski/Qwen2.5-Coder-3B-Instruct-GGUF/blob/main/Qwen2.5-Coder-3B-Instruct-Q4_K_M.gguf)
- [Boucle CPU llama.cpp historique PR #233](https://github.com/Abrasax63/Omega-pub/pull/233)
