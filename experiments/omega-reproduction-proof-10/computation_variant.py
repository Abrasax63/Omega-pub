"""Different ACTUAL Python dependency source implementing same computation."""
def aggregate(values):
    total = 0
    for value in values:
        total += int(value)
    return total
