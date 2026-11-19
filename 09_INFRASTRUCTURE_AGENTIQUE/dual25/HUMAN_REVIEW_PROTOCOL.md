# DUAL25 — protocole de revue humaine réellement indépendante

**Statut : `PENDING_INDEPENDENT_HUMAN_ANNOTATION`.** Aucun humain extérieur au développement d'Omega n'a encore relu les cas de cette expérience. Aucun score de fidélité ne doit être publié.

## Ce qui sera fourni au réviseur
- `HUMAN_REVIEW_PACKET.json`, généré par la CI, avec 24 documents de contrat contrôlés et 18 courts extraits externes historiques.
- Le paquet ne contient **ni les verdicts de l'auteur, ni les sorties des formaliseurs A/B**, mais les mêmes fichiers existent dans un dépôt public. Ce n'est donc **pas un aveuglement garanti**.
- Les 18 extraits externes sont **incomplets**. Le réviseur peut et doit répondre `CONTEXT_INSUFFICIENT`, plutôt que deviner les hypothèses des articles ou la signification des auteurs.

## Nouveau holdout humain nécessaire pour évaluer le transfert
1. Un tiers indépendant sélectionne des **documents mathématiques originaux complets**, avec URLs et licences, hors des 24/18 cas déjà vus. Les documents, empreintes SHA et protocole d'évaluation sont **figés avant analyse par les formaliseurs**.
2. Deux annotateurs humains, qui n'ont vu ni les réponses de A/B ni les labels de développement, notent séparément : domaine, codomaine, fonction, quantificateurs, hypothèses, proposition originale et possibilités d'ambiguïté.
3. Dans les désaccords, enregistrer les deux annotations et une décision d'adjudication **distincte**. Ne pas écraser silencieusement les divergences.
4. Un auditeur vérifie les identités et l'indépendance (déclarations seules = insuffisantes), les citations et la conservation des documents originaux. La CI ne peut **pas** certifier ces propriétés.
5. Sans annotations admissibles pour une proportion suffisante des sources, le statut est `HUMAN_FIDELITY_NOT_MEASURABLE`, pas 0 % ni 100 %.

## Mesures à publier ensuite, séparément
- **Couverture de lecture** : nombre d'énoncés complets dont le typage est supporté.
- **Accord structural A/B** : signatures de domaine, codomaine, coefficients, opérations, prédicats, quantificateurs.
- **Fidélité aux jugements humains** : accord des IR avec l'intention de chaque auteur sur les éléments effectivement annotés ; valeur inconnue avant revue.
- **Protection contre faux accords** : pourcentage de consensus A/B qui s'avère non fidèle selon la revue.
- **Abstention** : clarifications demandées et hypothèses absentes, en distinguant ambiguïtés réelles, texte incomplet et grammaire hors domaine.

## Limitations actuelles
A et B ont été codés dans la **même session** par le même assistant, et se fondent sur les mêmes définitions et composants exacts. Leur indépendance est donc algorithmique/structurelle seulement, non humaine ni statistique. Les cas contrôlés de TYPED24 ont été vus avant le développement de B. Un succès dans ces conditions établit un fonctionnement technique local, **pas un gain de compréhension mathématique générale**.

L'archivage est en lecture seule, sans règles Horn, certification automatique ou modification de `main`.
