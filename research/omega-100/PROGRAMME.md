# Omega — programme autonome de 100 itérations

Objectif mesurable : établir où Omega améliore effectivement la lecture mathématique, la fidélité des propositions et leur sélection pour vérification. Référence initiale : PR #179, commit def8bac9fdafd81422d40c4c45ac3652a6d47e35 et run #44177061894. Les travaux des PR #81 et #82 ont leur propre cycle.

## Pilotage

- 001–020 : fiabilité du lecteur et mesures de structure. 021–045 : fidélité des hypothèses/conclusions et abstentions sur de nouveaux documents. 046–070 : routage vers vérificateurs exacts et contrôles contradictoires. 071–095 : comparaison à budget égal et répétitions sur des sources indépendantes. 096–100 : réplication, bilan et choix des correctifs à proposer. Ces jalons guident la priorité ; un résultat négatif ou un obstacle documenté peut changer l'ordre des expériences.
- Avant chaque essai : une hypothèse falsifiable, une référence figée, des cas disjoints, un témoin négatif et un seuil de décision. Après : commandes, version, observations, métriques, décision et prochaine question. Compter une expérience nouvelle et reproductible, positive ou négative. Les préparations, blocages et simples relectures se consignent à part et ne font pas avancer le compteur.
- Choisir chaque prochain essai d'après l'incertitude qui bloque le plus. Après deux essais sans information nouvelle sur la même piste, changer de question. Une revue tous les dix cycles relève gains, régressions, coût et hypothèses encore ouvertes.
- Rejouer les tests pertinents et comparer les mêmes cas avec le même budget. Un candidat n'est retenu que s'il dépasse le seuil annoncé et préserve les contrôles. Un replay historique est une régression, jamais un nouveau holdout. Distinguer structure, fidélité des citations, fidélité mathématique et preuve.
- Expériences mathématiques et logicielles hors ligne ou sur sources publiques du dépôt. Aucun appel à une API payante, fusion, écriture sur main, modification d'un jeu gelé, publication de corrigés réservés ni promotion automatique de règles. Les seules écritures se font sur experiment/omega-100-2026-11-18. Journal par itération sous research/omega-100/ avec un nom unique NNN.md. L'état se déduit des fichiers successifs, jamais du compteur du planificateur. À 100, publier le bilan sur la branche et arrêter.

## Itération 001 — Préenregistrement

Question : les délimiteurs mathématiques autonomes `$$` et `\\[` / `\\]` ferment-ils le bloc et rendent-ils sa section au texte suivant ?
Référence : read.py au commit initial, sans modification. Jeu synthétique à quatre cas : bloc dollar multiligne de trois lignes suivi d'un titre niveau 2 puis un paragraphe ; bloc crochets de même forme ; paire dollar sur une ligne ; texte ordinaire sans formule. Critères fixés : un paquet mathématique dans chacun des trois cas avec formule, titre exclu des paquets, paragraphe rattaché à son propre titre et aucun marquage mathématique sur ce paragraphe. Rejouer aussi l'exactitude de tous les extraits. Budget : quatre documents locaux, aucun modèle. Réussite uniquement à quatre sur quatre ; sinon journaliser le témoin et laisser le correctif à une expérience distincte.
