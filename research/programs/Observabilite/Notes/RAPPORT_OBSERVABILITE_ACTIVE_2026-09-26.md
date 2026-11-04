# Observabilité active des systèmes finis contrôlés

## Itération du 26 septembre 2026

### Résultat exécutif

**RÉFUTÉ — conjecture de conversion locale.**

Il existe une machine de Mealy déterministe complète telle que

\[
r_{IO}<\infty,\qquad L_A<\infty,\qquad L_P=\infty.
\]

Un contre-exemple binaire comportementalement minimal à cinq états réalise exactement

\[
(r_{IO},L_A,L_P)=(2,3,\infty).
\]

Une seconde construction à cinq états, trois actions et trois sorties réalise

\[
(r_{IO},L_A,L_P)=(1,2,\infty).
\]

La mémoire locale finie du langage ne permet donc pas, même à l'ordre 1, de convertir en général une expérience adaptative en expérience prédéfinie.

La nouveauté bibliographique de ces témoins est **INDÉTERMINÉE**. Le résultat mathématique et les calculs sont certifiés ; aucune revendication de nouveauté n'est faite.

---

## 1. Convention précise pour le langage

**REFORMULATION.**

Posons \(\Sigma=A\times Y\). Un mot

\[
z=((a_1,y_1),\ldots,(a_k,y_k))
\]

est permis s'il est la trace d'au moins un état initial. Tous les états sont donc considérés comme initiaux et finaux dans le graphe étiqueté. Le langage \(L(M)\subseteq\Sigma^*\) est factoriel.

Pour traiter sans ambiguïté les mots plus courts que \(r+1\), on conserve explicitement \(L_{\le r}\). Alors \(r_{IO}\le r\) signifie que tout mot de longueur au moins \(r+1\) appartient à \(L(M)\) si et seulement si chacun de ses facteurs de longueur \(r+1\) y appartient.

Un mot interdit est minimal lorsque ses deux facteurs propres maximaux — son préfixe et son suffixe de longueur \(|w|-1\) — sont permis. Pour un langage factoriel :

\[
r_{IO}=\max_{w\in MF(L)} |w|-1
\]

si l'ensemble \(MF(L)\) des interdits minimaux est fini, et \(r_{IO}=\infty\) sinon.

Cette convention porte sur le langage unilatère de toutes les traces finies. Elle peut différer du langage bilatère après suppression des états transitoires. Le témoin binaire ci-dessous n'est pas affecté par cette subtilité : son action 0 est une permutation de tous les états, donc toute trace finie est prolongeable arbitrairement vers la gauche.

---

## 2. Contre-exemple binaire minimal dans l'univers binaire

### 2.1 Table de la machine

**DÉMONTRÉ.**

Soient \(X=\{0,1,2,3,4\}\) et \(A=Y=\{0,1\}\). Chaque cellule contient

\[
(\text{état suivant},\text{sortie}).
\]

| État | Action 0 | Action 1 |
|---:|:---:|:---:|
| 0 | (2,0) | (4,1) |
| 1 | (3,0) | (4,1) |
| 2 | (1,1) | (4,1) |
| 3 | (0,1) | (4,0) |
| 4 | (4,1) | (4,1) |

Une ADS distingue tous les états ; la machine est donc comportementalement réduite.

### 2.2 ADS optimale

**DÉMONTRÉ — \(L_A=3\).**

Politique adaptative :

1. jouer l'action 0 ;
2. si la sortie vaut 0, les états initiaux possibles sont \(\{0,1\}\), actuellement en \(\{2,3\}\) ; l'action 1 les sépare ;
3. si la sortie vaut 1, les états initiaux possibles sont \(\{2,3,4\}\), actuellement en \(\{1,0,4\}\) ; jouer 0 :
   - la sortie 1 identifie immédiatement l'état initial 4 ;
   - la sortie 0 laisse \(\{2,3\}\), actuellement en \(\{3,2\}\), que l'action 1 sépare.

La profondeur maximale vaut 3. Elle est optimale car un arbre binaire de profondeur 2 possède au plus quatre feuilles, alors que cinq états doivent être distingués.

### 2.3 Absence de toute PDS

**DÉMONTRÉ — \(L_P=\infty\).**

Considérons les paires non résolues

\[
p=\{0,1\},\qquad q=\{2,3\}.
\]

Sous l'action 0, les deux états de \(p\) produisent 0 et deviennent \(q\), tandis que ceux de \(q\) produisent 1 et deviennent \(p\). Une suite de 0 conserve donc simultanément deux paires ambiguës.

Sous l'action 1, la paire \(q\) est séparée, mais les deux états de \(p\) produisent 1 puis fusionnent dans l'état 4. Au premier 1 d'un mot prédéfini, l'une des deux paires se trouve nécessairement en position \(p\) et fusionne irréversiblement. Sans 1, les paires restent ambiguës. Aucun mot prédéfini ne distingue les cinq états.

Certificat par automate des paires : depuis l'ensemble initial des dix paires, les seuls masques pertinents sont

- \(U_0\), toutes les paires ;
- \(\{01,04,14,23\}\) ;
- \(\{01,23\}\) ;
- le poison diagonal \(\{44\}\).

L'ensemble vide n'est jamais atteint.

### 2.4 Mémoire locale exacte

Posons

\[
A=(0,0),\quad B=(0,1),\quad C=(1,0),\quad D=(1,1).
\]

**DÉMONTRÉ — antidictionnaire exact.**

Les mots interdits minimaux sont exactement :

- longueur 2 : `AA`, `BC`, `CA`, `CC`, `DA`, `DC` ;
- longueur 3 : `ABB`, `BBA`, `CBA`, `DBA`.

Il n'en existe aucun de longueur supérieure. Ainsi les facteurs de longueur 3 suffisent, tandis que `ABB` est interdit bien que `AB` et `BB` soient permis.

**DÉMONTRÉ — \(r_{IO}=2\).**

Le cœur productif de l'automate des interdits minimaux ne contient que cinq sommets et est acyclique. La longueur maximale d'un interdit minimal est 3.

---

## 3. Minimalité binaire certifiée

### 3.1 Quatre états

**CALCUL EXACT.**

Les \(8^8=16\,777\,216\) machines binaires complètes à quatre états ont été réénumérées sans quotient :

- ADS : 9 400 320 ;
- ADS sans PDS : 36 864 ;
- ADS sans PDS et \(r_{IO}<\infty\) : 0.

Cela reproduit indépendamment l'état de départ.

### 3.2 Cinq états

**CALCUL EXACT.**

Une action binaire sur cinq états possède \(10^5\) tables possibles. L'action 0 a été canonisée sous les 120 permutations d'états et l'inversion de sa sortie ; il reste 538 représentants. L'inversion est ici le renommage bijectif \((0,y)\mapsto(0,1-y)\) des symboles I/O : elle préserve les égalités de sorties, les expériences et les facteurs locaux. Pour chacun des 538 représentants, les \(10^5\) tables de l'action 1 ont été parcourues sans réduction :

\[
538\times100\,000=53\,800\,000
\]

occurrences représentatives.

Cette famille couvre toutes les \(10^{10}\) machines étiquetées : toute première action est équivalente à l'un des 538 représentants, puis la seconde action est libre. Des doublons subsistent ; les nombres ci-dessous ne comptent donc ni des classes d'isomorphisme ni toutes les machines étiquetées.

Résultats :

- ADS : 23 096 292 occurrences ;
- ADS sans PDS : 133 760 ;
- ADS sans PDS avec \(r_{IO}<\infty\) : 128 ;
- les 128 ont \(r_{IO}=2\) ;
- 64 ont \(L_A=3\), 64 ont \(L_A=4\) ;
- aucune n'a \(r_{IO}\le1\).

La profondeur ADS a été recalculée par relaxation de Bellman jusqu'au point fixe.

**CALCUL EXACT — minimum lexicographique dans l'univers binaire :**

\[
(|X|,|A|,|Y|,r_{IO},L_A)=(5,2,2,2,3).
\]

Avec une seule action, une stratégie adaptative ne dispose d'aucun choix et se réduit à l'unique expérience prédéfinie. Avec une seule sortie, plusieurs états ne sont pas identifiables. Les alphabets binaires sont donc minimaux.

**INDÉTERMINÉ — minimum global.**

La minimalité parmi les machines à quatre états et alphabets non binaires n'a pas été exhaustive­ment tranchée.

---

## 4. Contre-exemple d'ordre local 1

Ce second témoin montre que l'échec n'est pas un effet d'une mémoire locale déjà longue.

**DÉMONTRÉ.**

États \(P_0,P_1,Q_0,Q_1,S\), actions \(a,b,c\), sorties \(0,1,2\). Chaque cellule vaut « sortie, état suivant ».

| État | a | b | c |
|---|---|---|---|
| \(P_0\) | \(0,P_0\) | \(0,S\) | \(2,S\) |
| \(P_1\) | \(0,P_1\) | \(1,S\) | \(2,S\) |
| \(Q_0\) | \(1,Q_0\) | \(2,S\) | \(0,S\) |
| \(Q_1\) | \(1,Q_1\) | \(2,S\) | \(1,S\) |
| \(S\) | \(2,S\) | \(2,S\) | \(2,S\) |

**DÉMONTRÉ — \(L_A=2\).** Jouer \(a\). La sortie 0 sélectionne \(P_0,P_1\), séparés par \(b\) ; la sortie 1 sélectionne \(Q_0,Q_1\), séparés par \(c\) ; la sortie 2 identifie \(S\). Une seule étape, avec trois sorties, ne peut produire cinq feuilles.

**DÉMONTRÉ — \(L_P=\infty\).** Avant la première action différente de \(a\), les deux paires restent intactes. Si cette action est \(b\), \(Q_0,Q_1\) fusionnent dans \(S\) avec la même sortie 2 ; si elle est \(c\), \(P_0,P_1\) fusionnent de la même manière.

**DÉMONTRÉ — \(r_{IO}=1\).** Les neuf symboles action-sortie sont permis. Les bigrammes permis sont exactement :

- `a0` suivi de `a0`, `b0`, `b1` ou `c2` ;
- `a1` suivi de `a1`, `b2`, `c0` ou `c1` ;
- chacun de `a2`, `b0`, `b1`, `b2`, `c0`, `c1`, `c2` suivi de `a2`, `b2` ou `c2`.

Ces 29 bigrammes décrivent tout le langage ; les 52 autres sont les interdits minimaux. L'ordre zéro échoue car tous les symboles sont permis mais, par exemple, `a1 a0` est interdit.

**DÉMONTRÉ — ordre zéro impossible pour un contre-exemple.** Si \(r_{IO}=0\) et qu'une action possède deux sorties possibles, toutes les suites de ces deux symboles sur l'action répétée devraient être permises. Cela donnerait \(2^k\) traces pour l'entrée répétée de longueur \(k\), contre au plus \(|X|\) traces produites par les états initiaux. Chaque action a donc une sortie constante sur \(X\), et aucun état initial distinct n'est identifiable. L'ordre 1 est ainsi le plus petit ordre local compatible avec une ADS non triviale.

---

## 5. Algorithme exact pour \(r_{IO}\)

**DÉMONTRÉ.**

Pour un symbole \(z=(a,y)\) et \(B\subseteq X\), posons

\[
\Delta(B,z)=\{T(x,a):x\in B,\ \lambda(x,a)=y\}.
\]

Après le premier symbole d'un candidat interdit minimal, suivre simultanément :

- \(B\), l'image du mot entier lu ;
- \(C\), l'image du même mot privé de son premier symbole.

Toujours \(B\subseteq C\). Un état vivant vérifie

\[
\varnothing\ne B\subsetneq C\subseteq X.
\]

Sous le symbole \(z\), calculer \(B'=\Delta(B,z)\) et \(C'=\Delta(C,z)\).

- Si \(B'=\varnothing\ne C'\), un interdit minimal est terminé.
- Si \(\varnothing\ne B'\subsetneq C'\), continuer en \((B',C')\).
- Sinon, cette branche ne peut pas produire un interdit minimal.

Après restriction aux sommets accessibles et coaccessibles à une sortie terminale :

- un cycle donne des interdits minimaux arbitrairement longs, donc \(r_{IO}=\infty\) ;
- si le cœur est acyclique, son plus long chemin donne exactement la longueur maximale des interdits minimaux.

Il n'y a aucune troncature d'horizon.

Si \(b\) est le nombre de classes comportementales, le nombre de paires strictes non vides \(B\subsetneq C\subseteq[b]\) vaut

\[
3^b-2^{b+1}+1.
\]

**DÉMONTRÉ — borne :**

\[
r_{IO}<\infty\quad\Longrightarrow\quad
r_{IO}\le 3^b-2^{b+1}+1.
\]

Pour \(b=5\), cela donne \(r_{IO}\le180\). La nouveauté bibliographique de cette écriture explicite est **INDÉTERMINÉE**.

---

## 6. Pourquoi l'intuition de preuve échoue

**REFORMULATION.**

L'absence de PDS est exactement une obstruction dans l'automate simultané des paires non résolues : aucun mot d'entrée n'envoie l'ensemble initial de toutes les paires vers l'ensemble vide.

L'existence d'une ADS est exactement une propriété gagnante dans un jeu de croyances ramifié : à chaque nœud, une action doit conserver l'injectivité dans chaque branche de sortie, puis toutes les branches doivent être gagnantes.

Ces deux objets ne sont pas le graphe des follower sets du langage. Le témoin binaire possède un cycle/trap de paires ambiguës, alors que le cœur productif de ses mots interdits minimaux est acyclique. Le témoin ternaire pousse la séparation plus loin : son langage est déjà 1-step.

**RÉFUTÉ — lemme pressenti.**

Une obstruction cyclique à la PDS ne force pas un cycle productif dans les follower sets et n'implique pas \(r_{IO}=\infty\).

La cause est une opération de test destructif : une action peut résoudre une branche tout en fusionnant irréversiblement une autre. L'adaptation choisit le test en fonction de la branche observée ; un mot prédéfini doit choisir avant de connaître cette branche.

---

## 7. Objet unificateur \(F(u,w)\)

**REFORMULATION.**

Pour une entrée \(u\) et une sortie \(w\),

\[
F(u,w)=\{x:S_u(x)=w\},\qquad \mu(u,w)=|F(u,w)|.
\]

Alors :

- le langage observable est le support \(F(u,w)\ne\varnothing\) ;
- une PDS est un mot \(u\) pour lequel toutes les fibres non vides ont taille 1 ;
- une ADS est un arbre dont toutes les fibres terminales ont taille 1 ;
- les follower sets dépendent de la croyance d'arrivée \(T_u(F(u,w))\), et pas seulement de \(F(u,w)\) comme ensemble d'états initiaux ;
- \(r_{IO}\) ne voit que le support du langage, pas les multiplicités qui gouvernent l'identification.

Le quotient comportemental conserve le langage, les interdits minimaux et \(r_{IO}\). Il ne conserve pas \(\mu_{micro}\), mais conserve \(\mu_{beh}\). Les deux témoins sont déjà réduits, donc cette ambiguïté n'intervient pas dans leur certification.

---

## 8. Audit bibliographique

**CONNU DANS LA LITTÉRATURE.**

- Les PDS, ADS et expériences diagnostiques sont classiques. Lee et Yannakakis donnent notamment un algorithme polynomial décidant l'existence d'une ADS : D. Lee et M. Yannakakis, *Testing finite-state machines: state identification and verification*, IEEE Transactions on Computers 43(3), 306–320 (1994), [doi:10.1109/12.272431](https://doi.org/10.1109/12.272431).
- Rystsov étudie une notion appelée « mémoire finie » beaucoup plus forte que \(r_{IO}<\infty\) : après une longueur uniforme, une même entrée et une même sortie imposent le même état courant. Sous cette hypothèse de state locality, il obtient un mot diagnostique. Ce résultat ne s'applique pas ici : I. K. Rystsov, *Diagnostic words for automata having a finite memory*, Cybernetics and Systems Analysis 9, 927–928 (1973), [doi:10.1007/BF01071671](https://doi.org/10.1007/BF01071671).
- Pour les langages factoriels, l'antidictionnaire des mots interdits minimaux et son lien avec les présentations finies sont classiques ; voir A. M. Shur, *Polynomial languages with finite antidictionaries*, RAIRO-ITA 42 (2008), [doi:10.1051/ita:2008028](https://doi.org/10.1051/ita:2008028), et M.-P. Béal et al., *Computing forbidden words of regular languages* (2003), [doi:10.3233/FUN-2003-561-208](https://doi.org/10.3233/FUN-2003-561-208).
- La décision « présentation sofique déterministe versus SFT » appartient à une littérature distincte ; voir J. Cai et R. M. Frongillo, *Computational complexity of problems for deterministic presentations of sofic shifts*, Theoretical Computer Science 936 (2022), [doi:10.1016/j.tcs.2022.09.017](https://doi.org/10.1016/j.tcs.2022.09.017).

**INDÉTERMINÉ.**

La recherche ciblée n'a pas trouvé de publication énonçant exactement le couplage

\[
r_{IO}<\infty\quad\text{et}\quad ADS/PDS
\]

utilisé ici, ni les deux tables explicites ci-dessus. Une absence de résultat trouvé ne prouve pas la nouveauté.

---

## 9. Prochaine expérience à plus fort gain d'information

1. Fermer la minimalité globale en testant d'abord \(|X|=4, |A|=2, |Y|=3\), avec canonisation et SAT/énumération couvrante.
2. Classifier les gadgets de « test destructif branché » qui produisent \(L_A<\infty\), \(L_P=\infty\) tout en gardant \(r_{IO}=1\).
3. Chercher une famille à alphabets bornés avec \(r_{IO}=1\) et nombre d'états arbitraire, ou démontrer une obstruction.
4. Remplacer la conjecture réfutée par une hypothèse réellement suffisante, par exemple un délai fini de détermination de l'état courant — en la distinguant explicitement de la mémoire du seul langage.

Le verrou prioritaire devient la classification des tests destructifs, non la conversion générale ADS vers PDS.

---

## 10. Reproductibilité

Les fichiers associés sont :

- `verify_counterexample.py` : vérification indépendante du témoin binaire ;
- `mealy_active_observability.py` : analyseur exact général ADS/PDS/\(r_{IO}\) ;
- `exhaustive_binary_n4.cpp` : recensement complet à quatre états ;
- `exhaustive_binary_n5_orbits.cpp` : couverture exhaustive par orbites à cinq états ;
- `search_binary_n5.cpp` : recherche pseudo-aléatoire ayant découvert le premier témoin ;
- `hamming_neighborhood_n5.cpp` : audit du voisinage de Hamming du témoin.

Commandes minimales :

```bash
python3 verify_counterexample.py
g++ -O3 -std=c++17 exhaustive_binary_n4.cpp -o exhaust4
g++ -O3 -std=c++17 exhaustive_binary_n5_orbits.cpp -o exhaust5
./exhaust4
./exhaust5
```

Résultats réexécutés dans l'environnement de calcul : le témoin Python, les \(16\,777\,216\) machines à quatre états et les \(53\,800\,000\) occurrences représentatives à cinq états concordent avec les valeurs rapportées.