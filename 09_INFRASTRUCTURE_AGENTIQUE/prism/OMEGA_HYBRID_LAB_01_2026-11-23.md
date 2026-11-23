# OMEGA-HYBRID-LAB-01 — ossature vérifiable du système d'apprentissage hybride

**23 novembre 2026. PR expérimentale empilée sur #231, aucune modification de `main`.** Statut initial : **CODE D'AUDIT ET CONTRÔLE HORS LIGNE**, pas entraînement autonome exécuté. Les règles de curriculum sont explicites et déterministes, non une compétence de métacognition déjà démontrée. Ne pas revendiquer une connaissance scientifique acquise sur la seule base des tests.

## 1. Objectif et réemploi

La chaîne expérimentale actuelle sait chercher des sources (`incremental_math_library.py`), conserver des candidats dans un registre chaîné SHA-256, refuser leur promotion si la citation n'est pas conforme, et contrôler des relations binaires finies (`concept_abstraction_lab.py`, `omega_memory_real02.py`). Les pilotes #230 et #231 ont montré une recherche autonome mais des échecs de fidélité documentaire et sémantique.

Cette contribution **ne duplique aucun de ces moteurs**. `omega_hybrid_lab.py` consomme leur registre et l'oracle déjà codé, puis ajoute les éléments nécessaires pour l'évaluation d'une boucle d'apprentissage : admission de la preuve, états décisionnels, politique d'exercices et mesure appariée du transfert.

## 2. Périmètre exact livré

- **Porte de provenance** : `source_gate(record, snapshots)` confronte l'ID de la page, son type `web|primary`, sa révision, son empreinte SHA-256 et la citation exacte à un extrait **fourni séparément**. Les anciens enregistrements de PR #231 sans `source_kind` sont considérés comme `web` par compatibilité avec leur récupérateur Wikipédia ; une source primaire requiert un marquage explicite.
- **Porte formelle** : `bounded_gate(...)` réutilise `TARGETS`, `concept_name` et `is_example` de REAL-02 pour contrôler une signature d'axiomes, un exemple positif et un exemple négatif. Cette porte ne certifie **jamais** la prose de la définition.
- **Décision suivante** : `next_action` recommande `RESEARCH`, `REVISE_REPRESENTATION`, `PRACTICE` ou `CHALLENGE`, avec motif explicite. Aucun LLM n'est appelé.
- **Curriculum contrôlé** : `select_exercise` expose trois politiques comparables, `progressive`, `adaptive` et `random`, sur un ensemble d'exercices dont la difficulté est fixée dans un protocole séparé. Aucun problème réservé n'est transmis au générateur de défis.
- **Comparaison D/M/N** : `evaluate_holdout` recalcule la vérité de relations sur `a,b,c` par l'oracle existant, note les réponses directes (D), avec mémoire (M) et avec mémoire neutre (N), bloque les tâches répétées et les différences de tokens d'entrée supérieures à 5 %, et compte erreurs, abstentions, JSON invalides et réponses justes **sur le dénominateur total**.
- **Mémoire des épisodes** : `inspect_ledger` lit les enregistrements via `read_ledger` existant et peut écrire ses résultats d'audit dans un *registre distinct d'épisodes* via `append_candidate`. Les épisodes restent en quarantaine, ne sont pas des connaissances certifiées et n'effacent pas les candidats originaux.

## 3. Exécution hors ligne sans modèle

Dans le répertoire `09_INFRASTRUCTURE_AGENTIQUE/prism` :

```bash
python -m unittest -v test_omega_hybrid_lab
python omega_hybrid_lab.py \
  --ledger /chemin/vers/math_library_candidates.jsonl \
  --snapshots /chemin/vers/source_snapshots.json \
  --output /chemin/vers/omega_hybrid_audit.json \
  --episode-ledger /chemin/vers/learning_episodes.jsonl
```

`source_snapshots.json` est une **liste** de `{"source_kind":"web","page_id":123,"revision_id":456,"excerpt":"texte exact"}`. Les valeurs d'ID, de révision et de texte sont exemples de format, **pas de source empirique ou de validation**. Fournir les véritables extraits correspondant aux empreintes `excerpt_sha256` enregistrées dans le registre. S'ils manquent, la source reste en quarantaine. **Ne jamais remplacer des sources manquantes par du texte inventé.**

Le fichier d'entrée `--ledger` est ouvert en lecture seule. `--episode-ledger` est facultatif, écrit dans un autre fichier, sous contrôle du mécanisme de chaînage existant. L'exécution n'accède à aucun réseau, ne charge pas de modèle et ne modifie aucun poids.

## 4. Comparaison du transfert en conditions réelles — encore à construire

Le paquet de résultats transmis au comparateur contient uniquement des réponses **déjà produites** par un modèle réel, avec ses tokens d'entrée et le jeu d'instances gelé. Une tâche a `id`, `edges` (liste de paires de sommets), `outputs: {D, M, N}` (chaînes JSON brutes) et `prompt_tokens: {D, M, N}` (mesures réellement tokenisées). Le paquet doit déclarer `protocol_frozen=true` et `source_disjoint=true`. Le contrôleur n'en déduit **pas** que l'isolement a été vérifié par un tiers : le rapport précise `DECLARED_NOT_INDEPENDENTLY_AUDITED`.

Le banc de **quatre relations** de REAL-02 reste la première expérience de vérification du câblage. Un éventuel résultat positif est *ponctuel et descriptif*, pas statistiquement significatif. Pour un gain de compétence réel, passer à 40 tâches neuves appariées, puis une seconde cohorte de confirmation et des transformations de représentation. Un résultat sur des données synthétiques ou une réussite de CI ne remplace jamais cette expérience.

## 5. Contrats de sécurité épistémique

- Jamais de promotion automatique d'un énoncé scientifique : `scientific_claims_certified=0`, `free_text_semantics=NOT_VERIFIED`, `new_theorem_certified=false`.
- Une empreinte cohérente avec une **copie locale** n'établit pas l'authenticité externe de cette copie : `NOT_INDEPENDENTLY_RETRIEVED`. L'authenticité exige récupération et attestation indépendantes.
- Les signatures formelles ne couvrent que le vocabulaire fixé de REAL-02. Aucune démonstration de nouvelles représentations abstraites générales, ni de poids entraînés.
- Le module ne tente pas de corriger automatiquement un JSON invalide, d'associer une citation à une autre source, de sélectionner un autre holdout après le résultat, ni de contourner un garde.
- Le sélecteur adaptatif estime une difficulté à partir des derniers résultats ; il ne découvre pas automatiquement une théorie pédagogique optimale. Le tester contre `progressive` et `random` à budget égal.
- L'appel aux modèles, la sélection de passages fiables, les prompts équilibrés, l'isolement du holdout et l'éventuel SFT/LoRA sont **délibérément hors de ce premier patch**.

## 6. Prochaine vérification décisive

Après le test CI hors ligne : récupérer les artefacts bruts REAL-02 dans **une nouvelle exécution admissible**, avec source et poids gelés. Produire trois réponses D/M/N sur les mêmes tâches sans fournir les vérités calculées au modèle. Injecter les réponses et les nombres de tokens dans le comparateur, vérifier individuellement l'attribution documentaire et l'absence de fuite, conserver toutes les sorties. Ne pas rejouer les pages exposées du 22 novembre comme holdout indépendant.

**Un résultat favorable ne prouverait qu'un usage ponctuel de mémoire à ce stade.** Un véritable apprentissage exige une amélioration durable sur des tâches nouvelles et un transfert hors du gabarit entraîné.

## 7. Sources internes

- [PR #230 — premier pilote de recherche Web](https://github.com/Abrasax63/Omega-pub/pull/230)
- [PR #231 — bibliothèque et laboratoire d'abstraction](https://github.com/Abrasax63/Omega-pub/pull/231)
- [REAL-01 — résultat réel, 0 citation admise](https://github.com/Abrasax63/Omega-pub/actions/runs/45059812537)
- `OMEGA_LIBRARY_MEMORY_REAL_02_PREREG_2026-11-23.md` et `omega_memory_real02.py` de la branche expérimentale de PR #231.

**Références scientifiques d'orientation (leurs gains ne sont pas ceux d'Omega) :** [R-Zero (2026)](https://arxiv.org/abs/2508.05004), [Absolute Zero (2025)](https://papers.nips.cc/paper_files/paper/2025/hash/9837dc00ff67d176373268ed48042d49-Abstract-Conference.html).