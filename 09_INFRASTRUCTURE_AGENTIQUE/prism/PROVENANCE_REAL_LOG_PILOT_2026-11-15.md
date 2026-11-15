# Pilote de lecture de journaux réels — 15 novembre 2026

Statut : **OBSERVATIONS RÉELLES, PAS CERTIFICATION SCIENTIFIQUE**.

## Sources brutes indépendantes du code d'extraction

- [Run 43724979863, job 132844845630](https://github.com/Abrasax63/Omega-pub/actions/runs/43724979863/job/132844845630) : journal GitHub Actions consulté, checkout affiché `2b72bbe`, suites `10`, `80` et `6` tests.
- [Même run, job 132844845631](https://github.com/Abrasax63/Omega-pub/actions/runs/43724979863/job/132844845631) : checkout affiché `2b72bbe`, verdict affiché `Candidate alpha: recalcul`, `Candidate beta: copie`.
- [Run 43724963194, job 132844796587](https://github.com/Abrasax63/Omega-pub/actions/runs/43724963194/job/132844796587) : checkout affiché `2572265`, suites `10`, `75` et `6` tests.

## Confrontation au corrigé externe minimal

Le rattachement job → run est fourni par l'API GitHub et non par le texte des journaux.
Les deux premiers jobs sont dans **la même exécution 43724979863**. Ils ne
constituent donc pas deux reproductions indépendantes. Le troisième appartient
à un autre run, mais cette distinction n'établit pas l'indépendance causale
des calculs, données et scripts.

La PR propose `provenance_log_evidence.py` pour relever les lignes, les
checkouts, les comptes de tests et les empreintes des journaux. Le programme
`provenance_log_holdout.py` calcule les groupes par run_id, tout en
refusant de conclure à une indépendance scientifique.

## Limites décisives

- Cette première confrontation **n'est pas aveugle** : les identifiants
  et la relation job/run ont été examinés lors de la conception.
- Les journaux ont été consultés via l'API, mais les fichiers bruts ne sont
  pas encore archivés comme artefacts d'un test CI réservé et immuable.
- Les empreintes de journaux sont calculables par le script, mais non
  publiées ici comme mesures vérifiées sur les fichiers complets.
- Les observations ne démontrent pas que le programme a reconstruit seul
  une chaîne de dépendances entre artefacts.
- Le dernier commit du pilote doit encore passer sa propre CI.

## Prochaine expérience falsifiable

Sélectionner des runs GitHub **non vus** lors de la conception ; geler
leurs identifiants et journaux bruts, puis masquer les groupes au
vérificateur. Comparer les relations produites à un corrigé établi
séparément depuis l'API GitHub et les dépendances de jobs. Mesurer
précision, abstentions et faux liens, sans confondre identité des
exécutions et indépendance des calculs.
