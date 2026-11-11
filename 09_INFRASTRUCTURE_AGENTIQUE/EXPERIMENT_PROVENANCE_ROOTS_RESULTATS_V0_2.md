# OMEGA-PROV-002 — Audit exécuté : racines de preuves et autorité normative

**11 novembre 2026 — statut : CALCUL EXACT SUR CORPUS PUBLIC / CALIBRATION, aucune certification scientifique générale.**

## État de départ et version

Base [PR #31](https://github.com/Abrasax63/Omega-pub/pull/31), branche `experiment/provenance-equal-budget-2026-11-11`, commit initial `3c36e570843f6e94896bed97f32d7df637836caf`.
Pré-enregistrement `419df0d5a3e89a65e6e4288631c2b1b3ccba61d4`, écrit avant l'implémentation.

L'adaptateur `prism/trusted_receipt_adapter.py` contrôle le rattachement du reçu au catalogue : identifiant, origine, URL, champ, version, date, racine d'indépendance et rôle primaire. Une racine de provenance ne devient donc plus « indépendante » en changeant uniquement son étiquette dans le reçu. Le code d'Omega `optimize_policy` et le moteur de la PR #31 restent inchangés. Le correctif n'est **pas** une authentification cryptographique du contenu ni une garantie contre un collecteur qui invente toutes les métadonnées.

## Vérifications réellement exécutées

CI [43041187955](https://github.com/Abrasax63/Omega-pub/actions/runs/43041187955) : **SUCCESS**, 136 tests du Prisme, dont l'audit des métriques v0.2.

CI [43041472364](https://github.com/Abrasax63/Omega-pub/actions/runs/43041472364) : **SUCCESS**, 138 tests du Prisme, y compris le nouveau contre-test contre une référence fixe privilégiant l'autorité normative. Suites RCE, MCP et index : réussies.

| Rejeu sur les douze cas de la PR #31 | B v0.1 fixe | D v0.1 Omega | B v0.2 fixe | D v0.2 Omega |
|---|---:|---:|---:|---:|
| Décisions correctes | 8 | 8 | 8 | 8 |
| Abstentions (dont 1 tâche décidable manquée) | 4 | 4 | 4 | 4 |
| Erreurs de décision | 0 | 0 | 0 | 0 |
| Consultations | 21 | 21 | 21 | 21 |

Les chiffres sont issus du `PROVENANCE_V02_CI_SUMMARY` dans les journaux GitHub Actions, calculé en rejouant le code réel à partir des mêmes données. **Aucune amélioration globale et aucun avantage d'Omega sur la règle fixe ne sont constatés sur ce corpus.** Le nombre de consultations correspond à des appels simulés dans les enregistrements, pas à 21 requêtes réseau réellement exécutées.

### Contre-test D5 : indépendance fabriquée

Sur la fixture D5, un duplicat de la même source reçoit artificiellement l'étiquette `invented-independent` :
- V0.1 fixe **et** Omega : `yes`, alors que la clé de ce cas impose une abstention faute de deux acquisitions distinctes.
- V0.2 fixe **et** Omega : abstention, avec rejet `catalog_mismatch(field=independence)`.
- Même plafond : deux consultations facturées dans les deux variantes. L'attaque est synthétique et délibérée, non un incident réseau observé.

### Contre-test T3 : divergence documentaire réelle, source normative

La page MDN de 308 affirme à propos de 301 que la méthode reste inchangée, tandis que la RFC 9110 §15.4.2 permet explicitement POST vers GET ; MDN 301 confirme cette possibilité. La question T3 demande **la règle de RFC 9110**. Une table d'autorité `rule -> ietf` est donc déclarée **avant** d'observer les valeurs, identiquement aux stratégies fixe et Omega. Sur l'annotation publique de T3 :
- V0.1 : abstention après deux consultations.
- V0.2 fixe et Omega : `yes`, deux consultations, dont une secondaire écartée.
- **Comparateur fixe fort, exploratoire et défini après audit :** consulter directement la norme identifiée dans le catalogue. Même source, même budget maximum de deux consultations, mais **une seule consultation** suffit. Le test `test_normative_first_baseline` passe dans la CI.

Ce résultat ne doit pas être intégré comme un gain pré-enregistré : il est une vérification post-hoc du coût d'une décision de source. La table d'autorité est un **privilège informationnel accordé également aux deux politiques**, et non une faculté autonome démontrée.

### Test négatif — contenu falsifié

Avec une seule prétendue source primaire dont tous les champs de provenance correspondent au catalogue, remplacer son booléen de contenu par son contraire reste indétectable : la politique peut aboutir à une certitude fausse. **Limite reconnue** : un label et une URL ne prouvent pas la fidélité du contenu ; sans liaison vérifiée du contenu brut (digest, authentification du fournisseur, chaîne de collecte) ou une preuve indépendante, la confiance n'est pas justifiée.

## Verdict

- **CALCUL EXACT** : échec de la création d'un quorum par renommage de racine, et même correction pour B et D ; aucun avantage supplémentaire de la planification adaptative.
- **CALCUL EXACT** : deux politiques avec arbitrage de portée répondent à T3 ; une référence fixe préordonnée par autorité fait mieux en coût sur ce cas.
- **ÉTABLI UNIQUEMENT PAR CONTRE-EXEMPLE CONSTRUIT** : le contrôle de métadonnées ne protège pas contre une falsification du contenu étiqueté correctement.
- **INDÉTERMINÉ** : performance sur problèmes nouveaux, capacité de reconnaître l'autorité depuis la question sans une table fournie, calibration de la confiance probabiliste, robustesse en ligne contre un collecteur compromis, gain sur modèle de langage, effet de mémoire, coût réel.
- **Aucune preuve d'avantage stratégique général d'Omega.**

## Architecture et prochains verrous

1. Rattacher la preuve brute au collecteur et non aux déclarations de la page : URL résolue, date de collecte, digest du document brut, racine de copie, signature si disponible et gestion explicite des documents évolutifs. Les champs fournis par une même source ne constituent pas des vérifications indépendantes.
2. Introduire la priorité de la source normative **dans le calcul de la valeur des actions**, et non en aval de la décision : le contre-test T3 montre qu'une simple règle d'autorité prédéclarée économise un contrôle. Tester également le cas où la source dite normative est inaccessible ou hors périmètre.
3. Pré-enregistrer un **vrai benchmark à sessions isolées** : problèmes inédits, même modèle, mêmes droits de consultation et budgets, baseline adaptative forte bénéficiant du même filtre, correction indépendante aveugle. Aucun appel de modèle ni holdout privé n'a été exécuté ici.
4. Séparer strictement le coût des consultations, la confiance étayée et les décisions finales ; ne pas conditionner une promotion scientifique aux seuls tests unitaires.

## Reproduction

Depuis `09_INFRASTRUCTURE_AGENTIQUE/prism` :

```sh
python -m unittest -v test_trusted_receipt_adapter test_provenance_roots_v02_benchmark test_normative_first_baseline
python provenance_roots_v02_benchmark.py
```

Données préexistantes : `prism/provenance_cases/`. Aucun changement `main`, SQLite ou CORE. PR en brouillon.

Sources documentaires :
- https://www.rfc-editor.org/rfc/rfc9110#section-15.4.2
- https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Status/308
- https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Status/301
