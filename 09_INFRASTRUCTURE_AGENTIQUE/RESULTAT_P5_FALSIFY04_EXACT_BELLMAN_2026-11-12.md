# Résultat P5-FALSIFY-04 — vérificateurs imparfaits sous coût : égalité avec Bellman

**Statut : CALCUL EXACT SYNTHÉTIQUE / AUCUN GAIN PROPRE À OMEGA.** 12 novembre 2026.

## Chaîne de provenance
- Pré-enregistrement figé **avant** écriture du calcul : commit `4f1feef5372d61e27c1835fef8d3aaec8e8faea8`, fichier `EXPERIMENT_P5_FALSIFY04_COSTLY_VERIFIERS_PREREG_2026-11-12.md`.
- Programme : `prism/p5_falsify04_imperfect_verifier_dp.py`.
- Vérifications séparées : `prism/test_p5_falsify04_imperfect_verifier_dp.py`, quatre tests unitaires exécutés et réussis en session Python locale. Le second chemin énumère directement les vérités latentes et observations, au lieu d'intégrer uniquement par les croyances de Bellman.
- Workflow CPU GitHub Actions : `.github/workflows/omega-p5-falsify04-imperfect-verifier.yml` ; archive JSON publiée si la CI est exécutée et réussit. **Un calcul local réussi ne vaut pas confirmation automatique de CI.**

## Hypothèses (artificielles, PAS des mesures sur de vrais vérificateurs)
Y et R binaires équiprobables, modèle initial correct 2/3, indice historique H correct sur R dans 3/4 des cas, trois outils A/B/C conditionnellement indépendants. A et B : exactitude respectivement 90%/55% ou 55%/90% selon R, coût 0,06 ; C exactitude 80%, coût 0,13 ; deux appels maximum. Gains : +1 réponse juste, -2 réponse fausse, +0,05 abstention, moins les coûts. Toutes les politiques disposent du même M et H et connaissent les mêmes lois.

## Résultat exact (moyenne sur les quatre contextes M,H)
| Politique | Utilité espérée (par problème) | Coût moyen | Appels moyens | Réponses correctes prob. | Erreurs prob. | Abstention prob. |
|---|---:|---:|---:|---:|---:|---:|
| Sans vérification (optimisé) | 0,05000000 | 0 | 0 | 0 | 0 | 1 |
| Fixe A puis C | 0,34672917 | 0,19000000 | 2 | 0,73083333 | 0,10125000 | 0,16791667 |
| Heuristique « Omega-like » | **0,47958333** | 0,11145833 | 1,39583333 | 0,75833333 | 0,08750000 | 0,15416667 |
| **Bellman classique exact** | **0,47958333** | 0,11145833 | 1,39583333 | 0,75833333 | 0,08750000 | 0,15416667 |

L'utilité de Bellman et du candidat coïncide exactement : **1151/2400**. Les quatre contextes prennent le même premier achat (A si H=0, B si H=1). Le bénéfice par rapport à la règle fixe ne constitue pas une valeur ajoutée Omega : un contrôle classique fort effectue les mêmes choix.

## Démonstration du plafond
En notant b la croyance jointe sur (Y,R), `V(b,S,k)` optimise parmi arrêt et tests non achetés :
`V(b,S,k) = max(terminal(b), max[t in S](-cout(t)+sum_z P(z|b,t) * V(update(b,t,z),S\\{t},k-1)))`.
La récurrence inspecte tous les tests et toutes les observations admissibles (k≤2). Une politique candidate avec les mêmes b,S,k est donc incluse dans l'ensemble maximisé : **son gain espéré ne peut être supérieur à V**. Les fractions rationnelles évitent les effets d'arrondi.

## Portée et blocage
Ce résultat apporte un **test de correction de la conception des comparateurs**, pas un nouveau benchmark d'intelligence. Les erreurs des vérificateurs et l'indice historique sont simulés, les probabilités sont connues, aucune inférence LLM n'est appelée, aucun oracle humain indépendant ne réévalue les énoncés. La politique expérimentale dite « Omega-like » ne passe pas par le vrai planificateur P1, la mémoire P2, ni P3 ; elle ne démontre donc aucune aptitude du système Omega en service.

Le prochain vrai verrou n'est pas d'ajouter des agents : disposer de **preuves externes imparfaites observées**, mesurer coûts et dérive sur des tâches nouvelles, puis comparer l'implémentation **réelle** d'Omega avec Bayes stationnaire, Bayes décoté, le meilleur optimiseur calculable sous même budget, et les ablations mémoire/observabilité. L'indice H ou les données historiques doivent être mis à disposition des comparateurs également ; sinon le test mesure une asymétrie d'information, non une meilleure stratégie.

**Verdict : pas de plus-value propre démontrée. Ne rien fusionner dans main ni promouvoir CORE.**
