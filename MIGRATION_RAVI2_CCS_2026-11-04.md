# Migration publique — RAVI-2 / CCS

Date : 4 novembre 2026  
Dépôt source : `Abrasax63/Omega-`  
Branche source : `migration/bibliotheque-ravi2-2026-11-03`  
Dépôt cible : `Abrasax63/Omega-pub`  
Branche cible : `migration/ravi2-ccs-public-2026-11-04`

## Périmètre transféré

Cette branche de revue rassemble une sélection de documents de recherche depuis la branche source :

- cartes de résultats et briques réutilisables, avec leurs statuts d'origine ;
- audits, rapports de revue et certificats documentaires ;
- méthode RAVI-2, amendement sur la fermeture contrôlée des verrous, protocole de commit scientifique et définitions ;
- scripts et fichiers de contrôle RAVI-2 ;
- paquet CCS : sources Lean/Python, vérificateurs, manifestes et exemples de certificats.

Les fichiers sont regroupés dans `research/`, `reviews/` et `reproducibility/`. Les noms et contenus des documents transférés sont conservés, à l'exception de leur emplacement dans le dépôt public.

## Éléments volontairement non transférés

- La base binaire `RESEARCH_MEMORY.sqlite` version 33 : elle n'est pas présente dans cette migration. Son empreinte SHA-256 documentée dans la source ne constitue pas une copie de sauvegarde.
- Les fichiers de mémoire de conversation et d'architecture interne, qui ne sont pas nécessaires à une revue scientifique publique.
- Les fichiers qui ne sont pas accessibles en texte via l'interface GitHub utilisée pour cette migration.

## Limites de validation

Le transfert de fichiers ne vaut pas validation scientifique. Les statuts présents dans les documents sources sont conservés, mais ne sont pas promus par cette migration.

L'audit source du 4 novembre 2026 indique notamment que la réconciliation entre 85 résultats actifs admissibles de la base SQLite et les cartes individuelles est partielle : 26 correspondances explicites, 17 candidats à vérifier sémantiquement et 42 résultats sans carte individuelle correspondante dans le dossier migré. Ces nombres décrivent l'audit de la base source, pas une validation indépendante de chaque document public.

Les scripts et certificats n'ont pas tous été rejoués pendant cette opération. Les lecteurs doivent consulter les hypothèses, dépendances, limites et statuts de chaque dossier.

## Vérification de la migration

Cette branche est proposée sous forme de Pull Request en brouillon afin de permettre une revue avant intégration dans `main`. Les fichiers sont à contrôler sur la branche cible. La branche privée source n'est pas modifiée.

Aucune affirmation de migration intégrale de la bibliothèque privée n'est faite.
