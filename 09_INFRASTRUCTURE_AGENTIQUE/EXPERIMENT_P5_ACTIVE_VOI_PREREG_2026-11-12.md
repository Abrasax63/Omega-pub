# P5-ACTIVE-01 — choix actif d'une seule preuve par lot (pré-enregistré)

**12 novembre 2026. Document enregistré AVANT code, tout modèle P5-ACTIVE-01 et toute analyse de sorties.**

## Bibliographie primaire vérifiée et décision méthodologique

- Gong & Zhang, *The Cost of Information: Phase Transitions in Contextual Bandits with Paid Observations*, ICML/PMLR 2026 : https://proceedings.mlr.press/v306/gong26i.html
- Tucker et al., *Bandits with costly reward observations*, UAI/PMLR 2023 : https://proceedings.mlr.press/v216/tucker23a.html
- Snell et al., *Scaling LLM Test-Time Compute Optimally*, ICLR 2025 : https://proceedings.iclr.cc/paper_files/paper/2025/hash/1b623663fd9b874366f3ce019fdfdd44-Abstract-Conference.html
- Iyengar, *Sample, Mix, or Verify?*, arXiv:2610.23255 (prépublication oct. 2026, non vérifiée comme publiée) : https://arxiv.org/abs/2610.23255

**Différence structurante avec REAL-03** : au lieu d'une unique décision par instant avec crédit de vérification imposant un calendrier, donner **quatre réponses concurrentes par lot**, chacune dans un domaine différent, et autoriser **au plus une vérification choisie dans ce lot**. Tous les autres candidats doivent être publiés tels quels (DIRECT) ou faire l'objet d'une abstention. Un seul contrôle exact peut corriger une réponse par lot. **Ne pas revendiquer une nouveauté algorithmique** face aux approches de valeur de l'information, de bandit contextuel et d'abstention.

## Mesure de réponse : évitement du parseur fragile

Pour chaque question à réponse booléenne, l'énoncé déclare explicitement « A = vrai, B = faux ». Au lieu d'une génération libre suivie d'une règle regex, mesurer **les vraies probabilités de prochain token des deux alternatives A/B** à la position de la réponse du modèle, en mode inférence déterministe, sans échantillonnage. La réponse est l'argmax des scores conditionnels réels des deux étiquettes ; le *margin* est leur différence de logit absolue et la pseudo-confiance est `softmax(logits)[argmax]`, **non considérée comme probabilité calibrée de vérité**. Contrôler avant exécution que chaque étiquette est exactement un token pour chaque modèle, sinon échouer plutôt que tricher. Les textes et logits seront conservés dans l'archive. Ceci teste **la classification forcée**, pas la qualité des réponses libres ni le parseur V2.

Modèles publics : Qwen2.5-0.5B-Instruct révision `7ae557604adf67be50417f59c2c2f167def9a775` et Qwen2.5-1.5B-Instruct révision `989aa7980e4cf806f80c7fef2b1adb7bc71aa306`. Un seul appel forward par question ; **96 inférences réelles** total (32 calibration, 64 test). Aucun OpenAI API ni calcul smartphone.

## Questions : 4 familles binaires vérifiables par deux méthodes indépendantes

- `MUL` : l'égalité `a*b=c` est-elle vraie ? (addition répétée versus multiplication)
- `CRT` : le nombre proposé `x` satisfait-il simultanément deux congruences ? (modulo direct versus modulo à partir d'une solution par CRT)
- `RATE` : le taux global de A est-il **strictement supérieur** au taux global de B ? (Fraction versus produit croisé)
- `INJ` : une fonction finie explicitée par ses images est-elle injective ? (cardinalité image versus recherche paire à paire)

Pour chaque famille, les cas pairs sont conçus vrais et impairs faux **avant modèle** (contrôle d'équilibre de l'étiquette, pas un indice donné au sélecteur). Toutes les questions sont nouvelles et différentes des REAL-01/02/03, déterminées par `SHA256(P5ACTIVE01|famille|index|champ)`.

16 cas/famille ? **20 questions/famille** : calibration indices 0–3 (4/famille × 2 modèles = 32 passages), test indices 4–11 pour 1.5B, 12–19 pour 0.5B (8/famille/modèle = 64 passages). Aucun énoncé test identique à un énoncé calibration. Oracles indépendants doivent donner les mêmes 80 réponses avant chaque inférence.

## Organisation des lots et informations accessibles

**16 lots × 4 candidats** (exactement un par famille, ordonnés selon une permutation SHA par lot), huit lots Qwen1.5B puis huit lots Qwen0.5B, avec alternance par blocs de quatre `1.5B → 0.5B → 1.5B → 0.5B` au niveau du flux. Le modèle, le numéro de phase et l'indice des questions sont cachés aux sélecteurs. L'ordre des 4 candidats est visible ; les algorithmes ont les mêmes candidats, scores de tokens, coût, étiquette du modèle et catégorie de tâche. Seule l'identité de modèle/phase est cachée, jamais la famille. Références mathématiques et exactitude non vérifiée sont réservées à l'évaluateur.

**Une seule vérification par lot** (ou zéro), sans report de crédit vers les autres lots. Tous les sélecteurs ont 16 occasions, et tout contrôle exact coûte selon la famille : MUL 0,25, CRT 0,40, RATE 0,30, INJ 0,20. Les coûts sont des unités d'utilité fictives. Un contrôleur reçoit l'issue booléenne **seulement de la vérification qu'il a choisie** ; les autres références sont réservées au correcteur hors ligne.

L'action `VERIFY` publie le résultat exact (+1 − coût) ; sans vérification, le contrôleur choisit entre `DIRECT` (correct +1, faux −2) et `ABSTAIN` (+0,05). Pour toute candidate, la décision DIRECT/ABSTAIN se fait par le même seuil d'utilité estimée : `3p-2 > 0.05` pour DIRECT ; sinon abstention. `p` est une estimation construite seulement à partir des calibrations et des propres vérifications. Les actions peuvent différer entre politiques ; l'évaluateur ne communique jamais le résultat de DIRECT/ABSTAIN.

## Politiques pré-enregistrées (paramètres figés)

1. `none` : ne vérifier aucune réponse ; choisir DIRECT/ABSTAIN avec les mêmes probabilités de calibration par famille.
2. `fixed_first` : vérifier systématiquement le premier candidat du lot (témoin de position).
3. `round_robin` : vérifier la famille `MUL,CRT,RATE,INJ` en rotation par lot.
4. `voi_static` : sélectionner la candidate au plus grand **gain marginal estimé** de vérification `(1-cost) - max(3p-2,0.05)`, avec p de calibration par famille (prior de Laplace 1/1). Ne pas vérifier si gain ≤0.
5. `voi_online` : même règle, actualisation du posterior beta par famille à partir des **seuls contrôles payés**.
6. `voi_discount` : pareil, mais retours vérifiés exponentiellement décotés `gamma=0.75` du plus récent au plus ancien, ajoutés aux 4+4 calibrations.
7. `voi_margin` : distinguer les sorties à **faible et forte pseudo-confiance**, avec seuil `0.75` fixé avant les modèles ; estimer `p` à partir des données de calibration par famille + bin avec lissage 1/1, puis mises à jour des vérifications de cette famille/bin. Si aucune calibration dans le bin, utiliser `p` par famille. **N'utiliser jamais les logits pour trier sans offrir la même information aux témoins.**
8. `omega_candidate` : même règle `voi_online` en régime normal, avec journal scientifique append-only. À partir de **4 retours vérifiés** au total, comparer leur taux sur les quatre dernières observations au taux global sur calibration ; si écart ≥ **0.35**, activer une révision : pour chaque famille, utiliser un mélange `0.5*posterior_online_kind + 0.5*posterior_last4_global`. Sortir de révision si écart ≤ **0.15**. La décision du lot utilise ces `p` révisés, ses propres retours, **sans accès aux résultats non vérifiés**. Appel à `planner.plan_mission` pour la provenance seulement ; il ne fait pas l'apprentissage.
9. `omega_no_change` : ablation identique à `voi_online` (appel P1 mais pas de révision). Égalité des décisions des deux politiques exigée par test.
10. `hindsight_oracle` : choix optimal par lot en connaissant les vérités **uniquement pour établir un plafond post-hoc non déployable**, exclu des contrôles opérationnels.

Règles de déterminisme : tri des choix éligibles par gain marginal décroissant ; à égalité famille par ordre `MUL,CRT,RATE,INJ`. Calibration par famille = 8 labels (4 cas × 2 modèles). Les politiques ne connaissent pas les réponses de test, et ne doivent pas exécuter le vérificateur avant d'avoir choisi.

## Mesures, tests adversariaux et falsification

**Primaire :** utilité totale `omega_candidate − voi_discount` sur les 64 réponses de test avec 16 budgets par lots. Secondaires : différences à `voi_margin`, `voi_online`, `voi_static`, `round_robin` ; nombre de réponses exactes/fausses publiées, abstentions, vérifications et coût ; nombre de choix de vérification distincts entre politiques **et** nombre d'alarmes qui modifient effectivement des actions versus ablation. Agréger le gain par lot et par phase (phase visible seulement au correcteur). Mesurer la différence entre le score brut de confiance du modèle et la correction observée, sans jamais lui donner la confiance comme garantie.

**Garde-fou de discriminabilité** : si toutes les politiques vérifient la même famille dans au moins 14/16 lots, qualifier le benchmark de trop trivial. Si `omega_candidate` ne change aucune décision, aucune amélioration n'est attribuable à son mécanisme. Si `omega_candidate ≤ voi_discount` ou `omega_candidate ≤ voi_margin`, pas de gain adaptatif spécifique démontré. L'absence de gain doit être rapportée même si vérification globale améliore le taux d'erreur.

Évaluer enfin un test contrefactuel **sur les seules sorties d'archive** montrant qu'un gain attendu et son classement varient suivant les probabilités (aucun ajustement après lecture pour améliorer les chiffres primaires). Le code d'allocateur doit être audité pour absence de fuite des vérités cachées, cohérence des deux oracles, budget, intégrité des observations.

## Portée scientifique

Les observations sont réelles (logits de modèles publics), mais les questions sont conçues par l'auteur et les vérificateurs sont déterministes, exacts, sur des tâches élémentaires. Ce n'est pas une preuve d'intelligence générale, d'autonomie de P1 ou de mémoire scientifique Omega sur la littérature. Les comparateurs sont des variantes implémentées localement, **pas des reproductions certifiées des algorithmes théoriques cités**. Écrire `PUBLIC_OPEN_MODEL_ACTIVE_INFORMATION_EXPLORATORY` pour toute campagne complète. Aucun coût d'API ou fichier privé, aucune fusion `main`, PR antérieures inchangées.
