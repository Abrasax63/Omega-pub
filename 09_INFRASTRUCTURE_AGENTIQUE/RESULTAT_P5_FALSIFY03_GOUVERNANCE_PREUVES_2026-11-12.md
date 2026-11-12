# P5-FALSIFY-03 — La preuve gouverne la décision : gain causal du filtre, pas d'avantage propre à Omega

**12 novembre 2026. Statut scientifique : TEST TECHNIQUE RÉEL REPRODUCTIBLE / EFFET DÉCISIONNEL DU FILTRE D'OBSERVABILITÉ ÉTABLI / GAIN PAR RAPPORT AU CALCUL EXACT CLASSIQUE NUL.**

## Sources et intégrité de l'expérience

- [Pré-enregistrement avant implémentation et génération de cette campagne](EXPERIMENT_P5_FALSIFY03_CERTIFIED_DECISION_PREREG_2026-11-12.md), commit `cb07022bdc60184f232a277faa086c95b1ade17b`. Aucun changement des politiques ni des 20 cas après lecture des résultats.
- [GitHub Actions #43252970924 — SUCCESS](https://github.com/Abrasax63/Omega-pub/actions/runs/43252970924) : **9 tests spécialisés réussis**, accord des deux oracles sur **57 344** systèmes finis, tests adversariaux de reçus falsifiés/périmés, puis **100 vraies inférences** de `Qwen/Qwen2.5-0.5B-Instruct` révision `7ae557604adf67be50417f59c2c2f167def9a775`, un forward CPU par bras et problème. [Suite RCE #43252971125 — SUCCESS](https://github.com/Abrasax63/Omega-pub/actions/runs/43252971125).
- [Archive primaire GitHub Actions](https://github.com/Abrasax63/Omega-pub/actions/runs/43252970924/artifacts/13960272031) : SHA-256 du ZIP `87f012d780e6c542f5086c3e5c8489940c15cbe0afa50e7e67ecb5262657e08a`. SHA-256 du fichier `falsify03_real_five_arm_results.json` : `ba897e55e80c0d82a088810dd68568ac9ec9e5b069f99b12e7e62fbf614088e8`. Cohorte gelée SHA-256 `803375caf98e0661ff6c3f5ef489c1a0f5367cf029d330ebed1443d0b436b9a9`.
- **Deuxième voie de recomptage**, distincte du code générateur : tous les **100 enregistrements** ont été recalculés localement à partir du JSON primaire, avec contrôles des 20 IDs appariés, 4 calibrations/16 tests, budgets, 40 certificats effectivement validés, prédictions brutes et décisions finales. Aucun écart avec les métriques primaires. Cette voie **n'est pas une revue humaine externe**.
- [Script du pilote](prism/p5_falsify03_governance.py) ; [9 tests adversariaux](prism/test_p5_falsify03_governance.py) ; [audit de prévalence indépendant](AUDIT_P5_FALSIFY03_UNIVERSE_N4_L4_2026-11-12.md) ; [recalcul apparié de FALSIFY02](AUDIT_P5_FALSIFY02_LOGITS_PAIRED_2026-11-12.md).

## 1. Univers et validité des deux calculs

Sur `X={0,1,2,3}`, `T:X→X` totale, `pi:X→{0,1}` non constante, mot observé de longueur 4, **256 × 14 × 16 = 57 344** instances. Le programme a comparé la **réalisation par un état initial énuméré** à la **succession des ensembles d'états survivants**, y compris leurs derniers états témoins, sur tout l'univers. Les 9 tests n'ont trouvé aucune divergence.

Un second calcul séparé a montré que l'univers uniforme contient **10 432 mots réalisables (18,19 %)** et **46 912 non réalisables (81,81 %)**. Le sous-échantillon de **4 calibrations (2/2) et 16 évaluations (8/8)** est **volontairement équilibré pour diagnostiquer l'interface**. Un classificateur toujours `B=impossible` atteindrait **81,81 %** sur l'univers uniforme et 50 % sur ce sous-échantillon. Les taux du pilote ne sont donc **pas généralisables** à cette population sans correction de prévalence. **Il ne s'agit pas d'un holdout scientifique aveugle**, puisque le code générateur connaît le gold et que les systèmes sont synthétiques.

## 2. Cinq bras, même modèle réellement exécuté

- **A** `direct` : un forward du modèle et décision A/B brute.
- **B** `classical_exact` : même prompt et même forward brut que A, puis énumération mathématique classique exacte gouvernant le verdict.
- **C** `omega_no_memory` : P1 et certificat exact, vérification de cohérence, gouvernance du verdict, **0 consultation de mémoire**.
- **D** `omega_no_observability` : P1 + contexte réel de mémoire RCE/P2 mais **aucun certificat ni calcul d'observabilité** ; verdict brut du modèle.
- **E** `omega_full_governed` : P1 + mémoire RCE/P2 + calcul du certificat à deux méthodes + contrôle de périmètre, puis gouvernance du verdict final.

Pour C/E : **deux algorithmes exacts sur les mêmes données T,π**, pas deux origines de données indépendantes. Le reçu lie `T,pi,word,scope` à un SHA-256 et comprend la liste des états initiaux témoins, les cardinalités successives et les états survivants finaux. Il est **revérifié sur la tâche courante**. Les tests adversariaux injectent une empreinte fausse, un périmètre périmé, une provenance impossible ou des témoins contradictoires : tous déclenchent **`ABSTAIN_INVALID_CERTIFICATE`**. Aucun certificat artificiellement corrompu n'a été injecté lors des 100 forwards réels : le mécanisme de rejet est validé par des tests logiciels, non une statistique d'incidents réels.

**P1 reste planificateur, P2 préparateur RCE, P3 enregistreur** ; les appels Qwen sont exécutés par le **nouveau runner expérimental**, pas par P3. Le corpus documentaire RCE n'est pas une preuve mathématique de l'instance courante.

## 3. Mesures réelles : 16 cas d'évaluation

| Bras | Bonnes réponses /16 | Différences de décision par rapport à E | Vraies inférences (cal+test) |
|---|---:|---:|---:|
| A modèle direct | **8/16** | **8** | 20 |
| B exact classique | **16/16** | **0** | 20 |
| C Omega sans mémoire | **16/16** | **0** | 20 |
| D Omega sans observabilité | **8/16** | **8** | 20 |
| **E Omega complet gouverné** | **16/16** | — | 20 |

**Les 100 inférences Qwen ont encore toutes prédit `A`**, sur les cinq variantes. Le gouverneur de C et E a corrigé **8 prédictions A qui étaient fausses** pour les huit cas où l'ensemble de survivants est vide. Le bras B classique corrige **exactement les mêmes huit erreurs**, avec un simple algorithme de recherche.

Ce résultat donne une différence **causale de procédure** entre D et E : avec filtre actif et gouvernance finale, 8 décisions sont changées ; sans filtre, elles ne le sont pas. En revanche **C=E pour les 16 cas**, malgré l'activation de la mémoire pour E : **aucun effet décisionnel propre à la mémoire n'est identifié**. Ni une variation des logits, ni une requête RCE exécutée, ni un hash de contexte ne suffisent à prouver un effet causal sur la réponse.

**Critère principal discriminant : `gain E − B = 0 réponse correcte`.** Nous n'avons donc **pas démontré une intelligence supérieure** ; nous avons démontré que le contrôle de validité peut faire respecter un calcul exact plutôt que laisser le modèle le négliger.

## 4. Coûts effectivement observés, pas seulement budget maximal égal

Les bras ont tous reçu **20 forwards Qwen**, un maximum de 512 tokens en entrée par appel. Leur consommation réelle est **inégale** :

| Bras | Tokens entrants (20) | Temps d'inférence modèle | Calculs exacts (nombre) | Cas avec mémoire |
|---|---:|---:|---:|---:|
| A | 3 420 | 24,534 s | 0 | 0 |
| B | **3 420** | **24,450 s** | **20** | 0 |
| C | 6 100 | 40,792 s | 80 | 0 |
| D | 7 020 | 45,908 s | 0 | 20 |
| **E** | **9 280** | **59,832 s** | **80** | **20** |

La mémoire a été véritablement consultée **une seule fois physiquement par question**, puis son résultat a été partagé entre D et E. Soit **20 appels P2, 60 recherches RCE, 131,976 s de temps RCE physique mesuré** pour l'ensemble des deux bras; **ne pas compter 40 appels P2 indépendants**. Leurs prompts utilisent ce même contexte documentaire. Les temps d'inférence modèle du tableau **n'incluent pas** la préparation P2 ; la mémoire rend donc E **encore plus coûteux** que le seul temps d'inférence ne le suggère. Les temps de calcul exact (< 0,003 s cumulés pour E) sont faibles comparés aux temps de Qwen et de RCE.

**Dans cette famille de tâches, B est au moins aussi exact que E, et moins coûteux en tokens et temps modèle.** E requiert également plus de calculs et une recherche mémoire additionnelle. L'utilité de l'architecture plus lourde n'est donc pas soutenue par ce pilote.

## 5. Lecture mathématique et statut de l'observabilité

L'ensemble de survivants
`B_0={x:pi(x)=y_0}`, `B_{k+1}={T(x):x∈B_k et pi(T(x))=y_{k+1}}`
est **exactement vide si et seulement si aucun état initial ne réalise le mot entier**. La vérification par énumération indépendante confirme l'exactitude dans les 57 344 cas testés. Le module de gouvernance ne publie le verdict que si la cohérence des **témoins globaux**, du périmètre et de la source est vérifiée.

Cette garantie est cohérente avec la démarche d'observabilité `Δ_h`, mais **elle ne démontre pas un nouveau théorème sur `Δ_h` ni une supériorité Omega sur Bayes/VOI/POMDP**. Le résultat est celui d'une **interface preuve → décision correctement câblée**, sur un problème où un calculateur classique plus léger est déjà complet.

## 6. Verdict strict et prochain verrou

**DÉMONTRÉ sur ce domaine fini :** deux calculs exacts concordent sur 57 344 cas, les certificats malformés sont rejetés par tests, le gouverneur peut corriger des décisions erronées du modèle (8/16 test), le pilotage par mémoire P2 ne change pas les décisions dans ce protocole, et un solveur exact classique égale la justesse du gouverneur avec moins de ressources mesurées.

**NON DÉMONTRÉ :** supériorité adaptative propre à Omega, effet utile de la mémoire scientifique, coût total à budget égal, validité sur des problèmes scientifiques nouveaux, gain contre des vérificateurs faillibles, et validation externe indépendante.

**Arrêter les répétitions des mondes finis à oracle exact universel comme tests principaux de supériorité.** Dans ces mondes, Omega ne peut pas dépasser 100 % d'exactitude, et faire tourner plusieurs agents ou davantage de prompts est coûteux sans créer d'information. La prochaine expérience devra **mettre réellement plusieurs vérifications incomplètes et coûteuses en concurrence**, avec données et corrections nouvelles, puis mesurer une décision sur les preuves sous budget contre un témoin classique optimisant la même valeur d'information. La mémoire devra apporter une information pertinente et testable, pas un extrait générique.

**Gouvernance : PR #66 en DRAFT ; aucune fusion dans `main`, aucune promotion de supériorité dans CORE.**
