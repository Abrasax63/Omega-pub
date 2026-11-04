# Audit de certification RAVI-2 — Navier–Stokes

Date : 2026-10-15. Version 1.0. Périmètre : 26 cartes candidates du registre `NAVIER_STOKES_BRIQUES_RAVI2_2026-10-15.md`.

## Source et frontière épistémique

Source primaire : OpenAI, *Finite Time Blowup for Navier–Stokes*, 166 pages, https://cdn.openai.com/pdf/32d9f210-8b73-45e0-91bc-82a30aef8a9a/navier-stokes.pdf, théorème 1.1, §2–3. La source affirme l'existence, pour toute viscosité ν>0, d'une solution forcée avec force C∞ à support compact, issue du repos, énergie bornée et vitesse L∞ non bornée avant t=1. **Ce n'est pas le problème non forcé.** Le présent audit n'est pas une certification du théorème principal ni une compilation indépendante de la formalisation Lean.

Statuts : `V-EL` = identité élémentaire prouvée ici indépendamment (sous hypothèses explicites) ; `LIT-TRACE` = attribution/source identifiée, mais preuve profonde non reconstruite ; `INDET` = contrat source ou transfert restant à auditer. Une carte peut contenir une sous-brique V-EL sans que toute la carte soit certifiée.

## Sous-briques vérifiées indépendamment

1. **NS-02 / V-EL — Dérivée matérielle.** Si u est C¹ et X'(t)=u(X(t),t), alors d/dt u(X(t),t)=∂ₜu+(u·∇)u au point X(t). Preuve : règle de chaîne. Hypothèse : trajectoire classique.
2. **NS-03 / V-EL — Divergence cylindrique axisymétrique.** Pour r>0, div u = (1/r)∂ᵣ(ruᵣ)+(1/r)∂θuθ+∂zu_z ; si ∂θuθ=0, l'identité annoncée suit. **Ne pas extrapoler directement à r=0 sans condition de régularité cartésienne.**
3. **NS-04 / V-EL — Identité d'énergie forcée.** Pour u,p suffisamment réguliers, divergence nulle et intégrations par parties légitimes sur R³ : (1/2)d/dt||u||²₂+ν||∇u||²₂=∫f·u. La convection et la pression s'annulent par incompressibilité. Ne fournit aucune borne L∞ en dimension 3.
4. **NS-05 / V-EL — Résidu inverse.** Pour tout champ lisse divergence nulle u et p, poser f=∂ₜu+(u·∇)u−νΔu+∇p produit une solution formelle exacte. **La régularité de f au temps de concentration et son support compact ne suivent pas de cette définition.**
5. **NS-09/12 / V-EL — Comptabilité anisotrope.** ℓᵣ~τ^{1/2}, ℓ_z~τ^{1/2−h} donnent volume ~τ^{3/2−h}; avec amplitude ~τ^{−1/2−h}, énergie du cœur ~τ^{1/2−3h}; cet exposant est positif pour h<1/6, donc en particulier 0<h<1/100. Cela n'établit pas les bornes d'énergie du champ complet.
6. **NS-11 / V-EL — Changement de viscosité.** Si (u,p,f) satisfait l'équation à ν=1, alors uν(x,t)=√ν u(x/√ν,t), pν=νp(x/√ν,t), fν=√ν f(x/√ν,t) satisfait l'équation à ν>0. Chaque terme de l'équation est multiplié par √ν ; div uν=div u. L'énergie se transforme comme ||uν||²₂=ν^{5/2}||u||²₂. Vérification par règle de chaîne.
7. **NS-15 / V-EL — Reynolds anisotrope.** Reθ~τ^{−h}/ν, Rer=O(1/ν) pour ν fixé. Le rapport des taux de diffusion axial/radial est (ℓᵣ/ℓ_z)²~τ^{2h}→0. **Ces égalités sont conditionnelles aux échelles supposées.**
8. **NS-19 / V-EL — Moyenne quadratique non nulle.** v(θ)=a sin θ donne ⟨v⟩=0, ⟨v⊗v⟩=(a⊗a)/2. Ceci ne prouve ni divergence nulle ni réalisation de contraintes arbitraires.
9. **NS-08 / V-EL — Monotonie de la coordonnée q.** Avec D=1/2−h, τ=q(1−η²), z=q^Dη, éliminer η donne F(q)=q−z²/q^{2D−1}=q−z²q^{2h}, puisque 2D−1=−2h. Il faut soigneusement conserver le signe lors de la conversion de la puissance au dénominateur. Pour |η|<1, dF/dq=1−2hη²>0. Cette identité ne suffit pas à établir à elle seule l'existence globale des profils.

## Contrôle adversarial sur NS-08

En utilisant z=q^Dη, on a z²/q^{2D-1}=qη² et F'(q)=1−(1−2D)η²=1−2hη². Le signe positif vaut pour 0<h<1/2 et |η|<1. L'unicité locale en q suit. L'inversibilité globale et les bornes uniformes demandent la définition précise du domaine. Ce contrôle met en évidence une erreur facile de réécriture des exposants ; aucune nouvelle propriété globale n'est revendiquée.

## Cartes non certifiées intégralement

NS-01 : énoncé du modèle classique, pas certification d'existence globale. NS-06 : régularité C∞ du résidu ; NS-07 : régularité à l'axe ; NS-08 : construction de profils ; NS-10 : estimations des profils réels ; NS-13–14 : mécanismes et équations avec viscosité ; NS-16–18 : dynamique et support des pulses ; NS-20–23 : réalisation des contraintes et corrections à tous ordres ; NS-24–26 : raccordements, extérieur thermique et forçage compact. Toutes ces parties restent `LIT-TRACE/INDET` selon la portée, et non `V-EL`.

## Antériorité, d'après §1.1 du manuscrit

- Ondes cisaillées / vecteurs d'onde : Lifschitz–Hameiri ; Friedlander–Vishik ; Craik–Criminale ; Singh–Sridhar.
- Contraintes par oscillations : Daneri–Székelyhidi.
- Amplification multi-échelle avec forçage : Córdoba–Martínez-Zoroa et Córdoba–Martínez-Zoroa–Zheng.
- Équation de Navier–Stokes moyennée avec blowup : Terence Tao (2014), **équation modifiée**, distincte du présent manuscrit.
Ces références interdisent d'attribuer automatiquement les mécanismes classiques au manuscrit OpenAI.

## Chaîne de preuve principale à répliquer

Le §3 du manuscrit annonce : Proposition 5.5 (champ de base et contrainte annulaire), Proposition 7.5 (réalisation oscillatoire), Proposition 9.6 (amélioration du résidu), Proposition 9.9 et Proposition 10.1 (somme/localisation), Lemme 10.3 (force lisse), théorème 1.1 ; plus annexe A (moments/extérieure chaleur), B (profils à l'axe), C (cône des contraintes). Aucune de ces preuves profondes n'a été intégralement reconstruite dans cet audit.

## Décision de certification et commit

- **9 sous-briques élémentaires** disposent d'une preuve courte indépendante sur papier dans ce dossier ; leur statut `V-EL` est limité aux énoncés exacts ci-dessus. Le décompte n'est pas 9 cartes intégralement certifiées.
- **0 des 26 cartes globales** promue dans la table des résultats scientifiques certifiés ; les cartes sont composites et les preuves porteuses manquent.
- **0 certification indépendante du théorème principal** ; pas de promesse de résolution nouvelle.
- Aucun changement à `RESEARCH_MEMORY.sqlite`, `MEMORY_INDEX.md` ou au snapshot actif : il faudrait un commit transactionnel avec audit de schéma, déduplication et régression avant promotion.
- La décision est de conserver le registre et cet audit comme **preuves documentaires versionnées**, en vue d'une seconde passe sur les propositions porteuses.