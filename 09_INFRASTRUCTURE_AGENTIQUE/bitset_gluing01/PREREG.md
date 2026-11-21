# COMPRESS-01 — préenregistrement compression exacte des témoins (2026-11-21)

**Question** : sur les systèmes finis `T:X→X`, `π:X→Y`, peut-on conserver **tous** les états initiaux compatibles avec un mot d'observations, leurs multiplicités et la première obstruction, en utilisant moins de mémoire qu'une liste de couples `(état initial, état courant)` ?

## Nouvelle représentation, à prouver/tester
- Pour chaque horizon `i`, un masque entier `M_i(a)` représente tous les états initiaux `s` tels que `π(T^i(s))=a`.
- Le masque survivant pour `w=a_0...a_{L-1}` est l'intersection bit à bit `M_0(a_0) ∩ ... ∩ M_{L-1}(a_{L-1})`.
- Chaque bit représente un **état initial identifié**, et non une classe macro. Aucune fusion d'états, même si leurs observations ou leurs images coïncident.
- Les masques `M_i` sont construits progressivement par `T`, puis mémorisés par **la clé complète `(T,π)`** ; les survivants sont mémorisés par `(T,π,préfixe)`. Mémoire bornée par 8 systèmes et 2048 préfixes.
- Le masque exact permet de restituer tous les témoins initiaux (bits actifs), le nombre `bit_count`, le témoin minimal et le premier préfixe vide. Il ne prétend pas stocker gratuitement les états courants : ceux-ci peuvent être recalculés par `T^L` sur demande.
- Cette technique relève des méthodes classiques de filtrage d'ensembles et de bitsets, **pas d'une revendication d'innovation mathématique**.

## Test décisif
- Comparer pour `n=2,3,4`, toutes fonctions `T`, toutes observations binaires `π` (surjectives ou non) et tous mots binaires de longueur 1..5, soit **268 336** requêtes calculées exactement.
- Utiliser **trois** vérifications : traces microscopiques directes, filtre matriciel indépendant `delta_gluing_crosscheck.matrix_accepts`, et liste de couples complète issue de `witness_cache.WitnessCache`.
- Pour chaque cas vérifier : admissibilité, liste exhaustive des états initiaux survivants, quantité de témoins, témoin minimal et **premier préfixe impossible**.
- Contre-exemples forcés : `110` fantôme, `0001` d'obstruction profonde et systèmes même `Q` mais `W₃` différents. Tester limite/éviction/masques, changement de T/pi, mots vides, données non conformes.

## Mémoire et vitesse
- Comparer la représentation à paires et celle à bits sur **24 demandes répétées** avec `n=32,128,512,1024,2048`, longueur 12. Mêmes requêtes, résultats exacts.
- Mesurer temps Python et pic `tracemalloc` (ne représente ni RSS machine, ni énergie, ni un gain LLM). Report des allocations; même si les bitsets prennent plus de temps, ne pas effacer le résultat défavorable.
- Charge adversariale : 24 systèmes distincts `n=512`, donc **0 réutilisation**; examiner la mémoire retenue et l'intérêt d'un sélecteur adaptatif désactivant le cache lors de nouvelles demandes.
- Aucune incorporation en production avant mesure sur charges réelles et limites mémoire en octets, non seulement en nombre d'entrées.

## Périmètre
Branche empilée sur SCALE-01 #223, qui reste inchangée. Pas de LLM exécuté par cette PR, pas d'API payante, pas de nouvelle certification et aucune modification de `main`.
