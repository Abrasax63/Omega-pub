# P5-REAL-02 — deux modèles réels, variation cachée de fiabilité : audit

**12 novembre 2026. Statut : 96 GÉNÉRATIONS RÉELLES / TEST EXPLORATOIRE CORRIGÉ / AVANTAGE ADAPTATIF OMEGA NON DÉMONTRÉ.**

## Provenance et journal de correction

- Pré-enregistrement avant code et inférences : [EXPERIMENT_P5_REAL02_PREREG_2026-11-12.md](EXPERIMENT_P5_REAL02_PREREG_2026-11-12.md), commit `7d2905624217a9b0e0d81ebc2ef82f0f9fc86921`.
- **Déviation méthodologique explicitement documentée** : [AMENDEMENT_P5_REAL02_QUESTION_UNIQUENESS_2026-11-12.md](AMENDEMENT_P5_REAL02_QUESTION_UNIQUENESS_2026-11-12.md). Le premier générateur contenait trois paires d'énoncés INJ identiques ; premier [run 43201065909](https://github.com/Abrasax63/Omega-pub/actions/runs/43201065909) exclu de toute comparaison. Les images INJ sont désormais des permutations déterministes SHA et un test impose **80 énoncés distincts**. La correction a été enregistrée **sans consulter les sorties du premier run**, mais après le début de l'exécution initiale : la version corrigée reste exploratoire, et non un holdout intouché.
- **[Run corrigé officiel 43201468837 — SUCCESS](https://github.com/Abrasax63/Omega-pub/actions/runs/43201468837)** ; 8 tests Python passés, 96 inférences réelles complètes, 64 décisions d'évaluation, huit politiques, budget respecté, sortie publique archivée.
- [Archive JSON originale de la version corrigée](https://github.com/Abrasax63/Omega-pub/actions/runs/43201468837/artifacts/13935083633) (expiration GitHub selon la politique d'artefacts). SHA-256 du ZIP téléchargé : `66852a53df8229f084ac8f792839322df01012ca19027b0d3c9534d820c8fb9c`.
- Empreinte des entrées publiques corrigées : `1692a90764baa0eeec3765fa58d135f348ac085e48aa64e8b60a39c4850ce150`.
- Deux modèles réels : `Qwen/Qwen2.5-1.5B-Instruct` révision `989aa7980e4cf806f80c7fef2b1adb7bc71aa306`; `Qwen/Qwen2.5-0.5B-Instruct` révision `7ae557604adf67be50417f59c2c2f167def9a775`. Inférence CPU gratuite via GitHub Actions, **0 OpenAI API, aucune puissance locale**.
- Les 80 références mathématiques ont été comparées par les deux chemins du script ; un audit indépendant de l'archive a **recalculé les 96 références directement à partir du texte des questions**, sans divergence. Les huit scores, toutes les décisions et le débit des 24 crédits de vérification ont également été recomputés et validés.

## Organisation et épreuve

32 inférences de calibration (les mêmes 4 questions/famille passées à chacun des deux modèles), puis 64 réponses réelles de test sur des questions distinctes. Quatre familles : multiplication `MUL`, congruences `CRT`, comparaison de taux `RATE`, injectivité `INJ`. Quatre phases cachées aux politiques : `1,5B → 0,5B → 1,5B → 0,5B`, quatre questions/famille/phase ; chaque politique voit ses propres vérifications, jamais le modèle/phase ni la vérité des réponses non vérifiées.

Sur le **score de réponses extraites initialement figé**, 14/64 réponses de modèle sont exactes, 34 sont fausses avec extraction, et 16 n'ont pas été parsées. Par phase : 5/16, 2/16, 5/16, 2/16. Par famille : MUL **5/16**, CRT **0/16**, RATE **0/16** (défaut d'extraction ci-dessous), INJ **9/16**. Ces scores ne sont **pas** des estimations de la capacité générale des modèles.

## Politique × coût : résultats primaires figés

Convention de gain : correct +1, faux publié −2, abstention +0,05 ; vérifier coûte de 0,15 à 0,45 unités fictives selon le domaine. Même crédit progressif et maximum de 24 vérifications pour chaque politique.

| Politique | Gain total | Vérifications | Réponses correctes publiées | Fausses publiées | Abstentions |
|---|---:|---:|---:|---:|---:|
| Directe | −53,2 | 0 | 14 | 34 | 16 |
| Abstention systématique | 3,2 | 0 | 0 | 0 | 64 |
| Vérification périodique | −28,8 | 24 | 30 | 26 | 8 |
| **Règle statique par famille** | **18,8** | 24 | 24 | **0** | 40 |
| **Beta avec décote 0,70** | **18,8** | 24 | 24 | **0** | 40 |
| Beta en ligne | 14,7 | 24 | 24 | **2** | 38 |
| Omega candidat | 14,7 | 24 | 24 | **2** | 38 |
| Omega sans alarme | 14,7 | 24 | 24 | **2** | 38 |

**Contraste primaire pré-enregistré : Omega − Beta décoté = −4,1 unités.** Omega perd également face à la règle statique ; ces deux contrôles ont pris exactement les mêmes 64 décisions, pas seulement obtenu le même score. **Omega = Beta en ligne = Omega sans alarme, décision par décision (64/64 identiques).** Aucune alarme n'a été déclenchée et aucune décision n'a été modifiée par le mécanisme candidat.

Les **deux mauvaises publications supplémentaires** du candidat Omega sont des décisions `DIRECT` aux instants 51 et 59, famille `INJ`, sorties `NON` alors que les fonctions étaient injectives (réponse `OUI`). La règle statique et l'estimateur décoté ont choisi l'abstention. Les huit politiques ont respecté leurs budgets de vérification, et les niveaux de coûts calculés par le script sont reproduits par l'audit indépendant.

## Limitation majeure de notation : « Équipe A/B » non parsée

**Le parseur figé n'acceptait que A ou B en tête de ligne**, alors que **les 16 sorties RATE du test commencent par « Équipe A » ou « Equipe B »**. Elles ont toutes été classées `None`, bien que la lettre soit explicite.

Contrôle de sensibilité **POST-HOC, distinct du score primaire** : extraire la première lettre après `Équipe` (sans utiliser les résultats attendus pour la choisir) donnerait **10 réponses RATE correctes sur 16**, donc **24/64 réponses initiales correctes sur les 64 tests** au lieu de 14/64. Les deux modèles ont eu 3/8 correctes pour 1,5B et 7/8 pour 0,5B sur RATE dans cette analyse, sans preuve de supériorité intrinsèque du petit modèle : les petites cohortes et le biais de sortie A/B dominent.

**Attention : ce n'est pas une nouvelle estimation validée des huit politiques.** Changer le parseur modifierait les informations visibles aux sélecteurs et potentiellement **leurs décisions**, donc il faudrait pré-enregistrer une nouvelle évaluation pour produire de nouveaux scores de politiques. Pour les **actions fixes déjà choisies**, seul le score des politiques qui publient directement une sortie RATE changerait ; cela ne mesure pas ce qui se serait passé si ces politiques avaient été recalibrées.

Le défaut de notation est un résultat méthodologique du pilote et ne doit pas être caché, même si l'hypothèse de gain Omega est négative.

## Interprétation scientifique et décision

1. **EXÉCUTÉ et VÉRIFIÉ à portée restreinte :** 96 sorties réelles de deux modèles ouverts, 80 questions mathématiques distinctes, deux méthodes de calcul par famille, budget et information égaux, outil réel de vérification, réponses/trajectoires auditables.
2. **RÉFUTÉ dans ce protocole :** gain propre au détecteur Omega ; 0 alarme et 0 décision changée, score inférieur au témoin décoté. Le système n'a pas identifié la variation de source de modèle malgré quatre phases successives.
3. **BIAIS CONNU :** parseur excluant la totalité des réponses RATE ; le score original 14/64 sous-estime la précision des réponses publiables et peut infléchir les décisions. Enregistrer le 24/64 de sensibilité **seulement comme post-hoc**.
4. **INCONNU :** robustesse sur tâches indépendantes, domaines non mathématiques, vérificateurs non parfaits, gros modèles modernes, bibliothèques scientifiques historiques et intelligence adaptative générale. La candidate n'est pas l'architecture Omega complète ni un agent apprenant déjà intégré à P1.

**Décision : ne pas fusionner le contrôleur expérimental dans `main` ; maintenir PR en draft comme test négatif documenté.** La prochaine étape méthodologique n'est pas de régler les seuils sur ces 64 réponses, mais de pré-enregistrer un parseur sémantique/domainé indépendant et d'utiliser un nouveau jeu avec une source de difficulté variée et des retours suffisamment nombreux pour détecter une rupture, tout en conservant les témoins classiques.
