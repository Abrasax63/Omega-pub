# Audit additionnel des 200 sorties authentiques de P5-FALSIFY-02

**12 novembre 2026 — recalcul indépendant des marges à partir de l'archive originale, APRÈS la campagne #65. Pure exploration post-hoc : pas d'ajustement rétroactif des décisions ni nouvelle inférence.**

Source : [PR #65](https://github.com/Abrasax63/Omega-pub/pull/65), [run réel #43247186137](https://github.com/Abrasax63/Omega-pub/actions/runs/43247186137), [ZIP brut](https://github.com/Abrasax63/Omega-pub/actions/runs/43247186137/artifacts/13957349109). Archive téléchargée vérifiée SHA256 `5a3c1f08092c20976fe0b7aba29d25c670a0e18f3740828d0821a9616f02daab` ; fichier `falsify02_real_5arm_outputs.json` SHA256 `ba6a4253e4896035d4be1597c3aee7fd95e7749132bb639058d0ecbb7709f262`.

### Les lectures de mémoire ont réellement abouti

Sur les **40 cas** du pilote, les deux bras avec P2 possèdent chacun **40 contextes RCE non vides, avec 120 documents candidats récupérés et 40 manifests distincts**. Les bras directs et sans mémoire ont bien zéro document. L'inefficacité en décision ne vient donc **pas** d'un simple accès à la mémoire entièrement vide. Ces documents ne constituent toutefois **pas une validation scientifique des hypothèses** : la pertinence des extraits et leur capacité à résoudre la tâche n'ont pas été examinées indépendamment.

### Différence de score interne du modèle, sans différence d'action

Sur les **32 problèmes d'évaluation**, le post-traitement des logits originaux calcule pour chaque paire la différence des marges `(logit_A-logit_B)_bras1 - (logit_A-logit_B)_bras2`.

| Paire appariée, 32 mêmes problèmes | Différence moyenne de marge A−B | Intervalle observé des 32 différences | Choix A/B modifiés |
|---|---:|---:|---:|
| E complet − C sans mémoire | **−0,3155** | [−0,4736 ; −0,1728] | **0/32** |
| E complet − D sans observabilité | **−0,3198** | [−0,4629 ; −0,2441] | **0/32** |
| D sans observabilité − A direct | **−1,3418** | [−1,8001 ; −1,1113] | **0/32** |
| C sans mémoire − A direct | **−1,3461** | [−1,7521 ; −0,9940] | **0/32** |

Tous les bras ont choisi **A** sur ces 32 tâches. Les contextes et la preuve **déplacent la marge interne en direction de B** dans ces comparaisons, mais pas assez pour renverser le choix. **Ce n'est pas une mesure d'information causale isolée de la mémoire**, car les formulations de prompt et budgets consommés changent ; on ne peut que noter la variation appariée de la marge.

L'analyse justifie le nouveau test [FALSIFY-03, PR #66](https://github.com/Abrasax63/Omega-pub/pull/66) : conserver la sortie brute du modèle, mais faire **gouverner le verdict final par un certificat de témoin vérifié** plutôt que supposer qu'un décalage des logits suffira.

### Méthode du recalcul

Charger le JSON brut `raw`, apparier les enregistrements sur `task_id` et `arm`, restreindre à `split=="evaluation"`, et soustraire les quantités `model_logits.A-model_logits.B` pour chaque paire. Les marges individuelles sont publiques dans l'artefact. Aucun poids de modèle n'a été rechargé et aucun label nouveau n'a été créé.

**Statut : seconde voie descriptive / pas de validation externe / pas de gain démontré.** Aucune promotion en CORE ; ne pas transformer le changement des logits en avantage décisionnel.
