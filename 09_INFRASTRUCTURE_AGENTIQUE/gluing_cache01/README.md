# GLUE-CACHE-01 — réutilisation exacte sans recollement fantôme

**Statut : expérimentation de calcul déterministe, non intégrée aux LLM.**

## Origine mathématique existante

Ce prototype réemploie les résultats [CL-DYN / défauts de recollement](../../02_MATHEMATIQUES/defauts_recollement/RECONCILIATION_CL_DYN_01_04.md) et la [note exacte sur les obstructions internes](../../02_MATHEMATIQUES/defauts_recollement/sources/DELTA_H_RECOLLEMENT_INTERNE_2026-09-29.md). Il ne revendique pas un nouvel algorithme : propagation des ensembles de survivants et mémoïsation des préfixes relèvent des méthodes classiques de programmation dynamique et d'automates.

### Invariant utilisé
Pour `T:X→X`, `π:X→Y`, un mot `w`, conserver l'ensemble
`B(w)={(s,T^|w|(s)) : observations de s sur |w| étapes = w}`.
Puis prolonger pour une lettre `a` :
`B(wa)={(s,T(x)) : (s,x)∈B(w) et π(x)=a}`.

La récurrence est une identité exacte par induction sur la longueur de `w`. Un résultat positif fournit un état initial témoin et sa trace vérifiable ; un résultat négatif fournit la longueur du premier préfixe à survivants vides.

**Clé du cache : `(T,π,préfixe observé)` complets**, avec tuples immuables. Il serait incorrect de la remplacer par `Q`, `μ₂`, des extrémités, ou une classification LLM, car deux systèmes avec le même `Q` peuvent avoir des langages `W₃` différents.

## Tests falsifiables et contrôles indépendants

- CL-DYN `(T,π)=((0,0,2),(0,1,1))` : `110` est admissible par paires locales, **mais n'a aucun témoin microscopique**. Le cache doit le rejeter.
- Deux systèmes de quatre états avec même `Q` et `μ₂`, mais `001` admissible dans l'un et interdit dans l'autre : **aucune collision de cache**.
- Famille à recollement profond : `000` et `001` admissibles mais `0001` impossible.
- Changer `T` ou `π`, limiter/évincer le cache, demander le même mot plusieurs fois, données malformées.
- Comparer **toutes les 232 748 requêtes** pour les endofonctions à `n=2,3,4`, observations surjectives à `q=2`, mots de longueur `1..5` : référence par **traces directes originales** `delta_gluing_audit.words` ET par **matrices booléennes indépendantes** `delta_gluing_crosscheck.matrix_accepts`. Cette exhaustivité n'est que pour ces dimensions.

## Mini-benchmark de calcul

276 requêtes synthétiques sur quatre systèmes finis dont beaucoup partagent volontairement des préfixes. Comparer *exactement* chaque acceptation, certificat témoin et préfixe vide à la version sans cache ; rapporter :
- nombre d'étapes de propagation,
- visites de couples d'états microscopiques,
- succès du cache et nombre d'entrées en mémoire,
- durée murale (indicative sur runner, **non extrapolable**).

### Limites

Ne représente pas la charge réelle d'Omega et ne mesure aucun appel LLM, FLOP, joule ni économie monétaire. Un grand cache peut prendre plus de RAM qu'il n'économise de temps. Les sources historiques `CL-DYN` sont reconstituées avec des correspondances documentaires non certifiées ; l'essai emprunte des énoncés effectivement retrouvés, sans promouvoir d'identifiants historiques. **Aucune fusion dans `main` ni certification de résultat mathématique nouveau.**

## Reproduire

```bash
python -m unittest discover -s 09_INFRASTRUCTURE_AGENTIQUE/gluing_cache01 -p 'test_witness_cache.py' -v
python 09_INFRASTRUCTURE_AGENTIQUE/gluing_cache01/bench.py
```

Le branchement à l'orchestrateur d'Omega exigerait ensuite : cache par version de dépendances et contraintes complètes, stockage de témoins, contrôle exact sur les cache hits, taux réel de réutilisation, tests de non-régression, mode témoin sans cache et retour arrière immédiat.


## Contre-test de non-réutilisation

`bench_low_reuse.py` soumet **1 000 transitions différentes**, une fois chacune, avec la même observation et la même question. Les clés de cache ne correspondent jamais : **0 hit**. Il vérifie l'identité des verdicts ET des témoins, et l'égalité des opérations de propagation, tout en mesurant le coût du cache. Les allocations sont mesurées par `tracemalloc` (estimations d'allocations Python, pas RSS).

Ce contre-test détermine quand **ne pas** activer le cache : si la charge ne répète ni système ni préfixe, il ajoute de la gestion et consomme de la mémoire sans économiser un seul calcul exact. Les temps à l'échelle de quelques millisecondes restent dépendants du runner, donc ne constituent pas une mesure d'énergie ou une estimation des performances générales.

```bash
python 09_INFRASTRUCTURE_AGENTIQUE/gluing_cache01/bench_low_reuse.py
```
