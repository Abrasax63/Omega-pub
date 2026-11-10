# P5 — pipeline d'analyse descriptive v0.2

**Statut :** outil préparatoire ; aucune donnée expérimentale réelle n'est incluse.
**Compatibilité :** protocole P5 v0.2 et validateur de notes v0.2.
**Confidentialité :** clé d'aveuglement et sorties brutes conservées hors du dépôt public.

## Objectif

Transformer des notes aveugles figées en comparaisons appariées par cas, sans
fabriquer de verdict scientifique. Le pipeline utilise uniquement la bibliothèque
standard Python ; aucune dépendance externe ni calcul statistique lourd n'est requis.

## Fichiers d'entrée

1. ratings.jsonl : une ligne par couple (cas, sortie opaque, évaluateur), conforme
   à prism/evaluation.py. Le fichier ne contient jamais le bras A/B/C.
2. blind_key.json : fichier privé, utilisé uniquement après gel des notes.

Format attendu de la clé (identifiants fictifs) :

    {
      "mappings": [
        {"case_id": "case-01", "blind_output_id": "opaque-1", "arm": "A"},
        {"case_id": "case-01", "blind_output_id": "opaque-2", "arm": "B"},
        {"case_id": "case-01", "blind_output_id": "opaque-3", "arm": "C"}
      ]
    }

Ne jamais déposer la clé réelle dans le dépôt public, un artefact CI public,
ni dans un espace accessible aux évaluateurs.

## Exécution

Depuis le dossier prism :

    from analysis import analyze_files

    result = analyze_files(
        ratings_path="/private/p5/ratings.jsonl",
        blind_key_path="/private/p5/blind_key.json",
        output_path="/private/p5/analysis.json",
        ratings_sha256=frozen_ratings_digest,  # fourni par le registre privé du gel
        expected_case_ids={"case-01", "case-02", "case-03", "case-04", "case-05"},
    )
    print(result["validation"])

Les identifiants attendus doivent correspondre au pré-enregistrement réel,
pas à des noms supposés. Les fichiers privés ne sont pas copiés dans le dépôt.

## Sorties

- moyennes et étendues des six dimensions, par cas et par bras ;
- étendue des désaccords entre évaluateurs, dimension par dimension ;
- comparaisons appariées C−A, C−B et B−A, séparées pour chaque dimension ;
- nombre de cas favorables, égaux et défavorables ;
- comptages d'erreurs rapportés par les évaluateurs, explicitement étiquetés.

Aucun score composite, test de significativité, intervalle artificiel,
classement global ou certification n'est calculé. Avec cinq cas hétérogènes,
les résultats restent descriptifs et exploratoires.

## Garde-fous

- Vérifier l'empreinte SHA-256 et la liste de cas pré-enregistrée, puis valider les
  notes avant de lire la clé. L'empreinte doit venir du registre de gel privé,
  conservé séparément avec contrôle d'accès et horodatage.
- La clé doit couvrir exactement chaque couple cas/sortie opaque, sans doublon.
- Chaque cas doit avoir exactement une sortie par bras et répétition.
  Pour plusieurs répétitions, passer le nombre pré-enregistré avec
  `repetitions=` et donner un entier de 1 à ce nombre dans chaque entrée
  `repetition` de la clé privée. Les notes restent opaques.
- Chaque évaluateur doit noter toutes les sorties d'un cas. Les répétitions
  sont moyennées à l'intérieur du cas et ne gonflent pas le nombre de cas.
- Les notes initiales et les arbitrages restent dans des fichiers séparés.
- Ne pas moyenner les coûts, durées ou appels répétés dans les lignes de notation :
  ces mesures appartiennent au journal d'exécution, une ligne par exécution.
- L'outil ne prouve ni l'aveuglement ni l'indépendance humaine ; ces points exigent
  une procédure et des attestations externes.

## Limite de lancement

Ce pipeline ne crée pas de holdout privé et ne génère aucune réponse A/B/C.
Le holdout v0.2 reste un pilote public, pas un test secret garanti. Le lancement
attend un nouveau jeu non exposé, son corrigé privé vérifié, les prompts et budgets
gelés, et deux évaluateurs réellement indépendants. Aucun accès au corrigé n'est
requis pour exécuter le pipeline.
