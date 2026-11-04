# Rejeu indépendant V19–C5 et Mealy — 4 novembre 2026

## Objet et périmètre

Rejouer les contrôles décisifs annoncés avant la revue finale de la PR #2 :
- audit indépendant du catalogue V19, C5, horizon L=3 ;
- récupération du DOCX Mealy original et rejeu du certificat du témoin minimal ;
- rejeu du contrôle du nerf de compatibilité Mealy/Helly ;
- vérification d'hygiène ciblée de la PR et du workflow.

Ce rapport consigne des exécutions réellement effectuées le 4 novembre 2026. Il ne modifie aucun statut scientifique SQLite et ne constitue pas une revue mathématique tierce.

## 1. V19 — C5, L=3

### Source et exécution

Archive source retrouvée dans la Library : `C5_AUDIT_V19_2026-11-04.zip`.

Script exécuté depuis l'archive : `audit_v19_c5_independent_2026-11-04.py`.

SHA-256 du script : `2256241fd87ec5e87e2264e7ea6a77e3df12a8c10d45d9b0b377f3a18fa4f4f5`.

Méthode annoncée par le script : propagation directe des 32 colorations binaires du cycle, sans DSU ni union-find/parité.

### Résultats du rejeu

Le script termine sans assertion en échec et restitue :

- 3 341 diagrammes locaux canoniques ;
- 510 diagrammes à ombre propre ;
- 13 classes modulo D5 ;
- 14 classes orientées modulo C5 ;
- une scission chirale D5-06 en C5O-06 et C5O-09 ;
- 105 témoins de paires, avec 2 réparations de répétitions ;
- 455 témoins de triples D5, avec 26 réparations ;
- 105 triples orientés absents du catalogue D5, tous impliquant C5O-09 ;
- 560 triples orientés dans U42, tous vérifiés ;
- `U42_all_pass = true`.

Le JSON de sortie archivé a le SHA-256 `547e28d9a1a8f89c62cc376948241ed58fbe59122c7ab9f853647f5ead2285b8`.

### Limite essentielle

Le calcul indépendant vérifie la classification finie et les témoins selon la définition opérationnelle encodée. Il ne re-prouve pas la réduction générale par le lemme de localité L+2, ni l'exhaustivité de la forme canonique pour toute endofonction finie. La portée universelle reste donc conditionnée par le lemme L+2 de la source primaire V19. Les capacités maximales et l'originalité bibliographique ne sont pas auditées ici.

**Verdict du rejeu : CALCUL EXACT reproduit dans le domaine fini décrit, sous le lemme L+2 pour l'extrapolation générale.**

## 2. Mealy — récupération de la source originale et témoin minimal

### Source originale

Le document binaire `Adaptivity boundary - Mealy machines.docx` a été retrouvé dans la Library et lu directement, plutôt que de s'appuyer uniquement sur son extraction Markdown.

- SHA-256 DOCX : `b6a8a334ba427e62a613b43687284afa2ab6ddc0cc08f69c9aaa1942c958e1f7`.
- Structure lue : 79 paragraphes non vides et un tableau de 6 lignes (en-tête compris).
- Le tableau du témoin à cinq états, deux entrées et trois sorties est bien présent dans le DOCX.

### Certificat exécuté

Script retrouvé : `mealy_boundary_certificate.py`.

SHA-256 : `9496c346f86928c40137405dfda32046b922ff43ece0e55bfd3026c535e51555`.

Exécution : toutes les assertions passent. Sortie :

- témoin : 5 états, 2 entrées, 3 sorties ;
- propriété r_IO = 1 ;
- 6 configurations produit explorées ;
- 6 symboles observables et 13 2-blocs autorisés ;
- profondeur ADS optimale L_A = 3, sur 13 croyances accessibles ;
- aucun PDS, après fermeture d'un graphe de 6 configurations preset.

Le script vérifie séparément la fermeture locale exacte, la profondeur ADS par programmation dynamique et l'absence de PDS par BFS sur les paires d'identités encore non distinguées.

**Verdict du rejeu : CALCUL EXACT reproduit pour le témoin fini (5,2,3).**

### Nerf de compatibilité / borne de Helly

Archive retrouvée et exécutée : `PREUVES_MEALY_HELLY_2026-10-16.zip`, script `mealy_helly_bridge.py`.

SHA-256 du script : `48cb2d571b59aa9aa7de23faeb7bf0f6f27af20b467ff610bbbf06bfe06eacf2`.

Rejeu réussi :

- 21 constructions C(q,k), pour q=3,…,8 et 2≤k≤q−1 ;
- 492 états de connaissance accessibles cumulés ;
- 1 337 nœuds de nerf contrôlés ;
- aucune non-face minimale de taille supérieure à q−1 ;
- maximum observé : 7 pour q=8 ;
- la non-face minimale racine attendue de taille k est retrouvée pour chaque cas.

Le JSON de sortie reproduit a le SHA-256 `fc24611629a1835a86e61dd8f2aaf3b71f15abf1215fe5fe77eb3ccf3b06f73a`.

### Limite essentielle

Ce script contrôle la structure des nerfs et les non-faces minimales pour la famille construite. Il ne recalcule pas, pour chacune des 21 machines, la propriété r_IO=1 ni les valeurs L_A et L_P ; le rapport d'origine utilise la preuve de la borne fertile OBS-M27-FERTILE pour la borne universelle. Le script complémentaire `conflict_nerve_certificate.py`, mentionné dans le DOCX, n'a pas été retrouvé dans les éléments de Library consultés. Son absence dans cette recherche ne prouve pas qu'il n'existe nulle part.

La nouveauté bibliographique des énoncés reste INDÉTERMINÉE ; le DOCX lui-même demande une revue experte externe.

**Verdict du rejeu : CALCUL EXACT reproduit pour les contrôles finis du nerf ; la borne universelle reste conditionnée par la preuve OBS-M27-FERTILE et ses hypothèses.**

## 3. Hygiène ciblée de la PR #2

État GitHub consulté après les rejeux :

- PR #2 ouverte, en brouillon, non fusionnée ;
- branche cible `main`, branche source `migration/ravi2-ccs-public-2026-11-04` ;
- GitHub indique `mergeable = true` ;
- tête observée avant ajout du présent rapport : `43d35c9a4b358b1cab33bf3cb52aef7adfb94f25` ;
- 210 fichiers modifiés et 233 commits dans la PR.

Contrôles ciblés :

- aucun chemin modifié ne porte une extension de base SQLite/DB, clé privée, certificat ou fichier d'environnement ;
- les trois chemins contenant « SQLITE » dans leurs noms sont des rapports Markdown ; aucun fichier `RESEARCH_MEMORY.sqlite` n'est dans la liste des fichiers modifiés ;
- le workflow V19 ne demande que `contents: read`, installe Python 3.12 et exécute le script d'audit ;
- le dernier run associé à la tête vérifiée, run `41859306810`, est terminé avec conclusion `success`.

Ce contrôle est un triage de chemins et de configuration, pas un audit exhaustif du contenu des 210 fichiers ni un scan de secrets certifié.

## 4. Décision et limites restantes

Les deux familles de tests ciblées ont été rejouées avec succès. Cela améliore la traçabilité et la confiance dans ces calculs, sans certifier l'ensemble de la bibliothèque.

Restent notamment :
- la revue complète du diff des 210 fichiers et de l'historique de 233 commits ;
- la vérification de contenu exhaustive pour les secrets ou données privées ;
- la revue indépendante ligne par ligne des preuves mathématiques ;
- l'audit bibliographique et la revue humaine externe ;
- la décision séparée sur le sort des 32 fiches reconstituées et de la base SQLite privée.

Aucun fichier SQLite n'a été publié ou modifié. La branche `main` n'a pas été modifiée. La PR reste en brouillon et n'est pas fusionnée.
