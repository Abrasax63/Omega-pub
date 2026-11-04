# Mémoire quantique à trois temps : seuil de calibration et contrôle instrumental

**Itération du 30 septembre 2026.** Cet audit poursuit [la note précédente](NOTE_VALIDATION_CONTEXTES_QUANTIQUES_2026-09-30.md). Il porte sur les dix jeux de comptages de Giarmatzi *et al.* et leurs matrices publiques `Wexp`, `Wphys`, `Wmark`. Aucun tir supplémentaire sur les puces n'a été effectué. Toutes les probabilités et valeurs de (p) calculées ici à partir des comptes supposent, sauf mention contraire, des tirs indépendants sans dérive.

## Question et statut des sources

L'expérience prépare un qubit en (a), mesure (m\in\{X,Y,Z\}) à (B), annonce une préparation (r), puis mesure (c) à (C). Les deux issues (b=0,1) sont inscrites dans les fichiers sous des *réglages logiques* communs. Le montage réalise ces préparations en exploitant la projection à (B), des rotations ultérieures et un regroupement a posteriori des résultats ; il ne commande pas nécessairement la même opération native après les deux issues. Voir [l'article, section 3](https://arxiv.org/html/2308.00750v3) et [les données publiques](https://github.com/Christina-Giar/NMN-tomo).

**CALCUL EXACT — provenance.** Les fichiers locaux `ibm_raw.json` et `uq_raw.json` sont des copies exactes des fichiers des auteurs, empreintes Git `feaf45fdb64d404acedd5a7acb7fa8c4e6b508b9` et `07fd4759631e40d3002aa01d6c563b0bacd98724`. Les trois matrices MATLAB chargées ont les empreintes Git `b2fdde1d31b0b1e3eab76200d7cb6cdabb144dcf` (`Wexp`), `0627ed3e47e9c6b3bf3eb20479b412fe5d366fea` (`Wphys`) et `af7dbb7f948b00f8b1d067361154688cf207f1d2` (`Wmark`). La convention de contraction utilisée ci-dessous est celle du peigne publié : (\operatorname{tr}[W(\rho_a^T\otimes\Pi_{m,b}\otimes\rho_r^T\otimes\Pi_{c,d})]\). Les vérifications sur les matrices utilisent le contexte (a=Z_+,m=X,r=Z_+,c=Z), sans ambiguïté due à la transposition de (Y).

## Deux hypothèses instrumentales falsifiables

**DÉMONTRÉ — lecture seule.** Avec un processus markovien (W=T_1\otimes T_2), la *même* préparation effective (\rho_r) après chaque issue (b) et une mesure finale fixe, on a (P(B=b,C=d)=P(B=b)P(C=d)). Des erreurs de classification à (B) et (C), chacune représentée par une matrice stochastique fixe et indépendante des autres opérations, préservent ce produit :

\[
P(B_{\rm lu}=u,C_{\rm lu}=v)=
\left(\sum_b K_{u|b}P(B=b)\right)
\left(\sum_d L_{v|d}P(C=d)\right).
\]

**RÉFUTÉ sous ces hypothèses :** la seule confusion de lecture, sans effet sur l'état préparé ni dépendance des circuits, ne produit aucun contraste de (C) entre les deux issues lues de (B). Cette conclusion cesse de s'appliquer si le traitement de l'issue modifie la préparation, si les matrices de lecture dépendent des réglages ou si le regroupement utilise des circuits natifs différents.

**DÉMONTRÉ — contre-modèle instrumental.** Même avec un processus physique markovien, la préparation effective (\rho_{r,b}) dépendant de (b) donne

\[
g_{m,a,r,c}=P(C=1\mid B=0,a,m,r,c)-P(C=1\mid B=1,a,m,r,c)
=\operatorname{tr}[F_c(\rho_{r,0}-\rho_{r,1})],
\quad F_c=T_2^*(\Pi_{c,1}).
\]

Une dépendance non nulle de l'issue ne certifie donc la mémoire du **processus** que si la préparation logique a été calibrée effectivement identique dans les deux branches, ou si sa différence résiduelle est bornée. C'est une ambiguïté connue entre processus et instruments, pas une réfutation du résultat publié de tomographie sous ses hypothèses instrumentales.

## Ce que les dix acquisitions permettent de trancher

Pour écarter les branches presque vides, nous conservons seulement (a\perp m) parmi les états propres de Pauli : 12 contextes (a,m) par acquisition. Nous fixons (r=Z_+,c=Z). Le contraste a été sélectionné de façon **rétrospective** dans une itération précédente ; les valeurs ci-dessous ne sont pas une confirmation prospective.

| Plateforme | (C=1\mid B=0), comptes réunis | (C=1\mid B=1), comptes réunis | Contraste (g), comptes réunis | Signes des contextes |
|---|---:|---:|---:|---:|
| IBM, neuf acquisitions | (1363/432585=0,3151\%\) | (7121/430638=1,6536\%\) | (-1,3385) point | (108/108) négatifs |
| Queensland, une acquisition | (2744/58727=4,6725\%\) | (13973/53313=26,2094\%\) | (-21,5369) points | (12/12) négatifs |

**CALCUL EXACT.** La moyenne inverse-variance des contrastes IBM vaut (-0,013246\), avec un écart-type binomial *nominal* (0,00021) et une hétérogénéité (Q=93,4) pour 107 degrés de liberté. Au Queensland, la moyenne pondérée vaut (-0,214063) et l'hétérogénéité (Q=200,2) pour 11 degrés de liberté. Les contrastes IBM (r=Z_+,c=X,Y) valent respectivement (-0,002053) et (-0,000159) ; en changeant la préparation annoncée en (Z_-) et en gardant (c=Z), le contraste vaut (+0,002981). Cela décrit une forte dépendance du couple préparation et axe de lecture. Au Queensland, les contrastes (Z_+,X) et (Z_+,Y) valent respectivement (-0,044826) et (-0,056403). L'hétérogénéité très forte de (Z_+,Z) y invalide déjà le modèle d'un contraste constant dans tous les contextes équilibrés sous le seul bruit binomial.

**CALCUL EXACT — diagnostic indépendant par addition d'entiers.** La séparation (m=X) / (m=Y,Z) donne pour IBM (450/143568-2391/143873=-0,0134844) à l'apprentissage et (913/289017-4730/286765=-0,0133354) sur les axes tenus à l'écart. Pour Queensland, les deux nombres correspondants sont (-0,2240150) et (-0,2111272). Ces fractions recoupent la sortie du programme principal avec une seconde addition directe des fichiers JSON.

## Modèle physique simple, ajustement tenu à l'écart

**REFORMULATION — modèle réduit.** Par acquisition, pour chaque issue (b) et préparation annoncée (Z_+), nous ajustons sur les seuls quatre états (a\perp X) les trois probabilités de mesure (C=X,Y,Z) après (m=X). Ces trois nombres définissent un vecteur de Bloch (s_b=(1-2p_{b,X},1-2p_{b,Y},1-2p_{b,Z})), donc un état (\rho_b=(I+s_b\cdot\sigma)/2) lorsque (\|s_b\|\le1). Avec un canal final *identité*, c'est un véritable modèle de préparations dépendant de (b) suivi d'une dynamique markovienne. Il n'ajuste **que les probabilités conditionnelles finales** ; il ne prétend pas reproduire tous les 324 réglages et leurs marges (B) à partir d'un seul canal initial.

Nous prédisons, sans réajustement, les résultats conditionnels des huit états (a\perp m) avec (m=Y,Z). La référence « préparation aveugle à (b) » ajuste ses trois probabilités finales sur les mêmes données d'apprentissage en réunissant les deux branches.

| Plateforme | États de Bloch d'apprentissage physiques ? | Tirs de vérification | Gain de log-vraisemblance, modèle (b) / référence | Déviance du modèle contre fréquences libres |
|---|---:|---:|---:|---:|
| IBM, neuf acquisitions | Oui, (18/18) | 1 727 576 | (+1417,85) | (611,57) |
| Queensland | Oui, (2/2) | 223 237 | (+3665,45) | (525,98) |

**SIMULATION — contrôle de l'adéquation, pas de la causalité.** En conditionnant sur les nombres de tirs de chaque cellule et en simulant 2 000 fois un état final commun pour chaque triplet (acquisition, (b), axe (C)), puis en le réestimant seulement avec (m=X), la déviance médiane attendue vaut **538,24** sur IBM (95e centile **613,51**) ; la déviance observée **611,57** donne (p_{\rm simulé}=0,0565). Au Queensland, la médiane est **58,33**, le 99e centile **100,08**, et la déviance observée **525,98** donne (p_{\rm simulé}<0,0005). **RÉFUTÉ sous ce modèle de tirs :** un unique couple d'états de repréparation (\rho_{Z_+,b}), stable entre tous les (a,m), suffit pour le Queensland. **INDÉTERMINÉ :** l'échec supplémentaire vient-il d'une mémoire physique, de réglages natifs dépendant de (m,a), d'une dérive ou d'autres erreurs ? Sur IBM le contrôle est proche du seuil arbitraire de 5 % ; la non-réfutation n'établit pas que la cause est instrumentale. L'ordre et la famille de contextes ont été étudiés après publication des données.

## Une borne directement testable par calibration

**REFORMULATION — seuil de calibration conditionnel.** Pour deux préparations effectives (\rho_0,\rho_1), le même canal final (T_2) et le même effet (F), la borne de distinction de Helstrom donne exactement

\[
|g|=|\operatorname{tr}F(\rho_0-\rho_1)|
\le D(\rho_0,\rho_1):=\tfrac12\|\rho_0-\rho_1\|_1.
\]

Si chaque branche est calibrée à distance au plus (\varepsilon) d'une même cible, (\lvert g\rvert\le2\varepsilon). Si l'effet final change selon la branche avec (\|F_0-F_1\|_\infty\le\eta), alors (\lvert g\rvert\le D(\rho_0,\rho_1)+\eta). Ces inégalités sont invariantes par changement de base unitaire, mais leurs valeurs sur les données sont **conditionnelles** à l'identification physique des opérations et à l'absence de dérive non bornée.

**CALCUL EXACT sous modèle statistique spécifié.** Le contraste IBM réuni (-0,0133851) exige une distance entre préparations d'au moins **1,3385 %** sous l'hypothèse markovienne avec lecture finale commune. Son intervalle binomial nominal à 95 % donne une borne inférieure de **1,2969 %** sur la grandeur du contraste. Une certification indépendante (D(\rho_0,\rho_1)<1,29\%\), avec marge pour l'incertitude et (\eta), écarterait ce contre-modèle dans ces contextes. Les valeurs correspondantes des comptes Queensland sont **21,5369 %** et **21,1264 %**, mais leur hétérogénéité impose de spécifier l'axe et le contexte avant une calibration causale.

Si les trois mesures finales sont les Pauli idéales d'un *même* qubit de sortie, le vecteur (d=(g_X,g_Y,g_Z)) satisfait (\|d\|_2=D(T_2\rho_0,T_2\rho_1)\le D(\rho_0,\rho_1)). En réunissant les mêmes 12 contextes dans chaque acquisition, cette borne vaut **1,35 à 1,87 %** sur IBM et **22,82 %** au Queensland. Si l'on **fixe en outre** le canal final à celui des matrices `Wmark` publiées, sa ligne de transfert vers (Z) a une norme comprise entre **0,961 et 0,970** sur IBM et vaut **0,689** au Queensland ; les seuls contrastes (Z) exigent alors une distance d'entrée d'au moins **1,24 à 1,55 %** sur IBM et **31,25 %** au Queensland. Cette dernière évaluation est seulement *conditionnelle à `Wmark`*, matrice elle-même reconstruite avec des instruments supposés idéaux ; elle n'est pas une calibration indépendante des portes.

Les taux de classification publiés (IBM : 0,976 et 0,973 ; Queensland : valeurs différentes à (B) et (C)) ne bornent **pas** la distance entre les états réellement préparés après les deux issues. Les auteurs précisent que leur rééchantillonnage propage la statistique de tir et la classification, mais pas les défauts systématiques de portes. Voir [l'annexe expérimentale](https://arxiv.org/html/2308.00750v3).

## Relecture des reconstructions publiées

**CALCUL EXACT.** Dans les neuf acquisitions IBM, au réglage (a=Z_+,m=X,r=Z_+,c=Z), la moyenne non pondérée des différences (P(C=1|B=0)-P(C=1|B=1)) vaut :

| Source | Moyenne des neuf contrastes | Nombre de signes négatifs |
|---|---:|---:|
| Comptages bruts | (-0,013860) | 9/9 |
| Reconstruction linéaire `Wexp` | (-0,013836) | 9/9 |
| Projection physique `Wphys` | (-0,002980) | 7/9 |
| Produit markovien `Wmark` | (0) par construction | 0/9 |

L'écart moyen absolu entre le contraste prédit par `Wexp` et les comptes bruts n'est que **0,000063**, contre **0,010880** pour `Wphys`. `Wexp` présente toutefois des valeurs propres négatives (par exemple (-0,03309) dans la première acquisition) et prédit parfois des *probabilités négatives* dans cette même expérience. La projection semidéfinie vers `Wphys` change donc substantiellement **cette coordonnée** des données tout en imposant la positivité ; il serait faux d'identifier le contraste brut, cette coordonnée projetée et la distance globale de mémoire des auteurs. Leur distance (\mathcal D(W_{phys}\|W_{mark})) reste une autre statistique. Les matrices `Wmark` représentent un **contrôle mathématique produit**, pas des acquisitions physiques indépendantes d'une puce markovienne.

## Audit adversarial de la borne « 144 réglages » de la note précédente

**DÉMONTRÉ par un second argument tensoriel.** À marginales à deux temps fixées, chaque axe (j=X,Y,Z) de (B_i) porte (4\times4\times3=48) coordonnées (\sigma_i^{A_o}\otimes\sigma_j^{B_i}\otimes\sigma_k^{B_o}\otimes\sigma_l^{C_i}), (l\ne I). Un protocole qui mesure un seul axe de (B) et prépare le *même* (r) après les deux issues produit **une** fonction linéaire de son secteur (j), obtenue par la différence des issues de (B). Il faut au moins 48 protocoles par axe, soit 144 dans cette famille. Choisir (X_+,X_-,Y_+,Z_+) à A et après B donne la matrice de vecteurs de Bloch augmentés

\[
V=\begin{pmatrix}1&1&0&0\\1&-1&0&0\\1&0&1&0\\1&0&0&1\end{pmatrix},
\qquad\det V=-2.
\]

Pour chaque (j), les 48 mesures sont le produit tensoriel de deux bases (V) et des trois axes finaux, donc de rang (4\cdot4\cdot3=48). Les 36 coordonnées restantes, (i\ne I,j=I), viennent des sommes des issues de (B), dont le rang est (3\cdot4\cdot3=36). Les rangs totalisent 180. Il s'agit d'une vérification indépendante du calcul antérieur modulo 101. **Limite :** un « protocole logique à quatre issues » peut nécessiter plusieurs circuits natifs sans feed-forward dans l'expérience étudiée ; le nombre 144 n'est pas une borne universelle de circuits physiques.

## Comparaison bibliographique et prochaine expérience

**CONNU DANS LA LITTÉRATURE.** Le critère opérationnel de Markov par coupure causale précède cet audit : [Pollock *et al.* (2018)](https://doi.org/10.1103/PhysRevLett.120.040405). La tomographie auto-cohérente traite depuis longtemps l'ambiguïté de préparation et mesure : [Merkel *et al.* (2013)](https://arxiv.org/abs/1211.0322). [Li *et al.* (2024)](https://arxiv.org/abs/2307.14696) traitent même explicitement les ensembles d'instruments et les processus non markoviens sur puce. Les auteurs des présentes données expliquent eux-mêmes les limites SPAM de leur projection : [Giarmatzi *et al.* (2025)](https://arxiv.org/html/2308.00750v3). **REFORMULATION :** ici, la séparation entre le processus et l'instrument devient un *seuil quantifié de calibration* propre à un contraste et à ces deux plateformes. **INDÉTERMINÉ :** ce seuil ou sa variante multi-contexte constituent-ils une contribution originale publiable au-delà d'une réanalyse reproductible ? Aucune revendication de nouveau principe quantique ou de modification de l'équation de Schrödinger ne suit des calculs.

**Prochain verrou le plus informatif.** Acquérir, pour les **mêmes deux chemins natifs** donnant le même (r) logique, une tomographie (X,Y,Z) de l'état immédiatement après (B), dans un ordre de circuits randomisé, avec un contrôle physique où la seconde étape est indépendante de la première. Borner expérimentalement (D(\rho_{r,0},\rho_{r,1})) et (\eta), puis figer *avant* l'acquisition le contraste et la règle (\lvert g\rvert>D+\eta). Répéter sur deux appareils. Ce protocole départagerait l'erreur instrumentale stable, la dépendance contextuelle non contrôlée et une mémoire de processus qui traverse une coupure causale calibrée. Les données archivées actuelles ne contiennent pas ce contrôle.

## Reproduction

Avec Python, NumPy et SciPy : `python quantum_calibration_audit.py`. Le programme écrit `quantum_calibration_audit_result.json` et consigne contrastes, déviances et prédictions des matrices ; les empreintes sources des comptages figurent dans `PROVENANCE_DATA.txt` et celles des matrices dans la présente note. La graine des 2 000 simulations est 20260930. L'archive livrée avec ce rapport contient script, résultat et copies des fichiers publics, conformément à la licence MIT indiquée dans `UPSTREAM_LICENSE_NMN_tomo.txt`.