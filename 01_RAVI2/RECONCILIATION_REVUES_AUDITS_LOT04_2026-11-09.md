# Réconciliation des revues et audits historiques — lot 04 (10 fichiers, 9 novembre 2026)

**Dépôt :** `Abrasax63/Omega-pub`  
**Branche source :** `migration/ravi2-ccs-public-2026-11-04`  
**Branche de publication :** `maintenance/reconciliation-bibliotheque-2026-11-05`  
**Périmètre :** détail des 42 résultats sans carte, récupération d'artefacts V19/Mealy/Delta, registre SHA-256, rejeu indépendant V19/Mealy, revue Two Equal Gaps, correspondances des 17 cartes et deux certificats JSON.  
**Nature :** réconciliation documentaire de dix fichiers. Aucun script n'a été exécuté dans ce lot.

## 1. Fichiers examinés et empreintes Git source

| Fichier | SHA Git source |
|---|---|
| `RECONCILIATION_DETAIL_42_RESULTATS_SQLITE_V33_2026-11-04.md` | `fc5809cafb64959682504a113fb5e87d39bd39c1` |
| `RECUPERATION_APPROFONDIE_V19_MEALY_DELTA_2026-11-04.md` | `b0cddfb1c2805156979c132d65a26fb6e154f7b3` |
| `RECUPERATION_HISTORIQUE_32_RESULTATS_2026-11-04.md` | `5221f3fa3605924f7236bde0ad38d967795b22a9` |
| `REGISTRE_RECUPERATION_SOURCES_SHA256_2026-11-04.md` | `36a7cd8031fab701d332e3a5e4e60e4e789c03cd` |
| `REJEU_INDEPENDANT_V19_MEALY_2026-11-04.md` | `63c4dea39863d62352bc2fa56f918c5537742c12` |
| `REVUE_INDEPENDANTE_TWO_EQUAL_GAPS_2026-10-21.md` | `e2c0b4c382c6f5d7b2880bb567ecdab886e7f3c8` |
| `REVUE_SEMANTIQUE_17_CARTES_CANDIDATES_2026-11-04.md` | `3743ad488b260914dc59c2a9a09a0fcdc62eaa4b` |
| `TWO_EQUAL_GAPS_COMMIT_VERIFY_2026-10-20.json` | `065ffa71e0a2503583452dba896ec5391976d012` |
| `TWO_EQUAL_GAPS_RAVI2_CERTIFICATE_2026-10-20.json` | `2b95748ccf69cffaeca9f54d9f33b577025678cd` |
| `V19_ASSEMBLAGE_ORIENTE_2026-10-15.md` | `310b870ee1cb88bee15278970a93ed80824f1cb9` |

## 2. Résultats structurés et cartes manquantes

### Détail des 42 résultats

Le rapport de détail identifie 42 enregistrements SQLite v33, avec les statuts historiques copiés de la vue admissible : 33 DÉMONTRÉ et 9 CALCUL EXACT à ce snapshot. Il précise que les résultats ne sont pas absents de la base : ce sont les fichiers Markdown individuels qui manquent dans le dossier migré.

Le document décrit ensuite plusieurs récupérations successives :
- état initial : 42 sans carte ;
- après huit restaurations : 34 restantes ;
- après récupération de `BR-OBS-REVEAL-KERNEL` : 33 restantes ;
- après récupération de `OBS-RESTRICT-MULTIMOMENT` : 32 restantes.

Le bilan final de 10 cartes originales restaurées sur 42 concorde avec les audits de couverture et de recherche élargie.

### Récupération historique des 32 enregistrements

Le rapport de récupération confirme 32/32 lignes présentes dans SQLite v33, avec champs structurés, preuves et historique de versions. Le statut enregistré est alors réparti en 26 DÉMONTRÉ et 6 CALCUL EXACT.

La différence entre 33/9 dans le rapport détaillé initial et 26/6 dans le rapport de récupération n'est pas résolue par une simple égalité de périmètre : le second document décrit le reliquat après les restaurations successives et l'inventaire actualisé. Il faut conserver les deux états datés et ne pas mélanger les distributions de statuts. Les identifiants restent 32, mais les catégories de comptage sont des instantanés distincts ; leur correspondance exacte résultat par résultat demanderait une comparaison directe des exports SQLite datés.

Le rapport rappelle également que les versions dans `result_versions` sont des versions de lignes SQLite, pas des versions des fichiers Markdown originaux.

### Revue des 17 cartes candidates

La revue sémantique confirme 17/17 correspondances entre fiches Markdown et lignes SQLite v33 sur le titre, le noyau de l'énoncé, les hypothèses, le domaine, le statut et la version. La liaison d'évidence SQLite explicite vers ces 17 fichiers reste absente. Cette revue confirme une correspondance documentaire, pas une réparation de base ni une nouvelle certification mathématique.

## 3. Récupération des sources et empreintes

### Registre SHA-256

Neuf sources ont été matérialisées historiquement et leurs empreintes calculées. Cinq concordent avec une empreinte de référence SQLite : DOCX Mealy, note V19, note RQ-Q-4 et deux PDF OpenAI. Pour quatre autres (Delta, V10, rapport O41 et audit O41), le fichier a été retrouvé et son empreinte calculée, mais aucune empreinte de référence comparable n'était enregistrée dans les lignes consultées.

Une empreinte prouve l'identité binaire avec une référence disponible ; elle ne prouve ni la validité du contenu ni l'exhaustivité des preuves.

### Récupération approfondie V19 / Mealy / Delta

Le rapport identifie plusieurs fichiers V19 récupérés, dont les CSV de capacité, témoins D5, classes orientées, JSON U42, script indépendant et scripts auxiliaires. Deux versions du CSV de témoins triples — 15 octobre et 4 novembre « repaired » — ont même taille et même nombre de lignes, mais des SHA-256 différents et un premier octet divergent à la position 105. Elles doivent rester distinctes jusqu'à comparaison sémantique ligne par ligne.

Le script d'audit indépendant V19 attend quatre entrées ; le rapport de récupération en avait localisé trois, le CSV des témoins de paires manquant. Deux modules importés par le script de capacité n'étaient pas localisés. Le rapport ne revendique donc pas de rejeu à partir de ce seul lot de fichiers.

Pour Mealy27, le DOCX original et le manifeste de hachage ont été retrouvés, mais le script de pont et son JSON de résultats n'étaient pas localisés dans cette recherche ciblée. Pour Delta P3/N5, le rapport source était retrouvé, mais pas le script exact ni les données nécessaires au rejeu.

**Nuance de chronologie :** le rapport séparé `REJEU_INDEPENDANT_V19_MEALY` décrit des exécutions réussies à partir d'une archive C5 et d'artefacts Mealy récupérés par un autre chemin. Cela ne rend pas faux le constat de récupération approfondie : il s'agit de deux périmètres de récupération et de reproductibilité distincts. La provenance de l'archive et les artefacts précis utilisés pour chaque exécution doivent rester liés à leurs rapports respectifs.

## 4. Rejeu indépendant V19 et Mealy

### V19 C5, L=3

Le rapport de rejeu du 4 novembre décrit l'exécution du script indépendant depuis l'archive `C5_AUDIT_V19_2026-11-04.zip`, avec propagation directe des 32 colorations du cycle, sans DSU/parité-union. Il rapporte :
- 3 341 diagrammes locaux ;
- 510 ombres propres ;
- 13 classes D5 et 14 classes orientées C5 ;
- 105 témoins de paires ;
- 455 témoins de triples D5 ;
- 105 triples orientés absents du catalogue D5, tous impliquant C5O-09 ;
- 560 triples orientés vérifiés dans U42.

Le rapport qualifie ce rejeu de CALCUL EXACT dans le domaine fini encodé. Il précise que le calcul ne re-prouve pas le lemme général de localité L+2 ; l'extrapolation universelle reste conditionnée à ce lemme. Capacités maximales et originalité bibliographique restent hors périmètre.

### Mealy

Le DOCX original est lu directement et le certificat du témoin minimal ((5,2,3)) est rapporté comme rejoué avec assertions satisfaites. Le rapport décrit aussi un script de nerf Mealy–Helly exécuté sur 21 constructions (C(q,k)), 492 états de connaissance et 1 337 nœuds de nerf, sans non-face minimale supérieure à (q-1).

La limite est explicite : le script de nerf ne recalcule pas toutes les propriétés (r_{IO}), (L_A) et (L_P) pour chaque machine ; la borne universelle utilise la preuve `OBS-M27-FERTILE`. Le script complémentaire `conflict_nerve_certificate.py` n'a pas été retrouvé dans la recherche citée. L'originalité demeure INDÉTERMINÉE.

### PR #2 dans ce rapport

Les contrôles ciblés de chemin et de workflow sont des snapshots datés. Le rapport mentionne un run réussi pour une tête, puis un run ultérieur encore queued/pending. Aucun de ces états historiques ne permet de déduire l'état actuel de la PR. Le contrôle de chemins n'est pas un audit exhaustif de secrets.

## 5. V19 : orientation et coexistence

Le rapport d'assemblage V19 du 15 octobre établit la distinction essentielle :
- 13 classes d'ombres isolées modulo D5 ;
- 14 classes orientées modulo C5, car une classe D5 se scinde en deux classes chirales ;
- les rotations sont admissibles pour un cycle orienté, mais la réflexion conjugue (T) à (T^{-1}) et ne peut pas être appliquée indépendamment à chaque ombre dans un problème de coexistence.

Il rapporte 105/105 paires orientées compatibles, avec témoins de taille maximale 17, et 455/455 triples au quotient D5. Ces 455 témoins ne couvrent pas les 560 multisets orientés C5 : 105 triples orientés sont absents du catalogue D5, tous associés à la classe chirale C5O-09.

Le rapport énonce aussi un théorème de petit modèle pour (k) ombres, avec une borne de taille dépendant de (q,L,k), sous l'hypothèse de localité L+2 et de cohérence des contraintes forcées. Son statut général dépend donc du verrou L+2 ; les tests finis rapportés ne remplacent pas la preuve de ce lemme.

Le rejeu indépendant ultérieur rapporte 560 triples orientés dans U42. Les deux énoncés ne sont pas contradictoires : l'un signale les 105 triples non représentés dans le quotient D5, l'autre rapporte leur réalisation dans le témoin orienté U42. Il faut conserver les niveaux D5 et C5 séparés.

## 6. Two Equal Gaps : certificat, revue et non-conformité bibliographique

### Certificat JSON

Le certificat décrit `BR-WORD-TWO-EQUAL-GAPS-COMPLEX-01`, version 1, sur les mots cycliques (W=P^a0^\delta P^b0^\delta), avec (1\le a<b), (P=10^{g-1}), (g,\delta\ge1). Il consigne :
- validité interne : DEMONSTRATED_INTERNAL ;
- originalité : INDETERMINEE ;
- deux contrôles algorithmiques ;
- pas de réviseur humain ou modèle distinct à la date du certificat ;
- pas d'assistant de preuve formelle ;
- budget de deux expériences ;
- non-conformité conservée : la recherche bibliographique ciblée a été menée après le développement de la formule.

### Vérification du commit JSON

Le fichier de vérification rapporte 89 résultats, 85 admissibles, 49 dépendances, 25 tables communes identiques, 52 contrats stricts, intégrité SQLite OK, zéro erreur de clé étrangère et zéro cycle causal. Il précise que l'indépendance reposait sur deux algorithmes, sans réviseur humain/modèle distinct. Ces compteurs sont un instantané de commit, pas des compteurs actuels.

### Revue indépendante du 21 octobre

Deux agents IA distincts de l'auteur initial ont fourni des analyses séparées, l'une sur la preuve et l'autre sur la littérature. Le rapport précise qu'il ne s'agissait ni d'une revue aveugle, ni d'une revue humaine, ni d'une preuve formelle ; l'identité exacte des modèles n'est pas fournie. L'analyse reprend la classification des facteurs spéciaux et propose une correction rédactionnelle pour le cas (g=1), sans changer le théorème.

La source primaire de Frid (1999) sur le transport de complexité sous morphismes uniformes marqués a été vérifiée. Le rapport corrige une formulation bibliographique trop faible : la littérature contient des transports exacts sous hypothèses plus fortes. Le morphisme de la famille étudiée n'est pas uniformément marqué dans le cas général ; cela ne prouve toutefois pas l'absence d'une autre représentation ou d'une antériorité plus générale.

Décision conservée : validité interne maintenue selon la revue historique ; originalité toujours INDÉTERMINÉE. La revue analytique ne vaut pas validation humaine ou formelle.

## 7. Écarts et verrous transversaux

1. **42 résultats / 32 cartes :** les 32 résultats existent dans SQLite ; les 32 fichiers Markdown originaux manquent. Ne jamais dire que les résultats eux-mêmes sont absents.
2. **33/9 puis 26/6 :** distributions de statuts issues de rapports et états successifs ; conserver la chronologie et vérifier ligne par ligne avant de les rapprocher.
3. **V19 D5/C5 :** 13 classes D5 et 14 classes C5 orientées sont des objets différents ; les 455 triples D5 ne couvrent pas les 560 triples orientés.
4. **L+2 :** les calculs C5 finis ne re-prouvent pas le lemme général. La divergence P4/L+2 identifiée au lot 02 demeure ouverte.
5. **CSV triples :** versions historiques distinctes, ne pas écraser ni substituer sans comparaison sémantique.
6. **Mealy/Helly :** rejeu de certaines propriétés finies ne remplace pas la preuve de la borne universelle ni une revue bibliographique externe.
7. **Two Equal Gaps :** deux algorithmes et une revue analytique IA ne sont pas une revue humaine ni une preuve formelle ; originalité indéterminée.
8. **SHA-256 :** une concordance d'empreinte documente l'identité d'un artefact, pas la validité scientifique.

## 8. Décision de réconciliation

- Garder les sources et sorties V19 du 15 octobre et du 4 novembre séparées.
- Garder les niveaux D5 et C5 orienté séparés.
- Maintenir le lemme L+2 comme dépendance explicite de toute portée universelle.
- Ne pas transformer les 32 résultats SQLite en 32 cartes originales fictives.
- Ne pas ajouter automatiquement les 17 liaisons SQLite manquantes.
- Maintenir l'originalité Two Equal Gaps à INDÉTERMINÉE.
- Ne pas modifier SQLite, `main` ou les branches historiques.

## 9. Limites de ce lot

Aucun script, calcul, test, checker ou preuve Lean n'a été exécuté pendant cette réconciliation. Les exécutions citées sont celles des rapports historiques. Aucun statut scientifique n'est renouvelé et aucune base SQLite n'a été consultée ou modifiée dans ce lot.

**Verdict :** dix documents réconciliés documentairement. Les résultats de rejeu historique, les lacunes de récupération et les verrous universels sont distingués sans promotion scientifique nouvelle.
