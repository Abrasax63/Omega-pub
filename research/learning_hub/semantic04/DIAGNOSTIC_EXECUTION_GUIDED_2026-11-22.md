# Diagnostic causal OMEGA-SEMANTIC04 — édition dirigée par exécution

**Date 22 novembre 2026. Résultat analytique rétrospectif, NON nouvelle expérience indépendante.**
**Pas de modification du modèle, pas d'API payante, pas de \`main\`, pas de redémarrage du test caché comme benchmark inédit.**

## Données primaires

- [SFT01 entraînement LoRA CPU](https://github.com/Abrasax63/Omega-pub/actions/runs/45073297901) : 124 mises à jour réelles ; gain 0/12 → 11/12 sur des *erreurs syntaxiques*.
- [SEMANTIC04 première exécution](https://github.com/Abrasax63/Omega-pub/actions/runs/45074827572) : sur douze *erreurs logiques compilables*, SmolLM2 base **0/12** entièrement correct, LoRA **0/12** entièrement correct même avec extraction permissive, correcteur symbolique **11/12**. Détails : base **8/60** cas cachés corrects en extraction permissive, LoRA **9/60**, symbolique **55/60**.
- [Audit de correction post-hoc #45079031488](https://github.com/Abrasax63/Omega-pub/actions/runs/45079031488) : **24/24 tests logiciels (13 nouveaux et 11 d'origine)** réussis. Rapport de recalcul sur **les douze mêmes tâches consommées**, aucun nouvel appel à un modèle.

## Défaut exact du correcteur initial

La liste de substitutions cherchait seulement \`source.replace(old, new, 1)\`. Lorsque \`" in "\` apparaît dans \`for c in s:\` puis plus loin dans \`if c in out:\`, l'unique substitution cible d'abord le mot-clé Python \`for ... in\` et rend le candidat syntaxiquement invalide. La correction utile en seconde position n'était jamais proposée. Le cas précis **SEM04-even_distinct_lower-reversed_membership** était donc manqué **par le générateur de corrections**, et non par impossibilité théorique de retrouver la bonne opération.

\`execution_guided.py\` énumère toutes les positions de modification, déduplique par empreinte, valide l'AST, exécute **uniquement les exemples visibles** dans le sandbox déjà existant et conserve un budget borné.

## Comparaison post-hoc : distinguer recherche et sélection

Sur les **mêmes douze programmes déjà notés** :

| Méthode | Programmes complets corrects sur les tests cachés | Signification |
|---|---:|---|
| Correcteur symbolique S04 original | 11/12 | Résultat historique préenregistré |
| Correcteur symbolique avec toutes les positions | 12/12 | **Recalcul a posteriori**, pas généralisation indépendante |
| Mélange naïf de candidats symboliques et du texte LoRA, abstention sur conflit | 3/12 sélectionnés correctement ; 9 abstentions | Ajouter un modèle faible peut dégrader la décision en multipliant les possibilités |
| Hybride **symbolique d'abord**, LLM seulement si aucune correction admissible | 12/12 ; 0 consultation du texte LoRA nécessaire | Évite la régression observée sur ce petit corpus, sans prouver un avantage externe |

La **couverture de génération** (« la bonne solution existe parmi les candidats ») ne doit jamais être comptée comme un succès de **sélection**. La priorité symbolique n'est pas une preuve de correction générale : elle conserve une solution qui passe les cas publics et demande encore des contrôles indépendants.

## L'outil d'apprentissage interactif (pas de weight training ici)

- \`resolve_guarded\` protège une solution symbolique admissible. Si aucune n'existe, il peut inspecter le code proposé par un modèle **sans faire lui-même d'appel réseau/LLM**.
- Si plusieurs candidats passent les exemples publics mais prédisent des sorties différentes, \`probe_disagreement\` propose une nouvelle entrée qui sépare ces hypothèses. **Il n'invente jamais l'output correct et n'interroge pas les cas cachés** : il demande un nouvel oracle *autorisé*.
- Si le comportement de référence n'est pas disponible, la décision doit rester **ABSTENTION**. Cela évite de transformer un programme seulement plausible en connaissance validée.
- L'outil n'est pas un éducateur autonome et ne constitue pas une preuve que les paramètres d'Omega apprennent à coder. Il fournit une brique d'expérience active à connecter plus tard à un vrai modèle.

## Recherches comparables et implications

- [SWE-agent, NeurIPS 2024](https://proceedings.nips.cc/paper_files/paper/2024/hash/5a7c947568c1b1328ccc5230172e1e7c-Abstract-Conference.html) : donne au modèle des interfaces réelles pour éditer, lancer et inspecter les programmes.
- [Teaching Large Language Models to Self-Debug, ICLR 2024](https://proceedings.iclr.cc/paper_files/paper/2024/hash/2460396f2d0d421885997dd1612ac56b-Abstract-Conference.html) : un retour des tests et une explication peuvent aider la correction sans modifier les poids.
- [CodeT, ICLR 2023](https://arxiv.org/abs/2207.10397) : exécution de tests générés et accords entre programmes, à ne pas confondre avec la vérité d'un oracle indépendant.
- [Qwen2.5-Coder-1.5B-Instruct-GGUF, source du modèle](https://huggingface.co/Qwen/Qwen2.5-Coder-1.5B-Instruct-GGUF) : candidat gratuit pour une étude comparative avec un modèle *préentraîné pour le code* (aucune performance démontrée par Omega à ce stade).

## Suite décisive

Préenregistrer **de nouvelles familles de fonctions et de défauts** issues de sources externes auditables, avec tests de référence séparés et indépendants. Comparer dans **un même budget CPU/tokens** :

1. correcteur symbolique borné sans LLM ;
2. un modèle spécialisé en code (par ex. Qwen2.5-Coder-1.5B), réponse directe ;
3. le même modèle avec exécution + feedback + éventuellement une unique requête de clarification sur cas discriminant ;
4. modèle + correcteur symbolique **avec repli protégé**, sans rejet d'une solution vérifiée.

Mesurer exactitude sur *tous* les cas invisibles, erreurs silencieuses, abstentions, coût CPU, nombre d'appels, et amélioration du **même modèle** quand on retire les outils/mémoire après entraînement. Le modèle spécialisé n'a pas encore été exécuté dans ce pilote ; éviter toute annonce de gain avant run.

**Décision technique actuelle :** retenir \`execution_guided.py\` comme candidat expérimental vérifié par tests logiciels. **Ne pas** l'inscrire comme une capacité générale certifiée dans le registre horaire tant que le test externe inédit n'existe pas. PR demeure DRAFT, main inchangée.
