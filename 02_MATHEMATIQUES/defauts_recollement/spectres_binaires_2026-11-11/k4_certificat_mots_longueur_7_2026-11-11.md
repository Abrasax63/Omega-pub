# K=4 — Certificat par mots de longueur 7

11 novembre 2026. **CALCUL EXACT**, limité aux 6 216 représentants du fichier [k4_reconstructed_minimal.json](https://chatgpt.com/library?file_id=libfile_fe822e54938c819197b5fb1369f2838d&account_id=personal). SHA-256 du fichier contrôlé : `8062760f5a79239b2d1c605902f9bc014c3e8c8229c1e65ab6fdb0ea4b99df67`.

## Résultat

| Longueur des mots | Signatures distinctes |
|---:|---:|
| 1 | 1 |
| 2 | 32 |
| 3 | 2 545 |
| 4 | 5 182 |
| 5 | 5 901 |
| 6 | 5 957 |
| 7 | 5 965 |
| 8 | 5 965 |

Une signature est l’ensemble exact des mots observables de la longueur indiquée, avec tous les états comme départs. À chaque pas le symbole est (observation de l’état courant, action), puis l’action détermine l’état suivant. Les transitions sont totales et il existe toujours une action pour prolonger un mot. Les langages complets égaux ont donc les mêmes signatures, et deux signatures différentes attestent deux langages différents.

Pour chacun des 251 représentants supplémentaires à l’intérieur des classes de signature de longueur 7, un produit d’observateurs a confirmé l’équivalence du langage complet avec le premier représentant de la classe. Ainsi la longueur 7 suffit exactement sur cet inventaire. Multiplicités des classes : 5 758 de taille 1, 181 de taille 2, 8 de taille 3 et 18 de taille 4. Elles concordent avec [l’audit canonique antérieur](https://chatgpt.com/library?file_id=libfile_a56563291b6881919e70cb769f8b3098&account_id=personal).

La longueur 6 ne suffit pas. Les lignes d’indices 429 et 433 (numérotation à partir de zéro) ont les mêmes mots à longueur 6. Les observations des deux systèmes sont (1,0,0,0). Leurs deux tables d’actions sont respectivement ((0,2,3,1),(0,2,0,0)) et ((0,3,3,1),(0,2,0,0)). Le mot `1000010`, encodé en base 4 par le chiffre 2·observation+action à chaque pas, est admis seulement par la seconde ligne. Il reste huit fusions en excès à longueur 6, au sens de la différence des nombres de classes.

## Reproduction

Lire chaque ligne comme (T,π). Pour les mots courts, initialiser l’ensemble des couples (mot, état) par {(0,x) : x=0,1,2,3}. À chaque itération remplacer chaque (w,x) par (4w+2π(x)+a,T[a][x]) pour a=0,1, en dédupliquant les couples. À longueur fixée, grouper les lignes par leur ensemble d’entiers w.

Pour vérifier l’équivalence dans chaque groupe de longueur 7, parcourir les couples de sous-ensembles accessibles depuis le couple des ensembles pleins. Pour chaque symbole (y,a), garder les états d’observation y, puis appliquer T[a]. Le langage est le même si aucun couple accessible ne contient exactement un ensemble vide. Ce contrôle ne recourt pas à la numérotation canonique des automates.

## Test de conception du contrôle et limite historique

Deux sessions isolées ont reçu les mêmes pièces. Avant le résultat documentaire, chacune a proposé un rapprochement des deux inventaires par équivalence de langage et indiqué qu’une absence du jeu historique empêchait d’attribuer l’écart. Une consigne stratégique supplémentaire n’a changé ni le contrôle choisi ni le verdict. Après révélation du résultat documentaire, les deux se sont abstenues de lancer le rapprochement. Le temps n’a pas été mesuré.

Le nouveau calcul confirme **5 965** pour l’inventaire reconstruit. Aucun jeu, code ou journal attribuable au décompte historique **5 988** n’a été retrouvé dans les sources consultées. Le chiffre 23 reste un écart entre totaux, sans interprétation établie. La longueur 7 n’est pas revendiquée comme borne universelle pour tous les systèmes contrôlés à quatre états. Aucun changement GitHub ou SQLite.
