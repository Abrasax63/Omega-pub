# OMEGA-NEW5-ABC-02 — préenregistrement prospectif (2026-11-16)

**Statut initial : protocole gelé, aucun correctif exécuté ni confirmé pour cette nouvelle cohorte.**
Succède à [PR #108](https://github.com/Abrasax63/Omega-pub/pull/108) et réutilise son moteur et son oracle séparé. Tous les premiers essais de la cohorte #108 sont **historiques**, ne sont ni rejoués comme données nouvelles ni agrégés comme réplications indépendantes.

## Cohorte externe, choisie avant code ou exécution

Source : [BugsInPy, projet tqdm](https://github.com/soarsmu/BugsInPy/tree/master/projects/tqdm/bugs). Seuls les fichiers `bug.info` et `run_test.sh` des bugs 5, 6, 7, 8, 9 ont été consultés. Ne pas inspecter les correctifs historiques avant que les choix A/B/C aient été figés dans l'artefact du premier job.

- N1 = tqdm-5, `test_bool`, buggy `19b08ab34fdbfa0275bc5cb2430436c724c7e759`, fixed `4f340697af69b71850aad496387c9c5aa1904136`.
- N2 = tqdm-6, `test_imap`, buggy `a4b9c86db548b2d0dbb5af7a6bbdc26ab47e1eec`, fixed `6dad2e89019317e875c46d5a3a82a811ad6de2f9`.
- N3 = tqdm-7, `test_main`, buggy `caefe02fd6f3165e5634460ab20caf4c60400120`, fixed `4efd35246c924236f34d8130b1055a3c3ba78605`.
- N4 = tqdm-8, `test_format_meter`, buggy `08b8ad1ff3bd003ef8309faaa0cc108ffa40317d`, fixed `cae9d139c6df5614be3bf6e25ccbd600ee3286dc`.
- N5 = tqdm-9, `test_si_format` (première cible déclarée dans `run_test.sh`), buggy `9da1d5d116aec7a23d8f6dc22d5e23ecb1c40a7c`, fixed `d877c1dfb4739852105f7b967a8fceb869ac5042`. Le second test `test_update` n'est **pas** inclus dans le critère primaire ; le signaler comme limite.

**Corrélation : cinq bugs d'un SEUL projet** ; le nombre de projets indépendants est 1. Tests upstream authentiques mais publics, pas de réserve secrète ni de généralisation garantie.

## Hypothèse et comparaison

Même grammaire AST que #108, même pool de correctifs par bug (max. 90), deux lignes éditables au maximum. Le moteur reçoit le code défectueux et le test upstream, pas la ligne de correction ni le diff fixe.
- A = priorité lexicale déterministe, max. **4 tests de patch** par bug.
- B = priorité via traces réelles de la régression, **même pool**, max. **4 tests de patch**.
- C = la même liste que B, et **une seule** inférence locale Qwen2.5-Coder-3B par bug (128 tokens de sortie maximum), ID d'une liste de 12, puis max. **4 tests de patch**. Identifiant invalide : abstention sans repli.
- Tous les bras sont comparés sur le **même budget logique de tests** (plafond de 4), mais **PAS sur coût CPU total égal** : Qwen ajoute de l'inférence, B/C des traces, et les essais identiques peuvent être mutualisés physiquement. Les coûts et temps doivent être rapportés séparément ; aucun bénéfice à coût complet égal ne peut être affirmé.
- Ne pas conclure sur la valeur propre de la mémoire RCE : il n'existe pas d'ablation RCE dans ces trois bras.

## Étapes non négociables

1. Avant tout test, valider l'intégrité des métadonnées BugsInPy et le contenu du manifeste `COHORT_02_FREEZE.json`. Ne pas ouvrir de diff fixe en amont.
2. Job 1 : récupérer uniquement le code buggy SHA exact et le fichier de test historique autorisé. Reproduire `buggy FAIL`; générer les candidates, mesurer A/B/C ; figer les sources, les choix, traces et empreintes dans `selection.json`.
3. Job 2 séparé, après téléchargement et contrôle du gel : consulter pour la **première fois dans ce protocole** la source fixed et valider `fixed PASS`, `buggy FAIL`, `patch PASS` pour conclure sur **ce test ciblé seulement**. Les bloqueurs de dépendances et les tests non reproduits sont conservés, pas imputés à un bras.
4. Mesurer : corrections par bras, erreurs non corrigées, abstentions, nombre de tests logiques, nombre de tests Docker distincts, coûts d'inférence et d'instrumentation, traces SHA. Si les coûts complets ne sont pas mesurables, indiquer **INDÉTERMINÉ** plutôt que « budget total égal ».
5. Pas de remplacement de bugs après observation, pas de correctif de grammaire inspiré du diff sur cette cohorte, pas de fusion, pas de promotion CORE, jamais d'affirmation d'intelligence générale.

**Critère falsifiable :** au moins un cas reproductible `buggy FAIL / fixed PASS`, et comparaison A/B/C sur la même cible, à plafond de tests commun. S'il n'y a aucune réparation, valeur propre de Qwen non démontrée, et diagnostic du verrou (couverture grammaticale / choix / infrastructure) sous `INDÉTERMINÉ` si la trace ne permet pas de départager.

**Limite :** protocole prospectif par séparation de jobs, pas une étude aveugle externe indépendante, car les commits corrigés sont publics.
