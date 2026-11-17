# OMEGA-COST-TO-GO-04 — apprentissage du coût restant

**Objectif :** tester si apprendre le coût *total d'un épisode encore à terminer* permet à Omega de choisir de meilleures requêtes que les récompenses immédiates.

Le [préenregistrement daté](PREREG_2026-11-17.md) est le premier commit de la branche (`df94bba543d5e661005efcb892935dab1ecf6d89`), antérieur au code et aux résultats.

La [PR #159](https://github.com/Abrasax63/Omega-pub/pull/159) a démontré un contexte de décision exploitable mais **pas** de gain de son apprentissage contextuel par rapport à PRICE_AWARE. Ici, trois stratégies entraînables comparent :

- IMMEDIATE_CONTEXTUAL : moyenne des récompenses immédiates, **même principe que #159**, réentraînée sur les nouveaux mondes.
- RETURN_GLOBAL : moyenne de coûts réellement observés **du moment de la décision jusqu'à l'identification** ; optimisée globalement.
- RETURN_CONTEXTUAL : même cible, mais quatre cases selon le tarif et l'incertitude du posterior.

BALANCED et **PRICE_AWARE** sont conservées comme références déterministes. Toutes les méthodes voient les **mêmes 24 machines de TEST**, chacune parmi 16 candidates et jusqu'à 12 sondes payées de 10 bits. Il ne s'agit pas d'un réentraînement de poids d'un modèle de langage, ni d'une recherche réelle de démonstrations.

## Ce qui distingue les retours de la récompense immédiate

Après un épisode d'entraînement de coût total C, chaque action réellement choisie reçoit `somme(des coûts depuis cette action jusqu'à l'épisode terminé)`. Si l'identification échoue, une pénalité de 150 unités est ajoutée. Le bandit minimise la moyenne de ses coûts restants constatés ; aucun coût contrefactuel n'est fourni pour une action non exécutée. Aucun signal d'évaluation ne modifie le bandit.

Les nouvelles cohortes excluent les modèles présents dans les tests/prior studies #143, #145, #157, #158 et dans les trois pools de #159. Les deux méthodes entraînables choisissent elles-mêmes leur trajectoire : **les coûts réels de collecte peuvent différer**, même si elles voient les mêmes 48 mondes à plafond identique.

## Reproduction

Python 3.11, aucune bibliothèque externe, aucune API payante.

```bash
python -m unittest discover -s experiments/omega-cost-to-go-04 -p 'test_cost_to_go.py' -v
python experiments/omega-cost-to-go-04/cost_to_go.py --output evidence/report.json
sha256sum evidence/report.json
```

Le workflow dédié exécute **15 contrôles sur push**, sans ouvrir le TEST. La PR brouillon déclenche une unique comparaison TRAIN+HOLDOUT et un audit indépendant des journaux. Le rapport complet inclut tous les échecs et les coûts d'entraînement. Une CI verte ne démontre pas un gain sur le comparateur fort.

**État initial :** protocole et mécanisme proposés, aucune validation scientifique anticipée ; `main` et CORE inchangés, aucune fusion.
