# Audit métamorphique — témoin V19 C4, L=2

- **Date :** 2026-11-10
- **Périmètre :** témoin C4 à 9 états, huit paires C4O-00…07
- **Statut :** SIMULÉ / TEST AUTOMATISÉ RÉUSSI, périmètre fini uniquement
- **Branche :** \`work/omega-metamorphic-c4-2026-11-10\`
- **PR :** #13 (brouillon)

## 1. Question

Les huit ombres calculées pour le témoin V19 C4, L=2, restent-elles cohérentes sous des transformations de représentation qui ne changent pas le système mathématique sous-jacent ?

Ce contrôle est complémentaire des vérifications existantes. Il ne reprend pas comme nouveauté le test déjà rapporté des 120 renommages des cinq états transitoires.

## 2. Base documentaire et état antérieur

Le pilote C4, L=2, et le raccord primaire consignent :
- le témoin \(T=(1,2,3,0,8,7,6,2,0)\) ;
- le cycle distingué \(0\to1\to2\to3\to0\) ;
- les huit paires et leurs ombres brutes ;
- deux vérificateurs globaux et un vérificateur local ;
- un audit de 49 congruences ;
- 120 renommages des cinq états hors cycle, avec invariance des huit classes.

Précaution de provenance : l'audit de quotients précise que le calcul a été réimplémenté dans une exécution Python séparée. Le script GitHub correspondant ne doit pas être présenté comme ayant été exécuté tel quel. Le présent script est un nouveau banc autonome, écrit pour rendre explicites les relations métamorphiques et leur exécution CI.

## 3. Fondement méthodologique

Le *metamorphic testing* répond au problème de l'oracle : au lieu de connaître à l'avance chaque sortie attendue, on vérifie des relations nécessaires entre les sorties d'entrées transformées.

Références vérifiées :

1. Sergio Segura, Gordon Fraser, Ana B. Sánchez et Antonio Ruiz-Cortés, “A Survey on Metamorphic Testing”, *IEEE Transactions on Software Engineering*, 42(9), 2016, p. 805–824. DOI : [10.1109/TSE.2016.2532875](https://doi.org/10.1109/TSE.2016.2532875). La synthèse présente la transformation des entrées et la relation attendue entre sorties comme principe du test métamorphique.
2. Sofia F. Iakusheva et Anton S. Khritankov, “A systematic review of methods for deriving metamorphic relations”, *Program Systems: Theory and Applications*, 15(2), 2024, p. 37–86. DOI : [10.25209/2079-3316-2024-15-2-37-86](https://doi.org/10.25209/2079-3316-2024-15-2-37-86). La revue classe les méthodes de dérivation des relations métamorphiques en six types.
3. “Metamorphic relation automation: Rationale, challenges, and solution directions”, *Journal of Software: Evolution and Process*, 35(1), 2023 (première publication en ligne 2022). DOI : [10.1002/smr.2509](https://doi.org/10.1002/smr.2509). La revue souligne le coût de conception des relations et rappelle qu'un test métamorphique réussi ne garantit pas l'absence de défauts.

Ces références justifient la méthode générale, pas la validité mathématique de V19.

## 4. Relations testées

### R1 — Équivariance par renommage des états

Pour une permutation \(\sigma\) des neuf états, on transporte la dynamique par conjugaison :

\[
T'=\sigma\circ T\circ\sigma^{-1}.
\]

On transporte aussi le cycle distingué et les huit paires. Les masques projetés, exprimés dans l'ordre transporté du cycle, doivent rester identiques.

Le banc vérifie les 36 transpositions \((i\,j)\) de neuf étiquettes. Il ne parcourt pas les \(9!\) permutations. Les transpositions sont les générateurs usuels du groupe symétrique, mais le test informatique ne constitue pas à lui seul une preuve formelle d'équivariance pour toutes les compositions.

### R2 — Changement de l'origine du cycle

On remplace le cycle ordonné \((0,1,2,3)\) par chacun de ses quatre décalages cycliques. Les masques doivent subir la rotation correspondante de leurs quatre coordonnées, sans autre changement.

### R3 — Complément global de l'observation binaire

Le remplacement global \(c\mapsto1-c\) doit envoyer chaque masque \(m\) sur \(m\oplus 1111_2\). Chaque ombre attendue doit donc être stable par cette involution.

### R0 — Contrôle de base

Avant les transformations, le programme recalcule directement les huit ombres brutes et exige l'égalité exacte avec le catalogue de référence.

## 5. Implémentation et résultat

Script autonome :
\`code/test_metamorphic_v19_c4_l2.py\`

Workflow :
\`.github/workflows/omega-metamorphic-c4.yml\`

Exécution vérifiée :
- GitHub Actions run : [42777390913](https://github.com/Abrasax63/Omega-pub/actions/runs/42777390913)
- commit : \`ddcf95f3d80879ce5990305f94bf43bfb6c2570e\`
- job : \`metamorphic-c4\`
- Python : 3.12.16
- conclusion : **SUCCESS**

Sortie du programme :
\`\`\`text
BASE_WITNESS: PASS (8/8 ombres brutes)
STATE_RELABELING: PASS (36 transpositions de S_9, 8 classes chacune)
CYCLE_ORIGIN: PASS (4 origines, relation de rotation exacte)
COLOR_COMPLEMENT: PASS (8/8 ombres invariantes par c -> 1-c)
METAMORPHIC_C4: ALL CHECKS PASSED
\`\`\`

## 6. Limites et interprétation

- **SIMULÉ / TEST AUTOMATISÉ RÉUSSI** pour le témoin et les huit paires indiqués.
- Ce résultat ne prouve pas le théorème de petit modèle L+2 pour tous les systèmes.
- Il ne prouve pas la minimalité globale N=9 au-delà du périmètre déjà établi.
- Il ne remplace pas les vérificateurs globaux ou local, ni l'audit des quotients.
- Il ne démontre aucune nouveauté bibliographique.
- Les relations R1–R3 sont des contrôles de représentation ; elles ne sont pas des invariants physiques ou de nouvelles propriétés structurelles de la dynamique.

## 7. Suite proposée

1. Ajouter des tests de mutation volontaire : modifier une arête forcée, inverser une égalité de trajectoire ou permuter incorrectement les coordonnées du cycle ; vérifier que le banc échoue.
2. Étendre ensuite le générateur à d'autres témoins déjà validés, sans extrapoler depuis C4.
3. Ne considérer une généralisation qu'après comparaison avec les définitions primaires et une vérification indépendante.

Aucune promotion de statut scientifique, aucune écriture SQLite, aucune fusion et aucune modification de \`main\`.
