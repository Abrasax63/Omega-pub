# V19 — première observation sur C4 avec un état libre

18 novembre 2026, 12 h 32 (Paris). Branche `work/omega-math-brick-pilot-2026-11-14`, départ [f54a156](https://github.com/Abrasax63/Omega-pub/commit/f54a1562d924889ef18b63f203450da2fe3c7101). [Dernier cycle mathématique](OBS-V19-DISJOINT-PREFIX_2026-11-18.md) et [dernier cycle de provenance](https://github.com/Abrasax63/Omega-pub/commit/32e2cd9489e7a28ba409efb4fadf25ea6326f6b8).

L’ombre globale projette les colorations qui s’étendent à toutes les contraintes forcées et événementielles. Sources : [fiche d’audit](OBS-V19-LPLUS1-AUDIT_2026-11-14.md), [index historique #2](https://github.com/Abrasax63/Omega-pub/blob/2f71a6b8ed03914c0b5d308520d30e0133d9e9ad/research/bricks/INDEX_BRIQUES.md), [projecteur #5](https://github.com/Abrasax63/Omega-pub/blob/639dc01ca3ea58c61b075adb9a6d860bf41db7bc/research/code/audit_v19_c5_independent_2026-11-04.py), [convention #18](https://github.com/Abrasax63/Omega-pub/blob/763d77f0aa735d90bb558b2c7fac056298d5313c/02_MATHEMATIQUES/v19_c5/TEST_OPTIMALITE_LOCALITE_L_PLUS_1_2026-11-10.md).

Question : à horizon 2, sur C4 avec deux préfixes disjoints, une première lecture hors terminaux détermine-t-elle l’ombre même si la transition d’un sommet hors préfixe varie ? Critère de réfutation : deux complétions cohérentes partageant l’observation mais ayant deux ombres distinctes. Protocole fixé avant exécution : tous les prolongements cohérents du cycle et des chemins sur 10 puis 11 états, soit 100 puis 1 331 affectations à filtrer. Référence fixe : deux lectures terminales. Projecteur exhaustif des colorations, même budget de complétions pour les deux groupements. Contrôle négatif hors domaine : témoin historique à première lecture en boucle.

| États | Observations avec multiplicité | Groupes 1 lecture | Groupes 2 lectures | Groupes ambigus 1 / 2 |
| --- | ---: | ---: | ---: | ---: |
| 10 | 148 | 16 | 148 | 0 / 0 |
| 11 | 1 788 | 18 | 186 | 0 / 0 |

**EXÉCUTÉ — calcul exact fini. Conjecture générale INDÉTERMINÉE.** Le témoin négatif présente deux ombres, vide et complète (8 colorations). Le balayage et la projection prennent 1,124 s. Coût hors ligne du calcul, sans mesure du coût d’observation. Le garde existant donne zéro erreur contre le projecteur exhaustif sur les deux projections du témoin à cinq états et les 4 536 de la famille C5 distincte. Le test de lecture simple passe. Aucun changement du vérificateur. Originalité bibliographique non évaluée.

Depuis `research/code` : `python audit_v19_grouped_c4.py`, `python audit_v19_shadow_guard.py`, `python audit_v19_single_read.py`. SHA-256 du harnais `bd8e7580fb7de0cf709138e2c0e470ad169db45fc7590afbca7cfe67fa731d40`.

Prochain test : fixer C4 à horizon 3 avec deux chemins disjoints et un état libre, puis comparer les groupes à risque selon la nature de la première destination. Prochain cycle alterné : provenance.
