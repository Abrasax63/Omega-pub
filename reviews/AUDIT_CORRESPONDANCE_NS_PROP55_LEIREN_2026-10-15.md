# Audit RAVI-2 — Proposition 5.5 / Lei–Ren, 15 octobre 2026

Version 1.1 — annotation de reprise ajoutée.

## État consolidé

Correspondance structurelle forte documentée entre OpenAI Prop. 5.5 et Lei–Ren §§15–17, sans équivalence logique intégrale certifiée. Le mécanisme abstrait de stabilité d'une contrainte admissible sous perturbation relative a été séparé et certifié comme NS-CERT-E-10.

## Déjà fait — NE PAS REFAIRE

- Vérification de la divergence exacte / structure du reste plat au niveau des énoncés.
- Identification du mécanisme d'incompressibilité sous troncature et de la correction de commutateur.
- Identification des cinq moments comme verrou distinct.
- Vérification que le contrôle pondéré seul est insuffisant près des bords.
- Identification chez Lei–Ren du Lemma 17.1 : contrôle relatif de la perturbation de contrainte, puis Prop. 17.2 sous Assumption 13.1.
- Vérification indépendante du lemme abstrait : une perturbation plus petite que la marge préserve l'admissibilité.
- Constat que Lei–Ren Part I ne réalise pas encore l'annulation oscillatoire de la contrainte tangentielle.
- Abandon de l'objectif inutilement fort « identité terme à terme des profils » : seule une équivalence suffisante des hypothèses/mécanismes est requise pour les briques abstraites.

## Reste à faire / verrous

### P55-A — PRIORITÉ ACTIVE
Suivre Prop. 13.3 (13.31) → Assumption 13.1(v) → Lemma 17.1 → Prop. 17.2. Vérifier origine de la marge, uniformité, domaine, dépendance aux paramètres et absence de circularité. Comparer ensuite au Theorem 4.6(iv) / Prop. 5.5 OpenAI.

### P55-B — quantificateurs aux bords
Comparer λ, Z et q, η avec domaines exacts. La platitude sur |Z|<=1-ε ne doit pas être promue en uniformité jusqu'à Z=±1 sans preuve.

### P55-C — cinq moments
Comparer matrices, rang et uniformité paramétrique des corrections de moments.

### P55-D — candidat nouvelle CERT-E
Écrire une preuve autonome de conservation de l'incompressibilité sous troncature via fonction de courant/potentiel et correction de commutateur.

### Après Prop. 5.5
Auditer Prop. 7.5 (réalisation oscillatoire), puis 9.6, 9.9, 10.1, Lemma 10.3 et annexes pertinentes.

## Règle de reprise

Reprendre à P55-A. Ne pas refaire les vérifications listées dans « Déjà fait » sauf nouvelle source contradictoire ou modification de l'énoncé.

## Décision

NS-CERT-E-10 peut être conservée comme brique abstraite certifiée. Proposition 5.5 entière : NON CERTIFIÉE. Théorème principal : NON CERTIFIÉ. Aucun glissement de statut implicite.