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

## Limitations non résolues

1. L'essai de reprise a été fait dans **deux invocations de programme au sein d'un même job GitHub**, et non dans deux runs GitHub indépendants. La restauration depuis des artefacts inter-runs reste à vérifier.
2. Les artefacts sont conservés 7 jours ; un état expiré doit bloquer, jamais remettre le compteur à zéro silencieusement.
3. Le `schedule` toutes les 15 minutes n'est pas actif sur cette branche : GitHub requiert un workflow sur la branche par défaut. Pas de modification de `main` ni de la tâche ChatGPT existante.
4. La file finie doit être réalimentée par de véritables questions préenregistrées et de nouvelles sources indépendantes. L'inbox Omega 100 identifie une piste, mais n'a ni généré de nouveau jeu de test ni lancé de modèle local.
5. Le modèle LLM et les vérificateurs sémantiques n'ont pas été évalués dans ce pilote ; zéro nouvelle certification ou généralisation revendiquée.

## Prochaine vérification décisive

Démontrer **deux runs GitHub distincts** utilisant le même registre récupéré depuis un artefact précédent, avec contrôle de ses empreintes et du dernier ID : zéro répétition et refus si un rapport manque. Ensuite ajouter un adaptateur d'expérience nouvelle (Omega100 ou provenance externe), budget fixé et données de réserve réellement indépendantes. N'activer la cadence qu'après cette validation, sans achat de GPU.
