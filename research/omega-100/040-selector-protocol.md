# 040 — Sélection de preuves sur des fiches inédites

Référence de branche : cdeda3f0966de77e00243242ee711bb70855245c. Le test de sélection accepté par l'utilisateur prend la priorité sur la variation de la taille du JSON proposée en 039.

Question : à trois sélections maximum, Qwen2.5-Coder-3B-Instruct Q4_K_M retrouve-t-il davantage d'assertions pertinentes et exactes que la règle des trois premières lignes, avec au plus autant de faux positifs ?

Entrées figées avant les inférences : huit fiches synthétiques sur l'itération d'une application finie, avec six lignes candidates chacune. Les lignes pertinentes doivent répondre à la requête de la fiche et donner l'état exact. Les contrôles incluent des affirmations vraies mais hors sujet, des affirmations pertinentes fausses, et deux fiches où aucune ligne ne convient. L'oracle calcule les itérations par composition binaire, sans annotation du modèle. Deux contrôles unitaires testent la composition contre l'itération directe et vérifient le refus des identifiants hors liste et répétés.

Les deux bras voient les mêmes lignes et ont le même plafond de trois sélections. La règle prend les trois premières. Le 3B reçoit seulement l'application, la requête et les lignes numérotées. Une réponse valide est une liste d'identifiants distincts ou NONE. Le format et le choix sont évalués séparément. Pas de nouvelle tentative par fiche. Modèle épinglé au SHA-256 724fb256bec1ff062b2f65e4569e871ad2e95ab2a3989723d1769c54294730b7 et llama.cpp au commit 5a4afd80779ba51166b59986e61a0bfbb9e1a4c6. CPU local, température 0, graine 42, huit inférences au plus, 64 nouveaux tokens et 90 secondes au plus par fiche. Aucun réseau pour l'inférence.

Seuil du pilote : au moins deux vrais positifs de plus que la règle, pas de hausse des faux positifs, deux abstentions correctes sur les fiches sans réponse, et aucun rejet de format. Le temps d'inférence, les tokens et la latence de la règle sont relevés séparément. Mesurer le temps d'initialisation du serveur à part si disponible. Il s'agit d'un pilote de fidélité sur des systèmes finis synthétiques. Sa réussite déclencherait un essai sur des fiches naturelles indépendantes.
