# P5-FALSIFY-03 — audit indépendant de prévalence sur tout l'univers N=4, L=4

**12 novembre 2026 — CALCUL EXACT ARITHMÉTIQUE, effectué séparément du script principal de la PR #66.** Ce contrôle n'est **pas** un nouvel essai de modèle, ni une revue sémantique externe.

## Résultat

Univers : `X={0,1,2,3}`, `4^4=256` fonctions `T:X→X`, `2^4−2=14` observations binaires **non constantes**, `2^4=16` mots de longueur 4 ; total **57 344** triplets `(T,pi,word)`.

Pour chaque couple `(T,pi)`, une énumération distincte des **quatre états initiaux** reconstruit leurs mots, puis compte le nombre de mots distincts effectivement réalisés parmi les 16 possibilités. Le calcul a produit :

| Réalisation du mot | Nombre exact | Proportion du total uniforme |
|---|---:|---:|
| Mot réalisable | **10 432** | **18,191964 %** |
| Mot non réalisable | **46 912** | **81,808036 %** |
| Total | **57 344** | **100 %** |

Une politique triviale répondant toujours `B=non réalisable` atteint **46 912 / 57 344 ≈ 81,81 %** si l'on tire uniformément un triplet dans cet univers. Cela ne constitue ni une performance de LLM mesurée, ni une solution adaptative.

### Reproduction courte, sans dépendance externe

```python
from itertools import product
n = 4
pos = neg = 0
for T in product(range(n), repeat=n):
    for pi in product((0, 1), repeat=n):
        if len(set(pi)) != 2:
            continue
        realized = set()
        for initial in range(n):
            x = initial
            word = []
            for _ in range(n):
                word.append(pi[x])
                x = T[x]
            realized.add(tuple(word))
        pos += len(realized)
        neg += 2**n - len(realized)
assert (pos, neg) == (10432, 46912)
```

**Conséquence critique :** la cohorte technique de [FALSIFY-03, PR #66](https://github.com/Abrasax63/Omega-pub/pull/66) est stratifiée de manière égale : **8 réalisables / 8 non réalisables parmi les évaluations**, conformément au pré-enregistrement, pour observer les erreurs sur chaque issue. Son taux de réussite **ne mesure pas** une précision représentative sur l'univers naturel uniforme. Des améliorations apparentes par rapport à un modèle toujours `A` ou toujours `B` doivent être rapportées à la **distribution retenue**.

Ce constat est **indépendant de toute sortie Qwen** et n'a été utilisé pour modifier ni les 20 exemples sélectionnés, ni les politiques, ni le seuil de décision. Le test initial est conservé.

Pour une future campagne de performance générale, publier **les deux** évaluations : (a) population échantillonnée naturellement/pondération explicitée ; (b) sous-échantillon équilibré sur les classes ; comparer aux politiques constantes `always-A` et `always-B`. Ne pas optimiser des prompts sur la cohorte test.

**Ne pas promouvoir la performance du pilote en CORE.** Les mécanismes de preuve et leurs limites peuvent être conservés en PROVISOIRE.
