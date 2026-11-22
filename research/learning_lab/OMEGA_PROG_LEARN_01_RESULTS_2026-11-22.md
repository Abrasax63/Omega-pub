# OMEGA-PROG-LEARN-01 — audit du premier essai réel (22 novembre 2026)

**Statut : EXÉCUTÉ / TEST TECHNIQUEMENT VALIDE / GAIN DE TRANSFERT NON DÉMONTRÉ.**

## Sources immuables

- Exécution GitHub Actions : https://github.com/Abrasax63/Omega-pub/actions/runs/45062636718 — jobs preflight et modèle tous deux **SUCCESS technique**.
- Artefact brut (7 jours de rétention) : https://github.com/Abrasax63/Omega-pub/actions/runs/45062636718/artifacts/14769758932
- Rapport JSON, code A/B produit, prompts, entrées/sorties, réponses du modèle, notes et coûts dans l'artefact.
- Protocole gelé **avant inférence** : OMEGA_PROG_LEARN_01_PREREG_2026-11-22.md ; SHA workflow/run : 3e60c02dac86dfb443a1bfb13d51bae9c53a4c83.
- Modèle Qwen2.5-3B-Instruct-Q4_K_M ; SHA-256 fixé : 9c9f56a391a3abbd5b89d0245bf6106081bcc3173119d4229235dd9d23253f94.

## Résultats exacts observés

| Bras | Tests de développement réussis (après 1er code) | Tests cachés, premier code | Tests cachés, après réparation |
|---|---:|---:|---:|
| **B_direct** : B sans expérience | 0 / 7 | 0 / 36 | **0 / 36** |
| **A_learning** : apprentissage sur A | 0 / 7 | 1 / 36 | **0 / 36** |
| **B_transfer** : B avec leçon de A | 0 / 7 | 0 / 36 | **0 / 36** |

Coût : **10 appels** au modèle réel ; **4 585** tokens d'entrée et **762**
tokens de sortie reportés par llama.cpp ; **180,003 s** cumulées des requêtes
mesurées par le client (hors téléchargement, serveur, tests et runner).

- B_direct : 3 sondes choisies par le modèle ;
- A_learning : 3 sondes choisies, dont l'entrée vide et des caractères spéciaux ;
- leçon générée après A, assez générale : traiter l'état en boucle, ne pas
  oublier de caractères et tester les cas limites ;
- B_transfer : 3 sondes de sa propre initiative ; aucun cas caché divulgué.
- Les 10 tests logiciels de pré-enregistrement et de sandbox sont tous verts.

**Verdict sur l'hypothèse** : différence B_transfer - B_direct = **0/36**.
Aucun progrès de transfert observable. **On ne peut pas conclure que
l'algorithme de reconstruction a été appris.**

## Diagnostic précis : deux types d'échec

### 1. Échecs du langage Python — confirmés indépendamment

Les programmes B_direct et B_transfer, dès la première version et après
réparation, ont une **erreur de syntaxe Python** sur un littéral de barre
oblique inversée : la chaîne source contient une seule barre oblique
inversée devant le guillemet terminal, ce qui provoque
\`SyntaxError: unterminated string literal\`. Les quatre programmes B
ont été refusés par la vérification AST et ont donc produit **0/36**.
Le problème n'est pas l'oracle caché ni la boîte d'exécution.

Le premier code A était syntaxiquement valide, mais modélisait un
**comptage global de caractères** dans un dictionnaire, pas un
**regroupement de segments adjacents** : seulement **1/36** tests cachés
réussis. La correction A ajoutait un \`}\` final non apparié, déclenchant
\`SyntaxError: unmatched '}'\` : **0/36**.

Il y a donc à la fois **défaut de maîtrise syntaxique de Python** et
**erreur sémantique sur la notion d'état local**.

### 2. Feedback trop peu informatif — défaut de pédagogie du prototype

La première version du protocole renvoie pour une erreur de syntaxe
\`INVALID_PYTHON_SYNTAX\` sans ligne ni message du compilateur.
Le modèle ne reçoit donc PAS l'information déterminante pour comprendre
pourquoi son programme échoue.

Le fait que ses réparations restent syntaxiquement invalides est
cohérent avec cette lacune, mais il est **non démontré** qu'ajouter une
trace de \`SyntaxError\` suffirait à le faire progresser.

Le résumé d'expérience A est générique. Il ne démontre ni compétence
nouvelle ni compréhension transférable.

## Ce que le résultat ne prouve pas

- **N'établit pas** une incapacité intrinsèque de Qwen3B à coder : les
  programmes B n'ont même pas atteint le stade du test fonctionnel.
- **N'établit pas** un effet négatif de la mémoire : les scores B sont tous
  nuls, ce qui empêche de distinguer la compétence algorithmique.
- **N'établit pas** un apprentissage des poids : aucun gradient, aucun
  ajustement de paramètres ni modèle nouvellement entraîné dans l'expérience.
- **N'établit pas** une compréhension du code : les observations pourraient
  simplement être reproduites sans construction d'un modèle général.
- **N'est pas** une vraie comparaison de budget total identique : l'arm
  B_transfer consomme 4 appels supplémentaires pour A et le résumé.

## Vérification décisive suivante — jeu nouveau, protocole nouveau

**Ne pas modifier le code original et rejouer son holdout comme une nouvelle
réplication indépendante**. Les 36 cas B sont désormais exposés au développeur
dans l'artefact.

Nouvelle expérience recommandée :

1. Choisir **deux nouveaux programmes inconnus et des nouveaux cas cachés**,
   avec protocole gelé avant inférence et matériel pédagogique non renseigné.
2. À chaque essai, demander au modèle d'exécuter une étape **compilation Python
   seule** : renvoyer le type, la ligne et la phrase exacte de \`SyntaxError\`,
   sans exposer la source de l'oracle. Il doit corriger lui-même et montrer
   qu'il peut aboutir à un programme syntaxiquement valide.
3. Ensuite, seulement, fournir les erreurs fonctionnelles sur un ensemble de
   développement fixé. Garder un test caché strictement inaccessible.
4. Refaire B_direct et B_transfer, avec mêmes budgets de réparation et
   comptabilité de tous les appels. Maintenir les tests syntaxiques identiques
   entre les deux bras.
5. Classer séparément : **valide en Python**, **fonctionnel sur le développement**,
   **fonctionnel sur les données inconnues**, **gain du transfert**, **coût**.
6. Si le modèle écrit un programme complet et gagne les tâches inconnues,
   examiner ensuite l'option d'un véritable entraînement supervisé ou LoRA
   à partir des trajectoires, sur données distinctes et auditées.

La correction du feedback est une **amélioration du protocole d'apprentissage**,
pas une nouvelle règle mathématique arbitraire ; aucune compétence ne doit
être déclarée acquise sans test aveugle.

## Sécurité et intégrité

- \`main\` inchangée ; PR #232 DRAFT et expérimentale.
- Dépôt existant PUBLIC : pas de dépôt privé créé.
- Aucun programme généré n'a obtenu d'accès fichier, réseau ou secrets.
- Aucun appel d'API payante, aucun cron permanent.
- Seuls des exemples artificiels ont été utilisés.

**Conclusion :** le premier test établit la faisabilité de la chaîne de
reconstruction et mesure son échec. Avant l'autoconstruction de modèles IA,
Omega doit encore apprendre le langage de programmation et recevoir un
feedback plus pédagogique, puis démontrer que cela améliore ses résultats
sur du code jamais vu.
