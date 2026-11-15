# OBS-COL-09B — Pré-enregistrement de consolidation du benchmark
Date : 15 novembre 2026. Branche `experiment/obs-col09-common-eq-2026-11-15`, dérivée de PR #95.
**Ce document précède toute écriture de la nouvelle implantation EQ.** L'historique OBS-COL-09 n'est pas modifié.

## Question et critère de falsification

Comparer sur **exactement les mêmes automates et mêmes sondes proposées par l'oracle d'équivalence** :
- AALpy 2.0.0 : véritable L*, KV et L# ;
- AALpy L# + vrai pont Omega P1 : planification de chaque reset, **aucun choix autonome** ;
- LearnLib 0.18.0 : véritable TTT Moore Java.

Il faut pouvoir affirmer « même protocole d'EQ proposé » grâce à un **manifeste déterministe commun indépendant des sorties**, même si les modèles intermédiaires de chaque apprenant sont différents et donc les contre-exemples et nombres de tests effectivement exécutés divergent. Le protocole ne mesure pas la supériorité propre à Omega, seulement une baseline technique consolidée.

## Manifestes pré-engagés

Trois cibles tierces, mêmes fichiers `.dot` épinglés par empreintes que la PR #95. Pour chaque cible, alphabet trié lexicographiquement **après conversion en chaînes de caractères** :
- liste des mots de longueur 1..4, ordre longueur puis lexicographique (30 mots pour alphabet binaire) ;
- compléter jusqu'à **512 mots uniques** par un générateur `random.Random(20261117 + index_du_modèle)`, tirage d'une longueur entière uniforme 5..18 puis des symboles uniformes, **dans l'ordre d'apparition** ; aucune consultation de la cible ni du modèle apprenant ;
- enregistrer dans `*.eq.words` (format TSV, un mot/ligne) et la somme SHA-256 des octets.

À **chaque demande d'équivalence**, proposer ces 512 mots depuis le début dans le même ordre, effectuer reset + séquence, interrompre au **premier préfixe** dont la sortie diffère entre l'automate appris et le vrai système. Le tableau de transitions de la cible ne doit jamais être donné à l'apprenant ou au planificateur. S'il n'y a aucun contre-exemple dans cette suite finie, conclure seulement `NO_COUNTEREXAMPLE_IN_SUITE`, pas `CERTIFIED_EQUIVALENT`. Pas d'oracle d'équivalence parfait, pas d'utilisation d'un nombre d'états cachés.

Évaluation finale : réutiliser **les mêmes 256 mots de longueur 12..18** que la PR #95, générés depuis une autre graine `20261116+index`. Ne pas y accéder pour choisir les expériences. Marquer et exclure du score `unseen` ceux dont le mot complet figure parmi les préfixes physiquement observés, chez Python comme chez Java. Un mot ne doit pas être exclu sur la base de son erreur de prédiction.

## Équité, coûts et exclusions

- Plafonds identiques : 10 000 resets, 50 000 symboles réels (apprentissage + sondes EQ) ; si plafond atteint, `BUDGET_EXHAUSTED`, pas de faux succès. 40 itérations au plus ; arrivée au plafond d'itérations doit être signalée, pas présentée comme preuve de convergence.
- Reporter coût total resets / symboles, temps CPU / horloge (comparaison CPU Java/Python délicate), nombre de tests EQ réellement exécutés et cycles de contre-exemples.
- La liste de propositions EQ est identique, mais les **consultations physiques effectivement exécutées** peuvent différer entre algorithmes ; ce ne sont pas des réplications du même apprentissage.
- Contrôler l'empreinte SHA-256 du manifeste dans les deux langages, présence des 512 mots, et concordance des 256 mots de test. Vérifier sans supposer les coûts égaux.
- Test d'ablation : véritable L# vs véritable L# + P1, même traces, mêmes coûts physiques et modèle appris. Mesurer en supplément le coût de la validation P1.
- **Pas de conclusion générale de supériorité** sur seulement trois cibles publiques, pas de « nouvel algorithme TTT », pas de découverte scientifique, pas de certification universelle, pas d'agent autonome.

## Statuts et gouvernance

`PROPOSÉ` tant que le code n'est pas créé ; `IMPLÉMENTÉ` pour code présent ; `EXÉCUTÉ` lorsque la CI exécute vraiment les cinq bras ; `VÉRIFIÉ` uniquement pour les résultats étayés par logs et artefacts du même SHA de commit ; `INDÉTERMINÉ` en cas d'échec, d'équivalence non prouvée ou de test incomplet.

Conserver l'ancienne PR #95 inchangée, nouvelle PR DRAFT empilée, aucun changement direct de `main`, aucune promotion CORE ni fusion.
