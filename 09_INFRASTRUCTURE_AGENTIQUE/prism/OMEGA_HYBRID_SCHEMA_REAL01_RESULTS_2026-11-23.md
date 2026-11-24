# OMEGA-HYBRID-SCHEMA-REAL-01 — verdict du modèle réel, 23 novembre 2026

**Statut scientifique : FORMAT DE SORTIE RÉUSSI DANS CE CAS ; EXEMPLE POSITIF MATHÉMATIQUEMENT RÉFUTÉ ; AUCUN APPRENTISSAGE DÉMONTRÉ.** Le workflow termine `SUCCESS` pour l'archivage d'un résultat négatif, pas pour une certification scientifique. Aucune modification de `main`, aucun entraînement, aucune API payante.

## Provenance

- [Run GitHub #45274034725](https://github.com/Abrasax63/Omega-pub/actions/runs/45274034725), déclenché **une seule fois** par ajout du workflow, événement `push` avec filtre exclusif sur son chemin.
- [Artefact brut #14865223804](https://github.com/Abrasax63/Omega-pub/actions/runs/45274034725/artifacts/14865223804), cinq fichiers dont `result.json`, `model.sha256`, `summary.log`. SHA-256 du ZIP obtenu : `fe9f90d984c3c7db642cdfef81a7933c303af69a5f9606b6205c2c09c7403be8` ; SHA-256 du `result.json` lu : `f54f6060cb3e2426bccf2be9e71065a9b5c1bb4bf0d90b7f9d31a954ae5a83d9`.
- Source du sujet déjà exposé : [REAL-02 #45119536096](https://github.com/Abrasax63/Omega-pub/actions/runs/45119536096), candidat `candidate.jsonl` SHA-256 `04fe0bd95fdf92e390b94a1a7f2238f5134b85f0a488e3e0809f22e500db5137`.
- Qwen2.5-3B-Instruct Q4_K_M identique à REAL-02 par contrôle SHA-256 des poids ; llama.cpp b12633, exécution CPU, température 0, seed contrôlée dans `RealClient`. **Même notion, même modèle, aucun holdout scientifique neuf.**

## Déroulement exact

Le modèle avait antérieurement choisi « relation d'équivalence », et identifié `reflexive, symmetric, transitive`. Sa sortie REAL-02 la plus récente n'incluait ni `positive_edges` ni `negative_edges`. Le correctif `schema_retry` lui demande, une **seule fois**, de construire les deux exemples sur a,b,c **sans lui donner les arêtes correctes ni l'oracle**.

La sortie contient cette fois **exactement** les deux champs requis, au format JSON valide :

```json
{
  "positive_edges": [["a","a"],["b","b"],["c","c"],["a","b"],["b","a"],["b","c"],["c","b"]],
  "negative_edges": []
}
```

**Verdict exact de l'oracle préexistant :**
- Exemple annoncé **positif : FAUX**. La relation contient `aRb` et `bRc` mais pas `aRc`. Elle viole la **transitivité**, témoin `(a,b,c)`. Ainsi elle n'est pas une relation d'équivalence.
- Exemple annoncé **négatif : CORRECT**. La relation vide n'est pas réflexive sur `{a,b,c}`, témoin `(a,a)` (entre autres).
- Statut final : `QUARANTINE`, cause `MATHEMATICAL_COUNTEREXAMPLE`. `scientific_claims_certified=0`.

**Ressources réellement enregistrées :** 1 appel Qwen CPU, 172 tokens de prompt, 71 tokens produits (243 au total), 12,858 s d'inférence mesurée par le client. Les sorties brutes sont préservées et non remplacées par une correction calculée par le système.

## Interprétation

1. Le ciblage du schéma peut résoudre le défaut de sortie **dans cet essai** : les deux champs manquants sont présents. Ce constat ne permet pas d'affirmer un taux de réussite général.
2. Le modèle n'a **pas** construit une paire mathématiquement admissible. Même avec une définition et des axiomes explicites, une lacune de transitivité subsiste.
3. Le vérificateur exact et la quarantaine ont correctement arrêté la promotion ; c'est une **capacité du système logiciel**, pas la preuve d'une nouvelle compétence du modèle.
4. Ce test **ne mesure ni changement durable, ni transfert, ni poids entraînés**. La notion était déjà connue et le nombre d'appels est un.

## Suite scientifiquement discriminante

**Ne pas relancer à répétition cet exercice connu.** Une méthode pouvant réellement enseigner la transitivité devra être comparée à une tentative directe et à une consigne générique, sur un **ensemble d'apprentissage distinct**, avec témoins vérifiés indépendamment. Puis un second ensemble non isomorphe et jamais consulté sera nécessaire pour mesurer le transfert, idéalement après une session neuve. Les exercices à quatre objets de `omega_hybrid_example_clinic.py` sont utilisables pour préparer cet apprentissage mais **pas comme preuve d'amélioration tant qu'aucun modèle n'a été entraîné puis évalué à l'aveugle**.

Décision : conserver #250 en DRAFT, `main` inchangée, aucune mémoire scientifique certifiée ni SFT/LoRA autorisé par ce seul résultat.
