# P5-INDUCE-01 — gel avant les journaux réservés

**15 novembre 2026, UTC.** Branche empilée sur `experiment/provenance-semantic-transfer-2026-11-15` au commit `54d66988d830f94deb6db08db8d3bb176e8b9422`. Aucun changement de `main`, aucune fusion ni certification.

## Question falsifiable

Omega peut-il **induire une nouvelle règle de reconnaissance d'une opération de construction** à partir d'une trace d'un projet Go (`fzf`), puis réappliquer cette règle à des journaux jamais utilisés pour l'entraînement, notamment dans d'autres dépôts ? La règle est un **programme déclaratif borné**, pas du code Python auto-généré ni un agent LLM. Un succès de reconnaissance ne prouve ni l'identité des octets du binaire, ni l'absence de tout autre producteur.

La référence classique est une règle experte **`go build -o <sortie>`**, avec exactement le même extracteur, les mêmes filtres, les mêmes logs, les mêmes témoins et le même coût de lecture. Toute égalité avec cette référence interdit la revendication de gain propre à Omega.

## Entraînement : unique job déjà lu

- [junegunn/fzf — build, run 43003796079, job 130466140326](https://github.com/junegunn/fzf/actions/runs/43003796079/job/130466140326), réussite du 11 novembre, checkout `314cbe1be73849921ce7beb614ce674fae1515b3`.
- [Makefile épinglé](https://github.com/junegunn/fzf/blob/314cbe1be73849921ce7beb614ce674fae1515b3/Makefile) : recette `GOARCH=amd64 $(GO) build $(BUILD_FLAGS) -o $@`. Le log contient une ligne d'exécution `GOARCH=amd64 go build ... -o target/fzf-linux_amd64`.
- La seule annotation d'apprentissage sera **« commande de build explicite exécutée avec destination -o dans un job réussi »**, pas « fichier certifié ». Aucun autre journal de la cohorte d'évaluation n'est disponible pour le constructeur.

## Jobs d'évaluation fixés par métadonnées (journaux NON lus au gel)

| ID | Job, dépôt, checkout | Contrat |
| --- | --- | --- |
| H1 | [fzf 43137398863/130915918123](https://github.com/junegunn/fzf/actions/runs/43137398863/job/130915918123), `4499615fe9c06c0651aa5650e5d0d0a5face99a8` | Successeur même projet ; extraction de toute commande build avec sortie explicite |
| H2 | [Caddy Cross-Build 43617376109/132516131842](https://github.com/caddyserver/caddy/actions/runs/43617376109/job/132516131842), `09a508f328f524be4119abe536bac15de92e3169` | Projet Go inconnu du constructeur, Linux |
| H3 | [go-task/task CI 43467995680/132032174540](https://github.com/go-task/task/actions/runs/43467995680/job/132032174540), `bb2a8adae96a43af1fc8bddb9efd6e4e68ca3b38` | Projet Go différent, job « Build (1.27.x) » |
| H4 | [Hugo Test 43645632266/132602642451](https://github.com/gohugoio/hugo/actions/runs/43645632266/job/132602642451), `bccb192fbc8c59d007bebe6d7967b36eab3ebaff` | Projet Go différent, possible tâche sans destination |
| H5 | [ripgrep ci 43661343801/132651135271](https://github.com/BurntSushi/ripgrep/actions/runs/43661343801/job/132651135271), `178cc027e283fd965cb72d0a7395b219eada170c` | Contrôle négatif Rust : ne pas inventer un build Go |

Les **cinq jobs** et leur ordre sont fixés avant tout téléchargement de leurs journaux. Aucun remplacement d'un job peu favorable. Les jobs partagent des architectures de CI et l'entraînement fzf et H1 le même dépôt : ce ne sont pas cinq répliques indépendantes. C'est une **expérience de transfert bornée**, pas un benchmark général.

## Exécution contrôlée

1. Écrire et tester, avant lecture des logs H1–H5, le constructeur qui repère un sous-ensemble strict de commandes shell avec `-o <chemin>`. Il apprend `(outil, sous-commande, drapeau)` de l'exemple annoté sans avoir une règle Go pré-installée.
2. Le comparateur classique est figé dès maintenant : même parseur mais règle explicite `(go,build,-o)`. Il constitue un contrôle fort de non-supériorité.
3. Préférer le journal complet plutôt qu'un extrait choisi après observation. Budget **une lecture du log par méthode** ; une source épinglée peut servir pour un audit séparé, pas pour réécrire les règles.
4. Scores : jobs avec au moins une commande admissible, extractions correctes des destinations selon contrôle de la ligne, faux déclenchements sur H5, abstentions. Les résultats sont comparés **job par job** et la performance propre est la différence entre le constructeur et le comparateur.
5. Les lignes `echo`, les chaînes citées, les commandes de tests, les `&&` / `;` ambigus, les sorties `/dev/null`, les options `-o` absentes, les logs tronqués et les échecs donnent des abstentions au niveau du signal. Un job `success` ne prouve pas que chaque commande ait été exécutée sans gestion d'erreurs.
6. Journaliser la provenance des règles, les empreintes des données, les contre-exemples et les tentatives infructueuses. Ne pas retoucher le candidat sur la cohorte réservée.

**Critère favorable minimal :** au moins une commande admissible reconnue sur un projet jamais vu, aucune fausse confirmation sur les témoins et aucune information de l'évaluation injectée dans l'apprentissage. **Gain propre Omega :** strictement meilleur que le témoin classique sur un score juste, sinon **non démontré**. Absence de preuve de l'artefact = pas de certification.

Aucune modification des PR #81/#82, aucune promotion CORE, aucun déclenchement manuel de workflow distant.
