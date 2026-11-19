"""Choose a solver from two inexpensive input properties."""


def choose(case):
    if case['kind'] == 'parity':
        return 'B' if any(edge[2] for edge in case['edges']) else 'A'
    return 'A' if case['target'] in case['values'] else 'B'
