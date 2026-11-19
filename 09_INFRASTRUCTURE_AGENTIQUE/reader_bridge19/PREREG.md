# READER19 — audit mathématique exact indépendant d'implémentation (POST-HOC)

Date : 19 novembre 2026. **Préenregistrement avant le nouveau code.** Cette expérience est un contrôle de reproductibilité d'un résultat publié, pas un nouveau holdout aveugle. Branche empilée sur Reader18 (#187), `main` inchangée.

## Source et assertion existantes (connues avant ce protocole)
- Source [AUDIT_QUOTIENTS_TEMOIN9_C4_L2_2026-11-04.md](../../02_MATHEMATIQUES/defauts_recollement/AUDIT_QUOTIENTS_TEMOIN9_C4_L2_2026-11-04.md), Git blob `44f08ebe3e99ef97af8b16c98167b5f64383ce45`.
- Checker publié `02_MATHEMATIQUES/defauts_recollement/code/audit_quotients_temoins9.py` (ne pas l'importer ni le réutiliser dans le nouveau moteur), Git blob `58196b319cca13e8f138ea52b6aa57a1bc5f6e39`.
- Dynamique figée `T=(1,2,3,0,8,7,6,2,0)`.
- Paires figées `((0,1),(0,2),(1,8),(0,7),(0,6),(4,5),(1,4),(0,4))`.
- Ombres ciblées (masques de quatre bits), figées :
  `(0,7,8,15)`, `(0,5,10,15)`, `(2,7,8,13)`, `(1,6,9,14)`,
  `(0,3,4,7,8,11,12,15)`, `(0,1,4,5,10,11,14,15)`,
  `(4,5,6,7,8,9,10,11)`, `(2,3,6,7,8,9,12,13)`.
- Valeurs **déjà annoncées** à confirmer/refuser sans tolérance : 49 congruences, 9 quotients conservant cycle/paires et cohérence, taille `{5:1,6:2,7:3,8:2,9:1}`, un seul quotient conservant les huit classes d'ombres, la partition discrète; invariance des classes d'ombres sous 120 renommages des états transitoires. Ne pas ajuster l'algorithme pour forcer ces nombres après résultat.

## Algorithme indépendant
1. Générer les partitions des 9 états **par décomposition du sous-ensemble bitset** (chaque bloc contient le plus petit état restant), et non par fermeture des fusions ni par mots de croissance restreinte du vérificateur historique.
2. Tester la congruence par propriété sur les images des blocs : pour chaque bloc B, `T(B)` doit appartenir à un seul bloc. Vérifier le nombre total de partitions explorées (= Bell(9)=21 147).
3. Sur chaque congruence, former les classes quotient, vérifier que les quatre états 0,1,2,3 restent distincts, les huit couples ont des extrémités distinctes, que le degré entrant est au plus 2, et que le graphe des paires forcées est biparti. Contrôler taille et distribution.
4. Indépendamment du code source, énumérer par masques binaires les colorations forcées et les égalités à t=0,1. Former les huit ombres, puis quotienter par rotations du C4. Tester la conservation des huit classes ciblées.
5. Renommer les cinq états transitoires par les 5! =120 bijections, transporter T et les huit paires, vérifier l'invariance des huit classes pour le témoin original.
6. Conserver un journal JSON des partitions, statistiques, empreintes, condition de résultat et éventuels contre-exemples. Ajouter mutations négatives (par ex. modifier une paire ou T) **pour vérifier que le checker n'est pas codé pour retourner toujours les mêmes comptes**. Tester une dynamique non congruente manuellement construite.

## Limites et critères
Le verdict est **REPLICATION_EXACT_FINITE** seulement si toutes les valeurs préannoncées sont reproduites, et les contrôles de mutation sont discriminants. Un désaccord devient `DISAGREEMENT`, à auditer ; pas de réécriture du protocole comme si le test était indépendant.
Même un succès est une **réplication computationnelle conditionnelle aux définitions du témoin**, pas la preuve générale de minimalité N=9, pas une certification Lean, pas une revue mathématique indépendante par un tiers. Les résultats historiques sont déjà publics. **Aucun gain frontière, aucun entraînement du modèle, 0 appel API payant**, `main` inchangée.
