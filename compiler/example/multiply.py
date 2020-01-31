a = 2
b = -2
sh = 0
val = 0
while b > 0:
    odd = ((b + 1) >> 1) - (b >> 1)
    if odd == 1:
        val = val + (a << sh)
    sh = sh + 1
    b = b >> 1
print(val)
