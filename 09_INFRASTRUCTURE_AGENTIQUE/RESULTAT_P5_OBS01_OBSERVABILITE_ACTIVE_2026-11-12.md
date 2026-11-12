# P5-OBS-01 — observabilité contrôlée et valeur d'acquisition d'une preuve

**12 novembre 2026. Statut : CALCUL EXACT FINI VÉRIFIÉ ; gain contre méthode myope, MAIS PAS de contribution spécifique à Omega démontrée.**

## Provenance

- [Protocole publié AVANT le code et les résultats](EXPERIMENT_P5_OBS01_PREREG_2026-11-12.md) au commit `d8f9966d87356b815cf79ad6a4dba53fd9c01542`.
- [GitHub Actions #43218569217 — SUCCESS](https://github.com/Abrasax63/Omega-pub/actions/runs/43218569217), Python 3.12. **9 tests réussis** ; simulation exhaustive des **16 états cachés × 6 politiques = 96 trajectoires**. Ce sont des trajectoires **synthétiques calculées, pas 96 appels de modèles**.
- [Archive JSON des 96 trajectoires, certificats et comparateurs](https://github.com/Abrasax63/Omega-pub/actions/runs/43218569217/artifacts/13945660048). Les valeurs du DP et de l'énumération indépendante d'arbres coïncident exactement : `19/25`. Zéro API, zéro LLM, aucune donnée privée.
- Sources mathématiques réutilisées **sans nouvelle revendication de priorité** : [DELTA_H_RECOLLEMENT_INTERNE](../02_MATHEMATIQUES/defauts_recollement/sources/DELTA_H_RECOLLEMENT_INTERNE_2026-09-29.md) et [DELTA_H_STRATEGIE_COUVERTURE](../02_MATHEMATIQUES/defauts_recollement/sources/DELTA_H_STRATEGIE_COUVERTURE_2026-09-29.md).

## Raccord exact avec les travaux d'observabilité

Pour une dynamique totale `T:X→X` et une observation fixe `π:X→Y`, notre filtre de recollement est `B_{i+1}=T(B_i)∩π^{-1}(y_{i+1})` : les micro-états encore compatibles avec le **mot observé**. Il est exact, alors que `Q` perd la compatibilité de témoins successifs.

Contre-exemple réutilisé : `X={0,1,2}`, `T=(0,2,2)`, `π=(0,0,1)` : le mot **001** utilise deux transitions permises `00`, `01`, mais les survivants ont les tailles **2→1→0**. `001` est donc irréalisable, même si le défaut d'extrémités `Δ_h` reste vide. Le nouveau script confirme directement `Δ_h=∅` pour **h=1,...,20** ; l'énoncé pour **tous** les h demeure celui de la source mathématique antérieure, il n'est pas prouvé de nouveau par cet audit fini.

**Précaution** : le cadre actif de OBS-01 est un **modèle différent** avec actions de mesure `a`, transitions `T_a=id` et observations dépendant de l'action `π_a(x)`. L'identité des filtres d'états survivants est une **analogie opératoire exacte pour cette extension déterministe**, et non la preuve que les résultats autonomes sur `Δ_h` suffisent à résoudre un POMDP ou tout problème de vérification.

Autre précaution tirée des archives : certains **rangs de coalitions** en cas contrôlé ne sont pas intrinsèques au langage observé et varient entre présentations équivalentes. Une mesure arbitraire de « richesse en états observables » ne doit pas être traitée comme une valeur décisionnelle invariante ; mesurer les observations qui séparent réellement les hypothèses **pertinentes pour l'objectif**.

## Monde synthétique et politiques

16 états équiprobables `(u,v,z)` où `u,v` sont deux bits et `z∈{0,1,2,3}` un facteur de nuisance. La réponse finale est `y=u XOR v`. Les sondes `U` et `V` coûtent `0,12` et `Z` coûte `0,05`. Budget deux sondes. Gain +1 si réponse correcte, −2 si fausse, +0,05 pour abstention. Les contrôleurs voient uniquement les résultats de leurs propres sondes, jamais le secret. Chaque trajectoire conserve le cardinal des survivants après chaque observation.

## Calcul exact — toutes les valeurs étaient prédites dans le protocole

| Politique | Gain net moyen exact | Sondes utilisées |
|---|---:|---|
| Abstention sans vérification | `1/20` = **+0,05** | aucune |
| Valeur d'information immédiate myope | `1/20` = **+0,05** | aucune |
| Entropie du micro-état gloutonne | `−3/25` = **−0,12** | Z puis U |
| Contrôle fixe, connaissant les sondes utiles | `19/25` = **+0,76** | U puis V |
| **DP bayésien exact** (témoin fort) | `19/25` = **+0,76** | U puis V |
| **Omega observabilité candidat** | `19/25` = **+0,76** | U puis V |

**Pourquoi les politiques diffèrent :**

- Avant observation : `P(y=0)=P(y=1)=1/2`. Répondre directement vaut `0.5×1+0.5×(−2)=−0.5`. Il vaut mieux s'abstenir pour `+0,05`.
- Après une sonde U **seule**, les deux valeurs de y restent également possibles. La valeur de la décision finale demeure `+0,05` ; la **VOI immédiate est négative après coût**. Idem V.
- Après U **puis V**, l'étiquette est déterminée, quel que soit z. La décision correcte rapporte 1 moins `0,12+0,12` = **`0,76`**. C'est une complémentarité informationnelle non prise en compte par une optimisation à horizon un.
- La sonde Z a 4 issues possibles : elle révèle **2 bits sur l'état microscopique** contre 1 pour U ou V ; mais elle ne réduit pas l'incertitude sur **y**. Un algorithme d'entropie générique choisit Z puis U (budget épuisé), et termine à `0,05−0,05−0,12=−0,12`.
- La programmation dynamique bayésienne **standard** utilise les mêmes états/sondes et trouve exactement le même résultat qu'Omega. Le **contrôle fixe U puis V** l'égale aussi. Aucune originalité stratégique propre à Omega n'est donc établie.

Deux chemins indépendants validés par le workflow : (A) programmation dynamique sur ensembles de survivants, (B) énumération exhaustive de tous les choix possibles au premier niveau et de leurs choix conditionnels au second niveau. Les deux donnent **`19/25`** sans arrondi.

## Tests adversariaux et statut

- Invariant `001` : arêtes localement possibles, aucun micro-témoin global ;
- observations incompatibles : un ensemble survivant vide génère une erreur, aucune décision forcée ;
- budget **une seule sonde** : aucune ne permet de diagnostiquer y ; la meilleure politique s'abstient ;
- état initial entièrement connu : contrôleur exact n'achète **aucune** vérification inutile ;
- sondes payées : deux au maximum, sans répétition ; journal des résultats effectivement observés ;
- conformité avec `planner.plan_mission` du vrai P1 uniquement pour expliquer la nécessité de vérifier, **sans proclamer que P1 apprend ou planifie automatiquement ces sondes**.

**VERDICT CALCUL EXACT :** l'observabilité est pertinente pour **certifier les hypothèses compatibles** et pour identifier des vérifications **complémentaires** ayant une valeur future. **PAS DE SUPÉRIORITÉ OMEGA :** égalité complète avec le DP bayésien classique et une stratégie fixe informée. Les données ne testent **ni les véritables erreurs de modèles, ni des vérificateurs imparfaits, ni une mémoire scientifique active**.

## Suite justifiée, sans résultats inventés

Avant une nouvelle campagne avec Qwen, étendre l'interface expérimentale à :
- un ensemble de **mécanismes d'erreur candidats** (plutôt qu'un seul score de risque) et des sondes correspondant à des vérifications indépendantes ;
- une mise à jour de croyance sous **résultats potentiellement erronés ou incomplets**, avec vraisemblances explicites, et surtout une option « information non suffisante » ;
- une comparaison à un **POMDP/DP bayésien classique** avec coût de calcul comparable, à des bandits avec observation payante, et à une stratégie sans filtre d'observabilité ;
- des questions nouvelles et un critère de réussite pré-enregistré basé sur la **décision terminale et les erreurs évitées**, et non sur la seule réduction d'entropie ;
- un garde-fou de réalisabilité des chemins, qui rejette les conclusions fondées sur des raccordements impossibles entre témoins.

### Sources externes

- Kuize Zhang (2023), [*A survey on observability of Boolean control networks*](https://link.springer.com/article/10.1007/s11768-022-00122-x), sur les notions de distinction d'états sous entrées et sorties.
- De Santis & Di Benedetto (2017), [*Observability and diagnosability of finite state systems*](https://doi.org/10.1016/j.automatica.2017.02.042), sur l'observabilité et le diagnostic de défauts.
- [*From Reactive to Active Sensing*](https://doi.org/10.1145/3583068), synthèse sur les politiques de mesure au sein de problèmes à information partielle.
- Tucker et al. (2023), [*Bandits with costly reward observations*](https://proceedings.mlr.press/v216/tucker23a.html), cadre d'apprentissage avec rétroaction payante.

**Gouvernance : conserver PR en DRAFT, ne pas fusionner `main` et ne pas promouvoir cette extension expérimentale dans la bibliothèque CORE.**
