# OMEGA-TRANSFER-01 — mémoire vérifiée vers tâche inconnue

**Statut : EXPÉRIMENTAL / NON CERTIFIÉ.** [Préenregistrement](PREREG_2026-11-17.md) réalisé avant le code et les tests, sur branche empilée au-dessus de la PR #103. Pas de modification de `main`, ni entraînement payant.

## Question testée
Avec des poids Qwen inchangés, une liste de corrections candidates **identique** et un même RCE scientifique commun, est-ce que des exemples de réparations **testées sur d'autres programmes** améliorent la sélection du bon correctif ?

Ce n'est pas un véritable apprentissage des poids du modèle : Omega fabrique une petite **mémoire en contexte**, vérifie ses exemples par oracle puis la donne à Qwen. La capacité à généraliser hors de cette grammaire reste indéterminée.

## Pipeline
1. Importer de la PR #103 les cinq sources défectueuses et le générateur AST de patchs à une ligne. La ligne fautive n'est pas fournie à la fonction de proposition.
2. Sur les quatre tâches monofautes C1..C4, choisir des exemples de corrections qui passent la suite discriminante indépendante du générateur. Les résultats sont marqués comme **exemples d'entraînement**, pas des résultats nouveaux.
3. Pour chaque tâche C1..C4 tenue à l'écart, exclure son propre exemple et transmettre au modèle seulement les **trois autres** ; la tâche à deux fautes C5 emploie les quatre comme contrôle négatif. Source RCE et SHA sont vérifiés via `notes_from_rce`.
4. À chaque cible, Qwen reçoit **exactement la même source défectueuse**, la même liste de corrections validées sur les trois cas faibles, le même contexte RCE commun et les mêmes limites `-c 3072 -n 64 --temp 0`. Le témoin reçoit, à la place des exemples vérifiés, un texte neutre de **même nombre de caractères**.
5. Alternance des ordres d'appel ; consigner statuts réels, SHA de contextes, choix et durées. Geler les entrées réservées par empreinte avant tout appel et les choix par une seconde empreinte **avant** de calculer les réponses réservées.
6. Oracle `walks_exact` et suite discriminante sur les corrections choisies ; baseline `first_weak`. Comparer exactitude, abstentions, erreurs et le contrôle négatif.

Le rapport comprend un journal d'observations, un tableau par tâche et la différence MEMOIRE moins CONTROLE en nombre de réparations correctes sur quatre tâches simples.

## Exécution
Sans modèle ni réseau (tests d'intégration avec sélecteur simulé **clairement marqué**, aucune réussite Qwen inférée) :

```bash
cd 09_INFRASTRUCTURE_AGENTIQUE/memory_transfer
python -m unittest -v test_transfer.py
```

Modèle CPU local, ou workflow GitHub Actions de cette PR (binaire llama.cpp et poids Qwen épinglés, aucune clé d'API) :

```bash
python transfer.py --llama-cli /chemin/llama-cli \
  --model-file /chemin/model.gguf --output transfer-result.json
```

## Limitations / critères de non-promotion
- **4 cibles monofautes internes seulement** et une contrôle à deux fautes. Elles proviennent d'un même modèle de programme, avec des fautes connues des expérimentateurs ; ce n'est pas un jeu externe aveugle.
- Les règles sont choisies avec un oracle de test et une grammaire écrite par des humains. Les poids Qwen ne changent pas.
- Même nombre de **caractères** pour le contexte variable, mais nombre de **tokens non vérifié identique**. Budget total entraînement/vérification n'est pas strictement égal à celui d'un système ignorant cette mémoire.
- Même corpus pour toutes les comparaisons, donc résultats corrélés ; pas de test de significativité, ni résultat scientifique général certifié.
- Les corrections proviennent uniquement de la grammaire statique de PR #103, non de code arbitraire généré par Qwen. `check_public` exécute des constructions de cette grammaire en Python restreint ; cela **ne remplace pas un sandbox Docker** pour du code non fiable.
- La réussite du workflow prouve qu'il a exécuté les tests, pas que mémoire ou Qwen améliorent l'exactitude. Lire obligatoirement `transfer-result.json` et les annotations avant toute interprétation.
- Aucun résultat n'est promu automatiquement, aucune fusion, aucune modification de CORE ou `main`.

**Interprétation :** MEMOIRE = CONTROLE ou MEMOIRE inférieur signifie que ce premier raccord **n'apporte pas de gain mesuré** sur ces tâches. Un score supérieur ne serait qu'un signal préliminaire à confirmer sur des bugs réels nouveaux et des budgets de tokens mesurés.
