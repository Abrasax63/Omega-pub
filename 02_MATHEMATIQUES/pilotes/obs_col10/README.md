# OBS-COL-10 — Première sélection réellement différente de sondes dans la chaîne Omega

**Date :** 16 novembre 2026. **Statut :** EXPÉRIENCE DE CALIBRATION EXÉCUTÉE ; gain Omega scientifique **NON DÉMONTRÉ**.
**Branche :** `experiment/obs-col10-probe-policy-divergence-2026-11-16`, basée sur la PR #96, **sans modification directe de `main`**.
**Pré-engagement avant code et exécution :** [PREREG.md](PREREG.md), commit `73963b67a35c13645c1a76d45106c9c3e3b27345`.

## Pourquoi ce pilote est différent de ce que nous avions déjà fait

Les travaux antérieurs avaient déjà établi un circuit de comparaison :
- PR #47 : holdout privé candidat, sans évaluation indépendante finale ;
- PR #55 : 96 sorties réelles mais **aucun gain d'adaptation propre** ;
- PR #92 : le planificateur PR23, et non P1 seul, choisissait la sonde parmi des hypothèses données ; même score que l'optimiseur exact ;
- PR #96 : vrais L* / KV / L# / TTT, EQ commun ; **P1 ajouté à L# produisait rigoureusement les mêmes sondes et prédictions** ;
- PR #105 et #108 : épreuves prospectives sur des **bogues logiciels**, domaine différent, sans certification aveugle externe.

Il manquait **dans le banc d'apprentissage d'automates** un mécanisme de décision qui change véritablement les requêtes d'un L# de référence. OBS-COL-10 réalise un **contrôle de divergence comportementale** sur le banc #96 avant toute nouvelle réserve.

## Trois politiques, règles gelées, mêmes modèles

Toutes utilisent le **vrai L# de AALpy 2.0.0**, les mêmes trois automates publics tiers épinglés, les mêmes 512 candidats EQ (avec SHA-256), mêmes 256 mots d'évaluation séparés par cible, sans cache extérieur et mêmes plafonds (10 000 resets, 50 000 symboles).

- **fixed** : ordre de sondes figé par le manifeste (#96).
- **coverage_only** : politique classique déterministe, sélection par couverture du graphe **hypothétique** et diversité de sortie prédite.
- **omega_candidate** : mêmes deux critères + nombre de préfixes de sondes EQ pas encore consultés ; **le vrai P1 valide chaque reset**. Les expériences sont sélectionnées par la **nouvelle politique écrite dans `policy_divergence.py`**, pas par P1 lui-même.

La politique ne reçoit jamais le graphe générateur vrai, son identité, ses réponses de test, ni les 256 mots réservés pour décider. La fonction `run_method` déjà existante est réutilisée via une **injection optionnelle d'oracle EQ**, avec son comportement par défaut inchangé ; aucun nouvel apprenant de type L#, TTT ou moteur agentique n'a été recréé.

**Cette politique est une heuristique classique définie par nous.** Lui donner le nom de « candidat Omega » n'en fait pas une intelligence originale.

## Exécution vérifiable

[GitHub Actions #43814246829 — SUCCESS](https://github.com/Abrasax63/Omega-pub/actions/runs/43814246829) sur commit `b1ef497fd0711e4a74e3691b15b181eb350dce30` : **5/5 tests**, trois politiques réellement exécutées sur trois machines, JSON d'observations publié dans [l'artefact #14201039854](https://github.com/Abrasax63/Omega-pub/actions/runs/43814246829/artifacts/14201039854).

**La nouvelle politique propose des sondes différentes sur les trois cibles** (3/3 divergences d'ordre dès la première requête d'équivalence). Ce point est technique et vérifié : à la différence de P1 seul, l'ensemble du dispositif modifie effectivement les décisions d'interrogation.

| Politique | Resets physiques, trois cibles | Symboles exécutés | Erreurs / 757 mots non vus |
|---|---:|---:|---:|
| fixed L# | 1 636 | 17 601 | 0 |
| coverage_only L# | 1 595 | 17 501 | 0 |
| omega_candidate L# + vrai P1 | **1 588** | **17 519** | 0 |

Sur cette calibration, `omega_candidate` réduit le nombre de resets de 48/1636 (−2,93 %) et les symboles de 82/17601 (−0,47 %) par rapport à **fixed**. Mais **par rapport au comparateur de couverture classique plus fort**, il économise seulement **7 resets** et consomme **18 symboles supplémentaires**. Les trois politiques ont zéro erreur sur les mots non vus.

Le temps CPU indicatif total de **trois cas sur un seul run** est approximativement :
- fixed : 0,029 s ;
- couverture classique : 0,066 s ;
- candidat Omega/P1 : 0,093 s.

Les temps CPU d'une seule CI ne constituent **pas** une évaluation statistique fiable ; ils indiquent néanmoins que le routage P1 et le classement adaptatif ne sont pas gratuits. Les 1 588 appels P1 ne modifient pas le nombre de sondes sélectionnées par l'heuristique elle-même.

### Échecs et contradictions à conserver

1. La politique neuve **n'est pas Pareto-dominante** de `coverage_only` : 7 resets de moins, mais **18 symboles de plus**. On ne peut donc pas déclarer « Omega est meilleur » même sur les trois machines.
2. Les cibles sont **les mêmes trois automates publics** déjà utilisés pour concevoir et calibrer le banc ; aucun jeu externe réellement aveugle n'a été consommé ici.
3. L'ensemble de 512 mots EQ est commun mais **l'ordre change** ; les mêmes coûts maximum n'impliquent pas les mêmes traces de requêtes.
4. Aucune comparaison nouvelle à TTT/L# sur de nouveaux modèles, aucune conclusion générale, aucun certificat universel : le résultat est une **divergence de politique techniquement mesurée**, pas un gain scientifique validé.
5. La dénomination `omega_candidate` ne suffit pas à établir l'origine intellectuelle d'une règle : couverture/novelty sont des heuristiques standard.

## Règle de décision actuelle

- Condition préalable à un holdout indépendant **satisfaite** : une nouvelle politique choisit réellement d'autres expériences.
- Condition de supériorité sur une baseline classique forte **NON SATISFAITE** : le coût total est mixte et les échantillons trop peu nombreux.
- Véritable corpus privé conçu et noté par un évaluateur extérieur **ABSENT / INDÉTERMINÉ**. Ne jamais appeler ce run « test aveugle externe ».

**Prochaine vérification réellement nouvelle :** confier le code déjà gelé à un évaluateur distinct et utiliser des automates jamais vus dans la conception, avec un SHA des jeux, les mêmes méthodes L#/TTT, répétitions, mêmes budgets et résultats rendus publics même s'ils sont négatifs. Jusqu'alors, ce pilote doit rester **DRAFT**. Ne pas fusionner, modifier `main`, CORE ou les autres PR.
