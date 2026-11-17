# OMEGA-REAL-MATH-SCOPE-03 — adversarial fresh paraphrases v1 (post-engine freeze)
Date : 2026-11-17. Historical original engine commit: `3fe30ea94da55d97186416cec3870bd88754a845`.

## Question de falsification
Le moteur 03 conserve-t-il ses conclusions lorsque les mêmes faits des trois fiches mathématiques sont formulés différemment, **sans changer les données de référence** ?

## Protocole
1. Figé ici avant le jeu supplémentaire : 12 questions nouvelles, 4 par source BR-R90-01 / BR-R90-02 / C4 ; mélange de valeurs en toutes lettres, synonymes, préconditions implicites, assertions fausses et hors portée. Plusieurs cas sont volontairement hors des formes reconnues par le premier programme.
2. Commit des 12 nouvelles questions avec ID de source sans réponses, puis commit séparé des verdicts/rationales manuels avant toute nouvelle implémentation.
3. **NE PAS MODIFIER `engine.py`** : seulement un script de test utilise la version actuelle, lit les questions et les passe au moteur puis évalue après prédictions à partir du corrigé.
4. Compter `SUPPORTED`, `CONTRADICTED`, `ABSTAIN` exacts, abstentions non justifiées, erreurs affirmées avec confiance. Une mauvaise conclusion affirmée doit être traitée comme anomalie sérieuse. Pour R90, contrôle numérique indépendant par les fonctions finies existantes lorsque les nombres sont explicitement identifiables.

## Critère préalable
Le premier score 24/24 ne se généralise pas automatiquement. Dans les 12 reformulations nouvelles, succès local seulement si ≥9/12 conformes ET zéro verdict confiant incorrect. En deçà : échec du transfert linguistique borné, signal à conserver sans retoucher l'ancien historique.

## Limites
Le corpus reste généré par le même auteur après avoir observé le code, pas aveugle ni représentatif de toute la langue française. Ce test est **adversarial** et non une estimation statistique de précision en production. Aucun résultat ne certifie des preuves mathématiques ni un moteur sémantique universel.
