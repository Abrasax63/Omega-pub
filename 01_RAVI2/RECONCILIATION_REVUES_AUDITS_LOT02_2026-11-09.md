# Réconciliation des revues et audits historiques — lot 02 (10 fichiers, 9 novembre 2026)

**Dépôt :** `Abrasax63/Omega-pub`  
**Branche source :** `migration/ravi2-ccs-public-2026-11-04`  
**Branche de publication :** `maintenance/reconciliation-bibliotheque-2026-11-05`  
**Périmètre :** dix revues/audits supplémentaires de couverture, certification, C4/L=2, complexité temporelle, traçabilité et graphe de conjectures.  
**Nature :** réconciliation documentaire. Les exécutions décrites ci-dessous sont celles rapportées dans les fichiers historiques ; elles n'ont pas été rejouées dans ce lot.

## 1. Fichiers examinés et empreintes Git

| Fichier | SHA Git source |
|---|---|
| `AUDIT_COUVERTURE_HISTORIQUE_2026-11-04.md` | `fafd08523bf48276dfe07c4ea17c01471d14caa5` |
| `AUDIT_FINAL_PR2_2026-11-04.md` | `2aca06785c94b609ed6f998a16bc7b0c38b6e959` |
| `AUDIT_SEMANTIQUE_C4_L2_2026-11-04.md` | `83f919f4eae7427fc8c767794ad18447712e3372` |
| `AUDIT_SINGLE_GAP_FACTOR_COMPLEXITY_2026-10-19.md` | `05200a99df13ebd91989251b6185e7c0af4ffe2b` |
| `AUDIT_TIME_PREDICTIVE_COMPLEXITY_2026-10-19.md` | `078552af23a4fa1ba5644c2e925af4ed2a22b954` |
| `AUDIT_TRACABILITE_32_RECONSTITUTIONS_2026-11-04.md` | `b09af559bb0f6cbd4de44c2fe3739de17c7ba2f3` |
| `AUDIT_TRACABILITE_SYNCHRONISATION_RAVI2_2026-10-27.md` | `8cea972bd8d4d08968e79c4a35ed991e20398aa3` |
| `CERTIFICAT_METHODE_RAVI2_SOURCE_2026-10-27.md` | `9806d39a1ea7f2a90d9e74810fc6955122299488` |
| `INVENTAIRE_SOURCES_32_CARTES_MANQUANTES_2026-11-04.md` | `c3d9812fe1101d256f05cd072c7bff9799a5e4f7` |
| `RAVI2_CONJECTURE_GRAPH_V01_AUDIT.md` | `b65135ff5f21ea8652bc323c1b38008af3492d8b` |

Les SHA sont les identifiants de blobs Git fournis par GitHub.

## 2. Couverture historique et migration

### AUDIT_COUVERTURE_HISTORIQUE

L'audit historique distingue correctement :
- 85 résultats admissibles dans SQLite v33 : 74 déclarés DÉMONTRÉ et 11 CALCUL EXACT ;
- 26 liaisons d'évidence explicites vers des cartes ;
- 17 correspondances par nom, relues ensuite sémantiquement, mais toujours sans lien explicite dans SQLite ;
- 42 résultats initialement sans carte individuelle, dont 10 cartes originales restaurées, laissant 32 originaux non retrouvés ;
- 32 fichiers de reconstitution, qui ne sont pas des originaux.

Il consigne également un écart non résolu entre 26 liaisons explicites, 25 preuves de type carte et 22 relations `INTERFACE_CARD`. Ces compteurs ne doivent pas être amalgamés.

L'audit documente trois chantiers Ω distincts :
- W07 : SUSPENDU / NON VÉRIFIÉ ;
- W08 : EMPIRIQUE ANTÉRIEUR / NON RÉAUDITÉ ;
- W09 : reproductibilité partielle / NO-GO, malgré 135 contrôles PASS rapportés.

Ces statuts ne sont pas des verdicts renouvelés dans le présent lot.

### AUDIT_FINAL_PR2

Le rapport de PR #2 relève des risques et limites de migration : historique Git volumineux et divergent, secrets contrôlés seulement lexicalement, scripts historiques susceptibles d'écrire dans SQLite, dépendance à des artefacts non tous inclus et workflow C5 encore en attente au snapshot audité. Le fait que GitHub ait indiqué `mergeable=true` ne signifiait pas que la fusion était recommandée.

Ce rapport historique ne décrit pas l'état GitHub actuel de la PR. Il justifie la politique de conservation : aucune fusion globale de la branche de migration et aucune exécution des anciens scripts d'écriture sur une base de travail.

## 3. C4/L=2 : résultat fort et divergence de statut à résoudre

### Ce que rapporte l'audit du 4 novembre

`AUDIT_SEMANTIQUE_C4_L2` affirme :
- égalités de couleur aux temps t=0 et t=1 comme convention correcte ;
- 1 515 diagrammes, 172 ombres propres et 8 classes locales ;
- un témoin global à 9 états réalisant les huit classes ;
- absence exhaustive pour N≤8 sur 4 481 fonctions ;
- une reconstruction du lemme de localité L+2 fondée sur la classification des composantes forcées P1–P4 ;
- contrôle fini de cette reconstruction sur 38 systèmes C4, 536 comparaisons et aucune divergence ;
- formalisation Lean et revue humaine tierce non réalisées ; originalité bibliographique indéterminée.

L'audit identifie aussi une dérive documentaire précise : deux rapports archivés formulaient à tort une inégalité de trajectoire, alors que la note primaire et les scripts corrects imposent l'égalité. La variante inégalité ne conserve qu'une ombre brute sur huit dans le contre-test rapporté.

### Réserve de réconciliation

Le statut de ce document ne peut pas être repris comme verdict courant sans confrontation à l'état de recherche plus récent. Le suivi de travail actuel garde P4 comme verrou à contrôler. L'audit du 4 novembre déclare au contraire la classification P1–P4 et le lemme L+2 démontrés sous ses hypothèses.

Cette divergence n'est pas résolue par la seule lecture du rapport. Il faut comparer ligne par ligne :
1. l'énoncé exact de P4 et ses hypothèses ;
2. la preuve reconstruite de la section 4.1 ;
3. les scripts et données qui soutiennent le contrôle fini ;
4. le point précis qui motive le maintien ultérieur de P4 comme verrou.

En attendant cet audit primaire, le présent rapport conserve les deux états comme provenance historique distincte. Il ne déclare ni P4 fermé ni l'audit du 4 novembre réfuté.

## 4. Complexité en facteurs et détecteur fini

### AUDIT_SINGLE_GAP_FACTOR_COMPLEXITY

Le document présente une généralisation du profil de complexité en facteurs d'un mot binaire cyclique ayant un seul gap exceptionnel. Il rapporte deux expériences :
- 3 773 familles et 253 330 quadruplets (g,h,k,L), sans échec ;
- 1 674 familles supplémentaires et 75 375 longueurs, avec classification directe des facteurs spéciaux, sans échec.

La preuve utilise les deux familles de facteurs spéciaux : le bloc (0^L) et le facteur périodique au raccord du défaut. Le rapport conclut à une généralisation non redondante en interne de `BR-TIME-FACTOR-COMPLEX-01`.

La recherche bibliographique ciblée n'ayant pas établi l'absence d'antériorité, l'originalité externe reste INDÉTERMINÉE. La recommandation historique de promotion n'est pas une promotion effectuée par ce lot.

### AUDIT_TIME_PREDICTIVE_COMPLEXITY

Le rapport distingue deux résultats :
- profil exact de complexité prédictive du mot cyclique de `BR-TIME-01), avec contrôles historiques sur 5 446 couples et 489 tests adversariaux ;
- pont vers `DET-FIN-01), sous une loi nulle à phase initiale uniforme et un critère de risque total strictement inférieur à 1, avec contrôles historiques de 280 941 probabilités conditionnelles et 70 440 préfixes.

Le rapport insiste sur le fait que le critère de détection utilisé n'est pas l'ARL classique et que le résultat ne démontre aucune flèche du temps. L'originalité bibliographique des deux énoncés est explicitement INDÉTERMINÉE. Les dépendances proposées sont `BR-TIME-FACTOR-COMPLEX-01 → BR-TIME-01`, puis `BR-TIME-FINDET-BRIDGE-01 → BR-TIME-FACTOR-COMPLEX-01` et `DET-FIN-01`.

## 5. Reconstitutions et provenance des sources

### AUDIT_TRACABILITE_32_RECONSTITUTIONS

Le contrôle confirme 32/32 fichiers dans `research/bricks/reconstructed/`, explicitement marqués « RECONSTITUTION — NON ORIGINALE ». Les statuts et références sont recopiés des sources historiques ; les tests et audits n'ont pas été rejoués lors de la reconstitution.

Les groupes Delta, Mealy, V19, restrictions, OpenAI/Brauer, quantique et Ω-O4.1 ont des réserves de portée propres. Les références de Library, les sources primaires, les scripts, les sorties et les archives ne sont pas interchangeables. Plusieurs fiches partagent les mêmes rapports et sorties : cela ne constitue pas autant de réplications indépendantes.

### INVENTAIRE_SOURCES_32_CARTES_MANQUANTES

L'inventaire rapporte une recherche sur 1 440 fichiers de Library, huit pages, plus inspection de sources et d'archives. Il identifie des rapports, manuscrits, scripts, CSV/JSON et archives de preuves pour plusieurs des 32 identifiants, sans retrouver de fichier individuel original pour eux.

Le complément de recherche élargie mentionne 1 501 éléments et ne trouve aucune carte originale supplémentaire au-delà des dix déjà restaurées. Cette différence de taille de Library correspond à deux instantanés de recherche distincts ; elle n'est pas, à elle seule, une contradiction.

### CERTIFICAT_METHODE_RAVI2_SOURCE

Ce document est explicitement un certificat de provenance documentaire : il localise `RESEARCH_METHOD_RAVI2.md` comme source de `METHOD-RAVI-2`. Il ne certifie ni l'efficacité générale de la méthode, ni les résultats qui l'utilisent. Il signale que le remplacement de la base dans la Library partagée n'était pas confirmé à la date de rédaction.

## 6. Synchronisation SQLite : versions distinctes, ne pas mélanger

`AUDIT_TRACABILITE_SYNCHRONISATION_RAVI2` porte sur SQLite v32 au 27 octobre et rapporte dix résultats sans ligne `result_sources`, dont neuf disposant déjà d'une entrée `evidence`. Les compteurs étaient 89 résultats, 85 admissibles, 216 evidence et 62 tests enregistrés PASS. Le graphe mémoire avait sept nœuds actifs, zéro lien et un snapshot de sept éléments.

Le certificat documentaire de `METHOD-RAVI-2` décrit une réparation de provenance locale ultérieure à cet état, mais précise que la mise à jour de la Library partagée n'était pas confirmée.

**Important :** ces constats v32 du 27 octobre ne doivent pas être présentés comme l'état de v33 du 4 novembre. L'audit de consolidation v33, lu dans un autre lot historique, rapporte ensuite zéro résultat sans liaison `result_sources`, 217 entrées evidence et huit liens mémoire. Ce changement est cohérent avec une évolution de version, pas une contradiction à effacer.

## 7. Graphe de conjectures : réfutation et séparation des couches

`RAVI2_CONJECTURE_GRAPH_V01_AUDIT` rapporte :
- une conjecture de monotonie universelle du spectre d'obstruction, réfutée par un système fini dont le spectre jusqu'à 12 est `{2,4,6,8,10,12}` ;
- un principe abstrait de résumé fini donnant une périodicité ultime, démontré dans le prototype interne et reconnu comme mécanisme classique lié aux langages réguliers ;
- deux expériences décisives au maximum par verrou ;
- un corollaire V19 de tailles minimales `{11,21,41,61,81,161}`, maintenu en staging, non éligible au commit scientifique dans cette passe.

La distinction est essentielle : `PROVED_INTERNAL` dans le graphe de recherche n'est pas le statut DÉMONTRÉ du noyau scientifique. Le résultat dérivé V19 reste en staging et son originalité n'est pas auditée. Le prototype est présenté comme infrastructure de triage/falsification, pas comme autorité de certification.

## 8. Contradictions et points à conserver

1. **P4 / L+2 :** statut historique du 4 novembre plus fort que le verrou maintenu ensuite ; audit primaire nécessaire.
2. **SQLite v32 / v33 :** les compteurs et liaisons diffèrent entre instantanés ; les dater et ne pas les fusionner.
3. **Reconstitution / original :** 32 reconstitutions documentées ne sont pas 32 originaux retrouvés.
4. **Contrôle fini / preuve générale :** les énumérations finies soutiennent les preuves, mais ne les remplacent pas.
5. **Découverte / certification :** score, attracteur et `PROVED_INTERNAL` ne créent ni théorème certifié ni dépendance scientifique.
6. **Originalité :** les recherches ciblées sans résultat exact laissent l'antériorité INDÉTERMINÉE.
7. **PR #2 :** état de la PR au snapshot historique seulement ; aucun conseil de fusion globale n'en découle.

## 9. Décision de réconciliation

- Conserver les statuts tels qu'ils sont datés dans chaque source.
- Ouvrir un audit adversarial ciblé P4/L+2 avant toute fermeture de ce verrou.
- Conserver les versions SQLite v32 et v33 comme instantanés distincts.
- Garder les 32 fiches dans `reconstructed/`.
- Ne pas promouvoir le corollaire V19 de staging.
- Ne pas transformer les résultats de découverte en dépendances.
- Ne modifier ni SQLite, ni `main`, ni les branches historiques.

## 10. Limites de ce lot

Aucun script, calcul exact, checker, notebook ou preuve Lean n'a été exécuté dans cette opération. Les volumes et résultats de calcul sont ceux consignés dans les audits historiques. Aucune base SQLite n'a été consultée ou modifiée pendant cette réconciliation. Aucune certification scientifique n'est renouvelée.

**Verdict :** dix documents réconciliés au niveau documentaire. Le point P4/L+2 est explicitement conservé comme divergence de statut à résoudre, et non arbitré par supposition.
