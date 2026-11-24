# Jalon 050 — Tester chaque interface avant de faire coopérer les modules

24 novembre 2026, 23 h 55 CET. Les 49 journaux numérotés précédents sont présents au SHA dee7e73674870e1d8fd3bc7cf0d5588d14d627ee. Le présent commit ajoute la fiche [050](050.md), avec un résultat exécuté. Les dix fiches depuis le [jalon 040](BILAN_040.md) relatent des expériences.

- [041](041.md) et [042](042.md) ont exécuté une voie modèle. Leurs critères d'adoption ont échoué. L'oracle exact reste la voie de référence quand l'entrée le permet.
- [043](043.md) à [045](045.md) ont réduit des erreurs de routage et de vérification sur des fixtures. En [044](044.md) les faux positifs passent de 6 à 0 sur douze propositions simulées. [045](045.md) augmente la couverture des requêtes claires de 2/10 à 8/10, avec les six refus attendus.
- [046](046.md) isole le solveur et son contrat. [047](047.md) le raccorde au routeur. [048](048.md) porte les verdicts conformes de 4/12 à 12/12 en testant le domaine réel de la table. [049](049.md) valide les 16 cas de renommage et la panne explicite.
- [050](050.md) transfère après redémarrage une décision de cache qui évite 901 calculs. Le gain de bout en bout manque le seuil prescrit face au moteur fixe, et la variante sans politique reste plus rapide. La politique reste un résultat expérimental rejeté.

Le progrès mesuré porte sur les contrats, les vérificateurs et certaines entrées couvertes. Tester le seuil de rentabilité par taux de répétition avant d'évaluer un nouvel agencement de modules. Les expériences logicielles ne confèrent aucune preuve d'acquisition de compétence neuronale.
