# OMEGA-EXACT-SEMANTIC-11 — PREUVE DE FAISABILITÉ POST-HOC SUR UNE SOURCE
Date : 17 novembre 2026. Extension expérimentale à la PR #166, **APRÈS échec de couverture du holdout original**; pas un second holdout indépendant, conserver les scores originaux 0/16 et le run #44156820382 intacts.

## Énoncés et source
Document identifié et étudié APRÈS l'expérience #166 : `09_INFRASTRUCTURE_AGENTIQUE/semantic_fidelity10/holdout/NOTE_RECHERCHE_V7_POLYNOME_TEMPOREL.md`, original public blob Git `6c482f97345abbb7f3d5bcd5e20da96259b276ce`.
Codimension : lignes 7–34 (X fini, T totale, L≥1, p={x,y}, arêtes E_{p,L}, sous-espace D_{p,L}(K)), lignes 57–92 (dim D = κ(Γ), codim D = N−κ = rang de l'incidence, codim ≤ min(L,N−1)).
Polynôme temporel : lignes 96–145 (χ_{T,L}(q) compte les π:X→[q] injectives en histoires L, et χ = Σ_{J⊆binom(X,2)} (−1)^{|J|} q^{κ(∪ E_{p,L})}).
Traduction en deux contrats JSON **explicitement manuelle**, avec hypothèses, conclusions, portée, ancrages cités et statut `HUMAN_TRANSCRIPTION_UNVERIFIED`; le rapport ne dira jamais que le parseur #166 a produit ces contrats.

## Tests exacts différenciés
Corpus exhaustif préenregistré pour chaque N∈{1,2,3,4}, chaque application totale T:X→X (N^N), chaque horizon L∈{1,2,3}, et chaque paire distincte p :
1. Construire Γ avec la trajectoire (oracle 1), calculer κ par union-find ; calculer rang de la matrice d'incidence par élimination modulaire indépendante sur F2 et F3 (oracle 2) ; vérifier codim N−κ = rang et ≤ min(L,N−1) ; compter exhaustivement les colorations admissibles sur F2 et F3 et comparer à q^κ (oracle 3).
2. Pour mêmes N,T,L et chaque q∈{1,2,3}, compter directement les observations injectives par brute force des q^N π (oracle A). Recalculer par inclusion-exclusion sur tous J⊆binom(X,2), avec un deuxième calcul de composantes à partir de chaque union d'arêtes (oracle B). Comparer exactement.
3. Tests de falsification : remplacer codim par nombre d'arêtes, supprimer les sommets isolés, prétendre χ=q^N ; exiger des contre-exemples minimaux précis. Aucune valeur simulée, aucun LLM, pas d'API.

## Succès, portée et échec
Succès local uniquement si égalités vérifiées sur TOUS les cas préenregistrés, dénombrement exact des essais, 3 fausses variantes rejetées par des contre-exemples, citations et blocs sources exacts, aucune erreur de calcul, CI verte. Un contre-exemple à l'énoncé réel = échec scientifique, pas correction forcée.
Les essais exhaustifs N≤4 ne constituent pas une preuve universelle, et la transcription des énoncés demeure le travail de l'assistant, **pas une extraction autonome**. Pour valider la fidélité du texte→règles, demander ultérieurement une seconde annotation indépendante. Le résultat est une faisabilité 'proposeur manuel + vérificateur exact', pas une réussite d'Omega sur le holdout.

## Intégration
Code v11 sous un nouveau sous-dossier indépendant, aucun changement au moteur #166, #164 ou à `main`. Rapports/artefacts JSON imprimés, statuts distincts `FINITE_EXACT_CHECK`, `UNVERIFIED_SEMANTIC_MAPPING`, `NOT_A_UNIVERSAL_PROOF`.
