# Décision garantie par des vérifications à coût connu

Un monde possible porte un verdict et un résultat pour chaque contrôle. Un historique conserve les mondes dont les résultats concordent avec les observations. Il autorise un verdict dès que tous les mondes restants ont le même verdict. Deux mondes de verdicts différents que tous les contrôles laissent dans la même classe empêchent toute garantie.

Pour un ensemble de mondes encore possibles S, le coût adaptatif est zéro si le verdict est constant. Sinon, pour chaque contrôle non constant sur S, on ajoute son coût au maximum des coûts optimaux des classes de résultats. On prend le minimum de ces valeurs. Chaque classe est strictement plus petite, ce qui donne une preuve par induction. Un contrôle constant n’apporte aucune information. La stratégie fixée d’avance est un sous-ensemble de contrôles dont les classes communes ont chacune un verdict constant. Dans le pire cas, un ordre fixé avec arrêt anticipé a la même valeur optimale, car son préfixe le plus long est un ensemble séparant.

Le banc compare les coûts dans le pire cas, avec contrôles exacts et déterministes. Il fournit un arbre et rejoue chaque monde. Une seconde énumération contrôle les 256 tables de verdict binaires sur trois bits observables. Elle examine explicitement les racines et les deux choix de branche pour les arbres de profondeur deux.

Le test de P1 importe sa version du commit de la PR #55. Il lui donne un blocage, un menu, puis un contrôle déjà choisi par l’appelant. Le solveur exact est un banc d’essai distinct. P1 ne bénéficie d’aucun indice tiré de l’optimum et ne reçoit aucun changement.
