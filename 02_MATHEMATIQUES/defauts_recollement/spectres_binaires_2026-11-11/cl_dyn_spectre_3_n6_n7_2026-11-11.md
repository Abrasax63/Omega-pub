# CL-DYN — Le spectre {3} de six à sept états

11 novembre 2026. **CALCUL EXACT**, pour des endofonctions étiquetées et des partitions en blocs non étiquetés. Le spectre D contient les horizons h≥1 tels que Q^h diffère de E_h, la relation des extrémités effectivement réalisables.

## Mécanisme commun à six états

Les deux [classes à six états](cl_dyn_n6_spectres_et_extensions_2026-11-11.md) ont T=(1,0,0,2,3,4), avec π=(0,1,0,0,0,1) ou π=(0,1,0,0,1,1). La dynamique est un 2-cycle bicolore et une chaîne de quatre sommets qui y entre. Q² est complète dans les deux cas. Les puissances macro demandent donc tous les couples à partir de h=2.

La paire (1,1) est réalisée aux horizons pairs par le 2-cycle. À h=3, aucun départ de couleur 1 n'aboutit à cette couleur. À partir de h=5 impair, le sommet 5 atteint la couleur 1 par le 2-cycle après son entrée au temps 4. Les autres couples sont réalisés à h=3. Les tables E_h sont complètes à h=2 et h=4 et, dès h=5, les images T^h sont périodiques de période 2. Cela donne D={3} dans les deux cas.

## Tentatives de généralisation fixées avant le calcul à sept états

| Hypothèse testée | Verdict |
|---|---|
| Tous les systèmes de spectre {3} sont binaires. | Réfutée. |
| Tout système connexe de spectre {3} a un 2-cycle et une seule chaîne entrante. | Réfutée, même dans le cas binaire. |
| Un système binaire de spectre {3} a exactement une paire manquante à h=3, de la forme (a,a). | Vérifiée jusqu'à sept états dans les classes observées. Statut général indéterminé. |

Contre-exemple binaire ramifié : T=(1,0,0,0,2,4,5), π=(0,1,0,0,0,0,1). Le cycle (0,1) reçoit deux branches. Le seul manque à h=3 est (1,1).

Contre-exemple à cinq blocs et défaut hors diagonale : T=(0,0,0,1,2,3,4), π=(0,1,2,2,3,3,4). La dynamique converge vers un point fixe. Le seul manque à h=3 est (4,1), et D={3}.

## Inventaire à sept états

| Nombre de blocs | Classes d’isomorphisme de spectre {3} | Couples étiquetés |
|---:|---:|---:|
| 2 | 24 | 115 920 |
| 3 | 5 | 25 200 |
| 5 | 2 | 10 080 |
| Total | 31 | 151 200 |

Le parcours compte 343 types d’endofonctions et 171 837 classes de couples. La somme des poids vaut 722 247 211, soit 7⁷ × 877. Deux récurrences, l’une par blocs et l’autre sur (T^h,Q^h), concordent sur tous les représentants.

La description des deux témoins explique le défaut dans chacun d’eux. Le balayage à sept états tranche la portée de cette description. Cette itération compare les deux contrôles mathématiques sans comparaison de sessions Omega. Aucun changement GitHub ou SQLite.

## Reproduction

Le script imprime les comptes et le catalogue des classes de spectre {3} en JSON.

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
n=7;P=set(parts(n));perms=all_perms(n)
seen=set();maps=orbits=total=0;found=[]
for T in product(range(n),repeat=n):
 if T in seen:continue
 maps+=1
 conj=[(tuple(inv[T[x]] for x in order),order) for order,inv in perms]
 seen.update(S for S,order in conj)
 center=[order for S,order in conj if S==T];todo=P.copy()
 while todo:
  p=min(todo);orbit={rename(p[x] for x in order) for order in center}
  todo.difference_update(orbit);orbits+=1
  D=spectrum(T,p); assert D==independent(T,p); total+=factorial(n)*len(orbit)//len(center)
  if D!=(3,):continue
  Q={(p[x],p[T[x]]) for x in range(n)}; A=Q; M=T
  for _ in range(2):
   A={(u,w) for u,v in A for y,w in Q if v==y};M=tuple(T[x] for x in M)
  missing=A-{(p[x],p[M[x]]) for x in range(n)}
  reach=[]
  for x in range(n):
   v=x
   for _ in range(n):v=T[v]
   cyc={v};u=T[v]
   while u!=v:cyc.add(u);u=T[u]
   reach.append(tuple(sorted(cyc)))
  cycles=sorted(set(reach))
  found.append(dict(T=T,pi=p,q=max(p)+1,missing=sorted(missing),cycles=cycles,chain=max(Counter(T).values())<=2 and len(set(range(n))-set(T))==1,weight=factorial(n)*len(orbit)//len(center)))
assert total==n**n*len(P);print("total",total)
print(maps,orbits,len(found),sum(r['weight'] for r in found))
print(Counter((r['q'],tuple(map(len,r['cycles'])),r['chain'],len(r['missing']),all(a==b for a,b in r['missing'])) for r in found))
print(json.dumps(found))

```
