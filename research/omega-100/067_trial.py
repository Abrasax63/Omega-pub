"""Test identifiability of letter and position shortcuts at equal query budget."""
from collections import defaultdict
from itertools import product
import json
from time import perf_counter


def reachable(edges):
    seen={0}
    while True:
        extended=seen|{b for a,b in edges if a in seen}
        if extended==seen:
            return 3 in seen
        seen=extended


def oracle(edges):
    matrix=[[i==j or (i,j) in edges for j in range(4)] for i in range(4)]
    for k in range(4):
        for i,j in product(range(4),repeat=2):
            matrix[i][j]|=matrix[i][k] and matrix[k][j]
    return matrix[0][3]


def evaluate(truth,crossed):
    traces=defaultdict(list)
    exact=defaultdict(int)
    for value,inverted,rep in product(truth,(False,True),(False,True)):
        positive="B" if inverted else "A"
        negative="A" if inverted else "B"
        first="B" if crossed and rep else "A"
        expected=positive if value else negative
        predictions={"truth":expected,"opposite":negative if value else positive,
                     "letter_a":"A","letter_b":"B","first":first,
                     "last":"A" if first=="B" else "B"}
        for name,token in predictions.items():
            traces[name].append(token)
            exact[name]+=token==expected
    classes=defaultdict(list)
    for name,trace in traces.items():
        classes[tuple(trace)].append(name)
    return dict(n=sum(map(len,traces.values()))//len(traces),
                indistinguishable=sorted(sorted(c) for c in classes.values() if len(c)>1),
                distinct_signatures=len(classes),exact=dict(exact))


def main():
    start=perf_counter()
    graphs=({(0,1),(1,2),(2,3)},{(0,1),(1,2),(3,2)})
    truth=tuple(oracle(g) for g in graphs)
    assert truth==tuple(reachable(g) for g in graphs)==(True,False)
    fixed,candidate=(evaluate(truth,c) for c in (False,True))
    assert fixed["n"]==candidate["n"]==8
    assert fixed["indistinguishable"]==[["first","letter_a"],["last","letter_b"]]
    assert not candidate["indistinguishable"]
    assert fixed["exact"]==candidate["exact"]
    print(json.dumps(dict(fixed=fixed,candidate=candidate,seconds=round(perf_counter()-start,6)),indent=2))


if __name__=="__main__":
    main()
