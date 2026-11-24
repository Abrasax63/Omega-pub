# OMEGA-HYBRID-FORENSIC-01 — deux causes distinctes masquées par REAL-02

**23 novembre 2026 — audit direct des artefacts GitHub de deux exécutions effectivement réalisées, avant toute nouvelle inférence.**

## Objet

Les deux exécutions REAL-02 ont un statut GitHub Actions `success` mais un statut scientifique `BLOCKED_BOUNDED_FIDELITY`. Ces statuts ne décrivent pas une amélioration de compétence. Les rapports condensés écrivent `positive_example=false` et `negative_example=false|true` sans dire si le graphe était faux, mal formé ou absent. C'est un défaut de **diagnostic**, pas un avantage à dissimuler.

## Traces retrouvées et recontrôlées

| Run / artefact | Signature formelle | Exemple déclaré positif | Exemple déclaré négatif | Cause exacte de blocage |
| --- | --- | --- | --- | --- |
| [45118912669](https://github.com/Abrasax63/Omega-pub/actions/runs/45118912669) / [14793460094](https://github.com/Abrasax63/Omega-pub/actions/runs/45118912669/artifacts/14793460094) | `reflexive, symmetric, transitive` | Arêtes `(a,a),(b,b),(a,b),(b,a)` | Arêtes `(a,b),(b,a)` | **Erreur mathématique :** le graphe positif manque `(c,c)`, donc n'est pas réflexif sur `{a,b,c}`. Le graphe négatif est réellement négatif. |
| [45119536096](https://github.com/Abrasax63/Omega-pub/actions/runs/45119536096) / [14792897432](https://github.com/Abrasax63/Omega-pub/actions/runs/45119536096/artifacts/14792897432) | `reflexive, symmetric, transitive` | Champ `positive_edges` absent | Champ `negative_edges` absent | **Erreur de schéma de génération :** 0 graphe examiné ; aucune erreur mathématique de graphe n'a pu être testée. |

Dans les deux exécutions, le modèle avait choisi une recherche et une fiche de relation d'équivalence ; les deux rapports déclarent la citation conforme à leur propre vérificateur de texte et la définition libre `NOT_VERIFIED`. **Aucun essai de mémoire D/M/N n'a commencé** : le garde d'admission a arrêté l'expérience.

### Empreintes des fichiers d'artefact effectivement lus

- Exécution 45118912669 : SHA-256 de `candidate.jsonl` = `0702d0e072315e56542790b2fda7eaf782264e5eb4fcff79275e190baa99b331` ; `report.json` = `c96fe724ad28ee6a00928448c3e1ba41162798f9e6dabc470efc1520c4e7f18e`.
- Exécution 45119536096 : SHA-256 de `candidate.jsonl` = `04fe0bd95fdf92e390b94a1a7f2238f5134b85f0a488e3e0809f22e500db5137` ; `report.json` = `d4d7abad9a3dccb71d8204cf13b58cf202883901f6e9355fcddd688cf0c1c53d`.

Ces deux programmes réutilisent des notions et sources proches et ne constituent **pas** deux cohorte aveugles indépendantes de progression de compétences. Les archives sont périssables ; les empreintes permettent de détecter une modification du dossier déjà téléchargé, pas de retrouver un artefact expiré ni de certifier l'origine des sources externes.

## Correctifs d'architecture livrés dans la PR #250

- `omega_hybrid_example_clinic.py` et `test_omega_hybrid_real02_forensic.py` identifient si les **champs sont absents** (`MISSING_STRUCTURED_EXAMPLES`), présents mais **malformés**, ou corrects en format mais **faux mathématiquement**, en retournant le témoin exact de l'oracle sur les graphes réellement soumis. Aucun graphe manquant n'est construit silencieusement à la place du modèle.
- `omega_hybrid_schema_retry.py` permet **au maximum un nouvel appel**, spécifiquement sur les champs manquants, et demande au modèle d'inventer les arêtes sans en fournir. La réponse brute et les raisons du rejet restent archivées. Les graphes initialement faux ne sont pas « réparés » en silence.
- `omega_hybrid_example_clinic.py` peut créer **quatre exercices de pratique à quatre nœuds** (deux positifs et deux négatifs, non isomorphes), en enregistrant les invites sans réponses dans un fichier et l'oracle dans un **autre**. Ces exercices de pratique ne sont pas une évaluation indépendante des poids du modèle.
- `omega_hybrid_schema_real01.py` et le workflow dédié enregistrent une expérience réelle à un appel Qwen3B seulement sur le **cas ancien déjà exposé**, pour mesurer la capacité du modèle à répondre à une consigne structurée. **Ce n'est pas un test autonome de nouvelle connaissance.**

## Décision et prochains tests

1. **Seuil de format** : deux listes d'arêtes explicites, JSON valide, zéro cas corrigé hors protocole. En cas d'absence, au plus un appel additionnel documenté ; sinon arrêt.
2. **Seuil mathématique** : l'exemple positif satisfait *tous* les axiomes, le négatif en viole au moins un avec témoin calculé. Une preuve sur trois objets ne justifie pas de théorème général.
3. **Seuil de transfert** : utiliser une nouvelle cohorte, des instances non isomorphes et d'autres tailles, un modèle figé, des budgets appariés et un contrôle neutre. Aucune des deux archives du 23 novembre ne peut servir de holdout nouveau.
4. **Seuil de consolidation** : avant tout entraînement SFT/LoRA, corpus approuvé indépendamment, déduplication, absence de fuite de corrigé, contrôle d'oubli et comparaison de checkpoints.

**Conclusion :** cette itération améliore *l'observabilité des échecs et les conditions d'une expérience future*, pas les capacités intrinsèques d'Omega.