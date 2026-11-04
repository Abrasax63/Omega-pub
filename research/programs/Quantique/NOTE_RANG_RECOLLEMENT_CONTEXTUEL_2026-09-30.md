# Rang du recollement des interventions : seuil exact et contrôle des données

**RQ-Q-4 — 30 septembre 2026.** Suite de RQ-Q-3. On attaque l'extension de l'ambiguïté processus–instruments à un premier canal proche de l'identité, puis on examine les dix tableaux de comptage publics. Aucune nouvelle acquisition n'a eu lieu.

## 1. Identité non sélective

Fixons une préparation initiale \(a\), un axe intermédiaire \(m\), une préparation logique \(r\), et une issue finale \(z=(c,d)\). Un peigne \(W\) interrogé par les instruments idéaux

$$
\mathcal M_{m,b,r}(\rho)=\operatorname{tr}(\Pi_{m,b}\rho)\rho_r
$$

donne \(p_W(a,m,b,r,z)\). Puisque \(\Pi_{m,0}+\Pi_{m,1}=I\), la somme

$$
S_m^z(a,r):=\sum_b p_W(a,m,b,r,z)
=\operatorname{tr}[W(\rho_a^T\otimes I\otimes\rho_r^T\otimes E_z)]
$$

est **identique pour tous les axes \(m\)**, même si \(W\) a une mémoire temporelle. Il s'agit d'une relation linéaire de surcomplétude des interventions, dont la pertinence en tomographie autocohérente est connue [Li *et al.*](https://arxiv.org/html/2307.14696v4). La somme des deux lignes assemblées sous la même étiquette \(r\) est le test employé ici.

## 2. Théorème de rang commun

**DÉMONTRÉ.** Pour un ensemble fini \(A\) de préparations accessibles, des contextes \(m\in M\) et des issues \(b\in B\), formons la matrice observable

$$
P_m(a,b)=P(B=b\mid a,m).
$$

Supposons qu'un modèle alternatif markovien avec instrument de sortie locale ait

$$
p(a,m,b,r,z)=P_m(a,b)\,f_{m,b,r,z}.
\tag{1}
$$

La réponse finale \(f\) peut dépendre de l'axe, de l'issue, de la porte et de la question finale, **mais pas de \(a\) au-delà de \(b\)**. Si les mêmes probabilités admettent une représentation avec les instruments idéaux du §1, posons \(E_m=\operatorname{col}(P_m)\subseteq\mathbb R^A\). Si chaque \(P_m\) a plein rang colonne et si

$$
\bigcap_{m\in M}E_m=\operatorname{span}\{\mathbf1_A\},
\tag{2}
$$

alors \(f_{m,b,r,z}=f_{r,z}\) pour tous \(m,b\). Lorsque les états et effets idéaux sont tomographiquement complets et qu'un peigne physique les réalise, **ce peigne est le produit de ses deux canaux temporels**.

*Preuve.* L'identité du §1 donne un même vecteur \(h_{r,z}\in\mathbb R^A\) pour tous les axes. Par (1), \(h_{r,z}=P_m f_{m,r,z}\), donc \(h_{r,z}\) appartient à l'intersection (2) et vaut \(f_{r,z}\mathbf1_A=P_m(f_{r,z}\mathbf1_B)\). L'injectivité de \(P_m\) donne \(f_{m,r,z}=f_{r,z}\mathbf1_B\). Les probabilités se factorisent entre les interventions avant et après \(B\). Leurs produits engendrent l'espace hermitien complet ; l'unicité de la forme bilinéaire impose \(W=J_{\rm premier}\otimes J_{\rm second}\). **Fin.**

**Invariance.** Ces rangs et dimensions d'intersection sont conservés par permutation des préparations, issues et contextes et par duplication des préparations. Ils sont définis au niveau des probabilités étiquetées accessibles. Retirer des préparations peut changer le résultat : c'est un invariant *relatif à l'expérience*, non une propriété du micro sans accès défini.

**Barrière.** Une mesure non destructive peut laisser à la sortie de l'instrument de l'information sur \(a\) qui n'est pas contenue dans \(b\). Elle viole alors (1). Une dérive ou une erreur qui dépend directement de la préparation initiale sort aussi du théorème. Rien ne prouve que ces mécanismes soient absents des puces étudiées.

## 3. Seuil Pauli et borne robuste

**DÉMONTRÉ.** Si le premier canal est dépolarisant \(J_t\), les préparations \(a\in\{\pm X,\pm Y,\pm Z\}\) donnent

$$
P_m(a,0)=\tfrac12(1+t a_m).
\tag{3}
$$

Pour \(t>0\), chaque \(P_m\) a rang 2. Les fonctions \(\mathbf1_A,a_m,a_n\) sont indépendantes dès que \(m\ne n\), donc (2) est satisfaite. Le théorème vaut **pour tout \(t>0\)**, même arbitrairement petit. À \(t=0\), tous les \(P_m\) ont rang 1 : les contre-exemples de RQ-Q-3 exploitent exactement cette exception. Leur prolongement direct vers \(t>0\), en gardant l'hypothèse (1), est **RÉFUTÉ**.

**DÉMONTRÉ — forme quantitative.** Soit \(\delta=\max_{a,m,n,r,z}|S_m^z(a,r)-S_n^z(a,r)|\) dans le tableau candidat (1). Sous (3), pour tout \(m,r,z\),

$$
|f_{m,0,r,z}-f_{m,1,r,z}|\le 2\delta/t.
\tag{4}
$$

Comparer \(a=m_+\) et \(a=m_-\), puis un axe \(n\ne m\) : leur différence sur \(n\) vaut zéro, celle sur \(m\) vaut \(t(f_{m,0}-f_{m,1})\). Deux erreurs d'au plus \(\delta\) donnent (4). La constante \(2/t\) est optimale **pour une question finale scalaire** : \(f_{m,0}=1/2+q/2\), \(f_{m,1}=1/2-q/2\) donnent \(\delta=tq/2\). Ce cas d'égalité scalaire n'est pas présenté comme un jeu tomographique complet de portes CPTP.

**FALSIFICATION ANTICIPÉE.** Si l'un des \(P_m\) a rang 1, un contraste de ses deux réponses peut rester caché malgré une intersection égale aux constantes. Si les \(P_m\) sont tous identiques et de rang 2, leur intersection garde une direction non constante et la conclusion échoue également. Le programme reproduit ces deux petits contre-exemples rationnels. Les hypothèses (2) et de plein rang sont nécessaires à cette conclusion générale.

## 4. Audit des dix acquisitions publiques

**CALCUL EXACT — raccordement des lignes.** Pour chacune des 324 lignes \(a,m,r,c\) de chaque acquisition, le nombre d'issues 0 de la ligne \(r\) plus le nombre d'issues 1 de la ligne \(-r\) vaut exactement **8 000 pour les neuf séries IBM** et **9 216 pour la série UQ** : 3 240 égalités entières. Parmi les six étiquettes possibles, \(-r\) est l'unique partenaire global de \(r\) vérifiant cette conservation sur toutes les séries. Les deux fichiers locaux ont exactement les identifiants de contenu Git des données du [dépôt des auteurs](https://github.com/Christina-Giar/NMN-tomo) : IBM feaf45fdb64d404acedd5a7acb7fa8c4e6b508b9 ; UQ 07fd4759631e40d3002aa01d6c563b0bacd98724. Le cahier du dépôt lit les étiquettes logiques et reconstruit les peignes, sans table exploitable des identifiants d'impulsions natives. **Je ne peux pas confirmer** que la sortie matérielle de chaque mesure était \(Z_\pm\) à partir de ces fichiers.

**CALCUL EXACT — écarts descriptifs.** Dans chaque ligne, on calcule la fréquence finale \(d=1\) après somme sur \(b\), puis son étendue entre \(X,Y,Z\), pour les 108 triples \((a,r,c)\) de chaque acquisition.

| Série | Médiane des étendues | Maximum |
|---|---:|---:|
| IBM, neuf acquisitions | entre 0,006143 et 0,008306 selon la série | 0,033471 |
| UQ, une acquisition | 0,041031 | 0,137331 |

Le contraste de première issue entre les préparations \(m_+\) et \(m_-\), agrégé sur \(r,c\), va de 0,976785 à 0,981806 sur IBM ; sur UQ, il vaut 0,585383, 0,578107 et 0,722198 selon l'axe. Ces nombres **ne sont pas** des estimations indépendantes du vrai canal \(J_t\). Les tirs peuvent alimenter plusieurs lignes regroupées, et les identifiants natifs ainsi que les calibrations appariées manquent. Aucun niveau de significativité ni mécanisme physique n'est inféré de ces étendues.

Le [protocole publié](https://arxiv.org/html/2308.00750v3) décrit les six rotations et le regroupement sans rétroaction. Son exemple mesure \(X\) puis applique l'identité et annonce les sorties \(X_\pm\) ; cela ne permet pas d'identifier sans autre preuve l'architecture \(Z_\pm\) utilisée en RQ-Q-3.

## 5. Audit bibliographique et prochain verrou

**CONNU DANS LA LITTÉRATURE.** Les relations entre instruments surcomplets et le problème de leur calibration sont étudiés en [tomographie d'ensembles d'instruments](https://arxiv.org/html/2307.14696v4). Les peignes et les interventions de mesure puis préparation relèvent de la [tomographie des processus temporels](https://arxiv.org/abs/2106.11722). Le théorème de rang (2) est une conséquence algébrique spécialisée ; **je ne peux pas confirmer son originalité bibliographique** ni le présenter comme publiable à ce stade.

**Résultats de cette itération.** Le seuil \(t=0\), la condition de rang commun et la borne (4) sont **DÉMONTRÉS**. Les 3 240 raccordements entiers et les étendues rapportées sont **CALCUL EXACT**. L'extension automatique du contre-exemple intriqué de RQ-Q-3 à \(t>0\) sous (1) est **RÉFUTÉE**. L'identité précise des impulsions et le statut causal des écarts UQ sont **INDÉTERMINÉS**. Rien n'implique une modification de l'équation de Schrödinger.

**Prochain verrou.** Étudier les instruments physiquement valides qui transmettent une information sur \(a\) au-delà de \(b\) : soit trouver un contre-exemple intriqué avec premier canal proche de l'identité, soit étendre (2) aux **états conditionnels**. L'expérience décisive reste la tomographie appariée des sorties réelles des chemins \(r\) et \(-r\) avec leurs identifiants d'impulsions.

## Reproduction

Lancer python quantum_gluing_rank_audit.py dans le dossier contenant ibm_raw.json et uq_raw.json. Le programme utilise des fractions pour les certificats de rang, contrôle les 3 240 identités de comptage, les contre-tests et écrit quantum_gluing_rank_audit_result.json. Il ne calcule aucun test statistique.