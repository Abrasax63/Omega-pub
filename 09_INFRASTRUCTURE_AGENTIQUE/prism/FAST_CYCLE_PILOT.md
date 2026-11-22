# Omega — pilote accéléré avec file persistante

**État : pilote de raccord vérifié, non activé en cadence périodique.**
Branche `experiment/omega-fast-cycle-15min-2026-11-22`, PR brouillon #230.

## Ce qui est réutilisé

- Code de provenance `provenance_cycle.py` et `provenance_lab.py` de la PR #81.
- Projecteur `audit_v19_shadow_guard.py` et oracle exhaustif V19 de la PR #82.
- Mémoire scientifique `research/omega-100/NNN.md` depuis la branche du programme Omega 100.
- Les questions existantes sont triées en **sondes exécutables préenregistrées** et **prochaines questions non exécutables sans nouveau protocole**.

## La file et la mémoire

`fast_cycle_catalog.json` contient 7 vérifications finies explicites : 2 contrôles de raccord historiques et 5 échantillons finis V19 distincts, avec hypothèse, référence, périmètre et budget maximum. Ajouter une tâche est une action explicite sur le catalogue : **le programme ne fabrique pas tout seul une hypothèse scientifique nouvelle**.

`fast_cycle_queue.py` consomme au plus deux tâches nouvelles par invocation. Le registre `state.json` (schéma 2) et les rapports `results/<id>.json` sont chaînés par SHA-256. Une tâche déjà exécutée ne repasse pas. Tout changement rétrospectif du pré-enregistrement ou du résultat archivé est refusé. Le registre initial est écrit avant la première sonde afin de conserver un état vide vérifiable si elle bloque. Les tâches bloquées restent non validées ; le registre n'avance pas.

À chaque passage, `next_unverified_question()` relit la dernière fiche Omega 100 et en extrait la prochaine question **en statut non exécuté**. Il ne fait aucune inférence ni aucune promotion de résultat. Les résultats négatifs sont conservés comme résultats de test finis, non comme gains.

## Vérification sur GitHub, 22 novembre 2026

- [Run 45047135611](https://github.com/Abrasax63/Omega-pub/actions/runs/45047135611), SHA `bc47b2beca08fa25685cc80af8172c4d10e02fa2`, **succès**.
- Tests : 4/4 du raccord initial, 5/5 de la file, 7/7 du laboratoire de provenance, soit **16/16**.
- Premier appel : `PROV-COPY-SCOPE-V1` et `V19-C5-LEAVES-N8-V1`, 2/2 sondes finies.
- Second appel indépendant au même processus GitHub, en réutilisant le même registre sérialisé : `V19-C4-N7-H2-V1` et `V19-C5-N8-H3-V1`, 2/2 sondes finies.
- **4 identifiants distincts, zéro blocage, zéro gain scientifique nouveau revendiqué.**
- Il reste **3 vérifications préenregistrées**. Cette réserve limitée n'est pas un moteur de découverte infinie.
- Les sorties sont archivées dans `omega-fast-cycle-ci-45047135611`.

Un bogue de bootstrap et une incohérence de chemin des résultats ont été détectés par GitHub Actions, corrigés puis revalidés. Les anciens runs rouges ne doivent pas être considérés comme verts.

## Validation de reprise sur deux runs GitHub distincts

Le [run 45047307664](https://github.com/Abrasax63/Omega-pub/actions/runs/45047307664) a archivé le registre `omega-fast/state.json` et quatre rapports dans `omega-fast-cycle-ci-45047307664`.

Le [run 45047406683](https://github.com/Abrasax63/Omega-pub/actions/runs/45047406683), sur le commit `8df6b603c10e4273c07c461bf02bd9f700a43da2`, a **téléchargé cet artefact d'un run GitHub antérieur**, contrôlé ses premiers identifiants et ses rapports puis repris `fast_cycle_queue.py` avec le même état. Résultats : deux nouvelles sondes `V19-C4-N8-H4-V1` et `V19-C5-N9-H2-V1` exécutées sans blocage, **six identifiants distincts au total et zéro rejeu**. La reprise inter-runs est **VÉRIFIÉE sur ce pilote fixé**.

Les 4 tests initiaux, 5 tests de file et 7 tests des moteurs existants passent encore dans ce run (**16/16**). Après cette reprise, il reste **1 sonde préenregistrée**. Ces calculs finis ne constituent pas six découvertes scientifiques ni une amélioration générale démontrée.

## Limitations restantes

1. La restauration **de ce registre de PR connu** est validée entre deux runs distincts ; le mécanisme générique de sélection automatique du dernier artefact dans une cadence permanente n'a pas encore été évalué sur plusieurs déclenchements planifiés.
2. Les artefacts sont conservés 7 jours. Un état expiré doit bloquer, jamais réinitialiser les expériences silencieusement.
3. Le `schedule` toutes les 15 minutes n'est pas actif sur cette branche : GitHub requiert un workflow sur la branche par défaut. Pas de modification de `main` ni de la tâche ChatGPT existante.
4. La file finie doit être réalimentée avec **de nouvelles questions véritablement préenregistrées** et une vérité terrain indépendante. L'inbox Omega 100 relève une question, mais n'a ni généré un jeu de données nouveau ni lancé de modèle local.
5. Le modèle LLM et les vérificateurs sémantiques n'ont pas été évalués dans ce pilote ; zéro nouvelle certification ou généralisation revendiquée.

## Prochaine vérification décisive

Créer un **nouvel adaptateur de tâche scientifique** avec protocole et cas réservés réellement indépendants, puis tester la sélection du dernier état dans une troisième exécution planifiée (non initiée ici). N'activer une cadence soutenue qu'après ce test et l'estimation du rendement et des coûts. Le GPU n'est pas nécessaire pour ces vérifications exactes.
