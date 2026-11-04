# BR-STATE-COST-01 — Coût minimal d’extension par fermeture des comportements

**Statut : DÉMONTRÉ interne. Version 1.0 — 2026-10-19.**

## Domaine
Dispositif déterministe total fini, ensemble de comportements existants \(F_{old}\) fermé sous dérivées par les actions admises, et comportements exacts requis \(B_{req}\). Le coût compte uniquement le nombre d’états ajoutés et interdit de modifier les anciens comportements.

## Énoncé
Poser \(C=\mathrm{Der}(F_{old}\cup B_{req})\), la fermeture sous toutes les dérivées admissibles.

- Si \(C\setminus F_{old}\) est fini, le nombre minimal d’états à ajouter est exactement \(|C\setminus F_{old}|\).
- Si \(C\setminus F_{old}\) est infini, aucune extension déterministe finie satisfaisant exactement les comportements requis ne convient.

## Preuve
Chaque comportement dérivé nouveau doit être représenté par un état distinct : deux états portant des comportements différents ne peuvent être fusionnés sans changer une continuation observable. Réciproquement, ajouter un état pour chaque élément de \(C\setminus F_{old}\), avec les transitions données par dérivation, réalise tous les comportements et ferme le dispositif.

## Limites
Ce n’est pas une borne de coût algorithmique, probabiliste ou quantique. Le résultat suppose exactitude, totalité et conservation des anciens comportements.

## Provenance
`/Recherche/02_PROGRAMMES_ACTIFS/Transformations_Autonomie/theorie_transformations_2026-10-12.md`, proposition P5.