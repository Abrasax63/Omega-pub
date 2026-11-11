# OMEGA-EVIDENCE-001 — révision de certificats sur 40 changements Git réels

**11 novembre 2026. Statut : EMPIRIQUE REPRODUCTIBLE sur historique public Git, CALCUL EXACT pour l'applicabilité de contenu versionné. Avantage spécifique d'Omega : NON DÉMONTRÉ.**

## Contexte et gel avant résultats

Le protocole a été gelé au commit **`f8656498c699619591c18e06d33d025834b6fc88`**, avant téléchargement et examen des 40 transitions du corpus externe. Source : `pallets/flask`, commit final fixé à `49943b5a94413a530761350f04e896f76e8d620e` ([GitHub](https://github.com/pallets/flask/commit/49943b5a94413a530761350f04e896f76e8d620e)), 41 commits consécutifs de **premiers parents** en remontant l'historique.

Le commit historique initial est **`4b8bde97d4fa3486e18dce21c3c5f75570d50164`**. Sur cet état, l'algorithme sélectionne **128 chemins** sous `src/flask`, `tests` et `docs`, par tri **SHA-256 du chemin**, avant l'examen des modifications. Il en déduit **384 attestations** : une par fichier, une par couple et une par triple de dépendances consécutives. Vingt transitions chronologiques constituent la partition de calibration descriptive ; les vingt suivantes, la partition de test. Aucun réglage n'est choisi à partir des résultats de ces transitions.

**Attention :** une attestation certifie ici seulement « les octets des fichiers dont dépend cette assertion possèdent les empreintes SHA-256 associées à cette version Git ». Elle ne démontre **ni la vérité d'une proposition scientifique**, ni qu'un ancien contenu est devenu mathématiquement faux, ni l'authenticité de l'auteur de la source. Les deux digests de deux commits différents peuvent être tous deux des observations historiques valides. Ce protocole évalue une infrastructure de **provenance et de portée des attestations**, non la logique formelle d'un théorème.

## Résultat de l'évaluation externe : 20 transitions TEST

Les 384 assertions sont évaluées après chacune des 20 transitions de test, soit **7 680 occurrences assertion×révision par politique**.

| Politique | Attestations courantes exactes | Attestations faussement déclarées courantes | En attente/non accessibles | Lectures d'octets + SHA-256 comptées |
|---|---:|---:|---:|---:|
| `no_refresh` (témoin négatif) | 4 603 | **3 077** | 0 | 0 |
| `full_reverify` (référence sans plafond) | **7 680** | 0 | 0 | **2 560** |
| `dependency_index_8` (index simple, baseline forte) | **7 680** | **0** | **0** | **34** |
| `omega_ledger_8` (registre expérimental) | **7 680** | **0** | **0** | **34** |
| `invalidate_all_8` (témoin de perte d'état) | 161 | 0 | **7 519** | 160 |

Les lectures sont des **unités logiques de vérification de contenu** (octets du Git blob + SHA-256) ; les lectures des métadonnées Git permettant de lister les changements, communes à tous les bras, **ne sont pas incluses**. Les chiffres ne mesurent ni temps machine, ni coût réseau, ni tokens ni prix réel. La stratégie `full_reverify` ne respecte pas le plafond 8 et figure seulement comme référence de vérification exhaustive, non comme concurrent admissible à budget égal.

**Verdict :** C et D suivent exactement les mêmes vérifications et donnent les mêmes sorties sur les **40 transitions**, pas seulement les 20 de test. **Aucun avantage propre au registre Omega sur un index de dépendances classique.** Le résultat de sécurité intéressant est commun : ils ne présentent aucune attestation périmée comme actuelle, suspendent les validations non acquises et conservent l'historique. La faible dépense (34 lectures sur les 20 transitions TEST) provient de la possibilité de **reconnaître les dépendances réellement touchées**, propriété bien connue des index de dépendances, et non d'une intelligence scientifique nouvelle.

## Contrôles sur toutes les 40 transitions et sources indépendantes

- **29/40 transitions** touchent au moins un chemin du portefeuille et 11/40 n'en touchent aucun.
- **72 événements fichier sélectionné modifié** sur l'historique ; **une transition** dépasse le budget de huit modifications pertinentes. La stratégie indexée laisse temporairement **six occurrences d'attestation en attente durant les vingt premières transitions**, puis rattrape son retard à la transition suivante. Elle ne les présente jamais comme courantes avant vérification.
- Sur les 20 transitions de calibration : index/Omega **7 674 attestations exactes**, **0 fausse courante**, **6 en attente**, **38 lectures**, contre **2 560** pour la vérification complète. Le témoin sans contrôle présente déjà **1 685 occurrences périmées comme actuelles**.
- L'état final du registre Omega comprend **811 enregistrements de certificats historiques** associés aux commits au moment de leur vérification. Une implémentation **JavaScript indépendante** a reconstruit exactement les **40 transitions**, les mêmes décisions d'index, et les **811 enregistrements**. Elle a vérifié **1 762 dépendances de ces certificats** directement contre les octets réels des Git blobs à chaque commit historique revendiqué.
- **Diff Git trompeur :** l'interface qui exécute le rejeu confronte chaque manifeste `git diff --name-only` avec les métadonnées de `git ls-tree`, et bloque une discordance plutôt que de délivrer une preuve périmée. Ce contrôle est interne au même dépôt Git ; il ne constitue pas une vérification indépendante de l'auteur.
- Les tests adversariaux couvrent aussi suppression, changement de mode sans changement d'octets, dépassement du plafond huit, absence du rafraîchissement, conservations des anciens certificats et paths manquants.

## Raccordement au Prisme actuel, **opt-in et sans effet de bord**

`planner.plan_mission` accepte désormais **facultativement** un champ `source_revision_audit` : commits déclarés, liste déclarée des chemins modifiés et assertions assorties de leurs dépendances. Le module `prism/versioned_evidence_planner_bridge.py` renvoie uniquement les **identifiants potentiellement affectés**, sans modifier `next_action`, les rôles, les tâches, le statut d'exécution, ni la mémoire persistante.

**Différence de confiance essentielle :** cet adaptateur de planification ne lit pas lui-même Git et ne vérifie donc **ni l'intégrité du diff fourni, ni les fichiers, ni une preuve scientifique**. Même si le fournisseur déclare son diff « complet », la sortie n'étiquette **jamais** les autres assertions comme certifiées courantes. Les entrées sont bornées (256 assertions, 256 chemins modifiés, 16 dépendances par assertion, 512 caractères par chemin), les chemins non canoniques et les formats malveillants sont rejetés. C'est une interface de préparation de vérification, pas une mutation automatique des certificats.

## Vérification CI et artefacts

- [GitHub Actions externe #43081588435](https://github.com/Abrasax63/Omega-pub/actions/runs/43081588435) — **SUCCESS** : huit tests de falsification, 40 transitions Git réellement téléchargées et inspectées, seconde implémentation JavaScript indépendante et registre complet JSON.
- [GitHub Actions externe #43082153608](https://github.com/Abrasax63/Omega-pub/actions/runs/43082153608) — **SUCCESS** après ajout du diagnostic opt-in au planificateur. Les politiques de comparaison et le protocole restent inchangés.
- [GitHub Actions RCE #43082153738](https://github.com/Abrasax63/Omega-pub/actions/runs/43082153738) — **SUCCESS, 218 tests du Prisme**, plus 6 tests MCP et contrôles RCE/index.
- [Artefact des 40 transitions et certificats historiques](https://github.com/Abrasax63/Omega-pub/actions/runs/43081588435/artifacts/13884497361) (résultats du premier benchmark validé, avant raccordement du planificateur, sans modification du benchmark).

Premier défaut visible et réparé : une valeur **attendue dans un test unitaire SHA-256** a été mal recopiée ; sept des huit tests ont initialement réussi, puis la valeur de référence a été corrigée et les huit ont réussi. Les politiques et données gelées n'ont pas été modifiées après les résultats.

Reproduction :
```bash
# Depuis 09_INFRASTRUCTURE_AGENTIQUE/prism :
python -m unittest -v test_versioned_evidence_replay test_versioned_evidence_planner_bridge

# Le workflow dédié télécharge exactement le commit Flask préenregistré.
python versioned_evidence_replay.py --source-repo /chemin/vers/flask-pinned \
    --json-output /tmp/evidence-ledger.json
node versioned_evidence_crosscheck.mjs /chemin/vers/flask-pinned /tmp/evidence-ledger.json
```

## Implication pour l'objectif d'Omega

Cette expérience valide une **infrastructure de versionnement et de non-régression de la provenance**, pas une intelligence scientifique stratégique supérieure. Un index simple suffit à obtenir la même qualité au même budget ; les 811 archives montrent que conserver le contexte antérieur est faisable et vérifiable sans le confondre avec l'applicabilité actuelle.

**Verrou suivant, encore ouvert :** définir des affirmations **sémantiques** contradictoires issues de sources documentaires réelles, avec dates/autorité, annotations indépendantes et possibilité qu'une mise à jour de fichier ne change pas la vérité scientifique. Comparer quatre bras à même budget : vérification totale, simple index de dépendances + validation de la proposition, historique de certificats + validation, et planificateur adaptatif. Ne pas recycler des digests de fichiers comme substituts d'une preuve mathématique.

**Gouvernance :** PR DRAFT empilée sur #40 ; `main`, SQLite, mémoire CORE et résultats certifiés inchangés.
