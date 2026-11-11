# OMEGA-PROV-001 · audit et résultats v0.1

**Question.** À observations, hypothèses et plafond de consultations égaux, le contrôle de provenance et la planification adaptative améliorent-ils le verdict face à une référence forte ?

**Conclusion.** INDÉTERMINÉ pour les problèmes nouveaux avec des modèles. Sur la calibration publique, le filtre de provenance corrige certaines erreurs de l'optimiseur à hypothèses idéalisées, avec six consultations supplémentaires. Le routage fixe équipé du même filtre obtient exactement les mêmes décisions et coûts qu'Omega sur les douze cas. Une règle conditionnelle simple bat le coût d'Omega sur le rejeu de la PR #29.

## État initial audité

Base expérimentale `9e06385771552b5715b0a330da001173fc8adece`. Les SHA de tête/base des PR concordent sur la pile #22 → #23 → #24 → #25 → #28 → #29 → #30. La PR #22 part de la branche de pipeline P5. La pile mathématique #26 → #27 part de main et ne figure pas parmi les dépendances de cette pile. Les neuf PR consultées sont ouvertes et en brouillon dans l'instantané inspecté.

| PR | Ce que les artefacts établissent | Référence |
| --- | --- | --- |
| 22 | 24/24 accords avec le calcul de référence, 20/24 pour le premier gain positif. Modèles synthétiques à un pas. | [PR](https://github.com/Abrasax63/Omega-pub/pull/22) · [CI](https://github.com/Abrasax63/Omega-pub/actions/runs/42910778727) |
| 23 | 24 cas construits et 96 semés, accord avec l'oracle exhaustif, améliorations strictes 8 et 34. | [PR](https://github.com/Abrasax63/Omega-pub/pull/23) · [CI](https://github.com/Abrasax63/Omega-pub/actions/runs/42912736307) |
| 24 | 480 accords sur 120 modèles et 4 profondeurs d'oracle, 3 gains stricts entre profondeurs 2 et 3. Parités contrôlées séparément. | [PR](https://github.com/Abrasax63/Omega-pub/pull/24) · [CI](https://github.com/Abrasax63/Omega-pub/actions/runs/42916831933) |
| 25 | 24/24 sur format documentaire contrôlé et 96 prompts préparés. Le contexte fourni à l'ancien bras C change l'information initiale. Aucun score de modèle. | [PR](https://github.com/Abrasax63/Omega-pub/pull/25) · [CI](https://github.com/Abrasax63/Omega-pub/actions/runs/42918722407) |
| 26–27 | Branche mathématique séparée. Aucun run PR retourné pour la tête #26 par le connecteur. Le journal #27 confirme l'exécution de l'audit fini, dont 512 constructions, 119 singletons et 127 colorations exclues dans le graphe contraint. L'audit présent ne certifie aucune preuve universelle de la pile. | [PR 26](https://github.com/Abrasax63/Omega-pub/pull/26) · [PR 27](https://github.com/Abrasax63/Omega-pub/pull/27) · [journal](https://github.com/Abrasax63/Omega-pub/actions/runs/42992812545/job/130429540611) |
| 28 | CALCUL EXACT, 793/1 391 contre 777/1 391 sur tableaux aléatoires (+1,15 point) et 240/360 contre 180/360 sur cas construits (+16,67 points). Coût unitaire nul dans la fonction objectif, plafond de deux contrôles, vérité générée, comparaison avec le meilleur couple fixe. Ce résultat identifie la valeur du choix conditionnel sous le modèle. | [script](prism/equal_budget_pilot.py) · [journal](https://github.com/Abrasax63/Omega-pub/actions/runs/42992672378/job/130429076510) |
| 29 | Données issues de 12 PR externes selon le rapport et son instantané. Rejeu exact de 11/12 direct et 12/12 pour chacun des deux bras outillés, coûts 24/17. Une seule décision positive. Deux lectures GitHub partagent la source et la vérité est calculée avec les mêmes champs. CI sur instantané, aucune recollecte historique. | [instantané](prism/live_github_pr_gate_observations_2026-11-11.json) · [journal](https://github.com/Abrasax63/Omega-pub/actions/runs/43005701250/job/130472518311) |
| 30 | Rejeu 24/24 pour Omega et le contrôle fixe sur observation intègre, 16/24 et 8 erreurs confiantes chacun après injection. Les deux verdicts sont assignés à la même valeur observée dans le script. Le diagnostic avec clé connaît la vérité. Deux méthodes GitHub partagent le fournisseur, et seules certaines assertions URI/Python ont une vérification exécutable. | [script](prism/p5_multidomain_adversarial.py) · [journal](https://github.com/Abrasax63/Omega-pub/actions/runs/43018963852/job/130517041120) |

Les journaux #28/#29/#30 confirment les tests nommés et respectivement 112/115/119 tests du Prisme. Ils contrôlent le logiciel et les valeurs gelées. Les trois rejeux ont également été reproduits localement depuis les fichiers lus au SHA de base. Les latences de #29 incluent les lots concurrents du connecteur. Leur somme est impropre à une comparaison contrôlée.

**Contre-exemple au gain de coût face à une règle conditionnelle forte, PR #29.** Pour décider `fusionnée ET touche les tests`, interroger d'abord les fichiers puis la fusion uniquement lorsque le prédicat « touche les tests » est vrai. Les trois lignes concernées imposent un deuxième appel. Cette règle atteint 12/12 en 15 appels comptés sur l'instantané, contre 12/12 en 17 appels pour Omega et 12/12 en 24 pour le plan fixe intégral. Les 15 appels sont un CALCUL EXACT de rejeu, pas 15 appels réseau effectués. Le choix de l'ordre est rétrospectif. Dans le modèle uniforme de la PR #29, les deux ordres ont le même coût attendu et le départage lexical favorise la fusion. Le gain de sept appels sur le plan intégral est correct. Le gain face à l'autre ordre est RÉFUTÉ sur ce jeu. [Script et résultat](prism/audit_pr29_controls.py).

## Prototype et mesures

Le [protocole v0.1](EXPERIMENT_PROVENANCE_PREREG_V0_1.md) et les empreintes des entrées ont été publiés au commit [7fbf085](https://github.com/Abrasax63/Omega-pub/commit/7fbf08584106da4cac48bf6388ee2cd5f566e721) avant le premier rejeu comparatif. Le [filtre](prism/provenance_policy.py) réutilise `optimize_policy` avec des hypothèses révisées. Il contrôle l'origine, l'URL, le champ, la version et la date de référence fournis par l'adaptateur, exige au moins une pièce primaire et la corroboration configurée, journalise les conflits et recalcule le risque conditionnel exact. La confiance est celle du modèle fini, sans prétention de calibration probabiliste externe. L'authenticité et l'indépendance des reçus dépendent du système de collecte. Les dates de référence des fixtures ne sont pas des horodatages certifiés. L'adaptateur n'écrit ni dans le RCE ni dans son registre.

| Bras déterministe | Correctes | Erreurs confiantes | Abstentions justifiées | Décisions manquées | Score / 12 | Consultations | Médiane locale, µs |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| A Réponse stipulée | 6 | 5 | 1 | 0 | 7 | 0 | 0,4 |
| B Ordre fixe et filtre | 8 | 0 | 3 | 1 | 11 | 21 | 31,4 |
| C Omega actuel | 6 | 6 | 0 | 0 | 6 | 15 | 95,1 |
| D Omega et filtre | 8 | 0 | 3 | 1 | 11 | 21 | 143,0 |
| E Horizon 1 et filtre | 5 | 0 | 3 | 4 | 8 | 15 | 82,2 |

Les 60 trajectoires et les mesures brutes sont dans le [journal JSONL](prism/provenance_cases/trace_v0_1.jsonl). Ces durées d'un rejeu séquentiel en mémoire sont EMPIRIQUES. Les verdicts et consultations sont des CALCULS EXACTS sur le corpus stipulé. Aucun appel à un modèle ni à une source distante pendant le rejeu. La lecture manuelle de sources lors de la constitution du corpus n'est pas une consultation facturée à un bras. Les comparaisons LLM avec réponse directe, équipes fixes et sessions isolées restent non exécutées. Aucun jugement de qualité de preuve rédigée ou de coût en tokens n'est disponible. Les corrigés publics sont lus par le scoreur après les décisions.

D élimine les six erreurs confiantes de C. M1 et T1 sont corrigés grâce au rejet suivi d'une nouvelle consultation. F2, D4 et D5 restent indéterminés et sont signalés. P1 passe d'une fausse certitude à une abstention sur une question décidable. D et E divergent uniquement sur D1–D3, trois variantes d'un XOR construit pour exiger deux vérifications complémentaires. B résout ces variantes au même coût que D. L'horizon variable montre donc un effet contre l'horizon 1 sur cette strate, avec aucun avantage contre B sur le corpus complet.

**Divergence publique supplémentaire T3.** La page MDN consacrée au 308 affirme, à propos du 301, que la méthode doit rester inchangée. La RFC 9110 §15.4.2 autorise explicitement POST vers GET, ce que confirme la page MDN dédiée au 301. Le cas a été gelé [au commit e3f2a85](https://github.com/Abrasax63/Omega-pub/commit/e3f2a85bd0bb8bc8c1f42e67175ba7648195ca52) avant son propre rejeu et n'entre pas dans le tableau. D/B/E détectent le conflit et s'abstiennent, alors que la norme demandée permet de trancher. A et C répondent à tort. La provenance résout un conflit de version T1, mais le filtre v0.1 ne résout pas un conflit d'autorité T3. [RFC 9110 §15.4.2](https://www.rfc-editor.org/rfc/rfc9110#section-15.4.2) · [MDN 308](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Status/308) · [MDN 301](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Status/301) · [trace T3](prism/provenance_cases/supplement_t3_result.json).

## Prochaine architecture et tests de réfutation

Conserver le planificateur et placer la vérification entre l'observation et la mise à jour des hypothèses. Le [contrat RCE](CONTRAT_CONTEXT_ENGINE.md) fournit les dépendances explicites, le [modèle de provenance](MODELE_PROVENANCE.md) distingue les dimensions d'indépendance et le [contrat mémoire](CONTRAT_MEMOIRE.md) fixe l'isolation des résultats. Réutiliser la passerelle de lecture et les manifestes d'exécution. L'adaptateur de collecte doit établir l'URL finale, le localisateur, la version, la date de collecte, le digest du document et ses racines de dépendance hors du texte extrait. Pour une question visant une norme précise, tester l'arbitrage par cette norme après vérification de sa portée. Quand la question vise un fait empirique, conserver une abstention en présence d'un désaccord recevable et non arbitrable.

| Mécanisme | Test discriminant ou limite établie |
| --- | --- |
| Représentation | Comparer tables de mondes, règles de court-circuit et preuves symboliques sur les mêmes tâches. Rejeter l'adaptation si elle ne réduit ni les erreurs ni les coûts face à la meilleure représentation fixe. Ici, le contre-test de #29 favorise une règle de court-circuit. |
| Hypothèses fragiles | Retirer ou permuter les métadonnées de provenance et injecter une valeur fausse avec un reçu cohérent. Mesurer erreur et abstention contre une priorité primaire fixe. P1 montre la limite du contrôle d'origine. |
| Contre-exemples | Comparer recherche prioritaire de réfutation et vérification primaire d'abord avec les mêmes consultations. Le gain doit subsister sur des cas où la tentative de réfutation coûte un appel sans effet. M1 est un exemple construit, pas cette expérience indépendante. |
| Budget dynamique | Comparer D au meilleur ordre fixe et aux deux ordres conditionnels de #29 sur tâches nouvelles. Sur v0.1, D ne bat pas B et coûte plus que C. |
| Révision | Comparer rejet sans replanification, replanification et arbitrage normatif. T1 et T3 distinguent rejet de portée et conflit d'autorité. |
| Mémoire | Ablation avec un instantané antérieur, mêmes budgets et contrôle des réponses ou dérivés déjà présents. Écarter toute tâche dont la solution est récupérable en mémoire. Aucun effet mémoire mesuré ici. |
| Arrêt | Opposer valeur à horizon variable à un arrêt sur suffisance de preuve et à une politique de court-circuit. Inclure contrôles inutiles, synergies et corroborations coûteuses. M2 vérifie l'arrêt à zéro contrôle. |

La priorité est de comparer **filtre de provenance + règle forte** à **filtre de provenance + planificateur** sur un lot externe caché, en factorisant la présence du filtre et la politique d'arrêt. Figer le lot et les règles d'arbitrage avant exécution, séparer génération et notation, et pré-enregistrer les sources de coûts et la pénalité d'abstention. Le verrou principal est de montrer un bénéfice du planificateur après contrôle de la qualité des observations, avec des hypothèses construites sans accès aux réponses.

## Reproduction

Depuis `09_INFRASTRUCTURE_AGENTIQUE/prism` sur la branche de l'expérience :

```sh
python -m unittest -v
python equal_budget_pilot.py
python p5_multidomain_adversarial.py
python audit_pr29_controls.py
python provenance_benchmark.py
python provenance_benchmark.py --supplement
(cd provenance_cases && sha256sum -c SHA256SUMS)
```

Les neuf nouveaux tests couvrent les empreintes, le rejeu #29, le conflit documentaire réel, la révision, le budget, l'invariance, le doublon, l'indisponibilité et des contre-vérifications exactes. Le journal local couvre 87 tests du sous-ensemble récupéré et les journaux GitHub attestent les suites historiques au SHA de base.
