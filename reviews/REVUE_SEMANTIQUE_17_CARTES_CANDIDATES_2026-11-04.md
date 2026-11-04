# Revue sémantique des 17 cartes candidates — SQLite v33

Date : 4 novembre 2026  
Dépôt : `Abrasax63/Omega-pub`  
Branche : `migration/ravi2-ccs-public-2026-11-04`

## Objet

L'audit de réconciliation initial avait identifié 17 fichiers dont le nom commençait par un identifiant de résultat SQLite, sans liaison d'évidence explicite vers le fichier de carte correspondant. Cette revue vérifie si le contenu des cartes correspond effectivement aux enregistrements `results` de SQLite v33.

## Méthode

Pour chaque identifiant :
1. lecture de l'enregistrement SQLite v33 : titre, énoncé, domaine, hypothèses, statut et version ;
2. lecture du fichier Markdown correspondant dans la branche publique ;
3. comparaison du titre, du noyau de l'énoncé, des hypothèses de portée et du statut/version affichés ;
4. contrôle que le fichier est bien une fiche de résultat et non un rapport ou une note composite.

Aucune donnée SQLite, relation, source, statut scientifique ou version n'a été modifiée. Cette revue est une validation de correspondance documentaire, pas une nouvelle certification mathématique.

## Résultat

**17 correspondances sémantiques confirmées sur 17.**

| Identifiant SQLite | Fichier examiné | Résultat de comparaison |
|---|---|---|
| BR-OBS-BAD-01 | `research/bricks/BR-OBS-BAD-01_AFFINE_SIGNATURE.md` | Titre, RREF affine augmentée, hypothèses de non-vacuité et statut concordants |
| BR-OBS-CAP-01 | `research/bricks/BR-OBS-CAP-01_DYNAMIC_CAPACITY.md` | Définition de capacité, invariance et mécanismes de borne concordants |
| BR-OBS-CAP-02 | `research/bricks/BR-OBS-CAP-02_SUPPORT_VS_WEIGHT.md` | Distinction support/poids et inégalités de multiplicité concordantes |
| BR-OBS-CAP-03 | `research/bricks/BR-OBS-CAP-03_FIBER_BOX_TU.md` | Région produit des fibres et matrice d'incidence TU concordantes |
| BR-OBS-CIRCUIT-01 | `research/bricks/BR-OBS-CIRCUIT-01_2COVER_BIPARTITE.md` | Équivalence 2-recouvrement exact / bipartition concordante |
| NS-CERT-E-10 | `research/bricks/NS-CERT-E-10.md` | Énoncé de stabilité quantitative, hypothèses et limites concordants |
| NS-CERT-E-11 | `research/bricks/NS-CERT-E-11.md` | Sommation diagonale C∞ et hypothèses concordantes |
| NS-CERT-E-12 | `research/bricks/NS-CERT-E-12.md` | Identité de localisation solénoïdale et régularité concordantes |
| NS-CERT-E-13 | `research/bricks/NS-CERT-E-13.md` | Hypothèse de platitude de toutes les dérivées concordante |
| NS-CERT-E-14 | `research/bricks/NS-CERT-E-14.md` | Condition de moment nul et formule de l'inverse radial concordantes |
| NS-CERT-E-15 | `research/bricks/NS-CERT-E-15.md` | Condition de moyenne nulle et normalisation de la primitive concordantes |
| OBS-V19-BAD-FIBER2 | `research/bricks/OBS-V19-BAD-FIBER2_BRIQUE.md` | Fibre de taille au plus 2, paire-image et rectangle de préimages concordants |
| OBS-V19-C5-CAPACITY | `research/bricks/OBS-V19-C5-CAPACITY_BRIQUE.md` | Correction 85→70, spectre des capacités et orientation commune concordants |
| OBS-V19-COEX-REGION | `research/bricks/OBS-V19-COEX-REGION_BRIQUE.md` | Produit des capacités finies et orthant des capacités infinies concordants |
| OBS-V19-COEX-SMALLMODEL | `research/bricks/OBS-V19-COEX-SMALLMODEL_BRIQUE.md` | Borne de petit modèle et conservation des paires distinctes concordantes |
| OBS-V19-FIRST-OBSTRUCTION11 | `research/bricks/OBS-V19-FIRST-OBSTRUCTION11_BRIQUE.md` | Seuil k*=11 et capacités de classes orientées concordants |
| OBS-V19-N11-BADOBJECT | `research/bricks/OBS-V19-N11-BADOBJECT_BRIQUE.md` | Comptages 42,36,36,37,38 et hypothèses de reconstruction concordants |

## Réserve de provenance

La correspondance sémantique est confirmée, mais les liaisons d'évidence SQLite vers les fichiers Markdown individuels restent absentes pour ces 17 entrées. Les enregistrements SQLite référencent leurs preuves, audits ou scripts associés ; ils ne déclarent pas explicitement le fichier de carte de cette branche comme source. Aucune relation n'a été créée automatiquement, afin de ne pas transformer une comparaison de contenu en modification non auditée de la base.

La correction admissible est donc documentaire : le registre de migration peut désormais classer ces 17 fichiers comme **correspondances sémantiques confirmées**, tout en conservant la réserve **liaison SQLite explicite non réparée**.

## Verdict

- Correspondance sémantique : **17/17 confirmées**.
- Fichiers originaux de cartes : conservés tels qu'ils sont dans la branche ; aucune réécriture effectuée dans cette revue.
- SQLite v33 : lecture seule ; aucune modification.
- Statuts scientifiques : inchangés.
- Certification mathématique nouvelle : aucune.
