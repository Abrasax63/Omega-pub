# Omega · contrôle de provenance à budget égal · protocole v0.1

**Base** `9e06385771552b5715b0a330da001173fc8adece` (PR #30).
**Statut** CALIBRATION PUBLIQUE, corpus conçu avec le mécanisme, sans holdout ni notation humaine aveugle. Les mondes, schémas de requêtes et règles d'autorité sont fournis à tous les bras. Le corrigé n'est lu que par le scoreur après les décisions. Dans un futur essai de modèles, le corrigé public rend ce corpus inéligible à un holdout.

## Corpus et sélection

Inclure toutes les lignes de `prism/provenance_cases/tasks.json`, dans l'ordre du fichier, une fois par stratégie. Les entrées mathématiques et les tableaux synthétiques sont nouveaux dans ce corpus. T1 est une divergence documentaire réelle entre versions de norme. P1, M1 et D4 contiennent des injections ou manipulations de la simulation. F1 est une dépendance documentaire, F2 une absence synthétique, D5 un duplicat. Les catégories sont fixées avant mesure et ne servent pas à choisir une action. Les enregistrements constituent des annotations de rejouage, avec dates de référence de version, sans certification cryptographique ni consultation réseau pendant le rejeu.

## Stratégies et ressources

- A applique la réponse initiale stipulée sans délégation. C'est un contrôle déterministe, sans mesure de génération directe.
- B suit l'ordre fixe des identifiants et applique le même filtre de provenance que D. C'est un contrôle de routage de vérifications, sans exécution multi-agent.
- C utilise l'optimiseur actuel à horizon variable et traite l'observation brute comme exacte selon son modèle.
- D utilise le même optimiseur, valide l'origine et la portée, recalcule le risque après observation et reprend la planification en cas de rejet. Si le modèle soutient déjà une conclusion mais que la provenance reste insuffisante, il tente une corroboration primaire ou indépendante.
- E utilise la même interprétation que D et le même arrêt, avec un horizon glouton de 1.

Plafond de deux consultations unitaires par tâche pour chaque bras. Une consultation rejetée ou manquante est facturée. La pénalité de décision est 5 millièmes par consultation dans C/D/E, sans conversion monétaire. Un seul appel par identifiant. Les bras partagent les mêmes observations accessibles et peuvent finir avant le plafond. Aucun modèle, aucun token facturé et aucun appel réseau dans le rejeu. Chronométrer l'inférence locale par cas, de manière séquentielle, hors chargement des fichiers et notation. Ne tirer aucune conclusion de latence externe à partir de cette mesure.

Arrêt à une décision déterminée avec provenance suffisante pour le bras concerné, à l'épuisement du budget, ou à l'absence d'action utile. En cas de contradiction entre observations recevables sur un champ, D/B/E révoquent ce champ et demandent un arbitrage avant de l'utiliser. Ce pilote ne définit aucun arbitrage entre deux observations également recevables. Un refus conserve la raison dans la trace.

## Évaluation et réfutation

Par bras et par tâche, conserver réponse, statut, risque interne exact, contrôles et raison de chaque rejet, coût, durée et verdict. Compter réponses correctes, réponses erronées, abstentions justifiées, abstentions sur tâche décidable, erreurs confiantes (risque interne nul ou réponse directe catégorique). La notation binaire mesure le verdict avec piste de preuves structurée. Elle ne mesure pas la qualité d'une démonstration rédigée. Les abstentions justifiées et les décisions exactes contribuent au score principal. Rapporter couverture et coût séparément. D doit dépasser E sur ce score, sans hausse des erreurs confiantes, avant de retenir l'horizon variable pour ce jeu. Si B égale ou dépasse D, le gain d'une adaptation globale face au routage fixe reste indéterminé sur ce corpus. Comparer D et C pour quantifier bénéfices et pertes du contrôle de provenance.

Contre-tests fixés avant exécution : ordre des descriptions et des mondes, contradiction recevable, seconde observation issue de la même racine, provenance indisponible, refus hors budget, contrôle inutile quand la réponse est déjà déterminée, comparaison D/E sur la strate des contrôles complémentaires. Deuxième calcul indépendant pour les verdicts de mathématiques, programmation et analyse des données, plus vérification directe des références de T1, T2 et F1.

La recherche de contre-exemples se mesure ici par les injections et cas de non-identifiabilité. La représentation, l'extraction en texte libre, la mémoire et le routage de modèles restent hors de l'expérience causale. Le succès logiciel et le score de calibration ne suffisent pas à une validation scientifique.
