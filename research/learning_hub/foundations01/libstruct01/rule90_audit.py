from collections import Counter
import json
from pathlib import Path

def direct(n,h):
    mask=(1<<n)-1; hist=Counter()
    for x in range(1<<n):
        word=0
        for _ in range(h+1):
            word=2*word+int(((x&1)+((x>>1)&1)+((x>>(n-1))&1))>=2)
            x=(((x<<1)&mask)|(x>>(n-1)))^((x>>1)|((x&1)<<(n-1)))
        hist[word]+=1
    return hist

def reduced(n,h):
    # no wrapping in the local cone; evolve a shrinking interval
    width=2*h+3
    if n<width:raise ValueError('cone wraps')
    hist=Counter()
    for mask in range(1<<width):
        x=[mask>>i&1 for i in range(width)];w=0
        for _ in range(h+1):
            mid=len(x)//2;w=2*w+int(sum(x[mid-1:mid+2])>=2)
            x=[x[i-1]^x[i+1] for i in range(1,len(x)-1)]
        hist[w]+=1<<(n-width)
    return hist

if __name__=='__main__':
    rows=[]
    for h in range(5):
        for n in range(2*h+3,15):
            a=direct(n,h);b=reduced(n,h);assert a==b
            rows.append(dict(n=n,h=h,full=1<<n,reduced=1<<(2*h+3),uniform=len(a)==1<<(h+1) and len(set(a.values()))==1))
    out=dict(cases=len(rows),full=sum(r['full'] for r in rows),reduced=sum(r['reduced'] for r in rows),all_uniform=all(r['uniform'] for r in rows),rows=rows)
    print(json.dumps({k:v for k,v in out.items() if k!='rows'},indent=2));print(next(r for r in rows if r['n']==14 and r['h']==2));Path(__file__).with_name('rule90_results.json').write_text(json.dumps(out,indent=2))
