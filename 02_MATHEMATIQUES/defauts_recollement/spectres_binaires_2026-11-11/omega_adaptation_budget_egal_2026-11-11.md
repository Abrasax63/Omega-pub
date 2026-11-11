# Omega — choix et arrêt à budget égal

11 novembre 2026. Pilote synthétique, deux sessions isolées, même modèle, données et droit d’adaptation identiques, aucun outil autorisé aux sessions. La session guidée reçoit en plus la consigne de comparer les branches avant son choix, puis de réévaluer le second contrôle sur les scénarios encore compatibles.

Chaque vecteur de sorties est ordonné par h0, h1, h2, h3. Deux contrôles binaires au plus par cas. Avant la collecte, le barème accorde un point par ensemble compatible exact, avec économie de contrôles comme départage à exactitude égale. Les tables de réponses possibles sont visibles, les scénarios effectivement choisis et leurs résultats sont révélés après engagement.

| Cas | K | L | M | Scénario | Direct | Guidé | Ensemble final commun |
|---|---|---|---|---|---|---|---|
| I | 0100 | 0001 | 0011 | h2 | M=1, L=0 | M=1, L=0 | {h2} |
| II | 0101 | 0011 | 0001 | h1 | K=1, L=0 | K=1, L=0 | {h1} |
| III | 0011 | 0001 | 0010 | h0 | L=0, K=0 | K=0, arrêt | {h0,h1} |

Calcul exact sur les quatre scénarios possibles. Nombre de singletons avec les paires KL, KM, LM respectivement : I (2,2,2), II (4,2,2), III (2,2,2). Avec une politique adaptative optimale, maxima I=4, II=4, III=2. En III, h0 et h1 ont des signatures complètes identiques. La session directe a utilisé un second contrôle informatif après son choix initial L=0, qui laissait h2 compatible. La session guidée a choisi une première mesure qui a rendu ce second contrôle inutile sur le scénario réalisé.

Observation : 3/3 et deux scénarios identifiés par session, avec six contrôles pour la session directe et cinq pour la guidée. Un scénario joué par table, notation non aveugle, temps non mesuré. Aucun gain généralisé ni évaluation du RCE revendiqués.

Itération suivante : annoncer un critère de coût moyen ou de pire cas avant le test, jouer toutes les branches et masquer davantage la structure, par exemple avec des indices à interpréter plutôt qu’une table déjà normalisée.

[Audit et test précédent](audit_retroactif_omega_et_test_adaptatif_2026-11-11.md)
