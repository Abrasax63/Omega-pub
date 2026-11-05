from itertools import product

EXPECTED = {
'C4O-00': (0,7,8,15), 'C4O-01': (0,5,10,15),
'C4O-02': (2,7,8,13), 'C4O-03': (1,6,9,14),
'C4O-04': (0,3,4,7,8,11,12,15),
'C4O-05': (0,1,4,5,10,11,14,15),
'C4O-06': (4,5,6,7,8,9,10,11),
'C4O-07': (2,3,6,7,8,9,12,13)}
CYCLE=(0,1,2,3)
def rotate(mask,k): return sum(((mask>>i)&1)<<((i+k)%4) for i in range(4))
def canonical(S): return min(tuple(sorted(rotate(m,k) for m in S)) for k in range(4))
def coherent(F):
 n=len(F)
 if any(F.count(v)>2 for v in range(n)): return False
 edges=[(u,v) for u in range(n) for v in range(u+1,n) if F[u]==F[v] or {F[u],F[v]}=={u,v}]
 adj=[[] for _ in F]
 for u,v in edges: adj[u].append(v);adj[v].append(u)
 col=[-1]*n
 for s in range(n):
  if col[s]>=0:continue
  col[s]=0; stack=[s]
  while stack:
   u=stack.pop()
   for v in adj[u]:
    if col[v]<0: col[v]=1-col[u];stack.append(v)
    elif col[v]==col[u]:return False
 return True

def shadow(F,x,y):
 n=len(F); A=[x];B=[y]
 for _ in range(2): A.append(F[A[-1]]);B.append(F[B[-1]])
 # global assignment, every state included
 out=set()
 neq=[(u,v) for u in range(n) for v in range(u+1,n) if F[u]==F[v] or {F[u],F[v]}=={u,v}]
 eq=[(A[t],B[t]) for t in range(2) if A[t]!=B[t]]
 for bits in product((0,1),repeat=n):
  if any(bits[u]==bits[v] for u,v in neq):continue
  if any(bits[u]!=bits[v] for u,v in eq):continue
  out.add(sum(bits[i]<<i for i in CYCLE))
 return frozenset(out)

# Verify witness using global colorings
T=(1,2,3,0,8,7,6,2,0)
for name,pair in {'C4O-00':(0,1),'C4O-01':(0,2),'C4O-02':(1,8),'C4O-03':(0,7),'C4O-04':(0,6),'C4O-05':(4,5),'C4O-06':(1,4),'C4O-07':(0,4)}.items():
 S=shadow(T,*pair)
 assert tuple(sorted(S))==EXPECTED[name],(name,sorted(S))
print('GLOBAL witness PASS: all 8 raw masks match using assignments to all 9 states')
counts=[]
for n in range(4,9):
 total=n**(n-4); nc=0; found=False
 for code in range(total):
  z=code;F=[1,2,3,0]
  for _ in range(4,n):F.append(z%n);z//=n
  if not coherent(F):continue
  nc+=1
  seen=set()
  for x in range(n):
   for y in range(x+1,n):
    S=shadow(F,x,y)
    if not S:continue
    c=canonical(S)
    for name,target in EXPECTED.items():
     if c==canonical(frozenset(target)):seen.add(name)
    if len(seen)==8:found=True;break
   if found:break
 counts.append((n,total,nc,found))
 print(f'GLOBAL_ENUM N={n}: total={total}, coherent={nc}, witness={found}',flush=True)
 assert not found,(n,F)
print('GLOBAL PASS',counts)
