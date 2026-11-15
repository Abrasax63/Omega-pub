# Amendement avant première CI — politique de cache (2026-11-15)

**Aucun résultat OBS-COL-09B n'a encore été exécuté lorsque cet amendement est enregistré.**

Le banc AALpy encapsule normalement le système sous test dans un `CacheSUL` ; le programme TTT Java hérité n'a pas de cache équivalent partagé. Pour ne pas comparer la somme des **resets physiques** de deux couches qui réutilisent différemment des réponses, nous neutralisons **le cache extérieur AALpy** via `cache_and_non_det_check=False` pour les trois algorithmes et L#+P1. Les caches *internes* propres aux algorithmes restent autorisés et font partie de chaque méthode.

L'absence de cache extérieur n'impose pas le même ensemble de requêtes entre algorithmes : seul le **même manifeste de tests d'équivalence** est garanti. Les coûts couvrent, à chaque fois, les actions/restarts physiques réellement effectués, y compris les contrôles EQ.

Si cette option provoque une incompatibilité avec la bibliothèque originale, marquer échec et reconsidérer explicitement le protocole ; ne pas éditer silencieusement les règles en fonction d'un score. Le cas L# vs L#+P1 doit rester strictement identique en requêtes, même si le coût CPU de P1 augmente.

Les séquences d'évaluation finales restent réservées jusqu'à la fin des apprentissages.
