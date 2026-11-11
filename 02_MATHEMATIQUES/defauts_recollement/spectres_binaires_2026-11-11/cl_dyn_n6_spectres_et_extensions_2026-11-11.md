# CL-DYN — Spectres finis non vides à six états

11 novembre 2026. **CALCUL EXACT.** Endofonctions sur six états étiquetés et partitions à blocs non étiquetés. Le spectre D contient les horizons h≥1 où la puissance de la relation macro diffère de la relation des extrémités effectivement réalisables.

| Spectre | Couples étiquetés | Classes d’isomorphisme |
|---|---:|---:|
| {2} | 27 360 | 41 |
| {2,3} | 4 320 | 6 |
| {3} | 1 440 | 2 |
| Total fini non vide | 33 120 | 49 |

Il y a aussi 1 853 898 couples de spectre vide et 7 584 150 de spectre infini. Le parcours compte 130 types d’endofonctions, 15 981 classes de couples et un poids total de 9 471 168, égal à 6⁶ × 203. Deux récurrences exactes (bloc par bloc et sur les relations entières) concordent pour chaque représentant.

## Comparaison à cinq états

Une restriction est admise si les cinq états conservés sont fermés sous T. Le sommet supprimé peut être un point fixe, à condition qu’aucun autre état ne pointe vers lui. Les références sont les deux [classes à cinq états](cl_dyn_n5_orbites_240_2026-11-11.md).

25 classes (15 840 couples) admettent une telle restriction vers une référence. 24 classes (17 280 couples) n’en admettent aucune. Répartition des 24 : 18 de spectre {2}, 4 de spectre {2,3}, 2 de spectre {3}. Un premier filtre qui excluait toute suppression de point fixe ne trouvait que 21 classes. Le contrôle par construction a révélé quatre omissions. Après correction, les 60 extensions brutes des deux références (six cibles et cinq choix de bloc pour le nouveau sommet) redonnent exactement les 25 classes acceptées, après quotient.

Exemple sans restriction admissible vers une référence : T=(1,0,0,2,3,4), π=(0,1,0,0,0,1), D={3}. Ici l’unique sommet supprimable est 5 et la restriction n’a que deux blocs, contre quatre pour les références.

## Évaluation de la stratégie

Les deux sessions ont préféré conserver les représentants et leurs poids. La session directe a aussi proposé de tester les restrictions à cinq états. L’option détaillée contenait déjà les totaux et histogrammes de l’option agrégée, pour un coût supposé comparable. Aucun avantage de la consigne supplémentaire n’a été mesuré.

Itération suivante : comparer des contrôles dont aucun ne contient automatiquement l’autre, puis chercher une caractérisation structurale des deux classes de spectre {3}. Aucun changement GitHub ou SQLite.

## Script reproductible

Le script imprime les comptes et l’inventaire des classes retenues en JSON sur sa dernière ligne.

```python
from itertools import product, permutations
from collections import Counter
from math import factorial
import json

def parts(n,p=(0,)):
 if len(p)==n:yield p;return
 for c in range(max(p)+2):yield from parts(n,p+(c,))
def rename(p):
 ids={};return tuple(ids.setdefault(x,len(ids)) for x in p)
def all_perms(n):
 return [(p,tuple(p.index(i) for i in range(n))) for p in permutations(range(n))]
def spectrum(T,p):
 n=len(T);q=max(p)+1
 blocks=[frozenset(x for x in range(n) if p[x]==b) for b in range(q)]
 Q=[frozenset(p[T[x]] for x in block) for block in blocks]
 D=set()
 for b,S in enumerate(blocks):
  A=frozenset({b});seen={};fails=[]
  while (S,A) not in seen:
   seen[S,A]=len(fails);fails.append(frozenset(p[x] for x in S)!=A)
   S=frozenset(T[x] for x in S);A=frozenset(j for i in A for j in Q[i])
  if any(fails[seen[S,A]:]):return None
  D.update(h for h,fail in enumerate(fails) if fail)
 return tuple(sorted(D))
def independent(T,p):
 n=len(T);Q=frozenset((p[x],p[T[x]]) for x in range(n))
 links={x:{v for u,v in Q if u==x} for x in set(p)}
 M=tuple(range(n));A=frozenset((x,x) for x in set(p))
 seen={};bad=[]
 while (M,A) not in seen:
  seen[M,A]=len(bad);bad.append(A!=frozenset((p[x],p[M[x]]) for x in range(n)))
  M=tuple(T[y] for y in M);A=frozenset((u,w) for u,v in A for w in links[v])
 return None if any(bad[seen[M,A]:]) else tuple(i for i,b in enumerate(bad) if b)
def restrict(T,p,r):
 keep=[x for x in range(len(T)) if x!=r];ind={x:i for i,x in enumerate(keep)}
 return tuple(ind[T[x]] for x in keep),rename(p[x] for x in keep)
def canon(T,p,perms):
 return min((tuple(inv[T[x]] for x in order),rename(p[x] for x in order)) for order,inv in perms)
n=6;P=set(parts(n));perms=all_perms(n);p5=all_perms(5)
reference={((0,0,0,1,2),(0,1,2,2,3)):'I',((0,0,0,1,3),(0,1,2,2,3)):'II'}
seen=set();totals=Counter();hist=Counter();maps=orbits=0; rows=[]
for T in product(range(n),repeat=n):
 if T in seen:continue
 maps+=1
 conj=[(tuple(inv[T[x]] for x in order),order) for order,inv in perms]
 seen.update(S for S,order in conj)
 center=[order for S,order in conj if S==T]; todo=P.copy()
 while todo:
  p=min(todo);orbit={rename(p[x] for x in order) for order in center}
  todo.difference_update(orbit);orbits+=1
  D=spectrum(T,p)
  assert D==independent(T,p),(T,p,D)
  weight=factorial(n)*len(orbit)//len(center);totals[D]+=weight
  if not D:continue
  hits=[]
  for r in (x for x in range(n) if all(y==x or T[y]!=x for y in range(n))):
   key=canon(*restrict(T,p,r),p5)
   if key in reference:hits.append((r,reference[key]))
  hs=','.join(sorted({t for r,t in hits})) if hits else '-'
  hist[(D,max(p)+1,hs)]+=weight
  rows.append({'T':T,'pi':p,'D':D,'weight':weight,'restrictions':hits})
assert sum(totals.values())==n**n*len(P)
print('maps',maps,'pairs',orbits,'weights',sum(totals.values()),'totals',totals,'accepted_orbits',len(rows))
for key,value in sorted(hist.items()):print(key,value)
print('orbit summary',Counter((tuple(r['D']),bool(r['restrictions'])) for r in rows))
print('first no restriction',next((r for r in rows if not r['restrictions']),None))
print(json.dumps(rows))

```
