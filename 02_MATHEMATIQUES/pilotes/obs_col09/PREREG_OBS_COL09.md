# OBS-COL-09 — Pré-enregistrement avant code et exécution

Date : 2026-11-15 ; branche experiment/obs-col09-external-aalpy-benchmark-2026-11-15, empilée sur #92 ; main et CORE inchangés.

## Problème précis
Comparer de vrais implémentations de référence sur des **modèles publiés par un tiers** et compter séparément consultations de l'oracle, symboles d'action et CPU. Une bonne CI ne doit pas être prise pour une plus-value intellectuelle d'Omega.

## Provenance externe verrouillée
AALpy, dépôt `DES-Lab/AALpy` (licence MIT), modèles sous `DotModels/` :
- `Angluin_Moore.dot`, blob SHA Git `4ed5251c5580b1d115823486083ddc88b3e2a5ce` ;
- `coffee_moore.dot`, SHA `91edc61c18e5624e937b7b7c1c1bf5970432dbfa` ;
- `mooreModel.dot`, SHA `d494040778647da551ea7131fdc72350041ee76f`.

Copies exactes de ces modèles autorisées pour les besoins de ce pilote avec provenance et licence AALpy. Données réelles de benchmarks logiciels (pas phénomènes naturels), **publiques et non aveugles**. Aucun modèle synthétique de notre famille OBS-COL-04...08 n'est utilisé.

## Algorithmes vraiment proposés
Sous Python 3.11, installation épinglée `aalpy==2.0.0` :
1. AALpy **L***, `run_Lstar`, mode Moore.
2. AALpy **KV** (Kearns–Vazirani), `run_KV`, mode Moore.
3. AALpy **L#**, `run_Lsharp`, mode Moore.
4. Variante Omega/P1 : L# identique, mais **chaque consultation physique** doit passer par l'authentique `planner.plan_mission`; mêmes données, sondes, ordre aléatoire et oracle. P1 n'est **pas** crédité de choisir l'expérience.
5. **TTT** : l'algorithme existe dans LearnLib (Java), **pas dans AALpy 2.0.0**. Exécuter dans un job séparé seulement si une intégration LearnLib/AutomataLib réellement exécutable peut être construite ; sinon marquer **NON EXÉCUTÉ / PAS DE SCORE** et ne jamais substituer KV ou L# sous le nom TTT.

La campagne AALpy (L*/KV/L#/L#+P1) est prioritaire et doit être reproductible, même si TTT est un blocage. On n'agrège pas les sorties de méthodes ayant accès à des oracles d'équivalence différents.

## Équivalence et budgets
Pour chaque combinaison modèle/méthode, **même** `RandomWalkEqOracle` AALpy avec `num_steps=2000, reset_prob=0.12, reset_after_cex=True` et `random.seed(20261115 + indice_modele)`. Ni le nombre réel d'états ni la transition cachée ne sont communiqués à l'apprenant, pas de `PerfectKnowledgeEqOracle`, pas de Wp paramétré par la vérité.
Limites de sécurité : 50 000 symboles d'interaction physique maximum et 10 000 resets, timeout CI 8 min. Si dépassées, rapporter `BUDGET_EXHAUSTED`, pas inventer score.
Évaluation prédictive uniquement **après apprentissage**, 256 mots pseudo-aléatoires figés par modèle via graine 20261116 + indice_modele, longueur 5..12, réponses calculées par l'évaluateur. Consigner les erreurs. Ces mots ne doivent pas intervenir dans l'équivalence ou le choix des requêtes.
Mesures : reset physiques, symboles physiques, total des mots de requête si observable, nombre d'états prédits, temps `perf_counter` et `process_time`. CPU mesuré avec les limites de la machine CI, temps non comparable inter-runs non appariés. Ne pas mélanger les opérations de vérification P1 avec les observations du système.
Statuts : `COMPLETED`, `ERROR`, `BUDGET_EXHAUSTED`; conserver traces et versions de dépendances.

## Tests de falsification
- Le chargement des trois modèles externes marche et leur SHA-256 local est enregistré.
- L'/les véritables fonctions AALpy sont importées, aucune imitation locale de L#/TTT.
- L'usage de P1 est attesté par des appels à `plan_mission` avec identifiant neutre ; requêtes et réponses sont égales sans et avec P1.
- Les modèles ne sont pas consultés pour un oracle d'équivalence parfait, hors évaluation distincte.
- Pas de gain revendiqué contre les méthodes classiques tant que les coûts complets et la qualité n'ont pas été comparés.
- Si TTT bloque, le résultat reste partiel et explicitement nommé. 
- Aucun certificat scientifique, promotion CORE, fusion ni modification directe de main.

Références : AALpy (Muškardin et al. 2022), Angluin 1987, LearnLib (librairie Java, TTT).
