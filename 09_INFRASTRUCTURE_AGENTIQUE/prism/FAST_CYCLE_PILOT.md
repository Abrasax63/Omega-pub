# Pilote accéléré Omega — raccord aux moteurs existants

**PR #230, état expérimental, 22 novembre 2026.** Aucun changement de `main`, du planificateur ChatGPT horaire, des données privées ou des branches de travail #81/#82/Omega 100. Aucune API payante ni GPU.

## Ce qui fonctionne déjà

- Le workflow charge en lecture seule les vraies branches `work/omega-provenance-lab` (#81), `work/omega-math-brick-pilot-2026-11-14` (#82) et `experiment/omega-100-2026-11-18` (mémoire Omega 100).
- Il relit la suite des fiches `NNN.md` et les empreintes des deux modules scientifiques. Les lacunes dans la numérotation bloquent le pilote.
- Il lance deux tests falsifiables **distincts**, avec entrées synthétiques définies dans `fast_cycle.py`, références et critères avant exécution. Ils ne sont pas de nouvelles découvertes ni des gains externes.
  - `PROV-COPY-SCOPE-V1` : candidat de provenance `cp -v`, comparaison avec une référence vide et une règle fixe ; vérifie les abstentions sur journaux incomplets et écritures multiples.
  - `V19-C5-LEAVES-N8-V1` : contrôle du projecteur V19 existant face à une énumération exhaustive, sur deux cas finis à huit états, en modes local/global.
- Le registre JSON est chaîné par SHA-256 et refuse doublons, altérations et état absent (sauf amorçage explicite). À second passage, une tâche terminée ne se rejoue pas. Les statuts `VERIFIED_FINITE`, `REFUTED_ON_PILOT` et `BLOCKED` portent uniquement sur les critères finis de ce pilote.
- Les traces du run sont archivées ; un run GitHub sur PR reçoit un registre **isolé**, non réutilisé par les futurs schedules.

## Exécution vérifiée sur GitHub

Run [45045775658](https://github.com/Abrasax63/Omega-pub/actions/runs/45045775658), branche `experiment/omega-fast-cycle-15min-2026-11-22`, SHA `7eafcbf41a7fc9ca1fc43c7744030cb8cba47bed` : succès.

- 4/4 tests contractuels du pilote ; 7/7 tests existants de provenance.
- 2/2 vérifications finies exécutées, 0 blocage.
- Provenance : 2 confirmations correctes, 0 fausse, 2 abstentions ; **égalité avec la règle fixe**, donc **aucun gain externe démontré**.
- V19 : 4 projections ; 0 divergence candidat/exhaustif et 0 divergence local/global sur ces deux cas ; pas de preuve de généralisation.
- Artefact `omega-fast-cycle-ci-45045775658` : journal d'exécution, deux comptes rendus JSON et journaux de tests. Ces pièces constituent une validation d'intégration, pas une nouvelle certification scientifique.

## Limites importantes, avant activation

1. Le `schedule` GitHub toutes les 15 minutes ne fonctionne **que si le workflow est présent sur la branche par défaut**. Sur cette PR en brouillon, il **n'est pas actif**. Il ne faut pas fusionner uniquement pour activer la cadence sans revue. Un ordonnanceur externe est une alternative pour rester entièrement hors de `main`.
2. Les deux tests falsifiables prédéfinis sont un *pilote de raccord*. Après eux, le registre empêche correctement les rejouements et rapporte **0 nouvelle expérience**. Cela ne fournit donc pas encore 96 expériences originales par jour.
3. Le stockage de l'état dans des artefacts GitHub (7 jours) est un mécanisme pilote ; sa restauration inter-runs et sa résistance aux expirations doivent encore être vérifiées en condition réelle. Si l'état manque, le programme s'arrête plutôt que de le réinitialiser automatiquement.
4. Le planificateur de rôles du prisme prépare le travail mais n'appelle aucun modèle. Le pilote n'ajoute pas de génération LLM autonome et ne revendique aucune découverte ou compréhension sémantique nouvelle.
5. La cadence n'a pas été mesurée en charge réelle ; la limitation à 12 minutes par job et la concurrence non chevauchante ne garantissent pas des exécutions ponctuelles à chaque quart d'heure.

## Prochain test décisif

Sur un exécuteur explicitement autorisé, faire un **amorçage manuel**, télécharger le registre du premier passage, puis lancer le second passage avec **ce même registre**. Attendu : 0 expérience répétée, empreintes identiques, aucune nouvelle conclusion. Ensuite connecter une **file d'expériences inédites** alimentée par les problèmes non résolus et les références de #81/#82/Omega 100, avec séparation stricte entre propositions, corrigés réservés et vérifications. N'activer le calendrier rapide qu'après cette démonstration et la validation des limites de coût.
