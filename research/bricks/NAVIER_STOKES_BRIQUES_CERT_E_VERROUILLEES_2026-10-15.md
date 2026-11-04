# Registre verrouillé — briques élémentaires Navier–Stokes

Date : 2026-10-15
Version : 1.1
Statut global : VERROUILLÉ — CERT-E / V-EL
Source d'audit : AUDIT_CERTIFICATION_NAVIER_STOKES_2026-10-15.md ; AUDIT_CORRESPONDANCE_NS_PROP55_LEIREN_2026-10-15.md

## Frontière de certification

Ce registre contient dix sous-briques autonomes dont l'énoncé a été reconstruit indépendamment sous hypothèses explicites. Leur verrouillage ne certifie ni les 26 cartes composites du dossier Navier–Stokes, ni le théorème principal de blow-up. Les résultats profonds restent LIT-TRACE / INDET jusqu'à audit indépendant.

## NS-CERT-E-01 à NS-CERT-E-09

Conserver sans modification les neuf briques certifiées de la version 1.0 : dérivée matérielle ; divergence cylindrique axisymétrique ; identité d'énergie forcée ; résidu inverse ; comptabilité anisotrope énergie/volume ; changement de viscosité ; comptabilité de Reynolds anisotrope ; moyenne nulle avec flux quadratique non nul ; monotonie de la coordonnée de similarité. Leurs hypothèses et limites restent celles de la version 1.0.

## NS-CERT-E-10 — Stabilité quantitative d'une contrainte admissible sous perturbation relative

Soit K un ensemble admissible décrit localement par une marge quantitative m(T)>0 telle que la distance à la frontière pertinente soit au moins m(T). Si T0 est admissible et si une perturbation ΔT satisfait

||ΔT|| <= ε m(T0), avec 0 <= ε < 1,

alors, sous la norme utilisée pour définir cette marge, T0+ΔT reste admissible et sa marge est au moins

m(T0+ΔT) >= (1-ε)m(T0) > 0.

Preuve : inégalité triangulaire / stabilité de la distance à un fermé sous perturbation. Pour une formulation par distance d(T, K^c), la fonction distance est 1-lipschitz.

Statut : CERT-E pour l'énoncé abstrait sous hypothèses explicites. Correspondance documentaire forte avec le mécanisme de contrôle relatif de Lei–Ren §17, mais cette correspondance ne certifie pas la Proposition 5.5 entière.

Limites : ne démontre pas l'existence de T0 avec marge ; ne démontre pas l'estimation relative dans une construction donnée ; ne réalise pas une contrainte par oscillations ; ne prouve pas l'équivalence exacte OpenAI ↔ Lei–Ren.

## Annotation de reprise — NE PAS REFAIRE

Déjà vérifié au 2026-10-15 :
- les neuf briques NS-CERT-E-01..09 ;
- le lemme abstrait de stabilité relative NS-CERT-E-10 ;
- correspondance structurelle forte entre OpenAI Prop. 5.5 et Lei–Ren §§15–17 ;
- existence chez Lei–Ren d'une estimation relative |T_B-T_0| <= C λ^(2δ)|T_0| conditionnée aux hypothèses de leur construction ;
- le simple contrôle absolu/pondéré n'est pas suffisant près des bords ;
- aucune identité terme à terme des profils OpenAI et Lei–Ren n'a été démontrée ; cette identité n'est pas nécessaire pour réutiliser NS-CERT-E-10.

## Reste à faire — ordre de priorité

1. **P55-A / marge d'entrée** : auditer Prop. 13.3 (13.31) → Assumption 13.1(v) → Lemma 17.1 → Prop. 17.2 chez Lei–Ren et vérifier que la marge est bien obtenue pour la famille construite, sans hypothèse circulaire.
2. **P55-B / quantificateurs de bord** : comparer exactement la platitude en λ sur |Z|<=1-ε avec la formulation OpenAI en q, η∈[-1,1] ; ne pas fusionner les quantificateurs.
3. **P55-C / cinq moments** : comparer les cinq contraintes de moments, les matrices de correction et leur rang uniforme ; établir ou réfuter une équivalence suffisante.
4. **P55-D / incompressibilité sous troncature** : écrire la preuve autonome du mécanisme de correction de commutateur déjà identifié comme candidat CERT-E.
5. **P75 / oscillations** : seulement après P55-A..D, auditer la réalisation oscillatoire de la contrainte (Prop. 7.5 ou analogue). Ne pas considérer cette étape comme couverte par Lei–Ren Part I.
6. Ensuite : Prop. 9.6 → Prop. 9.9 → Prop. 10.1 → Lemma 10.3, avec les annexes A–C selon dépendances.

### Marqueur de reprise

À la prochaine session, reprendre directement à **P55-A**. Ne pas recommencer la recherche générale sur les profils, l'estimation relative ou l'identité stricte des deux constructions sauf apparition d'une nouvelle source qui change l'état de preuve.

## Politique de réutilisation

NS-CERT-E-01..10 peuvent être réutilisées sous leurs hypothèses exactes. Toute généralisation ou utilisation pour certifier le blow-up exige un lien démontré séparément. Les cartes NS-01..NS-26 restent candidates/composites jusqu'à certification séparée.