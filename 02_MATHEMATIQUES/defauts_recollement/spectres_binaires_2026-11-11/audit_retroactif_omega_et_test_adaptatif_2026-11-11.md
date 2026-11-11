# Rattrapage Omega et test adaptatif à deux contrôles

11 novembre 2026. Audit ciblé des échanges récupérés et des documents retrouvés. Aucune modification du dépôt GitHub ni du registre scientifique SQLite.

## Test à deux étapes — calcul exact et exécutions observées

Quatre hypothèses H0 à H3, trois contrôles binaires sans effet sur l’état, deux contrôles au maximum. Les réponses (A,B,C) sont H0=(0,0,0), H1=(0,1,0), H2=(1,0,0), H3=(1,0,1). Un scénario est identifié uniquement si la cellule compatible est un singleton.

- Plan fixé AB : H2 et H3 restent indiscernables. Pour AC, ce sont H0 et H1. Pour BC, ce sont H0 et H2. Chaque paire identifie donc exactement deux des quatre scénarios et aucune ne garantit l'identification.
- Plan adaptatif : faire A. Si A=0, faire B. Si A=1, faire C. Chaque branche sépare les deux scénarios compatibles. Vérification exhaustive des trois paires non ordonnées et des douze arbres déterministes qui ne répètent pas un contrôle sur un chemin. Un seul arbre identifie les quatre scénarios.
- Exécutions isolées, scénario H2 choisi pour les deux avant les retours. La session à plan fixe a engagé AB, reçu (1,0) et conservé {H2,H3}. La session adaptative a engagé A, reçu 1, choisi C, reçu 0 et identifié H2. Les deux ont utilisé deux contrôles et formulé un verdict correct au vu de leur information.

Statut : CALCUL EXACT pour la table et OBSERVÉ pour les deux exécutions. La table autorise explicitement l’adaptation dans un bras. Elle mesure la valeur de cette permission dans ce cas construit. Elle ne permet pas d'attribuer un gain général à Omega. Aucun temps de vérification mesuré. L'écart entre expériences adaptatives et prédéfinies est déjà étudié dans le [rapport d’observabilité active](https://chatgpt.com/library?file_id=libfile_0533dc742d5881919c690e13abcc6610&account_id=personal).

## Résultat récupéré — plateaux avec départs restreints

**DÉMONTRÉ.** Soit T une endofonction finie, π l'observation et W_k(S) les mots de longueur k à partir de S. Si T(S)⊆S et |W₂(S)|=|W₃(S)|, les comptes restent constants. La troncature de W₃ vers W₂ est bijective, donc une paire observée a une unique extension d'un symbole. Pour deux trajectoires qui coïncident sur k≥2 observations, appliquer cette règle à leurs états au temps k−2, toujours dans S, prolonge la coïncidence.

**RÉFUTÉ pour la seule couverture des couleurs.** Sur X={0,1,2,3,4}, T=(1,2,3,4,4), π=(0,0,0,0,1). Depuis S={0,1,4}, les mots de longueur quatre sont 0000, 0001, 1111. Les comptes aux horizons 2,3,4 sont (2,2,3), bien que S couvre les deux couleurs. Sans 4, les comptes sont (1,1,2). Témoin erroné contrôlé dans l'échange : remplacer T(2)=3 par T(2)=4 fait diverger les mots depuis 0 et 1 dès la longueur trois. Les comptes deviennent (1,2,2). Les trois suites ont été vérifiées par calcul exact dans les échanges.

**Minimalité, DÉMONTRÉE.** Tout témoin avec |W₂(S)|=|W₃(S)|<|W₄(S)| contient deux départs qui coïncident sur trois observations et se séparent à la quatrième. Les partitions globales de X par mots doivent donc se raffiner strictement entre les longueurs 1 et 2, 2 et 3, puis 3 et 4. En effet, un plateau global rendrait le raffinement stable puisque X est fermé sous T. Avec au moins deux couleurs, le rang 4 comporte au moins cinq classes. Il faut donc au moins cinq états. Le témoin ci-dessus atteint cette borne.

Dépendance : [raffinement global et borne K−q+1](https://github.com/Abrasax63/Omega-pub/blob/b42b861fee12bc4e488e7f1c66e31699fe62541e/02_MATHEMATIQUES/defauts_recollement/sources/DELTA_H_STRATEGIE_COUVERTURE_2026-09-29.md#L18-L26). Provenance du témoin restreint : échange de test critique du 11 novembre 2026. Aucune revendication de nouveauté bibliographique.

## Résultat récupéré — V19 sans cohérence globale

**RÉFUTÉ.** Les préfixes jusqu’au temps L+1 ne déterminent pas l’ombre si la cohérence globale est retirée. La suffisance sous cohérence et le témoin d’optimalité au temps L figurent déjà dans l'[audit des expériences du 10 novembre, §2](https://chatgpt.com/library?file_id=libfile_5c69c941975081919374668a63e5039e&account_id=personal).

Sur X={0,1,2,a,b}, garder le cycle B=(0,1,2) et les départs 0 et 1, L=2. Dans la première complétion, a,b sont fixes. L'unique opposition forcée est a-b. L'événement force B à être constant et ses deux colorations constantes s'étendent. Dans la seconde, a et b pointent vers 0. Les états 2,a,b ont la même image, forment un triangle d'oppositions et aucune coloration ne s'étend. Les préfixes et B sont identiques. Comme le triangle rencontre B, le témoin reste valide si seules les composantes forcées qui rencontrent B ou l’événement sont prises en compte. Les deux ombres ont été contrôlées par énumération. Dans les échanges, les témoins qui prennent deux points fixes comme départs avec une égalité imposée au temps zéro échouent : ces deux points sont déjà reliés par une arête d’invariance.

## Rapprochement avec les documents existants

- P1–P4, localité L+1, échec au temps L, et résultats C4/C5 : déjà consignés dans l'audit des expériences. La [PR #18](https://github.com/Abrasax63/Omega-pub/pull/18) documente le test fini historique. Son statut ne doit pas être utilisé à la place de la preuve de l’audit.
- CL-DYN-01 à 04, périodicité ultime et non-réciproques P1/P2/P3 : contenus retrouvés dans la [note de réconciliation](https://github.com/Abrasax63/Omega-pub/blob/b42b861fee12bc4e488e7f1c66e31699fe62541e/02_MATHEMATIQUES/defauts_recollement/RECONCILIATION_CL_DYN_01_04.md). Les correspondances exactes entre identifiants historiques et fiches originales restent à établir. Le nombre historique 360 reste en quarantaine selon le [rapport pilote](https://chatgpt.com/library?file_id=libfile_7eb72f36d80481919fc6f4c300ff1246&account_id=personal).
- CL-HEY-01 et la famille cyclique citée dans les échanges d'août/septembre : pistes de rattrapage. Les extraits retrouvés ne suffisent pas à établir l'énoncé complet, la preuve et l'état d'archivage. À reprendre à partir des pièces primaires.
- Le périmètre couvre les échanges retrouvés et les documents consultés, sans garantie d'exhaustivité de l'historique ou des fichiers.

## Axe pour l’itération suivante

Donner le droit de choisir après observation aux deux bras. Comparer alors la politique effectivement choisie par chaque bras sur des tables inédites dont les embranchements sont masqués, avec un contrôle négatif où l'adaptation ne donne aucun gain. Compter les décisions correctes, les abstentions justifiées et le coût en contrôles.
