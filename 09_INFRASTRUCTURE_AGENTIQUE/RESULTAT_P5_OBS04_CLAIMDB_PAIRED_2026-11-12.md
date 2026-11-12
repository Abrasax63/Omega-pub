# P5-OBS-04 — 1 000 désaccords potentiels entre deux méthodes réelles sur ClaimDB

**12 novembre 2026 — Statut : 1 000 VERDICTS APPARIÉS RÉELS, AUDIT TECHNIQUE REPRODUCTIBLE, SUPÉRIORITÉ SPÉCIFIQUE OMEGA NON DÉMONTRÉE.**

## Provenance et pré-enregistrement

- Pré-enregistrement avant consultation des sorties des deux configurations de modèles : [EXPERIMENT_P5_OBS04_CLAIMDB_PREREG_2026-11-12.md](EXPERIMENT_P5_OBS04_CLAIMDB_PREREG_2026-11-12.md), commit `40f9968f65ae7ed84b699b9573e8ff4d9afddbc1`.
- Source primaire : [ClaimDB, Theologitis et al., ACL 2026](https://aclanthology.org/2026.acl-long.1589/), dépôt [claimdb/claimdb](https://github.com/claimdb/claimdb) épinglé au commit **`e06c3a22cc14a8ef6858bb5d40bca7925241b98d`**, licence **CC BY-SA 4.0**.
- Conditions comparées par les **auteurs ClaimDB** : [GPT-5-mini avec outil SQL](https://github.com/claimdb/claimdb/blob/e06c3a22cc14a8ef6858bb5d40bca7925241b98d/experiments/public/gpt-5-mini.jsonl) et [GPT-5-mini sans outils](https://github.com/claimdb/claimdb/blob/e06c3a22cc14a8ef6858bb5d40bca7925241b98d/experiments/public/no_tools/gpt-5-mini.jsonl), jugés face aux annotations du [test public ClaimDB](https://github.com/claimdb/claimdb/blob/e06c3a22cc14a8ef6858bb5d40bca7925241b98d/final-benchmark/test-public.jsonl).
- Le fichier des sorties avec SQL est dans **Git LFS** : un pointeur n'a pas été accepté comme preuve. [Contrôle d'acquisition #43227890749 : SUCCESS](https://github.com/Abrasax63/Omega-pub/actions/runs/43227890749), empreintes vérifiées :
  - test public : SHA256 `b87d7062307cfcf5ae862bf03bd7e82f7123ff39cf0b69d3dc5cc25caaaea810` (329 130 octets);
  - SQL : `e31443bd85f46c4edc4a146243bb709634c6330c2914c726630c3f3349edb100` (11 729 249 octets);
  - sans outils : `552531cba335298816a998f7a2b6fb548d9cd0eb7f9b47e5d1272809620a9aa6` (2 018 249 octets).
- [Premier calcul officiel #43228587453 : SUCCESS](https://github.com/Abrasax63/Omega-pub/actions/runs/43228587453) ; **8 tests d'intégrité**, 1 000 lignes et `claim_id` uniques dans chacun des trois fichiers, **100 % de jointures complètes** ; aucune prédiction inventée.
- [Archive des scores dérivés et 1 000 dossiers anonymisés par identifiant](https://github.com/Abrasax63/Omega-pub/actions/runs/43228587453/artifacts/13947874257). ZIP SHA256 du premier run : `74506ac77a855d4c608edcfdac544a61f6b6d0bbce7163b8ed110236efbbbe9e`, contenu JSON `444c7397c6b53340680db018b19f95720a62da33481f05fb3d0843bf4d9e84d8`.
- Un script **distinct**, `prism/p5_obs04_independent_audit.py`, recompte indépendamment les 1 000 relations, les utilités, le risque et la couverture stratifiée ; ce contrôle rétrospectif n'entraîne aucune politique.

## Résultats réels — sans nouveaux appels à des modèles

Les trois catégories de la vérité annotée sont **ENTAILED (333)**, **CONTRADICTED (331)** et **NOT ENOUGH INFO (336)**. `NOT ENOUGH INFO` est une **étiquette de vérification factuelle**, à distinguer de l'action expérimentale `ABSTAIN` (« ne pas publier de verdict »).

| Configuration sur 1 000 affirmations | Corrects publiés | Faux publiés | Abstentions | Couverture |
|---|---:|---:|---:|---:|
| GPT-5-mini sans outils | **357** | 643 | 0 | 100 % |
| GPT-5-mini avec SQL | **827** | 173 | 0 | 100 % |
| Accord des deux méthodes, sinon abstention | **291** | **17** | 692 | **30,8 %** |
| SQL publié seulement si un événement d'outil en sortie est présent | **821** | 173 | 6 | 99,4 % |
| Toujours s'abstenir | 0 | 0 | 1 000 | 0 % |
| Oracle connaissant la vérité *après désaccord* | 893 | 17 | 90 | 91 % (PLAFOND non déployable) |

**Désaccords observés = 692/1 000 (69,2 %)**. Partition exhaustive des 1 000 cas :
- **291** : deux modèles d'accord et corrects ;
- **17** : deux modèles d'accord mais tous deux faux ;
- **536** : SQL correct et sans outils incorrect ;
- **66** : sans outils correct et SQL incorrect ;
- **90** : deux verdicts divergents mais tous deux incorrects.

Les cinq catégories totalisent exactement 1 000. Ces désaccords sont **authentiques**, issus de fichiers de sorties de modèles antérieurs publiés par les auteurs, et non générés par notre simulateur.

### Principal avertissement : l'accord masque l'indécidabilité

Le score apparent de **291/308 ≈ 94,5 % de corrections dans la seule partie publiée** n'est pas la performance sur les 1 000 cas. Il est largement lié aux réponses **NOT ENOUGH INFO** :

| Label réel dans ClaimDB | Cas totaux | Accords publiés | Parmi ces accords, corrects | Couverture par accord |
|---|---:|---:|---:|---:|
| ENTAILED | 333 | **19** | 13 | **5,7 %** |
| CONTRADICTED | 331 | **41** | 36 | **12,4 %** |
| NOT ENOUGH INFO | 336 | **248** | 242 | **73,8 %** |
| **Total** | **1 000** | **308** | **291** | **30,8 %** |

Les **250 verdicts de consensus `NOT ENOUGH INFO`**, dont 242 corrects, constituent plus de 81 % des accords. Il serait trompeur de dire qu'Omega sait établir 94,5 % des faits : cette règle **refuse de trancher la plupart des affirmations établies et contredites**. La couverture est cruciale.

### Risque et utilité sous la convention expérimentale antérieure

Avec +1 par réponse correcte, −2 par réponse incorrecte et +0,05 pour `ABSTAIN` (unités arbitraires) :
- SQL seul : **+481** pour 1 000 réponses publiées, risque `173/1000=17,3 %` ;
- accord ou abstention : **+291,6** pour 308 réponses publiées et 692 abstentions, risque conditionnel `17/308≈5,52 %` ;
- sans outils : **−929** ;
- abstention systématique : **+50**.

Le consensus réduit le nombre de fausses publications mais **perd 189,4 unités** face au SQL seul, sous cette fonction de gain. Ce résultat empêche d'annoncer une « meilleure stratégie » sans expliciter le coût réel d'une mauvaise décision, d'une abstention et du recours SQL. **Aucun coût monétaire ou latence SQL n'est comparé**.

### Traces SQL : provenance d'action, pas certificat de vérité

Le journal « avec outils » contient **5 172 événements `function_call` et 5 172 sorties `function_call_output`** explicitement enregistrés. Six affirmations n'ont pas de sortie d'outil consignée. Mais un événement d'appel SQL **ne démontre pas** que la requête était pertinente, exécutée sans erreur ou suffisante pour établir la conclusion. La porte « présence d'une trace SQL » laisse d'ailleurs **173 erreurs publiées** et **821 réponses correctes** sur 994 réponses publiées.

Cette vérification du **chemin de provenance** est une première condition nécessaire, non un certificat de validité. Pour un vrai module Omega, il faudra rattacher chaque requête à ses sorties exactes, à une base versionnée, puis à un sous-ensemble de témoins globalement cohérent.

## Limites causales et épistémiques

1. Les conditions **diffèrent aussi par leur prompt et leurs exemples** : la configuration outillée utilise des instructions et des exemples que le bras sans outils n'a pas exactement. **L'écart de 82,7 % contre 35,7 % n'est pas un effet causal isolé de l'accès SQL**.
2. Les deux bras proviennent du **même modèle de base GPT-5-mini** et du même benchmark annoté ClaimDB. Ils ne sont **pas deux fournisseurs indépendants**. Une concordance peut être une erreur commune, comme l'illustrent les **17 accords faux**.
3. Les annotations du jeu public sont prises comme vérité de référence. Nous **n'avons pas téléchargé les bases BIRD, ni exécuté les SQL pour reconstruire indépendamment les 1 000 vérités**. Une référence externe humaine indépendante n'a pas été sollicitée.
4. Le jeu était **public** et les deux sorties déjà publiées, donc aucune évaluation aveugle ou généralisation prospective n'est revendiquée. Les 1 000 cas sont regroupés dans **11 bases** ; un intervalle binomial naïf supposant des observations entièrement indépendantes serait trompeur.
5. `agree_or_abstain` et `sql_trace_gate` sont des **règles classiques transparentes**, pas des politiques de mémoire adaptative Omega. Le candidat P1 n'a pas généré ni amélioré les réponses.

## Raccord objectif avec notre observabilité `Δ_h`

- **Prouvé techniquement ici** : conservation des identifiants exacts et des verdicts appariés, distinction entre deux modes de réponse et une seule source de vérité, détection de désaccords réels et mesure du risque/couverture ; refus des preuves LFS absentes et des jointures incohérentes.
- **Non encore établi** : le recollement d'un raisonnement composé de requêtes SQL et de pages, au sens fort d'un **témoin commun réalisant toutes les observations successives**. Une trace d'appel ne suffit pas à construire le `B_i` des survivants ; il faut les données source, les transformations et les sorties des calculs.
- **Valeur de l'observabilité à tester ensuite** : identifier, dans un désaccord où les deux configurations ont été exécutées, quelles données ou requêtes nécessaires manquent pour départager les hypothèses, en limitant la vérification aux cas à risque ; comparer alors à un **contrôleur bayésien classique** de valeur d'information, à l'abstention et à un solveur SQL direct.

## Suite et décision de gouvernance

Pour un test de véritables chaînes de preuves : obtenir une base ClaimDB/BIRD **versionnée et accessible** ; journaliser requêtes et retours SQL complets, définir des assertions vérifiables et une procédure indépendante d'exécution ; prendre de nouveaux cas non utilisés pour calibrer la politique ; maintenir des contrôles forts et le budget égal. En complément, **FEVEROUS** fournit des annotations d'ensembles de preuves textuelles et tabulaires, sous licence conditionnelle Wikipedia/CC BY-SA 3.0, mais ses données n'ont pas été exécutées ici.

**Statuts : EMPIRIQUE (vraies sorties de modèles), CALCUL EXACT (scores et appariements), NON DÉMONTRÉ (originalité Omega et indépendance des preuves), À DÉPLOYER (vérifications réexécutables).**

**PR DRAFT, ne pas fusionner dans `main` ni promouvoir dans CORE.**
