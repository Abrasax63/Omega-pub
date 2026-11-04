# C4, horizon L=2 — coexistence des huit classes et minimum à 9 états

**Type :** fiche de résultat complémentaire, créée le 4 novembre 2026 à partir des rapports archivés.  
**Statut épistémique :** **CALCUL EXACT sous la définition primaire V19** (audit sémantique et recalculs du 4 novembre).  
**Certification RAVI-2 finale :** **À RÉEXAMINER** pour la formalisation supplémentaire et la revue humaine tierce.  
**Originalité bibliographique :** **INDÉTERMINÉE**.

> Cette fiche n'est pas une carte originale retrouvée et n'est pas intégrée au noyau certifié. Le verrou de traduction sémantique entre la note primaire V19 et les scripts est maintenant passé ; la certification RAVI-2 finale reste distincte.

## 1. Énoncé borné

Dans le modèle fini déterministe total encodé ci-dessous, avec un cycle distingué C4, observation binaire, contraintes forcées cohérentes et huit classes cibles C4O-00 à C4O-07, le nombre minimal d'états d'une dynamique qui réalise simultanément les huit classes est exactement **9**.

L'audit du 4 novembre a rapproché cette spécification de la note primaire V19 du 25 septembre : les égalités de trajectoire aux temps 0 et 1, les oppositions forcées et la projection sur C4 concordent. Le minimum de 9 est donc un calcul exact sous cette définition. La preuve indépendante ligne par ligne du lemme de localité L+2 et la formalisation RAVI-2 finale restent à faire.

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

## 7. Statut après audit sémantique du 4 novembre

1. **Convention de trajectoire : PASSÉE.** La note primaire du 25 septembre impose c(T^t x)=c(T^t y) pour 0≤t<L. Pour L=2, cela signifie égalité aux temps 0 et 1. Les états coïncidents ne créent qu'une égalité tautologique.
2. **Contraintes forcées : PASSÉES.** Pour u≠v, l'inégalité est imposée exactement lorsque T(u)=T(v) ou {T(u),T(v)}={u,v}.
3. **Projection et rotations : PASSÉES.** L'ombre est la projection sur les quatre états du cycle ; une rotation agit simultanément sur l'ensemble des masques.
4. **Catalogue local : CALCUL EXACT reproduit.** Une seconde énumération directe, sans DSU, retrouve 1 515 diagrammes, 172 ombres propres et les huit classes attendues. Sa complétude mathématique utilise le lemme de localité L+2.
5. **Coexistence et minimum : CALCUL EXACT sous la définition primaire.** Le témoin global à 9 états et l'absence exhaustive de témoin pour N≤8 ont été recalculés en énumérant les colorations de tous les états ; cette borne inférieure ne dépend pas du lemme de localité.
6. **Dérive documentaire corrigée :** les formulations en inégalité de trajectoire dans CERTIFICAT_CONDITIONNEL_V19_C4_L2_2026-10-28.md et AUDIT_OBS_V19_LOCAL_L2_2026-10-28.md sont obsolètes. Elles sont contredites par la note primaire et les scripts effectivement inspectés/exécutés. Voir le rapport d'audit ci-dessous.

**Verrous restants :** formalisation Lean éventuelle ; revue humaine tierce ; audit bibliographique d'originalité. La preuve du lemme de localité L+2 est reconstruite en §4.1 du rapport d'audit et contrôlée sur 38 systèmes, 536 paires et 173 composantes forcées sans divergence. Aucun de ces compléments ne remet en cause le calcul global de minimalité pour les huit classes cataloguées.

**Verdict à conserver :** **CALCUL EXACT** pour la coexistence des huit classes cataloguées et le minimum de 9 sous la définition primaire V19 ; lemme de localité L+2 **DÉMONTRÉ** sous les hypothèses primaires. La certification formelle et la revue tierce restent des étapes supplémentaires.

## 8. Provenance

Fiche créée le 4 novembre 2026 à partir de rapports et scripts archivés dans la bibliothèque privée. Elle ne constitue ni la restauration d'une carte originale, ni un nouvel audit de calcul.

## 9. Rapport de vérification reproductible — 4 novembre 2026

- [Audit sémantique et reproductibilité C4/L2](../../reviews/AUDIT_SEMANTIQUE_C4_L2_2026-11-04.md)
- [Script indépendant de génération locale et de contrôle direct des colorations](../code/c4_l2_independent_local_audit_2026-11-04.py)

Le rapport documente la correction des formulations archivées en inégalité, les sorties des scripts relancés, les sommes de contrôle et les limites restantes. SQLite v33 n'a pas été modifiée.
