# 039 — Protocole : coût bout en bout du garde de doublons

Préenregistré le 19 novembre 2026 à 21 h 25 (Paris), avant exécution.

- Hypothèse falsifiable : sur trois documents locaux distincts d'environ 1, 16 et 64 Kio, le décodage strict ajouté en 037 conserve une sortie bout en bout exactement identique et ajoute moins de 15 % au temps médian total `decode + read + gate` pour chaque taille.
- Référence : `json.loads`, puis le pipeline `reader_bridge12` épinglé à `def8bac9fdafd81422d40c4c45ac3652a6d47e35`.
- Candidat : `json_intake.decode` du patch 037, puis le même pipeline.
- Oracle indépendant : égalité JSON exacte des résultats complets référence/candidat.
- Témoin négatif : doublon de clé `source_blob`; la référence l'accepte et le candidat doit le refuser avant le pipeline.
- Budget : 100 appels de référence puis 100 appels candidats par document, 600 appels maximum, aucun modèle et aucun réseau.
- Succès : 3/3 égalités, 1/1 doublon refusé et surcoût < 15 % sur chaque taille.
- Échec : toute divergence, doublon accepté ou seuil dépassé. Aucun changement du lecteur n'est autorisé par cet essai.

