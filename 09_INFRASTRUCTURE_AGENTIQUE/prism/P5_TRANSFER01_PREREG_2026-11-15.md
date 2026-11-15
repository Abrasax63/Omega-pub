# P5-TRANSFER-01 — pré-enregistrement du transfert sur des journaux GitHub inédits

Date du gel : 2026-11-15 (UTC). Branche expérimentale empilée sur la PR #81, base `20a23455c9f7470c409e5904b6b92f60e850109c`. **Ce document est créé avant le téléchargement des journaux ci-dessous.** La liste des exécutions et leurs noms ont été obtenus par les métadonnées GitHub Actions ; les journaux n'ont pas été ouverts pour sélectionner les cas.

## Hypothèse falsifiable

Un candidat de vérification de provenance construit uniquement à partir des exemples antérieurs de la PR #81 pourrait produire, sur de **nouveaux jobs**, plus de confirmations correctes que le meilleur comparateur déterministe fixé ci-dessous, **sans** fausse confirmation et à preuves visibles égales. Une égalité ou une perte est un résultat négatif. Un gain sur quatre jobs ne suffit pas à établir une supériorité générale.

## Échantillon fixé AVANT lecture des logs

Tous ces jobs ont le statut GitHub `success` et sont publiquement identifiés. Le dernier run curl est postérieur aux expériences du 14 novembre ; les jobs docker appartiennent à une autre famille de dépôt.

| Lot | Dépôt et SHA du checkout | Run / job gelé | Cible de provenance posée avant lecture |
| --- | --- | --- | --- |
| C1 | curl/curl `f49c9c95bc31643518b86249e2a7f014699df305` | [Source 43679197664, job 132705913201](https://github.com/curl/curl/actions/runs/43679197664/job/132705913201), CM integration ubuntu-26.04-arm | `source.tar.gz` (script CMake historique ; à confirmer pour ce job) |
| C2 | curl/curl même checkout | [Linux 43679197809, job 132705914259](https://github.com/curl/curl/actions/runs/43679197809/job/132705914259), CM boringssl | `src/curl` (cible de compilation ; à confirmer) |
| D1 | docker/build-push-action `562e51947939164e4fe808a6eab5101977e509e0` | [CI 43583601993, job 132413316948](https://github.com/docker/build-push-action/actions/runs/43583601993/job/132413316948), provenance (binary) | `/tmp/buildx-build` (annoncé dans le nom du job ; existence non vérifiée) |
| D2 | docker/build-push-action même checkout | [CI 43583601993, job 132413316790](https://github.com/docker/build-push-action/actions/runs/43583601993/job/132413316790), minimal | `/tmp/buildx-build` (contrôle négatif de couverture, pas une vérité terrain) |

Cette sélection n'est **pas** aléatoire, les jobs d'une même famille sont corrélés et les deux cibles curl ont été inspirées de scripts déjà étudiés. Il s'agit d'un **petit test de transfert chronologique et inter-dépôts**, pas d'un holdout aveugle fort. Aucun remplacement d'un job manquant par un autre job plus favorable.

## Séparation temporelle et méthodes

1. Geler l'extracteur actuel `provenance_xtrace.py`, le constructeur `provenance_cycle.py`, `provenance_lab.py`, la règle fixe `fixed_verdict`, le budget et le protocole de choix avant toute lecture des quatre journaux.
2. Le candidat est **construit à partir du corpus antérieur** de la PR #81 ; les données C1/C2/D1/D2 ne peuvent contribuer ni à son choix ni au réglage des parseurs.
3. Chaque méthode reçoit **le même journal complet** puis au plus **un même script épinglé** : deux pièces maximum. Le script peut étayer la cible et le vrai verdict mais pas modifier rétroactivement la règle. Interdiction d'extraits privilégiés préparés après observation des logs.
4. Deux comparateurs : (a) la règle déclarative de référence de la PR #81, (b) la règle fixe `fixed_verdict` et les parseurs figés. La comparaison principale est contre le **meilleur comparateur fixe**, pas l'abstention seule.
5. L'oracle est un audit séparé du code au checkout épinglé et de l'exécution. Si l'exécution d'une transformation précise n'est pas attestée, l'attendu est **indéterminé**. Les journaux seuls ne démontrent pas l'identité d'octets. Conserver pour chaque cas URL, SHA du log, SHA du script, sortie, attestation et éventuelles contradictions.
6. Distinguer au résultat : `copie`, `recalcul`, `indéterminé`, `inaccessible`. Les cas sans attestation indépendante ne produisent pas de victoire. L'absence de trace ne prouve pas l'absence de production.
7. Rapporter le nombre de confirmations correctes, fausses confirmations, abstentions, pièces réellement lues, par job et par famille. **Ne pas** compter les jobs corrélés comme des reproductions indépendantes.

## Portes d'acceptation et d'arrêt

- **GO pour revue humaine seulement** : au moins une confirmation correcte de plus que le meilleur fixe, zéro fausse confirmation, aucune bonne confirmation antérieure perdue, même budget et preuve, extraction indépendante du candidat. Sans cela **NO-GO**.
- **STOP/INDÉTERMINÉ** : log inaccessible, SHA du checkout invérifiable, script incohérent, cible non présente, annotation impossible, ou dérivation postérieure du parseur. Ne modifier ni seuil ni jeux après résultat.
- **Promotion CORE interdite** sans une seconde famille réellement réservée, validation externe et tests de non-régression. Aucune fusion `main`, aucune exécution de workflow externe déclenchée par cette PR.

## Ordre d'exécution et fichiers attendus

(1) ce pré-enregistrement publié et empreinte de tête de branche ; (2) construction/gel du candidat sur anciennes traces ; (3) collecte des quatre logs et scripts (lecture seule) ; (4) observations brutes hachées ; (5) audit contradictoire oracle ; (6) évaluation figée ; (7) rapport y compris négatif.

Toute impossibilité de récupération sera documentée sans remplacer les cas. Un autre pilote sur la sélection autonome des briques V19 (#82) sera évalué séparément, pour éviter de mélanger les métriques.
