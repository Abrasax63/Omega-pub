# OBS-COL-11 — Amendement post-résultat, audit exact de généralisation

Date : 16 novembre 2026. **Post hoc** : les résultats du premier run ont été lus AVANT cette demande ; il ne s'agit PAS d'un critère de succès pré-enregistré initialement et ne doit pas servir à modifier les politiques.

Exécution historique figée : [GitHub #43822021430](https://github.com/Abrasax63/Omega-pub/actions/runs/43822021430), commit `380eaa5f25089cb7a4da003023cd76b5a0aea1f0`. Cohorte : 2 graphes incomplets exclus ; 4 registres de 4/8/16/32 états ; 5 bras chacun, 7 tests OK. Toute comparaison positive ou négative issue de ce run est conservée.

## Nouvelle question analytique, sans nouvelle politique

Pour chaque couple `(T_cible,H_appris)` issu de l'**exact même code et des mêmes seeds**, rechercher **après apprentissage**, indépendamment des données d'entraînement et des 256 mots réservés, un mot (w) de longueur minimale où les sorties de Moore divergent.

Algorithme : parcours en largeur du graphe produit de paires `(q_cible,q_H)` depuis les états initiaux. Si leurs sorties diffèrent, retourner le mot menant à la paire ; sinon, pour chaque action, examiner les successeurs couplés et ne visiter chaque paire qu'une fois. Si toutes les paires accessibles ont la même sortie, conclure `EXACT_EQUIVALENT_FOR_FINITE_COMPLETE_DETERMINISTIC_MOORE`, conséquence élémentaire de la déterminisation des trajectoires. Sinon `EXACT_COUNTEREXAMPLE`, sans prétendre qu'il soit dû spécifiquement à une politique Omega.

Les transitions **vraies** sont accessibles UNIQUEMENT à cet évaluateur après que le candidat a été gelé ; elles ne doivent jamais être remises à la politique. Ne pas corriger/reparamétrer/rerun sélectivement les modèles pour améliorer leur verdict. Ne pas promouvoir l'ancien résultat à une certification scientifique originale.

## Comparaison

- Rejouer le même banc sur les six fichiers verrouillés par SHA, les mêmes 5 bras et mêmes manifestes. Conserver toutes les traces de coûts ; valider la correspondance exacte aux compteurs du run initial avant de comparer les jugements.
- Dans les 4 cas compatibles, documenter l'état exact après gel et la longueur du plus court contre-exemple, ou l'absence exacte de contre-exemple dans les états du produit.
- Publier les résultats positifs ET négatifs. Sur les 2 graphes incomplets ne pas inventer de transitions.
- Aucune modification de `main`, aucune fusion, aucun appel payant, aucun nouvel algorithme apprenant ni gain d'Omega revendiqué.
