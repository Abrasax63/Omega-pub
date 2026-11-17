# Incident de collecte #44171172370 — ajout de récupération sans changement de cohorte

Le premier run PR du pilote #173, [GitHub Actions #44171172370](https://github.com/Abrasax63/Omega-pub/actions/runs/44171172370), a terminé `synthetic-controls` en succès (14/14), mais le job `collect-authentic-sources` a échoué **avant toute inférence**.

Deux problèmes distincts sont visibles dans les logs :
1. Erreur de configuration mineure : `tee evidence/collection-summary.log` s'exécute avant création du dossier `evidence`.
2. Erreur externe réelle : un appel authentifié à l'endpoint GitHub REST `/actions/jobs/{job_id}/logs` aboutit, après redirection temporaire, à **`HTTP Error 404: The specified blob does not exist.`**. Les métadonnées des runs et le listing des jobs ont été lus ; ce n'est pas une erreur de parseur ni un score négatif.

**Correctif prévu sans modifier les runs ni les sept artefacts figés par préenregistrement `4a66583`** :
- Créer le dossier `evidence` avant `tee`.
- Pour chaque run fixé, tenter la voie officielle `/actions/jobs/{jobid}/logs`; si la source de stockage d'un de ses jobs renvoie une erreur HTTP, essayer l'autre endpoint officiel `/actions/runs/{runid}/logs` (ZIP d'archives de logs du run entier), sans changer les sources, et décompresser en conservant *les véritables octets des traces*. Marquer explicitement la méthode de collecte dans le gold, et ne pas prétendre pouvoir rattacher une trace issue d'une archive de run à un `job_id` si celui-ci n'apparaît pas de manière fiable dans son nom.
- En cas de nouvel échec, marquer `COLLECTION_BLOCKED` et n'exécuter ni le parseur ni le score ; ne pas remplacer la cohorte par des fixtures synthétiques.
- Garder le parseur et le scorer identiques et les jeux testés inchangés. Ne pas exploiter de résultat de holdout : il n'existe pas encore.

Cet incident n'est **pas** un succès ni un échec du critère scientifique du pilote : **INDÉTERMINÉ AVANT COLLECTE**. Historique du run conservé. Aucune modification de `main`.
