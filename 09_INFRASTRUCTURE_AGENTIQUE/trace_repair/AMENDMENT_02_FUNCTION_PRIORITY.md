# Amendement #2 — priorisation par fonction, après le premier run

Date : 16 novembre 2026. Ce document est enregistré **après** l'inspection du [premier run #43777440387](https://github.com/Abrasax63/Omega-pub/actions/runs/43777440387), **avant** modification du générateur et avant toute nouvelle exécution.

## Faits ayant motivé l'amendement

- Le localisateur de fichiers place **tqdm/std.py** au rang 1/10 contre 8/10 alphabétique, et **cookiecutter/hooks.py** au rang 1/6 contre 4/6 alphabétique, avec de vraies traces `sys.setprofile`.
- Le premier générateur de deux lignes a proposé 20 candidats par projet, en a exécuté six chacun sous Docker, et les **12 ont échoué**.
- Plusieurs premiers candidats touchent des méthodes secondaires malgré la bonne localisation du fichier : `tqdm/std.py` change la fonction d'itération ou le verrou; `cookiecutter/hooks.py` change des tests de disponibilité généraux. La faiblesse nouvelle est donc une **absence de priorité par fonction à l'intérieur du bon fichier**.
- Les noms de fonctions de la vérité de référence sont déjà connus des expérimentateurs. Une nouvelle réussite sur cette cohorte restera **post-hoc et contaminée**, jamais une preuve de transfert aveugle.

## Changement unique et comparaison

Modifier uniquement **l'ordre d'examen des mêmes modifications génériques**. Chaque candidate se voit attribuer `function_name` et `function_start_line` par l'AST déjà disponible. Sans lire de corrigé, classer d'abord les candidates dans les fonctions dont le nom est présent dans les **symboles du test en échec**, puis conserver l'ordre des fichiers guidé par les traces et le numéro de ligne. Grammaire, coût et sécurité inchangés : max 20 candidats par projet, max deux lignes d'une seule fonction, max six tests Docker par projet.

Contrôles indispensables : nombre de candidats borné, remplacement uniquement sur lignes préexistantes, aucune source fixed comme entrée, test unitaire de la priorité, empreintes SHA des sources inchangées pour une candidate de même contenu, et nouvelle exécution GitHub avec détails des fonctions sélectionnées. Comparer à la première campagne sur les **mêmes deux bugs connus** ; un éventuel progrès est uniquement une **correction d'heuristique de classement**, pas une évaluation indépendante ni un entraînement neuronal.

Toute réussite demandera buggy FAIL, fixed PASS, patch PASS sur le vrai test historique. À défaut, publier l'échec.
