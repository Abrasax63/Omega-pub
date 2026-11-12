# P5-OBS-02 — observabilité, causes communes et vérifications imparfaites

**12 novembre 2026 — Verdict : CALCUL EXACT VALIDÉ et REJEU REPRODUCTIBLE ; PLUS-VALUE PROPRE À OMEGA NON DÉMONTRÉE.**

## Preuves d'exécution et provenance

- [Protocole pré-enregistré AVANT implémentation et calcul OBS-02](EXPERIMENT_P5_OBS02_PREREG_2026-11-12.md), commit `6e5d4dd02792d167caf93cf9a145d9e14fe99490`.
- [CI GitHub Actions #43222140065 : SUCCESS](https://github.com/Abrasax63/Omega-pub/actions/runs/43222140065), **8 tests spécialisés réussis**. La suite générale RCE [#43222140270 : SUCCESS](https://github.com/Abrasax63/Omega-pub/actions/runs/43222140270).
- [Archive brute JSON : 64 cas × 8 politiques, observations autorisées, postérieurs rationnels et traces](https://github.com/Abrasax63/Omega-pub/actions/runs/43222140065/artifacts/13945403425). SHA-256 du ZIP téléchargé : `e02357d3e4a2665a346a389e5cfe675253f8bc0c958bd172b8c19be94f10c08d`.
- Données réelles : uniquement les **96 choix binaires A/B préexistants** des deux modèles Qwen de [P5-ACTIVE-01, run #43214660818](https://github.com/Abrasax63/Omega-pub/actions/runs/43214660818), dont 32 calibrations et 64 tests. Aucun modèle n'a été réexécuté. Les réponses et corrections ont été conservées dans `prism/obs02_frozen_qwen96.zlib.b64`, avec SHA-256 du flux JSON compact décompressé `35d100beafc5f46dd2b4e971a20e44e671410df6fe284c3ddc53278d86d0311c`.
- **Les erreurs des outils de vérification sont SIMULÉES**, par SHA256 sur les identifiants des problèmes et trois mécanismes latents indépendants ; elles ne sont **pas les erreurs observées d'un fournisseur réel**. Le jeu de réponses Qwen était déjà connu du programme de recherche, donc ceci est un **rejeu exploratoire**, pas un holdout indépendant.
- Première CI #43221853000 : échec technique dû à un caractère manquant dans le flux base64 compact, corrigé sans changement des règles ni des données d'origine ; [commit correctif `98ec60bc720b9d77cfd914111ffbbf576b0d0a27`](https://github.com/Abrasax63/Omega-pub/commit/98ec60bc720b9d77cfd914111ffbbf576b0d0a27). La CI corrigée et la suite RCE sont toutes deux vertes.

## Lien avec nos théorèmes d'observabilité

Dans notre travail précédent, `B_{i+1}=T(B_i)∩π^{-1}(y_{i+1})` conserve les **témoin(s) microscopiques compatibles** avec une suite d'observations et refuse les raccordements fictifs. Voir [DELTA_H_RECOLLEMENT_INTERNE_2026-09-29.md](../02_MATHEMATIQUES/defauts_recollement/sources/DELTA_H_RECOLLEMENT_INTERNE_2026-09-29.md).

OBS-02 n'applique **pas** directement ce théorème autonome à des preuves probabilistes. Il l'emploie comme **principe de cohérence** pour construire un postérieur exact sur `(C,Z,D,M)` où :

- `C` indique que la réponse de Qwen est correcte (donnée vraie du replay, cachée à la politique) ;
- `Z` est le défaut commun aux deux vérificateurs corrélés `SHARED_A` et `SHARED_B` ;
- `D` est une erreur d'un troisième vérificateur ;
- `M` entraîne la non-résolution `UNKNOWN`.

Les politiques connaissent les lois **supposées** `P(Z=1)=P(D=1)=P(M=1)=1/4` et le prior `P(C=1)` tiré de la calibration par famille, mais elles ne connaissent jamais les réalisations cachées ni les issues des outils non achetés. Elles ont droit à **deux vérifications distinctes maximum par question**. Les coûts 0,03 / 0,04 / 0,08 / 0,80 sont des unités d'utilité fictives.

### Certificat de dépendance : preuve mathématique dans ce micro-modèle

Quand `p=P(C=1)=1/2`, la première réponse `SHARED_B=1` donne `P(C=1|SHARED_B=1)=3/4`. La seconde copie `SHARED_A=1` ne change **rien** : `P(C=1|SHARED_B=1,SHARED_A=1)=3/4`, puisque les deux outils renvoient **le même** `C XOR Z`.

Un calcul **incorrect** qui suppose les copies indépendantes donne à tort `9/10`. Pire, le chemin `SHARED_B=1,SHARED_A=0` est impossible dans la sémantique annoncée : la masse du postérieur est **nulle** ; le moteur le rejette plutôt que fabriquer une conclusion. Ce contrôle est proche, par sa logique de **témoin global**, de nos fantômes de recollement, mais ne constitue **pas** un nouveau théorème sur `Δ_h`.

Le signal `UNKNOWN` du vérificateur indépendant renseigne `M`, **sans modifier la probabilité marginale de correction C**, puisqu'il est indépendant de C dans ce modèle. Il n'est donc ni une preuve d'erreur ni une preuve de justesse.

## Vérification mathématique indépendante de la stratégie optimale

Deux implémentations **distinctes** — Bellman récursif avec fractions exactes et énumération exhaustive des politiques contingentes à deux niveaux — aboutissent **sans aucun arrondi** à :

| Probabilité initiale `P(C=1)` | Domaines | Valeur optimale espérée par problème, coûts déduits |
|---|---|---:|
| `3/5` | MUL | `31/100` = **0,310000** |
| `1/2` | CRT, RATE, INJ | `943/3200` = **0,294688** |

Sur 16 questions MUL et 48 autres, l'espérance **sous le modèle supposé** est `3821/200 = 19,105` d'utilité nette totale. La réalisation déterministe du rejeu sur 64 questions peut différer de cette espérance : ce n'est pas un test de calibration des fournisseurs réels.

## Résultats du rejeu sur 64 sorties authentiques de Qwen

**Gain total réalisé sous corruption ARTIFICIELLE des vérifications** ; +1 pour une réponse finale correcte, −2 pour fausse, +0,05 pour abstention, moins coût des sondes.

| Stratégie | Utilité nette | Correctes publiées | Fausses publiées | Abstentions | Vérifications |
|---|---:|---:|---:|---:|---:|
| Aucune preuve | **3,20** | 0 | 0 | 64 | 0 |
| Deux preuves communes, dépendance reconnue | **14,02** | 42 | 12 | 10 | 128 |
| Deux preuves communes, indépendance inventée | **14,52** | 49 | **15** | 0 | 128 |
| Deux sources distinctes fixes | **17,91** | 38 | 7 | 19 | 128 |
| Entropie sur micro-état | **17,91** | 38 | 7 | 19 | 128 |
| Valeur de l'information myope | **20,84** | 46 | **6** | 12 | 122 |
| **DP bayésien exact standard** | **20,84** | 46 | **6** | 12 | 122 |
| **Omega certificat de provenance** | **20,84** | 46 | **6** | 12 | 122 |

Le candidat Omega, le DP classique et la VOI myope ont pris **exactement les mêmes décisions** sur les 64 cas. Ils commencent par `SHARED_B` pour tous les cas, puis choisissent selon la réponse **48 fois INDEPENDENT, 10 fois GOLD et 6 fois STOP** ; leurs traces comportent **15 résultats UNKNOWN** sur 48 vérifications indépendantes.

La politique **naïve** publie trois réponses fausses supplémentaires par rapport à la même stratégie reconnaissant la corrélation (15 contre 12), malgré une utilité totale réalisée **légèrement plus haute** (14,52 contre 14,02). Ce constat n'est pas paradoxal : elle répond davantage (0 abstention) et le score moyen combine récompenses et pénalités. **Ne pas affirmer qu'elle est dominée en utilité sur toutes les réalisations** ; sa **surconfiance probabiliste** est prouvée, pas une domination décisionnelle universelle.

### Interprétation et limites critiques

1. **DÉMONTRÉ sous hypothèses explicites** : le deuxième instrument partageant `Z` n'ajoute aucune information ; les contradictions `1 puis 0` sont impossibles. Le filtrage refuse le témoin incohérent. Il ne faut pas compter deux fois la même preuve.
2. **CALCUL EXACT VALIDÉ** : équivalence de deux solveurs indépendants pour les quatre calibrations, traçabilité de la totalité des vérifications payées, tests de budget et d'absence de fuite du secret au contrôleur.
3. **REJEU EXPLORATOIRE** : amélioration d'utilité du candidat par rapport aux contrôles qui achètent inutilement des doublons ; mais **égalité** avec Bayes standard et avec la VOI myope ici. L'effet ne prouve **ni un avantage Omega, ni une complémentarité non myope dans OBS-02** ; celle-ci avait été illustrée par OBS-01, pas par le présent micro-modèle.
4. **OUTILS NON RÉELS** : les réponses Qwen sont authentiques, les 25% de faux signaux et d'inconclusifs sont artificiels et connus à l'avance ; la bibliothèque scientifique n'a pas été utilisée comme base d'observations contradictoires. L'optimiseur supposait la structure causale exacte, non apprise.
5. **PRISME P1** : `planner.plan_mission` indique seulement qu'il faut vérifier et justifie l'action dans le journal ; la distribution de croyance et le DP sont une **nouvelle couche de démonstration**, pas une faculté déjà démontrée du prisme.

## Nouvelle direction de recherche

Plutôt que multiplier les simulateurs ou les alarmes, la prochaine expérience réellement discriminante devrait utiliser des **journaux authentiques de plusieurs méthodes de vérification**, avec erreurs, citations, refus et désaccords effectivement constatés, pour apprendre les dépendances au lieu de les connaître par construction. La politique devra annoncer **son hypothèse de source commune** et tester sur des cas nouveaux si elle évite des erreurs que les contrôles bayésiens sur les mêmes données n'évitent pas.

Ce module fournit désormais une **interface testée de preuve et de refus de témoin impossible** qui peut être réutilisée dans Omega après audit. **Ne pas le fusionner dans `main`, ne pas le déclarer original par rapport aux POMDP ou aux systèmes d'observabilité existants et ne pas promouvoir la thèse de supériorité dans CORE.**

### Bibliographie externe

- [Norman, Parker, Zou (2017), Verification and control of partially observable probabilistic systems](https://doi.org/10.1007/S11241-017-9269-4).
- [From Reactive to Active Sensing (2023), revue de l'acquisition d'information en planification décisionnelle](https://doi.org/10.1145/3583068).
- [Tucker et al. (2023), Bandits with costly reward observations](https://proceedings.mlr.press/v216/tucker23a.html).
