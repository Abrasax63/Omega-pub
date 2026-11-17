# OMEGA-11 — examen sémantique POST-HOC après le premier vrai run Qwen

Le run [44157203400](https://github.com/Abrasax63/Omega-pub/actions/runs/44157203400) a produit 12/12 propositions techniquement ancrées, 6/6 appels au modèle et **0 preuve scientifique**, avec choix gelés SHA256 `c888847cc11661252bc93fad25d0c47f92860a3396813963bd5b16d21d7d965a`.

**Cet examen est défini APRES lecture des sorties générées et ne doit PAS être décrit comme un nouveau holdout.** Deux idées visibles dans l'artefact original sont soumises à un contre-modèle logique :
- `FOLIO-062`, candidat `333202f3d7e3f4431e64c5c8d1931bdb` : proposition « Mike has an F1 visa ». Une affectation possible où Mike a le statut étudiant international, J1 et CPT mais pas F1 satisfait pourtant les quatre prémisses.
- `FOLIO-064`, candidat `990b22ec140acf9999e816f1cadd7ef4` : proposition « Ted cannot be a pet ». Une interprétation finie avec Ted alligator ET animal de compagnie, plus un autre individu qui est vache, bovin, domestiqué et animal de compagnie, satisfait les cinq prémisses.

Test : représenter les deux situations par un mini-langage prédicatif explicite (constantes, unaires, conjonction, disjonction, implication, négation, existentiel), vérifier **chaque prémisse** sur un modèle fini à 1 ou 2 éléments, puis vérifier la négation de la proposition erronée. Les traductions du texte anglais vers les clauses du mini-langage sont **saisies manuellement pour cet audit** ; elles ne prouvent pas que le traducteur d'Omega est capable de reconstruire leur sémantique.

Ne jamais présenter ce résultat comme une réfutation d'une preuve formelle (aucune n'avait été produite), comme une confirmation du niveau général d'Omega, ni comme une donnée indépendante pour le benchmark initial. Il s'agit de deux contre-modèles reproductibles à des **hypothèses du générateur**.

Le journal de génération original (12 pistes) reste disponible comme artefact GitHub ; une copie de contrôle, chaînée et compressée, pourra être conservée dans la branche expérimentale. Ce contrôle est distinct de l'entraînement des poids et des conclusions scientifiques certifiées.
