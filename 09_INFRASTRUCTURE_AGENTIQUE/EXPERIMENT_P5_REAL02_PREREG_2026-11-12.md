# P5-REAL-02 — Pré-enregistrement : erreurs réelles diversifiées et changement de fiabilité

**12 novembre 2026 — gel AVANT création de l'exécuteur et avant toute génération de REAL-02.**

## Question falsifiable

Une politique Omega dotée d'une alarme sur l'évolution de la fiabilité de ses réponses, fondée uniquement sur des **vérifications effectivement payées**, surpasse-t-elle un contrôleur statique, un apprentissage classique en ligne et un estimateur décoté, à informations et budget identiques ? L'avantage propre au mécanisme d'alarme sera évalué par ablation. **Aucun gain présumé.**

Ce pilote corrige la faiblesse observée dans P5-REAL-01 (35 des 48 réponses étaient « B »), sans retoucher rétrospectivement ses résultats : nouvelle cohorte et consignes de réponse sans exemples de lettres non pertinents. Il ne teste pas l'intelligence générale ni la bibliothèque scientifique.

## Modèles et questions

Deux modèles ouverts, exécutés dans GitHub Actions CPU sur dépôt public, sans clé payante :
- `Qwen/Qwen2.5-0.5B-Instruct`, révision `7ae557604adf67be50417f59c2c2f167def9a775` ;
- `Qwen/Qwen2.5-1.5B-Instruct`, révision complète enregistrée depuis `model.config._commit_hash` au moment du test. Modèle Apache-2.0 officiel : https://huggingface.co/Qwen/Qwen2.5-1.5B-Instruct.

**96 inférences réelles** au maximum, `max_new_tokens=56`, génération déterministe `do_sample=False`. Quatre familles exactes, questions nouvelles construites par SHA256(`P5REAL02|kind|index|field`) :
1. `MUL` : multiplication de nombres de difficulté variée, entier exact ;
2. `CRT` : congruences à modules premiers entre eux, entier non négatif minimal ;
3. `RATE` : comparaison exacte de taux agrégés, réponse A/B ;
4. `INJ` : injectivité explicite d'une fonction finie, réponse OUI/NON.

**Calibration :** quatre questions par famille, indices 0–3, générées indépendamment par chacun des deux modèles = 32 sorties. **Évaluation :** pour le modèle 1,5B les indices 4–11, pour 0,5B les indices 12–19, huit questions **distinctes** par famille et modèle = 64 sorties. Aucun exemple de test n'apparaît dans la calibration, et aucune question n'est répétée dans le flux d'évaluation.

Le flux de 64 décisions est préfixé et caché aux contrôleurs : quatre phases de 16 cas `1,5B → 0,5B → 1,5B → 0,5B`, avec quatre cas de chaque famille par phase. **Le contrôleur ne reçoit ni le nom du modèle, ni le numéro de phase, ni l'index de la question, ni l'état caché de fiabilité.** Il reçoit seulement la famille, le texte, la sortie du modèle, la réponse parsée et les coûts. Chaque modèle est chargé séquentiellement pour réduire les besoins de mémoire ; ne jamais fusionner des réponses de modèles fictifs.

## Vérificateurs et anti-fuite

Les quatre familles ont des références indépendamment calculables par deux représentations : multiplication native vs addition répétée ; CRT inverse modulaire vs recherche brute ; RATE Fraction vs produits croisés ; INJ cardinalité de l'image vs collision par paires. Les références exactes servent au **correcteur** et à la calibration, mais jamais aux décisions de test non vérifiées. La vérification est effectivement exécutée et exacte sur ces familles ; elle n'est pas une simulation d'un outil documentaire imparfait. Un contrôleur peut recevoir l'issue **uniquement lorsqu'il exécute VERIFY** ; il peut savoir alors si la réponse du modèle était correcte. Sur DIRECT/ABSTAIN, aucun retour de vérité n'est révélé.

## Contraintes égales et utilités conventionnelles

Budget maximum **24 vérifications** sur 64 décisions par politique. Pour éviter que toutes les vérifications soient épuisées sur la première phase, chaque stratégie reçoit le même mécanisme public de **crédit progressif**, au maximum `floor((t+1)*24/64)` vérifications dépensables après l'index `t` (le crédit non utilisé se conserve). Le mécanisme repose sur l'index, pas sur les limites cachées des phases. Toute politique peut utiliser moins de 24 vérifications. Coûts de VERIFY : MUL=0,20, CRT=0,45, RATE=0,30, INJ=0,15 (unités **fictives**).

Score d'une réponse juste +1, fausse −2, abstention +0,05, vérification +1−coût. Sur une réponse non parsée, DIRECT équivaut à une abstention (0,05). VERIFY publie le verdict exact. Aucune « réussite du calculateur » n'est présentée comme gain propre à Omega.

## Contrôles préenregistrés

- `direct` : publier la réponse brute correctement extraite ;
- `abstain` : s'abstenir toujours ;
- `periodic` : vérifier dès qu'un crédit est disponible, sinon DIRECT ;
- `static_kind` : probabilité de réponse correcte calibrée par famille sur 32 réponses, sans adaptation ;
- `online_beta` : mise à jour par famille avec toutes ses vérifications, sans oubli ;
- `discount_beta` : pondération exponentielle `gamma=0,70` des derniers retours vérifiés, par famille ;
- `omega_candidate` : utilise exactement `online_beta`, mais déclenche une alarme si au moins **6 confirmations** vérifiées (toutes familles), et si `abs(mean_last_6_correct - mean_calibration_correct)>0,35`. Après alarme, estime les probabilités par famille à partir des **six dernières observations vérifiées disponibles de la famille** ; si moins de deux, revient à `online_beta`. L'alarme cesse dès que la différence sur les six derniers retours redescend à `0,20` ou moins. Une alarme n'obtient aucun retour gratuit ; tout changement de choix est journalisé ;
- `omega_no_alarm` : ablation du même estimateur, sans alarme, **doit correspondre à online_beta**.

Pour les politiques probabilistes : prior de Laplace (1 réussite, 1 échec fictifs). `p=(correct+1)/(n+2)` ; utilité DIRECT `3p−2` si réponse parsée, sinon 0,05 ; VERIFY `1−coût` si crédit et budget ; ABSTAIN=0,05. Égalités : ABSTAIN, puis DIRECT, puis VERIFY. Les labels de calibration sont disponibles **à tous**. Ni tokens ni précision « déclarée » par le modèle ne constituent une preuve.

## Mesures et échec

**Primaire :** `total_utility(omega_candidate) − total_utility(discount_beta)` sur 64 cas de test, avec `online_beta` et `static_kind` comme contrôles supplémentaires. Reporter nombres de réponses justes/fausses publiées, abstentions, vérifications, dépenses, gain par phase (uniquement l'évaluateur connaît les phases), alarmes et **nombre de décisions effectivement différentes** entre candidat Omega et son ablation. Comparaison appariée déterministe ; pas d'intervalle de confiance prétendant couvrir les tâches du monde réel.

**Réfutation pré-enregistrée :** ne pas revendiquer de gain spécifique si `omega_candidate` n'améliore pas `discount_beta` et `online_beta`, si les alarmes ne changent aucune décision, ou si le modèle amélioré reste incapable de produire des réponses suffisamment diversifiées. Les éventuels changements de performance doivent être interprétés à l'aune de la fiabilité des modèles, pas uniquement de la stratégie.

## Contraintes d'exécution et statut

Un seul passage et deux modèles séquentiels, CPU runner GitHub Actions standard sur repo public, **0 OpenAI API / 0 coût API / 0 calcul smartphone**. Échec de l'installation, absence des 96 générations ou désaccord entre oracles => `INCOMPLETE` ; aucune conclusion sur Omega. Statut réussi `PUBLIC_REAL_MULTIMODEL_EXPLORATORY_NOT_INDEPENDENT`. Jeu public conçu par l'auteur, sans validation externe indépendante, aucun holdout privé, pas d'intégration dans `main`. Le Prisme P1 actuel est un planificateur : la candidate d'alarme n'est pas une capacité déjà démontrée du système complet.
