# OMEGA-CREATIVE-MODEL02 — protocole gelé avant code et avant modèle

19 novembre 2026 — branche expérimentale empilée sur l'atelier #193. **Pas de modification de `main`, aucune API payante, aucune certification automatique.**

## La question qui compte
Un **modèle local réel**, sans recevoir de liste de stratégies préfabriquées, peut-il *proposer* une nouvelle représentation calculable d'un problème non présent dans le laboratoire #193 ? La proposition doit être produite **avant** les cas de validation, figée par SHA-256, évaluée sans correctif ni réessai, puis confrontée à un solveur classique performant. Une simple augmentation de performances contre la force brute n'est pas de l'innovation.

Nouveau domaine : reconnaître les chaînes bien parenthésées sur alphabet `(`, `)` (y compris la chaîne vide). Problème de départ donné au modèle en anglais : une chaîne est valide si un lecteur peut associer à chaque parenthèse fermante une ouvrante antérieure, et s'il ne reste aucune ouvrante en fin de chaîne. **Aucune notion de somme préfixe, chemin de Dyck, pile, transformation candidate ou solution ne sera décrite dans l'énoncé.**

## Interface générative : DSL non exécutant
Le modèle doit produire un **seul objet JSON**, dans la grammaire d'expressions :
- deux poids entiers `weights["("],weights[")"]` dans `[-2,2]` ;
- un prédicat booléen constitué d'au plus 31 noeuds, profondeur <=8, opérateurs `and,or,not,eq,ne,ge,gt,le,lt` et constantes entières bornées ;
- primitives descriptives **disponibles mais sans recette recommandée** : `length,sum,min_prefix,max_prefix,min_suffix,max_suffix,count_open,count_close,first_weight,last_weight,num_changes`.
- un champ `idea` texte <=500 caractères décrivant la perspective proposée. Les primitives sont une **bibliothèque de traits préconçue**, pas une invention d'opérateur de calcul par le modèle. Aucun code Python modèle ne sera exécuté, pas d'`eval` ou `exec`.
- aucune règle n'est fournie qui associe les caractéristiques à la solution. **Un exemple de syntaxe non pertinent** peut illustrer le JSON ; cela n'est pas un exemple mathématique annoté.

La bibliothèque expérimentale préexistante #193 se limitait à l'observabilité temporelle et aux graphes XOR ; cette nouvelle tâche et ses propositions ne sont pas des théorèmes mathématiques nouveaux. Le degré de nouveauté est seulement `NOT_IN_PREVIOUS_TWO_TRANSFORMATIONS`.

## Préengagements du modèle
Modèle local : **Qwen2.5-Coder-3B-Instruct Q4_K_M**, SHA256 GGUF `724fb256bec1ff062b2f65e4569e871ad2e95ab2a3989723d1769c54294730b7`, sur llama.cpp commit `5a4afd80779ba51166b59986e61a0bfbb9e1a4c6`, CPU GitHub Actions. Trois appels indépendants du même prompt **sans feedback** : seeds `11,17,23` ; températures `0,0.35,0.7` ; max `420` tokens par appel. Sorties brutes, raisons d'arrêt et nombres de tokens archivés dans un artifact GitHub **avant lancement de la correction**. Pas de requête web ni accès au corrigé pour le modèle.

## Corpus, baselines et métriques
Le code évaluateur sera commité avant l'inférence. Il générera après les propositions :
- **80 cas réservés** par `random.Random(20261119)` : 40 chaînes Dyck valides obtenues constructivement (2–24 paires), 20 invalides par changement de la première ouvrante en fermante, 20 invalides par échange de la première et de la dernière parenthèse. Cas distincts possibles non garantis : les trois ensembles sont construits sans sélection selon le résultat des candidats.
- **16 cas métamorphiques** additionnels : concaténation de paires de chaînes valides, puis changement d'une parenthèse ; les transformations exactes sont vérifiées par le correcteur externe.
- **Énumération exhaustive** de toutes les 8191 chaînes de longueur 0..12, positive ou négative. Cette validation donne un contrôle fini fort, **pas une preuve d'équivalence sur toutes les longueurs**.
- **A témoin direct faible** : réduction répétée de `()` jusqu'à point fixe ; **D témoin fort** : analyseur de pile classique en `O(n)` ; **C** : chaque candidat du modèle via interpréteur de DSL en lecture seule. Les vrais verdicts sont calculés *après* les sorties candidates figées et vérifiés par deux références différentes (pile et réduction).
- Comparer exactitude, faux positifs, faux négatifs, abstentions dues à parse/DSL, longueur des propositions, opérations instrumentées. Durées non utilisées comme preuves de performance équitable ; les primitives du DSL coûtent aussi `O(n)` ; **ne jamais déclarer un gain de coût sans égalisation des coûts réels**.
- Un succès strict de candidat signifie accord **96/96** sur les réservés/métamorphiques et **8191/8191** sur l'exhaustif, sans erreur non détectée ; une réussite limitée reçoit uniquement `EMPIRICAL_BOUNDED_EQUIVALENCE`, et non `GENERAL_THEOREM`.

## Risque central et règles d'intégrité
Le DSL fournit des opérateurs de préfixe potentiellement utiles, ce qui **réduit l'originalité de la proposition** ; le modèle est seulement testé sur sa capacité à choisir et composer ces traits sans recette. La génération de trois candidats n'implique aucune amélioration des poids, ni découverte mathématique, ni capacité générale à changer spontanément de représentation dans un domaine libre.

Si le modèle répond mal, si aucune proposition ne passe, si la CI est rouge, enregistrer **le résultat négatif**, les traces et l'hypothèse de cause. **Ne pas retoucher le prompt, le parseur, les seuils ou les cas pour sauver le score**. Les correctifs à d'éventuelles pannes purement techniques sont possibles uniquement si causaux, documentés et sans nouvelle inférence après lecture des résultats.

**Critère de prochaine étape** : comparer sur un *second domaine véritablement inédit* à un modèle sans perspective, tester la fidélité des AST sous revue indépendante, et vérifier si le modèle invente des **primitives**, pas seulement leur combinaison. Pas de branche principale modifiée et pas de fusion.
