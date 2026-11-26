# V19 — complétions groupées par première observation

18 novembre 2026, 09 h 16 (Paris). Branche `work/omega-math-brick-pilot-2026-11-14`, départ [93eae1f](https://github.com/Abrasax63/Omega-pub/commit/93eae1ffd9e98083cec5b790205dbed32acd2c27). [Dernière expérience](OBS-V19-OUTSIDE-TERMINAL_2026-11-18.md) et [cycle de provenance](https://github.com/Abrasax63/Omega-pub/commit/0996b2e8649d5d7426d71df9e2fb5b62a9a3b464).

L’ombre globale est la projection sur le cycle des colorations qui s’étendent à une solution de toutes les contraintes forcées et événementielles. Sources épinglées : [fiche d’audit](OBS-V19-LPLUS1-AUDIT_2026-11-14.md), [index #2](https://github.com/Abrasax63/Omega-pub/blob/2f71a6b8ed03914c0b5d308520d30e0133d9e9ad/research/bricks/INDEX_BRIQUES.md), [projecteur #5](https://github.com/Abrasax63/Omega-pub/blob/639dc01ca3ea58c61b075adb9a6d860bf41db7bc/research/code/audit_v19_c5_independent_2026-11-04.py) et [convention #18](https://github.com/Abrasax63/Omega-pub/blob/763d77f0aa735d90bb558b2c7fac056298d5313c/02_MATHEMATIQUES/v19_c5/TEST_OPTIMALITE_LOCALITE_L_PLUS_1_2026-11-10.md).

Question : une lecture sortant des deux terminaux fixe-t-elle l’ombre lorsque les autres transitions inconnues varient simultanément ? Témoin négatif : la première lecture en boucle du dossier précédent produit deux ombres. Domaine fixé du balayage discriminant : C3 distingué, deux préfixes disjoints externes au cycle et `(n,L)=(9,2),(10,2),(11,3)`. Les images non fixées par le cycle ou les préfixes balayent tout le support. Référence fixe : observer les deux transitions terminales. Chaque groupe utilise le projecteur qui énumère les colorations complètes. Réfutation si deux fonctions cohérentes dans un même groupe ont des ombres distinctes. Le premier balayage neuf sur 7 et 8 états a donné zéro observation admissible et n’établit aucune uniformité.

| États, horizon | Observations avec multiplicité | Groupes 1 lecture | Groupes 2 lectures | Groupes ambigus, 1 / 2 |
| --- | ---: | ---: | ---: | ---: |
| 9, 2 | 116 | 14 | 116 | 0 / 0 |
| 10, 2 | 1 302 | 16 | 150 | 0 / 0 |
| 11, 3 | 184 | 18 | 184 | 0 / 0 |

**EXÉCUTÉ — calcul exact borné. Conjecture générale INDÉTERMINÉE.** Le témoin négatif donne l’ombre vide et l’ombre complète de taille 8. Le calcul groupé a pris 0,503 s. L’égalité des verdicts après une et deux lectures vaut sur ce domaine fini. Le calcul hors ligne ne mesure pas le coût réel d’acquisition. Aucun changement du vérificateur. Le garde existant est rejoué : 0 erreur contre le projecteur exhaustif sur les deux projections du témoin à cinq états et les 4 536 projections de la famille C5 distincte. Le test de lecture unique passe également. Originalité bibliographique non évaluée.

Depuis `research/code` : `python audit_v19_grouped_first_read.py`, `python audit_v19_shadow_guard.py` et `python audit_v19_single_read.py`. SHA-256 du nouveau harnais `f2e27ffa3ac80f76881c89b63def5688e3549329d1d499a9af81e9967b0f2b6f`.

Prochain test mathématique : fixer un C4 et deux chemins dont les préfixes se croisent avec un décalage de temps, puis vérifier que le filtre des deux terminaux distincts inconnus admet au moins un groupe avant de lancer le calcul groupé. Prochain cycle alterné : provenance.
