# Spécification des tâches T1 et T3 — générateurs v0.1

**Date :** 10 novembre 2026  
**Branche :** `work/benchmark-prisme-adaptatif-v0-1-2026-11-10`  
**Statut :** spécification et pseudo-code ; aucun benchmark exécuté.

## 1. Principe de conception

T1 et T3 doivent différer sur une seule propriété contrôlée : la déterminabilité à partir des données fournies.

- **T1 — déterminé :** toutes les données nécessaires sont présentes. Une procédure exacte permet de calculer une unique réponse.
- **T3 — sous-déterminé :** au moins une donnée nécessaire est absente et plusieurs complétions compatibles conduisent à des réponses différentes. La réponse correcte consiste à signaler précisément l'information manquante, pas à deviner.

La difficulté de raisonnement ne doit pas être confondue avec le manque d'information. T1 peut avoir une chaîne de dépendances longue tout en restant déterminé ; T3 peut être très court tout en étant sous-déterminé.

## 2. T1 — chaîne déterministe de dépendances

### Définition

Une tâche T1 fournit une valeur initiale entière (x_0), une suite ordonnée de transformations affines (f_i(x)=a_i x+b_i), et demande la valeur finale (x_k). Tous les coefficients et toutes les étapes sont fournis.

La référence exacte est obtenue en appliquant successivement les transformations, dans l'ordre indiqué. Il existe une unique valeur finale.

### Exemple fixé

Entrée :
- (x_0=3)
- (f_1(x)=2x+1)
- (f_2(x)=3x-4)
- (f_3(x)=x+5)

Calcul de référence :
- (x_1=2(3)+1=7)
- (x_2=3(7)-4=17)
- (x_3=17+5=22)

Réponse attendue : **22**.

Cet exemple illustre une dépendance en chaîne, mais n'est pas en lui-même un test de localité L+1. Le benchmark Omega doit mesurer la profondeur de raisonnement à partir de la chaîne explicite, sans prétendre que les transformations affines réalisent le modèle orbital étudié en V19.

### Pseudo-code du générateur

```text
generate_T1(seed, k, coefficient_bound):
    rng = Random(seed)
    x = rng.integer(-coefficient_bound, coefficient_bound)
    initial = x
    steps = []

    repeat k times:
        a = rng.integer(-coefficient_bound, coefficient_bound)
        while a == 0:
            a = rng.integer(-coefficient_bound, coefficient_bound)
        b = rng.integer(-coefficient_bound, coefficient_bound)
        steps.append((a, b))
        x = a*x + b

    task = {
        "type": "T1",
        "initial": initial,
        "steps": steps,
        "question": "Quelle est la valeur finale ?"
    }
    oracle = replay_exactly(initial, steps)
    return task, oracle
```

### Contrôles du générateur

- La graine et tous les paramètres sont enregistrés.
- L'oracle recalcule la réponse depuis l'entrée sérialisée, sans lire la réponse produite par le générateur.
- Un test indépendant vérifie le résultat par substitution arrière ou par une seconde implémentation.
- Les cas (k=1), (k=2), chaîne longue, coefficients négatifs et coefficient (a=1) sont inclus.
- Éviter les valeurs trop grandes : fixer une borne et détecter les dépassements si une implémentation à entiers bornés est utilisée.

## 3. T3 — information indispensable absente

### Définition

Une tâche T3 fournit une relation (y=ax+b), avec (a), (b) et (y) connus, mais omet (x). Si (a=0), cette omission ne rend pas nécessairement (x) déterminable ; pour éviter les cas dégénérés, le générateur impose (a\ne0). La valeur de (x) est alors mathématiquement déterminée par les données, donc ce n'est PAS un bon T3.

Pour construire un vrai T3, on fournit plutôt (y=ax+b) avec (a\ne0), mais on omet la valeur de (y) ou de (b), sans autre contrainte qui la fixe. Plusieurs valeurs finales restent compatibles.

### Exemple fixé

Entrée :
- (x_0=3)
- (f_1(x)=2x+1)
- seconde transformation annoncée sous la forme (f_2(x)=3x+b)
- la valeur de (b) n'est pas fournie.

Question : « Quelle est la valeur après la deuxième transformation ? »

Deux complétions compatibles :
- si (b=0), résultat (3(7)+0=21) ;
- si (b=4), résultat (3(7)+4=25).

Les deux réponses sont compatibles avec l'énoncé. La sortie correcte est donc : **impossible à déterminer sans connaître (b)**. L'assistant doit demander la valeur de (b), ou fournir une réponse conditionnelle explicite.

### Pseudo-code du générateur

```text
generate_T3(seed, coefficient_bound):
    rng = Random(seed)
    x0 = rng.integer(-coefficient_bound, coefficient_bound)
    a1 = rng.nonzero_integer(-coefficient_bound, coefficient_bound)
    b1 = rng.integer(-coefficient_bound, coefficient_bound)
    a2 = rng.nonzero_integer(-coefficient_bound, coefficient_bound)
    b_hidden = rng.integer(-coefficient_bound, coefficient_bound)

    x1 = a1*x0 + b1
    visible_steps = [(a1, b1), ("affine", a2, "UNKNOWN")]
    task = {
        "type": "T3",
        "initial": x0,
        "visible_steps": visible_steps,
        "question": "Quelle est la valeur après la deuxième transformation ?"
    }

    witness_1 = a2*x1 + b_hidden
    alternative_b = b_hidden + 1
    witness_2 = a2*x1 + alternative_b

    assert witness_1 != witness_2
    assert both_completions_match_visible_input(task, b_hidden, alternative_b)

    oracle = {
        "status": "UNDERDETERMINED",
        "missing": "b de la deuxième transformation",
        "witness_answers": [witness_1, witness_2]
    }
    return task, oracle
```

### Contrôles du générateur

- L'oracle conserve deux complétions distinctes qui satisfont toutes les données visibles.
- Les deux complétions doivent produire des réponses différentes.
- Le paramètre caché ne doit apparaître ni dans l'énoncé ni dans les métadonnées transmises au système évalué.
- La référence attendue est le statut « sous-déterminé » et l'identification de la variable manquante.
- Un contrôle anti-fuite vérifie que la graine, le paramètre caché et les témoins ne sont pas inclus dans le prompt.

## 4. Contrat commun des données

Chaque instance doit être sérialisée avec deux objets séparés :

```json
{
  "task_id": "T1-<seed>-<index>",
  "family": "T1",
  "prompt": "...",
  "public_parameters": {},
  "oracle_private": {
    "expected_status": "DETERMINED",
    "expected_answer": 22
  },
  "generation": {
    "seed": 123,
    "generator_version": "0.1"
  }
}
```

Pour T3, `oracle_private.expected_status` vaut `UNDERDETERMINED`, `expected_answer` est nul, et `missing_information` nomme le paramètre omis. Les témoins de complétion restent privés pour la notation.

Le prompt public et l'oracle privé doivent être stockés séparément pendant l'évaluation afin d'éviter toute fuite de la réponse.

## 5. Barème de notation minimal

### T1
- 1 point : réponse numérique exacte.
- 1 point : étapes ou justification cohérentes avec les données.
- 0 point si la réponse est erronée ou si le système refuse sans raison.

### T3
- 1 point : détecte que l'information ne suffit pas.
- 1 point : identifie le paramètre manquant (b).
- 1 point : demande cette information ou donne une réponse conditionnelle correcte.
- 0 point si une valeur unique est inventée ou affirmée sans hypothèse.

Noter séparément la détection et la formulation : un système peut détecter l'indétermination sans identifier précisément ce qui manque.

## 6. Tests unitaires obligatoires avant génération en lot

1. L'exemple T1 ci-dessus produit exactement 22.
2. L'exemple T3 ci-dessus admet au moins deux réponses compatibles, 21 et 25.
3. Modifier le paramètre caché de T3 modifie le résultat sans modifier le prompt public.
4. Aucune donnée privée de l'oracle ne fuit dans le prompt.
5. Même graine + mêmes paramètres = même instance.
6. Graine différente : les instances peuvent différer, sans exiger que chaque tirage soit unique.
7. Les validateurs rejettent tout T3 dont les deux complétions produisent le même résultat.

## 7. Limites et prochaine étape

Ces deux familles constituent un pilote minimal de déterminabilité, pas une évaluation complète de l'intelligence ni une validation du routage adaptatif. Elles ne testent pas encore la recherche documentaire, les contradictions, ni les preuves mathématiques V19.

Avant tout benchmark comparatif :
1. implémenter le générateur et l'oracle dans deux modules séparés ;
2. exécuter les tests unitaires ci-dessus ;
3. vérifier l'absence de fuite entre prompt et oracle ;
4. figer une petite batterie pilote ;
5. seulement ensuite, exécuter les configurations A, B et C dans les mêmes conditions.

**Verdict actuel :** définitions T1/T3 et pseudo-code spécifiés. Aucun code de générateur exécuté ; aucun score de benchmark disponible.
