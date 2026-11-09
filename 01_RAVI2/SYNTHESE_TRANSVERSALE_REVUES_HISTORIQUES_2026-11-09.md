# Synthèse transversale des 47 revues et audits historiques — 9 novembre 2026

**Dépôt :** `Abrasax63/Omega-pub`  
**Branche source auditée :** `migration/ravi2-ccs-public-2026-11-04`  
**Branche de publication :** `maintenance/reconciliation-bibliotheque-2026-11-05`  
**Périmètre :** les 47 chemins de `reviews/` de l'inventaire exhaustif, rapprochés des six rapports de lots 01–06 et des audits antérieurs déjà lus.  
**Nature :** synthèse documentaire et hiérarchisation des verrous. Aucune preuve, simulation, base ou test n'a été exécuté dans cette synthèse.

## 1. Bilan de couverture

- 47/47 chemins de `reviews/` couverts.
- Six rapports de lots publiés : lots 01 à 06.
- Les six rapports et l'index `01_RAVI2/README.md` ont été relus depuis la branche de maintenance.
- Les empreintes Git des fichiers sources sont consignées dans les rapports de lots.
- Aucune source historique n'a été écrasée.
- Aucune écriture SQLite, aucun changement de statut scientifique, aucun changement de `main`, aucune fusion de branche.

**Sens exact de « couvert » :** lecture et réconciliation documentaire. Cela ne signifie pas que les 47 audits ont été rejoués ou que leurs conclusions ont toutes été revalidées.

## 2. État général de la bibliothèque

### Cartes et reconstitutions

Le corpus de briques compte 94 fichiers :
- 62 briques originales ;
- 32 reconstitutions explicitement marquées comme non originales.

Les 32 résultats associés aux reconstitutions existent comme enregistrements structurés dans SQLite v33. Ce sont les fichiers Markdown originaux autonomes qui n'ont pas été retrouvés. Plusieurs rapports, manuscrits, scripts, données et archives de preuve ont été localisés, mais ils ne sont pas transformés artificiellement en cartes.

Les 17 correspondances de cartes initialement repérées par nom ont été confirmées sémantiquement (17/17). Les liaisons explicites SQLite vers ces fichiers restent une question distincte dans les instantanés de migration concernés.

### SQLite v33

Les audits techniques historiques concordent sur le snapshot v33 :
- 89 résultats, 85 admissibles ;
- 74 DÉMONTRÉ et 11 CALCUL EXACT parmi les admissibles ;
- 49 relations `DEPEND_DE` ;
- 217 entrées `evidence`, 177 relations `result_sources` ;
- intégrité SQLite `ok`, aucune violation de clé étrangère ;
- 62 tests de régression enregistrés PASS.

Les 62 PASS sont des enregistrements historiques ; ils ne sont pas tous rejoués dans les audits de consolidation/vérification. Le binaire SQLite n'est pas dans le dépôt public et son SHA-256 n'est pas une sauvegarde.

## 3. Contradictions et divergences à ne pas lisser

### A. P4 / lemme de localité L+2 — priorité critique

Un audit C4/L=2 du 4 novembre reconstruit les composantes forcées P1–P4, affirme le lemme L+2 démontré sous les hypothèses primaires et rapporte 536 comparaisons finies sans divergence.

Un état de recherche ultérieur conserve pourtant P4 comme verrou à contrôler. Les audits V19 fibre≤2 et multiplicité s'appuient eux aussi sur la structure P1–P4.

**Verdict de synthèse : À RÉEXAMINER.** Ce n'est pas une réfutation de la preuve du 4 novembre, mais une divergence de statut suffisamment importante pour interdire de déclarer le verrou définitivement fermé sans confrontation primaire.

Contrôle décisif recommandé :
1. reconstruire la définition exacte de P4 à partir de la note primaire ;
2. vérifier les cas où une composante forcée rencontre simultanément le préfixe pertinent et le cycle ;
3. vérifier l'élimination des feuilles et la borne temporelle L+2 ;
4. comparer la preuve générale aux énumérations finies, sans les substituer à la preuve ;
5. établir si le verrou ultérieur concerne la même proposition et les mêmes hypothèses.

### B. Fibre paire → mauvais objet ≤2 — dépendance P4

Le rapport N11 du 15 octobre classe la borne universelle fibre≤2 comme INDÉTERMINÉE, car seuls cinq systèmes N=11 et des contrôles finis étaient alors disponibles.

Le rapport fibre≤2 ultérieur présente une preuve générale dans le domaine C5, binaire, L=3, mauvais objets propres non vides, avec un lemme de Krylov et la structure P1–P4.

**Verdict de synthèse : DÉMONSTRATION HISTORIQUE CONDITIONNELLE, statut courant À RÉEXAMINER à cause de P4.** Ne pas étendre aux objets vides, ombres pleines, autres horizons ou autres cycles.

### C. V19 : plusieurs objets de comptage

Les documents distinguent quatre niveaux :
- paires d'états distinctes ;
- mauvais objets distincts ;
- ombres géométriques exactes ;
- classes d'ombres modulo rotations ou réflexions.

Les nombres ne sont pas interchangeables :
- 13 classes D5 et 14 classes C5 orientées ;
- 105 paires orientées et 455 triples D5 dans un catalogue de témoins ;
- 560 multisets triples orientés réalisés dans U42 selon le rejeu indépendant ;
- premier ordre d'obstruction géométrique annoncé : 3 ;
- premier ordre d'obstruction au niveau des labels orientés : 11.

La réflexion fusionne une paire chirale ; le quotient D5 ne doit pas être utilisé comme substitut du problème orienté C5.

### D. Récupération V19 : fichiers historiques et réparés

Les CSV de témoins triples du 15 octobre et du 4 novembre « repaired » ont le même nombre de lignes mais des SHA-256 différents et un premier octet divergent. Ils doivent rester séparés jusqu'à comparaison sémantique ligne par ligne.

Le rapport de récupération approfondie note une entrée manquante pour le script V19 dans une recherche donnée ; le rapport de rejeu indépendant ultérieur décrit une exécution depuis une archive C5 distincte. Ces états sont compatibles si les chemins d'accès et artefacts exacts restent documentés. Ne pas prétendre qu'un script a été rejoué depuis un jeu d'entrées incomplet.

### E. SQLite v32 / v33 et compteurs de provenance

L'audit du 27 octobre concerne v32 et rapporte dix résultats sans relation `result_sources`, dont neuf avec evidence. Les audits du 4 novembre portent sur v33 et rapportent zéro liaison orpheline, 177 relations `result_sources` et 217 evidence.

Il s'agit de versions différentes, avec une réparation documentaire entre les deux. Ne pas les traiter comme des mesures simultanées.

Un autre écart historique concerne 26 liens explicites, 25 preuves de type carte et 22 relations `INTERFACE_CARD`. Les dénominateurs et types de relations diffèrent ; cet écart ne doit pas être corrigé par une addition ou une conversion automatique.

### F. Two Equal Gaps : validité interne / originalité

Le certificat enregistre validité interne, deux contrôles algorithmiques et originalité INDÉTERMINÉE. La revue ultérieure par deux agents IA distincts apporte une analyse contradictoire de la preuve et une vérification bibliographique supplémentaire, mais n'est ni aveugle, ni humaine, ni formelle. La source de Frid (1999) établit des résultats exacts de transport sous des hypothèses plus fortes ; elle ne règle pas à elle seule la priorité de la famille générale étudiée.

**Verdict de synthèse : validité interne conservée selon les audits historiques ; originalité INDÉTERMINÉE.**

### G. Discovery / Structural Graph / contrats stricts

Les couches doivent rester séparées :
- Discovery v0.1/v0.2 : génération de candidats et ranking ;
- Structural Graph : attracteurs et signatures structurelles ;
- contrats stricts v1.3 : compatibilité interne des interfaces, hypothèses, gardes et versions ;
- noyau scientifique : résultats et statuts.

Le benchmark comparatif a trouvé que l'heuristique structurée générique faisait moins bien que la baseline lexicale sur les mesures publiées. Les scores ne sont pas des preuves. Les certificats d'interface ne certifient pas la vérité mathématique des résultats reliés.

## 4. Verrous prioritaires proposés

Classement par influence sur plusieurs résultats, et non par nouveauté supposée.

### Priorité 1 — P4 / L+2

C'est la dépendance transversale la plus importante : elle touche la réduction locale C4/L=2, les résultats V19 de mauvais objets, la borne fibre≤2 et les arguments de coexistence qui utilisent les préfixes locaux.

**Statut : À RÉEXAMINER.** Reprendre la preuve primaire avant de toucher aux résultats dérivés.

### Priorité 2 — capacité en mauvais objets `μ_T(ω)`

La borne fibre≤2 donne seulement :
`ceil(ν_T(ω)/2) ≤ μ_T(ω) ≤ ν_T(ω)`.

Elle ne détermine pas la capacité exacte ni les coefficients des circuits. C'est un problème distinct de la capacité en paires et des capacités de classes.

**Statut : question ouverte distincte, ne pas la fermer par la borne fibre≤2.**

### Priorité 3 — réconciliation sémantique des témoins V19

Comparer les CSV originaux et réparés, confirmer les paires distinctes dans chaque ligne, conserver les témoins D5 et C5 orientés séparés, et vérifier les références exactes utilisées par chaque script.

**Statut : contrôles historiques rapportés ; audit sémantique complet des versions de témoins encore requis.**

### Priorité 4 — audit de provenance SQLite et cartes

Les 17 correspondances sémantiques confirmées ne sont pas des liaisons SQLite explicites. Les 32 reconstitutions ne sont pas des originaux. La base privée ne doit pas être modifiée avant un mapping exact de chaque source et une sauvegarde versionnée.

**Statut : réconciliation documentaire avancée ; réparation de base non entreprise.**

### Priorité 5 — antériorité bibliographique des résultats candidats

Plusieurs audits utilisent `NO_EXACT_PRIOR_ART_FOUND` ou une recherche ciblée. Ce n'est pas une preuve de nouveauté. Two Equal Gaps, les familles de complexité en facteurs et plusieurs résultats V19 conservent une originalité INDÉTERMINÉE.

**Statut : INDÉTERMINÉ ; une recherche bibliographique bornée ne peut pas être promue en preuve de priorité.**

## 5. Ce qui est établi par le travail de cette session

- Les 47 chemins de revue/audit de l'inventaire ont été couverts documentairement.
- Six rapports de réconciliation ont été créés sur la branche de maintenance et vérifiés par relecture GitHub.
- L'index `01_RAVI2/README.md` référence les six lots.
- Les divergences P4/L+2, D5/C5, SQLite v32/v33, CSV triples et Discovery/certification sont explicitement conservées.
- Aucun statut scientifique n'a été modifié ; aucun script, test, calcul, preuve Lean ou requête SQLite n'a été exécuté dans cette opération.

## 6. Ce qui n'est pas établi

- La validation mathématique indépendante des 47 audits.
- Le rejeu actuel des volumes de calcul cités.
- La fermeture définitive de P4/L+2.
- La capacité exacte des mauvais objets ou la classification complète des circuits.
- L'originalité bibliographique des résultats dont le statut est INDÉTERMINÉ.
- Le transfert/publication de la base SQLite binaire.
- Le déploiement GitHub Pages ou la fusion des branches.

## Conclusion

**47/47 revues/audits sont couverts au niveau documentaire.** Cette couverture a permis d'identifier un verrou prioritaire et plusieurs distinctions sémantiques indispensables. Elle ne renouvelle aucune certification scientifique.

La prochaine opération rationnelle n'est pas une nouvelle migration ni une promotion de cartes : c'est un audit adversarial primaire de P4/L+2, puis seulement, si ce verrou résiste, la reprise contrôlée des résultats fibre≤2 et capacité en mauvais objets.
