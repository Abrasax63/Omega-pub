# BR-OBS-01 — Expérience adaptative finie, expérience prédéfinie impossible

**Statut :** DÉMONTRÉ pour les témoins ; minimalité binaire appuyée par calcul exhaustif exact. Nouveauté bibliographique des témoins : INDÉTERMINÉE dans la source.

## Énoncé principal

Il existe une machine de Mealy déterministe complète telle que

`r_IO < ∞`, `L_A < ∞` et `L_P = ∞`.

Un témoin binaire comportementalement minimal à 5 états réalise exactement

`(r_IO, L_A, L_P) = (2, 3, ∞)`.

Un second témoin à 5 états, 3 actions et 3 sorties réalise

`(r_IO, L_A, L_P) = (1, 2, ∞)`.

Ainsi une mémoire locale finie du langage ne permet pas, en général, de convertir une expérience adaptative en expérience prédéfinie.

## Minimalité établie dans l'univers binaire

L'énumération exhaustive des machines binaires complètes à 4 états ne trouve aucune machine avec ADS, sans PDS, et `r_IO<∞`. Pour 5 états, le minimum lexicographique trouvé est

`(|X|,|A|,|Y|,r_IO,L_A)=(5,2,2,2,3)`.

La minimalité globale avec alphabets non binaires à 4 états reste indéterminée.

## Algorithme réutilisable pour r_IO

Le calcul exact peut suivre les couples stricts de croyances `∅≠B⊊C⊆X`. Après restriction au cœur accessible et coaccessible vers un interdit minimal : un cycle implique `r_IO=∞`; sinon le plus long chemin donne exactement la longueur maximale des interdits minimaux.

## Source

`/Recherche/02_PROGRAMMES_ACTIFS/Observabilite/Notes/RAPPORT_OBSERVABILITE_ACTIVE_2026-09-26.md`, sections 2–5.