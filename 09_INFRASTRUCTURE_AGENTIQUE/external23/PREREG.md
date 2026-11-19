# EXT23 — test hors distribution sur des formulations humaines indépendantes

Préenregistré le 19 novembre 2026 **avant le fichier de citations, le banc d'évaluation et les exécutions**. Branchée sur PR #207, sans modifier `main`.

## Question
Notre vérificateur de fonctions finies SEM22 prend-il en charge les textes réellement écrits par des personnes extérieures à Omega, ou abstient-il correctement lorsque leur syntaxe, leur domaine ou les quantificateurs sortent du contrat ?

## Échantillon
- Collecter **12 courts extraits** de pages externes publiques, mathématiques (questions/réponses Math Stack Exchange + une ou deux définitions de Wikimédia) ; chaque source doit avoir une URL et un fragment fidèle ainsi qu'une référence d'auteur ou d'œuvre.
- Tous les extraits et métadonnées sont **figés dans `EXTERNAL_SOURCES.json` avant le script de test**, puis l'évaluateur ne doit changer ni texte ni sources.
- C'est un **échantillon de commodité**, sélectionné par l'expérimentateur et **non un holdout aveugle, ni un jeu représentatif et ni une annotation indépendante de vérité**. L'expression « formulation humaine indépendante » signifie uniquement que les chaînes sont antérieures et écrites hors Omega.
- Le test doit comparer les extraits tels quels à l'analyseur SEM22 (source complète), et, séparément, à sa lecture d'assertion (sans modifier les mots originaux), pour diagnostiquer *mise en page/domaine* vs *langage de l'énoncé*. Le deuxième bras de lecture isole la syntaxe mais ne constitue **pas** une interprétation correcte du contexte mathématique original.
- Ne pas extraire une preuve ou vérité par recherche de mots (« injective », « surjective ») ni inférer un ensemble de départ absent. Toute hypothèse insuffisante signifie **INDÉTERMINÉ**.
- Des contrôles de cohérence avec les 168 propositions gelées de SEM22 (lecture originale inchangée) doivent empêcher une régression de la capacité existante.

## Protocole et décisions
- Pas de nouveau modèle, aucune API payante ni appel web dans le test CI ; web uniquement utilisé maintenant pour choisir et figer les sources.
- **Critère de sécurité préenregistré** : zéro verdict TRUE ou FALSE hors d'un périmètre syntaxique et mathématique complètement défini, zéro promotion/certification/Horn, zéro source non attribuée. Statuts `UNSUPPORTED_SOURCE` vs `INDETERMINATE_CLAIM` distincts.
- **Critère de couverture** : nombre d'extraits authentiques évalués avec verdict mathématique / 12 ; un résultat 0/12 est **un échec de généralisation**, même si l'abstention est correcte et les tests CI sont verts. Ne jamais le vendre comme réussite sémantique.
- La cohorte contient au moins une question sur une fonction linéaire modulo un **n numérique**, des situations en n variable, une fonction carré et un changement de domaine/codomaine pour mettre à l'épreuve les limites, sans faire semblant qu'elles sont toutes du même langage.
- Conserver les références et le texte des extraits, les SHA256 et les traces des rejets. Ne pas appeler « correction mathématique humaine » une formule simplement rédigée par un humain.
- Si le taux de couverture est insuffisant, ne pas élargir silencieusement le parseur en prenant cet échantillon comme nouveau holdout : classer les causes, proposer un **adaptateur typé minimal** puis un *autre* jeu externe non vu pour sa validation.

## Résultats attendus
Rapport JSON et Markdown, provenance source, taux d'abstention, types de causes, tests de régression. Pas de modèles réels requis pour évaluer le parseur. PR DRAFT, lecture seule, aucune modification de main, aucune certification générale.
