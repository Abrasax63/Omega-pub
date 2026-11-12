# P5-EVID-05 — première reproduction de faits ClaimDB sur une véritable base BIRD

**12 novembre 2026 — Statut : BASE SQLITE RÉELLE / REQUÊTES SQL EXÉCUTÉES / CERTIFICATS DE PROVENANCE VALIDÉS / SUPÉRIORITÉ OMEGA NON DÉMONTRÉE.**

## 1. Sources, enchaînement et contrôles effectifs

- **Protocole pré-enregistré AVANT tout téléchargement ou calcul sur la base BIRD** : [EXPERIMENT_P5_EVID05_BIRD_SQL_PREREG_2026-11-12.md](EXPERIMENT_P5_EVID05_BIRD_SQL_PREREG_2026-11-12.md), commit `63471285be2c271b2671537be0b908ae0de3918b`.
- **Amendement purement sémantique AVANT tout accès SQL** : [AMENDEMENT_P5_EVID05_EDITEUR_SEMANTIQUE_2026-11-12.md](AMENDEMENT_P5_EVID05_EDITEUR_SEMANTIQUE_2026-11-12.md), commit `37275aa93c9efa5f5ce748eb65928e87d42b2337`. Il traite le cas `publisher.id=1` mentionné dans `extra_info` et la notion naturelle `NULL/N/A/éditeur vide`, en imposant l'abstention du filtre de provenance pour #4179 même si les deux calculs concordent.
- Source des cinq affirmations et labels : [ClaimDB, Theologitis et al., ACL 2026](https://aclanthology.org/2026.acl-long.1589/), [fichier test public](https://github.com/claimdb/claimdb/blob/e06c3a22cc14a8ef6858bb5d40bca7925241b98d/final-benchmark/test-public.jsonl), commit `e06c3a22cc14a8ef6858bb5d40bca7925241b98d`, Git blob `a017545623508c0090cf2148716b8d26a6f8c337`. Cinq textes, `extra_info`, IDs et labels ont été **recomparés octet pour octet par champs** au fichier source initial téléchargé. Labels **jamais accessibles aux requêtes**.
- Base authentique **BIRD développement / superhero SQLite**, copie publique de [Tarzanagh/QAFD-RAG](https://github.com/Tarzanagh/QAFD-RAG/tree/2a3a42c8ea4e9c416de0a7fe53c04fab50b756ef/data/text2sql/bird/databases/superhero), commit `2a3a42c8ea4e9c416de0a7fe53c04fab50b756ef`, **237 568 octets** : Git blob `4cfbee0ba8b6033a7415184caff90d363fe444c2`, SHA-256 `75e94a2c3236ee3bb2c01fb97a1c4b4c1c269bcefd4eab1d04be323d2d0825b1`. **Les deux empreintes et la taille ont été vérifiées avant toute SQL** ; leur cohérence avec une autre copie BIRD publiée a ainsi été contrôlée. La base n'a **pas été redistribuée dans notre dépôt ni dans l'artefact**.
- Schéma nécessaire vérifié sur **cinq tables** : `superhero`, `colour`, `gender`, `race`, `publisher`. `superhero` contient **750 lignes** dans cette version. Exécution via SQLite Python en lecture seule (`mode=ro&immutable=1` et `PRAGMA query_only=ON`).
- [GitHub Actions #43233326446 — SUCCESS](https://github.com/Abrasax63/Omega-pub/actions/runs/43233326446) : **7 tests logiciels réussis**, les deux fichiers source authentifiés, les quatre prédicats SQL **réellement exécutés** via deux formulations chacune, artefact JSON signé par ses empreintes source. [Suite générale RCE #43233326342 — SUCCESS](https://github.com/Abrasax63/Omega-pub/actions/runs/43233326342).
- [Archive des textes SQL exécutés, sorties, témoins, empreintes et décisions](https://github.com/Abrasax63/Omega-pub/actions/runs/43233326446/artifacts/13951361782) ; [code de reproduction](prism/p5_evid05_bird_sql.py), [tests](prism/test_p5_evid05_bird_sql.py), [cinq affirmations gelées](prism/evid05_claimdb_5_preselected.json).

**Attention aux droits :** ClaimDB publie ses données sous CC BY-SA 4.0, avec attribution à ses auteurs. Le statut de redistribution des binaires BIRD et de chaque miroir doit être vérifié séparément. Aucun binaire BIRD n'est embarqué.

## 2. Résultats de la première exécution SQL authentique

| ClaimDB ID | Fragment réellement testé | Deux SQL concordants ? | Témoin dans la base | Verdict du filtre Omega |
|---|---|---|---|---|
| **4267** | Existence d'un homme mutant aux cheveux bleus | Oui : VRAI / VRAI | **Beast**, id 79 | `ENTAILED` |
| **4179** | Existence de personnages sans éditeur selon `NULL/éditeur vide`, puis vérification séparée selon `publisher.id=1` | Oui : VRAI / VRAI **pour les deux conventions** | Astro Boy, Bananaman, Bionic Woman (éditeur id 1, nom vide) | `ABSTAIN_SEMANTIC_CONVENTION` |
| **4324** | Nombre de femmes associées à Marvel Comics exactement égal à 111 | Oui : VRAI / VRAI | **COUNT(*) = 111** | `ENTAILED` |
| **3930** | Existence d'au moins un humain de 185 cm — contre-exemple à la négation du claim | Oui : VRAI / VRAI | **Adam Strange, Darkhawk, Deadshot**, chacun 185 cm | `CONTRADICTED` |
| **4419** | Renommage rétroactif hypothétique des personnages John | Non testé : hors observabilité de cette base statique | Aucun | `ABSTAIN_MISSING_OBSERVABLE_COUNTERFACTUAL` |

Les deux méthodes de chaque cas sont des **SQL réellement différents** (jointures et prédicat d'existence versus sous-requêtes de sélection et comptage), mais utilisent **les mêmes données BIRD**. Aucune contradiction numérique parmi les **quatre prédicats exécutés**.

### Nuances indispensables

- **#4179 : il ne s'agit pas d'un désaccord observé entre SQL.** Les deux conventions différentes produisent ici le même résultat **VRAI**, notamment parce que `publisher.id=1` a un nom d'éditeur vide. L'abstention est **une règle conservatrice pré-enregistrée** faute d'une revue sémantique indépendante de l'expression « sans éditeur ». On pourrait réexaminer sa nécessité dans une future politique, mais **on ne change pas rétroactivement son verdict**.
- **#3930 :** il suffit d'un seul humain de 185 cm pour réfuter la première clause « aucun humain de 185 cm » ; le certificat **ne prouve pas** la phrase causale entière « donc aucune couleur de cheveux ne peut être fournie » dans tous les mondes possibles. Cette limitation est explicitement notée.
- **#4324 :** les requêtes ne déduisent pas « 111 » d'une annotation du benchmark ; le dénombrement a été **réellement obtenu** en SQL sur la source externe et reporté dans l'artefact.
- **#4419 :** un `SELECT COUNT(*)` sur les noms existants n'aurait pas testé l'intervention contrefactuelle ; aucune étiquette n'a été publiée à partir de cette procédure insuffisante.

## 3. Comparaison à information égale avec deux méthodes classiques

Toutes les politiques ont accès aux **mêmes SQL exécutés** ; aucune n'a appris à choisir les requêtes ou utilisé le modèle de langage pour les générer dans cette expérience.

| Contrôle | Verdicts publiés /5 | Abstentions /5 | Concordance avec les labels publics parmi les verdicts publiés |
|---|---:|---:|---:|
| Une seule méthode SQL | **4** | 1 | **4/4** |
| Deux méthodes SQL concordantes (témoin classique solide) | **4** | 1 | **4/4** |
| **Omega, filtre de provenance et de portée sémantique** | **3** | 2 | **3/3** |

**Cela n'est PAS un score d'exactitude hors échantillon** : les cinq cas ont été **choisis manuellement après consultation de leurs labels publics**, les requêtes ont été rédigées par le même opérateur, et leur correspondence exacte à l'anglais **n'a pas été revue indépendamment**. La concordance avec ClaimDB est une **validation croisée limitée entre annotation et base**, et **non une certification par deux fournisseurs distincts**. Le résultat n'apporte **aucune supériorité mesurée d'Omega** ; son garde-fou conserve une abstention supplémentaire #4179, sur ce jeu alors que la SQL concorde.

Un véritable comparateur bayésien devrait disposer d'estimations empiriques des taux d'erreur, de la dépendance entre méthodes et des coûts des vérifications. **Ces paramètres ne sont pas observés ici.** Les inventer pour produire un classement bayésien aurait été un artefact méthodologique ; le contrôle fort effectif est donc le classique « deux requêtes SQL concordantes », avec source et coûts identiques.

## 4. Rapport au programme d'observabilité Δ_h

Ce test exploite le **principe de témoins cohérents et d'observations suffisantes** :
- un `EXISTS` doit pouvoir fournir **au moins une ligne témoin réelle** si le prédicat est positif ;
- deux lectures SQL cohérentes sur une même base **ne créent pas deux fournisseurs indépendants** ;
- une proposition contenant une intervention contrefactuelle **n'est pas observable** à partir des lignes de la base statique ;
- un décalage de définition entre l'énoncé naturel et la convention des annotations doit être enregistré avant de conclure.

Il ne démontre **aucune nouvelle conséquence du théorème autonome `Δ_h`**, ni une capacité d'apprentissage de P1, ni une vérification indépendante de toutes les propositions ClaimDB. C'est une **application technique du principe de filtrage des témoins**, déjà apparenté à l'observabilité et aux modèles probabilistes classiques.

## 5. Décision scientifique

**EXÉCUTÉ ET REPRODUCTIBLE :** vraie base BIRD, SHA-256 et Git blob vérifiés, deux SQL distincts réellement exécutés pour **4/4 fragments**, 3 témoins existentiels/numériques, prudence sur la proposition contrefactuelle, code/test/rapport archivés.

**NON ÉTABLI :** réduction d'erreur grâce à Omega comparée à un contrôle classique à information égale ; revue sémantique indépendante ; sélection intelligente de nouvelles preuves ; performance générale sur 1 000 claims ; indépendance entre fournisseurs.

**Prochaine étape discriminante :** étendre progressivement aux bases BIRD source versionnées qui couvrent des **claims avec divergences de méthodes authentiques**, préparer des énoncés et des requêtes **revus par un tiers** avant le calcul, et mesurer le choix des vérifications sous coût. Ne **pas** étendre automatiquement les cinq résultats sélectionnés à tout ClaimDB.

**PR DRAFT, `main` inchangée ; ne pas promouvoir une supériorité scientifique Omega dans la bibliothèque CORE.**
