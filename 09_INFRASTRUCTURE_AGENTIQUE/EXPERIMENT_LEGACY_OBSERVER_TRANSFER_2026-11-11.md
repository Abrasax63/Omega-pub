# Omega — audit rétrospectif, prototype de transfert et contrôle indépendant

Date : 2026-11-11. Statut : **EXPÉRIMENTAL / CALCUL EXACT FINI**, aucune promotion CORE.

## Décision

Prioriser la récupération des principes d'observation et de reconfiguration des représentations, **pas** l'incorporation du solveur géodésique en bloc. Le module joint fournit deux garde-fous **purs, sans effet de bord** : `terminal_probe_guard` et `reconfiguration_gate`. Ils ne sont pas branchés sur la décision réelle d'Omega, ni sur RCE / SQLite. Il serait prématuré de revendiquer un gain d'exactitude en résolution générale.

## Sources réexaminées

1. **Janvier 2026, conversations :** `GeoCertPro` (L-BFGS-B, lagrangien augmenté, Uzawa, raffinement adaptatif), `GeoCertLatent`, `GeoCertLatentAdaptive` / `GeoCertLiving` / `TopoOmegaLiving`. Code complet décrit dans les échanges, mais aucun fichier exécutable de ces variantes n'a été identifié dans les supports consultés. **Réutilisation de ces solveurs non vérifiée**. Attention : `TopoOmegaAdaptive` n'est pas une identité de fichier vérifiée.
2. **Omega/Omega historique, 21 juillet 2026 :** `omega_observer_structure_learning.py` (code récupéré : fonctions de partitions, split/merge, sélection locale, invariance par recodage, simulation finie à six histoires). L'existence du code est vérifiée, non sa transférabilité directe à l'API du planificateur actuel.
3. **Ω-W04, 10 août 2026 :** `OMEGA_W04_dynamic_observer_research.md`. Partition de représentation, famille de sondes, fonction de raffinement `F(P)=P∧Q_(S(P))`, points fixes sous-informatifs. Le théorème d'absence de cycles de longueur >1 sous pur raffinement est élémentaire et cohérent.
4. **Ω-W05/I9, 11 août 2026 :** quotient par une *famille* de tests et résolution par *une politique réalisable* sont distincts. Particulièrement utile pour éviter de surévaluer un planificateur ; l'adaptation conditionnelle à deux contrôles est déjà étudiée dans PR #28 et dans un audit de la bibliothèque daté du 11 novembre.
5. **Ω-W06/I1–I5, 12 août 2026 :** reconfiguration non monotone sous capacité, réduction aux Metrical Task Systems, test de récupération d'une information oubliée, limites des compressions dites universelles. Plusieurs idées sont connues de l'état de l'art et ne doivent pas être vendues comme nouvelles.
6. **Omega actuel :** PR #28 (comparaison synthétique à budget égal), PR #29 (pilotage de consultations sur 12 PR réelles), PR #30 (falsification construite de la provenance, 8 erreurs confiantes). Les PR sont expérimentales et ne constituent pas une validation générale.

Ce périmètre explore des archives ciblées et les rapports d'inventaire existants : **ce n'est pas une relecture exhaustive de tous les anciens échanges et fichiers**.

## Audit Ω-W04 : divergence quantitative reproduite

Énoncé historique : pour X à trois états, 5 partitions, 2 sondes déterministes représentées par des partitions (25 couples), 32 politiques qui choisissent 1 des 2 sondes par partition, 5 partitions initiales : 25 × 32 × 5 = **4 000** trajectoires. Raffinement itéré jusqu'au premier point fixe.

Définition testée d'un arrêt sous-informatif : la partition finale P n'est pas au moins aussi fine que le raffinement commun des deux sondes, i.e. `P` ne raffine pas `Q0∧Q1`.

Résultats **calculés dans ce protocole** :

| Mesure | Archive | Reconstruction 1 (étiquettes de blocs) | Reconstruction 2 (relations d'équivalence) |
|---|---:|---:|---:|
| Trajectoires | 4 000 | 4 000 | 4 000 |
| Cycles non triviaux | 0 | 0 | 0 |
| Arrêts sous-informatifs | 656 | **848** | **848** |

L'écart 656 / 848 n'a pas été résolu. Il peut venir d'un calcul ancien erroné **ou d'une convention non explicitée**. **Ne pas promener le chiffre 656 en CORE ; demander une vérification contradictoire du protocole original.** Les deux implémentations indépendantes dans le test produisent 848. Le chiffre 848 décrit des **trajectoires avec multiplicité**, pas des classes d'isomorphisme.

Certificat témoin : sondes `Q0=(0,0,0)` et `Q1=(0,0,1)`, départ P=(0,0,0), politique constante choisissant Q0 ; premier point fixe P sous-informatif, Q1 le raffine.

### Garde-fou de terminaison

Sous les hypothèses strictes de sondes **toutes connues, exactes, authentiques**, `terminal_probe_guard(P,Qselect,[Q0,Q1])` :
- n'annonce pas de fermeture générale ;
- identifie les 848 arrêts sous-informatifs ;
- pour ces 848 cas, une consultation supplémentaire de l'autre sonde donne la fermeture complète relative aux deux sondes.

**Contrôle négatif de causalité :** une baseline qui consulte toujours les deux sondes (coût de deux consultations) obtient une fermeture complète dans les 4 000 cas. L'écart favorable au garde-fou face à une politique qui s'arrête prématurément n'est **pas** une preuve de supériorité sur une baseline optimalement informée à budget égal.

### Écart avec la PR #30

Le nouveau garde-fou vérifie un défaut d'exploration **conditionnel aux sondes fournies**. Il ne vérifie pas leur provenance. Le cas de falsification des observations étudié par la PR #30 subsiste ; il faut un canal de corroboration distinct, avec authenticité établie et coût contrôlé.

## Audit Ω-W06 : reconfiguration de tâche

X = {0,1,2,3}; G1 = {0,1}|{2,3}; G2 = {0,2}|{1,3}; capacité C=2 blocs. Chacune requiert seulement 2 blocs, mais leur raffinement commun en demande **4**. Ainsi la représentation courante G1 ne peut rejoindre une représentation suffisante pour G2 **par raffinement seulement** sous C=2. Une substitution de représentation G1→G2 est structurellement possible, mais elle fait perdre des distinctions utiles à la tâche initiale. La mémoire scientifique durable ne doit pas être modifiée par ce mécanisme.

Sur les **49 couples ordonnés** des 7 partitions à deux blocs de X, 7 conservent la même partition (KEEP) et 42 exigent REPLACE si le budget reste 2. Résultat exact sur ce micro-modèle, qui ne mesure ni erreurs de LLM ni coût de reconstruction réelle.

Le module `reconfiguration_gate` détecte ce verrou sous hypothèses déclarées. Il ne décide pas comment choisir une nouvelle représentation à partir de données inconnues et ne remplace pas le planificateur d'Omega.

## Test, reproductibilité et provenance

- `python -m unittest -v test_legacy_observer_transfer.py` : **4 tests OK** dans cet environnement.
- `python legacy_observer_transfer.py --output audit_legacy_observer_transfer_2026-11-11.json` : produit les comptes et un témoin minimal.
- Tests : deux codages indépendants de la boucle de raffinement W04, vérification W06 exhaustive, contrôle négatif des sondes identiques, invariance par permutation.
- Exécution locale CPU standard, pas de modèle, pas de retrieval de sources réelles ni évaluation humaine aveugle.

## Intégration prudente proposée pour Omega

1. Conserver ces fonctions sous `09_INFRASTRUCTURE_AGENTIQUE/prism/` comme **candidates expérimentales**. Ne pas les invoquer par défaut.
2. Avant toute fin de mission, **seulement si** un ensemble complet de sondes fiables est explicitement fourni, signaler une éventuelle distinction encore testable. L'absence de distinction n'est qu'une fermeture relative.
3. En présence d'un changement de problème, signaler `replace` quand les distinctions requises par la nouvelle tâche sont incompatibles avec un raffinement monotone sous capacité. Ne jamais supprimer les pièces de provenance dans la mémoire scientifique.
4. Définir ensuite un vrai benchmark de problèmes nouveaux, avec baseline adaptative ayant les mêmes options, budget, sources et arrêt ; juges indépendants aveugles, coûts réels, contrôles négatifs, changements de tâche imprévus. Séparer échecs de provenance et échecs de stratégie.
5. Ne promouvoir ni W04 (avant résolution 656/848), ni un gain d'Omega (absent à ce stade) en CORE. Soumettre toutes conclusions à RAVI-2.

## Verdict et limite

**Contribution vérifiée aujourd'hui :** deux gardes explicables et leur suite de régression, plus une anomalie du résultat historique répliquée par deux implémentations. **Non démontré :** amélioration de la qualité des réponses d'Omega, généralisation hors modèles finis, originalité scientifique, authenticité des preuves, reconfiguration autonome à partir de données inconnues.