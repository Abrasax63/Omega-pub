# OMEGA-LEGACY-GATE-001 — résultats et contre-contrôles du transfert des observateurs historiques

**11 novembre 2026. Statuts : CALCUL EXACT (modèles finis), RÉFUTÉ (avantage systématique non conditionné aux coûts), INDÉTERMINÉ (valeur sur tâches naturelles).**

## 1. Provenance et périmètre

Les fonctions historiques `legacy_observer_transfer.py` (Git blob `f1fd030015d43b033ad3ec9883aeae7c2b903e32`) et leurs tests ont été copiés **sans changement algorithmique** depuis `experiment/legacy-observer-transfer-2026-11-11`. Le protocole de transfert opt-in est gelé au commit `e08a54fb0d69a971d05d84eba11f43c6555d6305`, antérieur à l'implémentation des deux expériences.

L'interface `planner.plan_mission` accepte **facultativement** `observer_audit`. Absente : sortie strictement inchangée. Présente : dictionnaire `read_only_advisory_opt_in`, sans modification de `next_action`, des rôles, des tâches, de la mémoire durable ou du statut de validation. Cette intégration **ne réintègre pas tout le solveur Ω-O4.2**, ni les solveurs géodésiques anciens `GeoCertPro`/ `GeoCertLatent` ; elle réutilise uniquement deux garde-fous de la branche historique.

## 2. T1 — ferme-t-on trop tôt ?

Modèle : toutes les 125 configurations ordonnées `(partition initiale P, sonde a, sonde b)` sur les cinq partitions de trois états. Les deux modèles exacts de sondes sont supposés fournis au même titre à tous les bras. Après une consultation initiale de `a`, comparer une politique naïve d'arrêt, une politique qui utilise le garde-fou puis consulte `b` si nécessaire et une politique qui consulte systématiquement les deux sondes.

| Bras | Fermetures exactes relativement aux deux sondes | Consultations tarifées |
|---|---:|---:|
| arrêt après `a` | 94/125 | 125 |
| garde-fou puis `b` si utile | **125/125** | **156** |
| `a` et `b` systématiques | **125/125** | 250 |

31 instances exigent la seconde sonde après `a`. Un vérificateur **indépendant**, basé sur les relations d'équivalence et l'intersection de ces relations (sans importer l'algorithme de raffinement historique), retrouve exactement les mêmes nombres.

### Coût réel du garde-fou : seuil à ne pas dissimuler

Si une consultation vaut `c` et calculer le garde-fou une fois vaut `g`, le coût total sur les 125 cas est :

- politique `guarded` : `156c + 125g` ;
- politique `fixed_both` : `250c`.

Par conséquent, **le garde-fou est moins cher si et seulement si `g/c < 94/125`** ; égalité au seuil, désavantage au-delà. La fonction `legacy_guard_cost_sensitivity.py` utilise exclusivement des fractions exactes et vérifie les cas frontières, sans inventer une valeur de `g`.

**Limite décisive** : les politiques ont accès gratuitement à la *description exacte* des modèles de sondes, et le temps de calcul de ce diagnostic n'a PAS été mesuré. Le gain en appels tarifés n'est pas une démonstration d'un gain de temps, de coût total ni de capacité face à une stratégie conditionnelle forte exploitant la même liste.

## 3. T2 — représentation de travail sous capacité finie

Sur les 7 partitions à deux blocs de 4 états, soit **49 transitions** ordonnées sous capacité 2 :

- **7** décisions `keep` ;
- **42** décisions `replace` ;
- **0** décisions `refine` ou `infeasible`.

Une stratégie basique `if current == target: keep else: replace` renvoie **exactement les 49 mêmes décisions** et effectue les mêmes 42 changements. Une stratégie qui remplace systématiquement la représentation de travail par la cible réalise aussi les 49 objectifs finaux mais effectue 49 changements. **Aucun avantage propre au mécanisme historique face au test d'identité simple** dans ce secteur.

Pour éprouver la généralité interne de la classification sans modifier T2, un stress test **ajouté après l'intégration** parcourt les **900 configurations** `15 × 15 × 4` (toutes les partitions de 4 états, chacune des capacités 1,2,3,4). Le second calcul utilise **un autre encodage par relations d'équivalence et union-find**, non l'algorithme historique. Les 900 décisions et les nombres de blocs concordent.

| Capacité | Keep | Refine | Replace | Infeasible | Total |
|---|---:|---:|---:|---:|---:|
| 1 | 1 | 0 | 14 | 210 | 225 |
| 2 | 15 | 7 | 98 | 105 | 225 |
| 3 | 45 | 67 | 98 | 15 | 225 |
| 4 | 60 | 165 | 0 | 0 | 225 |

Les actions `replace` et `refine` ne sont que des **recommandations sur une vue de travail**. Elles ne migrent aucun état, n'entraînent aucun modèle et ne suppriment ni une preuve, ni son origine, ni un résultat certifié. Le changement effectif n'est pas mesuré.

## 4. Test adversarial : catalogue incomplet et provenance non authentifiée

Exemple : état courant `[0,0,0]`, sonde déjà essayée `[0,0,0]`, une autre sonde effective `[0,0,1]` **absente** de la liste fournie. Trois contrôles produisent :

- catalogue honnêtement déclaré incomplet : `closure_unknown` ;
- même catalogue mais prétendu exhaustif : `closed_assuming_declared_probe_list` (**hypothèse du fournisseur non vérifiée**, pas certification) ;
- catalogue complété : `underinformative_relative_to_listed_probes`.

Ce contre-exemple montre que **déclarer `declared_exhaustive=true` ne rend pas les sources authentiques ni la liste réellement exhaustive**. Aucun des trois cas ne délivre un certificat scientifique. Les tests rejettent également mauvais types, booléens à la place d'entiers, partitions de longueurs différentes et sondes sélectionnées non présentes dans la liste.

## 5. CI et reproductibilité

Validation de base du raccordement :
- [GitHub Actions #43076872506](https://github.com/Abrasax63/Omega-pub/actions/runs/43076872506) — **SUCCESS**, 199 tests du Prisme, RCE/MCP et cohérence des index.

Tests supplémentaires :
- [GitHub Actions #43077525962](https://github.com/Abrasax63/Omega-pub/actions/runs/43077525962) — **SUCCESS**, 202 tests dont le vérificateur indépendant à 900 cas ;
- [GitHub Actions #43077677141](https://github.com/Abrasax63/Omega-pub/actions/runs/43077677141) — **SUCCESS**, 204 tests du Prisme, dont le prix du garde-fou calculé en fractions exactes.\n- [GitHub Actions #43078453200](https://github.com/Abrasax63/Omega-pub/actions/runs/43078453200) — **SUCCESS, 205 tests du Prisme**, six tests MCP, contrôles RCE/index réussis. Le dernier test ajoute des limites strictes de **64 états / 64 sondes listées** à l'entrée JSON facultative pour prévenir un coût quadratique non borné. Ce bornage est une mesure de sûreté, pas une hypothèse scientifique sur l'exhaustivité des sondes.

Pour reproduire depuis `09_INFRASTRUCTURE_AGENTIQUE/prism` :

```bash
python -m unittest -v test_legacy_observer_transfer test_observer_guard_bridge test_legacy_representation_stress test_legacy_guard_cost_sensitivity
python legacy_guard_benchmark.py
python legacy_representation_stress.py
python legacy_guard_cost_sensitivity.py
```

## 6. Conclusion et prochain verrou

**CALCUL EXACT** : l'intégration optionnelle fonctionne sur les modèles finis déclarés. Les tests de compatibilité et le vérificateur indépendant concordent, mais les preuves de fermeture ne valent **que relativement aux sondes fournies**.

**RÉFUTÉ POUR T2** : un besoin de remplacement n'implique pas une supériorité stratégique du garde-fou : la référence `keep if same else replace` l'égale exactement sur les 49 cas.

**INDÉTERMINÉ** : gain sur des tâches scientifiques ouvertes, authenticité et exhaustivité des sources, coût réel du diagnostic, résistance aux erreurs de sondes, capacité à reconstruire automatiquement une représentation, et éventuel avantage contre un sélecteur adaptatif simple ayant accès aux mêmes informations.

### Suite proposée : une nouvelle question, pas un raffinage cosmétique

Avant toute activation générale ou promotion CORE :
1. Contrôler des **données de sources avec preuves et provenance réellement vérifiables**, et non des seules étiquettes de partition fournies.
2. Comparer des stratégies tenant compte de preuves manquantes, contradictoires ou invalidées, à coûts de validation mesurés et budgets identiques.
3. Distinguer l'observateur scientifique de la mémoire durable : le premier peut suggérer de remplacer une vue de travail ; la seconde doit conserver l'historique, les contre-exemples, les certificats et leurs dépendances.

**Ne pas activer par défaut. Ne pas fusionner sur `main`, ni modifier SQLite/CORE. Conserver cette PR en brouillon.**
