# SELF-TEACH-04 — résultats du premier et unique essai réel (23 novembre 2026)

## Provenance
- Préenregistrement des trois cohortes **avant code et avant inférence** : [commit 22a32545](https://github.com/Abrasax63/Omega-pub/commit/22a32545bb5b149e55c912d13e07c9a1bdd98498).
- Implémentation unique du générateur/scoreur/garde : [commit a54965d](https://github.com/Abrasax63/Omega-pub/commit/a54965d977094b107719fad80480ee6522641af5).
- Premier [run GitHub Actions #45254057012](https://github.com/Abrasax63/Omega-pub/actions/runs/45254057012) : **SUCCESS technique**, 2 jobs verts, **7/7 tests logiciels hors ligne**, puis véritable Qwen2.5-3B-Instruct Q4_K_M local sur CPU.
- [Archive des sorties originales et du score #14857545971](https://github.com/Abrasax63/Omega-pub/actions/runs/45254057012/artifacts/14857545971), dont `raw.json`, `score.json`, journaux et empreintes. Empreintes SHA-256 : `raw.json = 7747616fd8832a54c8288509f7116999a22d435d381ee0d8be5f9dcd8bcb06f7` ; `score.json = 58b334a54d9b9eb7086c7bb7159cbed6c2a3c4d62a86dfcf4b016402062fc415`.
- Budget effectif : **10 appels au modèle**, 3 241 jetons d'entrée, 1 435 de sortie, 142,638 s dans la génération, zéro appel API payante, aucune modification des poids, `main` inchangée.
- Tête du journal d'entraînement chaîné SHA-256 : `352274c4f45ce347c5f9069575e30ed98adf6f20bd86330119f6d49ef0c15a2e`.

## Résultat sur les 18 tests réservés, désormais consommés

| Bras | Exact / 18 | Fonctions totalement correctes / 3 | Détail Q1/Q2/Q3 |
| --- | ---: | ---: | --- |
| A, réponse directe | **2/18** | 0/3 | 0/6, 0/6, 2/6 |
| P, conseil neutre | **12/18** | 1/3 | 6/6, 4/6, 2/6 |
| B, leçon admise ou alias contrôlé de P | **12/18** | 1/3 | 6/6, 4/6, 2/6 |

**Résultat préenregistré : `NO_AUTONOMOUS_LEARNING_GAIN_DEMONSTRATED`.** L'écart P–A de dix tests sur cette petite cohorte est réel mais n'est ni un entraînement de poids ni un effet d'une leçon acquise. **Aucune leçon n'a été admise.** La nouvelle garde applique B = P **octet pour octet** sur les générations et les codes, à tag de traçabilité près. Elle économise **trois appels de modèle** qui n'auraient fait que rééchantillonner le même prompt neutre. Le gain B–P est **0**. Pas d'inférence causale générale.

## Audit de pratique : blocage précis

- R1, regroupement des caractères identiques : **10/10 dès la réponse initiale** du modèle. Cette compétence était déjà disponible sur cette tâche ; elle n'est pas nouvellement apprise.
- R2, sous-chaînes de chiffres contigus : **0/10 selon le score de lot**, deux réparations sans amélioration, meilleur état conservé, aucune leçon.
- Le code brut initial R2 pose `j` **dans une branche conditionnelle seulement** puis exécute `i = j` après cette branche. Pour certaines entrées, `j` n'a pas été initialisé et l'exécution produit une `UnboundLocalError`; pour d'autres, `i` reste bloqué et le programme entre dans une boucle sans progrès. Deux corrections proposées par le modèle conservent l'erreur essentielle.
- **Défaut supplémentaire du banc d'entraînement** : `grade_cases` évalue les 10 chaînes dans **un même sous-processus**. Si un seul exemple dépasse la limite CPU, l'ensemble du lot reçoit `SANDBOX_EXIT_-9`, ce qui masque les comportements individuels. Ainsi le 0/10 du lot ne prouve pas que les dix entrées échouent séparément.

### Vérification locale supplémentaire (diagnostic rétrospectif, pas nouveau holdout)
Le code brut R2 du run a été rejoué en lecture seule sur des cas de **développement déjà consommés**, un par un, dans un travailleur Python isolé reprenant les limites CPU/AS et les builtins du sandbox.

- `a00` : `UnboundLocalError` plutôt que le seul `SANDBOX_EXIT_-9` du lot.
- `5` : sortie `['5']`, qui est fausse car un run d'un seul chiffre doit être ignoré.
- `0:01` : `SANDBOX_EXIT_-9` en exécution individuelle, conforme au défaut de progression.
- Les autres cas sont documentés dans la trace brute ; aucun de ces replays n'est une nouvelle preuve aveugle ou un apprentissage.

**Prochaine expérience décisive (NON exécutée ici)** : avant tout nouveau score aveugle, introduire un diagnostic de développement isolant les erreurs de lot (échec avec statut de la première entrée en cause, et éventuel témoin de non-progression). Tester la nouvelle présentation du feedback **contre le feedback originel**, à appels et tâches identiques sur une cohorte entièrement nouvelle ; ne jamais communiquer le code référence. Ne pas régénérer le holdout SELF-TEACH-04 pour prétendre à une réplication indépendante.

## Statuts
- Protocole et cohortes : **PRÉENREGISTRÉS**.
- Code et contrôles : **IMPLÉMENTÉS, 7/7 TESTS PASSÉS**.
- Modèle réel : **EXÉCUTÉ**.
- Auto-apprentissage/transfert : **NON DÉMONTRÉ**.
- Diagnostic de l'échec en lot : **OBSERVÉ ET REPRODUIT RÉTROSPECTIVEMENT**.
- Fusion / promotion mémoire / entraînement automatique : **NON AUTORISÉS** ; PR reste DRAFT.
