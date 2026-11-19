# Parité incrémentale avec garantie de budget

19 novembre 2026, 15 h 00 (Paris). **IMPLÉMENTÉ / EXÉCUTÉ / VÉRIFIÉ sur cas synthétiques.** Branche `experiment/omega-100-2026-11-18`, départ `d808fff5a3e087dbcbb1b97386ec19fcf6a4740a`. Pilote hors numérotation, suite du [prétest qui privait B de budget](../budgeted-probe/README.md).

Question fixée avant test dans le [protocole](protocol.md) : la détection des contradictions dès la lecture améliore-t-elle la couverture sous un plafond commun de 64 étapes ? Un candidat incrémental maintient les composantes et les couleurs relatives. Une relation interne contradictoire suffit à conclure. Une relation entre deux composantes réétiquette la plus petite et applique le XOR nécessaire à tous ses sommets. Une unité est débitée par relation lue et par sommet réétiqueté. La référence garde son compteur habituel (construction et visites du graphe pour B). Le coût d'initialisation et d'extraction du masque est inclus dans le temps. L'oracle exhaustif et les contrôles des témoins sont hors coût pour tous.

## Garde de coût

La route expérimentale emploie l'insertion uniquement si la référence demanderait B en parité et que `m + floor(n × ceil(log2(n)) / 2) ≤ 64`. Sinon elle appelle la référence. Les portées `n` et `m` comptent respectivement les sommets et les relations.

Justification : la somme, sur les composantes, de `s log₂(s)` augmente d'au moins `2a` lors d'une fusion de tailles `a ≤ b`. À `b=a` l'augmentation vaut `2a` et elle croît avec `b` car sa dérivée est `log₂((a+b)/b)`. Le potentiel part de zéro et ne dépasse pas `n log₂(n)`. Chaque fusion réétiquette `a` sommets. Le coût total entier est donc borné par la formule conservatrice ci-dessus. Cette garantie concerne le compteur instrumenté. La correction du solveur suit l'invariant de composante : les couleurs relatives satisfont toutes les relations lues, et une contrainte interne qui les contredit ne peut être corrigée par inversion commune. Une fusion préserve les relations internes et satisfait la nouvelle relation.

## Comparaison

Cas réservés créés après gel du code : 32 graphes dont des variantes denses, des arêtes réorientées, des boucles et des doublons, plus quatre sommes pour contrôler le routage inchangé. Le témoin incohérent, le témoin cohérent et les tests de stress sont exécutés avant la réserve. L'oracle indépendant énumère les colorations et vérifie les témoins positifs.

| Politique sur la même réserve | Corrects | Abstentions | Faux verdicts | Gains / pertes face à la référence | Étapes cumulées | Temps médian |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Règle de référence | 24/36 | 12 | 0 | 0 / 0 | 1 493 | 260,13 µs |
| Insertion sans garde | 33/36 | 3 | 0 | 10 / 1 | 1 135 | 240,02 µs |
| Insertion avec garde | 33/36 | 3 | 0 | 9 / 0 | 1 135 | 235,82 µs |

Temps sur 300 passages du lot, ordre tournant, choix et résolution compris. Les compteurs d'opérations reflètent les primitives propres aux méthodes. Les temps sont indicatifs sur ces tailles et ce poste. Le garde emploie l'insertion sur 29 cas et la référence sur 7. Sept gains concernent les graphes denses cohérents, deux concernent la famille à répétitions. Résultats des sommes inchangés, 3/4. [Mesures et groupes](results.json).

Sur le témoin historique, l'insertion détecte la contradiction en 32 étapes contre 36 pour B. Le prétest précédent s'abstenait à 64. Le nouveau témoin à 56 relations montre pourquoi la garde compte : B certifie en 59 étapes. L'insertion brute s'arrête à 64 avant de lire la dernière relation. La version gardée choisit B et préserve ce verdict. Ce témoin fait partie des contrôles et du code public. Les cas réservés et verdicts individuels restent hors dépôt.

**Décision :** conserver uniquement le candidat gardé comme expérience exploitable, sans basculement du pipeline actif. Les 16 tests métier passent. Un balayage séparé de 760 graphes simples signés jusqu'à quatre sommets donne zéro erreur et zéro dépassement de la borne. Ce contrôle porte sur une petite taille exhaustive, distincte du lot synthétique. Aucun modèle ni API. Prochain essai : tester si un ordre de lecture moins sensible au placement des contradictions peut réduire les abstentions parmi les graphes que le garde renvoie encore à B, avec coût du réordonnancement inclus.

## Reproduction

Reprendre `solver.py` et `rule.py` du [pilote structurel](../structural-choice/README.md). Placer ces fichiers avec `incremental.py`, `trial.py` et `exhaustive_check.py` dans un dossier temporaire. Exécuter `python trial.py CAS_RESERVES.json` et `python exhaustive_check.py`. Format de réserve identique au prétest : liste d'objets `group` et `case`. Les [empreintes](freeze.sha256) épinglent les fichiers et la réserve hors dépôt. SHA-256 du relevé `85966df9bd11b7d39c988a47c7b1364c865536e6df17cc7e6670528bffb98952`.
