# Réconciliation des cartes et résultats SQLite v33 — 4 novembre 2026

## Périmètre et méthode

Comparaison en lecture seule entre :
- les 85 lignes de la vue `certified_active_results` de SQLite v33 ;
- les 47 fichiers individuels de `01_BRIQUES_REUTILISABLES/` présents dans l'arbre GitHub de la branche de migration ;
- les références d'évidence `REUSABLE_CARD`, `RESULT_CARD` et les locateurs explicites vers `01_BRIQUES_REUTILISABLES` dans SQLite.

Les 47 chemins ont été constatés dans l'arbre GitHub récursif de la branche. La comparaison par identifiant de fichier est distincte d'une preuve de provenance : un préfixe de nom ne vaut pas liaison documentaire explicite.

## Résultat quantifié

Sur les 85 résultats admissibles :
- **26** ont une liaison d'évidence explicite vers un fichier individuel présent dans le dépôt ;
- **17** ont un fichier dont le nom commence par l'identifiant du résultat, mais sans liaison d'évidence explicite correspondante dans SQLite ;
- **42** n'ont pas de fichier individuel correspondant dans le dossier migré.

Sur les 47 fichiers individuels présents :
- **43** correspondent par identifiant exact ou préfixe unique à un résultat de la base ;
- **4** n'ont pas de correspondance directe avec un `result_id` : `GLOBAL-LOC-01.md`, `NS-P55-COMP-01.md`, `OSC-ITER-01.md`, `OSC-REAL-01.md`.

## Les 17 correspondances par nom seulement

`BR-OBS-BAD-01`, `BR-OBS-CAP-01`, `BR-OBS-CAP-02`, `BR-OBS-CAP-03`, `BR-OBS-CIRCUIT-01`, `NS-CERT-E-10`, `NS-CERT-E-11`, `NS-CERT-E-12`, `NS-CERT-E-13`, `NS-CERT-E-14`, `NS-CERT-E-15`, `OBS-V19-BAD-FIBER2`, `OBS-V19-C5-CAPACITY`, `OBS-V19-COEX-REGION`, `OBS-V19-COEX-SMALLMODEL`, `OBS-V19-FIRST-OBSTRUCTION11`, `OBS-V19-N11-BADOBJECT`.

Ces correspondances doivent être confirmées par lecture du contenu des cartes et ajout/réparation de la liaison SQLite appropriée ; aucune liaison n'a été créée automatiquement.

## Les 42 résultats sans carte individuelle correspondante

`APP-OBS-SPARSE-DISJOINT`, `BR-AFFINE-GAUGE-GLUE`, `BR-AFFINE-GROUP-CORE`, `BR-AFFINE-TREE-GLUE`, `BR-OBS-REVEAL-KERNEL`, `DELTA-P3-N5`, `DELTA-SPECTRUM-CLASS`, `DESC-SUM-01`, `EXT-OAI-MARG-REPAIR`, `EXT-OAI-MATCH-CORNER`, `EXT-OAI-MATCH-RANK`, `EXT-OAI-REL-CORNER`, `EXT-OAI-REL-SELECT`, `EXT-OAI-UNIT-LIFT`, `OBS-AFFINE-GROUP-CORE-VALIDATION`, `OBS-M27-BINARY`, `OBS-M27-CONFLICT`, `OBS-M27-FERTILE`, `OBS-M27-SPECTRUM`, `OBS-RESTRICT-AFFINE`, `OBS-RESTRICT-COUNT`, `OBS-RESTRICT-FORCED-QUOTIENT`, `OBS-RESTRICT-GREEDY`, `OBS-RESTRICT-MULTIMOMENT`, `OBS-RESTRICT-OVERLAP`, `OBS-RESTRICT-PROFILE`, `OBS-V19-C5-13`, `OBS-V19-C5-ORIENTED14`, `OBS-V19-FORCED-P4`, `OBS-V19-GAMMA-CONNECTED`, `OBS-V19-LOCAL-L2`, `OBS-V19-N11-MOMENT-GRAM`, `OBS-V19-N11-THIRD-ORDER`, `OBS-V19-PAIR-COMPLETE14`, `OBS-V19-TRIPLE-COMPLETE13`, `OBS-V19-UNIVERSAL10`, `OBS-V8-FACT-INF`, `OBS-V9-RANK`, `OBS-V9-STAB-N1`, `OMEGA-O41-DET-V11`, `Q-RQ4-COMMON-RANK`, `Q-RQ4-PAULI-ROBUST`.

L'absence de carte individuelle ne signifie pas que ces résultats sont faux ou non sourcés : plusieurs possèdent d'autres types d'évidence (preuves, audits, calculs, documents sources). Elle signifie uniquement qu'aucun fichier individuel correspondant n'a été identifié dans le dossier de cartes migré.

## Décision et suites

- **Aucune modification** des statuts, des résultats ou des relations SQLite.
- Les 17 correspondances par nom sont laissées en attente de validation sémantique.
- Les 42 résultats sans carte individuelle sont à examiner pour déterminer s'ils doivent recevoir une carte ou rester représentés par leurs artefacts existants.
- Les 4 fichiers non associés directement à un `result_id` doivent être classés comme documents composites, historiques ou cartes à rattacher après inspection.
- Le fichier binaire SQLite (819 200 octets ; SHA-256 `ef3e9a0de51a44b30599f73f027829751a2eb144e4468175c0f290b5e0159bf4`) n'a pas encore été transféré à GitHub. L'empreinte seule ne remplace pas la base. Le canal GitHub disponible ici accepte le contenu textuel/base64, mais ne fournit pas de passerelle permettant de transmettre directement le fichier local binaire depuis le conteneur ; le transfert binaire reste donc bloqué, non simulé.

## Verdict

**RÉCONCILIATION PARTIELLE, NON CERTIFIÉE.** Les 47 fichiers sont présents dans l'arbre de la branche ; 26 liaisons directes sont explicites, 17 correspondances restent nominales seulement, 42 résultats actifs restent sans carte individuelle correspondante, et 4 fichiers ne sont pas associés à un identifiant de résultat. Aucun statut scientifique n'a été changé.


## Mise à jour après revue sémantique — 4 novembre 2026

Les 17 correspondances précédemment classées « nom seulement » ont été relues individuellement contre les lignes SQLite (`result_id`, titre, énoncé, domaine) et contre leurs locateurs d'audit/code/source. **Les 17 correspondances de contenu sont confirmées.** Le détail des cartes, identifiants de blob Git et locateurs recoupés figure dans `ADDENDUM_REVUE_17_CARTES_CANDIDATES_2026-11-04.md`.

Cette revue ne crée pas de lien de carte dans SQLite v33 : les 17 restent donc distinctes des 26 liens explicites préexistants. Le décompte documentaire mis à jour est :
- 26 liaisons explicites dans SQLite ;
- 17 cartes correspondantes confirmées par revue de contenu, mais non reliées explicitement à leur résultat dans SQLite ;
- 42 résultats sans carte individuelle identifiée.

Aucune écriture SQLite, aucun changement de statut ou de dépendance n'a été effectué. La réconciliation demeure partielle et ne vaut pas validation mathématique externe.


## Complément de revue sémantique — 4 novembre 2026

Les 17 correspondances précédemment classées « par nom seulement » ont été relues contre les enregistrements SQLite v33 : titre, noyau d'énoncé, hypothèses, statut et version. **17/17 correspondent sémantiquement** à une fiche de résultat. Le rapport détaillé est [REVUE_SEMANTIQUE_17_CARTES_CANDIDATES_2026-11-04.md](REVUE_SEMANTIQUE_17_CARTES_CANDIDATES_2026-11-04.md).

La réserve reste documentaire : SQLite ne contient pas de liaison d'évidence explicite vers ces 17 fichiers Markdown. Aucune liaison, source, version ou statut n'a été modifié. Le classement devient donc « carte correspondante confirmée, liaison SQLite explicite non réparée », et non « preuve de provenance SQLite restaurée ».


## Classement des quatre fichiers sans identifiant SQLite direct — 4 novembre 2026

Les quatre fichiers restants ont été relus. Ils sont explicitement des interfaces ou certificats composites, et non des cartes autonomes associées à un `result_id` de SQLite v33 :

- `GLOBAL-LOC-01.md` : interface composite de localisation globale, dépend de `OSC-REAL-01` et des certificats NS.
- `NS-P55-COMP-01.md` : certificat composite de réalisation annulaire, avec sous-certificats P55-A/B/C/D.
- `OSC-ITER-01.md` : interface composite d'itération oscillatoire à gain fixe.
- `OSC-REAL-01.md` : interface composite de réalisation oscillatoire par sommation diagonale.

Ils sont donc classés comme **documents composites hors table des résultats**, sans rattachement artificiel à un identifiant SQLite. Aucun statut ni relation n'a été modifié.
