# OMEGA-LEAN-001 — état contrôlé avant validation du noyau Lean

**11 novembre 2026. Statuts provisoires : CALCUL FINI INDÉPENDANT pour le corpus ; LEAN FORMEL NON ENCORE VALIDÉ. Ne pas citer cette note comme preuve formelle de compilation.**

## Sources et gel

- 4 scénarios, 24 états, 91 questions, corpus synthétique verrouillé au commit `de4a08399a0f99d420f13e360fbf1deed5785161` **avant le programme** ;
- protocole et comparateurs gelés `5ec12b01b21f6e1216e81922aed9a01096b05ebc` avant le code ;
- Lean 4 v4.26.0 fixe, release officielle https://github.com/leanprover/lean4/releases/tag/v4.26.0 ;
- code générateur de trois théorèmes Lean par justification, révision de sources et calcul du coût : `formal_congruence/lean_proof_revision.py` ;
- contre-tests `formal_congruence/test_lean_proof_revision.py` ; contrôle JS extérieur aux fonctions CRT `formal_congruence/independent_lean_certificate_audit.mjs` ; workflow `.github/workflows/omega-lean-proof-revision.yml`.

## Calcul fini externe au compilateur, effectué à partir du corpus gelé

Un calcul **indépendant en JavaScript**, par énumération directe des 60 résidus, sans exécuter ni réutiliser le fichier Python du nouveau générateur, retrouve :

| Partition | États | Jugements | Impliqués | Réfutés | Indéterminés | Environnements incohérents | Supports actifs | Jugements à ≥2 supports |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Calibration | 11 | 39 | 22 | 5 | 8 | 4 | 41 | 12 |
| Test | 13 | 52 | 33 | 7 | 8 | 4 | 54 | 12 |
| Total | **24** | **91** | **55** | **12** | **16** | **8** | **95** | **24** |

Sur l'épreuve `SOURCE_REVISION`, la requête `n % 3 = 2` est :
1. impliquée à l'état initial par A et B ;
2. suspendue lorsque A est remplacée par `n % 6 = 1`, contradictoire avec B `n % 12 = 8` ;
3. réfutée par la nouvelle A après retrait de B ;
4. de nouveau impliquée après rétablissement de l'ancienne version A ;
5. de nouveau soutenue par deux voies si B est réactivée.

Ce calcul ne constitue ni un verdict du noyau Lean ni un résultat sur des problèmes mathématiques indépendants.

### Économie PRÉVUE de recompilation (non exécutée à ce stade)

D'après les supports exacts du corpus, **95 applications** de justifications correspondent à seulement **39 certificats conditionnels distincts, liés aux versions exactes des sources**. À raison d'un fichier de preuves par état et d'un fichier par ensemble de termes nouveaux :
- `full_recompile` devrait effectuer **21 invocations Lean et 95 chaînes de trois théorèmes** ;
- `strong_atms_index` et `omega_proof_ledger` devraient effectuer **chacun 10 invocations Lean et 39 chaînes de trois théorèmes** ;
- ces différences ne sont **pas des temps mesurés**, et le coût du maintien de l'index n'est pas compris dans le seul nombre d'invocations ;
- l'égalité de la politique indexée et de l'adaptateur Omega est attendue, donc **aucun gain propre** ne pourra être revendiqué si elle se confirme.

Le contrôle `no_revision` présente à tort une conclusion initiale devenue non applicable dans **24 évaluations** : 5 en calibration et 19 en test.

## Point d'épistémologie à protéger

Un terme Lean démontrant `(n%6=2) → (n%3=2)` peut rester formellement valide après retrait du fait source `n%6=2`. Cela **n'autorise pas** à affirmer `n%3=2` sans autre prémisse active.

Pire, le noyau Lean accepte logiquement le principe d'explosion : `n%2=0` et `n%2=1` permettent, **sous ces hypothèses incompatibles**, une implication vers n'importe quelle conclusion. Le garde externe de cohérence doit donc refuser toute promotion de ces termes à des conclusions scientifiques globales.

Les tests négatifs exigeront que Lean **rejette** un faux théorème non prouvable et une preuve sans prémisse, et qu'il puisse **accepter** l'exemple d'ex falso conditionnel tout en le laissant hors du registre de conclusions admises. **Ces contrôles ne sont pas encore certifiés par une exécution Lean.**

## CI : limites de la vérification à cette date

Le [workflow Lean sur la PR #44](https://github.com/Abrasax63/Omega-pub/pull/44) est créé et déclenché mais les runs restent dans l'état **`queued`**, sans job exploitable ni journal de compilation au dernier contrôle de cet état. Voir [run du dernier commit de contrôle `43096261141`](https://github.com/Abrasax63/Omega-pub/actions/runs/43096261141).

**Interdit tant qu'un run Lean n'est pas SUCCESS :** dire « 39 preuves formellement vérifiées », « compilées », « Lean certifie » ou « résultats de kernel démontrés ». Le code est prêt à être audité et l'arithmétique du corpus est contrôlée séparément ; **l'étape Lean est NON VÉRIFIÉE**.

## Décision expérimentale

La cible scientifique demeure la comparaison d'une mémoire Omega avec un **ATMS/index fort à information, preuves et coûts identiques**. Ce prototype est construit et non aveugle ; même une réussite complète de compilation montrerait seulement des implications modulaires conditionnelles et une mise à jour contrôlée de leurs dépendances. Une preuve d'intelligence stratégique supérieure demanderait encore une épreuve différente, issue de démonstrations indépendantes et d'une capacité réelle à trouver/choisir la prochaine preuve.

PR expérimentale en brouillon ; `main`, SQLite, CORE et mémoire durable inchangés.
