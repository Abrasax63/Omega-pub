# P5-FALSIFY-02 — cinq variantes, 200 vraies inférences Qwen : résultat négatif, échec de l'intégration des preuves

**12 novembre 2026 — Statut : EXPÉRIENCE TECHNIQUE RÉELLE REPRODUCTIBLE / CAUSE DE L'ÉCHEC IDENTIFIÉE / SUPÉRIORITÉ ADAPTATIVE D'OMEGA NON DÉMONTRÉE.**

## Source, pré-enregistrement, contrôle technique

- [Pré-enregistrement AVANT code et résultats](EXPERIMENT_P5_FALSIFY02_REAL_FIVE_ARM_SMOKE_PREREG_2026-11-12.md), commit `3227f6aee67d0cfea7f93e0613df40cde26be28a`. Ce protocole prévoit **un pilote uniquement synthétique**, pas le véritable benchmark multidomaine encore bloqué par [PR #64](https://github.com/Abrasax63/Omega-pub/pull/64).
- [GitHub Actions #43247186137 — SUCCESS](https://github.com/Abrasax63/Omega-pub/actions/runs/43247186137), **8 tests spécialisés réussis** puis **200 véritables forwards CPU** de `Qwen/Qwen2.5-0.5B-Instruct`, commit de poids/tokenizer épinglé `7ae557604adf67be50417f59c2c2f167def9a775`, avec `transformers==4.51.3` et `torch==2.6.0`. Aucun appel à une API payante, aucun service externe de génération.
- [Archive brute du préflight, des 200 réponses et de tous les logits/coûts par bras](https://github.com/Abrasax63/Omega-pub/actions/runs/43247186137/artifacts/13957349109). SHA256 du ZIP : `5a3c1f08092c20976fe0b7aba29d25c670a0e18f3740828d0821a9616f02daab`. SHA256 du JSON brut du benchmark : `ba6a4253e4896035d4be1597c3aee7fd95e7749132bb639058d0ecbb7709f262`.
- **Seconde voie de calcul local sur le JSON brut** : tous les IDs/splits, 200 appels, la réponse finale, les bonnes/mauvaises réponses, les différences appariées C/E et D/E et les budgets ont été recomptés par un programme séparé du générateur. **Aucune divergence arithmétique**. Cette vérification est effectuée par le même assistant, **pas par un auditeur scientifique externe**.
- [Code d'exécution expérimental](prism/p5_falsify02_real_five_arm.py), [tests anti-fuite et anti-alias](prism/test_p5_falsify02_real_five_arm.py). Le code appelle réellement P1 et RCE/P2 dans les conditions prévues. **P3 n'exécute pas le modèle** : un runner expérimental distinct effectue les 200 appels.

## Construction des 40 problèmes

Quarante systèmes finis distincts `T:{0,1,2}→{0,1,2}`, `π:{0,1,2}→{0,1}`, mots observés de longueur trois. La question est « ce mot a-t-il une trajectoire microscopique globale ? ». Deux calculateurs exacts concordent pour tous les problèmes (énumération des états initiaux, filtre d'états survivants).

- **8 cas de calibration** (4 possibles/4 impossibles), dont le contre-exemple de recollement `T=(0,2,2), π=(0,0,1), mot=001` déjà connu, uniquement en calibration.
- **32 cas d'évaluation** (16 possibles/16 impossibles), sélection déterministe en fonction des paramètres et d'une fonction SHA-256, sans doublons.
- Les données sont générées par le programme lui-même et équilibrées selon la vérité pour ce **pilote technique**. Ce ne sont **pas** 32 problèmes nouveaux indépendants créés par un tiers, ni un holdout aveugle.
- Les cinq bras utilisent le même modèle et exactement **une inférence contrainte A/B par problème**, soit **40 appels par bras**, à un maximum de 512 tokens en entrée. Les prompts et appels de mémoire/filtre varient réellement.

## Résultat d'exactitude, vérifié sur toutes les traces

| Bras réellement exécuté | Bonnes réponses sur 32 évaluations | Bonnes réponses sur 8 calibrations | Appels mémoire RCE sur les 40 cas | Calculs exacts |
|---|---:|---:|---:|---:|
| A `direct` | **16/32** | 4/8 | 0 | 0 |
| B `classical_exact` | **32/32** | 8/8 | 0 | 40 |
| C `omega_no_memory` | **16/32** | 4/8 | 0 | 40 |
| D `omega_no_observability` | **16/32** | 4/8 | 120 recherches (3 rôles par cas) | 0 |
| E `omega_full_candidate` | **16/32** | 4/8 | 120 recherches | 40 |

**Aucun gain propre à Omega.** Sur les **32 évaluations**, les réponses C et E sont identiques **32/32**, et D et E sont identiques **32/32**, malgré des prompts différents **sur les 32 cas**. Même A et E ont pris exactement les mêmes 32 décisions finales.

**Cause du défaut de décision :** le modèle a renvoyé **A (« possible ») sur les 40/40 problèmes, dans chacun des cinq bras**, y compris lorsque le vrai filtre de survivants du bras C ou E indiquait explicitement `is_possible=false`. A est juste sur la moitié du corpus artificiellement équilibré. La différence de logits `logit(A)-logit(B)` est restée **positive** pour chaque sortie :
- A/B : moyenne **+4,639**, minimum **+4,269** ;
- C : moyenne **+3,290**, minimum **+3,035** ;
- D : moyenne **+3,295**, minimum **+3,157** ;
- E : moyenne **+2,977**, minimum **+2,825**.

Le contexte et les certificats ont modifié la confiance relative exprimée par le modèle, **mais jamais son choix A/B**. L'énoncé « l'observabilité n'aide jamais » n'est PAS établi : **l'information était correcte et fournie, mais le modèle ne l'a pas suivie**. C'est un échec d'interface **preuve → décision**, et un signal que le modèle petit / la méthode de décodage A/B ne sont pas discriminants pour cette tâche.

### Coûts réels et inégalité de consommation

Les cinq bras ont effectué le même nombre de forwards du **même modèle avec la même version**, et ont respecté le plafond de 512 tokens d'entrée, mais leurs **coûts réellement consommés ne sont pas égaux** :

| Bras | Tokens entrants cumulés | Temps d'inférence modèle (s) | Temps recherche mémoire RCE (s) |
|---|---:|---:|---:|
| A | **7 120** | **49,965** | 0 |
| B | **7 120** | **49,491** | 0 |
| C | **10 240** | **67,383** | 0 |
| D | **14 440** | **94,332** | **304,792** |
| E | **16 640** | **107,710** | **304,788** |

Les temps sont **mesurés sur le runner CPU GitHub lors de cette exécution**, pas une estimation de coût financier ni une comparaison de performances normalisées à ressources strictement égales. Le temps de recherche correspond à des appels RCE/P2 répétés sur la même base documentaire, sans cache inter-bras dans ce pilote. L'inférence modèle et le RCE sont mesurés séparément ; ne pas les additionner comme si toute latence système était nécessairement représentée. **Omega E utilise plus de tokens, plus de temps et ne corrige aucune décision.** Cette absence de rendement constitue un résultat négatif robuste sur le pilote technique, et **ne démontre pas** qu'une mémoire bien intégrée soit inutile en général.

## Le vrai problème mis à jour

Les observations de `survivor_certificate` sont **exactes** et portent directement sur la vérité demandée. Les bras C et E les ont effectivement incluses dans le prompt, sans changement de réponse. La chaîne actuelle confie donc au modèle la tâche de respecter un calcul mathématique qui aurait pu, dans ce cas, être reconnu comme **autoritatif** après validation de son périmètre.

**Correction d'architecture à tester UNIQUEMENT sur une nouvelle cohorte :**
1. formaliser un reçu de preuve `question_id, source_hash, instrument, observations, scope, verdict, validité` ;
2. faire vérifier deux fois une affirmation mathématique déterministe (ou un résultat SQL avec source épinglée + contrôle de sémantique), avant toute adoption ;
3. lorsque le certificat est exact et dans son périmètre, **gouverner la décision finale par le résultat calculé** ; si contradiction/source non vérifiée, abstention explicite ;
4. ne pas confondre cette gouvernance avec de l'« intelligence supérieure » : **le témoin B fait déjà un calcul exact et atteint 32/32** ;
5. ne pas « recalculer » les scores primaires avec cette règle inventée après observation ; seulement réaliser une **analyse de sensibilité post-hoc** et geler la règle pour un **nouvel ensemble**.

Le résultat de cette campagne ne valide **ni** le système automatique P1/P2/P3 **ni** la thèse de supériorité adaptative. Il montre que des modules peuvent être activés et produisent de vraies preuves sans influencer la sortie d'un petit modèle.

## Statut et suite

**ÉTABLI :** 200 vraies inférences Qwen épinglées, 40 cas doublement vérifiés, 5 bras instrumentés, véritable recherche RCE/P2, filtrage d'observabilité exact, un bras classique parfait, résultat négatif et consommation de ressources mesurée.

**RÉFUTÉ DANS CE PILOTE :** gain décisionnel des modules actuels de mémoire/observabilité par simple injection dans le prompt ; zéro différence C/E et D/E malgré les traitements effectifs.

**INDÉTERMINÉ :** gain sur des problèmes variés et nouveaux, module de gouvernance des preuves à appliquer après revalidation, statut des véritables P1/P2/P3 pleinement exécutés, impact du choix d'un autre modèle ou décodage, pertinence de la mémoire sur une décision plus complexe.

**Gouvernance : conserver la PR en DRAFT ; `main` inchangée ; aucune promotion de supériorité dans CORE.**
