# BR-Q-SWAP-MEM-01 — Témoin SWAP de mémoire relative aux continuations

**Statut : DÉMONTRÉ interne. Version 1.0 — 2026-10-19.**

## Domaine
Deux qubits \(S,E\), opérateur SWAP \(V\), évolution unitaire engendrée par
\(H=\frac{\pi\hbar}{2\tau}(I-V)\).

## Énoncé
Comme \(V^2=I\), avec \(P_-=(I-V)/2\), on a \(U(\tau)=V\) et \(U(2\tau)=I\). À partir de \(|b,0\rangle\), \(b\in\{0,1\}\), l’évolution à \(\tau\) donne \(|0,b\rangle\) : le réduit de \(S\) est donc identique pour les deux préparations. Pourtant la même continuation pendant \(\tau\) restitue \(|b,0\rangle\) et rend \(b\) à nouveau observable sur \(S\).

Sous l’hypothèse qu’aucune mémoire extérieure au système décrit n’est disponible, un environnement de dimension 1 ne peut pas réaliser ce témoin, tandis qu’une dimension 2 suffit.

## Preuve / contrôle
Les identités de projecteur et de matrice SWAP sont exactes. Si l’environnement avait dimension 1, deux états complets identiques de \(S\) à l’instant intermédiaire évolueraient identiquement sous la même continuation et ne pourraient restituer deux valeurs différentes de \(b\). Un contrôle matriciel exact du 19 octobre 2026 vérifie \(V^2=I\), \(P_-^2=P_-\), \(I-2P_-=V\) et l’action sur les états préparés.

## Limites
Le témoin ne montre pas une mémoire irréductiblement quantique : deux étiquettes classiques peuvent reproduire ces deux préparations. Il montre seulement qu’un état réduit instantané peut être insuffisant pour prédire les continuations. Il ne réfute pas l’équation de Schrödinger.

## Provenance
`/Recherche/02_PROGRAMMES_ACTIFS/Transformations_Autonomie/theorie_transformations_2026-10-12.md`, section « Pont quantique ».