# OMEGA-READER12-REPAIR — correctif post-hoc de la preuve incluse dans une phrase
2026-11-17. Base PR #177, SHA `edb87ecfb0bf12227038336b8c8f699564d21c86`. Ne modifie ni le premier run holdout #44176403514 ni les fichiers Markdown figés. PR DRAFT empilée, main inchangée.

## Défaut reproduit
Le premier holdout sur BR DELTA (blob `0d449a5911b7364d03b5557b24afc3dfc6eef292`) permet d'ajouter comme conclusion candidate une phrase qui commence par `Preuve : si ...` (ligne 56), car l'en-tête de section est `## 6. Théorème fini et coût` et le gate ne contrôle pas les mentions de preuve en prose. L'élément est resté en quarantaine, aucune règle n'a été promue.

## Patch minimal
Le gate doit **refuser pour prémisse ou conclusion** toute citation appartenant à une ligne présentant explicitement une preuve (`Preuve`, `Démonstration`, `Proof`) ou une réfutation/contre-exemple explicite. Les preuves doivent rester consultables dans la lecture brute (`read.py` inchangé), et les citations de théorèmes autonomes sans ces marqueurs doivent toujours être admises seulement en quarantaine.

## Tests post-hoc
Rejouer les deux sources déjà vues sans les qualifier de nouvelles. Vérifier rejet de la citation 56, autorisation du cas de calibration V7 au statut QUARANTINE, 0 inférence ou publication automatique, tests d'intégrité des lignes et des sources, 0 appel LLM. Tous les tests doivent passer ; si la correction fait perdre des propositions, le signaler. Ne pas supposer le sens des hypothèses hors d'un examen indépendant.

Prochaine étape scientifique non incluse : vrai modèle local exécuté + gold externe sur fiches réellement inédites ; les tests de ce correctif ne représentent pas un succès de compréhension.
