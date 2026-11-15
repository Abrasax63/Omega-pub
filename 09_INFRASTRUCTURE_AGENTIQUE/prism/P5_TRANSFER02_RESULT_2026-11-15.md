# P5-TRANSFER-02 — résultats descriptifs de transfert de signatures

**Date** : 15 novembre 2026. **Statut : EMPIRIQUE BORNÉ / avantage spécifique Omega NON DÉMONTRÉ.**
Branche `experiment/provenance-semantic-transfer-2026-11-15`, isolée de `main`. Un nouveau module `provenance_pipeline02.py` et **13 tests unitaires locaux réussis**. Aucun run GitHub Actions déclenché ; l'évaluation sur journaux réels ci-dessous est issue d'une **inspection en lecture seule des logs et scripts épinglés**, et non du rejeu Python CI de bout en bout.

## Traçabilité chronologique

1. [Protocole initial gelé](P5_TRANSFER02_PREREG_2026-11-15.md) au commit `30d40071ebf5b3a2c4da95700bc1ca44fee88286`, avant toute ouverture de H1–H4.
2. [Extraits d'entraînement C3/C4](P5_TRANSFER02_TRAIN_EXCERPTS.json) précédemment examinés, jamais comptés au score.
3. Préflight : Bash emploie `++ sha256sum` sur l'entraînement. [Amendement pré-évaluation](P5_TRANSFER02_PREFLIGHT_AMENDMENT.md) documenté ; code et 13 tests gelés à `e48c8e86486830ec6f0239986720f5981de8120c`, avant toute ouverture de H1–H4.
4. H1–H4 inspectés sans adaptation. Une extension H5–H6 a été [figée avant leur lecture](P5_TRANSFER02_DISTINCT_CHECKOUT_FROZEN.md) et reprend strictement les mêmes méthodes.

## Méthodes et interprétation

- Le **constructeur** apprend, sur les seuls cas anciens, les correspondances de signaux `archive-pipeline → recalcul` et `ninja-link → recalcul`.
- Le **classique fixe**, défini avant consultation des nouveaux logs, utilise les *mêmes deux signatures, le même script et le même journal complet*. Aucune information privilégiée ni différence de budget.
- Le validateur repère l'exécution textuelle rapportée d'une opération ; il n'atteste **ni les octets du résultat, ni l'unicité globale des écrivains, ni une certification mathématique**.
- Les labels `recalcul` dans le tableau sont soutenus par le rapprochement syntaxique d'un script épinglé et d'une commande de journal GitHub, mais pas par un oracle d'exécution binaire indépendant. C'est une vérification opérationnelle partielle.

## Observations sur H1–H4

| ID / log GitHub | Contrat et indice | Candidat appris | Classique fixe |
| --- | --- | --- | --- |
| [H1 curl Windows 132705913153](https://github.com/curl/curl/actions/runs/43679197664/job/132705913153) | Script [test.sh](https://github.com/curl/curl/blob/f49c9c95bc31643518b86249e2a7f014699df305/tests/cmake/test.sh) ; `git archive`, `gzip`, `++ sha256sum`, `-DFROM_ARCHIVE=...source.tar.gz` concordent | recalcul | recalcul |
| [H2 curl mbedtls 132705914221](https://github.com/curl/curl/actions/runs/43679197809/job/132705914221) | Script [CMakeLists](https://github.com/curl/curl/blob/f49c9c95bc31643518b86249e2a7f014699df305/src/CMakeLists.txt) ; lien `cc ... -o src/curl` et exécution/version dans le log | recalcul | recalcul |
| [H3 docker image 132413316822](https://github.com/docker/build-push-action/actions/runs/43583601993/job/132413316822) | `docker buildx ... --output type=image` : hors domaine fichier | indéterminé | indéterminé |
| [H4 docker digest 132413316950](https://github.com/docker/build-push-action/actions/runs/43583601993/job/132413316950) | Aucune référence à la cible prédéfinie `/tmp/buildx-build` dans le journal ; absence non probante | indéterminé | indéterminé |

Empreintes **SHA-256 du texte décodé du connecteur puis réencodé en UTF-8**, sans prétendre qu'elles sont celles des octets bruts originaux de GitHub :

- H1 : `31ed176924f4a488378657c0893a1ec0981b18055643a433dea26c772fb4e85d` ;
- H2 : `f7e7f24d9916ddbd56782be486ebf92f6bbad4419178a22b230a29fd048f3491` ;
- H3 : `9d1b01af03554cd7176321428773b99da67857fe2195768df96061eb7710a984` ;
- H4 : `68c3b7d9dd7b1eaeffba0049fabc6a4a97e545c8d0c95998c1d9e3347cc60a25`.

**Bilan H1–H4** : 2 opérations de recalcul documentées par les signatures et 2 abstentions, pour les deux méthodes. Zéro avantage du candidat contre le fixe. Ce ne sont pas quatre évaluations indépendantes (2 dépôts, runs et checkouts corrélés).

## Extension à un checkout différent de curl/curl

Checkout `d67cc443498b943f82ccd7a43b75c210ab2089f5`, différent de l'apprentissage.

| ID | Preuve visible | Candidat / fixe |
| --- | --- | --- |
| [H5 CMake ubuntu ARM 132687805550](https://github.com/curl/curl/actions/runs/43673260605/job/132687805550) | [Script épinglé](https://github.com/curl/curl/blob/d67cc443498b943f82ccd7a43b75c210ab2089f5/tests/cmake/test.sh) : même recette `git archive | gzip` ; journal avec archive, gzip, hash, usage archive | recalcul / recalcul |
| [H6 CMake BoringSSL 132687809497](https://github.com/curl/curl/actions/runs/43673260575/job/132687809497) | [CMakeLists épinglé](https://github.com/curl/curl/blob/d67cc443498b943f82ccd7a43b75c210ab2089f5/src/CMakeLists.txt), ligne `cc ... -o src/curl`, exécutable testé par le job | recalcul / recalcul |

**Bilan H5–H6 :** les deux signatures sont également retrouvées sur ce second checkout. Les deux méthodes restent strictement à égalité. Les scripts et le dépôt sont toutefois les mêmes familles ; ceci n'est **pas** une généralisation inter-projets, ni un apprentissage de nouvelles primitives.

## Verdict rigoureux

- **IMPLÉMENTÉ** : grammaire restreinte, constructeur de deux règles déclaratives, garde de certaines doubles écritures explicites, comparaison au fixe, anti-réutilisation des observations et 13 tests unitaires.
- **EXÉCUTÉ LOCALEMENT** : 13 tests du module sur exemples construits. **OBSERVÉ EN LECTURE SEULE** : signatures sur six jobs réels, quatre confirmations de transformation compatibles avec les scripts épinglés, deux abstentions.
- **NON VÉRIFIÉ** : exécution des 13 tests sur le commit GitHub ; rejeu Python du corpus complet avec octets de logs ; séparation de provenance indépendante des scripts ; preuve d'identité de sorties ; absence générale de doubles écritures ; gain propre à Omega.
- **CONCLUSION** : l'extracteur expérimental couvre des opérations qui manquaient au précédent prototype, et le transfert de *motifs* est observable sur deux checkouts curl. **Aucun gain de décision du constructeur apprenant face à la référence classique de même portée : 0**. Pas de promotion CORE, pas de fusion `main`.

## Prochaine vérification décisive

Isoler une troisième famille logicielle n'utilisant pas les mêmes scripts ou signatures exactes. Construire ou sélectionner un vérificateur déclaratif depuis des cas d'entraînement exclusivement distincts, geler son code et ses règles, puis comparer sur les nouveaux jobs à une grammaire classique générale bien optimisée, avec vérité de production vérifiée au niveau des artefacts. Tant que le constructeur ne sait produire que deux étiquettes mémorisées, il s'agit d'une **synthèse de règles bornée**, pas d'une auto-programmation autonome générale.
