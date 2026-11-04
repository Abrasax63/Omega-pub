from collections import deque

def compare(A,B,obs,initials):
    todo=deque((a,b,[(a,b)]) for a,b in initials)
    seen=set()
    while todo:
        a,b,path=todo.popleft()
        if (a,b) in seen: continue
        seen.add((a,b))
        if obs[a]!=obs[b]:
            return {'status':'NON_EQUIVALENT','witness':path,'observations_A':[obs[x] for x,_ in path], 'observations_B':[obs[y] for _,y in path]}
        na,nb=A[a],B[b]
        todo.append((na,nb,path+[(na,nb)]))
    return {'status':'EQUIVALENT','explored_pairs':len(seen)}

if __name__=='__main__':
    A={0:1,1:2,2:3,3:3}
    B={0:1,1:2,2:2,3:3}
    obs={0:0,1:0,2:0,3:1}
    print('Test divergence:',compare(A,B,obs,[(0,0)]))
    print('Test identité:',compare(A,A,obs,[(0,0)]))