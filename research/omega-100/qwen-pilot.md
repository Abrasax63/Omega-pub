# Pilote Qwen local avec le contrôle Omega 031

19 novembre 2026, 13 h 27 (Paris). **EXÉCUTÉ / hypothèse de gain RÉFUTÉE sur ce pilote.** Branche `experiment/omega-100-2026-11-18`, départ `bf04bece827b638fefd170fcb32d2d84fb0983b8`. Pilote demandé séparément de la séquence horaire, sans numéro d'expérience. Référence [031](031.md), dont le routeur et ses deux dépendances ont été vérifiés octet pour octet contre les fichiers du dépôt.

Le [protocole](qwen-pilot-protocole.md) a été écrit avant les cas et le lancement. Le critère était de corriger au moins deux erreurs, de préserver chaque réponse correcte et de ne produire aucune promotion universelle. Les huit obligations synthétiques inédites se répartissent en quatre couples où une condition ou la conclusion change. Le témoin négatif injecte une prémisse modifiée dans une réponse par ailleurs annotée. Le contrôle la rejette.

Qwen2.5-Coder-3B-Instruct Q4_K_M a généré un verdict et une traduction par cas. Le verdict déclaré sert de référence et le raccord 031 vérifie la traduction de cette même génération. Chaque bras utilise donc les mêmes jetons. Cette comparaison isole l'effet du contrôle après génération. Elle ne mesure pas un bras avec une invite qui ne demande que le verdict. Les annotations manuelles sont isolées de l'invite. Des prédicats Python indépendants énumèrent les 33 entiers de −16 à 16 et servent à vérifier les verdicts et les témoins. L'adaptateur remplit la localisation des citations depuis le contrat, donc la fidélité mesurée ici concerne les AST proposés.

| Bras | Corrects | Erreurs | Abstentions |
| --- | ---: | ---: | ---: |
| Verdict direct de Qwen | 1 | 5 | 2 |
| Même génération avec le contrôle Omega | 0 | 0 | 8 |
| Oracle alimenté par le contrat manuel | 8 | 0 | 0 |

Six traductions ont un nombre de prémisses différent du contrat. Deux sorties échouent au contrôle de format ou de verdict. Aucun cas ne parvient au calcul dans le bras Omega. Son absence de verdict erroné découle de l'abstention systématique. Le seul verdict direct correct est perdu. Aucun candidat n'est retenu. Les 16 tests métier de la passerelle passent. Le harnais publiable reproduit les 8 verdicts appariés sur les générations enregistrées lors d'un rejeu local, sans nouvelle génération. Le jeu réservé et les réponses restent hors du commit.

Budget effectivement utilisé : 8 appels locaux, 1 418 jetons d'entrée, 1 315 de sortie et 113,69 s d'inférence cumulée. Le décodage et le contrôle après génération prennent ensemble 0,26 ms pour ce lot, hors annotation humaine. Le plafond de sortie est fixé à 384 par appel. Aucune promotion universelle. Voir les [mesures agrégées](qwen-pilot-summary.json).

Reproduction avec Python standard et llama.cpp `5a4afd80779ba51166b59986e61a0bfbb9e1a4c6`. Le [GGUF](https://huggingface.co/Qwen/Qwen2.5-Coder-3B-Instruct-GGUF) a pour SHA-256 `724fb256bec1ff062b2f65e4569e871ad2e95ab2a3989723d1769c54294730b7`. Lancer `llama-server -m MODELE.gguf --host 127.0.0.1 --port 18722 -c 2048 -t 8 -np 1`. Copier dans un répertoire temporaire le [harnais](qwen-pilot.py), `031-route.py` sous le nom `route.py`, `030-source_ast_contract.py` sous `source_ast_contract.py` et `026-finite_oracle.py` sous `finite_oracle.py`. Exécuter `python qwen-pilot.py CAS_LOCAUX.py`, où `CASES` contient des quadruplets (prémisses texte/AST, conclusion texte/AST, prédicat indépendant de prémisse, prédicat indépendant de conclusion). Sorties par cas destinées à la copie temporaire avec le corpus. Température 0, graine 71, un seul appel par cas.

SHA-256 du préenregistrement `ceb57820d9f0bb453807804f72648a4011935a86eaf608671076aae68499dc74`, du relevé détaillé hors dépôt `f49004de8257ce215ea1f4694ad0343ce65bd95b359361caaf380e76207639a8`, du relevé agrégé `42ddb2f4d97505590cbec8f8f90423c91597cfc23045d30226dfdbba37a5938e`.

Prochain test décisif sur de nouvelles obligations annotées : donner aux prémisses et à la conclusion des identifiants explicites dans l'invite commune et imposer un schéma de réponse. Mesurer séparément le respect du format, la fidélité AST et le score exact. Ce pilote local sur un seul modèle et huit cas ne permet pas d'estimer les capacités générales d'Omega.
