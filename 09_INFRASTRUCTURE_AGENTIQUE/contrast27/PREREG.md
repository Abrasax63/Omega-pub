# CONTRAST27 — dépasser le verrou de génération par reconnaissance contrastive de théorèmes externes

**Préenregistré le 19 novembre 2026 avant de lire les nouveaux documents, de figer leurs empreintes, de coder les contrôles ou d'appeler les modèles.** Branche empilée sur PROOFNET26 #211 ; ne pas modifier ni fusionner `main`.

## Hypothèse falsifiable
Aucun des deux formaliseurs déterministes de TYPED24/DUAL25 ne comprend directement les énoncés généraux de ProofNet-V. Peut-on acquérir une compétence *plus modeste mais réelle* en faisant reconnaître par un LLM local laquelle de deux formalisations Lean externes correspond à l'énoncé naturel, puis refuser les prédictions instables sous échange A/B ?

Ce n'est **pas** générer du Lean, prouver un théorème, ni établir la fidélité d'une traduction nouvelle ; c'est une épreuve de **reconnaissance appariée** avec négatifs construits par désappariement.

## Cohorte préengagée (aucun choix a posteriori)
- Source tiers : `marcusm117/ProofNet-Verified`, commit source **`b7ca411a2abaa6caf3580192b30d865e5bd10bc4`**, fichier original `proofnet-verified-latest/proofnet-N.lean`. Vérifier chaque blob SHA Git, commentaire natural-language et théorème Lean dans le même document, sans donner au modèle le SHA ou le numéro d'exercice.
- Indices **24 inédits pour l'évaluation Omega** : `4,5,7,8,9,11,12,13,14,15,16,17,18,19,20,21,23,24,25,26,27,28,29,30`, sans reprendre les 16 indices PROOFNET26.
- Douze groupes contigus choisis avant de regarder les textes : `(4,5),(7,8),(9,11),(12,13),(14,15),(16,17),(18,19),(20,21),(23,24),(25,26),(27,28),(29,30)`. Chaque NL est confronté à son **propre Lean de référence** et à un autre Lean de cette paire. Les théorèmes sont des originaux humains/formalisés de référence ; le **négatif est construit** par permutation et n'a pas lui-même été validé par un annotateur humain. Si deux théorèmes sont potentiellement équivalents, classer la paire `SEMANTICALLY_UNCERTAIN_NEGATIVE` et ne pas présenter son score comme exact sans examen indépendant.
- Gel des 24 blobs avant tout test et toute inférence ; aucune nouvelle donnée ajoutée après premier résultat.

## Deux ordres strictement appariés
- Pour chaque source NL, poser **deux questions séparées** au même modèle et avec les deux mêmes candidats Lean (A/B puis B/A), sans noms d'exercices, URLs ni labels de vérité. Normaliser seulement le nom du théorème des candidats, sans modifier le corps mathématique, le domaine, les hypothèses ou les quantificateurs. Réponse stricte `A`, `B` ou `NONE`.
- Deux modèles locaux gratuits sur GitHub Actions : Qwen2.5-0.5B-Instruct et Qwen2.5-3B-Instruct, poids GGUF Q4_K_M SHA256 **identiques à BENCH21**, `llama.cpp` pin **`5a4afd80779ba51166b59986e61a0bfbb9e1a4c6`**, température 0, 64 tokens, CPU. **96 générations** = 24 cas × 2 ordres × 2 modèles. Une seule génération par ordre, aucune réparation et aucun retry. Aucun service externe payant.
- Collecter réponses brutes, consommation de tokens, temps, refus, SHA fichier et Lean, les scores conditionnels et l'ordre exact. Maintenir un maximum de 4096 tokens de contexte.
- Baselines : `always_A` 50 % grâce à la permutation, `always_B` 50 %, `NONE` 0 couverture. Ne pas présenter un modèle qui dit toujours `A` comme compétent.

## Trois décisions séparées
1. **Direct** : taux de bonne sélection de la source Lean originale, y compris abstentions et erreurs de format, pour chacun des deux ordres. L'étiquette est fondée sur la paire originale externe.
2. **Stabilité contrefactuelle** : accepter une paire **uniquement si le modèle pointe vers le même document Lean** quand on échange A et B, sans utiliser le gold. Si désaccord ou `NONE`, s'abstenir. Mesurer couverture, précision conditionnelle, faux positifs évités et manque de rappel.
3. **Indices structuraux limités** : contrôles **non probabilistes, figés avant modèle** : signature de nombres entiers explicitement présents, signes de biconditionnelle et d'existence si explicitement mentionnés. Un candidat qui manque d'un marqueur requis est *suspect* ; l'architecture peut s'abstenir mais ne sélectionne jamais l'autre par simple heuristique. Rapporter la précision conditionnelle et le nombre d'abstentions supplémentaires. Ces indices ne sont **pas** une preuve de fidélité sémantique.

## Tests décisifs et limites
- Vérifier au moins 24/24 sources d'origine, 24/24 formalismes et 24 paires distinctes de corps mathématiques (sinon noter le cas et geler la conclusion).
- Test anti-biais de position : une réponse constante `A` ou `B` ne peut jamais passer le filtre de stabilité sur la même source dans les deux orientations.
- Vérifier qu'un modèle ne voit jamais l'indice ProofNet, l'identifiant du correct ou les chemins des sources.
- Injecter des sorties malformées, candidats permutés, doublons, changement de hash, formulaire sans choix, tampering de Lean et missing source ; aucun résultat ne peut être compté comme une réussite.
- Préférer les vrais résultats même s'ils sont à chance ou inférieurs ; aucune affirmation d'AGI, de modèle frontière, de preuve Lean ou de compréhension générale. La reconnaissance à choix forcé est **un proxy**. Un gain en précision par abstention s'échange contre une perte de couverture.
- Conserver les premières 24 réponses comme holdout désormais exposé ; toute amélioration future du modèle ou des règles doit s'évaluer sur un **autre** lot préenregistré.

### Références
- ProofNet-Verified (Ground False, 2026) : https://github.com/marcusm117/ProofNet-Verified
- Poiroux et al. EMNLP 2025, *Reliable Evaluation and Benchmarks for Statement Autoformalization* : https://aclanthology.org/2025.emnlp-main.907/
- *The Faithfulness Gap: Certifying Semantic Equivalence Between Natural-Language and Formal Mathematical Statements*, 2026 : https://arxiv.org/abs/2606.16541

Aucune modification de `main`, aucune certification, aucun appel API payant ni fusion. PR DRAFT.
