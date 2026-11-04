# SCH-SEXTIC-PARITY-01 — Secteur polynomial régulier du potentiel sextique

**Statut : DÉMONTRÉ interne. Version 1.0 — 2026-10-19.**

## Domaine
\(\sigma\in\{0,1\}\), \(N\ge2\), \(g(x)=a x^4/4+b x^2/2\),
\(\mathcal M_{N,\sigma}=x^\sigma e^{-g(x)}\mathcal P_N(x^2)\), et \(H=-D_x^2+V(x)\).

## Énoncé
\(\mathcal M_{N,\sigma}\) est invariant par \(H\) exactement lorsque
\[
V(x)=a^2x^6+2abx^4+[b^2-a(4N+2\sigma+3)]x^2+E-(2\sigma+1)b,
\]
où \(E\) est constant.

Si \(a\ne0\), un même potentiel et une même jauge de cette forme ne peuvent préserver deux secteurs distincts \((N,\sigma)\). Si \(a=0\), on retrouve une suite complète pour les deux parités.

## Preuve / contrôle
Après \(z=x^2\) et conjugaison par \(x^\sigma e^{-g}\), l’opérateur devient
\[
-4zD_z^2+[4az^2+4bz-2(2\sigma+1)]D_z-4Naz+E,
\]
et l’invariance se vérifie directement sur les monômes. Le contrôle rationnel indépendant du 19 octobre 2026 a testé exactement 4752 images de monômes pour \(N=2,\dots,12\), les deux parités et \(a,b,E\in\{-2,0,3\}\), sans échec.

## Limites
Il s’agit d’une famille quasi-exactement soluble connue. Aucune nouveauté bibliographique n’est revendiquée. Le résultat ne traite pas tous les domaines auto-adjoints, la normalisabilité globale ni l’ensemble des potentiels de Schrödinger.

## Provenance
`/Recherche/02_PROGRAMMES_ACTIFS/Delta_h_Fermeture/Notes/fermeture_mathematique_extensions_2026-10-13.md`.