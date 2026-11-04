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


## Complément C5–L=3 — synchronisation partielle du 4 novembre 2026

Le rapport C5 et son script indépendant sont présents dans la branche. Le script a été réorganisé pour utiliser `research/data/v19_c5/`. L'exécution locale sur l'archive C5 a retrouvé les comptes annoncés (3 341 diagrammes, 510 ombres propres, 13 classes D5, 14 classes C5, 105 paires, 455 triples D5 et 560 triples orientés U42).

**Synchronisation des données :** les quatre entrées historiques et les quatre sorties attendues sont maintenant présentes dans `research/data/v19_c5/`. Les six CSV ont été contrôlés sur GitHub : 14 classes, 105 paires, 455 triples D5, 105 paires réparées, 455 triples D5 réparés et 560 triples orientés U42. Le JSON de résultats est également présent. Les CSV ont été transférés comme exports textuels structurés ; leur identité binaire avec les originaux n'est pas revendiquée. Les Git blob SHA-1 sont consignés dans le README du dossier de données.

Le script a été exécuté avec succès sur l'archive source de la Library, puis depuis un checkout GitHub propre par GitHub Actions. **L'exécution depuis un checkout GitHub propre a réussi** via GitHub Actions : [run pull_request #41855315734](https://github.com/Abrasax63/Omega-pub/actions/runs/41855315734). Le workflow a installé Python 3.12, récupéré la branche et exécuté le script sans erreur. Les sorties sont régénérées dans l'environnement du job ; leur identité octet par octet avec les exports textuels versionnés n'est pas testée. Aucun statut scientifique n'est promu et SQLite v33 reste hors dépôt.


## Restauration de sources référencées par SQLite v33 — 4 novembre 2026

Le contrôle en lecture seule de SQLite v33 a isolé 12 chemins distincts sous `02_PROGRAMMES_ACTIFS` et `05_BIBLIOGRAPHIE`. Les 12 fichiers correspondants ont été retrouvés dans la Library. Onze sources Markdown ont été transférées sous `research/programs/` et `research/bibliography/`. Le douzième document, un DOCX (`Adaptivity boundary - Mealy machines.docx`), est représenté par une extraction textuelle explicitement marquée `EXTRACTED.md` : l'original binaire reste dans la Library et n'est pas présenté comme copié. Le manifeste des correspondances et limites est `research/programs/README.md`.

Les contenus transférés n'ont pas été utilisés pour promouvoir les statuts des résultats. La restauration documentaire ne remplace pas l'audit de chaque preuve et ne rend pas la base SQLite publique.


## Revue sémantique des 17 cartes candidates — 4 novembre 2026

Les 17 fichiers dont le nom correspondait à un résultat SQLite sans liaison d'évidence explicite ont été comparés à SQLite v33 (titre, énoncé, hypothèses, statut et version). Les 17 correspondances sont confirmées sémantiquement. Les liaisons d'évidence vers les fichiers Markdown restent toutefois absentes dans SQLite ; aucune relation n'a été ajoutée et aucun statut n'a changé. Voir `reviews/REVUE_SEMANTIQUE_17_CARTES_CANDIDATES_2026-11-04.md`.
