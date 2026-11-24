# RH-RAW-01 — premier test sans structure préfabriquée

## Révision critique de RH-READING-01

Le test précédent obtenait 16/16 sur des implications Horn **déjà traduites manuellement** depuis le guide de Rubinstein. Ce résultat démontre un calcul logique contrôlé, **pas** que le modèle sait lire le texte. Ce biais de « travail prémâché » motive ce nouveau protocole.

## Entrée réellement donnée au modèle

- Source brute : le [PDF original de Michael Rubinstein](https://www.math.uwaterloo.ca/~mrubinst/alpoge_claude_grh/zeta-paper.pdf), acquis automatiquement par GitHub Actions. Pages **physiques** 2 et 3, extraites par `pdftotext -layout` sans sélection de phrases, résumé, étiquetage, entité extraite ou graphe logique.
- Le PDF complet et les poids du modèle ne sont **pas** archivés dans la PR ; leurs empreintes SHA-256, les empreintes des pages, les prompts et les sorties le sont. La source reste publique et identifiable.
- Question générique 1 : relever de façon autonome les idées principales, ce qui est démontré dans le texte, les dépendances, les limites et les preuves importées ; chaque affirmation doit proposer une citation littérale.
- Question générique 2 : proposer librement une représentation alternative ou une hypothèse réfutable à partir du même texte, ou abstention. **Aucune mention de M, B, C, RH, nombres premiers, parités, graphe quotient ou théorème déjà reconstruit n'est présente dans le prompt.**
- Modèle local réellement exécuté : `Qwen2.5-0.5B-Instruct-Q4_K_M.gguf` du dépôt `bartowski/Qwen2.5-0.5B-Instruct-GGUF` (Apache 2.0), version de fichier liée à une révision publique ; moteur `llama.cpp` **b12633** téléchargé comme binaire précompilé ; uniquement CPU GitHub Actions. Pas d'API distante de modèle payante.
- Jusqu'à quatre appels : 2 pages × 2 tâches, température zéro, même modèle, pas de résultats pré-remplis. **Le modèle est seul face à la source.**

## Mesures qui restent autorisées sans vérité terrain

- Nombre d'appels réellement exécutés, secondes d'inférence, taille des entrées, empreintes des sources et modèle.
- Validité syntaxique du JSON ; nombre de citations textuelles littérales effectivement présentes dans la page ; citations rejetées.
- Vérification mécanique des citations : ce mécanisme ne peut absolument pas dire si une affirmation mathématique est **vraie**, si un résultat est **prouvé**, si une structure est **nouvelle** ni si une interprétation est fidèle.
- La sortie libre du modèle est conservée pour **revue sémantique distincte**, sur référence préparée indépendamment après verrouillage des sorties. Aucun label n'est fourni à l'inférence. La fidélité sémantique, le nombre d'hallucinations et la créativité restent **INDÉTERMINÉS** tant que cette revue n'est pas faite.
- La comparaison directe/modèle avec filtre Omega concerne **la traçabilité des citations**, pas la compréhension : la sortie brute et la sortie filtrée sont deux vues de la **même génération**, donc ce n'est pas un gain LLM autonome.

## Contraintes de sûreté et d'interprétation

- Un échec d'installation, de téléchargement, de lancement ou de génération est **BLOCKED**, pas une mesure scientifique négative.
- Une citation exactement recopiée n'est pas une preuve. Une hallucination plausible mais non citée est refusée. Une phrase citée mais détournée de son contexte requiert un évaluateur indépendant.
- Un modèle de 0,5 milliard de paramètres sert de pilote gratuit ; il ne représente ni le comportement d'un modèle frontière, ni l'ensemble d'Omega.
- Pas de mémoire du contenu attendu, pas de corrigé injecté, pas de jeu de cas mathématiques manuellement préfabriqué.
- Aucune suppression de tests, aucune fusion ni activation de cadence automatique.
- Si les résultats sont mauvais, le même essai n'est **pas** corrigé après inspection de la réponse : toute modification de prompt ou de modèle fera l'objet d'un protocole v2 avec nouveau corpus.

## Critère de progrès décisif

C'est une première mesure **sans prémâchage**, pas encore une preuve de compréhension. Le progrès réel exige un jeu plus large de sources nouvelles, un juge scientifique externe aveugle, des tests contrefactuels, et des comparaisons au **même modèle direct** et au même budget sur les mêmes données, avec vérification des citations et des hypothèses.
