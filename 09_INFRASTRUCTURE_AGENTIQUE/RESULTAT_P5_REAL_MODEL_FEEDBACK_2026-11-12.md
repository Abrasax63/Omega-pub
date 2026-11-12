# P5-REAL-01 — modèle réel, retours de vérification, absence d'avantage adaptatif

**12 novembre 2026 — statut : 48 VRAIES GÉNÉRATIONS EXÉCUTÉES / RÉSULTAT EXPLORATOIRE / AVANTAGE PROPRE À OMEGA NON DÉMONTRÉ.**

## Provenance et garde-fous

- [Pré-enregistrement](EXPERIMENT_P5_REAL_FEEDBACK_PREREG_2026-11-12.md) publié **avant code et inférence**, commit `0afbecd89cb3e0c3a7daae08bb5db7286251dacc`.
- [GitHub Actions #43197427288 — SUCCESS](https://github.com/Abrasax63/Omega-pub/actions/runs/43197427288). Les huit tests de protocole ont réussi, le modèle a réellement généré 48 réponses, l'évaluateur a exécuté huit politiques à budget égal et archivé la sortie JSON.
- [Archive publique complète, 48 réponses et trajectoires des huit politiques](https://github.com/Abrasax63/Omega-pub/actions/runs/43197427288/artifacts/13932769401). SHA-256 du ZIP téléchargé et audité indépendamment : `d6663e1fac2ef004f888cc85aa29ff9abbf9daa7ee59dfa95908ebd5289085f8`.
- [Suite RCE associée #43197427340 — SUCCESS](https://github.com/Abrasax63/Omega-pub/actions/runs/43197427340).
- Modèle `Qwen/Qwen2.5-0.5B-Instruct`, révision exacte `7ae557604adf67be50417f59c2c2f167def9a775`, inférence CPU locale au **runner distant GitHub**, `max_new_tokens=48`, **0 API OpenAI payante, aucun calcul smartphone, aucun holdout privé**.
- Empreinte des 48 questions publiques : `d22b38d8ef216aba3acbe4f61f7b1a366467761519ce765369085897dba556e4`.
- Un audit de calcul séparé a **recalculé les 48 références** avec une implémentation différente des deux formules, puis les utilités, coûts, actions et comptes des huit politiques à partir de l'archive ; **aucune discordance**. Cet audit n'est **pas** une expertise indépendante externe.

## Résultat du modèle sans outil

- Calibration : 16 problèmes publics ; évaluation : 32 problèmes publics différents, choisis avant toute génération.
- Sur les 32 cas de test, le modèle a obtenu **9 réponses extraites exactes**, **23 erronées**, **0 absence d'extraction**.
- Par strate : `DATA_SMALL` 3/8 exactes, `CRT_LARGE` 0/8, `DATA_LARGE` 6/8, `CRT_SMALL` 0/8.
- **35 sorties sur 48 sont simplement « B »** après extraction ; seulement **8 textes de sortie distincts**. Sur plusieurs questions de congruence, le modèle répond « B » au lieu d'un entier : il s'agit d'un échec de conformité de type, pas seulement d'une erreur arithmétique. Le modèle de 0,5 milliard de paramètres est ici un **instrument expérimental très faible**.
- Vérificateur limité, non artificiellement infallible : seulement **10 cas sur les 32** sont résolubles par le code de vérification proposé — les huit petits calculs de taux, plus deux petits problèmes CRT. Les autres se concluent `UNRESOLVED`. Une réponse `UNRESOLVED` entraîne une abstention et consomme quand même la vérification. Le second oracle exact est réservé à l'évaluation.

## Huit politiques comparées à budget identique

Budget de **16 vérifications** par politique sur 32 cas. Gains conventionnels : exact +1, erreur publiée −2, abstention +0,05 ; vérifier coûte 0,20 pour un taux et 0,35 pour une congruence. Les unités sont des **utilités fictives**, pas des euros.

| Politique | Utilité totale | Vérifications | Correctes publiées | Fausses publiées | Abstentions |
|---|---:|---:|---:|---:|---:|
| Réponse directe | **−37,0** | 0 | 9 | 23 | 0 |
| Vérifier d'abord jusqu'à épuisement | −10,0 | 16 | 14 | 10 | 8 |
| Toujours s'abstenir | +1,6 | 0 | 0 | 0 | 32 |
| Règle simple par domaine | +4,8 | 16 | 8 | 0 | 24 |
| **Règle simple par strate** | **+6,7** | 16 | 10 | 0 | 22 |
| **Bayes en ligne** | **+6,7** | 16 | 10 | 0 | 22 |
| **Omega candidat** | **+6,7** | 16 | 10 | 0 | 22 |
| **Omega sans alarme** | **+6,7** | 16 | 10 | 0 | 22 |

**L'égalité est exacte trajectoire par trajectoire :** `omega_candidate`, `omega_no_alarm`, `online_beta` et `stratum_rule` choisissent **exactement les mêmes actions** sur les 32 problèmes. Ce n'est pas un simple arrondi de score.

La candidate Omega vérifie les huit `DATA_SMALL` et les huit `CRT_SMALL`. Sur ces 16 appels, **10 aboutissent** (8+2) ; les six autres conduisent à l'abstention. Omega s'abstient sur tous les `CRT_LARGE` et `DATA_LARGE`. Elle ne publie aucune réponse fausse, mais ne fournit que 10 réponses sur 32. Cette amélioration du taux d'erreur des réponses publiées peut être reproduite **par une politique statique sans mécanisme adaptatif**.

## Alarme, mémoire et limitation scientifique

- L'extension candidate déclenche **0 alarme** sur le test ; son ablation sans alarme est indistinguable.
- Il n'existe donc **aucune preuve que la mémoire, l'identification d'un changement ou une révision de stratégie aient contribué** aux performances observées.
- La calibration de 16 exemples est **très petite**. Les tâches sont construites par l'auteur, sans validation indépendante ni véritable changement caché ; la taille/type de tâche est visible, et les petites/grandes catégories ont une couverture de vérificateur très différente.
- Les coûts sont artificiels et les outils de vérification sont déterministes et bornés ; ils sont incomplets, mais ne produisent pas de fausses conclusions quand ils aboutissent. Pas de véritable vérification documentaire faillible.
- L'extension candidate est **externe au P1 en production**, qui reste un planificateur statique ; aucun test de cette cohorte ne mesure la bibliothèque scientifique ou l'intelligence générale.
- **Contrôle exploratoire non pré-enregistré**, à ne pas intégrer aux scores primaires : rejeter gratuitement les réponses de mauvais type (ex. « B » pour CRT) donne 9 bonnes réponses, 15 fausses et 8 abstentions, utilité −20,6. Cela illustre qu'il existe encore des baselines simples à renforcer. Ce résultat post-hoc ne modifie pas l'hypothèse évaluée.

## Décision

**DÉMONTRÉ à portée restreinte :** exécution de 48 sorties réelles sur serveur distant sans API payante ; 8 politiques évaluées à budget égal ; oracle indépendant de la vérification bornée ; journal reproductible de toutes les actions ; amélioration de la fiabilité *conditionnelle à réponse publiée* par contrôle/abstention sur ce corpus.

**RÉFUTÉ sur cette expérience :** une plus-value propre aux alarmes adaptatives d'Omega. L'égalité complète avec `online_beta` et `stratum_rule`, et les **0 alarmes**, ne permettent pas d'attribuer la performance au mécanisme proposé.

**INDÉTERMINÉ :** bénéfice sur des modèles de capacité suffisante, sur des domaines variés non conçus par l'auteur, sur des vérificateurs imparfaits capables de résultats inexacts, et sur la mémoire scientifique réelle.

**Prochaine démarche :** avant d'accumuler des heuristiques de plus, **remplacer le générateur de réponses excessivement répétitif** par un second modèle libre plus capable ou des sorties de modèles déjà documentées et vérifiables, puis pré-enregistrer un test de *changement de fiabilité* où les observations auditables ne sont pas uniquement corrélées au type de problème. Un nouveau jeu indépendant et un témoin classique adaptatif fort restent nécessaires.

**Ne pas fusionner la politique candidate dans `main`**. Conserver cette PR en brouillon avec le résultat négatif, sans retoucher rétroactivement l'évaluation. PR #47–52 et les dossiers privés inchangés.
