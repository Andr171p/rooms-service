from pydantic import PositiveInt


def calculate(a: PositiveInt, b: PositiveInt) -> PositiveInt:
    return a + b


print(calculate(5, 0))
