# P5-FALSIFY-03 — pré-enregistrement du raccordement preuve → décision

**12 novembre 2026 — Règles établies AVANT tout calcul et toute nouvelle génération des réponses du modèle pour cette campagne.**

## Problème hérité et hypothèse réfutable

[PR #65](https://github.com/Abrasax63/Omega-pub/pull/65) : 200 inférences réelles Qwen, toutes prédisant A, y compris lorsque les sorties d'un filtre exact indiquaient que A était impossible. La mémoire documentaire et le certificat placés dans le prompt n'ont changé **aucune** décision, malgré un coût supplémentaire. Le bras classique exact a obtenu 32/32 contre 16/32 pour chacun des quatre bras sans arbitrage final.

**Test présent :** un certificat exact vérifié, dans son périmètre, **gouverne** la décision finale au lieu d'être seulement placé dans le prompt. En cas d'anomalie, le système s'abstient ; il ne remplace pas une preuve contradictoire par une réponse confiante du modèle.

**Ne pas chercher une victoire impossible :** un algorithme classique exact, qui résout gratuitement ou à faible coût ce même problème fini, est déjà parfait. Omega ne peut pas le dépasser en taux de réponses justes ; seul un gain de coût ou de généralisation pourrait être discuté sur des tâches nouvelles **où la vérification n'est pas trivialement exacte**. P5-FALSIFY-03 est un test causal d'intégration, pas le benchmark général de supériorité.

## Nouvelle cohorte, indépendante de la précédente en paramètres mais non aveugle

- États `X={0,1,2,3}`, fonction totale `T:X→X`, projection binaire non constante `pi:X→{0,1}`, mot projeté de longueur **4**, donc aucun triplet de la campagne N=3/L=3 n'est réutilisé.
- Construire l'univers en énumérant **256 fonctions T × 14 projections non constantes × 16 mots = 57 344 cas**. Un oracle indépendant énumère les quatre états initiaux ; un autre calcule les ensembles de survivants par filtrage séquentiel. **Exiger leur accord sur tous les cas du monde généré avant sélection**.
- Pour chaque ligne, `id=SHA256(JSON(t,pi,word))`. Trier par `SHA256("FALSIFY03|case-id")` puis par `id`, indépendamment des réponses de modèle.
- Sélection technique **stratifiée en vérité** : les **2 premiers possibles et 2 premiers impossibles** servent à la calibration ; les **8 suivants de chaque** à l'évaluation. **4 calibrations et 16 tests** ; tous distincts. Ceci est une *campagne de diagnostic technique* où le code générateur connaît le gold, **pas un holdout scientifique aveugle**.
- Aucune sélection/retouche des cas selon la sortie de Qwen ou la réussite d'une politique. Aucune modification de barème après la première inférence.
- `A=OUI, B=NON, ABSTAIN`; une sortie brute A/B est imposée par la comparaison d'un **pas** de logits, exactement comme dans P5-FALSIFY-02.
- Modèle réel commun : `Qwen/Qwen2.5-0.5B-Instruct` révision `7ae557604adf67be50417f59c2c2f167def9a775`; `torch==2.6.0`, `transformers==4.51.3`. **20 cas × 5 bras = 100 vrais forwards CPU**, même cap 512 tokens d'entrée, une sortie binaire par appel, aucun API payante.
- Temps d'inférence, tokens, opérations de filtre, consultations RCE, temps de récupération et exactitude sont **mesurés et rapportés** ; le plafond commun ne garantit pas des coûts effectifs égaux.

## Deux oracles, portée et chaîne de confiance

Pour un certificat `E=(task_spec_sha256,source,algorithm,answer,prefix_survivors,survivor_states)` :
1. vérifier que le SHA de l'énoncé `T,pi,word` concorde avec la tâche en cours ;
2. imposer les **deux** calculs structurés indépendants : (i) énumération directe sur les 4 états ; (ii) filtrage des survivants ;
3. exiger la même réalisation/non-réalisation et une liste finale compatible, avec au moins un état témoin si positif ;
4. refuser toute pièce non épinglée, périmée ou contradictoire ; ne jamais lire le gold caché de l'évaluateur pour trancher ;
5. attribuer `independent_data_providers=1` (même T,pi), `independent_computation_methods=2` (algorithmes distincts). Une seconde méthode n'est **pas** une deuxième source de données.

Le protocole d'arbitrage `final_answer = certified_answer` s'applique uniquement si `certificate.status=VALID` et si le scope/version est identique ; sinon `ABSTAIN`. L'absence de certificat pour un bras qui n'en utilise pas ne déclenche pas une fausse abstention : ce bras répond selon le modèle.

## Cinq bras pré-enregistrés

- A `direct` : Qwen seul, sans P1, P2 ni vérification.
- B `classical_exact` : même Qwen brut que A, puis oracle par énumération classique ; réponse finale exacte (inclure un appel outil exact, son coût et son temps).
- C `omega_no_memory` : P1, certificat **deux méthodes**, gouvernance finale, sans lecture P2.
- D `omega_no_observability` : P1 et lecture RCE/P2 réelle, réponse brute du modèle, sans calcul du certificat; aucun contrôle par le gold après l'inférence.
- E `omega_full_governed` : P1, lecture RCE/P2 et certificat **deux méthodes**, gouvernance finale.
- Le contexte de mémoire de D et E peut être **mis en cache par question pour éviter deux appels RCE identiques**, mais les métadonnées doivent préciser `shared_memory_cache`, le nombre réel de consultations, et le mode réutilisation. Un cache ne doit pas être compté deux fois comme deux lectures réseau.
- Les décisions C et E devraient égaler B lorsque les certificats sont valides : il s'agit d'une **prévision structurelle**, pas d'un score observé ou d'un gain propre à Omega. Si C et E ont des résultats différents sans défaut de certificat, arrêter la campagne.
- Si D et E prennent des décisions différentes, l'observabilité gouvernée est **causalement active** sur ces cas ; si C et E restent identiques, l'effet décisionnel de la mémoire demeure **non identifié**.
- Le modèle ne peut pas modifier la décision finale contre un certificat validé, mais son choix brut et ses logits sont conservés. L'expérience ne doit pas modifier rétroactivement les sorties de la PR #65.

## Contrôles adversariaux prévus

- changement du hash de tâche, champ de source absent, `prefix_survivors` ou état final falsifié, désaccord de deux méthodes → `ABSTAIN_INVALID_CERTIFICATE` ;
- refus d'appeler P2 pour le bras sans mémoire, et refus du vérificateur pour le bras sans observabilité ;
- tests de double oracle sur **tous les 57 344 cas**, non seulement les 20 cas évalués ;
- vérification que deux bras ayant des décisions identiques ne sont pas décrits comme une ablation démontrée de l'effet mémoire ;
- aucun prompt contenant le gold de l'évaluateur.

## Statut et arrêt

- **Critère de succès technique** : 100 vraies inférences enregistrées, les deux algorithmes exacts concordants, certificats invalides refusés, C/E interviennent effectivement sur au moins un choix erroné du modèle, B et E comparés avec leurs coûts.
- **Critère scientifique** : `NO_OMEGA_SPECIFIC_GAIN` si E n'améliore pas B sur les mêmes cases et/ou si E coûte davantage ; `MEMORY_EFFECT_NON_IDENTIFIABLE` si C=E. Ne **pas** présenter le nouveau résultat comme preuve générale d'intelligence adaptative.
- Si la CI échoue au contrôle d'empreinte, au schéma de preuve, à la tokenisation ou au budget, arrêter et publier l'échec; toute correction nécessite nouveau commit tracé. Aucun changement de politique sur des scores déjà vus.
- **Suite stratégique après ce pilote :** évaluer la sélection stratégique d'outils sous coûts observés et preuves réellement incertaines (sans oracle exact universel), contre une planification bayésienne classique forte, et sur des données sémantiquement revues.

**PR DRAFT, base PR #65, `main` inchangée. Aucun nouveau résultat scientifique promu en CORE.**
