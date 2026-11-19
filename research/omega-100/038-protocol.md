# Protocole 038 — récupération locale après JSON ambigu

Figé le 19 novembre 2026 à 17 h 34 (Paris), avant inférence.

Hypothèse réfutable : après le refus d'un objet contenant une clé dupliquée, une reformulation qui nomme exactement le défaut augmente le nombre de réponses JSON uniques, conformes au schéma et fidèles aux citations, par rapport à une relance neutre du même modèle.

- Modèle réel local : Qwen2.5-Coder-3B-Instruct Q4_K_M, SHA-256 `724fb256bec1ff062b2f65e4569e871ad2e95ab2a3989723d1769c54294730b7`.
- Quatre cas synthétiques disjoints, deux tailles de source; l'objet ambigu et la vérité terrain exacte sont fixés dans le harnais.
- Référence d'abord : relance neutre. Candidat ensuite : même requête, mais message de diagnostic `duplicate key: source_blob` et instruction de garder une occurrence.
- Même modèle, température 0, graine 3801, une requête par cas et par bras, maximum 180 jetons de sortie.
- Oracle indépendant : parse JSON avec détection des doublons; clés exactes; `source_blob` exact; une claim; deux preuves exactement égales aux deux lignes sources avec rôles premise/conclusion; aucun texte hors JSON accepté par le parseur.
- Témoin négatif : une réponse syntaxiquement valide dont la conclusion invente un fragment doit être rejetée par l'oracle avant l'inférence.
- Succès : candidat strictement supérieur en réponses exactes, zéro citation inventée acceptée, et aucune régression sur un succès de référence. Sinon ne pas retenir de règle de reformulation.
- Budget d'arrêt : huit inférences, aucun réseau externe, aucun appel payant.
