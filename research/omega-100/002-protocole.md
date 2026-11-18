# 002 — Préenregistrement du correctif de fermeture

Hypothèse : une fermeture liée au délimiteur ouvert corrige le témoin 001 et les variants distincts, tout en préservant les références source et les verdicts du correctif #179.

Comparaison : même lecteur public #179 et même corpus, avant/après une correction expérimentale en copie temporaire. Réserve fixée ici : un bloc dollar sur cinq lignes contenant une ligne blanche, puis un titre ; deux blocs dollars autonomes séparés par un titre et du texte ; un bloc crochets, puis un titre et un bloc dollar ; des titres successifs avec un paragraphe sans formule. Pour chaque cas, relever le nombre de paquets mathématiques, la section de chaque paragraphe attendu et la précision des citations. Attendus pour le nombre de paquets mathématiques : 1, 2, 2, 0 respectivement. Les quatre témoins 001 servent de non-régression. Budget identique, aucun modèle.

Critère : tous les cas 001 et les quatre cas réservés passent sur le candidat, avec un gain strict sur la réserve. Les tests de calibration #179 et de sa protection de contexte doivent conserver leurs résultats métier ; le test de gel du blob est exécuté sur la référence. V8/DELTA sont des relectures historiques. Conserver le patch expérimental uniquement si ces critères passent. Les tests de contrôle des citations sont des relectures de structure, sans verdict mathématique.
