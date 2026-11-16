# Audit vérifié — OMEGA-COVER-REPLICATION-05

Date : **16 novembre 2026**. Expérience sur la **PR #140**, branche `experiment/omega-cover-replication-05-2026-11-16` empilée sur #139.

## Documents de preuve
- Préenregistrement **antérieur à l'implémentation et aux résultats** : [commit `8ba60bd`](https://github.com/Abrasax63/Omega-pub/commit/8ba60bd44553b439d109302f9a6d0a07c99e7188).
- [Run GitHub Actions #43975864458 — SUCCESS](https://github.com/Abrasax63/Omega-pub/actions/runs/43975864458), job **#133679528836** : **10/10 tests** et **384 apprentissages AALpy L***.
- [Artefact brut #14281330711](https://github.com/Abrasax63/Omega-pub/actions/runs/43975864458/artifacts/14281330711) : `report.json` (**13 680 841 octets**), `report.sha256`, `summary.jsonl`. SHA256 du **rapport JSON recalculé indépendamment** depuis le ZIP téléchargé : **`5bb46f7c254cd2d568a87c8ab23318b9829a2561133159ee7423b769eccba300`**, conforme à la CI.
- 48 machines nouvelles **16×4, 16×5, 16×6 états** ; filtrage d'accessibilité/minimalité uniquement, signatures canoniques uniques et disjointes des **1 148 machines des PR précédentes**. Même backend **AALpy 1.6.2**, mêmes 4 méthodes et paramètres qu'en #139, EQ mots **exactement 10 symboles**, 32 EQ maximum par hypothèse, graines identiques par machine/méthode entre plafonds, oracle BFS exact **évaluation seulement**.
- 128 mots réservés par machine, distincts de l'entraînement (identité avec une requête traitée et exclusions reportées dans le JSON). Couts réellement facturés : MQ+EQ. Une acceptation provisoire de L* et une certification exacte par le BFS ne sont jamais confondues.

## Verdict principal préenregistré : NÉGATIF, réplication forte NON DÉMONTRÉE

**`NO_ROBUST_QUERY_GAIN_DEMONSTRATED`** au plafond 500, et aucun des trois tests appariés ne montre de différence significative.

| Méthode | Automates EXACTS / 48 | Mots TEST entiers corrects (moyenne) | Interruptions par budget | Symboles réellement payés |
|---|---:|---:|---:|---:|
| RANDOM_LEN10 | **46** | **97,7376 %** | 27/48 | 21 791 |
| FIXED_LEN10 | 45 | 96,4518 % | 26/48 | 21 785 |
| OLD_OMEGA_LEN10 | 45 | 97,1680 % | 27/48 | 21 837 |
| COVER_DISTINGUISH_LEN10 | **45** | 96,1589 % | 28/48 | 21 803 |

**Le résultat descriptif favorable du pilote #139 (10/12 COVER contre 9/12 des références) n'est PAS reproduit** : avec 48 nouvelles machines, COVER ne bat aucune des trois références et l'exactitude des mots TEST est également plus basse. Les coûts moyens réels sont voisins mais pas identiques : le plafond de 500 est partagé, **pas la dépense réellement égale**.

### Tableau apparié exact — COVER vs référence, plafond 500

| Comparateur | COVER seul exact W | Référence seule exacte L | Écart d'exactitude / 48 | McNemar unilatéral exact | p Holm corrigée | Bootstrap 95 % apparié stratifié |
|---|---:|---:|---:|---:|---:|---|
| RANDOM | **0** | **1** | **−1/48** | 1,0000 | 1,0000 | [−6,25 %, 0,00 %] |
| FIXED | 2 | 2 | 0 | 0,6875 | 1,0000 | [−8,33 %, +8,33 %] |
| OLD_OMEGA | 1 | 1 | 0 | 0,7500 | 1,0000 | [−6,25 %, +6,25 %] |

Calcul exact des p-values : conditionnement sur W+L, `P[Binomial(W+L,0.5) >= W]`. Correction Holm sur les trois tests. Intervalles non paramétriques bootstrap appariés stratifiés **16/16/16 par taille**, **5 000 réplications**, seed **48319** (+0/+1/+2 par comparateur). Les intervalles englobent zéro. **Aucun résultat ne satisfait le critère `REPLICATED_STRONG_QUERY_GAIN`**.

### Détail par taille au plafond 500 — reconstructions EXACTES sur 16

| Méthode | 4 états | 5 états | 6 états |
|---|---:|---:|---:|
| RANDOM | 15 | 15 | **16** |
| FIXED | **16** | 14 | 15 |
| OLD_OMEGA | 15 | 15 | 15 |
| COVER | 15 | 15 | 15 |

## Secondaire, budget 300 — descriptif, non significatif

| Méthode | EXACTS / 48 | Accuracy mots TEST | Interrompus par budget |
|---|---:|---:|---:|
| RANDOM | **38** | 85,7096 % | 48/48 |
| FIXED | 35 | 80,5501 % | 48/48 |
| OLD_OMEGA | 37 | 84,4564 % | 48/48 |
| COVER | **38** | **86,0840 %** | 48/48 |

À 300, COVER fait mieux que FIXED (+3 machines) et OLD_OMEGA (+1), mais **ne dépasse pas RANDOM** (38/48 chacun). Test exact McNemar unilatéral ajusté Holm face à FIXED **0,7617**, face aux deux autres **1,0**; tous intervalles bootstrap incluent zéro. Toutes les méthodes sont **interrompues par budget** sur les 48 machines au plafond 300, même lorsqu'une hypothèse provisoire s'avère exacte après audit indépendant. On ne peut pas appeler ces interruptions des certifications de L*.

Détail taille n=4/5/6 à 300 :
- RANDOM : **15 / 14 / 9**
- FIXED : **15 / 11 / 9**
- OLD_OMEGA : **15 / 13 / 9**
- COVER : **15 / 13 / 10**

## Statuts et interprétation
- **VÉRIFIÉ** : 10 contrôles, 384 exécutions, SHA identique à l'artefact, 48 nouvelles signatures, transitions/sorties cachées à l'apprenant, même L*, vraies sorties et coût par symbole, exactitude indépendante par BFS, calculs appariés statistiquement contrôlés, valeurs négatives conservées.
- **RÉFUTÉ sur ce nouveau holdout** : la réplication du gain brut 500 par rapport aux trois références ; COVER n'est pas meilleur sur la mesure primaire.
- **NON DÉMONTRÉ** : supériorité robuste de COVER sur ces distributions. Les tests ne prouvent pas l'identité des méthodes ni l'impossibilité d'un effet dans d'autres situations.
- **INDÉTERMINÉ** : performance sur systèmes réels / états plus nombreux / alphabets plus complexes ; généralisation hors de la famille du générateur ; intelligence scientifique, autonomie agentique ou modification autonome de l'algorithme.

**Prochaine décision recommandée :** NE PAS ajuster la couverture sur les nouveaux 48 cas ouverts. Conserver les expériences #136–#140 avec leurs statuts, puis analyser les situations où les méthodes divergent avant de formuler un nouveau protocole indépendant. Toute intervention devra être définie avant un nouveau holdout. Aucune fusion ou promotion à CORE ; PR #140 **DRAFT**, `main` inchangée, 0 API payante.
