def q_power(rows, steps):
    N = len(rows)
    if steps == 0:
        return [1 << i for i in range(N)]
    
    result = [1 << i for i in range(N)]
    
    for _ in range(steps):
        temp = [0] * N
        for i in range(N):
            for j in range(N):
                if rows[i] & (1 << j):
                    temp[i] |= result[j]
        result = temp
    
    return result
