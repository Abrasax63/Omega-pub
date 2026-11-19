# Repli pré-enregistré 038 — coût selon la taille

Figé le 19 novembre 2026 à 17 h 39 (Paris), après l'expiration à 90 s de la première inférence locale et avant ce test de repli. La tentative modèle n'a produit aucun bras complet et ne sera pas comptée comme gain.

Question : le contrôle d'unicité de 037 garde-t-il son gain sur trois tailles distinctes sans dépasser 15 % de surcoût médian sur JSON valide ?

- Tailles cibles : environ 1, 16 et 64 Kio; 100 décodages chronométrés par taille et par bras, référence d'abord.
- Référence : `json.loads`; candidat : `json_intake.decode` du patch 037.
- Contrôle positif : JSON valide, égalité structurelle exacte.
- Contrôle négatif : même charge avec `source_blob` dupliqué; la référence doit l'accepter silencieusement et le candidat doit refuser 100/100.
- Succès : 300/300 valides préservés, 300/300 doublons refusés, surcoût médian <=15 % à chaque taille. Toute taille au-dessus du seuil réfute la conservation sans condition.
- Aucun modèle, réseau ou API; coût borné à 1 200 décodages.
