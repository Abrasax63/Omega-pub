# BR-ACC-STATE-COMMUTE-01 — Accessibilité et quotient prédictif commutent

**Statut visé :** DÉMONTRÉ interne.  
**Originalité externe :** CONNU_OU_CLASSIQUE.

## Domaine
Système fini déterministe total muni d’un ensemble d’actions `A`, d’une observation fixe `π:X→Y` et d’un ensemble initial non vide `E⊆X`.

## Énoncé
Définir l’équivalence prédictive canonique

`x≈x'  <=>  π(T_u x)=π(T_u x')` pour tout mot d’actions `u∈A*`,

et le quotient `q:X→X/≈`. Poser `H=Reach_T(E)` et `Hbar=Reach_Tbar(q(E))` dans le quotient. Alors :

1. `q(H)=Hbar` ;
2. l’équivalence prédictive calculée dans le sous-système accessible `H` est exactement `≈|_H` ;
3. `q|_H` induit un isomorphisme canonique `H/(≈|_H) ≅ Hbar`.

Autrement dit, sur ce domaine déterministe, **fermer par accessibilité puis quotienter prédictivement** donne le même système que **quotienter prédictivement puis prendre la partie accessible**.

## Preuve
La définition de `≈` implique sa stabilité par chaque action : si `x≈x'`, alors pour tout `a` et tout mot `u`, `π(T_u T_a x)=π(T_{au}x)=π(T_{au}x')=π(T_u T_a x')`. Le quotient est donc bien défini et `q∘T_a=Tbar_a∘q`. Par induction sur les mots, `q(T_u e)=Tbar_u(q(e))`; l’union sur `e∈E` et `u∈A*` donne `q(H)=Hbar`.

Comme `H` est stable vers l’avant, toutes les continuations d’un état de `H` restent dans `H`. Deux états de `H` ont donc les mêmes réponses futures dans le système global si et seulement s’ils les ont dans le sous-système `H`. Ainsi l’équivalence prédictive interne à `H` est exactement `≈|_H`. Le troisième point suit du premier théorème d’isomorphisme pour le quotient ensembliste compatible aux actions et à l’observation.

## Validation indépendante
Le checker `ACCESS_PREDICTIVE_BRIDGE_CHECK.json` rapporte :
- 41 018 cas exhaustifs pour `n≤3`, deux actions, observation binaire et tous les ensembles initiaux non vides ;
- 20 000 cas aléatoires pour `n=4..8`, une à trois actions et observations à deux ou trois symboles ;
- zéro violation.

## Dépendances / interfaces
- `BR-ACC-01` : référence de définition pour la clôture accessible ;
- `BR-STATE-01` : référence de définition/théorème pour l’équivalence prédictive canonique et sa stabilité.

Ces références sont classées `DEFINITION_REFERENCE` dans la couche stricte ; la preuve ci-dessus est autonome et ne revendique pas une nouvelle composition générale.

## Limites
Le contrat certifié reste dans le cadre déterministe total et observation fixe. Aucune extension automatique aux systèmes partiels, stochastiques, quantiques ou aux politiques à mémoire infinie n’est revendiquée.

## Originalité
Le mécanisme est classique en minimisation d’automates/coalgebras : la littérature décrit explicitement l’interaction entre suppression des états inaccessibles et quotient par équivalence comportementale, y compris la possibilité d’effectuer les deux opérations dans l’un ou l’autre ordre sous les hypothèses appropriées. Aucune priorité n’est revendiquée.