# Réconciliation sémantique des briques — lot 07 (11 fichiers, 9 novembre 2026)

**Dépôt :** `Abrasax63/Omega-pub`  
**Branche source immuable :** `migration/ravi2-ccs-public-2026-11-04`  
**Branche de publication :** `maintenance/reconciliation-bibliotheque-2026-11-05`  
**Périmètre :** 11 briques originales de `research/bricks/`, lues depuis la branche historique.  
**Nature du travail :** classement documentaire et rapprochement des contrats, hypothèses, dépendances et limites. Ce rapport ne constitue pas un nouvel audit de preuve.

## 1. Fichiers examinés

| Fiche | SHA Git source |
|---|---|
| `BR-Q-01_AMBIGUITE_PROCESSUS_INSTRUMENTS.md` | `f2ffb7101f8e336fb4e81910b4300dc84e0832aa` |
| `BR-Q-PRED-HIDDEN-01_BRIQUE.md` | `d90deb72f530d626f1d2c05b40578e7e72258a96` |
| `BR-Q-SWAP-MEM-01_BRIQUE.md` | `2ba76078af4e1e20ccd7c3b52bf06f20eb4cfffa` |
| `BR-STATE-01_ETATS_PREDICTIFS_REPARATION.md` | `b7f79410a589dd8ba62a997860c924593e85a73c` |
| `BR-STATE-COST-01_BRIQUE.md` | `428f7056a5345c5aa826042ed3ba9ace762157d6` |
| `BR-TIME-01_RESOLUTION_SANS_FLECHE.md` | `9c17df58ecda9940f39024bfd532ec2b1d29f156` |
| `BR-TIME-FACTOR-COMPLEX-01_BRIQUE.md` | `22b3edb62a5e9864af0062604746a236c652d8f9` |
| `BR-TIME-FINDET-BRIDGE-01_BRIQUE.md` | `b45f06100815bed0ebbcee3aea666dad93ed4d1b` |
| `BR-WORD-SINGLE-GAP-COMPLEX-01_BRIQUE.md` | `e52a7247c4aa761aa7ce09e504c89d307c06f12f` |
| `DESC-CLIP-01_BRIQUE.md` | `3bb00f533e833482baf8f81374bc3a223f98b7a4` |
| `DET-FIN-01_BRIQUE.md` | `2d320dc803533e75b77784aa2af3910eac25edd1` |

## 2. Classement sémantique

### A. Processus quantiques, mémoire cachée et prédiction

- **BR-Q-01** : construction d'une ambiguïté entre processus non markovien avec interventions idéales et processus markovien avec instruments/préparations différents. Le point réutilisable est l'impossibilité d'attribuer la mémoire au seul processus sans calibration indépendante des instruments. La fiche rapporte une égalité rationnelle sur 1296 probabilités pour un ensemble de réglages donné ; cela ne tranche pas une plateforme expérimentale ni la nature classique ou quantique de la mémoire.
- **BR-STATE-01** : définit une équivalence prédictive relative à un ensemble de tests futurs, sa minimalité comme séparation comportementale, sa stabilité sous mise à jour sous hypothèses de fermeture, et une réparation déterministe par équivalence stable. Le domaine dépend explicitement de l'ensemble des tests admis : ce n'est ni une minimalité algorithmique ni une dimension quantique.
- **BR-Q-SWAP-MEM-01** : témoin à deux qubits où un état réduit instantané identique ne suffit pas à prédire une continuation future. La mémoire d'environnement de dimension 2 suffit et dimension 1 est exclue dans le modèle fermé déclaré. Le témoin n'établit pas une mémoire irréductiblement quantique.
- **BR-Q-PRED-HIDDEN-01** : raccorde l'équivalence prédictive à des familles d'états produit et corrélés. Les conclusions annoncées sont (N_{perf}le d_E) pour la famille produit et (N_{perf}=d^2) pour la construction corrélée de dimension (d	imes d). La fiche distingue correctement nombre de classes prédictives et nombre d'histoires parfaitement distinguables ; un continuum de classes n'implique pas une dimension mémoire infinie.
- **Dépendances / distinction** : BR-Q-PRED-HIDDEN utilise explicitement BR-STATE-01 et le témoin BR-Q-SWAP-MEM-01. BR-Q-01 est une ambiguïté d'identification processus/instruments, et non une conséquence du témoin SWAP ; ces deux arguments doivent rester séparés.

### B. Réparation comportementale et coût d'extension

- **BR-STATE-COST-01** : formule un coût minimal exact en nombre d'états ajoutés, égal à la cardinalité des dérivées nouvelles dans la fermeture comportementale, sous totalité, exactitude et conservation des comportements anciens. Ce n'est pas un coût algorithmique ou probabiliste.
- **Lien avec BR-STATE-01** : les deux fiches concernent des représentations comportementales, mais leurs objets ne sont pas identiques : BR-STATE-01 quotient des histoires par indistinguabilité prédictive relative à des tests ; BR-STATE-COST-01 compte les comportements nouveaux nécessaires à une extension déterministe fermée. Ne pas transférer automatiquement la formule de coût à un modèle probabiliste ou quantique.

### C. Temps observationnel, complexité en facteurs et détection

- **BR-TIME-01** : construit une permutation réversible de période (T=m^2) dont la résolution observationnelle est d'ordre (sqrt T). La fiche précise que cette échelle de distinguabilité n'est pas une flèche du temps.
- **BR-TIME-FACTOR-COMPLEX-01** : donne une formule par régimes pour la complexité en facteurs du mot binaire sparse de BR-TIME-01. Son domaine est ce mot particulier et les entiers impairs (m\ge5), pas les dynamiques réversibles en général.
- **BR-WORD-SINGLE-GAP-COMPLEX-01** : généralise la formule de complexité en facteurs à un mot cyclique ayant un seul gap exceptionnel. La fiche identifie BR-TIME-FACTOR-COMPLEX-01 comme cas particulier avec (k=(m-1)/2), (g=2m), (h=3m). Plusieurs gaps exceptionnels sont hors domaine.
- **DET-FIN-01** : résultat sur un détecteur déterministe fini à alerte absorbante, sous plancher uniforme (eta>0) des probabilités conditionnelles positives et risque total de fausse alarme (alpha<1). Il ne porte pas sur le critère ARL classique.
- **BR-TIME-FINDET-BRIDGE-01** : combine la résolution de phase et la complexité du mot de BR-TIME-01 avec DET-FIN-01. La fiche construit des changements par décalage de phase et en déduit une perte de sensibilité conditionnelle uniforme aux changements arbitrairement tardifs. Cette conclusion est conditionnelle au modèle de changement construit, au plancher (eta) et au critère de risque total ; elle n'est pas une affirmation universelle sur les détecteurs physiques.
- **Dépendances** : BR-TIME-FACTOR-COMPLEX-01 dépend de BR-TIME-01 ; BR-TIME-FINDET-BRIDGE-01 dépend de BR-TIME-FACTOR-COMPLEX-01 et DET-FIN-01 ; BR-WORD-SINGLE-GAP-COMPLEX-01 fournit une généralisation combinatoire et récupère la formule spécialisée.

### D. Facteurs d'évidence robustes

- **DESC-CLIP-01** : projette le prédicteur (q) sur l'intervalle nul ([\ell,u]), puis définit un facteur d'évidence valide pour chaque (p\in[\ell,u]). La fiche distingue la validité sous le nul, la dominance trajectorielle sur l'ancien facteur et l'optimalité logarithmique locale. Elle avertit qu'une alarme plus précoce ne garantit pas une meilleure puissance post-changement : le risque de fausse alarme reste pertinent.

## 3. Verrous et précautions de réutilisation

1. **Ne pas confondre mémoire cachée et mémoire quantique irréductible.** Les fiches Q établissent des distinctions opérationnelles dans des modèles spécifiés ; elles ne prouvent pas une irréductibilité quantique générale.
2. **Ne pas confondre quotient prédictif et dimension physique.** Le nombre de classes peut être infini même lorsque la mémoire physique est de dimension finie ; la distinguabilité parfaite est une notion plus restrictive.
3. **Ne pas confondre résolution et irréversibilité.** BR-TIME-01 est explicitement réversible.
4. **Ne pas généraliser les formules de mots.** Les résultats de complexité sont attachés aux familles combinatoires déclarées.
5. **Ne pas élargir le théorème de détection.** DET-FIN-01 exige un automate fini fixé, un plancher conditionnel et un contrôle du risque total ; le pont temporel utilise en plus un changement construit.
6. **Ne pas confondre validité et optimalité.** DESC-CLIP-01 sépare ces propriétés et limite explicitement sa conclusion d'optimalité au critère logarithmique local.

## 4. Provenance et statut de cette réconciliation

Les statuts inscrits dans les fiches sources sont conservés comme **statuts historiques déclarés**. Les contrôles numériques, scripts, audits et volumes d'essais mentionnés dans ces fiches sont rapportés comme provenance historique ; ils n'ont pas été réexécutés dans le cadre du présent lot. Aucune preuve n'a été reconstruite ligne par ligne, aucun contre-exemple indépendant n'a été recherché ici, aucun checker/Lean/notebook n'a été exécuté et aucune certification n'est renouvelée.

Aucune base SQLite privée n'a été consultée ou modifiée. La branche historique source n'a pas été modifiée. Ce document est une classification sémantique, non une validation scientifique nouvelle.
