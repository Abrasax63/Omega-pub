# P5-OBS-02 — Pré-enregistrement : fiabilité des preuves, causes communes et décision robuste

**12 novembre 2026. Ce protocole est fixé avant l'implémentation OBS-02 et le calcul de ses résultats.**

## Verrou scientifique

P5-OBS-01 [PR #57](https://github.com/Abrasax63/Omega-pub/pull/57) a confirmé l'intérêt du filtrage des micro-états compatibles et des informations complémentaires mais a seulement testé des sondes parfaites et une cible XOR synthétique. Tester désormais **le risque de fausse certitude quand deux vérifications partagent une même erreur**, et distinguer l'absence de preuve, la preuve erronée et l'incompatibilité logique de témoignages. Le critère est la qualité de la **décision finale**, pas seulement l'entropie réduite.

### Références externes

- [Norman, Parker & Zou (2017), *Verification and control of partially observable probabilistic systems*](https://doi.org/10.1007/S11241-017-9269-4).
- [*From Reactive to Active Sensing: A Survey on Information Gathering in Decision-theoretic Planning* (2023)](https://doi.org/10.1145/3583068).
- [Tucker et al. (2023), *Bandits with costly reward observations*](https://proceedings.mlr.press/v216/tucker23a.html).
- Source interne : [recollement par ensembles de survivants](../02_MATHEMATIQUES/defauts_recollement/sources/DELTA_H_RECOLLEMENT_INTERNE_2026-09-29.md) et [limite des invariants de présentation en cadre contrôlé](../02_MATHEMATIQUES/defauts_recollement/sources/DELTA_H_STRATEGIE_COUVERTURE_2026-09-29.md). **Aucune revendication de théorème nouveau ni d'avantage Omega préexistant.**

## Données réelles de modèle, sans nouvelle inférence

**Source figée** : reprendre l'archive publique de P5-ACTIVE-01 (96 inférences réelles binaires Qwen), [GitHub run 43214660818, artefact 13943231674](https://github.com/Abrasax63/Omega-pub/actions/runs/43214660818/artifacts/13943231674). Réviser ni les scores ni les étiquettes de cet essai. Utiliser les **32 réponses de calibration** (8 par famille) pour estimer `p(correct|famille)=(success+1)/(8+2)`, puis rejouer **64 réponses de test** effectivement produites par Qwen. Le contrôleur n'accède pas à la vérité non vérifiée. L'archive ayant déjà été analysée, cette campagne est **strictement une analyse exploratoire postérieure**, **pas un holdout neuf ni indépendant**.

## Modèle des vérificateurs imparfaits (artificiel et explicitement déclaré)

État microscopique `X=(C,Z,D,M)∈{0,1}⁴` : `C=1` si la réponse du modèle est correcte ; `Z=1` signale une erreur partagée ; `D=1` une erreur indépendante ; `M=1` une non-résolution. Probabilités a priori **connues des baselines** : `P(C=1)` dépend uniquement des 8 calibrations par famille ; `P(Z=1)=P(D=1)=P(M=1)=1/4`, variables indépendantes. **C est la vérité réelle dans le jeu Qwen ; Z,D,M sont simulées**, déterministes par SHA-256 de `P5OBS02|question_id|variable`, avec bit 1 si modulo 4 = 0. Ces faux bruits ne sont pas des erreurs observées chez de vrais fournisseurs.

Quatre outils, une réponse `C=0/1` ou `UNKNOWN` :
- `SHARED_A` (coût 0,04) renvoie `C XOR Z`.
- `SHARED_B` (coût 0,03) renvoie **exactement le même bit `C XOR Z`** : les deux témoignages ont la **même cause d'erreur**, ils ne constituent jamais deux preuves indépendantes.
- `INDEPENDENT` (coût 0,08) renvoie `UNKNOWN` si `M=1`, sinon `C XOR D`.
- `GOLD` (coût 0,80) est un contrôle exact, qui dévoile `C`.

Les coûts sont des **unités d'utilité conventionnelles**, pas des factures. Budget **2 outils distincts au plus par réponse**. Une décision finale choisit d'accepter la réponse du modèle, de publier la réponse binaire opposée ou de s'abstenir. Score : +1 juste, −2 faux, +0,05 abstention, moins coût cumulé des vérifications.

Les politiques connaissent les coûts et les caractéristiques publiées des outils. Elles ne connaissent **ni** les valeurs cachées `C,Z,D,M` du cas courant, **ni** les issues des outils non appelés. Le calculateur final seul dispose de `C`; l'outil GOLD ne le communique qu'après paiement. La projection `π_a` dépend des interventions ; il s'agit d'un **modèle probabiliste contrôlé**, non de la réutilisation sans hypothèses des théorèmes sur `Δ_h` autonome.

## Politiques (toutes pré-définies)

1. `no_probe` : décision fondée sur la calibration seulement.
2. `fixed_shared_pair_correct` : acheter SHARED_B puis SHARED_A, **connaître leur dépendance commune** et donc ne pas sur-interpréter le doublon ; contrôle d'achat inutile.
3. `fixed_shared_pair_naive` : mêmes actions et coûts, mais supposer **à tort l'indépendance** des deux sorties, pour tester la surconfiance du recollement erroné.
4. `fixed_shared_independent` : SHARED_B puis INDEPENDENT ; **contrôle fort simple** qui connaît les outils pertinents.
5. `myopic_voi` : choisir la vérification qui maximise la valeur de la décision **à un seul pas** moins le coût, et répéter tant qu'un gain strictement positif existe.
6. `entropy_micro` : maximiser gloutonnement l'information sur **tout l'état (C,Z,D,M)**, sans regarder le gain terminal; payer deux sondes au maximum.
7. `exact_bayes_dp` : programmation dynamique bayésienne exhaustive sur la distribution exacte des 16 états cachés, avec coûts et budget.
8. `omega_provenance_candidate` : **même DP exact**, avec certificat append-only `support compatible, probabilités C, action, origine des mesures, contradiction le cas échéant`. Appel à P1 uniquement pour expliquer l'incertitude, non pour exécuter des agents indépendants. Le résultat **DOIT égaler** le DP classique : aucune nouveauté algorithmique ne sera revendiquée.

Ordre de préférence des sondes en cas d'égalité : SHARED_B, SHARED_A, INDEPENDENT, GOLD. Egalité entre STOP et une action : **STOP**. En cas d'égalité des réponses finales : abstention, accepter, inverser.

## Validations obligatoires

- Deux calculateurs exacts **indépendants** : Bellman récursif sur croyances de fractions et énumération exhaustive de politiques contingentes à horizon 2 pour chaque a priori de domaine (quatre calculs). Ils doivent donner **la même valeur rationnelle**, sans flottants.
- Les deux copies partagées rendent des sorties **parfaitement corrélées** et leur seconde observation n'apporte **aucun gain sur C**, mais coûte 0,04 ou 0,03. **Une contradiction entre les deux copies est impossible**, le filtre doit alors refuser le chemin avec un certificat de réalisabilité vide (analogue au recollement impossible).
- Après une observation bruyante, **les deux valeurs de C peuvent encore être possibles** : ne jamais confondre probabilité élevée avec preuve de correction.
- Cas `UNKNOWN` de la sonde indépendante : posterior inchangé (conditionnel à sa non-résolution indépendante de C) ; coût néanmoins payé.
- Ne jamais divulguer `C,Z,D,M` à une fonction de décision ni offrir une réponse d'un outil non appelé.
- Test du « modèle nul » (zéro bruit, coût zéro et confirmation de C) : le contrôle exact n'a pas de raison d'acheter une seconde preuve, sans surcoût.
- Présenter la valeur espérée bayésienne **séparément** de l'utilité réalisée sur les 64 erreurs Qwen et bruits pseudo-aléatoires : le modèle n'est pas nécessairement calibré sur les observations réalisées.
- Comparer les décisions, la fréquence des fausses publications et des abstentions, les coûts, le volume des `UNKNOWN`, les doubles comptes de preuve et la différence aux témoins simples.

**Falsification :** aucun avantage propre à Omega si égal au DP classique (égalité obligatoire par construction), même si meilleure performance que les heuristiques. Une absence de gain sur le replay doit être publiée. Ce pilote ne peut **pas** démontrer l'efficacité sur de vrais vérificateurs faillibles, faute de journaux authentiques de leurs erreurs.

## Exécution et gouvernance

Résultat validé seulement si tests et double chemin exact réussis dans GitHub Actions Python 3.12 gratuit, sans inférence de modèle ni API. Statut `EXACT_NOISY_PROVENANCE_WITH_REAL_MODEL_OUTPUTS_SYNTHETIC_TOOL_FAULTS` ; conserver l'archive brute et ses empreintes. PR DRAFT, `main` et les anciennes PR inchangées. Ne pas promouvoir la candidate dans la bibliothèque CORE.
