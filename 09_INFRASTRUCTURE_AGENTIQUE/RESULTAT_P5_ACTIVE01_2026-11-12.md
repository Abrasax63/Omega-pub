# P5-ACTIVE-01 — choix actif de preuves sous budget : audit et échec d'identifiabilité

**12 novembre 2026 — statut : INFÉRENCE RÉELLE REPRODUCTIBLE ; AVANTAGE ADAPTATIF NON DÉMONTRÉ ; BENCHMARK NON DISCRIMINANT POUR LES POLITIQUES FORTES.**

## Sources et protocole

- Pré-enregistrement **avant code et avant inférence** : [EXPERIMENT_P5_ACTIVE_VOI_PREREG_2026-11-12.md](EXPERIMENT_P5_ACTIVE_VOI_PREREG_2026-11-12.md), commit `053ad19942ae9edc811b12b47901dd315dae7ff7`.
- [GitHub Actions #43214660818 — SUCCESS](https://github.com/Abrasax63/Omega-pub/actions/runs/43214660818) : **8 tests** passés, **96 inférences réelles** (un appel forward, deux scores de prochain token A/B par question) et dix politiques dont une référence a posteriori non déployable.
- [Archive JSON originale avec scores des modèles, 16 lots, actions et feedback](https://github.com/Abrasax63/Omega-pub/actions/runs/43214660818/artifacts/13943231674). Empreinte SHA-256 du ZIP archivé téléchargé : `1ce10fe754053e5cd24e17568b0798d4dbf1b091d01d6800930d72cc2bb30d8b`.
- Empreinte des 96 entrées publiques : `6737d2e28b9437162763c2de050ca4e988863a09b8d4cb6d278610aa1927e038`.
- Modèles : Qwen2.5-0.5B-Instruct révision `7ae557604adf67be50417f59c2c2f167def9a775` et Qwen2.5-1.5B-Instruct révision `989aa7980e4cf806f80c7fef2b1adb7bc71aa306`. **0 API OpenAI, 0 calcul sur téléphone, 0 dataset privé**.
- **Important** : les 96 appels sont des **scores de prochain token contraints à A ou B**, pas des générations libres. Le problème de parsing des REAL-02/03 a été supprimé *par construction*, mais les logits A/B peuvent être biaisés ou mal calibrés ; aucune vérité n'est donnée au sélecteur.
- Quatre domaines MUL, CRT, RATE, INJ, 80 questions mathématiques uniques, vraies/fausses équilibrées par construction, **deux oracles exacts concordants**. Calibration de 32 sorties, test de 64 sorties sur 16 lots de quatre réponses, dont **une seule peut être vérifiée** par lot.
- Chaque politique voit les mêmes informations disponibles et son propre flux de résultats des vérifications achetées. La vérité des réponses non vérifiées est réservée à l'évaluation : ce sont les mêmes **possibilités** d'observation, non des historiques identiques une fois les politiques divergentes.

## Résultat des modèles de base

Sur les 64 questions de test, **34/64 choix A/B corrects** : MUL 9/16, CRT 9/16, RATE 8/16, INJ 8/16. Qwen 0,5B 16/32 corrects, Qwen 1,5B 18/32 corrects dans ce jeu spécifique.

Le score de confiance est la probabilité A/B **renormalisée sur deux tokens seulement**, pas la probabilité calibrée que la réponse soit vraie. Contrôle descriptif sur le test : score de Brier du choix retenu par rapport à sa correction : Qwen 0,5B **0,264**, Qwen 1,5B **0,291** ; une prédiction constante de correction 0,5 aurait Brier **0,25** sur ces cas équilibrés. Cela suggère une mauvaise calibration sur ce petit corpus, sans établir la calibration générale des modèles.

## Scores officiels des politiques

Utilité conventionnelle : exact publié +1, incorrect publié −2, abstention +0,05, vérification +1 moins coût (INJ 0,20 ; MUL 0,25 ; RATE 0,30 ; CRT 0,40). **Unités fictives**.

| Politique | Utilité totale | Vérifications | Réponses exactes publiées | Fausses publiées | Abstentions |
|---|---:|---:|---:|---:|---:|
| Aucune vérification | +3,20 | 0 | 0 | 0 | 64 |
| Vérifier la première candidate du lot | +13,85 | 16 | 16 | 0 | 48 |
| Rotation des familles | +13,80 | 16 | 16 | 0 | 48 |
| VOI statique | **+15,20** | 16 | 16 | 0 | 48 |
| VOI en ligne | **+15,20** | 16 | 16 | 0 | 48 |
| VOI avec décote | **+15,20** | 16 | 16 | 0 | 48 |
| VOI avec score/marge du modèle | **+15,20** | 16 | 16 | 0 | 48 |
| Omega candidat | **+15,20** | 16 | 16 | 0 | 48 |
| Omega sans révision | **+15,20** | 16 | 16 | 0 | 48 |
| Oracle omniscient *a posteriori* | +44,30 | 12 | non comparable | non comparable | non comparable |

**Critère primaire : Omega − VOI décotée = 0,00.** Omega − VOI marge = 0,00. Omega sans révision prend les mêmes **64 actions** ; **0 alarme** et **0 décision imputable à la révision**. Ce mécanisme candidat est réfuté pour cette campagne ; aucune performance de la mémoire scientifique réelle n'a été testée.

### Nouvelle découverte causale — algèbre de la dégénérescence

Les estimations Laplace issues des 8 calibrations par famille étaient :

| Famille | Succès calibration | p Laplace | Gain marginal de VERIFY avant toute nouvelle observation |
|---|---:|---:|---:|
| MUL | 5/8 | 0,600 | 0,700 |
| CRT | 4/8 | 0,500 | 0,550 |
| RATE | 4/8 | 0,500 | 0,650 |
| INJ | 4/8 | 0,500 | **0,750** |

Le protocole choisissait DIRECT seulement si `3p−2 > 0,05`, soit **p > 2,05/3 ≈ 0,6833**. En dessous de ce seuil, toutes les politiques préfèrent ABSTAIN à DIRECT ; **le gain de vérification devient mathématiquement `0,95 − coût`**, *indépendant de la valeur de p*. Avec nos quatre coûts, **INJ domine mécaniquement**. Les vérifications choisies n'ont pas déplacé le posterior assez fortement pour franchir ce seuil : **six politiques VOI ou assimilées ont vérifié INJ dans les 16/16 lots**, laissé les 48 autres réponses en abstention, même lorsqu'elles disposaient de scores ou d'actualisations différents.

Les 16 contrôles INJ donnent 16 vérités exactes publiées, coût 16×0,20 ; les 48 abstentions rapportent 48×0,05 : **16×0,80 + 48×0,05 = 15,20**. Les scores positifs de ce jeu sont donc des **résultats du vérificateur exact**, pas une découverte d'intelligence adaptative.

Le fait qu'il existe **neuf patterns de choix** au total masque le problème : la diversité provient des contrôles naïfs (première candidate et rotation), pas des **six politiques fortes qui sont parfaitement confondues**.

L'outil de diagnostic explicite `prism/p5_active01_design_gate.py` renvoie **FAIL_NON_DISCRIMINATING** quand toutes les politiques fortes choisissent la même famille dans ≥14/16 lots ou exactement la même séquence ; ses quatre tests de non-régression ont réussi dans [workflow léger #43215870809](https://github.com/Abrasax63/Omega-pub/actions/runs/43215870809).

## Recherche bibliographique et ce qui existe déjà

- Gong & Zhang, [ICML/PMLR 2026](https://proceedings.mlr.press/v306/gong26i.html) : compromis minimax des observations payantes, meta-contrôleur adaptatif — ceci dépasse le simple VOI myope implémenté ici.
- Tucker et al., [UAI/PMLR 2023](https://proceedings.mlr.press/v216/tucker23a.html) : bandits avec feedback coûteux et exploration adaptative ; le coût d'observation affecte les bornes de regret.
- Snell et al., [ICLR 2025](https://proceedings.iclr.cc/paper_files/paper/2025/hash/1b623663fd9b874366f3ce019fdfdd44-Abstract-Conference.html) : allocation du calcul d'inférence selon la difficulté.
- Iyengar, [SPLIT, arXiv:2610.23255 (prépublication, octobre 2026)](https://arxiv.org/abs/2610.23255) : allocation entre génération et vérification sous vérificateurs imparfaits et corrélés. Ce résultat préliminaire nécessite une confirmation de son statut de publication pour toute revendication.

**Aucune nouveauté scientifique n'est démontrée par le routage myope.** La difficulté pertinente est de donner une valeur **aux informations acquises pour les décisions futures**, d'empêcher l'auto-sélection exclusive des outils familiers et de mesurer les erreurs des vérificateurs.

## Modification de méthode validée, sans nouveau score de modèle

- **STOP** sur tout test coûteux qui ne passe pas une porte de diversité des choix **avant** le lancement de nouvelles inférences. Le système doit vérifier sur calibration qu'au moins deux méthodes solides demandent des preuves sensiblement différentes et que des familles différentes sont explorées.
- **Baselines à implémenter dans un nouveau protocole** : meilleur calcul myope VOI exact, estimation bayésienne avec incertitude, `Thompson sampling` ou `UCB` avec observations payantes, apprentissage décoté, choix statique fondé sur coût ; comparer le coût de l'exploration et la précision/abstention.
- **Rendre les contextes authentiquement discriminants** : plusieurs outils de fiabilité imparfaite, résultats incertains et valeurs de conséquences différentes, plutôt que vérificateur mathématique parfait toujours préférable. Les coûts et impacts doivent être fixés avant les sorties du prochain corpus, non optimisés pour favoriser Omega.
- **Vraie validation nouvelle et indépendante** avant affirmation : ne pas réutiliser ces 96 sorties connues pour choisir des seuils puis les présenter comme test aveugle.

**Statuts : logiciel vérifié ; résultat de modèle réel limité ; absence d'avantage spécifique ; FAIL_IDENTIFIABILITÉ du benchmark.** La candidate n'est pas le planificateur P1 déployé. **PR DRAFT, ne pas fusionner `main`.**

## Note de dépense CPU

Le workflow coûteux de 96 forwards a été converti en `workflow_dispatch` **manuel uniquement** (commit `eb233fbab0144ad1905ef0cc8065e020cb401ff6`) ; les PR et les changements de rapport déclenchent seulement les tests rapides. Cela évite de relancer automatiquement des modèles coûteux après chaque modification documentaire. Des exécutions supplémentaires déjà parties avant cette protection restent des **répétitions techniques exclues de toute analyse**.
