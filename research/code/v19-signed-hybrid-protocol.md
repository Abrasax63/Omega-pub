# Pré-enregistrement — quotient signé seulement après filtre non signé

19 novembre 2026, 18 h 07 (Paris), avant exécution (mtime local conservé).

La définition source relue de l'ombre exige une extension à une coloration globalement cohérente. Le projecteur exhaustif reste donc l'oracle.

Question réfutable : un candidat à deux étages — quotient non signé, puis potentiels signés uniquement pour les requêtes survivantes — conserve-t-il exactement le verdict des noyaux minimaux à quatre événements tout en réduisant strictement le temps et les projections de la référence fixe ?

- Référence fixe : `priority(case)==0`, puis cinq projections exhaustives `certify` sur chaque survivant.
- Candidat : construit une fois le quotient non signé; abstient/rejette les non-cycles; calcule les potentiels signés seulement sur les survivants, sans projection.
- Oracle indépendant : cinq projections exhaustives sur toutes les requêtes.
- Contrôles : C4 pur négatif; témoin à cinq états positif; garde global sur le témoin et la famille C5 déjà gelée.
- Réserves nouvelles : C6 avec deux états libres (`n=8,q=6`) et C4 disjoint d'un C3 avec un état libre. Elles sont distinctes des campagnes `n=7,q=5`, `n=7,q=6`, `n=8,q=5` et C4+C2+deux libres.
- Succès : zéro erreur candidat et référence, zéro perte sur les contrôles, strictement moins de projections, temps candidat strictement inférieur sur chacune des deux réserves. Échec si une condition manque.
- Budget : au plus 30 secondes par campagne; aucune modification des jeux gelés.
