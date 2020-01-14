D = 7
N = 33
Q = 0
R = 0
n = 0
N_copy = N
while N_copy > 0:
    N_copy >>= 1
    n += 1
while n > 0:
    n -= 1
    R <<= 1
    R += (((N >> n) + 1) >> 1) - ((N >> n) >> 1)
    Q <<= 1
    if R >= D:
        R -= D
        Q += 1

print(Q, R)
