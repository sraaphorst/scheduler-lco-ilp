# timed_function.py
# By Sebastian Raaphorst, 2020.

from time import monotonic


def timed_function(f):
    def wrapper(*args, **kwargs):
        print(f"*** Beginning function {f.__name__}")
        start = monotonic()
        result = f(*args, **kwargs)
        print(f"*** Ending function {f.__name__}: {monotonic() - start} s")
        return result
    return wrapper
