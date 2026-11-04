# Audit final de la PR #2 — migration RAVI-2 / CCS

Date : 4 novembre 2026.

## 1. Périmètre et état GitHub au snapshot de l'audit

Dépôt : `Abrasax63/Omega-pub`  
PR : https://github.com/Abrasax63/Omega-pub/pull/2  
Branche source : `migration/ravi2-ccs-public-2026-11-04`  
Branche cible : `main`

Au snapshot vérifié avant l'ajout de ce rapport :

- PR ouverte, en brouillon, non fusionnée ;
- GitHub indique `mergeable = true` ;
- 219 fichiers modifiés et 253 commits selon les métadonnées de la PR ;
- tête : `648598e87fb12acf65ed3a9ac18dc6d391978a35` ;
- SHA de `main` : `86ab1d92c968364d92da21e2e71d604557e9b8fd`, inchangé par la migration.

Le statut `mergeable = true` indique que GitHub ne détecte pas de conflit de fusion ; il ne signifie pas que tous les contrôles sont terminés ou que la publication est recommandée.

## 2. Inventaire de la branche

L'arbre Git contient au snapshot :

- 94 fichiers dans `research/bricks/`, dont 32 fiches explicitement reconstituées ;
- 42 fichiers dans `reviews/` ;
- 44 fichiers dans `reproducibility/` ;
- 5 documents dans `research/method/` ;
- 14 fichiers dans `research/programs/` ;
- 5 fichiers dans `research/code/` ;
- 11 fichiers dans `research/data/`.

Le README racine a été actualisé pour refléter ces comptes. Les 32 fiches restent étiquetées comme reconstitutions et ne sont pas présentées comme les originaux.

## 3. Fichiers privés et recherche de secrets

Inspection des 219 chemins modifiés :

- aucun fichier de base SQLite/DB, fichier d'environnement, clé privée, certificat ou archive DOCX/ZIP n'est inclus ;
- les trois chemins comportant « SQLITE » sont des rapports Markdown ;
- aucun fichier `RESEARCH_MEMORY.sqlite` n'est présent ;
- une recherche ciblée des marqueurs usuels de jetons et clés (GitHub token, clé privée PEM, clé AWS, mots de passe ou champs de jeton) n'a retourné aucune occurrence.

Cette recherche est un contrôle lexical ciblé. Elle ne remplace pas GitHub Secret Scanning ni un scanner spécialisé exhaustif ; je ne peux donc pas certifier l'absence absolue de tout secret dans les contenus.

La base SQLite v33 reste volontairement privée et n'a pas été modifiée. Aucun fichier binaire de base n'a été publié.

## 4. Scripts — risque d'exécution historique documenté

La branche contient 28 scripts Python. L'inspection statique en a identifié 13 qui méritent une précaution particulière :

- 10 scripts historiques contiennent des opérations d'écriture SQLite (transactions, modifications, sauvegardes ou restaurations) ;
- 3 autres dépendent de chemins fixes sous `/mnt/data` et écrivent leurs sorties dans cet environnement historique.

Ces scripts ne sont pas exécutés par le workflow GitHub actuel et aucun d'eux n'a été lancé pendant cet audit. Le guide `reproducibility/RAVI2/README.md` les énumère et avertit explicitement de ne pas les lancer sur une base de travail. Il distingue ces anciens scripts de commit des contrôles réellement reproductibles depuis le dépôt.

Le script Mealy–Helly publié a, lui, été rendu portable : son résultat est écrit dans `research/data/mealy_helly/`, sans chemin privé fixe.

## 5. Liens et provenance documentaire

Un contrôle automatisé des liens Markdown relatifs dans les fichiers Markdown modifiés a été effectué après corrections : **aucun lien interne cassé restant** au snapshot testé.

Corrections réalisées :

- l'audit de calibration mémoire quantique, retrouvé dans la Library, a été restauré dans `research/programs/Quantique/` ;
- la note antérieure qu'il cite n'a pas été retrouvée dans les fichiers accessibles pour cette migration ; le lien a été remplacé par une mention explicite d'indisponibilité, sans substituer une source différente ;
- les sources Mealy–Helly, sa carte, le script, le JSON de résultat et le manifeste d'empreintes sont accessibles dans le dépôt ;
- le certificat du témoin Mealy `(5,2,3)` est publié sous `research/code/mealy_boundary_certificate.py` ;
- les scripts et leur périmètre sont décrits dans `research/code/README.md`.

Limites restantes de provenance :

- le DOCX original `Adaptivity boundary - Mealy machines.docx` reste dans la Library ; le dépôt ne contient qu'une extraction textuelle ;
- `conflict_nerve_certificate.py`, mentionné dans le DOCX, n'a pas été retrouvé ;
- les locateurs internes de la Library figurant dans plusieurs anciennes fiches ne sont pas tous des liens accessibles publiquement.

## 6. Workflow GitHub Actions

Le workflow `.github/workflows/v19-c5-repro.yml` :

- demande uniquement `contents: read` ;
- utilise `actions/checkout@v4` et `actions/setup-python@v5` ;
- installe Python 3.12 et exécute le script V19 C5 ;
- ne lit pas la base SQLite et ne lance aucun script historique de commit.

Amélioration de sécurité possible : épingler les actions tierces sur des SHA de commit complets plutôt que sur des tags majeurs.

Au snapshot de l'audit, le run `41863674215` associé à la tête `648598e87fb12acf65ed3a9ac18dc6d391978a35` était encore **queued** et le statut de commit était **pending**. Il n'est donc pas compté comme réussi. L'accès à la configuration de protection de branche n'a pas été accordé par GitHub ; les règles de protection et les contrôles obligatoires de `main` n'ont pas pu être confirmés.

## 7. Historique Git et confidentialité des métadonnées

La PR annonce 253 commits. L'endpoint paginé consulté a rendu 250 objets de commit ; les 250 retournés sont marqués non signés. L'historique est très granulaire, avec de nombreux commits de migration d'un fichier chacun. Ce n'est pas un défaut de contenu, mais cela rend la revue de l'historique difficile. Une fusion par squash est préférable si l'intégration est décidée.

**Point de confidentialité à vérifier avant publication définitive :** les métadonnées publiques des commits contiennent une adresse d'auteur qui n'est pas une adresse GitHub `noreply`. Je ne la reproduis pas dans ce rapport. Il faut confirmer que cette exposition est volontaire. Si elle ne l'est pas, la solution est de réécrire l'historique de la branche avec une adresse `noreply`, puis de pousser la branche réécrite avant fusion ; cela ne garantit pas l'effacement des copies déjà mises en cache ou clonées.

## 8. Résultats des contrôles scientifiques ciblés

Les contrôles V19 C5–L=3 et Mealy ont été rejoués et documentés séparément dans `reviews/REJEU_INDEPENDANT_V19_MEALY_2026-11-04.md`.

Ces rejeux établissent des calculs finis dans les domaines encodés. Ils ne constituent pas une revue mathématique tierce de toutes les preuves de la bibliothèque, ne rejouent pas les 62 tests historiques SQLite et ne certifient pas l'originalité bibliographique.

## 9. Verdict de l'audit

### Points satisfaisants

- aucune base SQLite privée ni fichier de clé identifié parmi les fichiers modifiés ;
- les 32 reconstitutions sont explicitement distinguées des originaux ;
- les scripts historiques dangereux à exécuter sont désormais documentés ;
- les liens Markdown relatifs ont été contrôlés et les ruptures identifiées corrigées ou signalées ;
- les certificats Mealy et leurs résultats sont mieux accessibles ;
- `main` est restée inchangée.

### Points à résoudre avant fusion

1. Attendre une conclusion `success` du workflow sur la tête finale de la branche ; le run observé est encore en attente.
2. Confirmer si l'adresse d'auteur visible dans les métadonnées de commit peut rester publique ; sinon, réécrire l'historique avant fusion.
3. Décider d'une stratégie de fusion, de préférence squash, compte tenu de l'historique très granulaire.

Les limites documentaires (DOCX original et certificat Mealy complémentaire non retrouvés) ne bloquent pas nécessairement une migration publique, à condition de rester clairement déclarées. La validation mathématique globale est hors du périmètre de cet audit de dépôt.

**Décision : PR maintenue en brouillon, non fusionnée.** Aucun changement n'a été poussé sur `main` et aucun statut scientifique n'a été modifié.
