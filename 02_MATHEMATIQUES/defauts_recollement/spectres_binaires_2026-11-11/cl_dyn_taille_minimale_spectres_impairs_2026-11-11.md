# CL-DYN — Taille minimale des spectres finis impairs

11 novembre 2026. **DÉMONTRÉ**. Dans le cadre binaire avec deux couleurs utilisées, soit D un spectre fini non vide et H=max D. Toute réalisation a au moins H+3 états. Cette borne est atteinte exactement quand tous les horizons de D sont impairs. Si D contient un horizon pair, il faut au moins H+4 états. L'optimum général pour ces spectres pairs ou mixtes reste ouvert ici.

## Borne inférieure et cas d'égalité

Un spectre fini non vide exige les deux passages entre couleurs dans Q et au moins une boucle. Sans passage ou sans boucle, les couleurs sont respectivement constantes ou alternées, sans défaut. S'il n'y a qu'un seul passage, la couleur cible est absorbante et le passage observé à un pas est réalisable à tous les horizons. Chaque boucle macro exigée à un horizon quelconque est exigée à tous. La finitude assure sa réalisation à un horizon arbitrairement grand. Un trajet qui part et revient à la même couleur dans cette dynamique monotone garde cette couleur tout le long, donc la boucle est réalisée à tous les horizons. Cela exclut un spectre fini non vide dans ce cas.

Deux passages et une boucle rendent Q² complète, puis Q^h complète pour h≥2. Comme D est fini, E_h est complète aux grands horizons, ce qui impose au moins un état périodique de chaque couleur : passé la profondeur transitoire, seules les couleurs périodiques peuvent être atteintes. Si d est la profondeur maximale, T^h, donc E_h, est périodique pour h≥d. Un défaut à H≥2 avec H≥d se répéterait indéfiniment. Ainsi d≥H+1. Une chaîne de profondeur d contient d états transitoires distincts. Avec au moins deux états périodiques, N≥H+3.

Si N=H+3, il y a exactement deux états périodiques et les H+1 états restants forment une seule chaîne. Deux points fixes ne conviennent pas : la chaîne n'entre que dans l'un d'eux, et le seul état du système dont le futur rejoint l'autre est cet autre point fixe. Le passage entre couleurs vers ce dernier est impossible aux grands horizons, alors que E_h doit être complète. Les deux états périodiques forment donc un 2-cycle bicolore. Il réalise les deux diagonales à tout horizon pair. Par le [théorème de la diagonale unique](cl_dyn_binaire_diagonale_unique_2026-11-11.md), aucun autre couple ne peut manquer lorsque D est fini. Donc D ne contient que des impairs.

## Construction optimale pour tout D impair

H est impair et ≥3. Prendre un 2-cycle aux couleurs 0 et 1 et une chaîne de profondeur L=H+1 qui entre dans le sommet 0. Le sommet de profondeur L a la couleur 1. Toutes les profondeurs paires inférieures à L et la profondeur 1 ont la couleur 0. Pour une profondeur impaire d≥3, donner la couleur 1 exactement si L−d n'est pas dans D.

Les deux passages et la boucle 0→0 sont observés à un pas, donc Q² est complète. Le cycle donne les passages hors diagonale aux horizons impairs, et les deux diagonales aux horizons pairs. À horizon pair, la profondeur 1 fournit 0→1 et la profondeur L fournit 1→0. À horizon impair, la profondeur 1 fournit 0→0. Il reste 1→1 aux horizons impairs h≥3. Aucun départ de couleur 1 à profondeur impaire ne le réalise : avant l'entrée au cycle il arrive à une profondeur paire strictement inférieure à L, et après l'entrée il arrive au sommet 0. Le sommet 1 du cycle ne le réalise pas non plus. Seul le départ de profondeur L peut fournir ce retour. Pour h<L, il aboutit à la profondeur L−h, qui a la couleur 1 exactement si h n'est pas dans D. Pour h≥L impair, il arrive sur la couleur 1 du cycle. Le spectre obtenu est D et le nombre d'états est H+3.

## Contrôle et intérêt

Vérification exacte par itération de (Q^h,T^h) jusqu'à répétition sur les 127 spectres non vides formés des impairs de 3 à 15. Aucune divergence. Les deux classes à six états de spectre {3} atteignent cette borne, en accord avec [l'inventaire à six états](cl_dyn_n6_spectres_et_extensions_2026-11-11.md).

L'horizon du dernier défaut donne une borne sur la mémoire transitoire cachée, et sa parité impose un état supplémentaire dans le cas pair ou mixte. C'est un filtre exact pour les recherches de petits témoins. La [construction générale à 4H+1](cl_dyn_classification_spectres_finis_binaires_2026-11-11.md) reste une majoration pour tous les spectres finis. Aucun changement GitHub ni SQLite.
