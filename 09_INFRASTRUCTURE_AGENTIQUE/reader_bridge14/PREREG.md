# OMEGA-LINE-SELECTOR14 — protocole pré-implémentation, 19 novembre 2026

## Constat et falsification
Le pilote réel Reader13 réparé (PR #182, runs [44471617247](https://github.com/Abrasax63/Omega-pub/actions/runs/44471617247) et [44471667101](https://github.com/Abrasax63/Omega-pub/actions/runs/44471667101)) réalise deux inférences réelles par run mais les deux réponses sont rejetées par le parseur JSON. Les textes sortis contiennent des fences Markdown et des exemples inventés dont le numéro de ligne 999. Zéro conclusion LLM n'est acceptée ; la baseline mécanique fait 8 conclusions acceptées dont 3 faux positifs selon des annotations non indépendantes.

## Question unique
La substitution d'un **classement de numéros de lignes de conclusions** à la copie de citations en JSON améliore-t-elle la sélection de conclusions par Qwen2.5-0.5B dans cette *calibration post-hoc* sans permettre la fabrication de citations ?

## Protocole verrouillé
- Base : PR #182, SHA `fa6f9d62f636e59718e46fc6aec2a508ff9a419b`.
- Deux fiches identiques à Reader13, même sélection des paquets, mêmes blobs et mêmes annotations provisoires : BR-R90-01 (`478ca7c518ed1368a0bf35deb5f9be160bba581d`) et BR-R90-02 (`0a9f6bab0b91a93f8fcc831c39a988171c169eb5`).
- Les candidats proposés au modèle sont **exactement** les lignes de conclusion déjà admises par le témoin mécanique et le gate de Reader13. Il ne peut donc pas découvrir une nouvelle conclusion ni augmenter le rappel hors de cette liste.
- Modèle **inchangé**, épinglé : `Qwen/Qwen2.5-0.5B-Instruct` au SHA `c89bee90d9f811437d9735454613c35b4a3c4dc8`. Un seul appel par fiche, décodage glouton, sortie limitée à 64 jetons ; aucun outil externe.
- Le modèle reçoit les lignes candidates sourcées et retourne une liste de 0 à 3 numéros (séparés par virgules), ou `NONE` ; aucune citation littérale générée.
- Le code refuse **toute** sortie qui n'est pas exclusivement une liste entière strictement valide et unique d'IDs proposés. Pas de conversion permissive, de regex salvage ou d'auto-correction post hoc.
- Citations et `packet_id` reconstruits depuis le Git blob immuable seulement **après** validation de la sélection ; gate indépendant inchangé ; toutes les propositions restent en quarantaine.
- Références : baseline `select all`, baseline `first 3` sur le même jeu candidat, Qwen, abstention constante. Comparaison de précision/rappel sur lignes visibles uniquement ; ne comparer que les métriques dont le dénominateur est défini.
- Afficher sortie brute, succès parsing, nombre de sélections invalides, numéros validés, nombre de conclusions acceptées, faux positifs, précision/rappel, coûts en jetons et secondes.
- Contrôles : valeur `999` hors ensemble, lignes dupliquées, markdown, prose additionnelle, sélection vide, séparation par virgule, limite à trois, sans candidats, test gate empêchant modification de source, aucune règle Horn ni promotion.

## Interprétation imposée
Ce pilote **réutilise les deux mêmes documents**, connus après le test négatif Reader13. Le résultat est `POSTHOC_CALIBRATION`, jamais un holdout neuf ni un gain scientifique général. Le classement ne mesure **que** le choix parmi des citations déjà extraites par la baseline ; il ne valide pas la compréhension mathématique, n'apprend pas les poids et ne certifie aucun théorème. Une amélioration ne peut être revendiquée qu'avec une nouvelle cohorte externe, aveugle, scorée indépendamment et à budget comparé.

## Critère
Faisabilité : les tests et deux inférences terminent, aucun ID non proposé n'atteint le gate, au moins une liste sélectionnée valide et non vide. Succès local du classifieur : précision au moins égale à la baseline `first 3`, rappel non nul, absence d'erreur affirmée sur la cohorte (selon gold non indépendant). Si échec, rapporter l'échec sans retoucher les documents et sans promouvoir.