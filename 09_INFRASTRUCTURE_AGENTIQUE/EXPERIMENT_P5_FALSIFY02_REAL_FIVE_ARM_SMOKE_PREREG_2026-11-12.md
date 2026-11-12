# P5-FALSIFY-02 — Pré-enregistrement du pilote d'intégration à cinq bras et modèle réel

**12 novembre 2026 — gel avant code et génération de nouveaux résultats.** Succède à [PR #64, FALSIFY-01](https://github.com/Abrasax63/Omega-pub/pull/64) : le contrôle de préparation a constaté que P1 planifie, P2 prépare la mémoire mais P3 n'exécute pas les appels de modèle. **Cette étude ajoute un exécuteur EXPÉRIMENTAL distinct, sans le confondre avec un Omega déployé.**

## Question technique, non promesse scientifique

Sur les **mêmes questions de systèmes finis**, les cinq variantes passent-elles réellement par le même modèle ouvert, les ablations activent-elles des mécanismes différents et les décisions changent-elles ? Peut-on ensuite constater le rôle d'un filtre d'états survivants contre un témoin de calcul classique ?

**Ce n'est PAS la validation d'une « intelligence supérieure » :** monde synthétique à 3 états, problèmes générés par code connu, une seule famille de tâches, oracle exact accessible au programme, P1 utilisé pour ses recommandations, P2 lecture RCE et P3 non connecté à l'exécution. Un modèle à prompt enrichi peut recevoir directement la réponse du filtre. Il faut l'indiquer dans tous les résultats.

## Cas et oracle avant modèle

- Monde autonome (X={0,1,2}), `T:X→X` totale et observation binaire `π:X→{0,1}` non constante.
- Tâche : déterminer si le **mot observé de longueur 3** est réalisé par au moins une trajectoire `π(x),π(Tx),π(T²x)`. Format final exactement `A` = possible, `B` = impossible.
- Deux oracles algorithmiquement distincts doivent toujours coïncider : (i) énumération directe sur les trois états initiaux, (ii) filtre `B_{i+1}=T(B_i)∩π^{-1}(y_{i+1})`.
- Cas témoin de recollement classique `T=(0,2,2), π=(0,0,1), y=(0,0,1)` **forcé en calibration uniquement**.
- Énumérer 27 fonctions T, 6 observations binaires non constantes, 8 mots, sélectionner selon le tri du SHA-256 des champs publics, équilibré par vérité **seulement pour un PILOTE d'intégration**, non holdout aveugle : **8 calibrations (4 A/4 B) et 32 évaluations (16 A/16 B)**, sans répétition de triplet.
- Tous les prompts affichent T, π et le mot ; le gold exact reste hors prompt et n'est utilisé qu'après inférence. Les candidats et le code générateur seront publics. Les réponses ayant une structure similaire aux travaux antérieurs sont explicitement **synthétiques**.

## Les cinq bras EFFECTIVEMENT exécutés

- A `direct` : exactement une inférence réelle Qwen2.5-0.5B-Instruct par cas, sans contexte externe.
- B `classical_exact` : **même inférence** et même entrée brute que A, mais réponse finale décidée par un **calculateur classique exact sur T,π**. Son calcul est un outil, facturé et tracé. C'est un **plafond fort et atteignable pour les tâches finies**, non un comparateur de même consommation d'outil si le coût est ignoré.
- C `omega_no_memory` : vrai plan `P1`, **vrai filtre d'états survivants**, aucune lecture P2; une inférence du même modèle enrichie d'un certificat de faisabilité.
- D `omega_no_observability` : vrai plan `P1`, recherche RCE via `P2` avec **contexte documentaire générique strictement limité**, aucun appel du filtre; inférence du même modèle.
- E `omega_full_candidate` : vrai plan `P1`, recherche RCE via `P2`, filtre d'états survivants; inférence du même modèle. Les fonctions sont **une nouvelle couche expérimentale**, PAS le planificateur déployé ni un sous-agent.
- Le contexte P2 peut être partagé entre D et E sur le même cas pour éviter les téléchargements redondants, mais **chacun doit déclarer une lecture de mémoire** ; cette mise en cache et son coût devront être explicités, interdisant toute affirmation d'égalité parfaite de ressources.
- Même modèle, révision FIXE `Qwen/Qwen2.5-0.5B-Instruct@7ae557604adf67be50417f59c2c2f167def9a775`, `transformers==4.51.3`, `torch==2.6.0`, score contraint sur deux labels A/B à un pas de sortie, pas de parsing de prose. Définir précisément les token IDs et conserver leur logit. 40 cas × 5 = **200 forwards CPU réels**.
- Tous les bras sont limités à **512 tokens d'entrée**, une décision de sortie, aucune API payante. Tokens exacts et temps CPU par bras mesurés : le plafond est égal, les dépenses effectivement consommées peuvent différer. Les outils `B`/`C`/`E` doivent compter un appel exact; la recherche P2 pour `D`/`E` doit être journalisée.

## Résultats attendus et critères de validité

- Aucune garantie de gain : B devrait obtenir **40/40** sous la définition exacte du problème. Omega E ne peut légitimement prétendre améliorer cette résolution parfaite; son coût probablement supérieur doit être affiché. Le résultat B est une **borne de calcul classique atteignable**.
- Rapporter nombres de modèles réellement appelés par bras, usage mémoire, filtre, taux de réponse correcte, **différences de décision C vs E, D vs E**, tokens et latences. Si des prompts changent sans différence de réponse, `ABLATION_NOT_IDENTIFIED_AT_DECISION`; si le filtre donne directement la vérité, signaler `EXACT_TOOL_ORACLE_SUPPLIED`.
- Vérifications avant l'inférence : 40 cas tous distincts, 2 oracles exacts, aucun gold dans les prompts; deux politiques ne doivent pas être des alias stricts; prompt et source versionnés; pas de modification des seuils en cours de campagne.
- **Pas d'inférence de significativité** sur 32 tâches corrélées générées par code ; pas de comparaison générale de mémoire scientifique ni de « compréhension » des preuves. La vraie expérience multi-domaines de 160 problèmes avec revue indépendante reste **NON PRÊTE** selon la PR #64.

## Gouvernance et arrêt

GitHub Actions libre/CPU, sans facturation API, temps de 30 minutes max, aucune donnée privée, artefact JSON brut non modifié et rapport indépendant des journaux. Arrêter sur échec d'empreinte modèle, fuite de vérité, budget dépassé, double oracle contradictoire. Conserver PR DRAFT, aucune fusion `main`, aucune conclusion CORE.

Statut prévu `REAL_FIVE_ARM_LLM_INTEGRATION_SMOKE_SYNTHETIC_EXACT_TASKS`. Aucune revendication de supériorité générale Omega ne peut être établie par cette expérience.
