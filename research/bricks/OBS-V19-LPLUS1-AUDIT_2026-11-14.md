# V19 — vérifier l’ombre avant de réutiliser la brique

## Sources et statuts

- [Index historique de la PR #2](https://github.com/Abrasax63/Omega-pub/blob/refs/pull/2/head/research/bricks/INDEX_BRIQUES.md) — navigation. Son écart historique 83/85 reste à réconcilier carte par carte.
- [PR #5](https://github.com/Abrasax63/Omega-pub/pull/5) — contexte et audits V19. Les résultats sur les témoins C4/C5 gardent leurs hypothèses propres.
- [PR #18](https://github.com/Abrasax63/Omega-pub/pull/18) — comparaison finie du préfixe jusqu’au temps L+1 et du système global. Script source, blob Git 408e57aa0bcc172491561b6762b7d4d9d4d57d7e.

## Rejeu exact

```sh
python3 research/code/audit_v19_full_coloring_projection.py
```

Le second projecteur énumère toutes les colorations binaires de l’espace, intersecte les solutions de chaque contrainte puis projette sur le cycle. Il réutilise l’énumération des systèmes, des paires, des cycles et la construction des contraintes de la PR #18.

Résultat local sur n≤6, L=2 ou 3 : 325 468 comparaisons, zéro désaccord local/global après projection exacte. Par rapport au projecteur d’origine, 9 520 ombres globales et 9 520 ombres locales diffèrent.

Témoin : T=(0,0,3,4,2), cycle=(2,3,4), paire=(0,1), L=2. Les contraintes exigent simultanément c(0) XOR c(1)=1 (fusion) et =0 (événement). Le projecteur ancré au cycle renvoie huit colorations, alors que l’ensemble des colorations globalement extensibles est vide. Dans cet exemple, le modèle local contient aussi les deux contraintes.

**CALCUL EXACT** pour la comparaison bornée sous la sémantique d’extension à une solution de l’ensemble des contraintes. **RÉFUTÉ** : le projecteur ancré implémente cette sémantique pour toutes les entrées de la campagne. **INDÉTERMINÉ** : suffisance universelle de L+1, et statut de l’optimalité de L+2. La variante « composantes touchant le cycle » doit garder sa propre définition si elle est employée ailleurs.

## Cycle suivant

Fixer le contrat de la brique source par lecture de la définition de l’ombre. Comparer le projecteur d’extension exact à un candidat qui vérifie la cohérence globale avant propagation. Geler le témoin à cinq états, puis réserver une famille distincte pour mesurer la correction et le coût. Consigner aussi les essais sans gain. Une égalité bornée ne devient pas une preuve générale. Toute revendication de nouveauté nécessite une vérification bibliographique et une revue distincte.
