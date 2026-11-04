# Audit sémantique et reproductibilité — V19, C4, L=2

Date : 4 novembre 2026  
Périmètre : définition de l'ombre, contraintes forcées, catalogue local C4/L2, témoin global et borne inférieure.  
Aucune modification de SQLite v33.

## 1. Verdict synthétique

| Verrou | Verdict |
|---|---|
| Sens des contraintes de trajectoire | **PASSÉ** : égalité de couleur aux temps t=0,1 |
| Contraintes forcées | **PASSÉ** : inégalité si T(u)=T(v) ou {T(u),T(v)}={u,v} |
| Projection et quotient par rotations | **PASSÉ** : projection sur C4 ; rotation simultanée de toute l'ombre |
| Catalogue local C4/L2 | **CALCUL EXACT reproduit** : 1 515 diagrammes, 172 ombres propres, 8 classes |
| Témoin global à 9 états | **CALCUL EXACT reproduit** |
| Non-existence pour N≤8 | **CALCUL EXACT reproduit** : 4 481 fonctions parcourues |
| Certification RAVI-2 finale | **À RÉEXAMINER** pour l'audit indépendant ligne par ligne du lemme de localité et la validation formelle complète |

La divergence de signe repérée dans les archives est une **dérive documentaire** : le texte primaire et les scripts corrigés imposent l'égalité des couleurs sur les trajectoires. Deux documents archivés contiennent encore une formulation erronée en inégalité et doivent être considérés comme supersédés pour ce point.

## 2. Source mathématique primaire

Source : NOTE_RECHERCHE_V19_GRAMMAIRE_ORBITALE(2).md, datée du 25 septembre 2026.

- Section 2 : pour L≥2, une paire distincte {u,v} est forcée si et seulement si T(u)=T(v) ou {T(u),T(v)}={u,v}. En binaire, elle impose c(u)≠c(v).
- Section 4 : le mauvais événement impose les égalités c(T^t x)=c(T^t y) pour 0≤t<L.
- Pour L=2, les seules contraintes de trajectoire sont donc les égalités aux temps t=0 et t=1.
- Si les deux états comparés coïncident, l'égalité est tautologique. Le code peut donc omettre cette contrainte sans changer l'ensemble des colorations admissibles.
- L'ombre est la projection des colorations globalement admissibles sur les quatre sommets du cycle distingué.
- Le quotient par rotations agit simultanément sur tous les masques d'une ombre ; il ne faut pas canoniser chaque masque indépendamment.

## 3. Concordance texte–code

La vérification a été faite sur le contenu des scripts, pas seulement sur leurs noms.

1. certificat_v19_c4_l2_global.py : pour chaque paire de trajectoires, il rejette les colorations qui violent l'égalité aux temps 0 et 1. Il énumère les colorations des N états entiers.
2. audit_v19_c4_l2_equalites.py : impose explicitement l'égalité des couleurs aux deux temps ; le paramètre de contre-test bascule vers l'inégalité.
3. verify_c4_l2_9state.py : utilise une union-find de parités avec parité 0 pour les égalités de trajectoire et parité 1 pour les contraintes forcées.
4. audit_brut_independant.py : énumère directement les colorations locales, sans DSU, avec égalités de trajectoire.

La cohérence globale est testée par le graphe de toutes les contraintes forcées : il doit être biparti. La borne de fibre ≤2 est aussi vérifiée explicitement ; elle découle déjà de la bipartition, puisqu'une fibre de taille 3 donnerait un triangle de contraintes d'inégalité.

### Dérive documentaire détectée

- CERTIFICAT_CONDITIONNEL_V19_C4_L2_2026-10-28.md contient dans sa description opérationnelle une inégalité de trajectoire (≠), contrairement à la note primaire.
- AUDIT_OBS_V19_LOCAL_L2_2026-10-28.md affirme que le script global impose des inégalités de trajectoire. L'inspection du script archivé montre le contraire : il rejette les colorations où les deux couleurs diffèrent, donc il impose l'égalité.
- AUDIT_V19_C4_L2_REPRISE_2026-10-28.md et RAPPORT_C4_L2_MINIMALITE_9_ETATS_2026-10-27.md donnent la convention correcte : égalités de trajectoire.

**Décision :** pour V19/C4/L2, la note primaire du 25 septembre prévaut. Les deux formulations en inégalité ci-dessus sont obsolètes et ne doivent plus être utilisées comme définition.

Contre-test : sur le témoin à 9 états, remplacer les égalités de trajectoire par des inégalités ne conserve que **1 ombre brute sur 8** (C4O-04) ; les sept autres changent. La variante inégalité est donc réfutée comme traduction du catalogue visé.

## 4. Reproduction du catalogue local

Le générateur historique extension_q4_l2(3).py a été inspecté et exécuté dans cette session. Sortie C4/L2 :

- 1 515 diagrammes ;
- 172 diagrammes à ombre propre ;
- 8 classes modulo rotations ;
- 4 classes de taille 4 et 4 de taille 8.

Un second générateur a été écrit indépendamment, avec étiquetage canonique des états anonymes par ordre de première apparition et énumération directe des colorations binaires locales, sans DSU. Il donne les mêmes comptes et les mêmes huit représentants canoniques, avec les mêmes multiplicités de diagrammes :

| Représentant canonique | Taille | Diagrammes |
|---|---:|---:|
| (0,1,14,15) | 4 | 16 |
| (0,5,10,15) | 4 | 8 |
| (1,4,11,14) | 4 | 8 |
| (1,6,9,14) | 4 | 16 |
| (0,1,2,3,12,13,14,15) | 8 | 40 |
| (0,1,4,5,10,11,14,15) | 8 | 4 |
| (1,2,5,6,9,10,13,14) | 8 | 64 |
| (1,3,4,6,9,11,12,14) | 8 | 16 |

L'énumération canonique couvre les identifications possibles des deux préfixes : chaque occurrence suivante d'un état déjà rencontré est déterminée par la fonction partielle ; sinon son image est soit un état déjà nommé, soit un nouvel état anonyme portant le prochain label. Cela énumère les diagrammes de préfixes jusqu'au temps L+2, à renommage près.

La complétude mathématique du passage de la dynamique totale à ces préfixes dépend du lemme de localité L+2 de la note primaire. Le présent rapport reproduit le calcul de préfixes ; il ne remplace pas une preuve indépendante complète de ce lemme.

## 5. Témoin global à 9 états

La fonction totale est :

T=(1,2,3,0,8,7,6,2,0), avec cycle 0→1→2→3→0.

Les paires qui réalisent les huit classes sont :

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

Les seules contraintes forcées globales sont (1,7) et (3,8). Toutes les fibres ont taille ≤2 et le graphe forcé est biparti.

## 6. Borne inférieure exhaustive

Le cycle distingué est fixé à 0→1→2→3→0. Tout système avec un cycle distingué de longueur 4 peut être renommé ainsi. Pour N états, les N−4 images restantes ont N choix chacune : toutes les N^(N−4) fonctions sont donc parcourues.

Deux scripts globaux ont été exécutés à nouveau dans cette session. Ils énumèrent toutes les colorations des états globaux et ne dépendent pas du lemme de localité L+2.

| N | Fonctions totales | Fonctions cohérentes | Huit classes réunies |
|---:|---:|---:|---|
| 4 | 1 | 1 | Non |
| 5 | 5 | 5 | Non |
| 6 | 36 | 32 | Non |
| 7 | 343 | 263 | Non |
| 8 | 4 096 | 2 695 | Non |
| **Total** | **4 481** | **2 996** | **Non** |

La recherche est exhaustive pour N≤8. Le témoin à 9 états fournit la borne supérieure. Le minimum pour réaliser simultanément ces huit classes est donc **9 états**, sous la définition primaire V19 et la liste de classes reproduite à la section 4.

## 7. Contrôles exécutés le 4 novembre

- certificat_v19_c4_l2_global.py : témoin PASS ; énumération N=4,…,8 PASS.
- audit_v19_c4_l2_equalites.py : 8/8 ombres exactes sous égalités ; contre-test inégalités 1/8 ; énumération N=4,…,8 PASS.
- verify_c4_l2_9state.py : témoin PASS.
- extension_q4_l2(3).py : catalogue C5/L3 et C4/L2 reproduit.
- c4_l2_independent_local_audit_2026-11-04.py : catalogue indépendant PASS ; concordance local/global sur les 36 paires du témoin PASS ; énumération locale N=4,…,8 PASS.
- L'ancien audit_brut_independant.py a été relancé mais l'exécution de cette session a dépassé le temps disponible après les lignes N=4,…,7. Son rapport historique du 27 octobre annonce une exécution complète ; cette exécution historique n'est pas comptée comme une nouvelle reproduction du 4 novembre.

Sommes de contrôle SHA-256 :

- certificat_v19_c4_l2_global.py : 72b3f1aa6882af44ea4a8d4cb537a85269a668eaef3c80cf0d86f20b2e207529
- audit_v19_c4_l2_equalites.py : 94998806131e05c74946f14ea3b4ee5a8e8bc83e0e65bed1a67d2139667ab027
- verify_c4_l2_9state.py : 393de64e64705b4f3ccca222434afb9e5fe72707165739ead5120bd65e5f2c14
- extension_q4_l2(3).py : a8347f6f63a84d83e04e3f1190f2a023739662c41d4aad9019d6b6322f247434
- c4_l2_independent_local_audit_2026-11-04.py : 018775cca545537563ede7eb23390456d5603b8658733baefeb19de8b6e8f9f1

## 8. Conclusion RAVI-2 et verrous restants

1. **Convention d'égalité : PASSÉE.** Le texte primaire et les implémentations correctes concordent. Les formulations en inégalité des deux documents listés en section 3 sont des erreurs documentaires.
2. **Catalogue C4/L2 : CALCUL EXACT reproduit.** Les huit classes et les comptes du générateur ont été retrouvés par une seconde énumération.
3. **Coexistence/minimum : CALCUL EXACT sous la définition primaire.** Le témoin et l'absence exhaustive pour N≤8 ont été recalculés par énumération globale.
4. **Lemme de localité L+2 :** la source primaire le déclare démontré ; l'audit indépendant ligne par ligne de sa preuve reste à faire. Le certificat global de minimalité, lui, n'utilise pas ce lemme pour calculer les ombres ou la borne inférieure ; le lemme intervient dans la justification de l'exhaustivité du catalogue local.
5. **Formalisation Lean, revue humaine tierce et originalité bibliographique :** non réalisées.

**Verdict conservé :** CALCUL EXACT pour la coexistence des huit classes cataloguées et le minimum de 9 sous la définition primaire V19 ; À RÉEXAMINER uniquement pour la certification RAVI-2 finale de l'exhaustivité du catalogue et de la preuve de localité. Aucun statut SQLite n'est modifié.
