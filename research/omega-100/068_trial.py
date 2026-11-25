"""Find a minimum balanced design robust to one binary response error."""
from itertools import combinations, product
import json
from time import perf_counter


def signatures(rows):
    return list(zip(*[(t^r,1^(t^r),0,1,o,1^o) for t,r,o in rows],strict=True))


def distance(words):
    return min(sum(x!=y for x,y in zip(a,b,strict=True)) for a,b in combinations(words,2))


def collisions(words):
    seen={}
    for key,word in enumerate(words):
        variants=[word]+[word[:i]+(1-word[i],)+word[i+1:] for i in range(len(word))]
        for v in variants:
            seen.setdefault(v,set()).add(key)
    return sum(len(owners)>1 for owners in seen.values())


def main():
    start=perf_counter()
    grid=list(product((0,1),repeat=3))
    fixed=signatures([(t,r,0) for t,r,_ in grid])
    assert fixed[2]==fixed[4] and distance(fixed)==0 and collisions(fixed)>0
    summary={}
    for n in (2,4,6,8):
        balanced=[s for s in combinations(grid,n) if tuple(map(sum,zip(*s)))==(n//2,)*3]
        reports=[]
        for s in balanced:
            words=signatures(s)
            d=distance(words)
            c=collisions(words)
            assert (d>=3)==(c==0)
            reports.append((d,c))
        summary[n]=dict(balanced=len(reports),best_minimum_distance=max(d for d,_ in reports),
                        zero_collisions=sum(c==0 for _,c in reports))
    assert min(n for n,row in summary.items() if row["zero_collisions"])==8
    crossed=signatures(grid)
    print(json.dumps(dict(plans=summary,reference_collision_words=collisions(fixed),
                          candidate_collision_words=collisions(crossed),
                          seconds=round(perf_counter()-start,6)),indent=2))


if __name__=="__main__":
    main()
