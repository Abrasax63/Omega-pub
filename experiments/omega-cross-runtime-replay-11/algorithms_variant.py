"""Different implementation of the SAME arithmetic dependency result."""

def aggregate(values):
    total = 0
    for value in values:
        total += int(value)
    return total
