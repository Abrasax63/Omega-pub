# Navier–Stokes — registre d'extraction mathématique RAVI-2

Date : 15 octobre 2026 · Version documentaire 0.1 · Statut global : **EXTRACTION CANDIDATE, NON CERTIFIÉE**.

## Source primaire et périmètre

*OpenAI, Finite Time Blowup for Navier–Stokes*, 166 pages, https://cdn.openai.com/pdf/32d9f210-8b73-45e0-91bc-82a30aef8a9a/navier-stokes.pdf . Manuscrit consulté via son texte public, principalement l'introduction, les sections 2–3 et la table des matières. **Les preuves intégrales des sections 4–10 et annexes A–C n'ont pas été vérifiées ligne par ligne** ; l'inventaire ne peut donc être déclaré exhaustif. Les repères de section sont des points d'entrée à contrôler avant toute promotion.

**Énoncé principal rapporté par la source, et non re-démontré ici :** pour tout ν>0, existence d'une force extérieure lisse à support compact, d'une solution lisse sur t<1 partant du repos, de support spatial compact, avec norme L² uniformément bornée mais norme L∞ non bornée quand t→1. Ce n'est **pas** une résolution de la régularité non forcée.

## Convention des cartes

Identifiants documentaires `LIT-NS-01` à `LIT-NS-26` ; ils ne sont pas des identifiants de résultats certifiés dans `RESEARCH_MEMORY.sqlite`. Catégories : **CLASSIQUE** (connaissance antérieure), **MÉCANISME SOURCE** (construction présentée dans le manuscrit), **OUTIL** (technique transférable sous conditions). Tous les statuts : **CANDIDAT / extraction à auditer**, sauf identités algébriques élémentaires indiquées « vérification directe » ; ces vérifications ne certifient pas le théorème du manuscrit.

| ID | Brique atomique / contrat | Nature | Source / vérification requise |
|---|---|---|---|
| NS-01 | Équation ∂ₜu+(u·∇)u−νΔu+∇p=f, div u=0 ; hypothèses sur domaine et régularité à préciser | CLASSIQUE | §1, (1.1) ; distinguer forcé/non forcé |
| NS-02 | Dérivée matérielle Dₜu=∂ₜu+(u·∇)u | CLASSIQUE | §1.1 ; identité de chaîne le long des trajectoires |
| NS-03 | Incompressibilité div u=0 et relation cylindrique (1/r)∂ᵣ(ruᵣ)+∂zu_z=0 en axisymétrie | CLASSIQUE | §3.1 ; contrôle de l'axe r=0 |
| NS-04 | Identité d'énergie pour solutions lisses avec travail de la force ; la borne d'énergie ne borne pas L∞ en dimension 3 | CLASSIQUE | §1–2 ; hypothèses de bord/intégrabilité indispensables |
| NS-05 | Résidu R(u,p)=∂ₜu+(u·∇)u−Δu+∇p ; construction inverse f:=R | OUTIL | §2, §3 (3.1) ; l'enjeu est la régularité de f |
| NS-06 | Contrôle C∞ : toute dérivée cartésienne spatio-temporelle du résidu doit s'étendre au temps singulier | OUTIL | §3, §§9–10 ; vérifier normes et estimations |
| NS-07 | Coordonnées cylindriques, base eᵣ,eθ,e_z et champs axisymétriques | CLASSIQUE | §2.1, §3.1 ; singularité apparente à l'axe |
| NS-08 | Variables de similarité q,η,X : τ=q(1−η²), z=qᴰη, X=r²/(2q) | MÉCANISME SOURCE | §3.1 (3.2) ; inversibilité et domaines à contrôler |
| NS-09 | Échelles anisotropes ℓᵣ ≍ τ^(1/2), ℓ_z ≍ τ^(1/2−h), 0<h<1/100 | MÉCANISME SOURCE | §2.1 ; ℓᵣ/ℓ_z ≍ τ^h→0 |
| NS-10 | Profil concentrant et lois de puissance : uθ,u_z ≍ τ^(−1/2−h), uᵣ=O(τ^(−1/2)) | MÉCANISME SOURCE | §2.1 ; estimations valables au cœur, pas uniformément partout |
| NS-11 | Changement de viscosité : uν(x,t)=√ν u(x/√ν,t), pν=νp(x/√ν,t), fν=√ν f(x/√ν,t) | OUTIL | §3, (10.22)–(10.23) ; vérification directe par chaîne |
| NS-12 | Concentration et intégrabilité : volume cœur ~τ^(3/2−h), énergie ~τ^(1/2−3h) malgré amplitude divergente | OUTIL | §2.1 ; comptabilité des exposants, non implication générale |
| NS-13 | Amplification par cisaillement/instabilité centrifuge dans un écoulement tournant | CLASSIQUE + MÉCANISME | §1.1, §2.2 ; critères de stabilité à préciser |
| NS-14 | Transport de moment angulaire ruθ et compétition advection/viscosité | CLASSIQUE | §2.1 ; conservation sans couple seulement |
| NS-15 | Bilan amplification–dissipation, nombre de Reynolds Re=Uℓ/ν ; Reθ~τ^(−h), Reᵣ=O(1) | OUTIL | §2.1 ; choix de U et ℓ essentiel |
| NS-16 | Évolution des vecteurs d'onde sous cisaillement, raccourcissement radial et amortissement visqueux | CLASSIQUE + MÉCANISME | §1.1, §2.2 ; équations de transport à extraire de §6–7 |
| NS-17 | Pulses oscillatoires localisés en espace-temps et séquencés vers t=1 | MÉCANISME SOURCE | §2.2, §§6–7 ; quantifier supports et queues |
| NS-18 | Décomposition écoulement moyen + fluctuation à moyenne angulaire nulle | OUTIL | §2.2, §7 ; moyenne et produits non commutent pas en général |
| NS-19 | Flux quadratique non nul malgré moyenne nulle : ⟨v⟩=0 n'impose pas ⟨v⊗v⟩=0 | CLASSIQUE | §2.2 ; vérification directe, p.ex. v=±a équiprobable |
| NS-20 | Réalisation d'une contrainte moyenne prescrite par familles d'oscillations | MÉCANISME SOURCE | §2.2, §7 ; vérifier géométrie et positivité |
| NS-21 | Cône de contraintes admissibles et représentation par tenseurs réalisables | OUTIL + MÉCANISME | annexe C ; ne pas présumer toute matrice réalisable |
| NS-22 | Correction du résidu par divergence de contraintes et ajustement des termes singuliers | MÉCANISME SOURCE | §3, §§7–9 ; préciser signes et compatibilités |
| NS-23 | Corrections asymptotiques à tous ordres du champ de base | MÉCANISME SOURCE | §5 ; distinguer formel de convergent |
| NS-24 | Raccordement intérieur/anneau/extérieur et conservation des équations/contraintes | OUTIL + MÉCANISME | §§4,8–10 ; compatibilité de dérivées à vérifier |
| NS-25 | Extérieur « chaleur » et appariement de moments radiaux | MÉCANISME SOURCE | §2.3, §10, annexe A ; conditions initiales/bord |
| NS-26 | Fonctions de coupure, localisation du support, prolongement lisse du forçage | CLASSIQUE + MÉCANISME | §2.3, §10 ; préserver div u=0 et régularité |

## Vérifications autonomes de premier niveau

1. **Exposants** : si le volume ~ℓᵣ²ℓ_z~τ^(3/2−h) et la vitesse dominante au carré ~τ^(−1−2h), leur produit ~τ^(1/2−3h). Comme h<1/100, l'exposant est positif. Ceci vérifie une *cohérence d'échelles*, pas une borne d'énergie du champ construit.
2. **Reynolds** : τ^(−1/2−h)τ^(1/2)/ν=τ^(−h)/ν ; τ^(−1/2)τ^(1/2)/ν=1/ν, ν fixé. L'ordre asymptotique concorde avec §2.
3. **Fluctuation quadratique** : pour v(θ)=a sin θ, ⟨v⟩=0 et ⟨v⊗v⟩=(a⊗a)/2. L'égalité ne garantit **pas** la réalisation d'un tenseur quelconque ni la divergence nulle.
4. **Changement de viscosité** : la règle de chaîne donne ∂ₜuν=√ν∂ₜu, (uν·∇)uν=√ν(u·∇)u, νΔuν=√νΔu, ∇pν=√ν∇p, tous évalués en (x/√ν,t).

## Graphe initial de dépendances (proposé, non certifié)

- NS-01 → NS-05 → NS-06 → NS-22 → NS-26.
- NS-03 + NS-07 + NS-08 → NS-09 + NS-10 → NS-12.
- NS-13 + NS-14 + NS-15 + NS-16 → NS-17.
- NS-18 + NS-19 + NS-21 → NS-20 → NS-22.
- NS-23 + NS-24 + NS-25 → NS-26.
- NS-11 est une transformation d'échelle de NS-01.

Les flèches sont des **hypothèses de dépendance pédagogique** et non des arcs `DEPEND_DE` validés par audit des preuves.

## Interfaces possibles avec nos programmes (aucune équivalence établie)

- Observabilité / autonomie macroscopique : NS-18/19 fournissent un exemple de perte de l'information de phase avec effet sur une quantité quadratique ; transfert vers une dynamique discrète à construire, non automatique.
- Défauts de fermeture : NS-05/22 peuvent inspirer des certificats de résidu, mais les normes fonctionnelles et relations discrètes sont distinctes.
- Flèche du temps / échelles : NS-09/12 proposent une géométrie d'échelles asymptotiques, sans établir de lien théorique avec τ_pred ou H(T,π).

## Audit RAVI-2 : blocages avant certification et commit SQLite

- [ ] Lecture systématique de chaque définition/lemme/proposition/théorème des §§4–10 et annexes A–C, avec numéro de page et hypothèses exactes.
- [ ] Dédoublonnage contre les cartes CORE, le registre de littérature et les résultats historiques SQLite.
- [ ] Bibliographie des antécédents (Lifschitz–Hameiri, Craik–Criminale, Daneri–Székelyhidi, Córdoba–Martínez-Zoroa, etc.) et attribution correcte.
- [ ] Reconstruction indépendante et contre-tests des lemmes porteurs, notamment contraintes réalisables, estimations C∞ et raccordements.
- [ ] Audit de robustesse et d'invariance de représentation ; test de redondance/théorème nul.
- [ ] Audit des dépendances causales et compatibilité avec le schéma SQL courant.
- [ ] Validation du commit, tests d'intégrité/régression, empreintes des sources, snapshot et index mis à jour.

**Décision :** sauvegarde documentaire des 26 candidats autorisée ; **aucune promotion dans `certified_active_results`** ni modification de `RESEARCH_MEMORY.sqlite` tant que les portes de certification ne sont pas passées. L'extraction est une base de travail réelle, pas une certification fictive.