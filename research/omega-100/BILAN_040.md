# Bilan du jalon 040

19 novembre 2026. Journaux 001 à 040 présents dans le programme, dont dix nouvelles expériences depuis le [jalon 030](BILAN_030.md).

- [031](031.md) à [036](036.md) ont évalué le raccord source–assertion–oracle et les contrôles de contrat. Les expériences montrent notamment 8 → 12 statuts conformes sur 12 en [032](032.md), 6 → 0 faux passages en [033](033.md), puis 32 → 0 contrats mal typés atteignant l'oracle en [035](035.md). Ces chiffres concernent les fixtures respectives.
- [037](037.md) arrête 4/4 réponses JSON ambiguës et conserve 96/96 entrées valides. [038](038.md) réfute le seuil de coût uniforme pour le seul décodage. [039](039.md) mesure un surcoût positif maximal de 1,57 % avec le traitement des documents inclus, à taille de réponse JSON constante.
- [040](040.md) exécute huit inférences réelles. Le 3B améliore les comptes bruts face aux trois premières lignes, de 3 → 4 vrais positifs et 21 → 11 faux positifs, mais échoue sur les deux abstentions attendues. Les preuves à ce stade soutiennent les contrôles déterministes du lecteur. L'adoption du sélecteur autonome exige une nouvelle évaluation.

Priorité : vérifier le rôle du modèle comme proposeur de lignes, avec une décision exacte indépendante dès que la tâche le permet. Reprendre aussi le test de taille du JSON proposé en 039 lors d'une expérience dédiée.
