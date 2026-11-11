# CL-DYN — Spectres pairs ou mixtes au seuil H+4

11 novembre 2026. Modèle binaire, D fini non vide, H=max D. La [construction générale](cl_dyn_classification_spectres_finis_binaires_2026-11-11.md) réalise tous ces spectres si 1∉D, avec au plus 4H+1 états. Le seuil H+4 concerne la taille minimale quand D contient un horizon pair.

## Réduction démontrée

Un système de taille H+4 réalisant un tel D doit être un 3-cycle bicolore avec une unique chaîne entrante de profondeur H+1. En effet, la [borne de profondeur](cl_dyn_taille_minimale_spectres_impairs_2026-11-11.md) impose d≥H+1 et les deux couleurs sur les états périodiques. Il y a donc deux ou trois états périodiques. Avec deux, le 2-cycle bicolore réalise les deux diagonales à toute longueur paire. Deux points fixes bicolores réalisent les deux diagonales à toute longueur. Ces formes ne peuvent avoir de défaut pair, puisque les défauts finis binaires sont diagonaux.

Avec trois états périodiques, tous les autres états constituent une seule chaîne. Un 2-cycle bicolore exclut encore tout défaut pair. Si tous les cycles sont monochromes, une seule composante possède des états transitoires. Chaque trajectoire finit par rejoindre un cycle. Un départ d'une couleur vers l'autre ne peut alors, aux grands horizons, se produire que dans la direction de la couleur cyclique de cette composante. La relation E_h ne peut donc pas être complète aux grands horizons, contrairement à la condition de spectre fini non vide. Il reste un seul 3-cycle bicolore.

Réciproquement, il suffit de tester les trois positions de la couleur minoritaire sur le cycle et les 2^(H+1) colorations de la chaîne. Vérifier E_h pour 2≤h≤H et sa complétude aux horizons H+1,H+2,H+3, qui couvrent la période terminale. Le cycle garantit Q² complète. Ce critère fini est exact pour tout H au seuil H+4. Comme les deux diagonales sont réalisées à tout multiple de 3 sur le cycle, si D contient un multiple de 3 et au moins un pair, alors N≥H+5. La condition ne dit rien sur les spectres purement impairs, déjà classés.

## Calculs

Spectres pairs ou mixtes distincts atteignant H+4 :

| H | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 | 13 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Nombre | 1 | 0 | 1 | 3 | 0 | 4 | 8 | 0 | 12 | 23 | 0 | 39 |

### Minimum exact pour D={2,3}

Le résultat structurel exclut N≤7, avec la borne précédente pour N≤6. Pour N=8, la profondeur minimale 4 force une chaîne de cinq sommets distincts qu'on peut renommer 0→1→2→3→4. On a testé les 8^4 complétions de T et les 127 colorations binaires non constantes à échange des couleurs près, soit 520 192 couples. Pour chacun, suivre les couples (T^h,Q^h) jusqu'à première répétition ou, équivalemment, suivre pour chaque bloc ses ensembles microscopique et macroscopique accessibles jusqu'à répétition. Aucun D={2,3}.

À neuf états, T=(1,2,3,4,0,0,5,6,7), π=(0,0,0,1,1,0,0,0,1). Le calcul direct donne Δ₂=Δ₃={(1,1)}, aucun défaut à h=1 et h=4,…,8. T^h est périodique de période 5 dès h=4 et Q^h est complète dès h=2. Donc le minimum est exactement 9.

Aucun changement GitHub ni SQLite.

## Code du contrôle au seuil H+4

```python
from collections import defaultdict

def rows(H):
 d=H+1
 T=(1,2,0,0)+tuple(range(3,H+3))
 n=len(T)
 pairs=[]
 power=tuple(range(n))
 for h in range(1,d+3):
  power=tuple(T[x] for x in power)
  pairs.append(power)
 full={(0,0),(0,1),(1,0),(1,1)}
 found={}
 for rare in range(3):
  for bits in range(1<<d):
   p=tuple(int(i==rare) for i in range(3))+tuple((bits>>i)&1 for i in range(d))
   E=[{(p[x],p[y]) for x,y in enumerate(power)} for power in pairs]
   if any(e!=full for e in E[d-1:]):continue
   D=tuple(h for h in range(2,H+1) if E[h-1]!=full)
   if not D or D[-1]!=H or not any(h%2==0 for h in D):continue
   assert all(full-E[h-1]=={(1,1)} for h in D)
   found.setdefault(D,(T,p))
 return found
if __name__=='__main__':
 for H in range(2,14):
  d=rows(H) if H%3 else {}
  print(H,len(d),sorted(d)[:20])

```
