# RAVI-2 — Amendement méthodologique : fermeture contrôlée des verrous
Date : 2026-10-16
Statut : ADOPTÉ COMME RÈGLE DE TRAVAIL ; efficacité empirique À ÉVALUER.

## Défaut observé
Déplacement récursif du verrou : une preuve locale renvoie à une nouvelle dépendance, puis à une autre, sans changement du verdict global. Les validations conditionnelles sont parfois présentées abusivement comme des certifications indépendantes.

## Contrat de décision
Au début de chaque investigation, fixer (a) l'énoncé et le domaine, (b) les quantificateurs et hypothèses, (c) le certificat minimal attendu, (d) les dépendances critiques, (e) le résultat incumbent et son statut.

Une nouvelle sous-dépendance n'ouvre une expérience que si les trois tests suivants sont positifs :
1. NÉCESSITÉ : la dépendance est effectivement requise pour le certificat visé.
2. DISCRIMINATION : sa résolution peut changer le verdict global ou invalider une prémisse essentielle.
3. TESTABILITÉ : une preuve indépendante, un contre-exemple calculable ou une source primaire contrôlable peut la trancher.

## Budget et arrêt
Par défaut, au plus deux nouvelles expériences décisives par verrou après sa définition. Les vérifications répétées ou simples reformulations ne comptent pas comme progrès et ne réinitialisent pas le budget. Un élargissement exige une justification explicite d'un gain discriminant exceptionnel, sans extension tacite.

À épuisement : verdict CERTIFIÉ uniquement si certificat complet vérifiable ; RÉFUTÉ si contre-exemple/preuve de contradiction ; sinon INDÉTERMINÉ. Archiver l'énoncé, le certificat partiel, les prémisses non fermées, le contre-test, les sources et la condition précise de réouverture. Passer à une autre piste.

## Discipline des statuts
DÉMONTRÉ / CALCUL EXACT : seulement pour l'énoncé exactement établi. LITTÉRATURE-VÉRIFIÉE : source primaire consultée, sans preuve indépendante. CORROBORÉ : contrôles partiels concordants. CONJECTURÉ, RÉFUTÉ, INDÉTERMINÉ et À RÉEXAMINER restent distincts. Aucun consensus multiagent ne remplace le certificat. Ne pas promouvoir une preuve conditionnelle en certification globale.

## Rôles contradictoires
Reconstructeur : produit le certificat minimal ; réfutateur : cherche le plus petit échec ; auditeur bibliographique : vérifie les sources ; auditeur de correspondance : confronte domaines, quantificateurs et constantes ; arbitre : tranche dans le budget imparti.

## Application immédiate : Navier–Stokes P55-B
Conserver les résultats locaux sur le cône positif, les covariances et Riccati ; ne pas réouvrir sans raison les dix briques déjà certifiées. Le certificat global P55-B reste INDÉTERMINÉ : les dérivées pondérées et leur transfert complet n'ont pas de reconstruction indépendante intégrale. Ne pas confondre les résultats locaux avec la certification de P55-B. Prochaine piste par défaut : P55-C, sauf expérience véritablement discriminante nouvelle.

## Suivi de performance
Mesurer par session : nombre de verrous réellement clos ; certificats indépendants ; réfutations ; nouvelles dépendances nécessaires ; itérations sans modification de verdict ; temps dépensé par verdict. Comparer sur plusieurs sessions à l'ancien protocole avant toute affirmation d'efficacité.

## Intégration
Cet amendement complète RAVI-2 sans remplacer les exigences de preuve, rollback, traçabilité et commit scientifique. Il ne certifie aucune nouvelle brique mathématique et ne modifie pas à lui seul les bases SQLite.