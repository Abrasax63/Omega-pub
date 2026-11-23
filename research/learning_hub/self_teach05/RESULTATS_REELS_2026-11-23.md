# SELF-TEACH-05 — essai réel : retour d'erreur groupé vs isolé

**Date :** 23 novembre 2026. **Verdict : `NO_VERIFIED_ISOLATED_FEEDBACK_GAIN`.**

## Preuves

- [Préenregistrement du protocole et des cohortes : `fe276670`](https://github.com/Abrasax63/Omega-pub/commit/fe276670df5c6e8dd5ba5b15cfd89a690aae6f8e), **avant implémentation et inférence**.
- [Première PR #247](https://github.com/Abrasax63/Omega-pub/pull/247) : [run #45258627425](https://github.com/Abrasax63/Omega-pub/actions/runs/45258627425) échoué uniquement au préflight (import circulaire), **zéro appel modèle et holdout non ouvert**.
- [Correctif minimal en PR #248](https://github.com/Abrasax63/Omega-pub/pull/248), commit `34db49dd9c560dd870bfde23a9297b88a6ced9db` pour l'import qualifié.
- **[Run définitif #45258863634](https://github.com/Abrasax63/Omega-pub/actions/runs/45258863634)** : `success` pour les deux jobs, **6/6 tests logiciels**, 16 vraies inférences CPU Qwen2.5-3B-Instruct Q4_K_M, sans API payante ni modification de paramètres.
- [Artefact brut #14860002966](https://github.com/Abrasax63/Omega-pub/actions/runs/45258863634/artifacts/14860002966) : réponses du modèle, prompts, scores, métriques, logs et empreintes.
- SHA-256 des fichiers archivés, recalculé sur le ZIP GitHub : `raw.json = b6ee770623e2268cef0dce48088a190ccfa006eefcf9fa4c7c0cb8af94737c48` ; `score.json = 77d1d058f5f9e2d24f1a22c997be13fb324b938fe59b881d04d082161a5b8779`.

## Scores sur le holdout nouveau, désormais consommé

| Famille | Réponse initiale | Ancien feedback groupé | Feedback isolé |
|---|---:|---:|---:|
| F1 — répétitions du même chiffre | 1/6 | 1/6 | 1/6 |
| F2 — suites croissantes de lettres | 6/6 | 6/6 | 6/6 |
| F3 — groupes de ponctuation | 0/6 | 0/6 | 0/6 |
| F4 — alternance binaire | 2/6 | 2/6 | 2/6 |
| **Total** | **9/24** | **9/24** | **9/24** |

Fonctions entièrement justes : **1/4** dans les trois bras. Codes sûrs : **3/4** dans les trois bras. Aucune régression de tâche entièrement réussie, mais **aucune amélioration non plus**. Sur F2, le modèle avait déjà 8/8 cas de développement et 6/6 cachés dès la première génération.

## Pourquoi le test n'a pas distingué les méthodes

- Deux corrections sur F1, deux sur F3 et deux sur F4 pour chaque méthode, soit **12 appels de révision**, tous **refusés** car ils n'amélioraient pas le score de développement. F2 n'a nécessité aucune réparation.
- **Les trois diagnostics renvoyés au modèle étaient exactement identiques entre BATCH et ISOLATED, pour chacune des 12 révisions.** Il n'y a eu aucun incident de type timeout ou erreur globale dans ces tentatives de modèle susceptible de distinguer les deux méthodes.
- F3 n'avait pas de code Python admis (`INVALID_JSON_OR_CODE`). Sans code exécutable, les deux modes renvoient les mêmes statuts `NO_CODE`.
- **Ce test démontre le fonctionnement du garde-fou, mais n'a pas effectivement soumis les deux stratégies à une panne de lot sur une génération réelle.** Il ne réfute pas l'utilité de l'isolement en présence de panne; il constate que la nouvelle méthode n'améliore pas les sorties sur cette cohorte.
- Le témoin négatif logiciel séparé **confirme** que la fonction volontairement bloquée masque en mode groupé un exemple correct, et que le mode isolé récupère le résultat. C'est une capacité de diagnostic **logicielle** démontrée, pas une compétence apprise par le LLM.

## Coûts observés

- **16 appels au modèle**, **6 967 jetons d'entrée** et **2 304 de sortie**, durée de génération totale **142,254 s** (incluant les évaluations).
- Évaluations de développement : **60 travailleurs / 0,9987 s** dans BATCH contre **88 travailleurs / 1,44 s** dans ISOLATED. Ce surcoût est mesuré sur les entrées de ce lot; il ne doit pas être généralisé.
- **Aucun entraînement LoRA** et zéro mise à jour des poids.

## Décision et prochaine vérification falsifiable

**Ne pas adopter l'isolement systématique comme gain d'apprentissage.** Conserver le mode groupé comme référence sur les exemples où il donne une réponse valide; étudier un **repli isolé uniquement lors d'une erreur globale ou d'un délai dépassé**, plutôt que de payer l'isolement pour tous les cas.

Prochaine expérience distincte, **non exécutée ici** : préenregistrer avant modèle un diagnostic de panne de lot avec une cohorte neuve, mesurer le taux d'incidents réels, comparer retour groupé, retour isolé conditionnel et feedback explicitant la zone de non-progression, à budget équivalent. Ne pas rouvrir ces 24 cas comme un holdout nouveau; ne pas fournir au modèle un code corrigé ni un oracle caché.

Statuts : préenregistrement **FAIT**, code **IMPLÉMENTÉ**, tests logiciels **6/6 VÉRIFIÉS**, modèle réel **EXÉCUTÉ**, gain d'apprentissage **NON DÉMONTRÉ**. PR DRAFT, `main` inchangée.
