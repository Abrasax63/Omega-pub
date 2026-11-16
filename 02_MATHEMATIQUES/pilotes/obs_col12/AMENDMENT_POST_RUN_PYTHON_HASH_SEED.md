# OBS-COL-12 — Amendement post-run : reproductibilité de l'ordre des tests

Date : 16 novembre 2026, **après la réussite** des runs #43841235628 (trois vérificateurs) et #43841813740 (quatre vérificateurs).

L'inspection des journaux révèle que Wp naturel a renvoyé des mots contre-exemples différents entre ces deux exécutions Python, malgré des cibles et politiques nominalement identiques. Les causes exactes internes ne sont pas certifiées. Les choix d'ordonnancement des collections, et en particulier la graine de hachage Python, sont une explication possible.

**Sans modifier aucune règle de sélection ni aucun modèle**, le dernier run exécute tous les processus Python de la CI avec `PYTHONHASHSEED=0` pour verrouiller une source fréquente de non-déterminisme. Le premier run reste une preuve historique intacte ; la version fixée n'est pas présentée comme « pré-enregistrée avant premier résultat ».

Ne pas présumer que le seul verrou de hachage supprime tout non-déterminisme. Comparer les coûts du dernier run et, si une seconde répétition est nécessaire, rapporter les divergences plutôt qu'éditer a posteriori le classement. Il s'agit d'un garde de provenance et de reproductibilité, non d'un amélioration scientifique d'Omega.
