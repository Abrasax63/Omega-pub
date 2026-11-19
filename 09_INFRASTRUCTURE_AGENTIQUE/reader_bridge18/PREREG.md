# READER18 — préenregistrement avant lecture des nouvelles sources et avant code

**19 novembre 2026.** Branche indépendante issue de Reader17 (#186), non de `main`. Statut `DRAFT`. Aucune fusion, aucune API payante, aucune modification de poids.

## Motivation : un pas de côté hors du seul LLM
Reader17 montre l'échec d'une politique fondée sur les titres (`A=0, C/D=0` sur certains documents), un troncage qui exclut les dernières sous-sections et des faux « résultats » qui sont en fait des définitions. Ajouter des paramètres au modèle ne résout pas ce goulot de provenance.

## Deux hypothèses distinctes et falsifiables
H1 — **retrieval/observabilité documentaire**, pas raisonnement : une sélection **par sous-sections équilibrées** de lignes sourcées couvrira au moins autant de sections distinctes que le troncage naïf en ordre du texte, avec une limite inchangée de 12 lignes/document. Comparer `D` (politique historique de Reader17, titres énoncé/proposition/théorème/résultat/lemme/corollaire) et `E` (toutes sections non bloquées, texte ancré et filtré par le *même gate* Reader12). E sélectionne les candidats par round-robin des sections de niveau 2, puis par ordre des lignes dans chaque section. **Aucune étiquette gold ni la réponse du modèle n'intervient dans l'extraction.** Le cap s'applique après filtrage gate; 12 candidats max pour D et E.
H2 — **vérification indépendante du générateur**, pas des sources réelles : un oracle arithmétique exact doit détecter toute assertion fausse `A * B = C` à entiers naturels (0..999, multiplication) présente dans un témoin synthétique (quel que soit le choix du modèle) et ne jamais qualifier les autres phrases comme prouvées. Il doit prouver correctement les égalités exactes et refuser les non-égales, sans appel au LLM. Tester mutations et limites de domaine; reporter `NOT_APPLICABLE` pour les formules mathématiques hors grammaire. Zéro certification de théorème non contrôlé.

## Nouvelles sources réelles figées AVANT lecture du contenu
Trois fichiers `*.md` choisis dans la liste Git des chemins, tailles et blobs (sans ouvrir les textes à ce stade), tous différents des trois sources Reader17 et des fiches R90 Reader13–16 :
1. `02_MATHEMATIQUES/observabilite_temporelle/OBS-V8-FACT-INF.md`, blob Git `6d7f6b44c683852871b08a37f814bae5381de11f`, 3387 octets.
2. `02_MATHEMATIQUES/defauts_recollement/AUDIT_QUOTIENTS_TEMOIN9_C4_L2_2026-11-04.md`, blob Git `44f08ebe3e99ef97af8b16c98167b5f64383ce45`, 4282 octets.
3. `02_MATHEMATIQUES/defauts_recollement/PILOTE_EXTRACTION_C4_L2_2026-11-04.md`, blob Git `874e284aedadcffb2d7b18055709ba880002586d`, 6778 octets.
Étiquettes de pertinence/validité mathématique **non disponibles**. Aucun score d'exactitude sémantique sur ces documents n'est autorisé. L'exposition historique aux modèles n'est pas exclue.

## Contrôles et budget
- `D` : algorithme Reader17 inchangé pour les ensembles de candidats, puis 12 premières lignes. `E` : toutes les sections sauf `BLOCKED_SOURCE_CONTEXT`, lignes 6..500 caractères, résultat du gate Reader12 inchangé, round-robin niveau 2. Les filtres sont des règles syntaxiques, **pas** une compréhension scientifique.
- Rapporter par document/politique : SHA Git vérifié, nombre de paquets, nombre de sections éligibles, pool complet, lignes soumises (max 12), couverture des sections, coûts en caractères; anciennes lignes C/D de Reader17 ne font pas office de label gold.
- Comme témoin, simuler `E-first12` (même pool E, mais ordre source non équilibré), comparer sections distinctes et couverture. Critère H1 : E round-robin doit améliorer la couverture d'au moins **un document** sans jamais faire moins bien que E-first12; sinon résultat négatif.
- Oracle externe purement arithmétique : construire après ce gel un corpus déterministe synthétique de 8 énoncés `Résultat : a * b = c` (4 exacts et 4 erronés), avec les 8 triplets figés par graine `20261119` et génération algorithmique (sans accès aux vrais documents), plus contrôles de phrase non supportée, négation, texte additionnel, entiers négatifs, opérateur de division. Vérifier indépendamment du modèle **avec une seconde fonction** le résultat de l'égalité par entier Python. Aucun gold ne passe à un futur modèle; les oracles ne prouvent que cette arithmétique élémentaire. Critère H2 : 8/8 verdicts exacts, zéro promotion incorrecte.
- Sans accès à un annotateur humain indépendant, la notion `ANNOTATION_INDEPENDANTE` sera affichée `NOT_AVAILABLE`, jamais inventée. L'oracle arithmétique est indépendant des sorties du modèle, mais n'est pas une revue scientifique extérieure.
- Un appel LLM est **facultatif et secondaire** : un seul Qwen Coder 3B `q4_k_m` par source × politique non vide, contexte max 12 lignes, 5 numéros ou `NONE`, 128 tokens max, même prompt pour D/E; consigner jetons/secondes, sorties brutes, nombre de citations admises, sans corriger après coup. Les tailles de pool pouvant différer, **pas de parité de coût garantie** ; scores H1/H2 restent **sans modèle**, même si LLM échoue.

## Invariants
Cit. exactes issues des blobs, pas du texte généré; gate non modifié; rejet des citations forgées, IDs non présentés, contexte bloqué; 0 règles Horn, 0 auto-certification scientifique, 0 changement de `main`; pas de promotion à partir d'un test logiciel vert. Toute modification au protocole ci-dessus après données sera étiquetée `POSTHOC`.
