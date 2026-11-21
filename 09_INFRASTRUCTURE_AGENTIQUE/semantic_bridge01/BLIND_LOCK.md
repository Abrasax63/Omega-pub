# Verrou aveugle avant premier accès aux nouvelles sources

- **SHA Git du moteur et du banc** après correction technique hors échantillon : `fcb3a1c0ab5a8521923618d112db17185a4068d4`.
- **Validation indépendante préalable** : [GitHub Actions #44879721676](https://github.com/Abrasax63/Omega-pub/actions/runs/44879721676), tous les tests de développement et de protocole réussis. Ces tests n'utilisent que huit anciens exemples connus et des entrées entièrement synthétiques.
- Manifest et questions fixés dès `328a220285e7028551356a177540a7d4bfb496f1` ; hypothèses et critères fixés dès `db63e9b43ca70f62a23bc8efcc1b1f3a1216c6a6`.
- **Aucun fichier du holdout** (indices 12,18,35,56,78,100,142,182,23,43,153,263) n'a encore été ouvert ou utilisé pour modifier le vocabulaire, les seuils ou les règles.
- À partir de maintenant, aucune modification des règles `structural_bridge.py`, des seuils, des identifiants ou des labels ne sera admise dans le verdict aveugle. Les correctifs d'infrastructure éventuels seront documentés sans retoucher le moteur.
- Les octets des fichiers pourront être récupérés pour calculer et figer leurs empreintes **maintenant seulement**, puis évalués sans sélection ni substitution. Ce corpus n'est pas un holdout des poids Qwen, seulement des essais d'Omega.
