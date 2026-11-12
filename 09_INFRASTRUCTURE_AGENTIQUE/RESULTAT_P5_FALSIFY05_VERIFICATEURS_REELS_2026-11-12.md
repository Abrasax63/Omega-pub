# P5-FALSIFY-05 — vrais vérificateurs faillibles et Bellman calibré : résultat négatif pour Omega-like

**12 novembre 2026 — Statut : ERREURS ET DÉSACCORDS DE MODÈLES RÉELS / REJEU DE DÉCISIONS SOUS COÛT CONVENTIONNEL / AUCUN AVANTAGE SPÉCIFIQUE OMEGA.**

## 1. Protocole, sources et corrections traçables

- [Pré-enregistrement avant chargement des trois sorties réelles](EXPERIMENT_P5_FALSIFY05_CLAIMDB_MULTI_VERIFIERS_PREREG_2026-11-12.md), commit `89d19f5e324bb76a577eec9cfb8c2b0a0decf883`, et [amendement avant tout score](AMENDEMENT_P5_FALSIFY05_VERDICTS_MANQUANTS_2026-11-12.md), commit `ac590dfd06e1c6c36d81b6140bfa3b4246c909fe`.
- Source d'origine : Theologitis et al., [ClaimDB, ACL 2026](https://aclanthology.org/2026.acl-long.1589/), [dépôt officiel](https://github.com/claimdb/claimdb), commit `e06c3a22cc14a8ef6858bb5d40bca7925241b98d`.
- **Fichiers authentiques Git LFS vérifiés par SHA256 avant traitement** : 1000 labels publics ; 1000 réponses GPT-5-mini sans outils ; 1000 réponses **GPT-5-nano**, **Gemini 2.5 Flash**, **Claude Haiku 4.5** avec outils. Les SHA-256 des cinq fichiers sont consignés dans le protocole gelé et exigés par la CI. Les trois derniers résultats sont des sorties réellement produites par des modèles de fournisseurs différents, **pas des erreurs artificielles générées dans Omega**. Le corpus, les annotations et les logs dépendent néanmoins d'un **même benchmark ClaimDB**, et les modèles peuvent avoir des erreurs corrélées.
- Le premier contrôle [#43262333944](https://github.com/Abrasax63/Omega-pub/actions/runs/43262333944) a détecté un verdict manquant pour Claude #884 avant toute notation. L'amendement a **conservé tous les 1000 cas** et codé `NO_VERIFIER_LABEL` séparément de `NOT ENOUGH INFO` et `NO_SQL_OUTPUT`. Un achat sans sortie exploitable coûte toujours son prix conventionnel.
- Le calcul primaire a réellement eu lieu lors du [run #43262751861](https://github.com/Abrasax63/Omega-pub/actions/runs/43262751861). Sa CI a d'abord échoué **après calcul**, parce que le test technique supposait à tort au moins dix bases dans l'évaluation, alors que le **test public de 1000 lignes contient seulement onze bases**. Les **80 bases** annoncées dans la publication concernent le corpus complet et non ce split de test. La CI a été corrigée en conservant exactement **les mêmes politiques, les mêmes 1000 lignes, le même découpage et tous les paramètres**. **[Run final #43263585438 — SUCCESS](https://github.com/Abrasax63/Omega-pub/actions/runs/43263585438)** : dix tests spécialisés réussis, cinq SHA externes authentifiés, comparaison complète de 419 problèmes et résultat identique octet pour octet au premier JSON. **[RCE #43263585444 — SUCCESS](https://github.com/Abrasax63/Omega-pub/actions/runs/43263585444).**
- **[Archive finale de référence — CI SUCCESS](https://github.com/Abrasax63/Omega-pub/actions/runs/43263585438/artifacts/13964497301)**, ZIP SHA256 `5b311084b6387f1fcc95a405b21d2a598d8f0dbb450767242f3d84a73f2264a0`. [Archive du premier calcul ayant échoué uniquement à l'assertion de couverture](https://github.com/Abrasax63/Omega-pub/actions/runs/43262751861/artifacts/13964422253), ZIP SHA256 `dcff3cdec688405f2d2f0406cb79ce7d3f0bfa1c91ff01b7747dbc9d6c63bba9`. **Les deux fichiers JSON de résultats décompressés ont exactement le même SHA256 : `6b421ac3e47c497c6861e40c15202cfc0c99a274c27e839868709ee22b95e5cb`.**

### Split vrai, sans duplication de bases

Le partitionnement déterministe par hachage des seuls noms de bases a produit **7 bases / 581 affirmations en calibration** et **4 bases / 419 affirmations en test** : `california_schools` (68), `codebase_community` (101), `superhero` (120), `formula_1` (130). Le partage par base prévient qu'une même base revienne directement dans les deux segments. Cela ne rend PAS les labels inconnus du public et ne garantit PAS l'absence de contamination des modèles pré-entraînés.

**Attention statistique : seulement quatre groupes de test indépendants par base !** Un bootstrap sur quatre groupes ne permet pas d'étayer une revendication robuste de généralisation. Les intervalles produits sont exploratoires et instables. Les conclusions doivent d'abord rester **descriptives**.

## 2. Comparaison sous budget — résultats réellement calculés

Barème pré-enregistré : **+1 correct, −2 faux, +0,05 abstention, moins le coût acheté**. `nano=0,08`, `gemini=0,12`, `claude=0,16` **unités d'utilité fictives**, maximum 2 achats et 0,24 par claim. **Aucun coût financier ni temps de modèle réel ne résulte de ces prix**, puisque les prédictions sont tirées des journaux historiques des auteurs.

| Politique | Utilité moyenne /419 | Exactes publiées | Fausses publiées | Abstentions | Vérifications achetées |
|---|---:|---:|---:|---:|---:|
| Sans outil, abstention prudente | **0,050000** | 0 | 0 | 419 | 0 |
| **Fixe : nano puis Gemini** | **0,435442** | **310** | **24** | 85 | 838 |
| **Bellman exact sur posterior JOINT raw** | **0,385036** | 332 | 50 | 37 | 692 |
| Bellman JOINT global + filtre des traces | **0,380835** | 325 | 49 | 45 | 662 |
| Bellman JOINT contextuel + filtre des traces | **0,340764** | 278 | 39 | 102 | 595 |
| Omega-like **sans mémoire statistique** | **0,219570** | 190 | 21 | 208 | 693 |
| Omega-like **sans filtre de provenance** | **0,401241** | 285 | 30 | 104 | 486 |
| **Omega-like avec provenance** | **0,376945** | **279** | **30** | 110 | 514 |
| Oracle connaissant les labels, NON DÉPLOYABLE | **1,000000** | 419 | 0 | 0 | 0 |

**Résultat principal pré-enregistré :** Omega-like full − Bellman contextuel = **+0,036181 unité/cas**. L'intervalle bootstrap descriptif enregistré est **[+0,001759 ; +0,064706]**, mais seulement **quatre bases de test** rendent son interprétation statistique très fragile. Cela n'est **ni** une victoire robuste, **ni** une validation de la vraie architecture P1/P2/P3.

**Surtout : l'heuristique Omega-like PERD contre des contrôles classiques annoncés AVANT le test.** Face à l'achat fixe de deux modèles, `0,376945 − 0,435442 = −0,058497` unité/cas. Face au Bellman raw, `−0,008091` ; face au Bellman global, `−0,003890`. Le contrôle fixe gagne malgré l'absence d'adaptation, montrant une **calibration ou un transfert hors domaine insuffisant** pour les politiques VOI ajustées à sept bases.

Par rapport à l'ablation « sans observabilité », l'ajout de la vérification des journaux de sortie est également **moins bon sur ce jeu** : `0,376945` contre `0,401241`. Ce n'est pas un effet isolé du seul filtre : les règles d'acquisition et le modèle probabiliste réestimé diffèrent aussi selon le canal raw/gated. Il serait erroné d'attribuer intégralement cet écart à l'observabilité causale.

### Témoins indépendants d'arithmétique

Le ZIP final de 49 Ko compressés contient le JSON de **419 trajectoires × huit politiques opérationnelles**. Un recalcul par programme séparé a vérifié **tous les coûts, plafonds, bons/mauvais verdicts et abstentions**, et obtenu **zéro divergence sur les totaux**. Empreintes :
- ZIP source primaire SHA256 `dcff3cdec688405f2d2f0406cb79ce7d3f0bfa1c91ff01b7747dbc9d6c63bba9`
- JSON primaire décompressé SHA256 `6b421ac3e47c497c6861e40c15202cfc0c99a274c27e839868709ee22b95e5cb`
- Recalcul indépendant local `omega_falsify05_independent_audit.json`, SHA256 `798728a4caedbc993c4ff75ef74742af9bb3dc8af33ea9705249560d035448de`.

Cette deuxième voie a été exécutée par **le même assistant**, et non par une équipe indépendante. Elle prouve seulement la cohérence arithmétique de l'archive, pas la vérité externe des labels.

### Variations entre quatre bases d'évaluation

| Base | Omega-like full | Achat fixe deux outils | Bellman contextuel |
|---|---:|---:|---:|
| california_schools (68) | 0,4725 | 0,4721 | **0,5040** |
| codebase_community (101) | 0,4031 | **0,4119** | 0,3307 |
| superhero (120) | 0,3879 | **0,4429** | 0,3297 |
| formula_1 (130) | 0,2965 | **0,4277** | 0,2735 |

L'heuristique Omega-like atteint pratiquement l'achat fixe sur `california_schools`, mais perd sur **trois des quatre bases** et particulièrement sur `formula_1`. Il serait trompeur de ne citer que sa supériorité moyenne face au seul Bellman contextuel. Les quatre bases sont insuffisantes pour une estimation robuste de variance interdomaines.

## 3. Ce qui vient réellement des outils — et ce qui n'est pas confirmé

Sur les **581 calibrations**, les traces des modèles étaient toutes présentes sous forme structurée; des réponses de modèle manquaient toutefois pour **Claude : 7 cas, Gemini : 5 cas, Nano : 0**. Sur les 419 évaluations, **aucun verdict texte manquant** ; en revanche le journal ne contenait pas de sortie d'outil pour un certain nombre d'affirmations (par exemple **390/419** sorties d'outil journalisées pour Gemini). Ces manques sont utilisés comme observations `NO_SQL_OUTPUT`, pas comme labels NEI.

**Un appel SQL journalisé n'est pas une vérification indépendante du texte ou du verdict.** La CI ne rejoue pas les SQL sur les données BIRD ; elle rejoue les réponses des modèles et les événements d'outil réellement publiés. Les modèles appartiennent à plusieurs organisations, mais leur vérification et l'étalon gold viennent du même dépôt scientifique. On ne peut confirmer ni l'indépendance des erreurs, ni leur validité sémantique avec cette seule archive.

## 4. Conclusion scientifique

**ÉTABLI :** l'architecture expérimentale peut exploiter des erreurs authentiques de trois modèles et choisir des vérifications sous un plafond ; une distribution jointe calibrée sert à une planification Bellman séquentielle ; l'évaluation a réellement porté sur 419 questions réparties par quatre bases ; le calcul initial et son recomptage sont cohérents.

**RÉFUTÉ dans ce protocole :** l'heuristique Omega-like avec provenance serait la meilleure politique sur les coûts fixés. Le **contrôle fixe** a obtenu un score supérieur. L'observabilité de provenance telle que codée n'apporte ici aucun gain démontré.

**INDÉTERMINÉ :** supériorité du véritable Omega P1/P2/P3, effet causal isolé de la mémoire scientifique, efficacité économique avec coûts réels de modèles, transférabilité à des domaines nouveaux et significativité statistique robuste avec seulement quatre bases.

**Prochain verrou utile :** arrêter la répétition des mêmes données ClaimDB ; obtenir un nouvel ensemble **non public au moment de la conception**, des coûts **mesurés**, un calibrateur de fiabilité robuste aux changements de source, et une **vraie politique Omega P1/P2/P3** dont les décisions dépendent de la mémoire et de témoins de provenance réellement vérifiés, face à un Bellman/Bayes classique ayant les mêmes sources.

**PR #68 DRAFT, `main` inchangée, aucune promotion d'une supériorité en CORE.**
