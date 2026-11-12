# P5-EVID-06 — sélection de vérifications SQL sous budget et trois nouveaux faits exécutés sur BIRD

**12 novembre 2026 — Verdict : REJEU DE DÉCISIONS SUR SORTIES RÉELLES + TROIS VÉRIFICATIONS SQL SUR BASE RÉELLE ; AUCUN AVANTAGE ADAPTATIF PROPRE À OMEGA.**

## 1. Provenance, pré-enregistrement, exécutions

- [Protocole enregistré AVANT code et nouvelle évaluation](EXPERIMENT_P5_EVID06_BUDGETED_ROUTING_PREREG_2026-11-12.md), commit `3af58758a14d5ab33db850cd4074e7a382074a87`. Les trois nouveaux claims de contrôle #15601, #3730 et #3971 ont été fixés avant exécution de leurs SQL. Les annotations publiques étaient déjà consultables et connues, donc **pas de holdout indépendant**.
- [GitHub Actions #43237122391 — SUCCESS](https://github.com/Abrasax63/Omega-pub/actions/runs/43237122391) : **9 tests spécialisés passés** ; comparaison de 64 vraies paires de sorties historiques, 8 lots de 8 et budget de 2 consultations par lot, plus exécution de 2 SQL pour chacun des 3 nouveaux fragments sur la vraie base BIRD.
- [RCE général #43237121933 — SUCCESS](https://github.com/Abrasax63/Omega-pub/actions/runs/43237121933).
- [Archive des trajectoires des politiques et sorties SQL, avec empreintes](https://github.com/Abrasax63/Omega-pub/actions/runs/43237122391/artifacts/13952881813). [Code de routage](prism/p5_evid06_budgeted_routing.py), [code du second contrôle SQL](prism/p5_evid06_bird_extra_sql.py), [tests](prism/test_p5_evid06_budgeted.py).
- Source de référence : Theologitis et al., [ClaimDB (ACL 2026)](https://aclanthology.org/2026.acl-long.1589/), commit `e06c3a22cc14a8ef6858bb5d40bca7925241b98d`. Les trois fichiers originaux **réellement téléchargés par Git LFS depuis les auteurs** ont eu leurs SHA-256 vérifiés avant analyse :
  - 1000 labels : `b87d7062307cfcf5ae862bf03bd7e82f7123ff39cf0b69d3dc5cc25caaaea810`
  - 1000 sorties GPT-5-mini avec SQL : `e31443bd85f46c4edc4a146243bb709634c6330c2914c726630c3f3349edb100`
  - 1000 sorties GPT-5-mini sans SQL : `552531cba335298816a998f7a2b6fb548d9cd0eb7f9b47e5d1272809620a9aa6`.
- Base BIRD `superhero.sqlite`, conservée **uniquement dans le runner temporaire**, source publique de [Tarzanagh/QAFD-RAG](https://github.com/Tarzanagh/QAFD-RAG/tree/2a3a42c8ea4e9c416de0a7fe53c04fab50b756ef/data/text2sql/bird/databases/superhero), Git blob `4cfbee0ba8b6033a7415184caff90d363fe444c2`, SHA-256 `75e94a2c3236ee3bb2c01fb97a1c4b4c1c269bcefd4eab1d04be323d2d0825b1` ; **aucun binaire redistribué**.
- Aucune API payante, aucune nouvelle génération de modèle, aucune donnée privée.

## 2. Comparaison de sélection sous budget — résultats officiels

Échantillon **déterministe par SHA-256 sur les seuls IDs**, sans tri par label, au sein de 120 claims `superhero` : 8 sentinelles exclues, **24 calibrations et 64 évaluations**. Empreinte de sélection : `e9e62effc3fa4d7151dda956e38ecea1e3dc55529b42cb77fb028c0040f0144a`. Huit lots de huit ; **deux requêtes « avec SQL » au maximum par lot**, 16 achats sur 64 cas. Les sorties « avec SQL » sont celles **historiquement produites par GPT-5-mini** : elles ne sont **pas des verdicts SQL indépendamment recalculés**. Le contrôleur ne voit ni cette réponse ni le label avant l'achat, uniquement le texte, son contexte lexical, la réponse sans outil et le coût.

### Calibrations et portée

| Catégorie lexicale | Cas calibration | p de réponse sans outil correcte (Laplace) | p avec SQL correcte (Laplace) |
|---|---:|---:|---:|
| Global | 24 | 0,4231 | 0,9231 |
| Nombre / calcul | 11 | 0,3846 | 0,9231 |
| Autres | 9 | 0,4545 | 0,9091 |
| Hypothétiques | 3 | 0,6000 | 0,8000 |
| Subjectifs | 1 | repli sur global | repli sur global |

`p` désigne un **estimateur de calibration à faible effectif**, pas une confiance certifiée pour chaque question. Les familles subjectives n'ont pas assez de cas pour une estimation spécifique.

**Qualité des sorties dans l'ensemble des 64 évaluations, selon labels ClaimDB :** mode sans SQL **25/64**, mode avec SQL **55/64**. Ce contraste est descriptif : ce sont deux modes réels publiés avec des instructions différentes et un même modèle, et pas une expérience causale nouvelle d'Omega ni une vérité indépendamment recalculée de la base.

### Résultats primaires — utilité conventionnelle

Score : réponse publiée juste +1, fausse −2, abstention +0,05, consultation achetée −0,20. Coût **fictif**, non monétaire ; 16 consultations au maximum, 2 par lot.

| Politique | Utilité nette | Consultations | Réponses justes publiées | Erreurs publiées | Abstentions |
|---|---:|---:|---:|---:|---:|
| Aucune vérification | **3,20** | 0 | 0 | 0 | 64 |
| Deux premières du lot | **12,20** | 16 | 15 | 1 | 48 |
| Deux au hasard par hash | **12,20** | 16 | 15 | 1 | 48 |
| VOI globale classique | **12,20** | 16 | 15 | 1 | 48 |
| VOI contextuelle | **12,20** | 16 | 15 | 1 | 48 |
| VOI contextuelle avec contrôle des logs | **12,20** | 16 | 15 | 1 | 48 |
| **Omega expérimental, même VOI et certificat d'origine** | **12,20** | 16 | 15 | 1 | 48 |
| Oracle omniscient *a posteriori*, **non déployable** | **38,95** | 16 | 41 | 0 | 23 |

**Critère principal : Omega − VOI contextuelle avec traces = 0,000000.** Les deux ont **exactement les mêmes 64 actions et 16 choix de consultations**. Omega ajoute 16 entrées de certificat signalant le fournisseur unique et l'absence de recalcul indépendant ; cela n'a pas modifié une seule décision. **Aucun gain spécifique**.

### Diagnostic important : diversité des actions mais égalité des scores

Le test de diversité des sélections trouve **deux séquences de consultation distinctes parmi les politiques VOI fortes** (`PASS_DIFFERENT_ROUTES`). Pourtant, **les six politiques qui achètent effectivement deux consultations dans chaque lot obtiennent exactement +12,20, 15 bonnes réponses et une erreur**. Les 16 cas achetés par les heuristiques contextuelles comportent 15 réponses SQL correctes et une incorrecte ; la sélection par hash a obtenu le même bilan. **Ce résultat ne démontre aucune bonne priorisation.**

Il faut distinguer trois niveaux :
1. **Choix différents** : oui, au moins deux sélections distinctes ;
2. **Résultats différents** : non, toutes les politiques déployables qui utilisent pleinement le budget obtiennent les mêmes agrégats ;
3. **Valeur propre à Omega** : non, car son action égale rigoureusement celle du comparateur de provenance.

L'oracle omniscient atteignant +38,95 montre qu'il existe de fortes différences *a posteriori* entre décisions optimales et décisions des contrôleurs. **Ce n'est pas une limite supérieure atteignable** : l'oracle utilise le vrai label de chaque item avant toute décision et peut donc savoir quand répondre sans achat, information inaccessible aux systèmes testés. Il interdit d'affirmer que l'apprentissage actif est optimisé par le pilote, mais ne prouve pas qu'un apprenant réel peut approcher cette valeur.

Sur les 16 cas achetés par la candidate, chaque log avait au moins une sortie d'outil journalisée ; le filtre de traçabilité n'a donc rejeté aucun achat. Une sortie journalisée ne vérifie ni la validité du SQL exécuté ni son rapport causal à l'énoncé. L'expérience ne démontre **pas** qu'Omega sait apprendre la fiabilité des outils : l'étiquette de vérité reste cachée après consultation.

## 3. Trois nouveaux prédicats réellement calculés sur la base BIRD

Les trois sentinelles étaient **exclues des 64 cas de routage**. Leurs SQL ont été rédigés et archivés dans le code avant téléchargement de la base, avec deux formulations (JOIN et sous-requête) par prédicat. Chaque conclusion a été comparée aux labels publics seulement **après** calcul.

| ClaimDB | Prédicat SQL préétabli | Mesures réellement obtenues | Accord des deux méthodes | Verdict |
|---|---|---|---|---|
| **#15601** | Exactement 40 héros au score maximum **Speed** | Score maximum **100**, **40** héros ex æquo ; Air-Walker (id 13), Angela (id 28), Ardina (id 43) parmi les témoins | VRAI / VRAI | `ENTAILED` |
| **#3730** | Exactement 42 héros ayant **Super Strength** et hauteur supérieure à **200 cm** | **56** héros, contre-exemples au dénombrement 42 ; A-Bomb, Abomination, Alien parmi les éléments comptés | FAUX / FAUX | `CONTRADICTED` |
| **#3971** | Les pouvoirs **Invisibility** sont-ils plus fréquents que **Super Strength** ? | **22** contre **358** ; Super Strength apparaît d'ailleurs premier parmi les pouvoirs, devant Stamina (288) et Durability (257) | FAUX / FAUX | `CONTRADICTED` |

**3/3 concordances entre les résultats SQL calculés et les annotations publiques** sur ces trois claims, échantillon **choisi manuellement après connaissance des labels**. Ce n'est donc ni un taux d'exactitude statistiquement inférable, ni une évaluation aveugle. Les SQL correspondent à des clauses explicites mais leur adéquation sémantique n'a **pas été revue par un tiers indépendant**. Pour #3971, la comparaison de deux pouvoirs est un **test nécessaire mais pas suffisant** de l'affirmation « le plus répandu » ; ici son résultat **FAUX suffit à réfuter** l'affirmation entière, sans inférence abusive.

Toutes les requêtes ont été réellement exécutées sur **la même source BIRD épinglée**, et ne constituent **pas** plusieurs fournisseurs de vérité. Elles apportent de véritables dénombrements et des exemples de témoins, absents des seuls labels ClaimDB.

## 4. Résultat pour l'observabilité et la mémoire scientifique

Dans ce protocole, le certificat Omega indique la provenance d'un résultat de mode avec SQL et distingue `tool_output_logged` de `fact_reproduced_with_pinned_SQL`. Il ne peut pas rejeter des trajets de preuves fictifs qu'il n'a pas réellement reconstruits : **le mode de routage n'exécute aucun SQL de preuve**, il sélectionne un résultat de modèle prépublié. C'est donc une **application du principe de provenance**, pas une nouvelle conséquence mathématique prouvée du formalisme `Δ_h`.

Le test SQL séparé démontre qu'on peut obtenir sur une vraie base des **témoins vérifiables**, des **contre-exemples** et des **décomptes** accompagnés de provenance. Pour faire jouer un véritable rôle décisionnel au programme d'observabilité, il faudra relier, pendant l'action, les alternatives de vérification aux **hypothèses encore compatibles** et au gain de décision, puis tester les mêmes entrées contre un contrôle bayésien exact ou un algorithme d'active sensing classique.

## 5. Étape suivante rationnelle, sans modification rétroactive des scores

**Ne pas refaire le même budget sur les mêmes 64 claims.** Notre design actuel ne discrimine pas les scores des sélecteurs parce que la méthode avec SQL est suffisamment bonne sur les candidats choisis, même au hasard, et la méthode sans SQL est majoritairement jugée indigne d'être publiée par les faibles estimations de fiabilité. La prochaine campagne doit établir **avant inférence** que les vérificateurs sont réellement concurrents, faillibles, de coûts et d'efficacité observables différents, et que le choix d'une preuve peut modifier les décisions futures. Éviter de construire un problème sur des labels déjà observés qui favoriserait Omega.

Contrôles à exiger avant une nouvelle campagne :
- protocole et sorties fixes, validation indépendante de la **sémantique des SQL** par un évaluateur distinct ;
- budget égal aux vrais coûts de modèles (tokens, temps, erreurs de connexion), pas seulement utilité arbitraire ;
- validation de non-fuite des labels et de la valeur informationnelle attendue d'une vérification avant toute politique ;
- comparateur d'active sensing/VOI/POMDP suffisamment fort, et **ablation** de la mémoire/observabilité ;
- incertitude/statistiques sur plusieurs cohortes nouvelles, en distinguant généralisation et exploration post-hoc.

**Statuts : SQL réel exécuté ; calculs reproductibles ; décisions de routage rejouées sur erreurs de modèle authentiques ; GAIN SPÉCIFIQUE OMEGA NON DÉMONTRÉ ; SÉMANTIQUE DES SQL NON REVUE INDÉPENDAMMENT.**

**PR DRAFT #63, aucune fusion dans `main` ni promotion d'une supériorité Omega dans CORE.**
