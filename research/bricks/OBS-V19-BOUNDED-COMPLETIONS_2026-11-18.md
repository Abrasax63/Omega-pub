# V19 — complétions exhaustives à espace d’états fixé

18 novembre 2026, 03 h 26 (Paris). Branche `work/omega-math-brick-pilot-2026-11-14`, base `4cd7af516c1bda7c6d955fd7764c8dcdf4e8f1a0`. [Cycle précédent](OBS-V19-ONE-READ-COMPLETIONS_2026-11-18.md), [sources et définition globale](OBS-V19-LPLUS1-AUDIT_2026-11-14.md). [Dernier cycle de provenance](https://github.com/Abrasax63/Omega-pub/commit/3326cf5564ac11564ff9f2b63dd47ce2eef7c8).

Question : une première lecture donnant une boucle au terminal suffit-elle à déterminer l’ombre ? On fixe le cycle, les deux préfixes au temps L=2, la première lecture et l’espace d’états étiqueté. On énumère toutes les endofonctions compatibles avec ces données et avec la cohérence des contraintes forcées. L’oracle exhaustif projette les colorations globales. Deux ombres différentes réfutent la suffisance de cette information. Le budget comparé est une transition observée, avec deux transitions comme référence d’acquisition. Le calcul hors ligne ne représente pas le coût d’une politique en production.

Premier lot fixé avant exécution : ancien témoin C4 sur dix états et contrôle C3 sur neuf états, deux choix du terminal lu. Puis extension fixée avant son exécution : même observation C3 sur dix états, avec le sommet 9 entièrement non observé. Ce troisième cas libère l’image de 9 ainsi que l’image terminale restante, ce qui vérifie une situation que le premier lot ne couvrait pas.

| Observation | Complétions brutes par côté | Cohérentes par côté | Tailles distinctes des ombres |
| --- | ---: | ---: | --- |
| C4, dix états | 10 | 9 | 0 et 16 |
| C3, neuf états | 9 | 8 | 0 et 8 |
| C3, dix états | 100 | 74 | 0 et 8 |

**RÉFUTÉ pour les observations testées.** 238 complétions brutes, 182 cohérentes, en comptant séparément les deux premiers choix. Les six observations partielles laissent chacune une ombre vide et une ombre pleine. Dans le cas étendu, si on lit T(3)=3, les complétions (1,2,0,3,4,3,4,5,6,0) et (1,2,0,3,0,3,4,5,6,1) donnent respectivement zéro et huit colorations sur le cycle. Les deux préfixes communs sont (7,5,3) et (8,6,4). Le harnais imprime aussi les témoins de l’autre côté. C’est un calcul exact fini, sans mesure de gain de lecture ni changement du vérificateur. Originalité bibliographique non évaluée.

Depuis research/code : `python3 audit_v19_bounded_completions.py`, `python3 audit_v19_one_read_completions.py`, `python3 audit_v19_single_read.py`. Les trois passent localement. Calcul final : 0,087 s. SHA-256 du harnais `26a812e96af04613c1c9829eacc8476cf08d0442b88a0809982b024692bdb367`.

Prochain test mathématique : balayer également les premières lectures sans boucle, avec un état non observé, et rechercher une classe d’observations dont toutes les complétions ont la même ombre. Prochain cycle : provenance.
