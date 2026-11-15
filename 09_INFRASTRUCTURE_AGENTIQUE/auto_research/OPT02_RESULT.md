# OMEGA-OPT-02 — résultat final du premier cycle

**Date : 15 novembre 2026. Statut : EXÉCUTÉ, EXACTITUDE CONFIRMÉE SUR LES CAS TESTÉS, AVANTAGE ALGORITHMIQUE NON DÉMONTRÉ.**

## Provenance et protocole

- Contrat scientifique gelé avant génération : [OPT02_PREREG.md](OPT02_PREREG.md), commit `184241464ceb425175ab5a48ea7e771cc06e44f4`.
- Modèle réel Qwen2.5-Coder-3B-Instruct GGUF Q4_K_M, poids SHA-256 `724fb256bec1ff062b2f65e4569e871ad2e95ab2a3989723d1769c54294730b7`.
- [Run original 43746056945](https://github.com/Abrasax63/Omega-pub/actions/runs/43746056945) : **3 appels LLM réels** (≤800 tokens de sortie par appel), **un seul programme distinct** (trois réponses identiques), SHA-256 source `46ddcea87b8640eae0d1757312f034d0d0ebe5db5c814264bf75751e08e0af77`. L'artefact initial [14173854768](https://github.com/Abrasax63/Omega-pub/actions/runs/43746056945/artifacts/14173854768), empreinte du JSON brut `35e5818fcccc239e38e315d164ce0938047e5909190b7b33403251dfd1b66a04`.
- Première exécution de développement : **échec infrastructure**, répertoire temporaire `0700` inaccessible au conteneur non-root. Ne pas interpréter comme un défaut du modèle.
- [Rejeu 43747010721](https://github.com/Abrasax63/Omega-pub/actions/runs/43747010721) : après correction `0700 → 0755`, **30/30 cas de développement corrects**, **zéro nouvel appel LLM**. Premier passage externe arrêté sur `ModuleNotFoundError: gate` sous Python `-I` : encore un défaut d'intégration, aucun score final.
- [Exécution finale 43747225462 — SUCCESS](https://github.com/Abrasax63/Omega-pub/actions/runs/43747225462), commit `a32559f7974b9797eb2795c284030d1700959c36` : imports rétablis depuis le seul répertoire d'évaluation monté en lecture seule. **Aucun nouveau modèle ni nouveau candidat.** [Archive JSON des résultats — artefact 14175145328](https://github.com/Abrasax63/Omega-pub/actions/runs/43747225462/artifacts/14175145328).

## Résultat scientifique

- **48/48 évaluations exactes** sur quatre réseaux historiques de NetworkX 3.5, chacun représenté par deux familles de relations, horizons 0,1,8,32,128,512.
- **32 cas chronométrés** (8 familles × 4 horizons), **9 répétitions de 20 appels** de chaque méthode et par cas, ordre randomisé, CPU mesuré dans Docker sans réseau.
- Rapport vitesse (plus rapide des deux classiques, **par cas** / code Qwen), moyenne géométrique = **0,8853257650634475**. Cela correspond à environ **1,1295× plus de temps CPU** pour Qwen, selon cette métrique, sur ce corpus, sans signification statistique générale.
- **2/8 familles** légèrement positives ; test de signe unilatéral dans le sens « Qwen plus rapide » : **p=0,96484375**. La majorité ne soutient pas une amélioration.
- Deux portes `gate.py` inchangées : face à `square-lowbit`, `REVIEW_REQUIRED` (coût total déclaré 646132 contre 650035 μs de médianes agrégées, effet minuscule et non fiable) ; face à `square-scan`, **REJECTED** (572099 contre 646132 μs). Cette asymétrie confirme pourquoi le choix du comparateur fort est essentiel.
- Le critère primaire préenregistré, **moyenne géométrique ≥1,10 avec médianes ≥1,03 dans 8/8 familles**, échoue clairement : **`NO_DEMONSTRATED_ADVANTAGE`**.
- L'implémentation générée par Qwen reproduit le calcul classique par exponentiation binaire et parcours des bits, sans principe nouveau démontré.

## Audit arithmétique indépendant du rapport

Les 32 rapports par cas ont été recalculés à partir des médianes CPU archivées : même moyenne géométrique `0,8853257650634475`, même nombre de familles positives `2` et même test de signe `0,96484375`. Les graphes NetworkX sources, leurs tailles et leurs empreintes sont conservés dans l'artefact.

## Limites et décision

Les jeux de graphes proviennent d'une bibliothèque **extérieure à Omega**, mais sont publics ; aucun tiers n'a gardé ces réponses en secret. Une seule machine d'exécution partagée n'établit pas la performance générale. Le calcul des médianes protège partiellement contre le bruit, sans créer une certification. L'isolation Docker partage le noyau. Aucune amélioration des poids du modèle ni du planificateur d'Omega n'a été démontrée.

**Décision : garder le candidat et le résultat négatif ; ne pas promouvoir au CORE ; ne pas fusionner ; ne pas optimiser sur les mêmes 32 cas.**

## Nouvelle hypothèse à tester lors d'un AUTRE protocole

Le goulet observé est **l'absence de diversité des propositions** : malgré trois variantes de consigne, Qwen a produit trois fois le même programme. La prochaine expérience devrait comparer à budget égal une génération libre et une génération par *modifications locales ciblées* d'un algorithme fort, avec un nouvel ensemble de tests réservé et une référence classique forte, sans accès aux scores de OPT-02 pour sélectionner la solution. Ne pas promettre qu'une variation du prompt suffit à améliorer le raisonnement.
