# OBS-COL-11 — Pré-enregistrement du transfert prospectif hors calibration
Date : 16 novembre 2026 ; figé AVANT récupération des modèles externes et AVANT première exécution du benchmark.

## Hypothèse et garde scientifique
OBS-COL-10 (#110) a établi une **divergence comportementale** sur trois modèles publics AALpy déjà utilisés pour calibrer la politique. OBS-COL-11 teste **sans ajuster cette politique** si la différence de requêtes et de coûts survit sur des modèles Moore **d'une autre source et jamais étudiés auparavant dans ce laboratoire**.

Cohorte **publique**, expérimentalement nouvelle ; ne jamais appeler « holdout privé indépendant » ou « évaluation aveugle par un organisme extérieur ». Origine : Radboud University Automata Wiki, benchmark `BenchmarkMoore-RivestShapire1993`, description : https://automata.cs.ru.nl/BenchmarkMoore-RivestShapire1993/Description ; téléchargements : https://automata.cs.ru.nl/BenchmarkMoore-RivestShapire1993/Moore.

Six fichiers dans cet ordre **figés avant de lire leur contenu** :
1. `crossword2x2.dot`
2. `crossword3x3.dot`
3. `register2.dot`
4. `register3.dot`
5. `register4.dot`
6. `register5.dot`

Chacun est téléchargé à URL `https://automata.cs.ru.nl/pmwiki/uploads/BenchmarkMoore-RivestShapire1993/<filename>`. Si un téléchargement est bloqué, si le format AALpy est incompatible, si l'alphabet est vide, ou si le modèle dépasse le budget avant convergence, enregistrer le blocage **sans substituer un autre fichier ni changer la méthode**. Un contrôle de SHA-256 des octets des fichiers téléchargés est requis dans l'artefact brut. Le contenu n'est jamais donné au sélectionneur : seulement les sorties du SUL et le modèle L# provisoire.

## Méthodes verrouillées
- Bras **A** : véritable AALpy 2.0.0 L# et ordre EQ figé dans le manifeste.
- Bras **B** : véritable L# + **couverture classique**, score `4×transitions hypothétiques distinctes + 2×changements de sortie prédite`.
- Bras **C** : même L# + **couverture + mémoire de préfixes observés** exactement comme OBS-COL-10, score `B + nouveaux préfixes / (longueur+1)`, P1 réel avant chaque reset. **Code déjà gelé** : `obs_col10/policy_divergence.py`, commit `198e3dfe4adf0ebc98158576bffabd212ba10576` ; A/B/C doivent importer la classe/fonctions directement ; aucun recalibrage post-résultat.
- Bras **D** : véritable AALpy L* (ordre EQ figé).
- Bras **E** : véritable AALpy KV (ordre EQ figé).
TTT LearnLib n'est pas intégré ici : **NON EXÉCUTÉ / PAS DE SCORE** ; l'infrastructure d'origine est conservée dans #96.

## Oracles et conditions
512 sondes EQ par machine, hypothèses : mots sur alphabet du modèle (normalisé en chaînes sans collision), toutes les séquences de longueur 1..4 puis 482 mots pseudo-aléatoires longueur 5..18 selon `random.Random(20261117 + index)`; **même graine et même générateur que #96**, jamais de données générées par un candidat. L'ordre est fixe dans A/D/E ; B/C ne modifient que la permutation de la même liste de 512.
256 mots d'évaluation indépendants des résultats (longueur 12..18, `random.Random(20261116 + index)`), **ouvrir uniquement après arrêt de tous les apprentissages**. Exclure des scores « non vus » les histoires physiquement observées pendant entraînement/EQ.
Sans cache physique externe ; 10 000 resets, 50 000 symboles, au plus 40 tours par candidat et machine. Tout dépassement ou erreur doit laisser un statut `BLOCKED`, avec log, **sans résultat inventé**. Coûts = resets, symboles, CPU et horloge mesurés, P1 inclus dans bras C. Ne comparer que les bras ayant convergé sur la même cible.
Séparer coûts de préparation des manifestations (communs) et coût de choix du bras C (son calcul et P1).
**Pas de fuite** : source/graphes et sorties réservées uniquement accessibles au simulateur ou à l'évaluateur, et non aux politiques. Vérifier l'empreinte de la classe politique C avant appel à l'oracle ; refuser les changements de code sémantique non motivés.

## Règles de verdict pré-déclarées
L'apprentissage d'automates et les calculs exacts restent **des méthodes classiques**. On reconnaît une *divergence effective* seulement si une sonde choisie diffère. Amélioration **Pareto** locale : erreurs non vues C<=B et A, resets C<=B et A, symboles C<=B et A, avec au moins une stricte inégalité, en comptant CPU en sensibilité, pas comme une preuve automatique. Si C perd sur l'une des métriques, noter trade-off ou détérioration. Aucun certificat scientifique ni généralisation statistique sur six cas publics.
Un seul run principal avec graines bloquées, pas de tuning sur les échecs ; les tests de reproductibilité ou corrections d'infrastructure peuvent être relancés mais identifiés comme tels.
Ne pas modifier `main`, CORE, la PR #110 ni ses résultats ; conserver en DRAFT.
