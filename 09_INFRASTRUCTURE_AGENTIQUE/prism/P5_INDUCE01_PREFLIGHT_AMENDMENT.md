# Amendement de préflight avant ouverture du holdout

Le contrôle du test `test_echo_not_an_executed_command` a relevé un défaut de l'extracteur initial : une commande `echo` pouvait être classée comme une déclaration de production par la grammaire générique, même si le filtre final ne l'aurait pas sélectionnée avec la règle `go build`.

**Correction pré-holdout :** commit [`2350444`](https://github.com/Abrasax63/Omega-pub/commit/235044491e74ad004d60c626cd8b2e1cc460b7ba), exclusion des outils de narration `echo`, `printf`, `cat`, `grep`, `sed`, `awk` dans la grammaire. Aucun des cinq journaux H1–H5 n'a été lu pendant cette correction. Les identifiants de jobs, le nombre d'exemples et les règles restent inchangés.

**Gel final code :** `235044491e74ad004d60c626cd8b2e1cc460b7ba`. Ce document conserve le gel initial et le motif de l'amendement pour l'audit, au lieu de réécrire l'histoire. Aucune promotion ni fusion `main`.
