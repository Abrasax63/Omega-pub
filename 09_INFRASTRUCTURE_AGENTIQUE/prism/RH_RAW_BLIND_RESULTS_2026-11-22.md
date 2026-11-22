# RH-RAW-01/02 — test sans prémâchage, résultats et décision

**22 novembre 2026. Expériences réellement exécutées. Statut : négatif pour la fidélité documentable ; compréhension scientifique NON CONFIRMÉE.** Branche PR #230, `main` inchangée, aucune API payante ni donnée de réserve fournie au modèle.

## Pourquoi changer de protocole

L'essai `RH-READING-01` (16/16) avait fourni d'avance des implications Horn normalisées. Il évaluait un moteur logique exact, **pas la capacité à découvrir seul ce raisonnement**. Le présent pilote supprime ces annotations. Il utilise des pages entières extraites mécaniquement d'un PDF réel, sans résumé, réponses, graphe, liste de lemmes ou aide sur les dépendances.

## Protocole RAW-01

- [Run GitHub 45055202839](https://github.com/Abrasax63/Omega-pub/actions/runs/45055202839), réussite **technique**.
- Document original : [Guide de Michael Rubinstein sur la preuve Alpöge–Claude](https://www.math.uwaterloo.ca/~mrubinst/alpoge_claude_grh/zeta-paper.pdf), téléchargé directement dans le runner. Empreinte PDF SHA-256 `667d88b3c375adf0466678094f452ca966aef0f4d368f6340d2bd5328b7fb706`.
- Pages physiques **2, 3** extraites avec `pdftotext -layout`; le modèle reçoit le texte intégral de chaque page sans interprétation humaine.
- Modèle réel : Qwen2.5-0.5B-Instruct Q4_K_M, exécuté sur CPU GitHub via llama.cpp b12633, sans API payante. Empreinte GGUF SHA-256 `6eb923e7d26e9cea28811e1a8e852009b21242fb157b26149d3b188f3a8c8653`.
- Quatre appels (deux tâches génériques par page) à température zéro. Le modèle doit proposer des citations littérales ; Omega les contrôle par égalité stricte avec la page. Il n'évalue **pas** la validité mathématique de la conclusion.
- **Résultat : 4 sorties / 4 techniquement générées ; 0 / 4 au format JSON complet demandé ; 0 citation vérifiable acceptée.** Plusieurs sorties sont tronquées par la longueur maximale et contiennent des reformulations données comme citations.
- Malgré quelques mentions pertinentes des limites du document, **la compréhension sémantique n'est pas évaluée ni démontrée** ; aucune thèse nouvelle admissible.

## Protocole RAW-02 — contre-test du format, sans indications sémantiques

- [Run GitHub 45055540432](https://github.com/Abrasax63/Omega-pub/actions/runs/45055540432), réussite **technique**.
- Le même PDF et le **même fichier de poids**, avec SHA-256 vérifiés strictement. Nouvelles pages physiques **4, 5**, jamais fournies dans RAW-01. Aucune structure de dépendance, liste d'affirmations ni vérité terrain n'est envoyée.
- Le changement est uniquement une grammaire de **format** plus contrainte (JSON et au plus deux affirmations demandées), un budget de sortie plus large (512 tokens) et un nouveau corpus de pages. La comparaison est exploratoire, car le nombre de pages et le prompt changent simultanément.
- **Résultat : 4 générations, 2 JSON syntaxiquement exploitables, 0 citation littérale admissible**. Deux sorties de lecture restent JSON incomplet / trop longues ; les deux réponses de réinterprétation contiennent des propositions insuffisamment étayées. Aucune preuve de découverte ou de compréhension.
- Les contrôles restent **stricts**, sans « sauvetage » après coup de fragments d'une sortie malformée.

## Mesures

| Mesure observable | RAW-01 | RAW-02 |
|---|---:|---:|
| Appels locaux réellement exécutés | 4 | 4 |
| JSON exploitable sans réparation | 0/4 | 2/4 |
| Citations validées littéralement | 0 | 0 |
| Hypothèses originales vérifiées | 0 | 0 |
| Compréhension sémantique mesurée sur vérité indépendante | Non | Non |
| Nouveaux théorèmes certifiés | 0 | 0 |

**Attention :** la validation de citation est purement textuelle et très stricte. Zéro citation admise ne prouve pas que toutes les observations du modèle sont fausses ; cela signifie que **nous ne disposons d'aucun appui de provenance admissible pour les promouvoir**. Il n'y a pas eu de correction humaine aveugle indépendante. Le programme d'inférence ne possédait aucun corrigé structuré.

## Conclusion pour Omega

- Le problème « travail préparé » est maintenant effectivement retiré du modèle : entrée brute, consignes génériques, aucun préalable mathématique injecté, aucune réponse cachée envoyée.
- Le premier modèle local de 0,5 milliard de paramètres est **insuffisant dans ce pilote** pour faire une reconstruction scientifique citée et fiable. Ce constat ne caractérise pas le potentiel de l'architecture entière d'Omega ou d'un modèle de plus grande taille.
- Le pipeline Omega sait conserver les sorties et **bloquer** la promotion de citations non vérifiées. Ce garde-fou peut empêcher une erreur, mais **aucun gain mesuré en compréhension autonome** n'est établi.
- Les workflows de modèle sont désormais **à exécution ponctuelle**, protégés contre des relances payantes/inutiles dues à de nouvelles modifications de la PR.

## Prochaine expérience discriminante

Répéter sur un **autre document mathématique**, avec une vérité terrain extérieure préparée à l'aveugle, le même budget et un modèle de capacité supérieure si le matériel gratuit disponible le permet. Comparer la réponse directe du **même modèle** à la réponse avec contrôles Omega (sans indices de fond), en mesurant exactitude des énoncés, hypothèses manquantes, hallucinations, changements de représentation, contre-exemples, abstentions et temps CPU. Tester si un mécanisme de relecture scientifique améliore le résultat **sans ajouter de nouvelles informations d'avance**.

Ne pas simplifier les tâches jusqu'à produire artificiellement des scores élevés. Conserver les échecs de RAW-01/02 comme références de non-régression, sans les compter comme découvertes.
