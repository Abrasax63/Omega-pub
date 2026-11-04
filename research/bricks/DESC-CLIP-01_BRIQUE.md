# DESC-CLIP-01 — Projection optimale locale d’un facteur d’évidence robuste

**Statut : DÉMONTRÉ interne. Version 1.0 — 2026-10-19.**

## Domaine
Observation binaire \(Y\), probabilité nulle inconnue mais contrainte à \([\ell,u]\subset(0,1)\), prédiction candidate \(q\in[0,1]\). On souhaite un facteur d’évidence non négatif dont l’espérance conditionnelle sous tout nul compatible est au plus 1.

## Énoncé
Poser
\[
p^\star=\min(u,\max(\ell,q)),\qquad
f_\star(1)=q/p^\star,\qquad
f_\star(0)=(1-q)/(1-p^\star).
\]
Alors :

1. \(\mathbb E_p[f_\star(Y)]\le1\) pour tout \(p\in[\ell,u]\), donc le produit des facteurs reste une supermartingale sous le nul déclaré.
2. Par rapport à l’ancienne règle \(f_{old}(1)=q/u\), \(f_{old}(0)=(1-q)/(1-\ell)\), on a \(f_\star(y)\ge f_{old}(y)\) pour chaque issue. Les incréments logarithmiques arrondis vers le bas héritent de cette dominance.
3. À prédicteurs, resets et seuils identiques, le temps de première alarme de la règle projetée est au plus celui de l’ancienne règle, trajectoire par trajectoire.
4. Parmi les facteurs continus valides sur \([\ell,u]\), \(f_\star\) maximise localement l’espérance \(\mathbb E_q\log f\).

Aucun registre persistant supplémentaire n’est nécessaire.

## Contrôle
La preuve est analytique. Un contrôle rationnel indépendant du 19 octobre 2026 a vérifié validité et dominance sur 50 couples intervalle/candidate, avec trois valeurs nulles par cas, sans échec.

## Limites
La dominance du temps de première alarme ne garantit pas une amélioration uniforme de la puissance post-changement : une alarme avancée peut être une fausse alarme. L’optimalité logarithmique est locale et continue ; elle ne vaut pas automatiquement pour toute la procédure arrondie.

## Provenance
`/Recherche/02_PROGRAMMES_ACTIFS/Transformations_Autonomie/detection_correlations_2026-10-14.md`, section 13.3–13.4.