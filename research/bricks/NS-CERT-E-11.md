# NS-CERT-E-11 — Sommation diagonale contrôlée dans C∞

Statut : DÉMONTRÉ — certificat interne RAVI-2. Version 1.

## Énoncé
Pour des familles f_j(a) tendant vers 0 dans chaque semi-norme C∞ lorsque a→∞ (j fixé), on peut choisir diagonalement a_j pour que Σ f_j(a_j) converge dans C∞ avec queues géométriquement contrôlées; les opérateurs différentiels linéaires annulant chaque terme annulent la somme.

## Domaine
C∞(Ω;R^m) muni d’une exhaustion compacte et de semi-normes croissantes.

## Hypothèses
- Convergence vers 0 de f_j(a) dans chaque semi-norme à j fixé
- Choix diagonal des paramètres

## Limites
Classique; principe fonctionnel seulement, pas les estimations physiques complètes du manuscrit.

## Provenance
Audit : `/Recherche/03_AUDITS_CERTIFICATS/NS_CERT_E_11_SOMMATION_DIAGONALE_2026-10-15.md`.
Commit : `COMMIT-RAVI2-2026-10-15-NS-E10-E15-07`.

Aucune revendication d’originalité mathématique. La certification porte sur la brique autonome, pas sur le théorème Navier–Stokes complet.