"""A deliberately finite, inspectable program grammar for exact graph walk powers.

Generated code is NOT arbitrary LLM-generated code; only four audited program
shapes can be emitted. The output is real executable Python source.
"""
from hashlib import sha256

STRATEGIES = ('linear', 'square')
COMPOSERS = ('scan', 'lowbit')

COMPOSE = {
    'scan': '''def multiply(a, b):
    width = len(a)
    result = []
    for mask in a:
        accum = 0
        for j in range(width):
            if (mask >> j) & 1:
                accum |= b[j]
        result.append(accum)
    return result
''',
    'lowbit': '''def multiply(a, b):
    result = []
    for mask in a:
        accum = 0
        while mask:
            bit = mask & -mask
            accum |= b[bit.bit_length() - 1]
            mask -= bit
        result.append(accum)
    return result
''',
}

POWER = {
    'linear': '''def q_power(rows, steps):
    width = len(rows)
    if steps < 0:
        raise ValueError("steps must be nonnegative")
    result = [1 << j for j in range(width)]
    for _ in range(steps):
        result = multiply(result, rows)
    return result
''',
    'square': '''def q_power(rows, steps):
    width = len(rows)
    if steps < 0:
        raise ValueError("steps must be nonnegative")
    result = [1 << j for j in range(width)]
    base = rows[:]
    while steps:
        if steps & 1:
            result = multiply(result, base)
        steps >>= 1
        if steps:
            base = multiply(base, base)
    return result
''',
}


def generate():
    """Deterministically produce algorithmic variants from fixed transformations."""
    variants = {}
    for strategy in STRATEGIES:
        for composer in COMPOSERS:
            name = strategy + '-' + composer
            source = '# Omega finite-template candidate: ' + name + '\n' + COMPOSE[composer] + '\n' + POWER[strategy]
            variants[name] = {'source': source, 'sha256': sha256(source.encode()).hexdigest()}
    return variants


def choose(training):
    """Training scores only; no holdout access. Lower verified measured work wins."""
    eligible = {name: data for name, data in training.items() if data['correct'] and data['errors'] == 0}
    if not eligible:
        return None
    return min(eligible, key=lambda name: (eligible[name]['cpu_us_total'], name))
