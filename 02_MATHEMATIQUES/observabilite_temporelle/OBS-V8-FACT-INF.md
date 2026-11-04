# OBS-V8-FACT-INF — Factorisation du polynôme d’observabilité à horizon infini

Version de migration : 0.1 — 2026-11-04
Statut RAVI-2 : DÉMONTRÉ (source interne)
Originalité externe : INDÉTERMINÉE
Publication dans ce dépôt : EXPÉRIMENTAL

## Énoncé
Soit X fini non vide et T:X→X. Une coloration c:X→[m] est génératrice si x↦(c(x),c(Tx),c(T²x),...) est injective.

Posons d_y=|T⁻¹(y)|, Per(T) l'ensemble des points périodiques, c_r(T) le nombre de cycles de période minimale r, et Q_r(z)=Σ_{e|r} μ(e)z^(r/e). Avec (z)_k=z(z−1)…(z−k+1), la factorisation est :

χ_obs(T,∞;z) = Π_{y non périodique}(z)_{d_y} · Π_{y périodique}(z−1)_{d_y−1} · Π_{r≥1} Π_{j=0}^{c_r(T)−1}(Q_r(z)−jr).

## Critère et preuve
Une coloration est génératrice si et seulement si elle est injective sur chaque fibre T⁻¹(y) et si les futurs symboliques des points périodiques sont deux à deux distincts. Sur chaque cycle, le mot cyclique doit être primitif ; deux cycles distincts de même longueur doivent recevoir des colliers primitifs distincts.

Le comptage des fibres non périodiques donne (z)_{d_y}. Pour une fibre au-dessus d'un point périodique, le prédécesseur cyclique a déjà sa couleur : les d_y−1 antécédents transitoires donnent (z−1)_{d_y−1}. Pour les c_r cycles de longueur r, les choix successifs de mots primitifs donnent Π_j(Q_r(z)−jr). Les fibres étant disjointes, les facteurs se multiplient.

Corollaire : m∞(T)=min{m : m≥Δ(T) et c_r(T)≤P_r(m) pour tout r}, où Δ(T)=max_y d_y et P_r(m)=Q_r(m)/r.

## Vérifications et limites
La note V7 rapporte une comparaison exhaustive avec l'énumération directe pour les 3 125 endofonctions à cinq états, pour q=1,2,3. L'audit V11 reconstruit une seconde preuve indépendante par codage des cycles puis propagation dans les arbres de préimages. La migration n'a pas réexécuté les scripts et ne prétend pas avoir retrouvé le script historique.

L'audit V11 indique que le critère qualitatif d'observabilité et le cas accessible « queue + cycle » sont connus. La factorisation complète pour une endofonction arbitraire fixée n'a pas été retrouvée dans les sources examinées. Cela ne prouve pas la nouveauté : originalité INDÉTERMINÉE.

Sources internes : NOTE_RECHERCHE_V7_POLYNOME_TEMPOREL.md ; NOTE_RECHERCHE_V8_FACTORIZATION_INFINITY.md ; AUDIT_V11_V8_PREUVE_ET_NOUVEAUTE.md.

Références de l'audit : Jungers & Blondel (2011), Laschov, Margaliot & Even (2013), Nicaud (1999), Domaratzki, Kisman & Shallit (2002), Vieira & Budroni (2022).

Portée : endofonctions finies déterministes, observation symbolique sans bruit, horizon infini. Ne certifie ni formule générale à horizon fini, ni extension stochastique, ni nouveauté externe, ni formalisation Lean. Aucune correspondance CL-DYN-01..04 n'est revendiquée. Aucune dépendance causale n'est déclarée.