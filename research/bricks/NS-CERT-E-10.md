# NS-CERT-E-10 — Stabilité quantitative d’une contrainte admissible sous perturbation relative

Statut : DÉMONTRÉ — certificat interne RAVI-2. Version 1.

## Énoncé
Si m(T0)=dist(T0,K^c)>0 et ||ΔT||≤ε m(T0), 0≤ε<1, alors T0+ΔT reste admissible et sa marge est ≥(1−ε)m(T0).

## Domaine
Espace normé; ensemble admissible K; marge définie par distance au complément.

## Hypothèses
- m(T0)>0
- 0≤ε<1
- ||ΔT||≤ε m(T0)

## Limites
Classique; certificat abstrait. Ne certifie pas Prop. 5.5 ni l’équivalence OpenAI–Lei–Ren.

## Provenance
Audit : `/Recherche/03_AUDITS_CERTIFICATS/NAVIER_STOKES_BRIQUES_CERT_E_VERROUILLEES_2026-10-15.md`.
Commit : `COMMIT-RAVI2-2026-10-15-NS-E10-E15-07`.

Aucune revendication d’originalité mathématique. La certification porte sur la brique autonome, pas sur le théorème Navier–Stokes complet.