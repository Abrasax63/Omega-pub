# Mémoire quantique ou instrument imparfait : certificat exact et protocole de départage

**Fiche RQ-Q-2, 30 septembre 2026.** Suite de [l'audit des dix acquisitions](AUDIT_CALIBRATION_MEMOIRE_QUANTIQUE_2026-09-30.md). Les fichiers disponibles n'incluent pas une tomographie indépendante des états immédiatement préparés après la mesure intermédiaire. Ce document construit donc un obstacle mathématique exact, puis une règle expérimentale vérifiable. **Aucune nouvelle mesure sur puce n'a été réalisée.**

## 1. Deux descriptions physiques indiscernables avec les 324 réglages

On utilise les quatre espaces qubit \(A_o,B_i,B_o,C_i\), les 6 états propres de Pauli à \(A\) et après \(B\), et les 3 axes de Pauli à \(B\) et \(C\). Pour un canal dépolarisant de facteur \(s\), soit \(J_s=s|\Phi\rangle\langle\Phi|+(1-s)I_4/2\), où \(|\Phi\rangle=|00\rangle+|11\rangle\) est **non normalisé**. Ainsi \(J_0=I_4/2\) et \(\operatorname{tr}J_s=2\). Posons \(\lambda=1/2\), \(0<\varepsilon<1/16\), et \(\lambda'=1/2+8\varepsilon\).

**DÉMONTRÉ — modèle N, processus non markovien avec interventions idéales.**

\[
W_N=J_0^{A_oB_i}\otimes J_\lambda^{B_oC_i}
+\varepsilon,I_{A_o}\otimes X_{B_i}\otimes I_{B_o}\otimes Z_{C_i}.
\]

Le deuxième terme a une trace nulle sur \(C_i\) et sur \(B_i\) ; les contraintes causales et les canaux à deux temps de \(W_N\) sont donc ceux de \(J_0\otimes J_\lambda\). La plus petite valeur propre de ce produit vaut \(1/8\) et la norme opérateur du terme ajouté vaut \(\varepsilon\), d'où \(W_N>0\) pour \(\varepsilon<1/16\). Le peigne markovien associé à ses **véritables** canaux réduits serait exactement \(J_0\otimes J_\lambda\), tandis que leur différence est non nulle ; \(W_N\) est donc non markovien au sens de factorisation des processus. Ce témoin ne démontre pas une mémoire *quantique* plutôt que classique.

**DÉMONTRÉ — modèle M, processus markovien avec instruments différents.** Prenons \(W_M=J_0\otimes J_{\lambda'}\). L'instrument annoncé « mesurer l'axe \(m\), obtenir \(b\), préparer l'état \(r\) » prépare en fait l'état de vecteur de Bloch

\[
v_{m,b,r}=\frac{\lambda}{\lambda'}r+
\frac{4\varepsilon}{\lambda'}(-1)^b\mathbf 1_{m=X}\,e_z.
\]

Les vecteurs \(r\) sont les six vecteurs unitaires de Pauli ; \(\|v_{m,b,r}\|\le(\lambda+4\varepsilon)/\lambda'<1\). La carte \(\rho\mapsto\operatorname{tr}(\Pi_{m,b}\rho)(I+v_{m,b,r}\cdot\sigma)/2\) est donc une intervention complètement positive et de trace décroissante ; la somme des deux branches conserve la trace.

**DÉMONTRÉ — égalité des probabilités.** Dans les deux modèles, pour *chaque* \(a,m,r,c,b,d\), la probabilité jointe est exactement

\[
P(b,d\mid a,m,r,c)
=\frac{1+(-1)^d\lambda r_c}{4}
+\varepsilon(-1)^{b+d}\mathbf 1_{m=X}\mathbf 1_{c=Z}.
\]

Ici \(r_c\in\{-1,0,1\}\) est la coordonnée de \(r\) selon \(c\). Pour N, la seconde ligne vient de la contraction du produit \(I\otimes X\otimes I\otimes Z\). Pour M, \(P(B=b)=1/2\), puis le canal dépolarisant \(J_{\lambda'}\) transforme \(v\) en \(\lambda r+4\varepsilon(-1)^b\mathbf1_{m=X}e_z\). Les deux expressions coïncident terme à terme. L'accord porte donc sur **324 réglages × 4 issues = 1 296 probabilités**, et subsiste avec un nombre arbitraire de tirs sur ces seuls réglages.

**CALCUL EXACT — témoin \(\varepsilon=1/64\).** Avec \(m=X,c=Z,r=X_+\), les quatre probabilités \((b,d)=(0,0),(0,1),(1,0),(1,1)\) sont \((17,15,15,17)/64\), soit un contraste \(P(C=1|B=0)-P(C=1|B=1)=-1/16\). Le vrai canal final du modèle M a \(\lambda'=5/8\), et les deux états préparés diffèrent de \(1/10\) en distance de trace. Pour tous les six états annoncés, l'écart à l'état nominal est au plus \(3/20\). Le contrôle matriciel trouve des valeurs propres minimales \(0,109375\) pour \(W_N\), \(0,09375\) pour \(W_M\), et \(0,05\) pour les états préparés. Le contrôle rationnel vérifie les 1 296 égalités ; la contraction matricielle indépendante a un écart maximal de \(5,6\times10^{-17}\).

**DÉMONTRÉ — obstacle à précision arbitraire.** L'écart maximal des préparations annoncées tend vers zéro :

\[
\max_{m,b,r}D(\rho'_{m,b,r},\rho_r)
\le\frac{6\varepsilon}{1/2+8\varepsilon}\longrightarrow0,
\]

tandis que pour chaque \(\varepsilon>0\), \(W_N\) reste non factorisable et les deux modèles restent rigoureusement indiscernables par les 324 réglages. Cela n'implique pas qu'un **effet fixé et non nul** puisse être dissimulé avec une erreur instrumentale tendant vers zéro : dans cette famille, l'effet observé vaut \(4\varepsilon\) et tend lui aussi vers zéro.

**BARRIÈRE DE GÉNÉRALISATION.** Le modèle M autorise des préparations effectives différentes selon \(m,b,r\). L'exemple ne prouve pas qu'un unique jeu de rotations natives, comme celui d'une puce donnée, réalise ces cartes. Il ne reproduit pas non plus les dix jeux de comptages publiés. Ses **vrais** canaux à deux temps diffèrent de ceux de N ; seuls leurs résultats avec les instruments annoncés sont égaux. Une mesure indépendante du canal final ou des préparations les départage.

**INVARIANCE DE REPRÉSENTATION — DÉMONTRÉ.** La proposition « il existe deux modèles physiques, l'un factorisable et l'autre non, donnant le même tableau de probabilités » est préservée par un changement unitaire cohérent des bases locales : conjuguer canaux, peignes, préparations et mesures conserve la positivité et chaque contraction. Le choix des lettres \(X,Z\) ne représente qu'une présentation commode de ce contre-exemple. Une transformation de jauge générale non unitaire n'est pas assimilée ici à une simple rotation physique et ne préserve pas nécessairement la distance de trace utilisée pour la calibration.

## 2. Règle d'expérience qui casse cette ambiguïté

**REFORMULATION — quantité opérationnelle conditionnelle.** Pour le contexte préenregistré \(A=Z_+,B=X,r=Z_+,C=Z\), mesurer \(p_b=P(C=1\mid B=b)\) et poser \(G=p_1-p_0\). Calibrer *sur les mêmes chemins natifs* l'état immédiatement après \(B\), avant l'évolution finale, pour les deux branches. Si les lectures \(X,Y,Z\) sont indépendamment calibrées et idéales dans leurs axes, les six probabilités \(u_{b,c}\) donnent

\[
D_{\rm prep}=D(\rho_0,\rho_1)
=\sqrt{\sum_{c=X,Y,Z}(u_{0,c}-u_{1,c})^2}.
\]

Un processus markovien avec le même canal final et le même effet final dans les deux branches impose \(|G|\le D_{\rm prep}\). Si l'effet effectif final dépend de la branche et si cette dépendance a été certifiée uniformément par \(\eta\ge\|F_0-F_1\|_\infty\), il impose \(|G|\le D_{\rm prep}+\eta\). Pour écarter ce modèle, la **borne inférieure** statistique du contraste doit dépasser les **bornes supérieures** calibrées de \(D_{\rm prep}\) et de \(\eta\). Sans borne crédible sur \(\eta\), aucun certificat ne sort.

**DÉMONTRÉ — validité de la règle.** La contraction de la distance de trace par un canal CPTP et la dualité de la mesure binaire donnent \(|\operatorname{tr}F(\rho_1-\rho_0)|\le D(\rho_0,\rho_1)\). L'inégalité triangulaire ajoute \(\|F_0-F_1\|_\infty\) lorsque les effets diffèrent. La règle est indépendante d'un choix de base **si les axes physiques et les effets sont réellement calibrés**. Une tomographie auto cohérente qui ne fixe pas cette référence physique ne lève pas à elle seule la liberté de représentation.

### Exécution à préenregistrer

1. **Contexte principal unique.** Figer \(A=Z_+, B=X, r=Z_+, C=Z\), la direction \(G>0\), le nombre de tirs ou la règle d'arrêt, et les budgets d'erreur avant la nouvelle acquisition. Les douze contextes équilibrés antérieurs sont exploratoires ; les autres réglages seront des tests secondaires.
2. **Chemins natifs appariés.** Conserver identifiants des circuits et portes après \(B\). Entrelacer aléatoirement les acquisitions \(b=0\) et \(b=1\), les mesures finales et les calibrations, en blocs horodatés. Le regroupement a posteriori de circuits différents doit être documenté : la préparation nominalement identique ne suffit pas. Les auteurs utilisent précisément une mesure, une rotation et un regroupement dépendant de l'issue. [Méthode expérimentale](https://arxiv.org/html/2308.00750v3).
3. **Calibrations supplémentaires.** Juste après l'opération de préparation de chaque chemin natif, lire \(X,Y,Z\) sur un jeu de tirs *séparé* des tirs du témoin. Vérifier aussi l'effet final effectif sur une base d'états préparés de façon indépendante, pour obtenir une borne uniforme \(\eta\), avec sa couverture statistique. Comparer les calibrations avant et après chaque bloc pour détecter la dérive. La tomographie locale n'a valeur de borne que si elle caractérise effectivement les mêmes opérations pendant les tirs du témoin.
4. **Contrôle produit et contrôle injecté.** Acquérir, si l'appareil le permet, une seconde étape physiquement indépendante de la première, après isolation ou remplacement par un qubit frais dont l'environnement et les commandes ont été vérifiés indépendants ; réutiliser les mêmes chemins instrumentaux. Ce contrôle doit satisfaire la règle markovienne à sa précision calibrée. Ajouter une corrélation classique *connue* sur un autre jeu de circuits pour vérifier que l'analyse la détecte. La matrice synthétique \(T_1\otimes T_2\) est seulement un contrôle de calcul, pas ce contrôle matériel.
5. **Deux plateformes, certificats séparés.** Les bornes de calibration d'une puce ne sont pas transportées vers l'autre. Répéter le plan et la règle sur chacune. En présence d'une dépendance forte au contexte comme dans les données Queensland archivées, compléter par une calibration séparée pour chaque \((a,m,r)\) étudié.

## 3. Outil de décision déjà exécuté sur les deux modèles exacts

Le programme `certificat_calibration_quantique.py` reçoit un JSON de comptages \([k,n]\) pour le témoin et pour les six lectures de calibration, plus une borne externe `eta_upper`. Il calcule des intervalles binomiaux exacts de Clopper–Pearson, avec une correction de Bonferroni sur les six probabilités de calibration et les deux probabilités du témoin. Par défaut, les budgets de non-couverture sont \(\alpha_{\rm témoin}=0,025\) et \(\alpha_{\rm calibration}=0,025\). Ce total **exclut** l'incertitude éventuelle de `eta_upper` : si celle-ci est estimée avec un risque \(\alpha_\eta\), réserver ce risque dans les budgets, par exemple \(0,02+0,02+0,01=0,05\).

**CALCUL EXACT sur données synthétiques, non expérimentales.** Avec les probabilités rationnelles du cas \(\varepsilon=1/64\) converties en un million de résultats entiers par cellule, les deux modèles donnent les *mêmes* comptes du témoin : \(468750/10^6\) pour \(b=0\), \(531250/10^6\) pour \(b=1\). Leurs **calibrations supplémentaires** donnent des conclusions différentes lorsque \(\eta=0\) est certifié :

| Jeu synthétique | Borne inférieure sur \(G\) | Borne supérieure sur \(D_{\rm prep}\) | Sortie |
|---|---:|---:|---|
| N, états immédiatement préparés identiques | 0,060006 | 0,004053 | `CERT-V` : modèle markovien calibré exclu |
| M, états de branche différents | 0,060006 | 0,102906 | `CERT-I` : indéterminé |

Ces entiers ont été construits à partir de probabilités exactes, **sans tirage aléatoire**. Le programme démontre le fonctionnement de la règle, pas une couverture empirique ni une découverte sur IBM ou Queensland. En particulier `CERT-I` ne signifie jamais « absence de mémoire ». Le programme refuse une entrée qui omet la calibration ou `eta_upper`.

## 4. Audit de nouveauté et statut du programme

**CONNU DANS LA LITTÉRATURE.** L'ambiguïté du couple processus–instruments et les changements de jauge compatibles avec les probabilités sont formulés explicitement par [Li *et al.*, exemple 2 et section 3](https://arxiv.org/html/2307.14696v4). La condition opérationnelle de Markov par coupure causale remonte au moins à [Pollock *et al.* (2018)](https://doi.org/10.1103/PhysRevLett.120.040405). [Giarmatzi *et al.*](https://arxiv.org/html/2308.00750v3) décrivent la limite des instruments idéalisés et des défauts systématiques de portes.

**REFORMULATION avec certificat exact.** Les deux peignes positifs et le jeu de 324 probabilités identiques rendent cette ambiguïté concrète pour *le protocole discuté*, y compris lorsqu'on contraint l'erreur des instruments à devenir arbitrairement petite avec l'effet. La règle de calibration utilise la distance de trace connue. Je ne peux pas confirmer que cette construction explicite soit nouvelle dans l'ensemble de la littérature, et elle ne fonde pas à elle seule un article publiable.

**RÉFUTÉ.** L'idée « répéter indéfiniment les mêmes 324 réglages suffit, sans contrôle des instruments, à séparer forcément mémoire et erreur de préparation » est fausse : les deux distributions construites sont exactement égales.

**INDÉTERMINÉ.** Quelle part du contraste des données IBM/Queensland provient réellement du processus, et quelle part vient des instruments ? Les calibrations indépendantes exigées ci-dessus ne figurent pas dans les fichiers publics étudiés. Ces calculs n'impliquent aucune révision de l'équation de Schrödinger.

**Prochain verrou à fort gain d'information.** Réaliser le jeu apparié de préparations après \(B\), fixer la borne de dérive \(\eta\) et tester \(G_{\rm bas}>D_{\rm haut}+\eta_{\rm haut}\) sur une acquisition nouvelle et préenregistrée. Si l'accès à une puce reste absent, la prochaine tâche mathématique est de chercher si cette indistinguabilité subsiste quand on impose explicitement les **mêmes portes natives** et le regroupement sans feed-forward de l'article.

## Reproduction

Dans l'archive jointe, exécuter `python quantum_instrument_gauge_witness.py` et `python certificat_calibration_quantique.py exemple_nonmark_calibre.json`, puis de même avec `exemple_markov_instrument_imparfait.json`. Dépendances : Python, NumPy, SciPy. Le premier programme vérifie les fractions, la positivité, les contraintes causales, les marginales et une contraction indépendante des matrices ; il écrit `quantum_instrument_gauge_witness_result.json`. Aucun accès réseau n'est nécessaire.