"""Check all absent/equal/opposite choices on simple graphs with up to four vertices."""
from itertools import combinations, product
from incremental import incremental, upper_bound
from solver import truth, verify


def main():
    tested = errors = over_bound = 0
    for n in range(1,5):
        pairs = tuple(combinations(range(n),2))
        for assignment in product((-1,0,1),repeat=len(pairs)):
            edges = [(a,b,sign) for (a,b),sign in zip(pairs,assignment) if sign>=0]
            case = dict(kind='parity',n=n,edges=edges)
            result = incremental(case)
            tested += 1
            errors += verify(case,result,truth(case)) != 'correct'
            over_bound += result['steps'] > upper_bound(n,len(edges))
    print(f'{tested} graphes, {errors} erreur(s), {over_bound} dépassement(s) de la borne')
    assert not errors and not over_bound


if __name__=='__main__':
    main()
