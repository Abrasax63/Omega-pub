# SCH-POLY-CLOSURE-01 — Fermeture polynomiale d’un opérateur d’ordre deux

**Statut : DÉMONTRÉ interne. Version 1.0 — 2026-10-19.**

## Domaine
Sur un intervalle réel, soit
\(L=-P(z)D_z^2+A(z)D_z+B(z)\) et \(\mathcal P_N=\mathrm{span}\{1,z,\dots,z^N\}\), \(N\ge2\).

## Énoncé
1. \(L\mathcal P_N\subseteq\mathcal P_N\) si et seulement si \(P,A,B\) sont polynomiaux de degrés au plus \(4,3,2\) et
\[
A_3=2(N-1)P_4,\qquad B_2=-N(N-1)P_4,\qquad B_1=N(N-1)P_3-NA_2.
\]
2. Si deux indices distincts \(N,M\ge2\) sont préservés, alors nécessairement et suffisamment
\(\deg P\le3,\deg A\le2,B=B_0+B_1z\),
\[
A_2=(N+M-1)P_3,\qquad B_1=-NM P_3.
\]
3. Si trois indices distincts \(N,M,K\ge2\) sont préservés, alors \(\deg P\le2,\deg A\le1\), \(B\) est constant, donc tous les \(\mathcal P_n\) sont préservés.
4. Deux secteurs ne suffisent pas en général : \(L=-z^3D_z^2+5z^2D_z-8z\) préserve \(\mathcal P_2\) et \(\mathcal P_4\), mais pas \(\mathcal P_3\).

## Preuve / contrôle
La preuve se fait degré par degré avec le coefficient
\(C_s(n)=-n(n-1)P_{s+2}+nA_{s+1}+B_s\), quadratique en \(n\). Les annulations forcées aux degrés de bord donnent les conditions ci-dessus. Un contrôle rationnel indépendant du 19 octobre 2026 a vérifié 792 images T1, 880 images T2, 1092 contrôles T3 et 483 images des contre-exemples généralisés.

## Limites
Le résultat suppose une même variable \(z\), une même jauge et le même opérateur. Il ne classifie pas les espaces lacunaires ni les secteurs obtenus avec des coordonnées/jauges différentes. Il ne résout pas l’équation de Schrödinger. Les classifications générales d’espaces polynomiaux invariants sont anciennes ; aucune priorité historique n’est revendiquée pour cette formulation.

## Provenance
`/Recherche/02_PROGRAMMES_ACTIFS/Delta_h_Fermeture/Notes/fermeture_mathematique_extensions_2026-10-13.md`.