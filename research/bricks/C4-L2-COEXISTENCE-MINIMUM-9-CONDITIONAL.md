# C4, horizon L=2 — coexistence des huit classes et minimum conditionnel à 9 états

**Type :** fiche de résultat complémentaire, créée le 4 novembre 2026 à partir des rapports archivés.  
**Statut épistémique :** **CALCUL EXACT sous spécification opérationnelle**.  
**Statut mathématique inconditionnel :** **À RÉEXAMINER**.  
**Originalité bibliographique :** **INDÉTERMINÉE**.

> Cette fiche n'est pas une carte originale retrouvée et n'est pas intégrée au noyau certifié. Elle consigne un résultat calculatoire conditionnel, sans promotion des statuts V19.

## 1. Énoncé borné

Dans le modèle fini déterministe total encodé ci-dessous, avec un cycle distingué C4, observation binaire, contraintes forcées cohérentes et huit classes cibles C4O-00 à C4O-07, le nombre minimal d'états d'une dynamique qui réalise simultanément les huit classes est exactement **9**.

La conclusion est conditionnelle à l'équivalence entre cette spécification opérationnelle et la définition mathématique primaire de l'ombre V19. Cette équivalence n'est pas encore certifiée.

## 2. Spécification effectivement calculée

- États : X={0,…,N−1}.
- Dynamique : endofonction totale T:X→X.
- Cycle distingué fixé : 0→1→2→3→0.
- Observation : coloration c:X→{0,1}.
- Pour deux états distincts u,v, une opposition de couleur est imposée si T(u)=T(v) ou si {T(u),T(v)}={u,v}. Le second cas inclut deux points fixes distincts et un 2-cycle.
- Cohérence globale : chaque fibre de T a taille au plus 2 et le graphe de toutes les oppositions forcées est biparti.
- Pour une paire (x,y), les trajectoires sont comparées aux temps t=0,1 : lorsque les deux états comparés sont distincts, le mauvais événement impose **l'égalité** de leurs couleurs.
- L'ombre est l'ensemble des motifs binaires projetés sur les quatre états du cycle, obtenu en énumérant toutes les colorations globales admissibles.
- Les ombres sont comparées modulo rotations de C4. Une rotation agit simultanément sur tous les masques d'une ombre ; canoniser chaque masque séparément est incorrect.

Cette fiche ne remplace pas la définition primaire V19 : elle décrit précisément ce que les programmes exécutent.

## 3. Témoin explicite à 9 états

La fonction totale est :

```text
T = (1, 2, 3, 0, 8, 7, 6, 2, 0)
```

Le cycle distingué est 0→1→2→3→0. Les paires et ombres brutes sur les 16 colorations de C4 sont :

| Classe | Paire | Ombre brute |
|---|---:|---|
| C4O-00 | (0,1) | {0,7,8,15} |
| C4O-01 | (0,2) | {0,5,10,15} |
| C4O-02 | (1,8) | {2,7,8,13} |
| C4O-03 | (0,7) | {1,6,9,14} |
| C4O-04 | (0,6) | {0,3,4,7,8,11,12,15} |
| C4O-05 | (4,5) | {0,1,4,5,10,11,14,15} |
| C4O-06 | (1,4) | {4,5,6,7,8,9,10,11} |
| C4O-07 | (0,4) | {2,3,6,7,8,9,12,13} |

Les seules oppositions forcées globales de ce témoin sont (1,7) et (3,8). Il possède un point fixe (6), aucun 2-cycle et toutes ses fibres ont une taille au plus 2. Le graphe forcé est biparti.

## 4. Borne inférieure : énumération exhaustive N≤8

Le cycle est fixé dans l'ordre 0,1,2,3. Toutes les images des N−4 états restants sont énumérées, soit N^(N−4) endofonctions par taille. Cette fixation ne perd aucun cas avec cycle distingué : tout cycle orienté de longueur 4 peut être renommé dans cet ordre.

| N | Fonctions totales examinées | Fonctions cohérentes | Les huit classes coexistent |
|---:|---:|---:|---|
| 4 | 1 | 1 | Non |
| 5 | 5 | 5 | Non |
| 6 | 36 | 32 | Non |
| 7 | 343 | 263 | Non |
| 8 | 4 096 | 2 695 | Non |
| **Total** | **4 481** | **2 996** | **Non** |

Chaque fonction cohérente est testée sur toutes ses paires d'états. Aucun témoin des huit classes n'est trouvé pour N≤8. Le témoin à 9 états établit l'existence. Dans la spécification codée, le minimum est donc exactement 9.

## 5. Contrôles indépendants et correction de canonisation

Les rapports du 27–28 octobre enregistrent trois voies concordantes :

1. recherche exhaustive C++ des endofonctions jusqu'à N=8 ;
2. vérificateur Python fondé sur un DSU de parités ;
3. implémentation indépendante sans DSU, énumérant explicitement les colorations binaires des états locaux puis les systèmes globaux de tailles 4 à 8.

Les trois voies retrouvent le témoin à 9 états, les huit ombres et les mêmes comptes d'exhaustivité négative.

Une erreur de canonisation a été identifiée dans une première version : chaque masque avait été canonisé séparément. La correction applique chaque rotation simultanément à l'ensemble complet des masques, puis compare les ensembles tournés. Les comptes restent inchangés après correction.

Le test adversarial qui remplace les égalités de trajectoire par des inégalités ne reproduit qu'une ombre sur huit. La convention d'égalité est donc décisive pour ce certificat.

Ces exécutions sont celles rapportées dans les fichiers archivés ; cette fiche ne prétend pas avoir relancé les scripts le 4 novembre.

## 6. Sources et artefacts retrouvés

- `RAPPORT_C4_L2_MINIMALITE_9_ETATS_2026-10-27.md` — témoin et énumération négative N=4,…,8.
- `RAPPORT_AUDIT_INDEPENDANT_C4_L2_9_ETATS_2026-10-27.md` — troisième vérification directe sans DSU.
- `CERTIFICAT_CONDITIONNEL_V19_C4_L2_2026-10-28.md` — spécification opérationnelle et limites explicites.
- `AUDIT_V19_C4_L2_REPRISE_2026-10-28.md` — correction de canonisation et contre-test égalités/inégalités.
- `RAVI2_C4_L2_GLOBAL_COEXISTENCE_AUDIT_2026-10-27.md` — témoin antérieur à 15 états ; existence globale mais pas minimalité.
- `verify_c4_l2_9state.py` — vérification directe du témoin.
- `certificat_v19_c4_l2_global.py` — certificat d'énumération globale.
- `audit_v19_c4_l2_equalites.py` — audit des égalités de trajectoire et de la canonisation ; SHA-256 rapporté : `94998806131e05c74946f14ea3b4ee5a8e8bc83e0e65bed1a67d2139667ab027`.
- `c4_l2_minimality_search.cpp` — recherche exhaustive des petites tailles.
- `extension_q4_l2.py` — nom d'un générateur local retrouvé, mais le rapport précise qu'il s'agit d'une reconstruction et non d'une récupération certaine du script historique original.

## 7. Limites qui empêchent la certification inconditionnelle

1. La définition primaire complète de l'ombre V19 et son équivalence avec la spécification opérationnelle ci-dessus doivent être vérifiées ligne par ligne.
2. Le sens exact de l'événement, les coïncidences de trajectoires, les oppositions forcées et la projection sur C4 doivent être rapprochés du texte mathématique de référence.
3. La complétude du catalogue initial des huit classes locales doit être distinguée de la preuve conditionnelle de leur coexistence/minimalité.
4. Aucun développement Lean n'est rapporté comme compilé ; aucune validation humaine tierce ni priorité bibliographique n'est revendiquée.

**Verdict à conserver :** minimum 9 = **CALCUL EXACT CONDITIONNEL** dans la spécification opérationnelle ; théorème V19 inconditionnel = **À RÉEXAMINER**. Ne pas inscrire dans le noyau certifié avant fermeture de ces verrous.

## 8. Provenance

Fiche créée le 4 novembre 2026 à partir de rapports et scripts archivés dans la bibliothèque privée. Elle ne constitue ni la restauration d'une carte originale, ni un nouvel audit de calcul.