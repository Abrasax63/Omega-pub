# OMEGA-PY-LEARN-02 — audit de l'essai réel, 22 novembre 2026

**Statut : EXÉCUTÉ, régression observée, compétence durable NON DÉMONTRÉE.**

## Traçabilité

- PR #233 : https://github.com/Abrasax63/Omega-pub/pull/233
- Run technique (SUCCESS) : https://github.com/Abrasax63/Omega-pub/actions/runs/45063615722
- Artefact ZIP intégral : https://github.com/Abrasax63/Omega-pub/actions/runs/45063615722/artifacts/14770666582
- Git SHA évalué : `f5cd0f93c28102d9af8c67b2a8a1a6170e864267`.
- Préenregistrement : `OMEGA_PY_LEARN_02_PREREG_2026-11-22.md`, créé AVANT le run.
- Modèle fixe Qwen2.5-3B-Instruct Q4_K_M, SHA vérifié dans le run :
  `9c9f56a391a3abbd5b89d0245bf6106081bcc3173119d4229235dd9d23253f94`.
- Exécution libre CPU, aucun endpoint payant, 0 modification des poids, aucun changement de `main`.

## Bilan quantifié directement à partir de l'artefact

| Indicateur | Résultat |
|---|---:|
| Préflight hors ligne | 20/20 tests réussis (10 ancien + 10 nouveau) |
| Exercices Python avec premier programme compilable | 2/3 |
| Exercices Python avec dernier programme compilable | **1/3** |
| Exercice de boucle : réussite sur cas publics | **2/2** |
| Programme C, premier et dernier code sur holdout | **0/40, 0/40** |
| Programme D, sans apprentissage, premier code | **5/40** |
| Programme D, sans apprentissage, code final | **11/40** |
| Programme D, après atelier + C + leçon, premier code | **1/40** |
| Programme D, après atelier + C + leçon, code final | **0/40** |
| Différence D final après - avant | **−11/40** |
| Nombre d'appels au modèle | **16** |
| Tokens d'entrée reportés | **6 177** |
| Tokens de sortie reportés | **1 032** |
| Temps cumulé des requêtes modèle | **156,243 s** |

Le statut vert du workflow valide l'EXÉCUTION, non l'apprentissage. Le total
de calcul de D_transfer comprend dix appels de formation additionnels :
**budgets totaux non égaux**, pas de preuve de causalité ni d'une perte de
compétence persistante.

## Diagnostic ligne par ligne — problèmes de modèle ET d'architecture

### A. Atelier barre oblique inversée : deux échecs différents

Premier programme : `SyntaxError: unterminated string literal` à la ligne
du test de barre oblique inversée ; le modèle reproduit l'erreur de son
énoncé. Le message du compilateur lui est transmis.

Dernière réponse : JSON non exploitable ; aucun code Python final admis.
Il faut distinguer **format de transport JSON** et **syntaxe Python** :
le second échec n'est pas une validation sémantique de son code.

### B. Atelier boucle : une réussite limitée mais réelle

Le modèle corrige le `for` sans deux-points ; premier et dernier
programmes Python valides, deux exemples publics corrects sur deux.
**C'est une correction d'exercice de syntaxe**, pas une preuve de transfert
à un programme inconnu.

### C. Atelier accolade : régression causée par l'absence de conservation

Première correction : valide en Python et fonctionnellement **2/2** sur
les exemples publics. La réponse suivante est du JSON non exploitable,
ce qui écrase le meilleur programme par `None` et conduit à **0/2** au
score final de cette fiche.

Le pilote n'a **pas de conservation du meilleur état validé**. Cela
contredit notre objectif d'apprentissage sans perte des acquis.
La prochaine version doit enregistrer les versions et préserver la
meilleure, sans falsifier le journal ni assimiler les deux scores.

### D. Programme inconnu C : conflit Python / environnement restreint

Les deux propositions C contiennent la méthode standard de chaîne
`str.isalnum()`. L'analyseur AST du prototype autorise `isalpha`,
`isdigit`, etc., mais **pas `isalnum`** : les deux codes sont rejetés
avec `FORBIDDEN_METHOD`, malgré une syntaxe Python correcte.

Cela rend **0/40 inexploitable comme mesure pure de capacité à programmer**.
Le code proposé comporte aussi des erreurs de représentation de l'algorithme
et une condition de priorité potentiellement erronée ; autoriser
`isalnum` ne prouverait donc pas la correction fonctionnelle.

**Défaut d'évaluation** : une politique de sécurité interne ne doit pas
être confondue avec une erreur de langage Python. Pour la suite, soit
autoriser explicitement cette méthode sûre avec audit, soit afficher au
modèle la liste et la ligne des méthodes interdites. Garder séparés les
scores « syntaxe », « politique », « sémantique ».

### E. Programme inconnu D : véritable confusion fonctionnelle

Le programme sans formation est syntaxiquement valide et, après une
correction, transforme les lettres en minuscules mais **ne supprime
pas les répétitions**. Il réussit 11/40 cas cachés.

Après le parcours pédagogique, le modèle produit un algorithme
de segmentation reposant sur le caractère `?` et les changements
locaux de caractère. Cela ne correspond pas au comportement observé
d'unicité par ordre de première occurrence. Les deux versions D_transfer
sont syntaxiquement valides mais échouent fonctionnellement, 1 puis 0/40.

La leçon auto-produite est générale (« traitement des chaînes,
cas limites, lisibilité »), insuffisante pour justifier un transfert.

Cette dernière différence n'est pas uniquement un refus du sandbox :
elle reflète une reconstruction incorrecte de D. Toutefois, on ne peut
pas attribuer causalement la baisse à l'atelier avec un seul modèle/
une seule graine et des budgets différents.

## Décision et prochaine expérience discriminante

**Ne pas relancer les 40 cas exposés**, ni ajuster le script puis appeler
cela une réplication indépendante.

Construire une cohorte V3 **nouvelle et préenregistrée** avec :

1. **Feedback format/syntaxe/politique/sémantique séparés.** Message
   exact de Python, JSON invalide explicitement décrit, méthode
   interdite identifiée avec ligne si politique; aucune réponse
   d'oracle caché exposée.
2. **Retour arrière non destructif.** Enregistrer toutes les tentatives
   mais conserver le meilleur programme ayant passé la compilation et
   les cas de développement. Mesurer le score « première tentative »,
   « dernière tentative » ET « meilleur état admissible ».
3. **Cours progressifs et test de maîtrise.** Passer au module suivant
   seulement si les exercices de syntaxe passent des tests inédits,
   sans donner les solutions. La pratique doit être répétée sur des
   variantes originales, plutôt que trois réparations isolées.
4. **Cohorte de nouvelles tâches inconnues.** Mesurer un nouvel ensemble
   de programmes et de holdouts ; documenter dès l'origine les
   méthodes Python autorisées. Ne jamais recycler les C/D exposés.
5. **Vrai apprentissage durable si compétence observée.** Constituer un
   ensemble séparé de corrections validées et un corpus d'évaluation
   étanche pour une adaptation supervisée/LoRA, avec GPU approprié ;
   vérifier le transfert sur des tâches jamais utilisées à
   l'entraînement. Aucun fine-tuning n'a été réalisé ici.

Ne pas promouvoir de compétence en mémoire certifiée sur ce seul essai.

**Conclusion :** le pilote a démontré une faiblesse de l'enseignement
et du banc de test, et une erreur de reconstruction indépendante sur D.
Il n'a **pas** démontré qu'Omega progresse par formation en contexte.
