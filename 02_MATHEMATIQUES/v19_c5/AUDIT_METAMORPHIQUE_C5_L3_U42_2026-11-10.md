# Audit métamorphique — témoin V19 C5, L=3, U42

- Date : 2026-11-10
- Témoin : U42, 42 états, cycle C5
- Horizon : L=3 ; préfixes vérifiés jusqu'à L+2=5
- Paire : (0,20), archivée dans le triple U42 comme C5O-13
- Branche : \`work/omega-metamorphic-c5-l3-2026-11-10\`
- Statut : test automatisé sur un témoin fini ; aucune certification générale

## 1. Pourquoi ce second témoin ?

Le banc C4 précédent contrôlait un témoin à neuf états et un cycle de longueur quatre, pour L=2. Le présent cas change simultanément la taille du cycle, l'horizon et la structure de l'extension : U42 contient 42 états.

Le dossier V19 C5/L=3 indique que le catalogue local a été calculé à partir des deux trajectoires jusqu'au temps 5, conformément à la borne L+2, et que le témoin U42 couvre les 14 classes orientées C5. Le présent test ne réexécute pas les 560 triples : il isole un témoin archivé, C5O-13, et vérifie la robustesse de son calcul.

Données de référence :
- \`research/data/v19_c5/V19_UNIVERSAL10_U42_2026-10-15.json\`
- \`research/data/v19_c5/V19_TRIPLE_WITNESSES_C5O14_U42_2026-11-04.csv\`
- \`02_MATHEMATIQUES/v19_c5/AUDIT_V19_C5_L3_2026-11-05.md\`

Le témoin a :
\[
T=(1,2,3,4,0,0,1,2,3,4,5,5,\ldots,19,19,41,40)
\]
avec cycle distingué \(B=(0,1,2,3,4)\) et paire initiale \((0,20)\). La trajectoire du second état commence \(20\to10\to5\to0\), tandis que le premier suit le cycle. Le préfixe de contrôle contient donc le cycle et les états des deux trajectoires jusqu'au temps 5.

## 2. Méthode

Le test compare les ombres obtenues par deux implémentations :
- union-find à parité ;
- propagation de contraintes dans le graphe, en fixant chacune des \(2^5=32\) colorations du cycle.

Il compare ensuite le calcul global sur les 42 états au calcul local restreint au cycle et aux deux préfixes jusqu'à \(L+2=5\).

Relations métamorphiques :
1. **Renommage d'états** : conjugaison \(T'=\sigma T\sigma^{-1}\), transport du cycle et de la paire. Les 861 transpositions des 42 étiquettes sont testées.
2. **Origine du cycle** : les cinq rotations de l'ordre du cycle doivent entraîner la rotation correspondante des masques.
3. **Complément binaire** : \(c\mapsto1-c\), donc \(m\mapsto m\oplus11111_2\).
4. **Contrôle négatif** : remplacer les égalités du mauvais événement par des inégalités doit changer l'ombre.
5. **Équivalence des solveurs** : les deux algorithmes doivent produire exactement le même ensemble de masques.

## 3. Référence méthodologique

Elkawakjy et Catal, “Metamorphic relation automation: Rationale, challenges, and solution directions”, *Journal of Software: Evolution and Process*, 35(1), 2023, DOI [10.1002/smr.2509](https://doi.org/10.1002/smr.2509). La revue décrit les relations métamorphiques comme des relations attendues entre sorties de plusieurs exécutions et avertit qu'une relation satisfaite ne garantit pas l'absence de défauts ; une violation, en revanche, signale un défaut à investiguer.

Raunak et Olsen, “Metamorphic Testing on the Continuum of Verification and Validation of Simulation Models”, MET 2021, DOI [10.1109/MET52542.2021.00015](https://doi.org/10.1109/MET52542.2021.00015). Les auteurs examinent l'emploi du test métamorphique dans la vérification et la validation de modèles de simulation.

Ces publications justifient la démarche de test, pas le lemme mathématique V19.

## 4. Implémentation

Script : \`research/code/test_metamorphic_v19_c5_l3.py\`

Workflow : \`.github/workflows/omega-metamorphic-c5-l3.yml\`

Le script vérifie explicitement la taille 42, le cycle, la paire (0,20) et les premiers pas de trajectoire du témoin archivé. Il ne lit pas de données externes au runtime : les constantes sont recopiées depuis les entrées versionnées afin de rendre l'exécution CI autonome. Les références des sources sont consignées dans le présent rapport.

## 5. Portée et limites

- Le contrôle porte sur une seule paire C5O-13 dans U42, pas sur les 560 triples.
- Les 861 transpositions sont testées explicitement ; le programme n'énumère pas les \(42!\) permutations.
- L'égalité des ombres globales et locales sur ce témoin ne démontre pas le lemme L+2 pour tous les systèmes.
- Les deux solveurs partagent les mêmes définitions des arêtes forcées et du mauvais événement. Leur diversité algorithmique réduit certains risques d'implémentation, mais ne vérifie pas indépendamment la justesse des définitions.
- Le test négatif vérifie une mutation déterminée ; il ne mesure pas la couverture générale des défauts.
- Aucune preuve Lean nouvelle n'est ajoutée et aucun statut théorique n'est promu.

## 6. Verdict attendu

Si le workflow passe, le statut sera : **CALCUL EXACT / TEST AUTOMATISÉ RÉUSSI sur le témoin U42, paire C5O-13, L=3**.

Si une divergence global/local ou entre solveurs apparaît, elle devra être conservée comme contre-exemple expérimental et auditée avant toute correction. Aucun résultat ne sera remplacé silencieusement.
