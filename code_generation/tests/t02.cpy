def fact(n: int) -> int:
    value: int = 1
    while n > 1:
        value = value * n
        n = n - 1
    return value

def fact_r(n: int) -> int:
    if n > 1:
        return n * fact_r(n - 1)
    return 1

print(fact(5))
print(fact_r(5))

