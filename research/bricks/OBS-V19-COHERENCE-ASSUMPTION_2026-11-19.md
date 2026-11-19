# V19 — la cohérence distingue ombre vide et ombre complète

19 novembre 2026, 01 h 37 (Paris). Branche `work/omega-math-brick-pilot-2026-11-14`, départ [187cd7e](https://github.com/Abrasax63/Omega-pub/commit/187cd7e23a993fb4e285d2434a3b7d2aed056f95). [Dernier cycle](OBS-V19-TWO-FREE-STATES_2026-11-18.md). [Dernier cycle de provenance](https://github.com/Abrasax63/Omega-pub/commit/e409c1723c17e854692db36ffcf9551a9ac58f95).

L’ombre reste la projection des colorations globalement extensibles. Sources épinglées : [audit](OBS-V19-LPLUS1-AUDIT_2026-11-14.md), [index #2](https://github.com/Abrasax63/Omega-pub/blob/2f71a6b8ed03914c0b5d308520d30e0133d9e9ad/research/bricks/INDEX_BRIQUES.md), [projecteur #5](https://github.com/Abrasax63/Omega-pub/blob/639dc01ca3ea58c61b075adb9a6d860bf41db7bc/research/code/audit_v19_c5_independent_2026-11-04.py), [convention #18](https://github.com/Abrasax63/Omega-pub/blob/763d77f0aa735d90bb558b2c7fac056298d5313c/02_MATHEMATIQUES/v19_c5/TEST_OPTIMALITE_LOCALITE_L_PLUS_1_2026-11-10.md).

Hypothèse falsifiable fixée avant test : supprimer la cohérence présupposée des contraintes forcées permet des ombres différentes au sein d’un même groupe d’observation. C4, horizon 2, chemins (4,5,6) et (7,8,9), états libres 10 et 11. Une première lecture terminale vers 10 est fixée ; les trois images restantes varient sur 12 états. Budget 3 456 affectations pour les deux côtés. Référence : toutes les contraintes globales. Pour les fonctions incohérentes, l’ombre est vide par définition ; pour les autres, le certificat existant doit établir l’ombre complète. Quatre témoins, premier de chaque classe et côté, sont aussi vérifiés par le projecteur exhaustif. Les trois contrôles du certificat sont rejoués avant le balayage.

| Terminal lu | Affectations | Ombre vide | Ombre complète |
| --- | ---: | ---: | ---: |
| 6 vers 10 | 1 728 | 310 | 1 418 |
| 9 vers 10 | 1 728 | 310 | 1 418 |

Exemple au terminal 6 : `T=(1,2,3,0,5,6,10,8,9,0,0,0)` a une ombre vide ; `T=(1,2,3,0,5,6,10,8,9,0,1,2)` a une ombre complète de taille 16. Les chemins observés et la première lecture sont identiques. Les deux transitions terminales sont même identiques dans cette paire : la différence porte sur les deux états libres. La référence fixe à deux lectures ne peut donc distinguer cette paire hors hypothèse de cohérence.

**EXÉCUTÉ — calcul fini exact avec certificat. Uniformité sans cohérence RÉFUTÉE dans cette famille.** Quatre confirmations exhaustives concordent. Temps 0,073 s. Le constat ne réfute pas la conjecture formulée sur les endofonctions cohérentes. Aucun changement de vérificateur, aucun gain de coût nouveau revendiqué. Originalité bibliographique non évaluée. Le garde historique et le projecteur exhaustif concordent sur 2 projections du témoin à cinq états et 4 536 de la famille C5 distincte ; le contrôle de lecture simple passe.

Depuis `research/code` : `python audit_v19_coherence_assumption.py`, `python audit_v19_shadow_guard.py`, `python audit_v19_single_read.py`. SHA-256 du nouveau harnais `4c39ad8c7725173911b242192491df5dee64cc4e70867d100d56a7b704d4a5e7`.

Prochain test mathématique : produire un certificat local de cohérence qui couvre aussi les composantes hors préfixe, puis vérifier s’il exige plus d’information que la première lecture. Comparer ce coût avec la référence complète. Prochain cycle alterné : provenance.
