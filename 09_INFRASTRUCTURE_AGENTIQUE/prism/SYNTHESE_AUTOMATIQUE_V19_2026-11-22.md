# Synthèse structurelle automatique — premier essai V19

**22 novembre 2026. Expérience de recherche limitée, sans modèle de langage ni API payante.** Branche `experiment/omega-fast-cycle-15min-2026-11-22`, PR #230. Travail non fusionné sur `main`.

## Objectif discriminant

Passer des thèses écrites manuellement à une **génération algorithmique de règle** à partir d'exemples finis, suivie d'une falsification indépendante. L'essai mesure une capacité restreinte de *synthèse de programmes* et de reconstruction d'une structure connue, **pas** une compréhension générale de textes, de preuves ou de mathématiques.

La source existante `research/bricks/OBS-V19-SIGNED-CORE_2026-11-19.md` de la PR #82 est épinglée par Git blob `1fdff7076cb769765193b0955bf1863e2b54aaae`. Elle avait déjà présenté le mécanisme de contradiction minimale par cycle signé. Aucune revendication de nouveauté.

## Protocole effectivement exécuté

- **Entrées** : contraintes forcées et relations orbitales produites par `test_v19_locality_l_plus_1.py` (PR #82) ; systèmes cohérents uniquement, exactement quatre relations événementielles.
- **Oracle indépendant du candidat** : énumération de toutes les (2^n) colorations binaires admissibles, puis contrôle d'une contradiction minimale par suppression de chacune des quatre relations.
- **Grammaire fournie** : sept caractéristiques de graphe, dont cycle simple du quotient, parité XOR, sommets, boucles, unicité des arêtes et contrôles distracteurs. Les conjonctions de 1 à 3 caractéristiques fournissent **63 règles candidates**.
- **Apprentissage** : deux familles à **8 états**, 1 017 cas dont 65 positifs. La règle initiale du seul cycle quotient faisait 165 faux positifs et a fourni un témoin négatif explicite. La recherche de conjonctions a sélectionné `cycle_four_quotient AND odd_signed_cycle`, avec zéro erreur d'apprentissage.
- **Réserve séparée par familles** : deux familles à **9 états**, choisies par empreinte avant lecture de l'oracle, **1 600 cas dont 97 positifs**. Elle est *disjointe par famille*, **pas** un holdout externe et aveugle : les familles et la grammaire ont été conçues par l'expérimentateur.
- **Contrôles contrefactuels** : 32 changements de parité d'une relation (32 changements du verdict exact, zéro divergence) et 32 renommages d'états (zéro divergence). Le changement de parité définit un autre système XOR abstrait, qui ne correspond pas nécessairement à une contrainte issue de l'orbite initiale.

## Mesures sur les 1 600 cas réservés

| Stratégie | TP | FP | FN | TN |
| --- | ---: | ---: | ---: | ---: |
| Référence constante négative | 0 | 0 | 97 | 1503 |
| Cycle quotient, sans parité | 97 | 184 | 0 | 1319 |
| Règle reconstruite automatiquement | **97** | **0** | **0** | **1503** |

La règle reconstruite correspond à une propriété mathématique **déjà connue** dans les briques V19. Les performances ne démontrent donc pas une découverte nouvelle, une capacité de généralisation scientifique hors du domaine XOR fini, une créativité ouverte ou une compréhension sémantique.

## Anti-doublons de connaissances

Lorsque le candidat est **exactement** la signature connue `{cycle_four_quotient, odd_signed_cycle}`, `fast_cycle_queue.py` le classe `KNOWN_RECONSTRUCTION_NOT_A_NEW_RESEARCH_TASK` et l'associe au document historique. Il ne l'enregistre **pas** comme nouvelle hypothèse à exécuter, et ne supprime aucun fichier ni aucun test.

Si une formule différente est sélectionnée, le statut reste `NOT_PROVEN_NEEDS_EXTERNAL_REPLICATION`. L'identité de formule ne prouve ni identité des hypothèses, ni nouveauté réelle ; la revue des sources reste obligatoire.

## Sécurité et reproductibilité

- Source de recherche ancrée sur son Git blob ; empreintes de protocole et d'entrées, journal JSON, absence de mutation de la source.
- La synthèse ne lit la réserve qu'après le choix de la formule ; cela empêche une adaptation directe **dans ce script**, mais ne crée pas à lui seul un véritable holdout externe.
- Toute erreur de source, de contrainte ou d'oracle hors domaine entraîne une erreur explicite.
- Aucun passage automatique au statut de théorème. Ni `main`, ni les automatisations horaires, ni les programmes originaux ne sont modifiés.

Run de référence initial : [#45049682932](https://github.com/Abrasax63/Omega-pub/actions/runs/45049682932) (31 tests logiciels réussis, sans vérification de la déduplication additionnelle). Le run après ajout de la déduplication doit être contrôlé séparément.

## Prochaine vérification réellement nouvelle

Faire soumettre au générateur des structures d'un **autre domaine formel**, une nouvelle grammaire et un holdout préparé indépendamment. Mesurer nouveauté justifiée, résultats exacts, erreurs non détectées, capacité d'identifier les hypothèses manquantes et coût CPU/temps. Pour tester la compréhension de langage et la reformulation libre, il faut ensuite raccorder un modèle local/CPU ou GPU et comparer à budget égal, sans exposer les corrigés à la génération.

**Décision :** conserver comme preuve d'intégration d'un synthétiseur symbolique avec critique et déduplication de résultats connus ; ne pas promouvoir une avancée scientifique ni l'utiliser pour supprimer des artefacts historiques.
