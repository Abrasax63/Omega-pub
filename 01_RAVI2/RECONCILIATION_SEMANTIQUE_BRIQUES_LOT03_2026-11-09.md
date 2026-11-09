# Réconciliation sémantique des briques — lot 03 (11 fichiers)

Date : 9 novembre 2026  
Branche source en lecture seule : `migration/ravi2-ccs-public-2026-11-04`  
Commit source : `2f71a6b8ed03914c0b5d308520d30e0133d9e9ad`  
Branche de publication : `maintenance/reconciliation-bibliotheque-2026-11-05`

## Portée et méthode

Ce lot cible le noyau V19 C5/L=3 et ses interfaces de capacité, de circuits et de moments. Onze fiches ont été lues intégralement. Aucun script, checker, calcul ou preuve formelle n'a été exécuté. Les résultats de tests cités ci-dessous sont donc les déclarations des fiches historiques. Les empreintes sont les SHA Git des blobs du commit source indiqué dans le manifeste exhaustif.

Les statuts sont les **statuts déclarés dans les sources**, pas des statuts renouvelés. Tous les éléments de preuve, données et dépendances restent non réaudités dans ce lot.

## Fiches lues

### 1. `OBS-V19-BAD-FIBER2_BRIQUE.md`
- ID : `OBS-V19-BAD-FIBER2` v1.
- Statut déclaré : DÉMONTRÉ, certification interne RAVI-2 ; originalité INDÉTERMINÉE.
- Domaine : endofonction finie avec cycle orienté C5, observation binaire, horizon L=3, contraintes forcées cohérentes ; mauvais objet non vide à ombre propre.
- Énoncé : chaque mauvais objet propre est produit par au plus deux paires non ordonnées ; en cas de collision, les paires ont même paire-image exacte et correspondent aux deux coins opposés de même parité d'un rectangle 2×2 de préimages.
- Dépendances causales déclarées : `BR-OBS-KRYLOV-01`, `OBS-V19-FORCED-P4`.
- Mécanisme de preuve déclaré : quotient par les contraintes forcées invariantes, croissance stricte de Krylov projetée sur C5, récupération du générateur, puis analyse des fibres de T.
- Contrôles déclarés : 4 820 systèmes cohérents N=5…9, 148 120 paires propres, 132 990 mauvais objets distincts ; aucune fibre >2 ; régressions N11 et 100 systèmes supplémentaires.
- Limites : C5/binaire/L=3 ; mauvais objets non vides à ombre propre seulement ; ne borne ni les coefficients d'un circuit ni les cas d'ombre pleine/vide.
- Provenance : audit V19_BADOBJECT_FIBER2, checker exact et régression JSON mentionnés.
- Contrôle du lot : preuve, hypothèse P1–P4 et checker non réexaminés ; non réaudité.
- SHA Git source : `6aeb31c4e8b139896e4d721e4b44b86add0e8fc6`.

### 2. `OBS-V19-COEX-REGION_BRIQUE.md`
- ID : `OBS-V19-COEX-REGION` v1.
- Statut déclaré : DÉMONTRÉ, interne RAVI-2 ; originalité INDÉTERMINÉE.
- Domaine : cycle orienté C5, observation binaire, L=3, contraintes forcées cohérentes ; 70 ombres géométriques exactes.
- Énoncé : région de coexistence géométrique décrite comme produit des intervalles de capacités des 50 ombres finies et de N^20 pour les 20 ombres infinies ; aucune inégalité mixte supplémentaire au niveau des paires.
- Dépendances déclarées : `BR-OBS-CAP-03`, `OBS-V19-C5-CAPACITY` v2.
- Construction déclarée : sélection coordonnée dans des fibres disjointes, cœur fini atteignant simultanément les capacités, puis gadgets disjoints à 2-cycle pour les directions infinies.
- Résultats dérivés déclarés : ordre critique géométrique 3 ; après projection sur 14 labels orientés, bornes 10,10,10,10,40,20,∞,40,∞,60,∞,80,∞,160 ; ordre critique des labels 11.
- Limites : région au niveau des paires et ombres géométriques ; le relèvement vers mauvais objets distincts et circuits reste explicitement ouvert.
- Provenance : rapport, code, résumé JSON et projection CSV identifiés dans la fiche.
- Contrôle du lot : aucune donnée ni preuve de cofinalité rejouée ; non réaudité.
- SHA Git source : `ca222769a64c630c213235bbd47f303789f1de97`.

### 3. `OBS-V19-FIRST-OBSTRUCTION11_BRIQUE.md`
- ID : `OBS-V19-FIRST-OBSTRUCTION11` v2.
- Statut déclaré : DÉMONTRÉ, certification interne RAVI-2 ; originalité INDÉTERMINÉE.
- Domaine : C5 orienté, observation binaire, L=3, contraintes forcées cohérentes ; occurrences = paires distinctes, partage d'états autorisé.
- Énoncé : premier ordre de multiplicité interdit parmi les 14 labels orientés égal à 11.
- Région déclarée : bornes des labels C5O-00…13 ; toutes les combinaisons respectant ces bornes sont dites réalisables.
- Dépendance causale actuelle déclarée : `OBS-V19-COEX-REGION`. Les anciennes voies via `OBS-V19-UNIVERSAL10` et `OBS-V19-C5-CAPACITY` sont signalées comme historiques pour v1.
- Distinction essentielle : ordre critique géométrique 3 avant agrégation des cinq rotations ; ordre critique des labels 11 après agrégation.
- Limites : ne classe pas les supports de mauvais objets distincts ni les coefficients des circuits.
- Provenance : rapport régional v2, rapport multiplicité v1 et code de coexistence.
- Contrôle du lot : capacités et projection non recalculées ; non réaudité.
- SHA Git source : `0520f094003913ce0f53998409370af9459a2724`.

### 4. `OBS-V19-N11-BADOBJECT_BRIQUE.md`
- ID : `OBS-V19-N11-BADOBJECT` v2.
- Statut déclaré : CALCUL EXACT, certification interne RAVI-2 ; originalité INDÉTERMINÉE.
- Domaine : cinq endofonctions historiques N=11, observation binaire, L=3 ; mauvais objets affines attachés aux paires non ordonnées.
- Résultats déclarés : 42, 36, 36, 37, 38 mauvais objets distincts ; 48, 48, 48, 47, 50 paires propres avant déduplication ; fibres observées de taille 1 ou 2.
- Gap déclaré pour chacun des cinq systèmes : pas de partition exacte ; packing disjoint maximal 7 ; 2-recouvrement exact par 16 objets ; rang 15, nullité 1, noyau positif ; graphe de chevauchement non biparti.
- Dépendances : `BR-OBS-BAD-01`, `BR-OBS-CIRCUIT-01`. La fiche précise que le recomptage fini N11 est direct et ne dépend pas causalement du théorème fibre≤2.
- Limites : calcul fini sur cinq mappings N11, pas les 34 cas N12 ; ne classe pas tous les circuits positifs.
- Provenance : mappings historiques, checker exact, CSV de reconstruction, témoins JSON et audit.
- Contrôle du lot : checker et données non exécutés ; non réaudité.
- SHA Git source : `e2ba7203487ea95bfda3f7d6acb6c420507462f7`.

### 5. `OBS-V19-N11-MOMENT-GRAM_BRIQUE.md`
- ID : `OBS-V19-N11-MOMENT-GRAM` v1.
- Statut déclaré : CALCUL EXACT interne ; originalité application connue.
- Domaine : cinq mappings N11 figés à L=3, colorations admissibles uniformes, masques indépendants sur sommets originaux.
- Énoncé : matrices de moments polynomiales et rangs/nullités déclarés ; conservation des cinq supports historiques de 2-recouvrement ; identités de couverture vérifiées dans les fixtures.
- Valeurs déclarées : mauvais objets distincts 42/36/36/37/38 ; rangs 30/24/24/25/24 et nullités 12/12/12/12/14 à plusieurs valeurs de p ; rang 15 et noyau `ones` pour chacun des supports de 16.
- Dépendance / interface : théorème `BR-OBS-REVEAL-KERNEL` pour l'extension des rangs à p<1 ; données fixtures et supports historiques figés.
- Limites : aucune conclusion universelle N12 ou fibre≤2 ; conservation de couvertures historiques, pas nouvelle résolution de coexistence.
- Provenance : rapport `V19_N11_MOMENTS_ET_NOYAU_2026-10-15.md`, archive de preuves et données.
- Contrôle du lot : 7 169 entrées, 35 845 évaluations et 2 048 masques rapportés mais non rejoués ; pas de compilation formelle ni validation humaine externe déclarées.
- SHA Git source : `b00d2c50740c352c7f560556f49519ca173b8215`.

### 6. `OBS-V19-N11-THIRD-ORDER_BRIQUE.md`
- ID : `OBS-V19-N11-THIRD-ORDER` v1.
- Statut déclaré : CALCUL EXACT interne ; originalité NON_EVALUE.
- Domaine : cinq mappings N11 figés, L=3, prior uniforme admissible et révélation indépendante des sommets originaux.
- Énoncé : des triples ont mêmes lois individuelles et mêmes trois lois jointes par paires, mais des probabilités d'intersection triple différentes (1/16 contre 0 dans les témoins décrits).
- Contrôles déclarés : 41 966 polynômes triples, 2 048 masques originaux, comparaisons coefficient par coefficient ; 15 comparaisons de lois jointes complètes.
- Dépendances / interface : indexation des mauvais objets distincts normalisés et fixtures N11 figées ; la fiche renvoie au rapport troisième ordre.
- Limites : n'établit aucune nouvelle couverture ni coexistence générale ; les témoins sont dans les familles complètes, pas les supports particuliers de 16 objets.
- Provenance : `V19_TROISIEME_ORDRE_2026-10-15.md`, archive de preuves.
- Contrôle du lot : polynômes, appariements et masques non recalculés ; non réaudité.
- SHA Git source : `6350cf79fb40dcac70200aeb1e995d31e3135225`.

### 7. `BR-OBS-CAP-02_SUPPORT_VS_WEIGHT.md`
- ID : `BR-OBS-CAP-02`.
- Statut déclaré : DÉMONTRÉ interne RAVI-2 ; originalité reformulation spécialisée / indéterminée.
- Domaine : témoins, mauvais objets distincts, projection géométrique et circuits positifs.
- Énoncé : distingue multiplicité de support `r_C(ω)` et poids projeté `A_C(ω)`; établit `r_C(ω)≤μ_T(ω)≤ν_T(ω)≤Cap(ω)`.
- Non-théorème central : la capacité ne borne pas en général les coefficients positifs des circuits.
- Dépendance déclarée : `BR-OBS-CAP-01`.
- Limites : une borne sur les coefficients exige une hypothèse supplémentaire de poids unitaire ou une interprétation en témoins distincts.
- Application : V16/V17, circuits multi-recouvrement ; la capacité contraint le support dynamique mais pas automatiquement les poids.
- Contrôle du lot : preuve et exemples de circuits non vérifiés ; non réaudité.
- SHA Git source : `3b5f4a645de2520e7ddd461ef98dd116d3b5fbd7`.

### 8. `BR-OBS-CIRCUIT-01_2COVER_BIPARTITE.md`
- ID : `BR-OBS-CIRCUIT-01`.
- Statut déclaré : DÉMONTRÉ interne RAVI-2 ; originalité principe connu / reformulation spécialisée.
- Domaine : 2-recouvrement exact d'un ensemble fini par des blocs distincts.
- Énoncé : une sous-famille partitionne exactement l'ensemble si et seulement si le graphe de chevauchement des blocs est biparti ; une obstruction contient donc un cycle impair.
- Dépendance : utilisée par `OBS-V19-N11-BADOBJECT`.
- Limites : ne s'étend pas directement aux k-recouvrements pour k>2.
- Application déclarée : les cinq gaps N11 ont un 2-recouvrement par 16 mauvais objets et des graphes non bipartis.
- Contrôle du lot : preuve et graphes témoins non reconstruits ; non réaudité.
- SHA Git source : `8f2b165a16b050423d340e06f3fd231edb6ed314`.

### 9. `BR-OBS-KRYLOV-01_GENERATOR_RECOVERY.md`
- ID : `BR-OBS-KRYLOV-01`.
- Statut déclaré : DÉMONTRÉ interne RAVI-2 ; originalité principe connu / reformulation spécialisée.
- Domaine : endomorphisme sur espace vectoriel ; sous-espace de Krylov de longueur L de dimension L et croissance stricte au pas suivant.
- Énoncé : si deux vecteurs engendrent le même sous-espace de Krylov de longueur L sous ces hypothèses, ils sont proportionnels ; sur F₂, ils sont égaux.
- Dépendance / application : forme quotient utilisée dans `OBS-V19-BAD-FIBER2`.
- Limites : conclusion fausse en général sans croissance stricte ; sur un corps non binaire, seulement à scalaire près.
- Contrôle du lot : preuve algébrique élémentaire non vérifiée indépendamment ; non réaudité.
- SHA Git source : `de2ecdd2ea5ded00261e92c77daaf260fc25189b`.

### 10. `BR-OBS-REVEAL-KERNEL_BRIQUE.md`
- ID : `BR-OBS-REVEAL-KERNEL` v1.
- Statut déclaré : DÉMONTRÉ interne ; originalité application connue.
- Domaine : espace probabilisé fini, indicatrices, covariance, événement observable de révélation complète indépendant de l'état et de probabilité positive ; corollaire V19 uniforme avec masquage iid.
- Énoncé : encadrement de Loewner des matrices de covariance et égalité de noyaux sous révélation complète positive ; dans le canal V19, invariance des rangs/noyaux pour p<1 ; caractérisation d'un k-recouvrement exact par condition de covariance et somme des poids.
- Dépendances / interface : utilisée par `OBS-V19-N11-MOMENT-GRAM` pour prolonger les rangs ; hypothèses de canal iid et de prior explicites.
- Limites : à p=1 la covariance s'annule sans impliquer de nouvelles relations ; les moments d'ordre 2 ne reconstruisent pas toutes les intersections triples.
- Provenance : rapport N11 moments/noyau et archive de preuves.
- Contrôle du lot : preuves de variance/Fourier et audit exact-cover non rejoués ; non réaudité.
- SHA Git source : `6c7dca87aab78f5986569daf48f0bd170b42dca1`.

### 11. `OBS-RESTRICT-AFFINE_BRIQUE.md`
- ID : `OBS-RESTRICT-AFFINE` v1.
- Statut déclaré : DÉMONTRÉ interne ; originalité application connue.
- Domaine : systèmes affines cohérents sur F₂^n, prior uniforme et canaux de révélation indépendants par coordonnée.
- Énoncé : formule de Fourier pour le moment conjoint de deux postérieurs, pondérée par les supports des vecteurs dans l'intersection des espaces de lignes ; phase relative invariante sous translation commune ; cohérence de l'union équivalente à phase nulle.
- Dépendances / interface : base analytique déclarée pour le transfert affine V19 ; relation détaillée avec les autres briques à expliciter au niveau des contrats.
- Contrôles déclarés : 11 472 contrôles sur sous-espaces affines n≤3 et 10 620 événements graphiques n≤4.
- Limites : systèmes incohérents traités séparément ; hypothèses de prior et de masques indépendants indispensables ; covariance peut changer de signe ou s'annuler malgré intersection non triviale.
- Provenance : `TRANSFERT_AFFINE_V19_2026-10-15.md`, archive scripts et audits.
- Contrôle du lot : preuve Fourier et campagnes de tests non reproduites ; non réaudité.
- SHA Git source : `cfeb3e0fededf0de0f0b5dba8ceef9cbe9d99b86`.

## Graphe documentaire de dépendances et d'interfaces

Le contenu des fiches fait apparaître les relations suivantes (elles sont reproduites comme dépendances **déclarées**, pas comme dépendances vérifiées) :

- `BR-OBS-CAP-01` → `BR-OBS-CAP-02` → interface entre capacité d'occurrences et support/poids des circuits.
- `BR-OBS-CAP-03` + `OBS-V19-C5-CAPACITY` → `OBS-V19-COEX-REGION` → `OBS-V19-FIRST-OBSTRUCTION11`.
- `BR-OBS-KRYLOV-01` + `OBS-V19-FORCED-P4` → `OBS-V19-BAD-FIBER2`.
- `BR-OBS-BAD-01` + `BR-OBS-CIRCUIT-01` → reconstruction finie `OBS-V19-N11-BADOBJECT`.
- `BR-OBS-REVEAL-KERNEL` → prolongement des rangs dans `OBS-V19-N11-MOMENT-GRAM`.
- `OBS-V19-N11-THIRD-ORDER` et `OBS-V19-N11-MOMENT-GRAM` traitent respectivement des informations d'ordre 3 et des moments/covariances ; ne pas les confondre.

## Points de vigilance et verrous ouverts

1. **Trois niveaux de multiplicité.** Les fiches distinguent (i) paires/occurrences, (ii) mauvais objets distincts après quotient, (iii) coefficients positifs dans les circuits. `BR-OBS-CAP-02` interdit de transférer directement une borne de capacité vers les coefficients. C'est un verrou central pour toute tentative de relier la région C5 au gap d'intégralité.
2. **Géométrie vs labels orientés.** Les ordres critiques 3 et 11 ne se contredisent pas : le premier est géométrique avant quotient par rotations, le second concerne les 14 labels orientés après agrégation. Garder les espaces de coordonnées distincts.
3. **Dépendance P4 à contrôler.** `OBS-V19-BAD-FIBER2` invoque `OBS-V19-FORCED-P4` et une propriété P1–P4. La reconstitution correspondante existe dans `reconstructed/`, mais le contrat exact, la provenance primaire et la portée du lemme doivent être rapprochés avant toute promotion de statut.
4. **N11 n'est pas une preuve universelle.** Les valeurs 42/36/36/37/38 et les supports à 16 sont des calculs finis sur cinq mappings. La borne fibre≤2 est une affirmation universelle séparée, dans son domaine restreint.
5. **Moments d'ordre 2 vs ordre 3.** Le rapport N11 moment-gram ne remplace pas les témoins d'intersections triples. Les deux couches sont complémentaires, pas interchangeables.
6. **Contrôles historiques non rejoués.** Les nombres de systèmes, masques, évaluations et rangs restent rapportés par les fiches, sans reproduction dans ce lot.

## Verdict du lot

- 11/11 fichiers individuels lus intégralement.
- Classification documentaire réalisée : ID, statut déclaré, domaine, énoncé, dépendances, contrôles, provenance et limites.
- 0 script/checker exécuté ; 0 preuve vérifiée indépendamment ; 0 statut scientifique revalidé ; 0 certificat renouvelé.
- 0 fichier de la branche source modifié ; 0 écriture SQLite.
- Les briques restantes, les revues (47) et les artefacts de reproductibilité (44) restent à classifier sémantiquement.

Ce lot établit une carte documentaire plus précise du noyau V19 C5/L=3, mais ne valide pas mathématiquement ses dépendances ni ne relie encore ce corpus au moteur agentique.
