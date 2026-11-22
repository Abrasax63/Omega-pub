# Omega — réinterprétation contrôlée et audit de redondance

**Date : 22 novembre 2026.** Dossier expérimental de la PR #230, sans fusion, suppression ni modification de la cadence existante.

## Ce qui existe avant ce raccord

- Le prisme de la PR #81 planifie des missions mais ne revendique ni exécution de modèles ni compréhension scientifique automatique.
- Le programme Omega 100 a déjà des contrôles de lecture et de fidélité, une méthode d'expériences séparées et un journal, notamment l'expérience 042 (fausse route détectée malgré un gain sur paraphrases).
- La PR #82 contient une représentation V19 par quotient non signé, signe XOR et projecteur exhaustif, et a déjà montré que l'amélioration du coût dépend de la famille étudiée.

**La réinterprétation n'est pas une preuve.** Une proposition doit relier une citation littérale unique à un Git blob vérifié, déclarer deux représentations alternatives, leurs invariants et leurs domaines d'échec, formuler un contrefactuel discriminant et préciser un test avec réserve indépendante. Le registre d'exécution demeure distinct.

## Deux thèses proposées, non démontrées

1. `OMEGA-HYP-SEM42-SPAN-ROUTING` — la paire état/horizon est représentée simultanément par des slots et un graphe de justifications textuelles. Hypothèse : exiger les deux fragments source et l'abstention sur ambiguïté diminue les fausses routes sans perdre le rappel. **À tester** sur de nouvelles paraphrases, corrigé indépendant, même budget que le routeur de référence.
2. `OMEGA-HYP-V19-SURVIVAL-SWITCH` — passage adaptatif entre graphe quotient sans signe et contraintes XOR signées. Hypothèse : choisir la stratégie selon un seuil figé de survivants réduit le coût sur des familles nouvelles à verdict exactement identique. **À tester** avec références et réserves nouvelles; des constructions proches ont déjà été étudiées, originalité non revendiquée.

Le script `research_reflector.py` valide des **contrats de proposition**, pas leur vérité. Aucune des thèses n'entre automatiquement dans la file des résultats vérifiés.

## Résultat de l'audit non destructif

[Run #45048412642](https://github.com/Abrasax63/Omega-pub/actions/runs/45048412642), SHA `f797f146f7e84e1a1def992784e4686990e4d3d0`, vert : **15 groupes de fichiers Python à contenu octet-identique** entre les trois checkouts inspectés (PR81, PR82, Omega100) et **3 paires de tâches textuellement voisines** parmi six activités déclarées.

Les groupes de fichiers identiques sont surtout des copies **sur plusieurs branches**, pas 15 tâches exécutées en double. Une copie de test peut servir à reproduire un résultat historique ; son contenu identique ne justifie pas de l'effacer.

Les trois ressemblances à examiner sont :

| Activités | Similarité lexicale observée | Évaluation |
| --- | ---: | --- |
| Synthèse provenance #81 / sonde d'intégration PR230 | 0,889 | Objectif proche, rôles différents : calcul candidat versus contrôle de raccord |
| Projecteur exact V19 #82 / contrôle V19 PR230 | 1,000 | Même cible formulée, mais oracle de référence versus nouveaux échantillons bornés |
| Routeur Omega100 #042 / proposition de routage avec citations | 0,545 | Réutilisation d'un problème pour tenter une autre représentation ; pas une répétition d'expérience exécutée |

**Suppression sûre démontrée : aucune.** **Travail redondant confirmé par identité complète de contrat, entrées, sources, oracle, réserve et coût : aucun dans cet inventaire.** Des tâches lexicalement proches peuvent être complémentaires. La similarité de noms ne prouve pas l'équivalence sémantique.

## Stratégie d'optimisation sans risque inutile

- **Conserver** les sources historiques, certificats, tests critiques et réserves gelées. Aucune suppression ni fusion autonome.
- **Éviter** de recompter la même expérience comme nouvelle grâce aux identifiants, hypothèses et empreintes déjà journalisés.
- **Proposer**, mais ne pas appliquer sans validation, un regroupement de contrôles strictement équivalents avec mêmes versions, entrées, oracle, et résultats. Rejouer les tests à chaque changement de dépendance et périodiquement comme non-régression.
- **Quarantaine réversible** seulement si une fiche paraît obsolète : conserver original, SHA, références entrantes, raison, restauration et preuve de non-régression avant toute décision ultérieure.
- **Mesurer** CPU-seconds / expérimentation utile, temps du modèle, nouvelles hypothèses réellement falsifiées, régressions, abstentions et taux de répétition ; un audit de doublons n'est pas un gain de performance mesuré.

## Pourquoi ceci ne prouve pas une compréhension d'Omega

Citer correctement une phrase ne prouve pas que sa signification est maîtrisée. Un test plus fort exige qu'Omega prévoie comment un changement de prémisse modifiera une conclusion, conserve le même verdict à travers deux représentations équivalentes et reconnaisse les contre-exemples. Ces conditions sont inscrites dans les **propositions**, mais leur réalisation sur des tâches scientifiques nouvelles reste à mesurer. Aucun modèle LLM supplémentaire n'a été appelé pendant ce pilote.

## Vérification suivante

1. Constituer des cas indépendants pour les deux thèses, préenregistrer seuils et budget, sans réutiliser les corrigés de l'expérience 042 ou ceux des familles V19 déjà exploitées.
2. Comparer une proposition structurée à la référence, à budget équivalent, avec vérification de cohérence entre représentations.
3. Examiner le graphe des dépendances des fichiers qui paraissent redondants avant de proposer toute mise en quarantaine; ne supprimer automatiquement **aucun** actif du dépôt.

**Verdict :** capacité de préparer des interprétations alternatives **implémentée et vérifiée au niveau du contrat**, génération autonome de thèses **non démontrée**, compréhension scientifique générale **non démontrée**, doublons de travail à supprimer **non confirmés**.

## Validation d'intégration finale : propositions en attente, jamais certifiées

[Run #45048723462](https://github.com/Abrasax63/Omega-pub/actions/runs/45048723462), SHA `9fe4d0be2b8e77a0afe8a15e3f0a1adc92e7cb71`, **succès**.

- **24/24 tests** : 4 du raccord, 6 de la file, 7 du contrôle des propositions et redondances, 7 des moteurs de provenance existants.
- Les deux thèses ancrées sur des sources réelles sont transmises à `fast_cycle_queue.py` sous le statut `NOT_EXECUTED_NEEDS_INDEPENDENT_TEST`. Elles ne deviennent ni un événement scientifique vérifié ni une nouvelle expérience exécutée.
- Deux invocations consécutives du pilote, puis une reprise depuis un run GitHub précédent, préservent les identifiants et évitent de rejouer les sondes (contrôles verts).
- Audit répété : 15 groupes de fichiers identiques, 3 paires d'activités à examiner, **0 suppression** et **0 certification automatique**.

**Mesure manquante :** pas encore de benchmark comparant la qualité des hypothèses d'Omega à des hypothèses de référence sur de nouvelles données, et aucun gain de temps dû à une suppression de tâches. Le résultat validé porte sur l'intégrité des sources, les contrats, la mémoire et le comportement non destructif.
