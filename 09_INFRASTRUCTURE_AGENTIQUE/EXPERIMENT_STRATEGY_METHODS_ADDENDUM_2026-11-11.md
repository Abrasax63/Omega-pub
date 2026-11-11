# Addendum STRAT-002-A — comparateur de sous-type

Ajout AVANT la première exécution du benchmark et sans consulter ses sorties.

Un comparateur fort supplémentaire, **F**, est autorisé : il sélectionne les deux méthodes fixes par **sous-type de tâche** (`mod`, `euler`, `map`, `zip`, `ratio`, `simpson`, `rfc`) plutôt que par grand domaine, avec la même recherche exhaustive et uniquement les 16 tâches de calibration. Le sous-type est une information initiale lisible dans l'énoncé et doit être fourni **également à Omega**. Les échecs de méthode restent cachés jusqu'à l'essai.

F ne change pas le plafond de deux essais ni la règle d'abstention. Il est rapporté distinctement de la baseline B gelée. Une victoire de C contre B qui disparaît contre F n'est pas un avantage propre d'Omega. Les nombres ne sont pas connus lors de cet addendum.