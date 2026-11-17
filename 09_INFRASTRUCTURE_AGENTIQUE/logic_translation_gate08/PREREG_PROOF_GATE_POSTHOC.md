# OMEGA-PROOF-GATE-09 — correctif post-hoc, test de sécurité et non un nouveau holdout
Date 2026-11-17. Base PR #163, commit `61cbbac05b591b7470f974a21cc419e612240b4b`. PR brouillon empilée, main intacte.

## Défaut
Le run intact #44153288183 révèle 4 propositions syntaxiques extraites de `## Preuve` dans BR-ACC-STATE-COMMUTE-01. Bien qu'aucune ne soit promue, leur contexte de preuve peut être trompeur pour un lecteur ou un importeur futur. La barrière actuelle bloque `Non-théorème` et `Limites` mais pas une section intitulée simplement `Preuve`.

## Correction minimale prévue
Ajouter l'expression `^preuve` à la liste des titres de sections à traiter comme impropres à la création de propositions autonomes. Enregistrer ces formules comme `blocked` avec la raison `RELATION_IN_NON_THEOREM_OR_LIMIT` (générique, couvre désormais section de preuve), sans modifier les citations originales, le schéma de typage ni aucune source.

## Critères post-hoc
Contrôle explicite : aucune proposition autonome lorsque la section s'appelle `Preuve`, `Non-théorème`, `Limites`; les éléments sont présents dans `blocked` avec provenance. Préserver la définition et les égalités venant de `## Énoncé`, ne pas effacer les distinctions formelles; vérifier l'absence d'export Horn, absence de citation inventée, SHA historiques et tests antérieurs hors holdout. Évaluer en *replay post-hoc* sur exactement les deux anciennes fiches, sans en faire un nouveau holdout.

Le nombre de propositions repérées peut diminuer ; cela représente un renforcement de la prudence, pas un progrès de compréhension. Gold de PR #163 et rapports du run original conservés. Pas de fusion ni activation dans l'agent autonome.