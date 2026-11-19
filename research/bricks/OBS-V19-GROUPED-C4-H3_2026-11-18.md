# V19 — première lecture à horizon 3 sur C4

18 novembre 2026, 17 h 36 (Paris). Branche `work/omega-math-brick-pilot-2026-11-14`, départ [afce4a5](https://github.com/Abrasax63/Omega-pub/commit/afce4a508993c96539fbe49eed6dfe89c174bc92). [Cycle C4 à horizon 2](OBS-V19-GROUPED-C4_2026-11-18.md). [Dernier cycle de provenance](https://github.com/Abrasax63/Omega-pub/commit/2ae9298fb31ec7eb4461df7278eab4c5ad62d9f7).

L’ombre est la projection sur le cycle des colorations qui s’étendent aux contraintes globales. Sources épinglées : [fiche d’audit](OBS-V19-LPLUS1-AUDIT_2026-11-14.md), [index #2](https://github.com/Abrasax63/Omega-pub/blob/2f71a6b8ed03914c0b5d308520d30e0133d9e9ad/research/bricks/INDEX_BRIQUES.md), [projecteur #5](https://github.com/Abrasax63/Omega-pub/blob/639dc01ca3ea58c61b075adb9a6d860bf41db7bc/research/code/audit_v19_c5_independent_2026-11-04.py), [convention #18](https://github.com/Abrasax63/Omega-pub/blob/763d77f0aa735d90bb558b2c7fac056298d5313c/02_MATHEMATIQUES/v19_c5/TEST_OPTIMALITE_LOCALITE_L_PLUS_1_2026-11-10.md).

Question : à horizon 3, une première lecture hors terminaux détermine-t-elle l’ombre sur C4 même si un sommet hors des deux chemins a une transition inconnue ? Critère fixé avant test : deux complétions cohérentes avec la même observation et des ombres distinctes réfutent la conjecture. Deux chemins disjoints fixés. Budget : 144 affectations à 12 états et 2 197 à 13, filtrées par cohérence. Référence : groupement par deux lectures terminales, même oracle exhaustif et même budget de complétions. Témoin négatif : première lecture en boucle dans le C3 historique.

| États | Observations avec multiplicité | Groupes à 1 / 2 lectures | Groupes ambigus à 1 / 2 lectures |
| --- | ---: | ---: | ---: |
| 12 | 224 | 20 / 224 | 0 / 0 |
| 13 | 3 108 | 22 / 270 | 0 / 0 |

Destinations à 13 états : 8 groupes vers le cycle, 12 vers les chemins, 2 vers le sommet libre. Le témoin négatif produit les ombres de taille 0 et 8. Calcul en 7,572 s, coût d’acquisition non mesuré. **EXÉCUTÉ — calcul exact fini. Conjecture générale INDÉTERMINÉE.** Aucun changement de projecteur. Le garde existant concorde avec l’oracle sur 2 projections du témoin à cinq états et 4 536 de la famille C5. Le contrôle de lecture simple passe. Originalité bibliographique non évaluée.

Depuis `research/code` : `python audit_v19_grouped_c4_h3.py`, `python audit_v19_shadow_guard.py`, `python audit_v19_single_read.py`. SHA-256 du harnais `036cbccc821b909137aabcded1243e70e07457d4cc85b69e04baec970dfd3bee`.

Prochain test mathématique : examiner le mécanisme de fixation des deux groupes dont la première destination est libre, avant de passer à deux états hors préfixe. Prochain cycle alterné : provenance.
