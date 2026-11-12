# P5-REAL-03 — audit du parseur et test réel d'adaptation, résultat négatif

**12 novembre 2026 — 96 générations réelles, tous tests passés. Critère de gain adaptatif NON SATISFAIT.**

## Sources et intégrité

- [Pré-enregistrement avant code et avant toute génération REAL-03](EXPERIMENT_P5_REAL03_PREREG_2026-11-12.md), commit `b72c3def13651708b3d7dd4eb7b1f04ed71513f2`. L'extracteur `p5_real03_semantic.py` a été committé **avant le run**, commit `b792951bda5fc426ccdbed75d38617a155f3916d`. **Aucune modification postérieure** de ses règles durant l'évaluation.
- [GitHub Actions #43209647890 — SUCCESS](https://github.com/Abrasax63/Omega-pub/actions/runs/43209647890) : **6 tests** de protocole réussis, **96 inférences réelles** sur le CPU distant, **64 problèmes de test**, neuf politiques exécutées et sortie complète archivée.
- [Archive JSON des 96 sorties et neuf trajectoires](https://github.com/Abrasax63/Omega-pub/actions/runs/43209647890/artifacts/13939344843), conservation GitHub temporaire. SHA-256 de l'archive ZIP téléchargée : `5a70d483150b29c56d2d0e06cd47b29ca626a898158332020dc33ed7e668d60b`.
- 80 questions différentes, quatre familles : `MUL, CRT, RATE, INJ` ; deux méthodes de calcul mathématiques pour chaque référence ; 32 calibrations, 64 évaluations sur questions non utilisées en calibration ; modèles Qwen 0,5B et 1,5B, révisions gelées `7ae557604adf67be50417f59c2c2f167def9a775` et `989aa7980e4cf806f80c7fef2b1adb7bc71aa306`.
- **0 API OpenAI, aucun calcul smartphone, aucune donnée privée**. Le contrôle a confirmé le respect des **24 vérifications maximales par politique** et une exposition des références au correcteur uniquement. `main`, le holdout privé et les PR #47–54 sont inchangés.

## Scores primaires figés avant inférence

Sur les 64 réponses du jeu de test, le parseur pré-enregistré a extrait **13 réponses exactes, 29 réponses extraites mais fausses, et 22 non extraites**. Ces métriques mélangent les erreurs de modèle et de parsing ; elles ne sont pas une évaluation sémantique indépendante.

| Domaine | Correctes extraites sur 16 | Non extraites sur 16 |
|---|---:|---:|
| MUL | 7 | 6 |
| CRT | 0 | 0 |
| RATE | 0 | **16** |
| INJ | 6 | 0 |
| **Total** | **13** | **22** |

Défaut diagnostiqué **après coup** : le parseur avait prévu « Équipe A/B » (forme rencontrée dans REAL-02), mais le nouvel énoncé demandait « Quel **groupe** ... ? », et les **24 réponses RATE** (calibration + évaluation) étaient de la forme « Groupe B ... ». Leur rejet systématique montre que l'outil de notation n'était **pas** suffisamment robuste aux variantes pourtant attendues de la langue.

Les modèles produisent des réponses hétérogènes sur MUL, notamment `64 * 3 = 192` et `Elle vaut 280.`, également refusées par ce correcteur. La correction du parseur après lecture des réponses serait une **déviation de protocole** ; les scores primaires et les politiques ne sont donc **pas** recalculés.

### Analyse de sensibilité post-hoc — hors protocole primaire

En extrayant seulement les formulations syntaxiques non ambiguës « Groupe A/B », « nombre × nombre = résultat » et « Elle vaut nombre », **sans demander le résultat de référence au parseur**, un script d'audit séparé a obtenu :

| Domaine | Correctes selon parseur figé | Correctes dans l'analyse post-hoc |
|---|---:|---:|
| MUL | 7/16 | 12/16 |
| CRT | 0/16 | 0/16 |
| RATE | 0/16 | 9/16 |
| INJ | 6/16 | 6/16 |
| **Total** | **13/64** | **27/64** |

Les **22 réponses initialement non extraites** deviennent alors syntaxiquement interprétables. Cela prouve que l'échec initial du parseur crée une **sous-estimation majeure** de réponses interprétables sur ces 64 cas. **Ce score est exploratoire**, établi après lecture des réponses ; il ne constitue ni une nouvelle mesure pré-enregistrée, ni un prétexte pour annoncer un meilleur score d'Omega. Recalculer les neuf politiques avec le parseur modifié nécessiterait de recalibrer toutes leurs observations et de relancer un **nouveau protocole sur de nouvelles questions**.

## Neuf politiques comparées sur les mêmes 64 réponses réelles

Même crédit progressif, budget maximal **24 vérifications**, conventions de gain figées : +1 correct, −2 faux, +0,05 abstention, coûts de vérification selon la famille de 0,15 à 0,45 (unités d'utilité fictives).

| Stratégie | Utilité | Vérifications | Correctes publiées | Fausses publiées | Abstentions |
|---|---:|---:|---:|---:|---:|
| Réponse directe | −43,9 | 0 | 13 | 29 | 22 |
| Abstention systématique | 3,2 | 0 | 0 | 0 | 64 |
| Vérification périodique + réponse directe | −4,5 | 24 | 34 | 16 | 14 |
| **Règle simple statique par domaine** | **18,8** | 24 | 24 | 0 | 40 |
| **Beta cumulatif** | **18,8** | 24 | 24 | 0 | 40 |
| **Beta décoté** | **18,8** | 24 | 24 | 0 | 40 |
| **Beta à fenêtre glissante** | **18,8** | 24 | 24 | 0 | 40 |
| **Omega candidat** | **18,8** | 24 | 24 | 0 | 40 |
| **Omega sans alarme** | **18,8** | 24 | 24 | 0 | 40 |

**Contraste primaire : Omega − Beta décoté = 0,00.** Les six dernières politiques (statique par domaine, cumulatif, décoté, fenêtre glissante, Omega et ablation) ont pris exactement **les mêmes 64 actions**. Le candidat déclenche **0 alarme** et provoque **0 décision différente** de `omega_no_alarm`. Le critère de gain spécifique n'est pas satisfait ; ne pas confondre le bénéfice d'un vérificateur exact et celui du mécanisme d'adaptation.

### Pourquoi le banc d'essai ne discrimine pas les stratégies

Une reconstruction indépendante des décisions montre que les politiques vérifient aux mêmes **24 instants** (ex. t=2,5,7,10,13,15, etc.), lorsque le crédit progressif devient disponible, et s'abstiennent aux **40 autres instants**. Elles ne publient aucune des réponses du modèle sans outil. La règle d'utilité `VERIFY=1−coût` face à un modèle mal calibré rend **dominante la vérification à l'instant crédité** et évite les autres décisions ; le mécanisme d'alarme ne reçoit pas l'occasion de transformer un choix pertinent.

Cette observation constitue un **défaut d'identifiabilité du test** : les politiques sont nombreuses mais le protocole réduit leur espace de décision à une règle calendaire. On ne peut pas utiliser leur égalité pour conclure qu'aucune forme d'adaptation ne pourrait jamais fonctionner. Cela réfute seulement la plus-value de la candidate **dans ce banc d'essai**.

## Piste méthodologique recommandée (sans prétendre aux résultats futurs)

**Ne pas relancer immédiatement 96 nouveaux appels au même protocole.** D'abord :

1. Résoudre le problème d'extraction **par conception** : réponses catégorielles A/B et OUI/NON déterminées par un choix contraint parmi les étiquettes (ou un format de sortie validé avant inférence), et réponses numériques vérifiées par une grammaire définie avant modèle. Auditer les contradictions, ne pas inventer une réponse à partir du gold.
2. Donner un **choix stratégique réel** : un lot simultané de plusieurs réponses candidates, plusieurs vérifications possibles, **une seule vérification autorisée par lot**, des coûts différents, et éventuellement la possibilité de demander une seconde preuve. Le contrôle doit choisir **quoi** vérifier, non seulement attendre son prochain crédit fixe.
3. Comparer une règle statique, un calcul classique de valeur de l'information, une politique à mémoire courante, et Omega **avec et sans révision** ; gel du protocole et des métriques avant une nouvelle génération.
4. Tester la capacité d'une politique à changer ses décisions **sur des trajectoires artificielles seulement pour des tests logiciels**, puis sur un jeu indépendant d'erreurs réelles. Aucun score d'adaptation revendiqué si ces changements n'apportent pas un gain par rapport au meilleur contrôle.

**Conclusion : VALIDÉ logiciel, mais PAS DE PLUS-VALUE PROPRE À OMEGA DÉMONTRÉE. Le problème de notation persiste et le problème de conception des décisions est identifié.** Conserver la PR en draft ; aucun transfert dans `main`.
