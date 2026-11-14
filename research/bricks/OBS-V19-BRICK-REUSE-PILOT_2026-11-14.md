# Pilote V19 — réutilisation d’une brique

14 novembre 2026. Base `8030f907384db9938159b1a25e90db3ce10adba1`. Source épinglée : [garde V19](https://github.com/Abrasax63/Omega-pub/blob/8030f907384db9938159b1a25e90db3ce10adba1/research/bricks/OBS-V19-SHADOW-GUARD_2026-11-14.md).

Mission commune : calculer les masques du cycle qui s’étendent à une coloration satisfaisant les contraintes forcées et les égalités de l’événement. Les deux stratégies reçoivent les mêmes entrées et disposent d’un appel de projecteur par cas. La stratégie directe énumère les masques binaires sur X. Avec le catalogue, le sélecteur déterministe compare le domaine déclaré de deux fiches au contrat de la mission. Il écarte la fiche sur la localité bornée et choisit le garde pour la projection globale binaire. Le catalogue est encodé manuellement pour ce pilote. Le projecteur exhaustif sur tuples de couleurs calcule les réponses après le retour des deux stratégies.

## Calcul fini

Famille distincte du test du garde : C4, deux points fixes et deux feuilles vers deux destinations périodiques distinctes. Quinze endofonctions sur huit états, toutes les 28 paires et L=2,3,4. Sur 1 260 cas, l’oracle trouve 248 ombres vides. Les deux stratégies retrouvent exactement les mêmes masques sur les 1 260 cas.

| Stratégie | Erreurs | Médiane locale, trois passages |
| --- | ---: | ---: |
| Directe, énumération par masques | 0 | 0,151 s |
| Réutilisation du garde V19 | 0 | 0,021 s |

Le rapport observé est d’environ 7,2 sur ces durées de calcul, hors constitution des entrées et calcul de l’oracle. L’ordre fixe d’exécution et trois mesures locales limitent l’interprétation du temps. Le résultat compare deux algorithmes et un sélecteur par domaine codé à la main. Il ne mesure ni la recherche autonome d’une fiche dans l’index, ni la supériorité face à un autre solveur direct optimisé. L’originalité bibliographique n’a pas été évaluée.

Depuis `research/code` :

```sh
for i in 1 2 3; do python3 pilot_v19_brick_reuse.py; done
python3 audit_v19_shadow_guard.py
python3 test_v19_locality_l_plus_1.py
```

Contrôles existants : zéro erreur avec garde sur 4 536 projections réservées, et ancien test L+1 terminé sur 325 468 comparaisons selon sa sémantique historique. SHA-256 du pilote `a580d615a483e48acaa19d29e5f75e31ad8ea3ac44a0d7d5ee55dd65c0b10fa4`. Empreinte ordonnée des masques de l’oracle `58c13185ea043fcdd7fb71c6c3dcc48dfe05dfcfb561090c76865d1edb6051f4`.

Prochain test : fournir plusieurs missions aux contrats voisins, avec des fiches distractrices et un cas hors domaine. Mesurer les sélections, les abstentions et le coût total en ajoutant un solveur direct à contraintes de parité.
