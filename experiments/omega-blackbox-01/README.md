# OMEGA-BLACKBOX-01 — apprendre le comportement d'une machine inconnue

[Préenregistrement scientifique du 16 novembre 2026, commit 2715f32](https://github.com/Abrasax63/Omega-pub/commit/2715f3255ed4527c0a411998a62d48e971e7cc97) — créé avant les premiers tests et scores.

## Rupture avec les précédents essais

Dans les PR #127–#135, le contrôleur connaissait les transitions et les sorties de la machine de Mealy ; seul son état initial était caché. Ici, **aucune table n'est accessible à l'apprenant** : il envoie un mot binaire à un système réinitialisé en état 0, et reçoit uniquement le mot de sorties ternaires réellement obtenu. Chaque symbole effectivement envoyé est débité. L'algorithme reconstruit **une hypothèse de machine**, dont nous évaluons le comportement exact.

Cette expérience utilise la bibliothèque académique [AALpy](https://github.com/DES-Lab/AALpy), version **1.6.2**, pour un véritable **apprentissage actif L*** de machines Mealy. **Les trois bras utilisent exactement le même L***. Le changement exploré par Omega est exclusivement la méthode de **choix des contre-exemples probables** lors de l'équivalence approximative :

- **RANDOM_LSTAR** : essais de mots binaires aléatoires, longueurs 3 à 11.
- **FIXED_LSTAR** : ordre fixe longueur puis lexicographique, longueurs 3 à 11.
- **OMEGA_GUIDED_LSTAR** : choisir des chemins de transitions peu testées dans l'**hypothèse courante**, puis des suffixes distinguant des états de l'hypothèse ou des prolongements exploratoires. Le vrai système **n'est jamais lu pour choisir** ces mots. Cette heuristique de « provenance des transitions » est une **variante expérimentale de choix de tests**, et non un nouveau L* ou la réutilisation du « cerveau » d'un agent Omega autonome.

Les trois méthodes interrogent le **même système** avec le même **plafond maximal** de 1 400 symboles (primaire) ou 700 (secondaire) par machine. Le compteur est commun aux questions d'apprentissage et à la recherche de contre-exemples. Les algorithmes peuvent finir plus tôt, d'où des **dépenses réellement différentes** ; aucune égalisation artificielle.

## Cohorte et données réservées

**9 machines**, 3 de chaque taille 4,5,6, deux entrées / trois sorties, transitions et sorties tirées uniformément, état initial 0. Cohortes seed 32041,32051,32061, distinctes par isomorphisme des **1 112 machines anciennes PR #127–#135** et des autres machines du nouveau pilote. Ne rejeter ni machine difficile, ni état inaccessible, ni machine comportementalement non minimale.

Pour chaque machine : **128 mots réservés**, seed `880000 + 100*n + j`, longueur 12 à 20. Le test n'entraîne **aucun** modèle et exclut les mots identiques réellement interrogés, tout en les comptabilisant. La métrique est le pourcentage de **mots entiers** entièrement prédits, puis l'exactitude par symbole.

### Deux niveaux de preuve indépendants

1. Les « équivalences » utilisées durant L* sont **seulement approximatives** (au maximum 32 tests par hypothèse). Un arrêt normal de L* **ne certifie rien**.
2. **Après l'entraînement**, un évaluateur qui, lui, voit le monde réel, construit par BFS le **produit fini du monde et de l'hypothèse** ; soit il certifie une **équivalence comportementale exacte depuis l'état initial**, soit il donne un contre-exemple de longueur minimale. Cet oracle **n'est jamais utilisé pour apprendre**.

Un modèle sans reconstruction complète ou interrompu par le budget est noté comme tel ; il n'est jamais remplacé par la vérité.

## Critère principal

À **1 400 symboles de budget maximal**, OMEGA_GUIDED_LSTAR doit avoir **strictement plus de modèles exactement équivalents** que RANDOM_LSTAR **et** FIXED_LSTAR sur les 9 machines, **sans perdre** en exactitude moyenne des mots réservés par rapport à chacune. Sinon **`NO_DEMONSTRATED_QUERY_GAIN`**.

Le budget de 700 est secondaire. Une victoire descriptive sur 9 machines n'est ni une certification de généralisation, ni une preuve d'intelligence d'un agent autonome.

## Exécution reproductible

    python -m pip install aalpy==1.6.2
    python -m unittest discover -s experiments/omega-blackbox-01 -p test_blackbox.py -v
    python experiments/omega-blackbox-01/blackbox_lab.py --output /tmp/omega-blackbox-01.json

GitHub Actions (Python 3.11, dépendance publique gratuite) exécute **14 contrôles**, puis les 9 systèmes × 3 bras × 2 plafonds et archive `report.json`, `report.sha256`, `summary.jsonl`. Aucun modèle de langage, aucune API payante, aucun GPU. La PR est **DRAFT**, empilée sur #135, sans fusion ni modification `main`.

Les journaux distinguent requêtes d'apprentissage `MQ` et requêtes d'équivalence `EQ`, état provisoire du modèle, erreurs de prédiction, dépense réelle et certification BFS. Les tableaux de vérité du monde sont **archivés seulement pour audit après expérience**, jamais fournis aux apprenants.

**Limites** : un SUL en mémoire simule le monde inconnu ; les méthodes sont des variantes de test d'équivalence à même L*, et les machines sont synthétiques. Les sorties des vieux pilotes et les nouveaux benchmarks ne sont pas directement comparables, car les tâches diffèrent.
