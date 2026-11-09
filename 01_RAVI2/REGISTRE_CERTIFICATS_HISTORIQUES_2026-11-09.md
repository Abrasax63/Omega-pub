# Registre d'inventaire des certificats et artefacts de vérification — 9 novembre 2026

**Dépôt :** `Abrasax63/Omega-pub`  
**Branche de travail :** `maintenance/reconciliation-bibliotheque-2026-11-05` (PR #5)  
**Sources historiques :** `migration/ravi2-ccs-public-2026-11-04`  
**Nature :** inventaire documentaire initial, pas une nouvelle certification scientifique.

## 1. Verdict immédiat

Les certificats et artefacts de vérification historiques ne sont **pas encore tous intégrés à la nouvelle architecture agentique**. Ils sont présents dans la branche de migration historique et dans certains dossiers déjà repris par la branche de maintenance. Le module `09_INFRASTRUCTURE_AGENTIQUE/` décrit un modèle cible de provenance et de mémoire, mais son propre README le qualifie de proposition non implémentée. Il ne constitue donc pas encore un résolveur effectif de l'ensemble du corpus.

Ce registre rend les artefacts retrouvés navigables et sépare leur nature. Il ne copie pas les fichiers sources, ne remplace aucune fiche, ne modifie aucun statut scientifique et ne déclare aucun résultat nouvellement certifié.

## 2. Périmètre documentaire connu

L'audit final de la migration historique du 4 novembre recensait dans la branche source :
- 94 fichiers sous `research/bricks/`, dont 32 fiches explicitement marquées comme reconstitutions non originales ;
- 42 fichiers sous `reviews/` ;
- 44 fichiers sous `reproducibility/` ;
- 5 documents de méthode, 14 fichiers de programmes, 5 fichiers de code et 11 fichiers de données.

Ces nombres comptent des fichiers, pas des certificats mathématiques indépendants. Les 32 reconstitutions sont documentées par des références de sources, mais leurs fiches originales autonomes n'ont pas été retrouvées dans cet audit. Leur rapprochement documentaire n'est ni un rejeu, ni une revalidation.

## 3. Artefacts identifiés — échantillon à empreinte Git vérifiée

Les empreintes ci-dessous sont les SHA Git des blobs retournés par GitHub pour les chemins et la branche indiqués. Ce ne sont pas des SHA-256 calculés sur les fichiers locaux, et elles ne prouvent pas la validité du contenu.

| Classe | Chemin dans la branche historique | SHA Git du blob | Qualification documentaire |
|---|---|---|---|
| Certificat de méthode | `reviews/CERTIFICAT_METHODE_RAVI2_SOURCE_2026-10-27.md` | `9806d39a1ea7f2a90d9e74810fc6955122299488` | Certificat de localisation de source ; explicitement pas une preuve mathématique ni une validation indépendante. |
| Certificat RAVI-2 | `reviews/TWO_EQUAL_GAPS_RAVI2_CERTIFICATE_2026-10-20.json` | `2b95748ccf69cffaeca9f54d9f33b577025678cd` | Déclare `DEMONSTRATED_INTERNAL`, originalité indéterminée ; deux contrôles algorithmiques, sans revue externe ni assistant de preuve formel. |
| Brique certifiée interne | `research/bricks/BR-CTRL-01_CERTIFICAT_MEMOIRE_INFINIE.md` | `3d52e5372f2eaecc6c66d960b0601e727325e2b2` | Source indique DÉMONTRÉ et CERT-V ; spécialisation d'un mécanisme classique. |
| Brique Navier–Stokes | `research/bricks/NS-CERT-E-10.md` | `b0b805065e15dffc278a862c27b2c80d214875e6` | DÉMONTRÉ interne ; brique autonome, ne certifie pas le théorème Navier–Stokes complet. |
| Brique Navier–Stokes | `research/bricks/NS-CERT-E-11.md` | `b59f06b98b762526bcbb8b19ba05e17b7649dfab` | DÉMONTRÉ interne ; principe fonctionnel classique, limites précisées dans la fiche. |
| Brique Navier–Stokes | `research/bricks/NS-CERT-E-12.md` | `be6b13c3e44471e5b63dd6acaec33418e10d5b5f` | DÉMONTRÉ interne ; localisation solénoïdale, limites explicites. |
| Brique Navier–Stokes | `research/bricks/NS-CERT-E-13.md` | `81d9bb273a1f1ec3e13c9912861b11d1b78e8e98` | DÉMONTRÉ interne ; platitude de toutes les dérivées requise. |
| Brique Navier–Stokes | `research/bricks/NS-CERT-E-14.md` | `601cd1d4eebaaf4ea9c61deba28f12b94623b5fe` | DÉMONTRÉ interne ; intervalle radial strictement éloigné de zéro. |
| Brique Navier–Stokes | `research/bricks/NS-CERT-E-15.md` | `aa116d4adf083a3254b54118bbe3543d2a138a96` | DÉMONTRÉ interne ; primitive périodique et condition de moyenne nulle. |
| CCS — certificat exemple | `reproducibility/CCS/ccs_certificat_exemple_v06.json` | `480712532c3ed37656b50e8aa33206a4e4a68dc0` | Exemple de structure de certificat, pas preuve autonome de correction du moteur. |
| CCS — certificat formel | `reproducibility/CCS/ccs_certificat_formel_v07.json` | `62de254311491943fd5e172bab937971191024b1` | Données source/cible et appariement ; à contrôler avec le contrat et le vérificateur correspondant. |
| CCS — certificat de trace | `reproducibility/CCS/ccs_certificat_trace_v08.json` | `6334ad84e91fc6be5c31795428b5281151640863` | Inclut une provenance et le statut `MANUAL_REVIEW_REQUIRED`. |
| CCS — script de contrôle | `reproducibility/CCS/ccs_certificat_v03.py` | `b7b6c9e2afa8a367e572f9af634fb6fe9590c56c` | Implémentation de comparaison ; son JSON de résultats annonce un témoin de non-équivalence. |
| CCS — résultat archivé | `reproducibility/CCS/ccs_certificat_v03_resultats.json` | `6a865c8768f7ae42ce9ce2714090b7a92c4a0d59` | Sortie archivée ; ne prouve pas qu'elle a été régénérée pendant cet inventaire. |

## 4. Contrôles et dossiers d'audit structurants

Les rapports suivants ont été retrouvés et lus dans la branche historique :
- `reviews/AUDIT_FINAL_PR2_2026-11-04.md` : périmètre, sécurité, scripts historiques, workflow, limites de l'audit.
- `reviews/AUDIT_RAPPROCHEMENT_32_CARTES_2026-11-04.md` : distingue les 32 fiches originales non retrouvées, leurs reconstitutions et les sources référencées.
- `reviews/AUDIT_TRACABILITE_32_RECONSTITUTIONS_2026-11-04.md` : contrôle documentaire 32/32, sans revalidation scientifique.
- `reviews/REGISTRE_RECUPERATION_SOURCES_SHA256_2026-11-04.md` : neuf sources historiques matérialisées et empreintes SHA-256 rapportées ; cinq concordances exactes avec les références SQLite décrites dans ce rapport.
- `reviews/AUDIT_CERTIFICATION_NAVIER_STOKES_2026-10-15.md` : sépare sous-briques élémentaires vérifiées, traces bibliographiques et parties non certifiées intégralement.
- `research/bricks/INDEX_BRIQUES.md` : index historique utile, mais son propre avertissement signale une divergence de comptage avec SQLite v33 (83 dans le texte historique contre 85 admissibles dans la vue citée).

## 5. Risques d'exécution — ne pas lancer en bloc

Le fichier `reproducibility/RAVI2/README.md` identifie dix scripts historiques qui écrivent dans SQLite, ainsi que trois scripts dépendant de chemins fixes sous `/mnt/data`. Ils ne doivent pas être exécutés sur une base de travail. Le présent inventaire n'a lancé aucun de ces scripts.

Les fichiers JSON sont traités comme sorties archivées. Leur présence ne signifie pas que les calculs ont été rejoués. Le workflow V19 C5 documenté ne lance pas ces scripts historiques. La base SQLite v33 reste hors du dépôt public et n'a pas été modifiée.

## 6. Compatibilité avec l'architecture agentique

Le modèle de provenance de `09_INFRASTRUCTURE_AGENTIQUE/MODELE_PROVENANCE.md` prévoit les objets `KnowledgeItem`, `Artifact`, `Activity`, `Agent`, `Run` et `SourceSnapshot`, ainsi que les relations `used`, `generated`, `wasDerivedFrom`, `dependsOn`, `reviewed` et `contradicts`. C'est une bonne structure cible pour ce corpus.

Mais l'architecture est explicitement déclarée « proposition non implémentée ». À ce stade :
- aucun registre complet de certificats n'est raccordé au moteur de contexte ;
- aucune résolution automatique des identifiants et versions du corpus historique n'est démontrée ;
- les statuts de publication et les statuts scientifiques doivent rester deux champs distincts ;
- les certificats documentaires, certificats de calcul, preuves formelles, contrôles de code, sorties archivées et reconstitutions doivent rester des types distincts ;
- une empreinte ou une reprise par un agent ne vaut jamais preuve mathématique ni vérification indépendante.

## 7. Lacunes et prochaines opérations

1. Extraire la liste complète des 94 chemins de briques, 42 revues et 44 artefacts de reproductibilité depuis l'arbre historique, puis classifier chaque fichier sans inférer son statut.
2. Relier chaque certificat à son identifiant de résultat, version, source primaire, preuve, contrôles, dépendances et éventuelles contradictions.
3. Rapprocher les fichiers avec le registre transversal et l'index global de maintenance ; conserver les divergences de comptage comme anomalies ouvertes tant qu'elles ne sont pas résolues.
4. Pour les 32 reconstitutions, récupérer les sources primaires disponibles, calculer les empreintes, comparer les empreintes de référence et ne jamais remplacer une reconstitution sans original vérifié.
5. Définir le schéma de registre puis brancher le Context Engine en lecture seule ; ne permettre aucune promotion de statut par un agent.
6. Rejouer seulement les tests discriminants manquants, dans un environnement jetable et après audit des scripts. Ne pas toucher à SQLite privée.

## 8. Limites de cet inventaire

- Il s'agit d'un inventaire initial ciblé, pas encore du catalogue exhaustif fichier par fichier.
- Les SHA Git du tableau identifient les blobs sur la branche consultée ; ils ne remplacent pas les SHA-256 des sources originales.
- Les descriptions de statut sont reprises des fiches et rapports consultés ; elles ne sont pas réauditées ici.
- Aucun calcul, test, preuve Lean, revue bibliographique ou certification scientifique n'a été exécuté ou renouvelé pendant cette opération.
- Aucun fichier source historique n'a été déplacé ou supprimé ; aucune branche source n'a été fusionnée ; `main` et la base SQLite privée ne sont pas modifiées.

**Verdict :** premier registre de provenance documentaire établi sur la branche de maintenance ; intégration complète et raccordement effectif à l'architecture agentique restent à faire.
