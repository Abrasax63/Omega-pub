"""Independent, intentionally direct reference for walks of exact length h."""


def observed_relation(transition, colors, color_count):
    if len(transition) != len(colors) or color_count < 1:
        raise ValueError('bad dimensions')
    if any(type(t) is not int or t < 0 or t >= len(transition) for t in transition):
        raise ValueError('invalid transition')
    if any(type(c) is not int or c < 0 or c >= color_count for c in colors):
        raise ValueError('invalid color')
    rows = [0] * color_count
    for state, successor in enumerate(transition):
        rows[colors[state]] |= 1 << colors[successor]
    return rows


def walks_exact(rows, steps):
    """Set-union dynamic programming, independent of generated bitwise matrix code."""
    if steps < 0:
        raise ValueError('steps must be nonnegative')
    width = len(rows)
    edges = [{j for j in range(width) if (mask >> j) & 1} for mask in rows]
    reached = [{i} for i in range(width)]
    for _ in range(steps):
        reached = [{target for intermediary in reachable for target in edges[intermediary]} for reachable in reached]
    return [sum(1 << j for j in reachable) for reachable in reached]


def actual_h_relation(transition, colors, color_count, steps):
    """Independent direct orbit computation for R_h (not Q^h)."""
    result = [0] * color_count
    for start in range(len(transition)):
        state = start
        for _ in range(steps):
            state = transition[state]
        result[colors[start]] |= 1 << colors[state]
    return result


def delta(transition, colors, color_count, steps, q_power_rows):
    observed = actual_h_relation(transition, colors, color_count, steps)
    return [row & ~actual for row, actual in zip(q_power_rows, observed)]
