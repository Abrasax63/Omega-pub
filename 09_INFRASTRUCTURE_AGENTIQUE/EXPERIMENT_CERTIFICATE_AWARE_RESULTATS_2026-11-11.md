# OMEGA-CERT-001 — résultats contrôlés de l'objectif de certification

**11 novembre 2026. Statut CALCUL EXACT SUR CALIBRATION CONSTRUITE, NON AVEUGLE.**

## Pré-enregistrement et gel

- Données **48 cas nouveaux** (24 entraînement + 24 test) gelées dans `prism/certification_cases_v01.json` au commit [c395e0e](https://github.com/Abrasax63/Omega-pub/commit/c395e0e065f345a0d083e383c13e6fac8077ad60), avant le nouveau code et ses exécutions. Les paramètres des sept sous-types sont distincts de tous ceux de STRAT-002, même si les gabarits et méthodes sont apparentés.
- Récompense, pénalités, budgets, arrêts et baselines fixés au commit [bb36071](https://github.com/Abrasax63/Omega-pub/commit/bb360711d8790706f55abf28bcb3db3b0eeb43f1) avant toute mesure.
- Pannes de méthode : **14 pannes artificielles** déclarées dans l'instantané ; les politiques ne lisent pas le champ d'indisponibilité du cas cible avant l'exécution. Quatre méthodes sont exécutées en code Python réel (`formal`, `compute`, `refute`, `source`), le dernier étant un **instantané de règle documentaire locale**, et non une requête réseau.
- Les contrôles de vérité sont séparés lorsque possible : congruence via `k=0/k=1` vs coefficients multiples, existence d'un circuit eulérien via DFS sur les arêtes vs critère degrés/connexité, et fractions vs produits croisés. **48 cas × 4 méthodes = 192 vérifications d'invariant**, pas 192 expériences humaines indépendantes.
- La source primaire pour le prédicat documentaire `header` est [RFC 9110 §13.1.3](https://www.rfc-editor.org/rfc/rfc9110#section-13.1.3), qui exige l'ignorance d'`If-Modified-Since` si `If-None-Match` est présent et limite l'évaluation de l'en-tête à GET/HEAD. Le cas est défini sous hypothèses de date HTTP valide et date de modification disponible ; le corpus ne prétend pas modéliser tout HTTP.

## Comparaison principale à coût et information égaux

Deux essais maximum par cas, succès certifié +1, erreur -5 à la notation, abstention 0, coût de chaque essai 1/20 dans l'objectif expérimental.

| Bras | Correctes sur 24 | Abstentions | Erreurs | Essais facturés | Score conventionnel |
|---|---:|---:|---:|---:|---:|
| A : ordre fixe global appris | 19 | 5 | 0 | 36 | 17,2 |
| B : meilleur ordre fixe par sous-type appris | **22** | 2 | 0 | **26** | **20,7** |
| C : nouvel Omega `certificate_coverage_DP` | **22** | 2 | 0 | **26** | **20,7** |
| D : repli conditionnel fort, indépendamment énuméré | **22** | 2 | 0 | **26** | **20,7** |
| E : Omega original `optimize_policy` | 18 | 6 | 0 | 24 | 16,8 |

Les `26` essais sont des **exécutions de procédures locales** en rejeu et des coûts unitaires normalisés, pas des requêtes vers GitHub, des tokens ou un coût monétaire réel. Le critère de score `correct - 5*wrong - (calls/20)` est une convention ; ne pas le présenter comme une utilité humaine mesurée.

**Verdict local :** le critère « produire un certificat » donne quatre conclusions supplémentaires comparé au solveur bayésien original, avec deux essais supplémentaires. La comparaison appariée établit exactement **5 cas récupérés / 1 cas perdu**, d'où +4 net. Mais **C, B et D rendent exactement la même décision et utilisent exactement les mêmes méthodes sur chacun des 24 cas de test**, pas seulement le même score final. Le bénéfice est donc attribuable à l'orientation vers la preuve, **pas à une supériorité spécifique du planificateur dynamique**.

Une version indépendante du sélecteur D énumère la meilleure première action et les meilleures secondes actions conditionnelles à l'échec. Elle donne, pour chaque sous-type de l'entraînement, le même objectif exact que le programme dynamique C. Cette double voie contrôle le calcul, mais les deux utilisent les mêmes observations construites et ne constituent pas deux correcteurs humains indépendants.

## Les deux abstentions qui subsistent

1. **`CERT-DOCUMENTATION-header-07`** : la source normative locale est artificiellement déclarée indisponible et les trois autres procédures ne peuvent pas conclure selon le contrat. **Aucun certificat disponible** parmi ces quatre procédures ; abstention justifiée dans ce cadre.
2. **`CERT-MATH-euler-04`** : circuit eulérien positif sur un cycle à six sommets ; `formal` est indisponible, `refute` ne peut pas établir l'existence. La stratégie C/B/D essaie `formal` puis `refute`, donc s'abstient. En revanche, **`compute` peut construire le circuit et conclure correctement**. Il reste une insuffisance de sélection de méthode après un échec.

### Plafond rétrospectif — non admissible comme bras causal

Après consultation des 24 cas test, le meilleur ordre fixe **choisi a posteriori** par sous-type donne **23/24 en 26 essais** : le sous-type Euler gagne à tester `compute` avant `formal` sur cette cohorte. Ce chiffre constitue un diagnostic ou une borne empirique *avec accès aux résultats du test*, **pas une victoire de stratégie prospective**.

La borne mécanique maximale du portefeuille de quatre méthodes est également de **23/24** : un cas ne dispose d'aucune méthode concluante. La stratégie C atteint 22/23 cas certifiables, contre 18/23 pour l'ancien Omega, sans pouvoir raisonnablement inférer une probabilité de généralisation de cet échantillon.

## CI réellement vérifiée

[GitHub Actions 43056420728](https://github.com/Abrasax63/Omega-pub/actions/runs/43056420728) — **SUCCESS**, 166 tests du Prisme.

[GitHub Actions 43056749786](https://github.com/Abrasax63/Omega-pub/actions/runs/43056749786) — **SUCCESS**, **168 tests du Prisme**, dont deux contre-tests et l'audit des cas appariés. Les suites d'intégration RCE/MCP et de cohérence des index réussissent également.

Réplication depuis `09_INFRASTRUCTURE_AGENTIQUE/prism` :

```bash
python certificate_aware_selector_v01.py
python certification_failure_audit_v01.py
python -m unittest -v test_certificate_aware_selector_v01 test_certification_failure_audit_v01
```

Les traces complètes sont reproductibles par le script. Les mécanismes existants `action_planning_two_step.optimize_policy` et le routeur général sont conservés sans réécriture.

## Limites de validité

1. Corpus **entièrement construit**, paramètres nouveaux mais gabarits proches de STRAT-002 ; il n'est **ni indépendant des concepteurs, ni aveugle**. Les générateurs et règles de correction sont publics. 
2. Quatre programmes déterministes, pas quatre modèles de langage ; aucun agent externe, aucun multi-agent autonome, aucun token ni coût externe mesuré.
3. Les pannes sont **injectées**, pas des erreurs de fournisseurs observées. Des « certificats » algorithmiques et une règle RFC locale ne remplacent pas une validation formelle automatisée des preuves ni une signature de provenance du contenu brut.
4. Tous les bras connaissent le sous-type, ont accès aux mêmes quatre méthodes et à la même partition d'apprentissage. `E_original` utilise aussi les étiquettes de vérité des cas d'apprentissage pour reproduire l'objectif bayésien ; C/B/D n'en ont pas besoin.
5. Les méthodes sont conçues pour conclure correctement ou s'abstenir sur les cas retenus, ce qui produit zéro erreur factuelle. Cela n'établit aucune résistance à des faux certificats ou à des preuves contradictoires.
6. L'équivalence appariée C/B/D n'est pas une preuve qu'un modèle adaptatif ne pourra jamais surpasser une règle fixe **dans d'autres structures**. Dans cette structure particulière (deux essais, réponses terminales yes/no, échec non concluant, coût uniforme), une stratégie fixe conditionnelle très forte suffit à rejoindre le DP sur les données.

## Suite scientifique prioritaire

Ne pas « ajuster » les 24 cas test. Concevoir une nouvelle expérience indépendante avec **plusieurs observations intermédiaires informatives et non terminales** : résultat de calcul partiel, incompatibilité de provenance, contrainte logique révélée, ou contre-exemple qui élimine seulement certaines hypothèses. Le choix de méthode suivant doit véritablement dépendre du *contenu* du résultat, pas seulement du fait qu'une tentative a échoué.

Prédéclarer une référence forte autorisée à exploiter les mêmes retours intermédiaires et à changer de stratégie, plus une baseline à politique fixe exhaustive. Ajouter une vérification de la validité des certificats non triviale et un contrôle de provenance externe. Le seuil de preuve d'un avantage stratégique est un bénéfice sur ce nouveau lot **après** comparaison avec la référence adaptative forte et coût égal.

**Ne pas fusionner `main`, écrire dans SQLite ou promouvoir en CORE à ce stade.**
