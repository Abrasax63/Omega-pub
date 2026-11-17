# BR-STATE-01 — États prédictifs et réparation canonique

**Statut :** DÉMONTRÉ dans le domaine déclaré ; constructions apparentées connues dans la littérature sur états causaux/PSR et quotients comportementaux.

## Domaine

Histoires accessibles `h`, ensemble de tests futurs `E`, résultats `r` et loi normalisée `P(r|h,e)`.

## Énoncé A — état prédictif relatif

Définir

`h ~_E h'  <=>  pour tout e,r, P(r|h,e)=P(r|h',e)`.

Les classes `[h]_E` sont la représentation minimale au sens de séparation prédictive : toute représentation qui restitue toutes les réponses doit distinguer deux histoires appartenant à des classes différentes, et les classes suffisent à restituer les lois.

## Énoncé B — mise à jour

Si `E` est fermé sous précomposition par les interventions permises et sous les continuations conditionnées admissibles, avec probabilités cohérentes et branches de probabilité positive, alors l'équivalence est stable sous mise à jour : deux histoires équivalentes donnent des histoires mises à jour équivalentes après une même intervention et un même résultat observé.

## Énoncé C — raffinement par visibilité

Si `E ⊆ F`, l'équivalence relative à `F` raffine celle relative à `E`. Des tests plus riches ne peuvent donc que conserver ou augmenter le nombre de distinctions prédictives.

## Énoncé D — réparation canonique déterministe

Pour des actions `T_a:X→X` et une observation `π:X→Y`, définir

`x ≈ x' <=> π(T_u x)=π(T_u x')` pour tout mot d'actions `u`.

Alors `≈` est la plus grossière équivalence stable par les actions qui raffine l'observation `π`. Elle fournit la réparation canonique d'une description instantanée qui n'est pas autonome.

## Limites

La minimalité est prédictive, pas une minimalité de coût algorithmique ni de dimension quantique. Sans fermeture adéquate de l'ensemble des tests, la stabilité de mise à jour peut échouer.

## Source

`/Recherche/02_PROGRAMMES_ACTIFS/Transformations_Autonomie/theorie_transformations_2026-10-12.md`, sections 3–4.