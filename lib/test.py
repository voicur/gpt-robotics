from itertools import cycle

keys = ["1", "2", "3"]

keyCycle = cycle(keys)

next(keyCycle)
print(next(keyCycle))
print(next(keyCycle))

print(next(keyCycle))
print(next(keyCycle))