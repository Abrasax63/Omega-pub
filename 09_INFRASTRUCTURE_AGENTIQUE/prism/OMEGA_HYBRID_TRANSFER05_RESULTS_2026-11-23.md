# OMEGA-HYBRID-TRANSFER-05 — rapport réel et audit contradictoire (23 novembre 2026)

**Statut : EXPÉRIENCE RÉELLE EXÉCUTÉE, gain d'apprentissage par contre-exemple NON OBSERVÉ.** Il s'agit d'un petit test exploratoire d'utilisation d'une règle en contexte. **Aucune nouvelle compétence paramétrique, transfert durable ou supériorité statistique démontrés.**

## Provenance vérifiable

- [Run réel CPU #45276666362](https://github.com/Abrasax63/Omega-pub/actions/runs/45276666362), deux jobs **SUCCESS** : gel du protocole + comparatif effectif à 26 appels Qwen2.5-3B-Instruct Q4_K_M (`llama.cpp b12633`, modèle dont le SHA-256 est contrôlé avant chargement).
- [Artefact brut #14867153503](https://github.com/Abrasax63/Omega-pub/actions/runs/45276666362/artifacts/14867153503) : `model_inputs.json`, `oracle_only.json`, `report.json`, journal et SHA de modèle, sources inspectables ; ZIP téléchargé SHA-256 `c1eb621f39706fbe58fed2adc39b6ea8d46acd0366dfb04f0e2b34bc40f08d1b` ; `report.json` SHA-256 `a957bed17e3db720d8f0d8889a97f4ac9de91dc3115e92009ca3e72c11d5993a`.
- Protocole fixé AVANT modèle : `OMEGA_HYBRID_TRANSFER05_PREREG_2026-11-23.md`. Empreinte gelée des **questions** `413dd18d03ba5a3b3aa918eb924d8ca0b1f6fc1ecc47249d11d9d9a08265140c` ; des **réponses oracle** `590a30c359c25c943b27cbd4ea5a94862693fe8e645c48f7ab15c784d9286279`. Les deux concordent avec le rapport archivé ; les réponses de l'oracle n'ont jamais été transmises au modèle.
- Code `omega_hybrid_transfer05.py` ; vérification supplémentaire `omega_hybrid_transfer05_audit.py` et tests `test_omega_hybrid_transfer05_audit.py`. Le deuxième oracle exploite l'équivalence : pour une relation réflexive symétrique, être transitive signifie que **chaque composante connexe forme une clique complète**. Le test confronte cette méthode à `check_axioms` sur **les 64 graphes** du domaine, sans désaccord.
- [Contrôles CI hors ligne #45277052556](https://github.com/Abrasax63/Omega-pub/actions/runs/45277052556) : **59/59 tests réussis**, sans inférence de modèle ni API payante.

## Résultats préenregistrés — 8 relations inédites à quatre nœuds

Les 8 cas sont 4 relations d'équivalence et 4 relations réflexives symétriques mais **non transitives**. Tous sont non isomorphes deux à deux. Les trois conditions sont D sans aide, G avec règle auto-générée après un rejet générique, W avec règle auto-générée après un contre-exemple exact sur un ancien graphe à trois sommets.

| Bras | Booléen correct / 8 | Tous les axiomes exacts / 8 | JSON invalides | Tokens d'entrée d'évaluation | Tokens de sortie d'évaluation |
|---|---:|---:|---:|---:|---:|
| **D direct** | 4 | **4** | 0 | 1696 | 149 |
| **G retour générique** | 3 | **3** | 0 | 1704 | 149 |
| **W témoin exact** | 3 | **3** | **1** | 1696 | 155 |

Les budgets d'entrée de chaque triple de tâches sont comparables à ±5 % : `actual_prompts_balanced=true`, `approximate_prompts_balanced=true`. En revanche, **le coût total n'est PAS apparié à D**, puisque G et W comprennent chacun une génération préalable de règle.

**Coût total réel par bras, apprentissage en contexte inclus :**
- D : **8 appels**, 1696 tokens d'entrée, 149 de sortie ;
- G : **9 appels**, 1849 tokens d'entrée, 169 de sortie (incluant la génération de règle : 145+20) ;
- W : **9 appels**, 1878 tokens d'entrée, 202 de sortie (incluant la génération de règle : 182+47).

Le seuil de gain exploratoire exigeait W ≥6/8, W-G ≥2, W-D ≥2, zéro JSON invalide, et budgets comparables. **ÉCHEC SUR TOUS LES CRITÈRES D'ACCURACY ET SUR LE FORMAT** : W=3/8, W-G=0, W-D=-1, 1 JSON invalide. Verdict enregistré : `PRE_REGISTERED_GAIN_NOT_OBSERVED`.

## Échec de mécanisme : une règle vraie n'est pas une règle appliquée

Les règles **réellement formulées par le modèle** avant les tests :
- G : `Check if the relation is reflexive, symmetric, and transitive.` — consigne correcte mais très générale ;
- W : `For all x, y, z in the relation, if (x, y) and (y, z) are in the relation, then (x, z) must also be in the relation.` — reformulation correcte de la transitivité, et grammaticalement plus opérationnelle.

Les prédictions détaillées montrent un **effet de réponse dominante**, plutôt qu'une véritable inspection des arêtes :
- D a classé **tous les huit cas comme équivalences** (`holds=true`) : ses quatre bonnes réponses viennent exclusivement des positifs.
- G a répondu **`holds=false` pour sept cas sur huit** : trois des quatre négatifs sont reconnus, tandis que les positifs sont souvent rejetés.
- W a répondu **`holds=true` pour sept cas sur huit** ; la huitième sortie propose `failed_axioms=["transitivity"]`, alors que le contrat exige le nom d'axiome `transitive`. Il s'agit d'une erreur de schéma, pas d'un témoin mathématique valide ; elle reste dans le dénominateur.

**Analyse appariée :** W réussit trois tâches ratées par G, et G réussit trois tâches ratées par W : avantage net **zéro**. W ne corrige aucun des quatre échecs du bras D ; D réussit un cas que W manque. Le petit effectif interdit une conclusion statistique générale.

Cette expérience **ne prouve pas qu'Omega ignore totalement le sens de la transitivité**. Elle montre précisément que, sur ces huit cas et selon ce contrat, **la présence d'une règle verbale correcte ne se traduit pas en compétence opérationnelle de classification**.

## Interprétation structurelle et décision

Le vrai goulet ne semble plus être seulement la génération d'un JSON. C'est la **conversion d'une règle énoncée en procédure appliquée à toutes les arêtes**. La boucle « témoin exact → texte de règle → nouvelle question » n'est donc pas une stratégie d'apprentissage suffisante pour Omega dans ce test. Augmenter aveuglément la difficulté ou le nombre de tours risque d'aggraver les heuristiques de réponse.

**Décision :** conserver le résultat négatif, pas de relance de ces huit questions ni de changement du seuil a posteriori. Ne promouvoir aucune règle en mémoire de compétences et n'autoriser aucun entraînement sur ce seul jeu.

### Prochaine hypothèse falsifiable

Tester **une procédure intermédiaire contrôlée** au lieu d'une simple règle textuelle : Omega devra représenter et énumérer les triples `(x,y,z)` où `xRy` et `yRz`, vérifier pour chacun `xRz`, puis décider avec un témoin explicite. Comparer cette procédure à la règle simple et au recours à l'oracle externe, sur un jeu **nouveau à cinq nœuds**, avec des vérifications adversariales et contrôle de coût. La capacité d'Omega à **produire lui-même** les triples exacts (plutôt que recevoir les témoins de l'oracle) devra être mesurée séparément. Toute réussite aidée d'un outil reste un gain **du système**, non une modification des poids.

**Ne pas appeler le test du 23 novembre un entraînement des poids** : il s'agissait uniquement de reformulation et d'injection temporaire d'un conseil dans les prompts.