# Réconciliation sémantique des briques — lot 08 (13 fichiers, 9 novembre 2026)

**Dépôt :** `Abrasax63/Omega-pub`  
**Branche source immuable :** `migration/ravi2-ccs-public-2026-11-04`  
**Branche de publication :** `maintenance/reconciliation-bibliotheque-2026-11-05`  
**Périmètre :** les 13 briques originales restant à classer selon le bilan documentaire précédent.  
**Nature :** réconciliation sémantique, sans nouvel audit de preuve ni exécution des artefacts de reproductibilité.

## 1. Fichiers examinés et empreintes Git source

| Fiche | SHA Git source |
|---|---|
| `BR-R90-02_MAJORITY_WALSH.md` | `4319a4b78b8218b7aa1795245edbbd532ce92c8b` |
| `GLOBAL-LOC-01.md` | `20ee97227215e02cc8f4d713fe79f4df71c22139` |
| `OSC-ITER-01.md` | `e1a57ecd4bc8894a252d7232c4055eeb91459c47` |
| `OSC-REAL-01.md` | `e56af60421af524cda947cba2978c860596307e0` |
| `SCH-POLY-CLOSURE-01_BRIQUE.md` | `0458e97a04ce2d02b8c93be6378b0763844db7a3` |
| `SCH-SEXTIC-PARITY-01_BRIQUE.md` | `4cc8d8c167c6098c7cf4778a5e0850a425081692` |
| `NS-CERT-E-10.md` | `b0b805065e15dffc278a862c27b2c80d214875e6` |
| `NS-CERT-E-11.md` | `b59f06b98b762526bcbb8b19ba05e17b7649dfab` |
| `NS-CERT-E-12.md` | `be6b13c3e44471e5b63dd6acaec33418e10d5b5f` |
| `NS-CERT-E-13.md` | `81d9bb273a1f1ec3e13c9912861b11d1b78e8e98` |
| `NS-CERT-E-14.md` | `601cd1d4eebaaf4ea9c61deba28f12b94623b5fe` |
| `NS-CERT-E-15.md` | `aa116d4adf083a3254b54118bbe3543d2a138a96` |
| `NS-P55-COMP-01.md` | `498cc5670c9efc235509ad1e04e5c90dbaf3b5ab` |

## 2. Classement sémantique

### A. Règle 90 : uniformité Majority–Walsh

**BR-R90-02** affirme que, pour une règle 90 sur un cycle de taille (N), avec observation Majority de trois bits et états initiaux uniformes, le mot observé de longueur (h+1) est uniforme lorsque (N\ge 2h+3). Le mécanisme indiqué est une décomposition Fourier–Walsh dont le support ne subit pas d'identification après réduction modulo (z^N-1) dans ce régime.

- La condition est déclarée suffisante, pas nécessaire.
- Le résultat ne démontre ni fermeture locale de l'observation Majority ni flèche du temps.
- À distinguer de BR-R90-01 (noyaux/périodes) : les deux fiches portent sur la règle 90, mais les objets et conclusions ne sont pas interchangeables.

### B. Chaîne d'itération oscillatoire et localisation globale

Les trois fiches suivantes décrivent des étapes successives d'une construction composite :

1. **OSC-ITER-01 — étape d'itération.** Une étape oscillatoire à gain résiduel fixe (+1/10), avec base/stress admissible, amplitudes primaires, inverse linéarisé signé et corrections moyennes. La fiche corrige explicitement la portée de l'identité de covariance : l'égalité bilinéaire linéarisée est exacte, tandis que la covariance non linéaire complète reste dans le résidu suivant. Cette étape ne construit pas à elle seule l'objet limite.
2. **OSC-REAL-01 — réalisation par sommation diagonale.** Combine l'itération avec un domaine commun et des pertes de dérivées contrôlées pour obtenir un champ local (C^\infty) incompressible dont le résidu est plat à tout ordre. La platitude ne signifie pas que le résidu est identiquement nul.
3. **GLOBAL-LOC-01 — localisation globale.** Utilise OSC-REAL-01, des propositions/lemmes externes et NS-CERT-E-11 à E-13 pour passer d'un champ local/potentiels à un champ compactement supporté et exactement incompressible, en préservant le champ près du noyau singulier. La fiche indique expressément qu'elle ne certifie pas à elle seule les lemmes 10.4–10.5 ni la conclusion globale du théorème principal.

**Chaîne déclarée :** OSC-ITER-01 → OSC-REAL-01 → GLOBAL-LOC-01. La dernière étape a aussi des dépendances externes et des sous-briques identifiées ; ce n'est pas une chaîne autonome fermée par ces trois fiches seules.

### C. Opérateurs de Schrödinger et secteurs polynomiaux

- **SCH-POLY-CLOSURE-01** : caractérise, pour un opérateur différentiel d'ordre deux sur un intervalle réel, les conditions de degrés et de coefficients permettant de préserver un espace polynomial ℙ_N. La fiche distingue les cas d'un, deux et trois indices préservés. Elle fournit un contre-exemple explicite montrant que préserver deux secteurs distincts n'implique pas préserver le secteur intermédiaire. Les hypothèses « même variable, même jauge, même opérateur » sont essentielles à la portée annoncée.
- **SCH-SEXTIC-PARITY-01** : décrit une famille sextique quasi-exactement soluble avec secteur (x^\sigma e^{-g(x)}\mathcal P_N(x^2)). Pour (a\ne0), un même potentiel et une même jauge ne préservent pas deux secteurs distincts de cette forme ; pour (a=0), la fiche indique le retour à une suite complète pour les deux parités. La fiche reconnaît explicitement le caractère connu de la famille et ne revendique pas de nouveauté bibliographique.

**Distinction :** la première fiche est une caractérisation de fermeture polynomiale pour un opérateur d'ordre deux général dans son domaine ; la seconde est une famille particulière de potentiel sextique et de jauge. Ne pas les fusionner en une classification de tous les opérateurs ou potentiels de Schrödinger.

### D. Sous-certificats élémentaires Navier–Stokes

Les six fiches NS-CERT-E-10 à E-15 sont des certificats de résultats auxiliaires autonomes, déclarés classiques dans leurs propres domaines :

- **E-10 — stabilité d'admissibilité :** une perturbation relative de norme au plus ε fois la marge initiale conserve l'admissibilité et laisse une marge au moins ((1-ε)m(T_0)), pour (0\le\varepsilon<1).
- **E-11 — sommation diagonale dans (C^\infty) :** choix diagonal assurant la convergence avec queues contrôlées dans les semi-normes d'une exhaustion compacte ; les opérateurs linéaires qui annulent chaque terme annulent la somme.
- **E-12 — localisation solénoïdale par potentiel :** l'identité (u=\operatorname{curl}(\chi A)=\chi v+\nabla\chi\times A) conserve la divergence nulle et contrôle le support sous les hypothèses de régularité indiquées.
- **E-13 — extension lisse par platitude quantitative :** le prolongement par zéro est (C^\infty) et plat si toutes les dérivées spatio-temporelles ont les estimations d'ordre arbitraire requises, localement uniformes en espace. La platitude de la seule fonction ne suffit pas.
- **E-14 — inverse radial à moment nul :** résolution explicite de φ'+(e/R)φ=f sur un intervalle strictement éloigné de (R=0), avec condition nécessaire et suffisante de moment nul. L'axe (R=0) est exclu.
- **E-15 — primitive périodique :** une fonction lisse périodique admet une primitive périodique si et seulement si sa moyenne est nulle ; la normalisation de moyenne nulle fixe l'unicité.

Ces six briques ne certifient pas le théorème de Navier–Stokes complet. Elles ne doivent pas être promues de façon collective en preuve de l'assemblage global. Les limites de chacune restent celles de sa fiche.

### E. Assemblage de la base annulaire

**NS-P55-COMP-01** est une fiche composite déclarant une interface entre profil principal avec marge directionnelle, contrôle pondéré et corrections de base, pour obtenir un champ axisymétrique incompressible et un stress annulaire réalisé avec reste plat à tout ordre.

- Dépendances annoncées : Theorem 4.6(iii)–(iv) et Proposition 5.5 du manuscrit OpenAI ; contrôle croisé Lei–Ren Theorem 12.4, Proposition 13.3, Lemma 17.1 et Proposition 17.2.
- Sous-certificats : P55-A/B/C/D.
- Limites explicites : comparaison λ ↔ √(1−t) non uniforme hors secteurs fixes ‖Z‖≤1−ε ; la fiche ne certifie ni les oscillations ni le théorème principal.

Cette brique composite doit rester séparée des six sous-certificats E-10 à E-15. Son statut déclaré ne remplace pas une vérification indépendante de ses dépendances externes et de l'assemblage complet.

## 3. Points de vigilance transversaux

1. **Statuts composites et élémentaires :** GLOBAL-LOC-01 et NS-P55-COMP-01 sont composites ; NS-CERT-E-10 à E-15 sont des résultats auxiliaires autonomes. Leurs statuts ne se transfèrent pas automatiquement.
2. **Résidu plat :** OSC-REAL-01 et NS-P55-COMP-01 parlent de platitude du reste ; cela ne signifie pas annulation identique du résidu.
3. **Dépendances externes :** les références aux résultats du manuscrit OpenAI et au contrôle Lei–Ren sont des prémisses déclarées ; elles ne sont pas revalidées dans ce lot.
4. **Domaines restreints :** E-14 exclut l'axe radial ; E-13 exige la platitude de toutes les dérivées ; SCH-POLY-CLOSURE-01 exige une même variable/jauge/opérateur.
5. **Portée physique :** aucune de ces fiches, prise isolément, ne démontre le théorème Navier–Stokes principal.

## 4. Provenance et statut de la réconciliation

Les statuts et contrôles inscrits dans les fiches sont conservés comme **déclarations historiques des sources**. Les contrôles numériques, audits et certificats mentionnés dans ces documents n'ont pas été réexécutés ici. Aucun checker, script, notebook, calcul exact ou preuve Lean n'a été lancé. Aucune preuve n'a été reconstruite ligne par ligne et aucune certification n'est renouvelée.

Aucune base SQLite privée n'a été consultée ou modifiée. La branche source historique n'a pas été modifiée. Le présent rapport classe le contenu documentaire et ses dépendances ; il ne constitue pas une validation scientifique nouvelle.
