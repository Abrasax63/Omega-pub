# OMEGA-AST-001 — pré-enregistrement avant lecture des modifications ou des résultats

**11 novembre 2026. Statut : test externe historique de la portée de déclarations syntaxiques ; aucun résultat calculé avant ce protocole.**

## Verrou scientifique

Le précédent protocole `EVIDENCE-001` vérifiait le SHA-256 de **fichiers entiers**. Une modification des octets n'implique pas que toutes les assertions au sujet d'un fichier soient fausses. Mesurer s'il est possible de conserver **des assertions syntaxiques précises** après une modification réelle, sans déclarer valide une assertion devenue inexacte. Comparer le registre Omega à un **index AST fort disposant des mêmes preuves, même budget, même choix d'actions**.

**Portée :** un fait ci-dessous atteste uniquement « la déclaration syntaxique est présente et sa signature AST a cette empreinte dans cette version ». Il ne prouve pas la conformité du code exécuté, le comportement des décorateurs, l'exécution d'une fonction, la vérité d'un test, ni une proposition scientifique hors du code. Appeler ce résultat « preuve sémantique » sans cette réserve serait trompeur.

## Source gelée, population, partitions

Réutiliser la source publique **`pallets/flask`**, commit cible `49943b5a94413a530761350f04e896f76e8d620e`, **41 commits consécutifs par premiers parents**, de `4b8bde97d4fa3486e18dce21c3c5f75570d50164` au commit cible, donc 40 transitions. La population est choisie **exclusivement à la révision initiale**, avant les différences :
- **tous les fichiers `.py`** sous `src/flask/` et `tests/` (inventaire de métadonnées initial : **65**, non choisi sur les changements) ;
- une assertion `module_ast` par fichier, empreinte SHA-256 de `ast.dump(module, include_attributes=False)` ;
- toutes les déclarations de classes, fonctions et fonctions asynchrones au **niveau module**, ainsi que les méthodes déclarées directement dans ces classes, extraites à l'initialisation. Identifier les doublons de noms par un ordinal déterministe par `(qualname, type)`, sans prétendre identifier des méthodes générées dynamiquement ;
- une classe porte une empreinte des expressions de bases et mots-clefs AST ; une fonction porte une empreinte des arguments (noms, types, défauts) et de l'annotation retour, **sans le corps**. Les décorateurs n'entrent pas dans l'empreinte de signature ; toute affirmation plus large serait injustifiée.

Les **20 premières** transitions sont une calibration descriptive et les **20 dernières** constituent le test chronologique. Aucun choix d'hyperparamètre, de fait, de fichier ni d'ordre d'analyse ne doit dépendre des changements de la partition test. Les nouvelles déclarations apparues après l'état initial ne sont **pas** ajoutées à ce corpus fixe, pour éviter l'extension sélective de la population.

## Comparateurs et coût

La politique voit **le manifeste Git des chemins modifiés**, recoupé avec `git ls-tree`; les contenus AST cibles ne deviennent visibles qu'en lisant et analysant leur blob. Une vérification coûte **une lecture de blob + une analyse `ast.parse`**, quel que soit le nombre de déclarations dans ce fichier ; le coût de la métadonnée Git est commun et **non** facturé. Aucun coût CPU, réseau ni mémoire n'est supposé connu.

Bras :
- **A `stale_no_refresh`** : conserve sans relecture les anciennes signatures en les annonçant courantes (contrôle négatif, faux positifs possibles).
- **B `file_path_invalidate`** : rend en attente toutes les assertions de tout fichier modifié, sans parser de nouveau (conservateur, sans coût de parsing mais couverture inférieure).
- **C `full_ast_reverify`** : parse chaque fichier présent à chaque révision, sans budget (borne supérieure de couverture, concurrent non admissible à coût égal).
- **D `ast_dependency_index_8`** : lorsqu'un fichier pertinent change, suspend ses seules assertions, reparse au maximum **8 fichiers par transition**, en privilégiant les changements du commit, puis les dossiers en attente, tri lexicographique. Toute signature inchangée peut être déclarée toujours applicable **après parsing**. Une déclaration absente est `unavailable`. Le fait nouveau est enregistré sous un nouveau certificat versionné ; l'ancien reste historisé.
- **E `omega_ast_ledger_8`** : même information et budget ; reprendre l'historique certifié du dossier `EVIDENCE-001`, comparer aux assertions AST et **ne pas attribuer une supériorité si les mêmes choix et résultats sont produits que par D**.
- **F `invalidate_all_8`** : invalide tout à chaque commit et ne reparse que 8 fichiers, témoin de la perte d'information en l'absence de dépendances.

L'ordre de vérification D/E est prédéterminé avant tout test ; **aucune optimisation dynamique, aucun LLM et aucun planificateur général ne sont invoqués dans E**. Le nom Omega décrit ici un module de mémoire versionnée, pas une intelligence autonome. Le score doit être présenté dans ces termes.

## Mesures, refus de preuve et contrôles

Pour chaque révision et chaque bras, compter les *occurrences assertion × révision* : `current_verified`, `false_current`, `pending`, `unavailable`, `parse_error`, le nombre de lectures/parsings, et les certificats historiques conservés. Un oracle indépendant **après les décisions** reparse les fichiers des 65 chemins au commit cible, vérifie l'empreinte de chaque assertion et rejette toute attribution `current` fausse. Ne jamais fournir cet oracle à la politique avant la décision.

Rapporter les chiffres TRAIN/TEST séparés, les modifications d'octets dont la signature d'une déclaration reste inchangée, et **les changements véritables de signature** observés. Si aucune signature ne change dans TEST, déclarer le test insuffisamment discriminant sur l'invalidation de signatures (ne pas inventer de contradictions). Une erreur de parsing doit produire une abstention, non une confiance inventée.

Contrôles négatifs :
1. changement de commentaires/formatage avec AST identique ;
2. changement de corps de fonction, sans changement de signature, et empreinte de module modifiée ;
3. changement de signature ou suppression d'une fonction ;
4. ajouts d'une déclaration non suivie initialement ;
5. renommage, suppression ou réintroduction de fichier ;
6. dépassement du budget de huit et invalidation sans réexamen ;
7. diff Git incomplet ou inventé (bloquer, plutôt que certifier) ;
8. archive contenant deux versions divergentes d'une signature : elles sont des **faits versionnés**, non deux vérités simultanées sur un même commit ;
9. vérification indépendante d'au moins une partie des sorties et du calcul de coût dans une deuxième voie distincte.

## Verdict prédéfini

Ce protocole démontre au plus une **granularité plus fine de la provenance et de la continuité des déclarations syntaxiques**. Aucune supériorité d'Omega n'est établie si D=E, même si D/E surpassent un contrôle de fichier grossier. C doit être marqué « coût non égal ». Un gain d'astreinte ou de mémoire scientifique, de découverte de preuves ou de vérité sémantique requiert des tâches distinctes et de meilleurs contrôles.

**PR brouillon empilée sur #41 ; `main`, SQLite, CORE et mémoire certifiée inchangés.**
