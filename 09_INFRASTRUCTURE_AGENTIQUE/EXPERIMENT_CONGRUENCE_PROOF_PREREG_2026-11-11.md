# OMEGA-CONG-001 — pré-enregistrement : test de congruence, révision des preuves et maintien de la cohérence

**Date : 2026-11-11. Cas gelés avant code et résultats au commit `7d6185185f3deddef95553d7af1dead31ef3c88b`.**

## Question centrale

Quand des hypothèses modulaires deviennent incompatibles, sont retirées ou remplacées, Omega sait-il 1) éviter les conclusions obtenues par explosion logique, 2) conserver les voies de démonstration alternatives valides, 3) produire un certificat mathématique vérifiable et 4) historiser les anciennes justifications sans les affirmer actuelles ?

**Statut : expérience synthétique de cohérence/provenance, pas une évaluation sur nouvelles recherches scientifiques indépendantes.**

## Domaine mathématique gelé

Une variable entière x. Chaque prémisse est `x ≡ r (mod m)` avec m diviseur de 60 ; toutes les résidues de solutions distinctes s'observent donc exactement dans `U = {0,...,59}`.

Les 4 scénarios sont gelés dans `prism/congruence_revision_cases_v01.json` :
- `CONG-A-alternative` (calibration) : deux preuves possibles puis retrait d'une prémisse ;
- `CONG-B-conflict` (calibration) : contradictions, rétractations et réactivation ;
- `CONG-C-multi-moduli` (test) : moduli 3/4/5/20/30/60 et dépendances alternatives ;
- `CONG-D-contradictory-revisions` (test) : prémisses de parité contradictoires et changement de source.

Chaque scénario inclut les prémisses possibles, les requêtes et la liste complète des événements `activate/retract`, sans étiquettes pré-répondues. L'état initial est évalué, puis chaque transition : **50 états**, dont **26 états test**. Il est interdit d'adapter les règles après découverte de leurs résultats.

## Trois voies d'évaluation distinctes

1. **Oracle fini indépendant** : énumérer les 60 entiers U, filtrer les x compatibles avec toutes les prémisses actives, vérifier pour chaque requête si elle est universellement vraie, toujours fausse ou indéterminée ; si aucune solution des prémisses, déclarer uniquement `inconsistent_environment`, jamais une proposition déduite par explosion.
2. **Baseline forte ATMS par labels finis** : à partir des mêmes prémisses possibles, pré-calculer les ensembles minimaux de justifications de taille <=3 via **intersections exactes d'ensembles de solutions** et maintenir les justifications activées ; tester aussi la cohérence globale des prémisses actives. Les preuves alternatives doivent survivre aux rétractations.
3. **Omega — registre symbolique de certificats** : établir des justifications mathématiques par CRT/gcd, vérifier leurs conclusions modulo q, et enregistrer chaque preuve avec l'identifiant d'état et l'ensemble précis des prémisses. Les réfutations font appel à `gcd` et à un témoin d'impossibilité. Un certificat mathématique est conservé historiquement mais est **inapplicable au nouvel état** dès que ses prémisses ne sont plus actives. Les contenus de prémisses sont fixés ; une source qui change de contenu est représentée par rétractation puis activation d'une nouvelle prémisse.

ATMS et Omega voient la même liste de prémisses, les mêmes requêtes et les mêmes événements. Ils n'utilisent **aucun oracle extérieur aux prémisses** et ne reçoivent pas les réponses de l'oracle avant leur prédiction. Les deux voies déclaratives doivent être évaluées contre l'oracle exhaustif après décision.

## Statuts fixés

- `entailed` : au moins une justification active, cohérente et vérifiée implique la requête ;
- `refuted` : au moins une justification cohérente exclut la requête ;
- `undetermined` : l'environnement est cohérent, mais la requête n'est ni impliquée ni exclue ;
- `inconsistent_environment` : les prémisses actives sont incompatibles ; toutes les réponses globales doivent être suspendues jusqu'à révision. Des justifications locales peuvent rester archivées, mais ne sont pas présentées comme preuves globales.

Une justification `S` est valide si `S` possède une solution et si **toutes** ses solutions impliquent/excluent la requête. Les justifications gardées sont minimales pour l'inclusion (on rejette les sous-ensembles redondants). Pour des congruences dont les moduli divisent 60, au plus 3 prémisses (une puissance pertinente pour chacun des facteurs premiers 2/3/5) suffisent à décrire une intersection de contraintes. Cette borne doit être **revérifiée empiriquement sur tous les états et toutes les requêtes par l'oracle exhaustif** et ne sera pas présentée comme un théorème général en dehors de cette famille.

Une contradiction minimale existe déjà dans une paire de congruences incompatibles selon `gcd(m,n)`, ou doit être signalée comme erreur d'implémentation. Toute preuve utilisant une prémisse inactive, tout faux digest, tout résultat mathématiquement incorrect, ou toute conclusion affirmative en environnement contradictoire doit être rejeté.

## Mesures et comparaisons

Pour chacun des 50 états et chaque requête : verdicts oracle/ATMS/Omega, erreurs, abstentions, contradictions détectées, nombre de justifications alternatives valides et antérieures enregistrées, sorties de certificats, conservation après rétractation et nombre de calculs d'une fonction de congruence.

**Comparaison principale : même exactitude de vérité pour ATMS vs Omega.** Un gain propre à Omega n'existe que s'il est établi au-delà d'ATMS sur une métrique comparable ; aucun gain n'est présupposé. Le coût symbolique de CRT et l'énumération ne sont **pas** des coûts monétaires ni des secondes/tokens mesurés. Le scénario est construit et les vérités sont déterministes, donc la généralisation au raisonnement scientifique en langage naturel est **indéterminée**.

## Contre-tests obligatoires

- deux supports indépendants pour une même conclusion, puis rétractation de l'un : conclusion toujours démontrée si l'autre est actif ;
- conflit explicite `x≡0 (mod 2)` et `x≡1 (mod 2)`, puis rétraction : aucune conclusion globale pendant la contradiction ;
- contradiction de sources ne doit pas effacer les certificats applicables à une version antérieure ;
- réfutation différente d'une absence de preuve et de l'incompatibilité de l'environnement ;
- preuve forgée d'une requête non impliquée, preuve issue d'une prémisse inactive et preuve d'un ensemble incohérent : refus ;
- vérification séparée par énumération x=0..59 (deuxième voie, pas la fonction CRT) de chaque preuve émise ;
- réordonner les prémisses sans changer les résultats ni les justifications ;
- refus de moduli invalides / identifiants d'événements inconnus.

Les conclusions permises sont **sur des contraintes modulaires finies**, pas sur la supériorité d'Omega, l'authenticité des sources ou une capacité de mathématique générale. PR DRAFT empilée sur #42. Pas de fusion main, pas d'écriture SQLite/CORE.