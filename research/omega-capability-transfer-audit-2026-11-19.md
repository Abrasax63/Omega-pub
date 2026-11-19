# Audit ciblé : de la reproductibilité au transfert de capacité

Date : 2026-11-19. Statut : diagnostic partiel, non-certification.

## Sources examinées
- README.md, ARCHITECTURE.md (branche principale / recherche GitHub)
- tools/repro_scientific_pilot.py, tools/repro_fingerprint.py, tools/repro_targeted_gate.py, tools/repro_adversarial_integrity.py (branche de la PR #205)
- GitHub Actions : runs 44619036483, 44621533735, 44621983556.

## Constat vérifié
1. Le script symbolique de spécialisation unaire s'exécute en CI.
2. Le pilote historique calcule une empreinte du script et une déclaration « no-external-inputs-declared » ; il n'inventorie pas effectivement les entrées.
3. Son manifeste conserve Python et SymPy, mais omet mpmath. La sonde d'import a observé mpmath 1.3.0 dans le processus testé.
4. Les sept tests adversariaux réussis portent sur des fichiers *déclarés*.
5. Le contrôle de métadonnées (médiane 1,432241 ms) est moins coûteux que la réexécution (430,119784 ms) dans le cas testé ; le gain complet du cache n'est pas mesuré.
6. Aucune intégration du cache au planificateur réel n'a été établie dans cette revue.
7. Aucun résultat de transfert d'apprentissage vers un problème nouveau n'est établi par ces runs.

## Ce qui reste indéterminé
- Inventaire complet des mécanismes sémantiques, de mémoire et d'apprentissage dans les autres branches/PR.
- Validité d'une attestation indépendante, authenticité de son auteur et vérification scientifique réelle.
- Découverte automatique de fichiers lus, réseau, subprocessus et effets non déterministes.
- Effet causal d'une mémoire ou d'une correction sur la qualité des solutions.

## Prochaine expérience discriminante : transfert avec et sans correction
Préenregistrer au moins six paires inédites (A, B) où B partage une structure avec A mais diffère de surface, et six paires témoins non liées.
Pour chaque paire, comparer à budget identique et modèle identique :
- témoin : résoudre B sans retour de A ;
- traitement : résoudre A, recevoir une correction vérifiée, puis résoudre B ;
- placebo : recevoir une correction de longueur comparable, mais sans rapport avec B.

Randomiser l'ordre et l'affectation des paires ; figer les problèmes, correcteurs et métriques avant toute génération. Aucune fuite des réponses de B dans le contexte. Conserver les sorties brutes et les coûts.

Mesures : exactitude de B, erreurs non détectées, abstentions correctes, coût et temps, amélioration traitement moins témoin, comparaison au placebo. Compter les échecs d'extraction comme échecs de mesure distincts.

Décision : ne parler de transfert que si le traitement dépasse les deux contrôles sur des problèmes tenus à l'écart, avec analyse des incertitudes. Ne pas inférer de progrès AGI d'une simple réussite.

## Garde-fou
Ne pas intégrer le cache à main. Corriger en priorité l'inventaire réel des entrées/dépendances et l'authentification de la validation ; garder le pilote réversible. Ce dossier ne remplace pas un audit exhaustif du dépôt.
