# OMEGA-LIBRARY-MEMORY-REAL-02 — préenregistrement du test minimal

Date de gel du PROTOCOLE : 2026-11-23. Statut : PROTOCOLE SEUL / AUCUNE INFÉRENCE REAL-02 EXÉCUTÉE. Portée : PR #231 (branche expérimentale), jamais main. Cette expérience est nouvelle, distincte du pilote REAL-01 du 22 novembre. Ne pas réutiliser les pages 68, 120, 180 ni leurs problèmes comme cohorte indépendante.

## Hypothèses distinctes (ne pas les confondre)

- H_A (acquisition) : le même modèle local, depuis un passage mathématique nouveau non annoté, choisit une recherche, récupère au moins une source traçable et archive une fiche JSON avec une citation littérale rattachée à la bonne source.
- H_F (fidélité) : la définition de la fiche, ses hypothèses et son exemple/counter-exemple correspondent à la notion de la source, avec vérification mathématique indépendante (et non simple correspondance de citation).
- H_M (réutilisation) : dans une session neuve, sans accès au Web ni au texte primaire, l'injection de cette fiche PERSISTÉE améliore le résultat sur des tâches nouvelles par rapport au direct ET à un placebo de mémoire à budget comparable.

## Gel des données AVANT exécution (précondition, pas encore réalisé)

Source primaire : un NOUVEAU passage sur les relations binaires dans un manuel public d'une édition distincte, par exemple Oscar Levin, `Discrete Mathematics: An Open Introduction, 4e éd.`, https://discrete.openmathbooks.org/dmoi4.html . Enregistrer dans un commit antérieur au run : URL précise du passage, licence, texte exact ou représentation autorisée, SHA-256, texte extrait, sélection déterministe, et SHA des quatre cas de holdout. Si cette fixation documentaire manque, NE PAS EXÉCUTER. Le passage ne doit pas contenir les réponses aux holdouts. Une seule tentative, aucun remplacement après inspection des réponses du modèle.

Le domaine exact admissible est fixé : propriété d'une relation binaire finie parmi `reflexive, irreflexive, symmetric, antisymmetric, transitive, total, serial, functional`, ou l'une des conjonctions standards `equivalence` = réflexive+symmetric+transitive, `preorder` = réflexive+transitive, `partial_order` = réflexive+antisymmetric+transitive. Si le modèle choisit une notion hors de cette grammaire, enregistrer `OUT_OF_ORACLE_SCOPE`; ne pas lui substituer une notion choisie par l'expérimentateur.

## Modèle, acquisition et traçabilité

Réutiliser Qwen2.5-3B-Instruct Q4_K_M et llama.cpp b12633, CPU seulement, température 0, seed fixée, sans API payante. Rejeter le run si le SHA du GGUF diffère du fichier de REAL-01 (`9c9f56a391a3abbd5b89d0245bf6106081bcc3173119d4229235dd9d23253f94`) sans amendement préenregistré. Un `run(max_hops=1)` seulement : 1 requête libre choisie par le modèle, jusqu'à 2 articles Wikipédia du récupérateur FIXE, 1 fiche candidate. Conserver : requête, résultats API bruts ou paquets de passages rejouables avec les droits nécessaires, page_id, revision_id, extrait et empreinte, JSON brut, temps, tokens, SHA du registre; la citation doit correspondre à son vrai support. Toujours QUARANTAINE, jamais mémoire scientifique certifiée.

Vérifier AVANT toute évaluation de réutilisation : le JSON est valide; la citation >=20 caractères appartient exactement au passage archivé du `source_page_id` déclaré; le texte de la citation apporte une preuve documentaire pertinente; la définition, les hypothèses, l'exemple et un contraste positif/négatif sont mathématiquement corrects au regard du passage primaire et du contrôleur exact. Le contrôle du sens requiert une fiche de jugement séparée explicitant la correspondance sémantique; si ambiguë, `F_INDETERMINE`. Le seul contrôle d'octets ne suffit pas. En cas d'échec d'un garde, ne pas « réparer » la fiche a posteriori : H_F échoue ou reste indéterminée et H_M bout-en-bout n'est PAS TESTÉE.

## Holdout et trois bras (si et seulement si H_A et H_F passent)

Une seule fiche admissible suffit pour ce test : charger cette fiche avec `read_ledger` dans un NOUVEAU processus/session ; ne pas exiger les deux fiches de `from_library`, car cette étude isole la mémoire et NON l'abstraction à deux concepts. Arrêter l'accès au réseau. Garder la même version de modèle, le même budget maximal de sortie (260 tokens), les mêmes paramètres de décodage, les mêmes questions et le même ordre contrebalancé.

L'oracle existant `check_axioms` calcule exactement les réponses des relations finies sur 3 objets. Construire DÉTERMINISTIQUEMENT 4 relations nouvelles (2 satisfaisant la notion choisie et 2 ne la satisfaisant pas) à partir du sel public `OMEGA-LIBRARY-MEMORY-REAL-02-HOLDOUT`, via tri SHA-256 des 512 relations à 3 sommets; si la notion est hors domaine, ne pas évaluer. Exclure et signaler les éventuels spécimens identiques/isomorphes à un exemple montré dans le passage ou la fiche, sans sélection manuelle de remplaçants; la règle d'exclusion et de remplacement déterministe doit être figée avec les données avant inférence. Ne communiquer au modèle ni l'oracle ni les réponses.

Pour chaque même tâche, trois prompts ne diffèrent que par la zone mémoire :
- D = DIRECT : aucune fiche mathématique, zone mémoire neutralisée.
- M = MÉMOIRE RÉELLE : fiche validée lue depuis le registre vérifié après redémarrage, avec son candidate_id.
- N = TÉMOIN NÉGATIF : même enveloppe, métadonnées et candidate_id, mais les champs apportant la connaissance (`definition, hypotheses, relations, example, falsifier, exact_quote`) sont masqués et remplacés par du contenu neutre, sans relation mathématique.

Aucune des trois conditions n'a accès au Web ni au document original pendant les tâches. Aligner l'occupation de contexte dans les trois conditions à ±5 % de tokens de prompt, au moyen d'un remplissage NEUTRE gelé, et conserver le nombre réellement tokenisé. Si cette comparabilité échoue, pas de conclusion causale. Randomiser de façon déterministe l'ordre des bras par tâche et conserver l'ordre et les réponses brutes. Le bras N doit prouver que l'effet n'est pas seulement « un prompt plus long » ; le bras D mesure le niveau de base. Ne pas utiliser une fausse définition nuisible comme témoin principal, car cela artificiellement dégraderait N.

## Métriques (dénominateurs et absences explicites)

- Acquisition A : 1/1 requête autonome admissible, 1/1 récupération avec page_id+revision_id+SHA, 1/1 JSON strict, 1/1 citation exacte dans sa source, 1/1 paquet documentaliste rejouable. Reporter chaque sous-métrique binaire ET la raison d'échec.
- Fidélité F : 1/1 définition fidèle, 1/1 hypothèses exactes, 1/1 exemple/contre-exemple vérifié, 0 amalgame/équivalence invalide. Un seul énoncé faux suffit à rejeter F sur le cas. Distinguer contrôle mathématique exact et jugement sémantique indépendant.
- Mémoire : corrects complets D/M/N sur 4, erreurs non détectées, abstentions, JSON invalides, tâches où la décision change et vers quoi, tokens entrée/sortie, temps CPU, nombre d'appels et précision de l'oracle; aucun score ne doit exclure les réponses mal formées du dénominateur.
- Le maximum prévu : 2 appels modèles d'acquisition + 12 prédictions sur holdout = 14 appels, sans réessais opportunistes.

## Verdict gelé — pas de modification après observation des résultats

1. `ACQUISITION_RATEE` si requête, récupération, JSON, source ou citation échoue.
2. `FIDELITE_REFUTEE_SUR_CE_CAS` si la représentation énonce au moins une affirmation mathématique fausse; `FIDELITE_INDETERMINEE` si jugement impossible. Dans les deux cas, ne pas lancer M sur la fiche erronée pour annoncer un gain d'apprentissage.
3. `MEMOIRE_GAIN_PONCTUEL` **seulement** si A et F passent, D/M/N sont comparables, M >= 3/4 exactes, M >= D + 2 bonnes réponses, M >= N + 2, **0 erreur silencieuse en M**, et le chargement réel de candidate_id a été tracé après redémarrage.
4. `GAIN_MEMOIRE_NON_OBSERVE` si l'essai de réutilisation est admissible, mais M <= D ou M <= N, ou les seuils stricts de progrès échouent. Si D et N sont au plafond (4/4), noter `EFFET_INIDENTIFIABLE_PLAFOND` plutôt que prétendre à une impossibilité générale.
5. `INDETERMINE` si échec du protocole, des budgets, de l'oracle, du gel ou des artefacts. Ne pas remplacer les observations négatives ou manquantes par des données synthétiques.

Un gain ponctuel sur quatre tâches NE démontre ni supériorité statistique, ni compréhension générale, ni mise à jour des poids, ni AGI. Une absence de gain ne prouve pas qu'aucune architecture mémoire ne puisse marcher : elle réfute uniquement le critère préenregistré de ce pilote.

## Frontière d'exécution

Ce commit est le protocole seulement : ne contient ni nouvel exécuteur, ni appel LLM, ni workflow et ne modifie pas `main`. **Ne pas exécuter REAL-02** avant un second gel explicite des données, des prompts/evaluateurs et de leurs empreintes. Aucun contournement du garde de citation ni promotion de candidat. Tout amendement après run relève d'une nouvelle cohorte.
