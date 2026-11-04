# Méthode scientifique Ω / RAVI-2

Version 2.0 — 14 octobre 2026.

1. Conserver la question brute.
2. Faire une cartographie bibliographique initiale courte : sources primaires, définitions standard, résultats connus, frontières et redondances probables.
3. Formaliser QUESTION, SCOPE, STOP, MODE, hypothèses et critères de réfutation.
4. Établir l’incumbent avec ses dépendances, limites, preuves et contradicteurs.
5. Ouvrir une branche semi-aveugle à la littérature détaillée.
6. Mener deux pistes indépendantes : preuve/construction et réfutation/contre-exemple.
7. Appliquer les barrières adversariales : cas minimaux et extrêmes, symétries, suppression d’hypothèses, invariance de représentation, théorème nul/redondance, généralisation.
8. Relier chaque affirmation à une preuve, un calcul exact, une expérience, des données ou du code vérifiable.
9. Faire une reconstruction indépendante ou aveugle.
10. Faire l’audit bibliographique final : antériorités, théorèmes plus généraux, contre-exemples, originalité.
11. En cas d’échec, appliquer le rollback causal et réexaminer les dépendants.
12. Certifier séparément statut épistémique, domaine, limites, provenance et originalité.
13. Commit mémoire versionné : ne jamais écraser silencieusement une ancienne brique.

Règles : une simulation n’est pas une preuve mathématique ; l’absence de contre-exemple n’est pas une preuve ; une sortie de modèle n’est pas une source ; une revendication d’originalité reste provisoire jusqu’à audit documentaire suffisant.

Règle de correction partielle : si un résultat reste valable après restriction de portée, changement d’hypothèses ou reclassement d’une relation, ne pas utiliser une réfutation totale. Produire un amendement versionné, conserver la formulation antérieure dans la provenance, reclasser explicitement les relations causales devenues seulement conceptuelles, puis relancer les tests de régression et l’analyse d’impact.


## Commit obligatoire — instruction utilisateur14octobre2026
Appliquer SCIENTIFIC_COMMIT_PROTOCOL.md : sources primaires avant promotion, archive intégrale des versions, séparation statuts, rollback causal restreint, contrôle de la base et des index, persistance avec garde de version, rematérialisation et comparaison des octets persistés.
Cycle : CHARGER → RECONSTRUIRE → COMPARER → DÉTECTER → AUDITER → FALSIFIER → COMMIT → PROPAGER → CONTRÔLER → PERSISTER → VÉRIFIER → SNAPSHOT.
Une sortie de modèle/snapshot ne certifie rien seule. Les audits internes ne valent pas validation externe.


## Amendement opérationnel — fermeture contrôlée des verrous (2026-10-16)
Référence normative : RAVI2_AMENDEMENT_FERMETURE_VERROUS_2026-10-16.md. Avant d'ouvrir une dépendance, valider NÉCESSITÉ, DISCRIMINATION et TESTABILITÉ. Deux expériences décisives maximum par verrou par défaut, sans réinitialisation par simple reformulation. À épuisement : CERTIFIÉ si certificat complet, RÉFUTÉ si contre-preuve, sinon INDÉTERMINÉ, avec conditions de réouverture. Archiver et changer de piste. Ne pas assimiler reconstruction locale conditionnelle et certification globale. Les tables lock_decisions et lock_experiments sont des instruments de suivi, pas un moteur autonome ni un vérificateur formel.