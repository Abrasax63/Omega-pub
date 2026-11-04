# BR-CTRL-01 — Certificat cyclique de mémoire locale infinie

**Statut :** DÉMONTRÉ, `CERT-V` dans la source ; mécanisme d'automates réguliers classique, ici spécialisé au problème de recollement contrôlé.

## Domaine

Système fini déterministe contrôlé avec ensemble de départ fermé `H`, alphabet `Σ=Y×A` et langage factoriel `L_H`.

## Base interdite minimale

Avec le filtre de croyance

`δ(B,(y,a))={T_a(x): x∈B, π(x)=y}`,

la base des mots interdits minimaux est

`F = (L_H Σ) ∩ (Σ L_H) \\ L_H`.

## Certificat fini

Suivre trois croyances :

- `B_w` pour le mot entier ;
- `B_p` pour le mot privé de sa dernière lettre ;
- `B_s` pour le mot privé de sa première lettre.

Sous une lettre `z` :

`(B_w,B_p,B_s) -> (δ(B_w,z), B_w, δ(B_s,z))`.

Un état est acceptant si `B_w=∅`, `B_p≠∅`, `B_s≠∅`.

**Critère :** `F` est infini si et seulement si un cycle accessible de cet automate peut encore atteindre un état acceptant. S'il n'existe aucun tel cycle, la longueur maximale des interdits minimaux est finie ; la source donne la borne effective grossière `≤ 8^K` pour `K=|H|`.

## Témoin minimal utile

Il existe un système à 3 états, 2 observations et 2 actions totales où, pour tout entier impair `n≥1`, un interdit minimal de longueur `n+3` existe. Chaque action prise isolément a un ordre local fini, tandis que leur combinaison donne un ordre infini.

## Barrière de généralisation

Le certificat porte sur les mots action–observation d'un système déterministe fini à actions totales et toutes suites d'actions autorisées. Il ne doit pas être identifié à une profondeur ADS/PDS ni à une mesure portant seulement sur les observations.

## Source

`/Recherche/02_PROGRAMMES_ACTIFS/Delta_h_Fermeture/DELTA_H_ACCES_INTERVENTIONS_V1_1_2026-09-29.md`, sections 3–5.